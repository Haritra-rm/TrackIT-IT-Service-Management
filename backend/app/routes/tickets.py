from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.ticket import (
    TicketCreate,
    TicketUpdate,
    TicketAssign,
    TicketStatusUpdate,
    TicketResolve,
    TicketReopen,
    TicketResponse,
    TicketStatusHistoryResponse,
    PriorityRecommendationRequest,
    PriorityRecommendationResponse,
)
from app.schemas.comment import CommentCreate, CommentResponse
from app.schemas.common import ApiResponse, PaginatedResponse
from app.services.ticket_service import TicketService
from app.services.comment_service import CommentService
from app.services.priority_service import PriorityRecommendationEngine
from app.core.dependencies import get_current_user, require_admin
from app.models.user import User

router = APIRouter(prefix="/tickets", tags=["Tickets"])


@router.post(
    "",
    response_model=ApiResponse[TicketResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create a new support ticket",
)
def create_ticket(
    payload: TicketCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = TicketService(db)
    ticket = service.create_ticket(payload, current_user)
    return ApiResponse(success=True, data=ticket, message="Ticket created successfully")


@router.get(
    "",
    response_model=ApiResponse[PaginatedResponse[TicketResponse]],
    summary="List, search, filter and paginate tickets",
)
def list_tickets(
    search: Optional[str] = Query(None, description="Search by title, description or ticket ID"),
    ticket_id: Optional[int] = Query(None, description="Direct match by ticket ID"),
    status: Optional[str] = Query(None, description="Filter by status: OPEN, ASSIGNED, IN_PROGRESS, RESOLVED, CLOSED, REOPENED"),
    priority: Optional[str] = Query(None, description="Filter by priority: LOW, MEDIUM, HIGH, CRITICAL"),
    category_id: Optional[int] = Query(None, description="Filter by category ID"),
    assigned_to: Optional[int] = Query(None, description="Filter by assigned agent ID"),
    created_by: Optional[int] = Query(None, description="Filter by creator ID (Admin/Agent only; ignored for employees)"),
    from_date: Optional[datetime] = Query(None, description="Filter by created date >= from_date"),
    to_date: Optional[datetime] = Query(None, description="Filter by created date <= to_date"),
    sort_by: str = Query("created_at", description="Field to sort by: created_at, priority, due_at, status"),
    sort_order: str = Query("desc", description="Sorting direction: asc or desc"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = TicketService(db)
    items, total = service.list_tickets(
        current_user=current_user,
        search=search,
        ticket_id=ticket_id,
        status=status,
        priority=priority,
        category_id=category_id,
        assigned_to=assigned_to,
        created_by=created_by,
        from_date=from_date,
        to_date=to_date,
        sort_by=sort_by,
        sort_order=sort_order,
        page=page,
        page_size=page_size,
    )
    total_pages = (total + page_size - 1) // page_size if total > 0 else 1

    return ApiResponse(
        success=True,
        data=PaginatedResponse(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        ),
    )


@router.post(
    "/recommend-priority",
    response_model=ApiResponse[PriorityRecommendationResponse],
    summary="Get smart priority recommendation based on impact and blast radius",
)
def recommend_priority(
    payload: PriorityRecommendationRequest,
    current_user: User = Depends(get_current_user),
):
    result = PriorityRecommendationEngine.recommend(
        category_name=payload.category_name or "",
        affected_users=payload.affected_users,
        business_impact=payload.business_impact,
        is_security_incident=payload.is_security_incident,
        is_system_down=payload.is_system_down,
    )
    return ApiResponse(
        success=True,
        data=PriorityRecommendationResponse(**result),
        message="Priority recommendation calculated",
    )


@router.get(
    "/{id}",
    response_model=ApiResponse[TicketResponse],
    summary="Get ticket details by ID",
)
def get_ticket(
    id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = TicketService(db)
    ticket = service.get_ticket(id, current_user)
    return ApiResponse(success=True, data=ticket)


@router.put(
    "/{id}",
    response_model=ApiResponse[TicketResponse],
    summary="Update ticket details (Title, Description, Category, Priority)",
)
def update_ticket(
    id: int,
    payload: TicketUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = TicketService(db)
    ticket = service.update_ticket(id, payload, current_user)
    return ApiResponse(success=True, data=ticket, message="Ticket updated successfully")


@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a ticket (Admin only)",
)
def delete_ticket(
    id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    service = TicketService(db)
    service.delete_ticket(id, current_user)
    return None


@router.post(
    "/{id}/assign",
    response_model=ApiResponse[TicketResponse],
    summary="Assign ticket to a support agent or admin",
)
def assign_ticket(
    id: int,
    payload: TicketAssign,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = TicketService(db)
    ticket = service.assign_ticket(id, payload, current_user)
    return ApiResponse(success=True, data=ticket, message="Ticket assigned successfully")


@router.post(
    "/{id}/status",
    response_model=ApiResponse[TicketResponse],
    summary="Advance ticket status according to lifecycle rules",
)
def update_ticket_status(
    id: int,
    payload: TicketStatusUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = TicketService(db)
    ticket = service.update_status(id, payload, current_user)
    return ApiResponse(success=True, data=ticket, message=f"Ticket status changed to {ticket.status}")


@router.post(
    "/{id}/resolve",
    response_model=ApiResponse[TicketResponse],
    summary="Mark ticket as RESOLVED with resolution notes",
)
def resolve_ticket(
    id: int,
    payload: TicketResolve,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = TicketService(db)
    ticket = service.resolve_ticket(id, payload, current_user)
    return ApiResponse(success=True, data=ticket, message="Ticket marked as RESOLVED")


@router.post(
    "/{id}/reopen",
    response_model=ApiResponse[TicketResponse],
    summary="Reopen a resolved or closed ticket if problem persists",
)
def reopen_ticket(
    id: int,
    payload: TicketReopen,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = TicketService(db)
    ticket = service.reopen_ticket(id, payload, current_user)
    return ApiResponse(success=True, data=ticket, message="Ticket reopened successfully")


@router.get(
    "/{id}/history",
    response_model=ApiResponse[List[TicketStatusHistoryResponse]],
    summary="Get chronological status history for a ticket",
)
def get_ticket_history(
    id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = TicketService(db)
    history = service.get_status_history(id, current_user)
    return ApiResponse(success=True, data=history)


@router.get(
    "/{id}/comments",
    response_model=ApiResponse[List[CommentResponse]],
    summary="Get comments for a ticket",
)
def get_ticket_comments(
    id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = CommentService(db)
    comments = service.get_ticket_comments(id, current_user)
    return ApiResponse(success=True, data=comments)


@router.post(
    "/{id}/comments",
    response_model=ApiResponse[CommentResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Add a comment to a ticket",
)
def add_ticket_comment(
    id: int,
    payload: CommentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = CommentService(db)
    comment = service.add_comment(id, payload, current_user)
    return ApiResponse(success=True, data=comment, message="Comment posted successfully")
