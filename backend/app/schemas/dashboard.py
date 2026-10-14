from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel


class DashboardSummary(BaseModel):
    total_tickets: int
    open_tickets: int
    assigned_tickets: int
    in_progress_tickets: int
    resolved_tickets: int
    closed_tickets: int
    reopened_tickets: int

    # SLA Metrics
    sla_breached_count: int
    sla_at_risk_count: int
    sla_on_track_count: int
    sla_breach_rate: float  # (breached / applicable) * 100

    # Timing metrics
    avg_resolution_time_hours: float
    avg_first_response_time_hours: float
    resolution_rate: float  # (resolved + closed) / total * 100


class StatusCount(BaseModel):
    status: str
    count: int
    percentage: float


class PriorityCount(BaseModel):
    priority: str
    count: int
    percentage: float


class CategoryCount(BaseModel):
    category_id: int
    category_name: str
    count: int
    percentage: float


class AgentPerformanceMetric(BaseModel):
    agent_id: int
    agent_name: str
    agent_email: str
    assigned_count: int
    in_progress_count: int
    resolved_count: int
    avg_resolution_hours: float
    sla_compliance_rate: float


class AuditLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: Optional[int]
    user_name: Optional[str] = None
    action: str
    entity_type: str
    entity_id: Optional[int]
    timestamp: datetime
    metadata_json: Optional[str] = None
