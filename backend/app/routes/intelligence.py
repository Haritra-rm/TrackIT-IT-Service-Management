import json
from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.core.dependencies import get_current_user
from app.core.exceptions import NotFoundException, ForbiddenException
from app.models.user import User, UserRole
from app.models.ticket import Ticket
from app.repositories.ticket_repository import TicketRepository
from app.repositories.audit_repository import AuditRepository
from app.services.related_ticket_service import RelatedTicketService
from app.services.escalation_service import EscalationService
from app.schemas.intelligence import RelatedTicketsResponse, EscalationAssessmentResponse
from app.schemas.common import ApiResponse
from app.core.logging import logger

router = APIRouter(prefix="/intelligence", tags=["Incident Intelligence"])


def _get_authorized_ticket(ticket_id: int, current_user: User, db: Session) -> Ticket:
    """
    Fetch ticket with relations and enforce strict RBAC:
    - Employees can only view intelligence for tickets they created.
    - Support Agents and Admins can view intelligence for any ticket.
    """
    ticket_repo = TicketRepository(db)
    ticket = ticket_repo.get_by_id_with_relations(ticket_id)
    if not ticket:
        raise NotFoundException(f"Ticket with ID {ticket_id} was not found", code="TICKET_NOT_FOUND")

    if current_user.role == UserRole.EMPLOYEE and ticket.created_by != current_user.id:
        logger.warning(
            f"RBAC Violation: Employee #{current_user.id} attempted to access intelligence for Ticket #{ticket_id}"
        )
        raise ForbiddenException("You are not authorized to view intelligence for this ticket", code="FORBIDDEN")

    return ticket


@router.get(
    "/tickets/{ticket_id}/related",
    response_model=ApiResponse[RelatedTicketsResponse],
    summary="Detect potentially related tickets using TF-IDF and Cosine Similarity",
)
def get_related_tickets(
    ticket_id: int,
    threshold: float = Query(
        RelatedTicketService.DEFAULT_SIMILARITY_THRESHOLD,
        ge=0.1,
        le=1.0,
        description="Cosine similarity cutoff threshold (default: 0.65)",
    ),
    limit: int = Query(
        RelatedTicketService.DEFAULT_MAX_RESULTS,
        ge=1,
        le=20,
        description="Maximum number of related tickets to return",
    ),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    ticket = _get_authorized_ticket(ticket_id, current_user, db)

    service = RelatedTicketService(db)
    result = service.find_related_tickets(ticket, threshold=threshold, limit=limit)

    # Record lightweight audit log
    try:
        AuditRepository(db).log_action(
            action="RELATED_TICKETS_VIEWED",
            entity_type="TICKET",
            user_id=current_user.id,
            entity_id=ticket.id,
            metadata_json=json.dumps({
                "threshold": threshold,
                "matches_found": len(result.related_tickets),
            }),
        )
    except Exception as e:
        logger.debug(f"Audit log skipped for related tickets view: {e}")

    return ApiResponse(
        success=True,
        data=result,
        message=f"Found {len(result.related_tickets)} potentially related tickets",
    )


@router.get(
    "/tickets/{ticket_id}/escalation",
    response_model=ApiResponse[EscalationAssessmentResponse],
    summary="Calculate rule-based smart escalation assessment for a ticket",
)
def get_escalation_assessment(
    ticket_id: int,
    threshold: float = Query(
        RelatedTicketService.DEFAULT_SIMILARITY_THRESHOLD,
        ge=0.1,
        le=1.0,
        description="Similarity threshold used to count related tickets",
    ),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    ticket = _get_authorized_ticket(ticket_id, current_user, db)

    # 1. Determine related tickets count
    related_service = RelatedTicketService(db)
    related_res = related_service.find_related_tickets(ticket, threshold=threshold, limit=20)
    related_count = len(related_res.related_tickets)

    # 2. Compute rule-based escalation recommendation
    assessment = EscalationService.assess_ticket(ticket, related_tickets_count=related_count)

    # Record lightweight audit log
    try:
        AuditRepository(db).log_action(
            action="ESCALATION_ASSESSMENT_GENERATED",
            entity_type="TICKET",
            user_id=current_user.id,
            entity_id=ticket.id,
            metadata_json=json.dumps({
                "recommendation": assessment.recommendation,
                "risk_score": assessment.risk_score,
                "related_count": related_count,
            }),
        )
    except Exception as e:
        logger.debug(f"Audit log skipped for escalation assessment: {e}")

    return ApiResponse(
        success=True,
        data=assessment,
        message="Escalation assessment calculated successfully",
    )
