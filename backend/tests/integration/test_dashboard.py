import pytest
from tests.conftest import get_token_header
from app.models.ticket import Ticket, TicketStatus, TicketPriority


def test_dashboard_summary_admin(client, admin_user, employee_user, sample_category, db_session):
    # Insert a couple of tickets in different states
    t1 = Ticket(
        title="Sample Test Ticket A",
        description="Detailed description for test ticket A",
        category_id=sample_category.id,
        priority=TicketPriority.HIGH,
        status=TicketStatus.OPEN,
        created_by=employee_user.id,
    )
    t2 = Ticket(
        title="Sample Test Ticket B",
        description="Detailed description for test ticket B",
        category_id=sample_category.id,
        priority=TicketPriority.LOW,
        status=TicketStatus.RESOLVED,
        created_by=employee_user.id,
    )
    db_session.add_all([t1, t2])
    db_session.commit()

    headers = get_token_header(admin_user)
    response = client.get("/api/v1/dashboard/summary", headers=headers)
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["total_tickets"] >= 2
    assert "open_tickets" in data
    assert "resolved_tickets" in data
    assert "sla_breach_rate" in data
    assert "avg_resolution_time_hours" in data


def test_dashboard_tickets_by_status(client, admin_user):
    headers = get_token_header(admin_user)
    response = client.get("/api/v1/dashboard/tickets-by-status", headers=headers)
    assert response.status_code == 200
    statuses = response.json()["data"]
    assert any(s["status"] == "OPEN" for s in statuses)


def test_dashboard_tickets_by_priority(client, admin_user):
    headers = get_token_header(admin_user)
    response = client.get("/api/v1/dashboard/tickets-by-priority", headers=headers)
    assert response.status_code == 200
    priorities = response.json()["data"]
    assert any(p["priority"] == "HIGH" for p in priorities)


def test_dashboard_agent_performance(client, admin_user):
    headers = get_token_header(admin_user)
    response = client.get("/api/v1/dashboard/agent-performance", headers=headers)
    assert response.status_code == 200
    agents = response.json()["data"]
    assert isinstance(agents, list)
