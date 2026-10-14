from typing import List
from sqlalchemy.orm import Session

from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryUpdate, CategoryResponse
from app.repositories.category_repository import CategoryRepository
from app.repositories.audit_repository import AuditRepository
from app.core.exceptions import NotFoundException, ConflictException
from app.core.logging import logger


class CategoryService:
    def __init__(self, db: Session):
        self.db = db
        self.category_repo = CategoryRepository(db)
        self.audit_repo = AuditRepository(db)

    def get_all(self, active_only: bool = False) -> List[CategoryResponse]:
        if active_only:
            categories = self.category_repo.get_active_categories()
        else:
            categories = self.category_repo.get_all()

        results = []
        for cat in categories:
            resp = CategoryResponse.model_validate(cat)
            resp.ticket_count = len(cat.tickets) if hasattr(cat, "tickets") else 0
            results.append(resp)
        return results

    def create_category(self, payload: CategoryCreate, user_id: int) -> CategoryResponse:
        existing = self.category_repo.get_by_name(payload.name)
        if existing:
            raise ConflictException(f"Category '{payload.name}' already exists", code="CATEGORY_EXISTS")

        category = Category(
            name=payload.name.strip(),
            description=payload.description.strip() if payload.description else None,
            is_active=payload.is_active,
        )
        created = self.category_repo.create(category)

        self.audit_repo.log_action(
            user_id=user_id,
            action="CATEGORY_CREATED",
            entity_type="CATEGORY",
            entity_id=created.id,
        )
        logger.info(f"Category '{created.name}' created by user {user_id}")
        return CategoryResponse.model_validate(created)

    def update_category(self, category_id: int, payload: CategoryUpdate, user_id: int) -> CategoryResponse:
        category = self.category_repo.get_by_id(category_id)
        if not category:
            raise NotFoundException(f"Category with ID {category_id} not found", code="CATEGORY_NOT_FOUND")

        if payload.name and payload.name.lower().strip() != category.name.lower():
            existing = self.category_repo.get_by_name(payload.name)
            if existing and existing.id != category.id:
                raise ConflictException(f"Category '{payload.name}' already exists", code="CATEGORY_EXISTS")
            category.name = payload.name.strip()

        if payload.description is not None:
            category.description = payload.description.strip() if payload.description else None

        if payload.is_active is not None:
            category.is_active = payload.is_active

        updated = self.category_repo.update(category)
        self.audit_repo.log_action(
            user_id=user_id,
            action="CATEGORY_UPDATED",
            entity_type="CATEGORY",
            entity_id=updated.id,
        )
        logger.info(f"Category {category_id} updated by user {user_id}")
        return CategoryResponse.model_validate(updated)
