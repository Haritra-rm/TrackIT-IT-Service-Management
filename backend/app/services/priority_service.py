from typing import Tuple, Dict, Any
from app.core.config import settings
from app.models.ticket import TicketPriority


class PriorityRecommendationEngine:
    """
    Deterministic Rule-Based & Blast-Radius Engine for IT ticket priority classification.
    Calculates priority and explainable reasoning based on:
    - Business Impact Weight (Low=5, Medium=15, High/Department Blocked=25, Critical/Org Blocked=40)
    - Blocker Indicators (Security incident=+50, System down=+50)
    - Blast Radius / Affected-User Bonus (1=0, 2-4=5, 5-19=10, 20-49=15, 50-99=25, >=100=35)
    - Category Handling (Network/Access=+10, Security=+20)
    """

    # Scoring weights
    IMPACT_WEIGHTS = {
        "LOW": 5,
        "MEDIUM": 15,
        "HIGH": 25,
        "DEPARTMENT_BLOCKED": 25,
        "CRITICAL": 45,
        "ORGANIZATION_BLOCKED": 45,
    }

    # Thresholds
    CRITICAL_SCORE_THRESHOLD = 75
    HIGH_SCORE_THRESHOLD = 35
    MEDIUM_SCORE_THRESHOLD = 20

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
        impact_normalized = (business_impact or "LOW").upper().strip().replace(" ", "_")

        reasons = []

        # 1. Base Impact Weight
        impact_score = cls.IMPACT_WEIGHTS.get(impact_normalized, 5)

        # 2. Affected Users Bonus (Blast Radius)
        if affected_users >= 100:
            user_score = 35
        elif affected_users >= 50:
            user_score = 25
        elif affected_users >= 20:
            user_score = 15
        elif affected_users >= 5:
            user_score = 10
        elif affected_users > 1:
            user_score = 5
        else:
            user_score = 0

        # 3. Category Severity Bonus
        cat_score = 0
        if "security" in cat_lower:
            cat_score = 20
            reasons.append("- Security category")
        elif "network" in cat_lower or "access" in cat_lower:
            cat_score = 10
            reasons.append(f"- {category_name.title()} category")

        # 4. Critical Blocker Flags
        blocker_score = 0
        if is_security_incident:
            blocker_score += 50
            reasons.append("- Active security incident flagged")
        if is_system_down:
            blocker_score += 50
            reasons.append("- Complete system / infrastructure outage")

        # Total Blast Radius Score
        total_score = impact_score + user_score + cat_score + blocker_score

        # Structured Reason Items
        if affected_users > 1:
            reasons.append(f"- {affected_users} affected users")

        if impact_normalized in ["HIGH", "DEPARTMENT_BLOCKED"]:
            reasons.append("- Department blocked")
        elif impact_normalized in ["CRITICAL", "ORGANIZATION_BLOCKED"]:
            reasons.append("- Organization-wide blocker")
        elif impact_normalized == "MEDIUM":
            reasons.append("- Team productivity impacted")
        elif impact_normalized == "LOW" and not is_security_incident and not is_system_down:
            reasons.append("- Individual user non-blocking issue")

        # Determine Priority based on thresholds
        if is_security_incident or is_system_down or impact_normalized in ["CRITICAL", "ORGANIZATION_BLOCKED"] or total_score >= cls.CRITICAL_SCORE_THRESHOLD:
            priority = TicketPriority.CRITICAL
        elif total_score >= cls.HIGH_SCORE_THRESHOLD or (affected_users >= 20 and ("network" in cat_lower or "access" in cat_lower)):
            priority = TicketPriority.HIGH
        elif total_score >= cls.MEDIUM_SCORE_THRESHOLD or affected_users > 1 or impact_normalized == "MEDIUM":
            priority = TicketPriority.MEDIUM
        else:
            priority = TicketPriority.LOW

        sla_hours = settings.get_sla_hours_for_priority(priority)
        reason_text = "\n".join(reasons) if reasons else f"Standard assessment: classified as {priority} priority."

        return {
            "recommended_priority": priority,
            "reasoning": reason_text,
            "sla_hours": sla_hours,
            "score": total_score,
        }
