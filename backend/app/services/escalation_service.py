from datetime import datetime
from typing import List, Dict, Any, Optional

from app.models.ticket import Ticket, TicketPriority
from app.services.sla_service import SLAService
from app.schemas.intelligence import EscalationAssessmentResponse
from app.core.logging import logger


class EscalationService:
    """
    Deterministic, Rule-Based Escalation Recommendation Engine.
    Evaluates blast radius, priority severity, SLA urgency, and related ticket clustering
    to generate transparent, explainable recommendations for IT support operations.
    """

    RECOMMENDATION_NORMAL = "NORMAL"
    RECOMMENDATION_MONITOR = "MONITOR"
    RECOMMENDATION_ESCALATE = "ESCALATION RECOMMENDED"

    @classmethod
    def assess_ticket(
        cls,
        ticket: Ticket,
        related_tickets_count: int = 0,
        current_time: Optional[datetime] = None,
    ) -> EscalationAssessmentResponse:
        """
        Evaluate risk score and generate actionable recommendation:
        - Risk signals:
          +2 if priority is CRITICAL, +1 if HIGH
          +2 if affected_users >= 20, +1 if >= 10
          +2 if SLA is BREACHED, +1 if AT_RISK
          +2 if related_tickets >= 5, +1 if >= 3
        - Recommendation mapping:
          0-2: NORMAL
          3-4: MONITOR
          5+:  ESCALATION RECOMMENDED
        """
        now = current_time or datetime.now()

        # Handle edge cases where ticket fields might be missing or uninitialized
        if not ticket or not ticket.priority or not ticket.created_at:
            return EscalationAssessmentResponse(
                ticket_id=ticket.id if ticket else 0,
                priority=ticket.priority if ticket else "UNKNOWN",
                affected_users=1,
                related_tickets_count=related_tickets_count,
                sla_status="UNKNOWN",
                risk_score=0,
                recommendation=cls.RECOMMENDATION_NORMAL,
                reasons=["Insufficient data for escalation assessment."],
                assessed_at=now,
            )

        # 1. Compute SLA status dynamically using SLAService
        sla_info = SLAService.evaluate_sla_status(
            created_at=ticket.created_at,
            due_at=ticket.due_at,
            resolved_at=ticket.resolved_at,
            status=ticket.status,
            current_time=now,
        )
        sla_status = sla_info.get("sla_status", "ON_TRACK")

        affected_users = getattr(ticket, "affected_users", 1) or 1
        priority = (ticket.priority or TicketPriority.MEDIUM).upper()

        risk_score = 0
        reasons: List[str] = []

        # --- Rule 1: Priority Severity ---
        if priority == TicketPriority.CRITICAL:
            risk_score += 2
            reasons.append("CRITICAL priority issue")
        elif priority == TicketPriority.HIGH:
            risk_score += 1
            reasons.append("HIGH priority issue")

        # --- Rule 2: Affected Users (Blast Radius) ---
        if affected_users >= 20:
            risk_score += 2
            reasons.append(f"High blast radius: {affected_users} affected users")
        elif affected_users >= 10:
            risk_score += 1
            reasons.append(f"Moderate blast radius: {affected_users} affected users")

        # --- Rule 3: SLA Deadline Pressure ---
        if sla_status == "BREACHED":
            risk_score += 2
            reasons.append("SLA deadline has breached")
        elif sla_status == "AT_RISK":
            risk_score += 1
            reasons.append("SLA is at risk of breaching")

        # --- Rule 4: Incident Clustering / Related Tickets ---
        if related_tickets_count >= 5:
            risk_score += 2
            reasons.append(f"High volume cluster: {related_tickets_count} similar tickets detected")
        elif related_tickets_count >= 3:
            risk_score += 1
            reasons.append(f"Emerging trend: {related_tickets_count} similar tickets detected")

        # --- Fallback explanation for low-risk tickets ---
        if risk_score == 0:
            reasons.append("No significant escalation indicators detected.")

        # --- Score to Recommendation Mapping ---
        if risk_score >= 5:
            recommendation = cls.RECOMMENDATION_ESCALATE
        elif risk_score >= 3:
            recommendation = cls.RECOMMENDATION_MONITOR
        else:
            recommendation = cls.RECOMMENDATION_NORMAL

        logger.info(
            f"EscalationService: Ticket #{ticket.id} evaluated. "
            f"Score={risk_score}, Recommendation={recommendation}, Reasons={len(reasons)}"
        )

        return EscalationAssessmentResponse(
            ticket_id=ticket.id,
            priority=priority,
            affected_users=affected_users,
            related_tickets_count=related_tickets_count,
            sla_status=sla_status,
            risk_score=risk_score,
            recommendation=recommendation,
            reasons=reasons,
            assessed_at=now,
        )
