from datetime import datetime, timedelta
import pytest
from app.models.ticket import Ticket, TicketPriority, TicketStatus
from app.services.escalation_service import EscalationService


def test_escalation_assessment_low_priority_normal(sample_category, employee_user):
    now = datetime(2026, 10, 14, 10, 0, 0)
    ticket = Ticket(
        id=101,
        title="Slack profile photo update issue",
        description="Cannot change avatar in Slack profile settings.",
        category_id=sample_category.id,
        priority=TicketPriority.LOW,
        status=TicketStatus.OPEN,
        created_by=employee_user.id,
        created_at=now,
        due_at=now + timedelta(hours=72),
        affected_users=1,
    )

    assessment = EscalationService.assess_ticket(ticket, related_tickets_count=0, current_time=now)
    assert assessment.recommendation == "NORMAL"
    assert assessment.risk_score == 0
    assert "No significant escalation indicators detected." in assessment.reasons[0]


def test_escalation_assessment_monitor_threshold(sample_category, employee_user):
    now = datetime(2026, 10, 14, 10, 0, 0)
    # Created 23 hours ago for a HIGH priority ticket (SLA = 24 hours -> remaining = 1 hour -> AT_RISK)
    created_at = now - timedelta(hours=23)
    due_at = created_at + timedelta(hours=24)

    ticket = Ticket(
        id=102,
        title="Email sync latency in Outlook client",
        description="Emails arriving 15 minutes late in desktop client.",
        category_id=sample_category.id,
        priority=TicketPriority.HIGH,  # +1
        status=TicketStatus.IN_PROGRESS,
        created_by=employee_user.id,
        created_at=created_at,
        due_at=due_at,
        affected_users=12,  # 10 <= users < 20 -> +1
    )

    # 3 related tickets -> +1. Total score = 1 (HIGH) + 1 (12 users) + 1 (AT_RISK) + 1 (3 related) = 4 -> MONITOR
    assessment = EscalationService.assess_ticket(ticket, related_tickets_count=3, current_time=now)
    assert assessment.recommendation == "MONITOR"
    assert assessment.risk_score == 4
    assert any("HIGH priority" in r for r in assessment.reasons)
    assert any("12 affected users" in r for r in assessment.reasons)
    assert any("SLA is at risk" in r for r in assessment.reasons)
    assert any("3 similar tickets" in r for r in assessment.reasons)


def test_escalation_assessment_escalate_recommended(sample_category, employee_user):
    now = datetime(2026, 10, 14, 10, 0, 0)
    # Created 30 hours ago for HIGH ticket -> due was 6 hours ago -> BREACHED (+2)
    created_at = now - timedelta(hours=30)
    due_at = created_at + timedelta(hours=24)

    ticket = Ticket(
        id=103,
        title="Core corporate VPN gateway authentication failure",
        description="All engineering staff unable to connect to internal Kubernetes clusters.",
        category_id=sample_category.id,
        priority=TicketPriority.HIGH,  # +1
        status=TicketStatus.OPEN,
        created_by=employee_user.id,
        created_at=created_at,
        due_at=due_at,
        affected_users=25,  # >= 20 -> +2
    )

    # 5 related tickets -> +2. Total score = 1 + 2 + 2 + 2 = 7 -> ESCALATION RECOMMENDED
    assessment = EscalationService.assess_ticket(ticket, related_tickets_count=5, current_time=now)
    assert assessment.recommendation == "ESCALATION RECOMMENDED"
    assert assessment.risk_score == 7
    assert any("HIGH priority" in r for r in assessment.reasons)
    assert any("25 affected users" in r for r in assessment.reasons)
    assert any("SLA deadline has breached" in r for r in assessment.reasons)
    assert any("5 similar tickets" in r for r in assessment.reasons)


def test_escalation_assessment_critical_priority_boost(sample_category, employee_user):
    now = datetime(2026, 10, 14, 10, 0, 0)
    ticket = Ticket(
        id=104,
        title="Ransomware warning pop-up on finance workstation",
        description="Workstation displaying suspicious file encryption alert.",
        category_id=sample_category.id,
        priority=TicketPriority.CRITICAL,  # +2
        status=TicketStatus.OPEN,
        created_by=employee_user.id,
        created_at=now,
        due_at=now + timedelta(hours=4),  # ON_TRACK
        affected_users=50,  # >= 20 -> +2
    )

    # Related count: 3 (+1) -> Total score: 2 + 2 + 0 + 1 = 5 -> ESCALATION RECOMMENDED
    assessment = EscalationService.assess_ticket(ticket, related_tickets_count=3, current_time=now)
    assert assessment.recommendation == "ESCALATION RECOMMENDED"
    assert assessment.risk_score == 5


def test_escalation_assessment_insufficient_data_safe():
    empty_ticket = Ticket(id=0, title="", priority="", created_at=None)
    assessment = EscalationService.assess_ticket(empty_ticket, related_tickets_count=0)
    assert assessment.recommendation == "NORMAL"
    assert assessment.risk_score == 0
    assert "Insufficient data" in assessment.reasons[0]
