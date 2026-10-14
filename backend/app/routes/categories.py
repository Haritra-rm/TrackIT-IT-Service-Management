from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.category import CategoryCreate, CategoryUpdate, CategoryResponse
from app.schemas.common import ApiResponse
from app.services.category_service import CategoryService
from app.core.dependencies import get_current_user, require_admin
from app.models.user import User

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.get(
    "",
    response_model=ApiResponse[List[CategoryResponse]],
    summary="List issue categories",
)
def list_categories(
    active_only: bool = Query(False, description="Filter active categories only"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = CategoryService(db)
    categories = service.get_all(active_only=active_only)
    return ApiResponse(success=True, data=categories)


@router.post(
    "",
    response_model=ApiResponse[CategoryResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create a new ticket category (Admin only)",
)
def create_category(
    payload: CategoryCreate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    service = CategoryService(db)
    category = service.create_category(payload, current_user.id)
    return ApiResponse(
        success=True,
        data=category,
        message="Category created successfully",
    )


@router.put(
    "/{id}",
    response_model=ApiResponse[CategoryResponse],
    summary="Update an existing category (Admin only)",
)
def update_category(
    id: int,
    payload: CategoryUpdate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    service = CategoryService(db)
    category = service.update_category(id, payload, current_user.id)
    return ApiResponse(
        success=True,
        data=category,
        message="Category updated successfully",
    )
