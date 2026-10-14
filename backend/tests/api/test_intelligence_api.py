import pytest
from tests.conftest import get_token_header
from app.models.ticket import Ticket, TicketPriority, TicketStatus
from app.models.user import User, UserRole
from app.core.security import get_password_hash


def test_related_tickets_api_success(client, employee_user, sample_category, db_session):
    emp_headers = get_token_header(employee_user)

    # 1. Target ticket
    target = Ticket(
        title="VPN connection is not working",
        description="I cannot connect to the office VPN.",
        category_id=sample_category.id,
        priority=TicketPriority.HIGH,
        status=TicketStatus.OPEN,
        created_by=employee_user.id,
    )
    # 2. Similar candidate ticket
    cand = Ticket(
        title="Office VPN connection failure",
        description="Cannot connect to office VPN tunnel from remote network.",
        category_id=sample_category.id,
        priority=TicketPriority.HIGH,
        status=TicketStatus.IN_PROGRESS,
        created_by=employee_user.id,
    )
    db_session.add_all([target, cand])
    db_session.commit()

    res = client.get(f"/api/v1/intelligence/tickets/{target.id}/related?threshold=0.4", headers=emp_headers)
    assert res.status_code == 200
    body = res.json()
    assert body["success"] is True
    data = body["data"]
    assert data["target_ticket_id"] == target.id
    assert len(data["related_tickets"]) >= 1
    first_match = data["related_tickets"][0]
    assert first_match["ticket_id"] == cand.id
    assert first_match["similarity_score"] > 0.4
    assert 0 <= first_match["similarity_percentage"] <= 100


def test_escalation_assessment_api_success(client, employee_user, sample_category, db_session):
    emp_headers = get_token_header(employee_user)

    ticket = Ticket(
        title="VPN connection is not working",
        description="I cannot connect to the office VPN.",
        category_id=sample_category.id,
        priority=TicketPriority.HIGH,
        status=TicketStatus.OPEN,
        created_by=employee_user.id,
        affected_users=25,
    )
    # Add a couple of similar tickets to bump related count
    cand1 = Ticket(
        title="Office VPN connection failure",
        description="Cannot connect to office VPN tunnel from remote network.",
        category_id=sample_category.id,
        priority=TicketPriority.HIGH,
        status=TicketStatus.IN_PROGRESS,
        created_by=employee_user.id,
    )
    cand2 = Ticket(
        title="Office VPN tunnel down",
        description="Office VPN connection is not working.",
        category_id=sample_category.id,
        priority=TicketPriority.HIGH,
        status=TicketStatus.OPEN,
        created_by=employee_user.id,
    )
    cand3 = Ticket(
        title="VPN connection not working at branch",
        description="Cannot connect to office VPN.",
        category_id=sample_category.id,
        priority=TicketPriority.HIGH,
        status=TicketStatus.OPEN,
        created_by=employee_user.id,
    )

    db_session.add_all([ticket, cand1, cand2, cand3])
    db_session.commit()

    res = client.get(f"/api/v1/intelligence/tickets/{ticket.id}/escalation?threshold=0.4", headers=emp_headers)
    assert res.status_code == 200
    body = res.json()
    assert body["success"] is True
    data = body["data"]
    assert data["ticket_id"] == ticket.id
    assert data["affected_users"] == 25
    assert data["related_tickets_count"] >= 2
    assert data["risk_score"] >= 3
    assert data["recommendation"] in ["MONITOR", "ESCALATION RECOMMENDED"]
    assert len(data["reasons"]) >= 1


def test_employee_cannot_access_other_employee_ticket_intelligence(client, employee_user, sample_category, db_session):
    # Create second employee user
    other_emp = User(
        name="Bob Other",
        email="bob.other@trackit.internal",
        password_hash=get_password_hash("Secret@123"),
        role=UserRole.EMPLOYEE,
        is_active=True,
    )
    db_session.add(other_emp)
    db_session.commit()
    db_session.refresh(other_emp)

    # Ticket created by Bob
    ticket = Ticket(
        title="Bob's private workstation issue",
        description="Private laptop hardware failure details.",
        category_id=sample_category.id,
        priority=TicketPriority.LOW,
        status=TicketStatus.OPEN,
        created_by=other_emp.id,
    )
    db_session.add(ticket)
    db_session.commit()

    # Employee Alice attempts to access Bob's intelligence
    alice_headers = get_token_header(employee_user)

    # 1. Related tickets endpoint
    rel_res = client.get(f"/api/v1/intelligence/tickets/{ticket.id}/related", headers=alice_headers)
    assert rel_res.status_code == 403
    assert rel_res.json()["error"]["code"] == "FORBIDDEN"

    # 2. Escalation endpoint
    esc_res = client.get(f"/api/v1/intelligence/tickets/{ticket.id}/escalation", headers=alice_headers)
    assert esc_res.status_code == 403
    assert esc_res.json()["error"]["code"] == "FORBIDDEN"


def test_support_agent_and_admin_can_access_ticket_intelligence(client, employee_user, agent_user, admin_user, sample_category, db_session):
    from datetime import datetime, timedelta
    now = datetime.now()
    ticket = Ticket(
        title="Network router packet drop in server room",
        description="Cisco router experiencing 40% packet drops on uplink.",
        category_id=sample_category.id,
        priority=TicketPriority.CRITICAL,
        status=TicketStatus.OPEN,
        created_by=employee_user.id,
        created_at=now - timedelta(hours=5),
        due_at=now - timedelta(hours=1),  # Breached SLA (+2) -> Total 2+2+2 = 6 -> ESCALATION RECOMMENDED
        affected_users=100,
    )
    db_session.add(ticket)
    db_session.commit()

    agent_headers = get_token_header(agent_user)
    admin_headers = get_token_header(admin_user)

    # Agent checks
    agent_rel = client.get(f"/api/v1/intelligence/tickets/{ticket.id}/related", headers=agent_headers)
    assert agent_rel.status_code == 200
    agent_esc = client.get(f"/api/v1/intelligence/tickets/{ticket.id}/escalation", headers=agent_headers)
    assert agent_esc.status_code == 200
    assert agent_esc.json()["data"]["recommendation"] == "ESCALATION RECOMMENDED"

    # Admin checks
    admin_rel = client.get(f"/api/v1/intelligence/tickets/{ticket.id}/related", headers=admin_headers)
    assert admin_rel.status_code == 200
    admin_esc = client.get(f"/api/v1/intelligence/tickets/{ticket.id}/escalation", headers=admin_headers)
    assert admin_esc.status_code == 200


def test_intelligence_non_existent_ticket_returns_404(client, admin_user):
    admin_headers = get_token_header(admin_user)
    rel_res = client.get("/api/v1/intelligence/tickets/999999/related", headers=admin_headers)
    assert rel_res.status_code == 404
    assert rel_res.json()["error"]["code"] == "TICKET_NOT_FOUND"

    esc_res = client.get("/api/v1/intelligence/tickets/999999/escalation", headers=admin_headers)
    assert esc_res.status_code == 404
    assert esc_res.json()["error"]["code"] == "TICKET_NOT_FOUND"
