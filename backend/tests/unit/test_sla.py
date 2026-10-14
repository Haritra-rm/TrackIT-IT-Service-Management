from datetime import datetime, timedelta
from app.services.sla_service import SLAService


def test_sla_due_date_calculation():
    now = datetime(2026, 1, 1, 12, 0, 0)

    # CRITICAL -> 4 hours
    crit_due = SLAService.calculate_due_date(now, "CRITICAL")
    assert crit_due == now + timedelta(hours=4)

    # HIGH -> 8 hours
    high_due = SLAService.calculate_due_date(now, "HIGH")
    assert high_due == now + timedelta(hours=8)

    # MEDIUM -> 24 hours
    med_due = SLAService.calculate_due_date(now, "MEDIUM")
    assert med_due == now + timedelta(hours=24)

    # LOW -> 72 hours
    low_due = SLAService.calculate_due_date(now, "LOW")
    assert low_due == now + timedelta(hours=72)


def test_scenario_1_newly_created_ticket():
    """Scenario 1: Newly created ticket (0% elapsed) -> ON_TRACK"""
    created_at = datetime(2026, 5, 1, 9, 0, 0)
    due_at = created_at + timedelta(hours=8)  # HIGH priority
    current_time = datetime(2026, 5, 1, 9, 15, 0)  # 15 mins later

    sla = SLAService.evaluate_sla_status(created_at, due_at, status="OPEN", current_time=current_time)
    assert sla["sla_status"] == "ON_TRACK"
    assert sla["is_breached"] is False
    assert sla["sla_remaining_hours"] == 7.8


def test_scenario_2_ticket_near_sla_deadline_at_risk():
    """Scenario 2: Ticket near SLA deadline (>= 75% elapsed) -> AT_RISK"""
    created_at = datetime(2026, 5, 1, 9, 0, 0)
    due_at = created_at + timedelta(hours=8)  # 8 hours total duration
    # 6.5 hours elapsed (81% elapsed, only 1.5h left)
    current_time = datetime(2026, 5, 1, 15, 30, 0)

    sla = SLAService.evaluate_sla_status(created_at, due_at, status="IN_PROGRESS", current_time=current_time)
    assert sla["sla_status"] == "AT_RISK"
    assert sla["is_breached"] is False
    assert sla["sla_remaining_hours"] == 1.5


def test_scenario_3_breached_ticket():
    """Scenario 3: Unresolved ticket past SLA deadline -> BREACHED"""
    created_at = datetime(2026, 5, 1, 9, 0, 0)
    due_at = created_at + timedelta(hours=8)
    current_time = datetime(2026, 5, 1, 18, 0, 0)  # 1 hour past deadline

    sla = SLAService.evaluate_sla_status(created_at, due_at, status="IN_PROGRESS", current_time=current_time)
    assert sla["sla_status"] == "BREACHED"
    assert sla["is_breached"] is True
    assert sla["sla_remaining_hours"] < 0


def test_scenario_4_resolved_before_deadline_met():
    """Scenario 4: Ticket resolved before deadline -> MET"""
    created_at = datetime(2026, 5, 1, 9, 0, 0)
    due_at = created_at + timedelta(hours=8)
    resolved_at = datetime(2026, 5, 1, 14, 0, 0)  # 5 hours elapsed (< 8h)

    sla = SLAService.evaluate_sla_status(created_at, due_at, resolved_at=resolved_at, status="RESOLVED")
    assert sla["sla_status"] == "MET"
    assert sla["is_breached"] is False
    assert sla["sla_remaining_hours"] == 0.0


def test_scenario_5_resolved_after_deadline_breached():
    """Scenario 5: Ticket resolved after deadline -> BREACHED"""
    created_at = datetime(2026, 5, 1, 9, 0, 0)
    due_at = created_at + timedelta(hours=8)
    resolved_at = datetime(2026, 5, 1, 19, 0, 0)  # 10 hours elapsed (> 8h)

    sla = SLAService.evaluate_sla_status(created_at, due_at, resolved_at=resolved_at, status="RESOLVED")
    assert sla["sla_status"] == "BREACHED"
    assert sla["is_breached"] is True
    assert sla["sla_remaining_hours"] == 0.0


def test_scenario_6_reopened_ticket_lifecycle():
    """Scenario 6: Reopened ticket reset with new SLA deadline -> ON_TRACK"""
    reopened_at = datetime(2026, 5, 2, 10, 0, 0)
    new_due_at = SLAService.calculate_due_date(reopened_at, "HIGH")  # 10:00 + 8h = 18:00
    current_time = datetime(2026, 5, 2, 11, 0, 0)  # 1h after reopen

    sla = SLAService.evaluate_sla_status(reopened_at, new_due_at, status="REOPENED", current_time=current_time)
    assert sla["sla_status"] == "ON_TRACK"
    assert sla["is_breached"] is False
    assert sla["sla_remaining_hours"] == 7.0
