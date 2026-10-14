from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class RelatedTicketItem(BaseModel):
    ticket_id: int
    title: str
    status: str
    priority: str
    category_id: int
    category_name: Optional[str] = None
    similarity_score: float = Field(..., description="Cosine similarity score between 0.0 and 1.0")
    similarity_percentage: int = Field(..., description="Similarity score as percentage (e.g. 92 for 92%)")
    created_at: datetime


class RelatedTicketsResponse(BaseModel):
    target_ticket_id: int
    threshold_used: float
    total_candidates_analyzed: int
    related_tickets: List[RelatedTicketItem]


class EscalationAssessmentResponse(BaseModel):
    ticket_id: int
    priority: str
    affected_users: int
    related_tickets_count: int
    sla_status: str
    risk_score: int
    recommendation: str = Field(..., description="'NORMAL' | 'MONITOR' | 'ESCALATION RECOMMENDED'")
    reasons: List[str]
    assessed_at: datetime
