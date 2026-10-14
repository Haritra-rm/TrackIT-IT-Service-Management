from typing import Optional, List
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.user import UserResponse, UserUpdate, UserStatusUpdate
from app.schemas.common import ApiResponse, PaginatedResponse
from app.services.user_service import UserService
from app.core.dependencies import get_current_user, require_admin, require_support_or_admin
from app.models.user import User

router = APIRouter(prefix="/users", tags=["Users"])


@router.get(
    "",
    response_model=ApiResponse[PaginatedResponse[UserResponse]],
    summary="List and filter users (Admin & Support Agents)",
)
def list_users(
    search: Optional[str] = Query(None, description="Search by name or email"),
    role: Optional[str] = Query(None, description="Filter by role: EMPLOYEE, SUPPORT_AGENT, ADMIN"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(require_support_or_admin),
    db: Session = Depends(get_db),
):
    service = UserService(db)
    items, total = service.list_users(
        search=search, role=role, is_active=is_active, page=page, page_size=page_size
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


@router.get(
    "/agents",
    response_model=ApiResponse[List[UserResponse]],
    summary="Get active support agents list for ticket assignment",
)
def get_agents(
    current_user: User = Depends(require_support_or_admin),
    db: Session = Depends(get_db),
):
    service = UserService(db)
    agents = service.get_support_agents()
    return ApiResponse(success=True, data=agents)


@router.get(
    "/{id}",
    response_model=ApiResponse[UserResponse],
    summary="Get user details by ID",
)
def get_user_by_id(
    id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = UserService(db)
    user = service.get_user_by_id(id)
    return ApiResponse(success=True, data=user)


@router.put(
    "/{id}",
    response_model=ApiResponse[UserResponse],
    summary="Update user details",
)
def update_user(
    id: int,
    payload: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = UserService(db)
    user = service.update_user(id, payload, current_user)
    return ApiResponse(success=True, data=user, message="User updated successfully")


@router.patch(
    "/{id}/status",
    response_model=ApiResponse[UserResponse],
    summary="Activate or deactivate a user account (Admin only)",
)
def update_user_status(
    id: int,
    payload: UserStatusUpdate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    service = UserService(db)
    user = service.set_user_status(id, payload, current_user)
    return ApiResponse(
        success=True,
        data=user,
        message=f"User account {'activated' if payload.is_active else 'deactivated'} successfully",
    )
