import json
from typing import Optional, List, Tuple
from sqlalchemy.orm import Session

from app.models.user import User, UserRole
from app.schemas.user import UserResponse, UserUpdate, UserStatusUpdate
from app.repositories.user_repository import UserRepository
from app.repositories.audit_repository import AuditRepository
from app.core.exceptions import NotFoundException, ForbiddenException, ConflictException, ValidationException
from app.core.logging import logger


class UserService:
    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)
        self.audit_repo = AuditRepository(db)

    def get_user_by_id(self, user_id: int) -> UserResponse:
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundException(f"User with ID {user_id} was not found", code="USER_NOT_FOUND")
        return UserResponse.model_validate(user)

    def list_users(
        self,
        search: Optional[str] = None,
        role: Optional[str] = None,
        is_active: Optional[bool] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> Tuple[List[UserResponse], int]:
        skip = (page - 1) * page_size
        users = self.user_repo.search_users(search=search, role=role, is_active=is_active, skip=skip, limit=page_size)
        total = self.user_repo.count_users(search=search, role=role, is_active=is_active)
        return [UserResponse.model_validate(u) for u in users], total

    def get_support_agents(self) -> List[UserResponse]:
        agents = self.user_repo.get_active_agents()
        return [UserResponse.model_validate(a) for a in agents]

    def update_user(self, user_id: int, payload: UserUpdate, actor: User) -> UserResponse:
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundException(f"User with ID {user_id} was not found", code="USER_NOT_FOUND")

        # RBAC Check: Only Admin can update other users or change roles/status
        if actor.id != user.id and actor.role != UserRole.ADMIN:
            raise ForbiddenException("You cannot edit another user's profile", code="FORBIDDEN")

        # Non-admins cannot change their own role or active status
        if actor.role != UserRole.ADMIN:
            if payload.role and payload.role != user.role:
                raise ForbiddenException("Non-admins cannot change their role", code="FORBIDDEN")
            if payload.is_active is not None and payload.is_active != user.is_active:
                raise ForbiddenException("Non-admins cannot change their active status", code="FORBIDDEN")

        # If email is being changed, verify uniqueness
        if payload.email and payload.email.lower().strip() != user.email:
            existing = self.user_repo.get_by_email(payload.email)
            if existing and existing.id != user.id:
                raise ConflictException("Email is already registered to another user", code="EMAIL_EXISTS")
            user.email = payload.email.lower().strip()

        if payload.name:
            user.name = payload.name.strip()

        if payload.role and actor.role == UserRole.ADMIN:
            if payload.role not in UserRole.ALL_ROLES:
                raise ValidationException(f"Invalid role '{payload.role}'")
            user.role = payload.role

        if payload.is_active is not None and actor.role == UserRole.ADMIN:
            user.is_active = payload.is_active

        updated = self.user_repo.update(user)

        self.audit_repo.log_action(
            user_id=actor.id,
            action="USER_UPDATED",
            entity_type="USER",
            entity_id=user.id,
            metadata_json=json.dumps({"updated_by": actor.id, "target_user": user.id}),
        )

        logger.info(f"User {user.id} updated by actor {actor.id}")
        return UserResponse.model_validate(updated)

    def set_user_status(self, user_id: int, payload: UserStatusUpdate, actor: User) -> UserResponse:
        """Admin-only endpoint to activate or deactivate a user account."""
        if actor.role != UserRole.ADMIN:
            raise ForbiddenException("Only administrators can activate/deactivate accounts", code="ADMIN_REQUIRED")

        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundException(f"User with ID {user_id} was not found", code="USER_NOT_FOUND")

        # Prevent admin from deactivating themselves
        if user.id == actor.id and not payload.is_active:
            raise ValidationException("Administrators cannot deactivate their own account", code="SELF_DEACTIVATION_PROHIBITED")

        user.is_active = payload.is_active
        updated = self.user_repo.update(user)

        self.audit_repo.log_action(
            user_id=actor.id,
            action="USER_STATUS_CHANGED",
            entity_type="USER",
            entity_id=user.id,
            metadata_json=json.dumps({"is_active": payload.is_active}),
        )

        logger.info(f"User {user.id} status set to is_active={payload.is_active} by admin {actor.id}")
        return UserResponse.model_validate(updated)
