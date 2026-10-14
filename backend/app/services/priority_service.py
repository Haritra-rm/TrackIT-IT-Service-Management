from typing import Tuple, Dict, Any
from app.core.config import settings
from app.models.ticket import TicketPriority


class PriorityRecommendationEngine:
    """
    Rule-Based Expert Engine for smart IT ticket priority classification.
    Calculates appropriate priority based on:
    - Blast Radius (number of affected users)
    - Business Impact criticality
    - Category severity (e.g. Security, Network outage)
    - Infrastructure downtime indicator
    """

    @classmethod
    def recommend(
        cls,
        category_name: str = "",
        affected_users: int = 1,
        business_impact: str = "LOW",
        is_security_incident: bool = False,
        is_system_down: bool = False,
    ) -> Dict[str, Any]:
        cat_lower = (category_name or "").lower().strip()
        impact_upper = (business_impact or "LOW").upper().strip()

        # Rule 1: Security breach or company-wide system down -> CRITICAL
        if is_security_incident or is_system_down:
            reason = "Security threat or complete system outage immediately escalates to CRITICAL."
            priority = TicketPriority.CRITICAL

        # Rule 2: Critical business impact or widespread network failure
        elif impact_upper == "CRITICAL" or (("network" in cat_lower or "access" in cat_lower) and affected_users >= 20):
            reason = f"High blast radius ({affected_users} users) affecting core infrastructure qualifies as CRITICAL priority."
            priority = TicketPriority.CRITICAL

        # Rule 3: High impact or team-wide outage (5+ users)
        elif impact_upper == "HIGH" or affected_users >= 5 or "security" in cat_lower:
            reason = f"Multiple users impacted ({affected_users}) or high operational impact warrants HIGH priority."
            priority = TicketPriority.HIGH

        # Rule 4: Medium impact or multiple individuals affected (2-4 users)
        elif impact_upper == "MEDIUM" or affected_users > 1:
            reason = f"Departmental/group impact ({affected_users} users) recommended for MEDIUM priority."
            priority = TicketPriority.MEDIUM

        # Rule 5: Default individual non-blocking issue
        else:
            reason = "Single-user issue without operational blockage classified as LOW priority."
            priority = TicketPriority.LOW

        sla_hours = settings.get_sla_hours_for_priority(priority)

        return {
            "recommended_priority": priority,
            "reasoning": reason,
            "sla_hours": sla_hours,
        }
