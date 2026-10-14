import datetime
from datetime import datetime as dt, timedelta, timezone
from typing import Any, Dict, Optional
import jwt
from passlib.context import CryptContext
import bcrypt

from app.core.config import settings
from app.core.exceptions import UnauthorizedException

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a raw password against the stored bcrypt hash."""
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception:
        # Fallback to direct bcrypt if passlib encounters issues
        try:
            return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
        except Exception:
            return False


def get_password_hash(password: str) -> str:
    """Generate a secure salted bcrypt hash for a given password."""
    try:
        return pwd_context.hash(password)
    except Exception:
        # Fallback to direct bcrypt
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Generate a signed JWT token containing the user identity, role, and expiration.
    """
    to_encode = data.copy()
    now = dt.now(timezone.utc)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({
        "exp": expire,
        "iat": now,
        "nbf": now,
    })

    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )
    return encoded_jwt


def decode_access_token(token: str) -> Dict[str, Any]:
    """
    Decode and validate a JWT access token.
    Raises UnauthorizedException on expired or invalid signatures.
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise UnauthorizedException("Authentication token has expired", code="TOKEN_EXPIRED")
    except jwt.InvalidTokenError:
        raise UnauthorizedException("Invalid authentication token", code="INVALID_TOKEN")
