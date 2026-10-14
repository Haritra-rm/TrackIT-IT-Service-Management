from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from app.core.exceptions import AppException
from app.core.logging import logger


async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    """Handles all domain-specific application exceptions."""
    logger.warning(f"AppException: code={exc.code}, message={exc.message}, path={request.url.path}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "code": exc.code,
                "message": exc.message,
                "details": exc.details,
            },
        },
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Formats Pydantic request validation errors into standard TrackIT error format."""
    errors = []
    for err in exc.errors():
        field = " -> ".join(str(loc) for loc in err.get("loc", []))
        msg = err.get("msg", "Invalid value")
        errors.append({"field": field, "message": msg})

    logger.warning(f"Validation error on {request.url.path}: {errors}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Input validation failed. Please check the submitted fields.",
                "details": errors,
            },
        },
    )


async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Catches unhandled errors, logs complete traceback, and prevents information leakage."""
    logger.exception(f"Unhandled system error on {request.method} {request.url.path}: {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred while processing your request. Please contact support.",
            },
        },
    )
