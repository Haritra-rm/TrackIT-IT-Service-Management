from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Optional
from app.core.config import settings


class SLAService:
    """
    Manages Service Level Agreement (SLA) calculations and compliance tracking.
    SLA thresholds are dynamically resolved from configuration rather than hardcoded.
    """

    @classmethod
    def calculate_due_date(cls, created_at: datetime, priority: str) -> datetime:
        """Calculate the due_at deadline based on ticket priority and configured SLA hours."""
        sla_hours = settings.get_sla_hours_for_priority(priority)
        return created_at + timedelta(hours=sla_hours)

    @classmethod
    def evaluate_sla_status(
        cls,
        created_at: datetime,
        due_at: Optional[datetime],
        resolved_at: Optional[datetime] = None,
        status: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Evaluate real-time SLA metrics:
        - sla_status: 'ON_TRACK', 'AT_RISK', 'BREACHED', 'MET'
        - sla_remaining_hours: float
        - is_breached: bool
        """
        if not due_at:
            return {
                "sla_status": "ON_TRACK",
                "sla_remaining_hours": None,
                "is_breached": False,
            }

        # Normalize datetime awareness consistently
        if due_at.tzinfo is None:
            now_cmp = datetime.now()
            due_cmp = due_at
            resolved_cmp = resolved_at
        else:
            now_cmp = datetime.now(timezone.utc)
            due_cmp = due_at
            resolved_cmp = resolved_at

        # If ticket has already been resolved or closed
        if status in ["RESOLVED", "CLOSED"] and resolved_cmp:
            if resolved_cmp <= due_cmp:
                return {
                    "sla_status": "MET",
                    "sla_remaining_hours": 0.0,
                    "is_breached": False,
                }
            else:
                return {
                    "sla_status": "BREACHED",
                    "sla_remaining_hours": 0.0,
                    "is_breached": True,
                }

        # Active ticket (OPEN, ASSIGNED, IN_PROGRESS, REOPENED)
        remaining_seconds = (due_cmp - now_cmp).total_seconds()
        remaining_hours = round(remaining_seconds / 3600.0, 1)

        if remaining_seconds <= 0:
            return {
                "sla_status": "BREACHED",
                "sla_remaining_hours": remaining_hours,
                "is_breached": True,
            }

        # If remaining time is less than or equal to 4 hours, mark as AT_RISK
        if remaining_hours <= 4.0:
            return {
                "sla_status": "AT_RISK",
                "sla_remaining_hours": remaining_hours,
                "is_breached": False,
            }

        return {
            "sla_status": "ON_TRACK",
            "sla_remaining_hours": remaining_hours,
            "is_breached": False,
        }
