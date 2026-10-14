from typing import List
from sqlalchemy.orm import Session

from app.models.comment import Comment
from app.models.user import User, UserRole
from app.schemas.comment import CommentCreate, CommentResponse
from app.repositories.comment_repository import CommentRepository
from app.repositories.ticket_repository import TicketRepository
from app.repositories.audit_repository import AuditRepository
from app.core.exceptions import NotFoundException, ForbiddenException
from app.core.logging import logger


class CommentService:
    def __init__(self, db: Session):
        self.db = db
        self.comment_repo = CommentRepository(db)
        self.ticket_repo = TicketRepository(db)
        self.audit_repo = AuditRepository(db)

    def add_comment(self, ticket_id: int, payload: CommentCreate, current_user: User) -> CommentResponse:
        ticket = self.ticket_repo.get_by_id(ticket_id)
        if not ticket:
            raise NotFoundException(f"Ticket with ID {ticket_id} was not found", code="TICKET_NOT_FOUND")

        # RBAC Check:
        # Employee can only comment on their own tickets
        if current_user.role == UserRole.EMPLOYEE and ticket.created_by != current_user.id:
            raise ForbiddenException("You cannot comment on tickets created by other employees", code="FORBIDDEN")

        comment = Comment(
            ticket_id=ticket.id,
            user_id=current_user.id,
            comment=payload.comment.strip(),
        )
        created = self.comment_repo.create(comment)

        self.audit_repo.log_action(
            user_id=current_user.id,
            action="COMMENT_ADDED",
            entity_type="TICKET",
            entity_id=ticket.id,
        )

        logger.info(f"Comment added to ticket {ticket_id} by user {current_user.id}")

        return CommentResponse(
            id=created.id,
            ticket_id=created.ticket_id,
            user_id=created.user_id,
            comment=created.comment,
            created_at=created.created_at,
            user_name=current_user.name,
            user_role=current_user.role,
        )

    def get_ticket_comments(self, ticket_id: int, current_user: User) -> List[CommentResponse]:
        ticket = self.ticket_repo.get_by_id(ticket_id)
        if not ticket:
            raise NotFoundException(f"Ticket with ID {ticket_id} was not found", code="TICKET_NOT_FOUND")

        if current_user.role == UserRole.EMPLOYEE and ticket.created_by != current_user.id:
            raise ForbiddenException("You cannot view comments for another employee's ticket", code="FORBIDDEN")

        comments = self.comment_repo.get_by_ticket_id(ticket_id)
        return [
            CommentResponse(
                id=c.id,
                ticket_id=c.ticket_id,
                user_id=c.user_id,
                comment=c.comment,
                created_at=c.created_at,
                user_name=c.user.name if c.user else "Unknown",
                user_role=c.user.role if c.user else "USER",
            )
            for c in comments
        ]
