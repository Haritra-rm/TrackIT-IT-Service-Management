import json
from datetime import datetime, timezone
from typing import Optional, List, Tuple, Dict, Any
from sqlalchemy.orm import Session

from app.models.ticket import Ticket, TicketStatus, TicketPriority
from app.models.user import User, UserRole
from app.models.category import Category
from app.models.status_history import TicketStatusHistory
from app.schemas.ticket import (
    TicketCreate,
    TicketUpdate,
    TicketAssign,
    TicketStatusUpdate,
    TicketResolve,
    TicketReopen,
    TicketResponse,
    TicketStatusHistoryResponse,
)
from app.repositories.ticket_repository import TicketRepository
from app.repositories.category_repository import CategoryRepository
from app.repositories.user_repository import UserRepository
from app.repositories.audit_repository import AuditRepository
from app.services.sla_service import SLAService
from app.services.priority_service import PriorityRecommendationEngine
from app.core.exceptions import (
    NotFoundException,
    ForbiddenException,
    ValidationException,
    InvalidTransitionException,
)
from app.core.logging import logger


class TicketService:
    def __init__(self, db: Session):
        self.db = db
        self.ticket_repo = TicketRepository(db)
        self.category_repo = CategoryRepository(db)
        self.user_repo = UserRepository(db)
        self.audit_repo = AuditRepository(db)

    # Allowed state transitions state machine
    VALID_TRANSITIONS = {
        TicketStatus.OPEN: [TicketStatus.ASSIGNED],
        TicketStatus.ASSIGNED: [TicketStatus.IN_PROGRESS, TicketStatus.OPEN],
        TicketStatus.IN_PROGRESS: [TicketStatus.RESOLVED, TicketStatus.ASSIGNED],
        TicketStatus.RESOLVED: [TicketStatus.CLOSED, TicketStatus.REOPENED],
        TicketStatus.CLOSED: [TicketStatus.REOPENED],
        TicketStatus.REOPENED: [TicketStatus.IN_PROGRESS],
    }

    def _enrich_ticket_response(self, ticket: Ticket) -> TicketResponse:
        """Helper to enrich a Ticket model with computed SLA status and relation names."""
        sla_info = SLAService.evaluate_sla_status(
            created_at=ticket.created_at,
            due_at=ticket.due_at,
            resolved_at=ticket.resolved_at,
            status=ticket.status,
        )

        return TicketResponse(
            id=ticket.id,
            title=ticket.title,
            description=ticket.description,
            category_id=ticket.category_id,
            category_name=ticket.category.name if ticket.category else None,
            priority=ticket.priority,
            status=ticket.status,
            created_by=ticket.created_by,
            creator_name=ticket.creator.name if ticket.creator else None,
            creator_email=ticket.creator.email if ticket.creator else None,
            assigned_to=ticket.assigned_to,
            assignee_name=ticket.assignee.name if ticket.assignee else None,
            assignee_email=ticket.assignee.email if ticket.assignee else None,
            created_at=ticket.created_at,
            updated_at=ticket.updated_at,
            due_at=ticket.due_at,
            resolved_at=ticket.resolved_at,
            closed_at=ticket.closed_at,
            resolution_notes=ticket.resolution_notes,
            sla_status=sla_info["sla_status"],
            sla_remaining_hours=sla_info["sla_remaining_hours"],
            is_breached=sla_info["is_breached"],
            comments_count=len(ticket.comments) if hasattr(ticket, "comments") else 0,
        )

    def create_ticket(self, payload: TicketCreate, creator: User) -> TicketResponse:
        # Verify category exists and is active
        category = self.category_repo.get_by_id(payload.category_id)
        if not category:
            raise NotFoundException(f"Category with ID {payload.category_id} was not found", code="CATEGORY_NOT_FOUND")
        if not category.is_active:
            raise ValidationException(f"Category '{category.name}' is currently inactive", code="CATEGORY_INACTIVE")

        # Validate priority
        priority = (payload.priority or TicketPriority.MEDIUM).upper()
        if priority not in TicketPriority.ALL_PRIORITIES:
            raise ValidationException(f"Invalid priority '{priority}'. Allowed: {TicketPriority.ALL_PRIORITIES}")

        now = datetime.now()
        due_at = SLAService.calculate_due_date(now, priority)

        # Support Agents & Admins can create tickets on behalf of employees
        ticket_creator_id = creator.id
        if payload.on_behalf_of_id:
            if creator.role not in [UserRole.SUPPORT_AGENT, UserRole.ADMIN]:
                raise ForbiddenException("Employees are only permitted to create tickets for themselves", code="FORBIDDEN")
            target_user = self.user_repo.get_by_id(payload.on_behalf_of_id)
            if not target_user:
                raise NotFoundException(f"User with ID {payload.on_behalf_of_id} was not found", code="USER_NOT_FOUND")
            if not target_user.is_active:
                raise ValidationException("Cannot create tickets on behalf of an inactive user", code="USER_INACTIVE")
            ticket_creator_id = target_user.id

        ticket = Ticket(
            title=payload.title.strip(),
            description=payload.description.strip(),
            category_id=category.id,
            priority=priority,
            status=TicketStatus.OPEN,
            created_by=ticket_creator_id,
            created_at=now,
            due_at=due_at,
        )
        created_ticket = self.ticket_repo.create(ticket)

        # Record initial status in history
        self.ticket_repo.record_status_change(
            ticket_id=created_ticket.id,
            old_status=None,
            new_status=TicketStatus.OPEN,
            changed_by=creator.id,
        )

        # Audit log
        self.audit_repo.log_action(
            user_id=creator.id,
            action="TICKET_CREATED",
            entity_type="TICKET",
            entity_id=created_ticket.id,
            metadata_json=json.dumps({
                "priority": priority,
                "category_id": category.id,
                "on_behalf_of": ticket_creator_id if ticket_creator_id != creator.id else None,
            }),
        )

        logger.info(f"Ticket #{created_ticket.id} created by user {creator.id} with priority {priority}")
        return self._enrich_ticket_response(self.ticket_repo.get_by_id_with_relations(created_ticket.id))

    def get_ticket(self, ticket_id: int, current_user: User) -> TicketResponse:
        ticket = self.ticket_repo.get_by_id_with_relations(ticket_id)
        if not ticket:
            raise NotFoundException(f"Ticket with ID {ticket_id} was not found", code="TICKET_NOT_FOUND")

        # RBAC: Employees can ONLY view their own tickets
        if current_user.role == UserRole.EMPLOYEE and ticket.created_by != current_user.id:
            logger.warning(f"Access denied: Employee {current_user.id} tried to view ticket {ticket_id}")
            raise ForbiddenException("You are not authorized to view this ticket", code="FORBIDDEN")

        return self._enrich_ticket_response(ticket)

    def list_tickets(
        self,
        current_user: User,
        search: Optional[str] = None,
        ticket_id: Optional[int] = None,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        category_id: Optional[int] = None,
        assigned_to: Optional[int] = None,
        created_by: Optional[int] = None,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
        page: int = 1,
        page_size: int = 20,
    ) -> Tuple[List[TicketResponse], int]:
        # Strict RBAC enforcement at repository query layer:
        # If Employee: force created_by filter to current_user.id
        filter_created_by = created_by
        if current_user.role == UserRole.EMPLOYEE:
            filter_created_by = current_user.id

        skip = (page - 1) * page_size
        tickets, total = self.ticket_repo.search_and_filter(
            search=search,
            ticket_id=ticket_id,
            status=status,
            priority=priority,
            category_id=category_id,
            created_by=filter_created_by,
            assigned_to=assigned_to,
            from_date=from_date,
            to_date=to_date,
            sort_by=sort_by,
            sort_order=sort_order,
            skip=skip,
            limit=page_size,
        )

        return [self._enrich_ticket_response(t) for t in tickets], total

    def update_ticket(self, ticket_id: int, payload: TicketUpdate, current_user: User) -> TicketResponse:
        ticket = self.ticket_repo.get_by_id_with_relations(ticket_id)
        if not ticket:
            raise NotFoundException(f"Ticket with ID {ticket_id} was not found", code="TICKET_NOT_FOUND")

        # Closed tickets cannot normally be modified without reopening
        if ticket.status == TicketStatus.CLOSED:
            raise ValidationException("Closed tickets cannot be modified. Reopen the ticket first.", code="TICKET_CLOSED")

        # RBAC Check:
        # Employees can only edit their own tickets and only if still OPEN
        if current_user.role == UserRole.EMPLOYEE:
            if ticket.created_by != current_user.id:
                raise ForbiddenException("You cannot edit tickets created by others", code="FORBIDDEN")
            if ticket.status != TicketStatus.OPEN:
                raise ValidationException("Employees can only modify ticket details while ticket is OPEN", code="INVALID_STATUS")

        if payload.title:
            ticket.title = payload.title.strip()
        if payload.description:
            ticket.description = payload.description.strip()

        if payload.category_id:
            category = self.category_repo.get_by_id(payload.category_id)
            if not category:
                raise NotFoundException("Specified category not found", code="CATEGORY_NOT_FOUND")
            ticket.category_id = category.id

        if payload.priority:
            p_upper = payload.priority.upper()
            if p_upper not in TicketPriority.ALL_PRIORITIES:
                raise ValidationException(f"Invalid priority '{payload.priority}'")
            # Only Support Agents or Admins can change priority of tickets after creation
            if current_user.role == UserRole.EMPLOYEE and ticket.priority != p_upper:
                raise ForbiddenException("Only support agents or admins can reassign priority", code="FORBIDDEN")
            ticket.priority = p_upper
            # Recalculate SLA due_at with updated priority
            ticket.due_at = SLAService.calculate_due_date(ticket.created_at, ticket.priority)

        updated = self.ticket_repo.update(ticket)
        self.audit_repo.log_action(
            user_id=current_user.id,
            action="TICKET_UPDATED",
            entity_type="TICKET",
            entity_id=ticket.id,
        )
        return self._enrich_ticket_response(self.ticket_repo.get_by_id_with_relations(updated.id))

    def assign_ticket(self, ticket_id: int, payload: TicketAssign, current_user: User) -> TicketResponse:
        # RBAC: Only Support Agents or Admins can assign tickets
        if current_user.role not in [UserRole.SUPPORT_AGENT, UserRole.ADMIN]:
            raise ForbiddenException("Employees are not authorized to assign tickets", code="FORBIDDEN")

        ticket = self.ticket_repo.get_by_id_with_relations(ticket_id)
        if not ticket:
            raise NotFoundException(f"Ticket with ID {ticket_id} was not found", code="TICKET_NOT_FOUND")

        # Validate target assignee
        assignee = self.user_repo.get_by_id(payload.assigned_to)
        if not assignee:
            raise NotFoundException("Assigned user does not exist", code="USER_NOT_FOUND")
        if assignee.role not in [UserRole.SUPPORT_AGENT, UserRole.ADMIN]:
            raise ValidationException("Tickets can only be assigned to Support Agents or Admins", code="INVALID_ASSIGNEE")
        if not assignee.is_active:
            raise ValidationException("Cannot assign ticket to an inactive agent", code="ASSIGNEE_INACTIVE")

        old_status = ticket.status
        ticket.assigned_to = assignee.id

        # If ticket was OPEN, transition automatically to ASSIGNED
        if ticket.status == TicketStatus.OPEN:
            ticket.status = TicketStatus.ASSIGNED
            self.ticket_repo.record_status_change(
                ticket_id=ticket.id,
                old_status=old_status,
                new_status=TicketStatus.ASSIGNED,
                changed_by=current_user.id,
            )

        updated = self.ticket_repo.update(ticket)

        self.audit_repo.log_action(
            user_id=current_user.id,
            action="TICKET_ASSIGNED",
            entity_type="TICKET",
            entity_id=ticket.id,
            metadata_json=json.dumps({"assigned_to": assignee.id, "assignee_name": assignee.name}),
        )

        logger.info(f"Ticket #{ticket.id} assigned to agent {assignee.id} by user {current_user.id}")
        return self._enrich_ticket_response(self.ticket_repo.get_by_id_with_relations(updated.id))

    def update_status(self, ticket_id: int, payload: TicketStatusUpdate, current_user: User) -> TicketResponse:
        ticket = self.ticket_repo.get_by_id_with_relations(ticket_id)
        if not ticket:
            raise NotFoundException(f"Ticket with ID {ticket_id} was not found", code="TICKET_NOT_FOUND")

        target_status = payload.status.upper()
        if target_status not in TicketStatus.ALL_STATUSES:
            raise ValidationException(f"Invalid status '{payload.status}'. Allowed: {TicketStatus.ALL_STATUSES}")

        # RBAC Check: Employees can never manually change ticket status except closing their own resolved ticket
        if current_user.role == UserRole.EMPLOYEE:
            if target_status != TicketStatus.CLOSED:
                raise ForbiddenException(
                    "Employees cannot manually change ticket status. Use Reopen or Close endpoints.",
                    code="FORBIDDEN",
                )
            if ticket.created_by != current_user.id:
                raise ForbiddenException(
                    "Only the original ticket creator can close a resolved ticket after verifying the resolution",
                    code="FORBIDDEN",
                )

        # Validate transition against state machine
        allowed_next = self.VALID_TRANSITIONS.get(ticket.status, [])
        if target_status not in allowed_next:
            raise InvalidTransitionException(
                f"Cannot transition ticket from '{ticket.status}' to '{target_status}'. Allowed transitions: {allowed_next}",
                code="INVALID_STATUS_TRANSITION",
            )

        # RBAC Check: Only the original ticket creator can close a resolved ticket
        if target_status == TicketStatus.CLOSED and ticket.created_by != current_user.id:
            raise ForbiddenException(
                "Only the original ticket creator can close a resolved ticket after verifying the resolution",
                code="FORBIDDEN",
            )

        old_status = ticket.status
        ticket.status = target_status

        if target_status == TicketStatus.RESOLVED:
            ticket.resolved_at = datetime.now()
        elif target_status == TicketStatus.CLOSED:
            ticket.closed_at = datetime.now()

        updated = self.ticket_repo.update(ticket)

        self.ticket_repo.record_status_change(
            ticket_id=ticket.id,
            old_status=old_status,
            new_status=target_status,
            changed_by=current_user.id,
        )

        self.audit_repo.log_action(
            user_id=current_user.id,
            action="TICKET_STATUS_CHANGED",
            entity_type="TICKET",
            entity_id=ticket.id,
            metadata_json=json.dumps({"old_status": old_status, "new_status": target_status, "notes": payload.notes}),
        )

        logger.info(f"Ticket #{ticket.id} status changed from {old_status} to {target_status} by user {current_user.id}")
        return self._enrich_ticket_response(self.ticket_repo.get_by_id_with_relations(updated.id))

    def resolve_ticket(self, ticket_id: int, payload: TicketResolve, current_user: User) -> TicketResponse:
        # RBAC: Support Agents or Admin
        if current_user.role not in [UserRole.SUPPORT_AGENT, UserRole.ADMIN]:
            raise ForbiddenException("Only Support Agents or Admins can resolve tickets", code="FORBIDDEN")

        ticket = self.ticket_repo.get_by_id_with_relations(ticket_id)
        if not ticket:
            raise NotFoundException(f"Ticket with ID {ticket_id} was not found", code="TICKET_NOT_FOUND")

        if ticket.status in [TicketStatus.RESOLVED, TicketStatus.CLOSED]:
            raise ValidationException(f"Ticket is already in '{ticket.status}' status", code="ALREADY_RESOLVED")

        old_status = ticket.status
        ticket.status = TicketStatus.RESOLVED
        ticket.resolved_at = datetime.now()
        ticket.resolution_notes = payload.resolution_notes.strip()

        updated = self.ticket_repo.update(ticket)

        self.ticket_repo.record_status_change(
            ticket_id=ticket.id,
            old_status=old_status,
            new_status=TicketStatus.RESOLVED,
            changed_by=current_user.id,
        )

        self.audit_repo.log_action(
            user_id=current_user.id,
            action="TICKET_RESOLVED",
            entity_type="TICKET",
            entity_id=ticket.id,
            metadata_json=json.dumps({"resolution_notes": payload.resolution_notes}),
        )

        logger.info(f"Ticket #{ticket.id} marked as RESOLVED by user {current_user.id}")
        return self._enrich_ticket_response(self.ticket_repo.get_by_id_with_relations(updated.id))

    def close_ticket(self, ticket_id: int, current_user: User) -> TicketResponse:
        """
        Closes a ticket after verification by the original ticket creator.
        Enforces:
        1. Ticket must be in RESOLVED status (unresolved tickets cannot be closed).
        2. Only original ticket creator can close (Employee, Support Agent, or Admin creator).
        """
        ticket = self.ticket_repo.get_by_id_with_relations(ticket_id)
        if not ticket:
            raise NotFoundException(f"Ticket with ID {ticket_id} was not found", code="TICKET_NOT_FOUND")

        # 1. Unresolved tickets cannot be closed
        if ticket.status != TicketStatus.RESOLVED:
            raise InvalidTransitionException(
                f"Cannot close ticket in '{ticket.status}' status. Only RESOLVED tickets can be verified and closed.",
                code="INVALID_STATUS_TRANSITION",
            )

        # 2. Permission check: Only original creator can close
        if ticket.created_by != current_user.id:
            raise ForbiddenException(
                "Only the original ticket creator can close a resolved ticket after verifying the resolution",
                code="FORBIDDEN",
            )

        old_status = ticket.status
        ticket.status = TicketStatus.CLOSED
        ticket.closed_at = datetime.now()

        updated = self.ticket_repo.update(ticket)

        self.ticket_repo.record_status_change(
            ticket_id=ticket.id,
            old_status=old_status,
            new_status=TicketStatus.CLOSED,
            changed_by=current_user.id,
        )

        self.audit_repo.log_action(
            user_id=current_user.id,
            action="TICKET_CLOSED",
            entity_type="TICKET",
            entity_id=ticket.id,
        )

        logger.info(f"Ticket #{ticket.id} CLOSED by original creator {current_user.id}")
        return self._enrich_ticket_response(self.ticket_repo.get_by_id_with_relations(updated.id))

    def reopen_ticket(self, ticket_id: int, payload: TicketReopen, current_user: User) -> TicketResponse:
        """
        Reopens a ticket if the issue persists.
        Employees can reopen their own tickets; Admins can reopen any ticket.
        """
        ticket = self.ticket_repo.get_by_id_with_relations(ticket_id)
        if not ticket:
            raise NotFoundException(f"Ticket with ID {ticket_id} was not found", code="TICKET_NOT_FOUND")

        # RBAC Check
        if current_user.role == UserRole.EMPLOYEE and ticket.created_by != current_user.id:
            raise ForbiddenException("You cannot reopen another employee's ticket", code="FORBIDDEN")

        # Business Rule: only RESOLVED or CLOSED tickets can be reopened
        if ticket.status not in [TicketStatus.RESOLVED, TicketStatus.CLOSED]:
            raise ValidationException(f"Only tickets in RESOLVED or CLOSED status can be reopened. Current: {ticket.status}", code="CANNOT_REOPEN")

        old_status = ticket.status
        ticket.status = TicketStatus.REOPENED
        ticket.resolved_at = None
        ticket.closed_at = None

        # When reopening, extend SLA or re-evaluate deadline
        ticket.due_at = SLAService.calculate_due_date(datetime.now(), ticket.priority)

        updated = self.ticket_repo.update(ticket)

        self.ticket_repo.record_status_change(
            ticket_id=ticket.id,
            old_status=old_status,
            new_status=TicketStatus.REOPENED,
            changed_by=current_user.id,
        )

        self.audit_repo.log_action(
            user_id=current_user.id,
            action="TICKET_REOPENED",
            entity_type="TICKET",
            entity_id=ticket.id,
            metadata_json=json.dumps({"reopen_reason": payload.reason}),
        )

        logger.info(f"Ticket #{ticket.id} REOPENED by user {current_user.id} with reason: {payload.reason}")
        return self._enrich_ticket_response(self.ticket_repo.get_by_id_with_relations(updated.id))

    def delete_ticket(self, ticket_id: int, current_user: User) -> None:
        """Admin-only hard delete."""
        if current_user.role != UserRole.ADMIN:
            raise ForbiddenException("Only administrators can delete tickets", code="ADMIN_REQUIRED")

        ticket = self.ticket_repo.get_by_id(ticket_id)
        if not ticket:
            raise NotFoundException(f"Ticket with ID {ticket_id} was not found", code="TICKET_NOT_FOUND")

        self.ticket_repo.delete(ticket)

        self.audit_repo.log_action(
            user_id=current_user.id,
            action="TICKET_DELETED",
            entity_type="TICKET",
            entity_id=ticket_id,
        )
        logger.info(f"Ticket #{ticket_id} deleted by admin {current_user.id}")

    def get_status_history(self, ticket_id: int, current_user: User) -> List[TicketStatusHistoryResponse]:
        ticket = self.ticket_repo.get_by_id(ticket_id)
        if not ticket:
            raise NotFoundException(f"Ticket with ID {ticket_id} was not found", code="TICKET_NOT_FOUND")

        if current_user.role == UserRole.EMPLOYEE and ticket.created_by != current_user.id:
            raise ForbiddenException("You cannot view status history for another employee's ticket", code="FORBIDDEN")

        histories = self.ticket_repo.get_status_history(ticket_id)
        return [
            TicketStatusHistoryResponse(
                id=h.id,
                ticket_id=h.ticket_id,
                old_status=h.old_status,
                new_status=h.new_status,
                changed_by=h.changed_by,
                changed_at=h.changed_at,
                author_name=h.author.name if h.author else "System",
                author_role=h.author.role if h.author else "SYSTEM",
            )
            for h in histories
        ]
