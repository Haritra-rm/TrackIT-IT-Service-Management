from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.auth import RegisterRequest, LoginRequest, TokenResponse
from app.schemas.user import UserResponse
from app.schemas.common import ApiResponse
from app.services.auth_service import AuthService
from app.core.dependencies import get_current_user
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=ApiResponse[UserResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Register a new employee account",
)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    """Registers a new user and returns user info."""
    service = AuthService(db)
    user = service.register_user(payload)
    return ApiResponse(success=True, data=user, message="User registered successfully")


@router.post(
    "/login",
    response_model=ApiResponse[TokenResponse],
    summary="User login with JWT token generation",
)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    """Authenticates credentials and returns a signed JWT bearer token."""
    service = AuthService(db)
    token_response = service.authenticate_user(payload)
    return ApiResponse(success=True, data=token_response, message="Login successful")


@router.get(
    "/me",
    response_model=ApiResponse[UserResponse],
    summary="Get current authenticated user profile",
)
def get_me(current_user: User = Depends(get_current_user)):
    """Returns the profile of the currently logged-in user."""
    return ApiResponse(
        success=True,
        data=UserResponse.model_validate(current_user),
        message="Profile retrieved",
    )
