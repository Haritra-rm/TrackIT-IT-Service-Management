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
        current_time: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """
        Evaluate real-time SLA metrics:
        - sla_status: 'ON_TRACK', 'AT_RISK', 'BREACHED', 'MET'
        - sla_remaining_hours: float
        - is_breached: bool
        Supports controllable clock (current_time parameter) for deterministic testing.
        """
        if not due_at:
            return {
                "sla_status": "ON_TRACK",
                "sla_remaining_hours": None,
                "is_breached": False,
            }

        # Normalize datetime awareness consistently
        is_tz_aware = due_at.tzinfo is not None

        if current_time is not None:
            now_cmp = current_time
        else:
            now_cmp = datetime.now(timezone.utc) if is_tz_aware else datetime.now()

        due_cmp = due_at
        resolved_cmp = resolved_at
        created_cmp = created_at

        # Ensure tz-awareness consistency between created_cmp, due_cmp, and now_cmp
        if is_tz_aware and now_cmp.tzinfo is None:
            now_cmp = now_cmp.replace(tzinfo=timezone.utc)
        elif not is_tz_aware and now_cmp.tzinfo is not None:
            now_cmp = now_cmp.replace(tzinfo=None)

        if created_cmp.tzinfo is not None and not is_tz_aware:
            created_cmp = created_cmp.replace(tzinfo=None)
        elif created_cmp.tzinfo is None and is_tz_aware:
            created_cmp = created_cmp.replace(tzinfo=timezone.utc)

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

        # Proportional AT_RISK calculation:
        # A ticket is marked AT_RISK if >= 75% of the SLA duration has elapsed
        # or less than 2 hours remaining
        total_duration_seconds = (due_cmp - created_cmp).total_seconds()
        if total_duration_seconds > 0:
            elapsed_seconds = (now_cmp - created_cmp).total_seconds()
            elapsed_ratio = elapsed_seconds / total_duration_seconds
            if elapsed_ratio >= 0.75 or remaining_hours <= 1.0:
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
