from datetime import datetime, timedelta, timezone
from app.services.sla_service import SLAService
from app.core.config import settings


def test_sla_due_date_calculation():
    now = datetime(2026, 1, 1, 12, 0, 0)

    # CRITICAL -> 4 hours
    crit_due = SLAService.calculate_due_date(now, "CRITICAL")
    assert crit_due == now + timedelta(hours=4)

    # HIGH -> 24 hours
    high_due = SLAService.calculate_due_date(now, "HIGH")
    assert high_due == now + timedelta(hours=24)

    # MEDIUM -> 48 hours
    med_due = SLAService.calculate_due_date(now, "MEDIUM")
    assert med_due == now + timedelta(hours=48)

    # LOW -> 72 hours
    low_due = SLAService.calculate_due_date(now, "LOW")
    assert low_due == now + timedelta(hours=72)


def test_sla_status_evaluation_on_track():
    now = datetime.now()
    created_at = now - timedelta(hours=2)
    due_at = now + timedelta(hours=20)  # plenty of time left

    sla = SLAService.evaluate_sla_status(created_at, due_at, status="OPEN")
    assert sla["sla_status"] == "ON_TRACK"
    assert sla["is_breached"] is False
    assert sla["sla_remaining_hours"] > 4.0


def test_sla_status_evaluation_at_risk():
    now = datetime.now()
    created_at = now - timedelta(hours=22)
    due_at = now + timedelta(hours=2)  # only 2 hours left (< 4 hours)

    sla = SLAService.evaluate_sla_status(created_at, due_at, status="IN_PROGRESS")
    assert sla["sla_status"] == "AT_RISK"
    assert sla["is_breached"] is False


def test_sla_status_evaluation_breached():
    now = datetime.now()
    created_at = now - timedelta(hours=30)
    due_at = now - timedelta(hours=5)  # past deadline

    sla = SLAService.evaluate_sla_status(created_at, due_at, status="OPEN")
    assert sla["sla_status"] == "BREACHED"
    assert sla["is_breached"] is True
    assert sla["sla_remaining_hours"] < 0


def test_sla_status_evaluation_resolved_met_vs_breached():
    created_at = datetime(2026, 1, 1, 10, 0)
    due_at = datetime(2026, 1, 1, 14, 0)

    # Resolved on time (met)
    resolved_on_time = datetime(2026, 1, 1, 13, 0)
    met_sla = SLAService.evaluate_sla_status(created_at, due_at, resolved_at=resolved_on_time, status="RESOLVED")
    assert met_sla["sla_status"] == "MET"
    assert met_sla["is_breached"] is False

    # Resolved late (breached)
    resolved_late = datetime(2026, 1, 1, 16, 0)
    breached_sla = SLAService.evaluate_sla_status(created_at, due_at, resolved_at=resolved_late, status="RESOLVED")
    assert breached_sla["sla_status"] == "BREACHED"
    assert breached_sla["is_breached"] is True
