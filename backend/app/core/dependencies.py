from typing import List, Callable
from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.core.exceptions import UnauthorizedException, ForbiddenException
from app.database.session import get_db
from app.models.user import User, UserRole
from app.repositories.user_repository import UserRepository

# HTTPBearer extracts the "Bearer <token>" header cleanly
oauth2_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """
    Decodes the JWT Bearer token, extracts the subject (user_id), and fetches the User.
    Enforces that the user exists and is active.
    """
    if not credentials:
        raise UnauthorizedException("Authentication token is required", code="MISSING_TOKEN")

    token = credentials.credentials
    payload = decode_access_token(token)

    user_id_str = payload.get("sub")
    if not user_id_str:
        raise UnauthorizedException("Invalid token payload", code="INVALID_TOKEN")

    try:
        user_id = int(user_id_str)
    except ValueError:
        raise UnauthorizedException("Invalid user identifier in token", code="INVALID_TOKEN")

    user_repo = UserRepository(db)
    user = user_repo.get_by_id(user_id)

    if not user:
        raise UnauthorizedException("User associated with this token no longer exists", code="USER_NOT_FOUND")

    if not user.is_active:
        raise ForbiddenException("User account is disabled", code="USER_DISABLED")

    return user


def require_role(allowed_roles: List[str]) -> Callable[[User], User]:
    """
    Role-Based Access Control (RBAC) Dependency Factory.
    Ensures that the calling user has one of the allowed roles.
    Raises 403 ForbiddenException if unauthorized.
    """
    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles:
            raise ForbiddenException(
                f"Access denied. Required roles: {allowed_roles}. Your role: {current_user.role}",
                code="INSUFFICIENT_PERMISSIONS",
            )
        return current_user

    return role_checker


# Convenient pre-configured role dependencies
require_admin = require_role([UserRole.ADMIN])
require_support_or_admin = require_role([UserRole.SUPPORT_AGENT, UserRole.ADMIN])
require_any_authenticated = get_current_user
