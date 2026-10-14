from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError

from app.core.config import settings
from app.core.exceptions import AppException
from app.database.connection import engine
from app.database.base import Base
import app.models  # noqa: F401

from app.middleware.error_handler import (
    app_exception_handler,
    validation_exception_handler,
    global_exception_handler,
)
from app.middleware.logging_middleware import RequestLoggingMiddleware

from app.routes.auth import router as auth_router
from app.routes.users import router as users_router
from app.routes.categories import router as categories_router
from app.routes.tickets import router as tickets_router
from app.routes.dashboard import router as dashboard_router
from app.routes.audit import router as audit_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Ensure database tables exist on startup and handle clean teardown."""
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="""
# TrackIT — Smart IT Service & Issue Management Platform API

Enterprise-grade IT Service Management platform supporting full ticket lifecycle,
intelligent priority scoring, dynamic SLA compliance tracking, RBAC, and analytics.

### Architecture & Capabilities:
* **Roles**: EMPLOYEE, SUPPORT_AGENT, ADMIN
* **Core Workflow**: OPEN → ASSIGNED → IN_PROGRESS → RESOLVED → CLOSED (with REOPENED loop)
* **SLA Engine**: Real-time evaluation based on urgency rules
* **Security**: JWT Authentication (HS256) & bcrypt password hashing
    """,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/api/v1/openapi.json",
    lifespan=lifespan,
)

# 1. Logging Middleware
app.add_middleware(RequestLoggingMiddleware)

# 2. CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3. Exception Handlers
app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, global_exception_handler)

# 4. Include Versioned API Routers
API_V1_PREFIX = "/api/v1"
app.include_router(auth_router, prefix=API_V1_PREFIX)
app.include_router(users_router, prefix=API_V1_PREFIX)
app.include_router(categories_router, prefix=API_V1_PREFIX)
app.include_router(tickets_router, prefix=API_V1_PREFIX)
app.include_router(dashboard_router, prefix=API_V1_PREFIX)
app.include_router(audit_router, prefix=API_V1_PREFIX)


@app.get("/health", tags=["Health"])
def health_check():
    """Liveness and readiness probe for cloud deployments and load balancers."""
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
    }
