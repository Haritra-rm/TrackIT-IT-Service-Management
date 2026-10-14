from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.dashboard import (
    DashboardSummary,
    StatusCount,
    PriorityCount,
    CategoryCount,
    AgentPerformanceMetric,
)
from app.schemas.common import ApiResponse
from app.services.dashboard_service import DashboardService
from app.core.dependencies import get_current_user, require_support_or_admin
from app.models.user import User

router = APIRouter(prefix="/dashboard", tags=["Dashboard & Analytics"])


@router.get(
    "/summary",
    response_model=ApiResponse[DashboardSummary],
    summary="Get operational summary KPI metrics",
)
def get_dashboard_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = DashboardService(db)
    summary = service.get_summary(current_user)
    return ApiResponse(success=True, data=summary)


@router.get(
    "/tickets-by-status",
    response_model=ApiResponse[List[StatusCount]],
    summary="Get distribution of tickets by lifecycle status",
)
def get_tickets_by_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = DashboardService(db)
    counts = service.get_tickets_by_status(current_user)
    return ApiResponse(success=True, data=counts)


@router.get(
    "/tickets-by-priority",
    response_model=ApiResponse[List[PriorityCount]],
    summary="Get distribution of tickets by priority level",
)
def get_tickets_by_priority(
    current_user: User = Depends(require_support_or_admin),
    db: Session = Depends(get_db),
):
    service = DashboardService(db)
    counts = service.get_tickets_by_priority()
    return ApiResponse(success=True, data=counts)


@router.get(
    "/tickets-by-category",
    response_model=ApiResponse[List[CategoryCount]],
    summary="Get distribution of tickets by problem category",
)
def get_tickets_by_category(
    current_user: User = Depends(require_support_or_admin),
    db: Session = Depends(get_db),
):
    service = DashboardService(db)
    counts = service.get_tickets_by_category()
    return ApiResponse(success=True, data=counts)


@router.get(
    "/agent-performance",
    response_model=ApiResponse[List[AgentPerformanceMetric]],
    summary="Get support agent performance, resolution, and SLA metrics",
)
def get_agent_performance(
    current_user: User = Depends(require_support_or_admin),
    db: Session = Depends(get_db),
):
    service = DashboardService(db)
    metrics = service.get_agent_performance()
    return ApiResponse(success=True, data=metrics)
