import pytest
from tests.conftest import get_token_header
from app.models.ticket import Ticket, TicketStatus, TicketPriority


def test_employee_cannot_view_other_employees_ticket(client, employee_user, employee_user_2, sample_category, db_session):
    # Create ticket owned by Employee Two
    ticket = Ticket(
        title="Private Confidential Issue",
        description="Salary dispute inquiry that should be strictly private to employee 2.",
        category_id=sample_category.id,
        priority=TicketPriority.LOW,
        status=TicketStatus.OPEN,
        created_by=employee_user_2.id,
    )
    db_session.add(ticket)
    db_session.commit()
    db_session.refresh(ticket)

    # Employee One attempts to access Employee Two's ticket
    emp1_headers = get_token_header(employee_user)
    response = client.get(f"/api/v1/tickets/{ticket.id}", headers=emp1_headers)
    assert response.status_code == 403
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "FORBIDDEN"


def test_support_agent_and_admin_can_view_any_ticket(client, agent_user, admin_user, employee_user, sample_category, db_session):
    ticket = Ticket(
        title="Office Switch Reboot",
        description="Core rack reboot scheduled.",
        category_id=sample_category.id,
        priority=TicketPriority.HIGH,
        status=TicketStatus.OPEN,
        created_by=employee_user.id,
    )
    db_session.add(ticket)
    db_session.commit()
    db_session.refresh(ticket)

    # Agent view
    agent_headers = get_token_header(agent_user)
    agent_res = client.get(f"/api/v1/tickets/{ticket.id}", headers=agent_headers)
    assert agent_res.status_code == 200

    # Admin view
    admin_headers = get_token_header(admin_user)
    admin_res = client.get(f"/api/v1/tickets/{ticket.id}", headers=admin_headers)
    assert admin_res.status_code == 200


def test_employee_cannot_assign_ticket(client, employee_user, agent_user, sample_category, db_session):
    ticket = Ticket(
        title="Unassigned Ticket",
        description="Needs triage and resolution.",
        category_id=sample_category.id,
        priority=TicketPriority.MEDIUM,
        status=TicketStatus.OPEN,
        created_by=employee_user.id,
    )
    db_session.add(ticket)
    db_session.commit()
    db_session.refresh(ticket)

    emp_headers = get_token_header(employee_user)
    response = client.post(
        f"/api/v1/tickets/{ticket.id}/assign",
        headers=emp_headers,
        json={"assigned_to": agent_user.id},
    )
    assert response.status_code == 403
    assert response.json()["error"]["code"] == "FORBIDDEN"


def test_admin_can_deactivate_user(client, admin_user, employee_user):
    admin_headers = get_token_header(admin_user)
    response = client.patch(
        f"/api/v1/users/{employee_user.id}/status",
        headers=admin_headers,
        json={"is_active": False},
    )
    assert response.status_code == 200
    assert response.json()["data"]["is_active"] is False


def test_non_admin_cannot_deactivate_user(client, agent_user, employee_user):
    agent_headers = get_token_header(agent_user)
    response = client.patch(
        f"/api/v1/users/{employee_user.id}/status",
        headers=agent_headers,
        json={"is_active": False},
    )
    assert response.status_code == 403
    assert response.json()["error"]["code"] == "INSUFFICIENT_PERMISSIONS"
