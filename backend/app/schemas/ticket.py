from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict


class TicketBase(BaseModel):
    title: str = Field(..., min_length=5, max_length=200)
    description: str = Field(..., min_length=10)
    category_id: int
    priority: str = Field(default="MEDIUM")


class TicketCreate(TicketBase):
    affected_users: Optional[int] = Field(default=1, ge=1)
    business_impact: Optional[str] = Field(default="LOW")
    on_behalf_of_id: Optional[int] = Field(default=None, description="Optional: Support Agent / Admin raising ticket on behalf of an employee")


class TicketUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=5, max_length=200)
    description: Optional[str] = Field(None, min_length=10)
    category_id: Optional[int] = None
    priority: Optional[str] = None


class TicketAssign(BaseModel):
    assigned_to: int = Field(..., description="User ID of the support agent or admin")


class TicketStatusUpdate(BaseModel):
    status: str = Field(..., description="Target status: OPEN, ASSIGNED, IN_PROGRESS, RESOLVED, CLOSED, REOPENED")
    notes: Optional[str] = Field(None, description="Optional transition notes")


class TicketResolve(BaseModel):
    resolution_notes: str = Field(..., min_length=5, description="Clear explanation of how the issue was resolved")


class TicketReopen(BaseModel):
    reason: str = Field(..., min_length=5, description="Why the issue persists or was not satisfactorily resolved")


class PriorityRecommendationRequest(BaseModel):
    category_id: Optional[int] = None
    category_name: Optional[str] = None
    affected_users: int = Field(default=1, ge=1)
    business_impact: str = Field(default="LOW", description="LOW, MEDIUM, HIGH, CRITICAL")
    is_security_incident: bool = False
    is_system_down: bool = False


class PriorityRecommendationResponse(BaseModel):
    recommended_priority: str
    reasoning: str
    sla_hours: int


class TicketStatusHistoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    ticket_id: int
    old_status: Optional[str] = None
    new_status: str
    changed_by: int
    changed_at: datetime
    author_name: Optional[str] = None
    author_role: Optional[str] = None


class TicketResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str
    category_id: int
    category_name: Optional[str] = None
    priority: str
    status: str

    created_by: int
    creator_name: Optional[str] = None
    creator_email: Optional[str] = None

    assigned_to: Optional[int] = None
    assignee_name: Optional[str] = None
    assignee_email: Optional[str] = None

    created_at: datetime
    updated_at: datetime
    due_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    closed_at: Optional[datetime] = None
    resolution_notes: Optional[str] = None

    # Calculated SLA fields
    sla_status: Optional[str] = "ON_TRACK"  # ON_TRACK, AT_RISK, BREACHED, MET
    sla_remaining_hours: Optional[float] = None
    is_breached: bool = False
    comments_count: Optional[int] = 0
