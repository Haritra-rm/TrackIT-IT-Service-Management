import json
from datetime import timedelta
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import get_password_hash, verify_password, create_access_token
from app.core.exceptions import UnauthorizedException, ConflictException, ValidationException
from app.core.logging import logger
from app.models.user import User, UserRole
from app.schemas.auth import RegisterRequest, LoginRequest, TokenResponse
from app.schemas.user import UserResponse
from app.repositories.user_repository import UserRepository
from app.repositories.audit_repository import AuditRepository


class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)
        self.audit_repo = AuditRepository(db)

    def register_user(self, payload: RegisterRequest) -> UserResponse:
        # Check if email is already in use
        existing_user = self.user_repo.get_by_email(payload.email)
        if existing_user:
            logger.warning(f"Registration failed: Email {payload.email} already exists")
            raise ConflictException(f"User with email '{payload.email}' already exists", code="EMAIL_ALREADY_EXISTS")

        # Validate role
        requested_role = (payload.role or UserRole.EMPLOYEE).upper()
        if requested_role not in UserRole.ALL_ROLES:
            raise ValidationException(f"Invalid role '{requested_role}'. Must be one of: {UserRole.ALL_ROLES}")

        # Hash password securely
        hashed_password = get_password_hash(payload.password)

        new_user = User(
            name=payload.name.strip(),
            email=payload.email.lower().strip(),
            password_hash=hashed_password,
            role=requested_role,
            is_active=True,
        )
        created_user = self.user_repo.create(new_user)

        # Log audit entry
        self.audit_repo.log_action(
            user_id=created_user.id,
            action="USER_REGISTERED",
            entity_type="USER",
            entity_id=created_user.id,
            metadata_json=json.dumps({"role": created_user.role, "email": created_user.email}),
        )

        logger.info(f"User registered successfully: id={created_user.id}, email={created_user.email}, role={created_user.role}")
        return UserResponse.model_validate(created_user)

    def authenticate_user(self, payload: LoginRequest) -> TokenResponse:
        user = self.user_repo.get_by_email(payload.email)
        if not user:
            logger.warning(f"Failed login attempt: non-existent email '{payload.email}'")
            raise UnauthorizedException("Invalid email or password", code="INVALID_CREDENTIALS")

        if not verify_password(payload.password, user.password_hash):
            logger.warning(f"Failed login attempt: incorrect password for user id={user.id}")
            raise UnauthorizedException("Invalid email or password", code="INVALID_CREDENTIALS")

        if not user.is_active:
            logger.warning(f"Login rejected: account id={user.id} is deactivated")
            raise UnauthorizedException("User account has been deactivated. Please contact an Administrator.", code="ACCOUNT_DEACTIVATED")

        # Create JWT Access Token
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        token_data = {
            "sub": str(user.id),
            "email": user.email,
            "role": user.role,
            "name": user.name,
        }
        token = create_access_token(data=token_data, expires_delta=access_token_expires)

        # Log successful login
        self.audit_repo.log_action(
            user_id=user.id,
            action="USER_LOGIN",
            entity_type="USER",
            entity_id=user.id,
        )

        logger.info(f"User login successful: id={user.id}, role={user.role}")
        return TokenResponse(
            access_token=token,
            token_type="bearer",
            user=UserResponse.model_validate(user),
        )
