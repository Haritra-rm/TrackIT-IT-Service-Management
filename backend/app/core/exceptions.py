from typing import Any, Optional


class AppException(Exception):
    """Base application exception for TrackIT"""

    def __init__(
        self,
        code: str,
        message: str,
        status_code: int = 400,
        details: Optional[Any] = None,
    ):
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details
        super().__init__(self.message)


class NotFoundException(AppException):
    def __init__(self, message: str, code: str = "NOT_FOUND"):
        super().__init__(code=code, message=message, status_code=404)


class UnauthorizedException(AppException):
    def __init__(self, message: str = "Could not validate credentials", code: str = "UNAUTHORIZED"):
        super().__init__(code=code, message=message, status_code=401)


class ForbiddenException(AppException):
    def __init__(self, message: str = "You do not have permission to perform this action", code: str = "FORBIDDEN"):
        super().__init__(code=code, message=message, status_code=403)


class ConflictException(AppException):
    def __init__(self, message: str, code: str = "CONFLICT"):
        super().__init__(code=code, message=message, status_code=409)


class ValidationException(AppException):
    def __init__(self, message: str, code: str = "VALIDATION_ERROR", details: Optional[Any] = None):
        super().__init__(code=code, message=message, status_code=422, details=details)


class InvalidTransitionException(AppException):
    def __init__(self, message: str, code: str = "INVALID_STATUS_TRANSITION"):
        super().__init__(code=code, message=message, status_code=400)
