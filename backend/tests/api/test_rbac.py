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


def test_employee_accessing_admin_endpoints_returns_403(client, employee_user):
    emp_headers = get_token_header(employee_user)
    # Employee attempting to list all system users
    res = client.get("/api/v1/users", headers=emp_headers)
    assert res.status_code == 403
    assert res.json()["error"]["code"] == "INSUFFICIENT_PERMISSIONS"


def test_cannot_modify_closed_ticket(client, admin_user, sample_category, db_session):
    ticket = Ticket(
        title="Completed Router Replacement",
        description="Router was replaced successfully.",
        category_id=sample_category.id,
        priority=TicketPriority.LOW,
        status=TicketStatus.CLOSED,
        created_by=admin_user.id,
    )
    db_session.add(ticket)
    db_session.commit()
    db_session.refresh(ticket)

    admin_headers = get_token_header(admin_user)
    # Attempting to edit a closed ticket must be rejected
    update_res = client.put(
        f"/api/v1/tickets/{ticket.id}",
        headers=admin_headers,
        json={"title": "Trying to modify closed ticket"},
    )
    assert update_res.status_code == 422
    assert update_res.json()["error"]["code"] == "TICKET_CLOSED"


def test_employee_unauthorized_status_change_rejected(client, employee_user, sample_category, db_session):
    ticket = Ticket(
        title="Open Printer Bug",
        description="Paper jam issue.",
        category_id=sample_category.id,
        priority=TicketPriority.LOW,
        status=TicketStatus.OPEN,
        created_by=employee_user.id,
    )
    db_session.add(ticket)
    db_session.commit()
    db_session.refresh(ticket)

    emp_headers = get_token_header(employee_user)
    # Employee trying to advance status directly to IN_PROGRESS
    res = client.post(
        f"/api/v1/tickets/{ticket.id}/status",
        headers=emp_headers,
        json={"status": "IN_PROGRESS"},
    )
    assert res.status_code == 403
    assert res.json()["error"]["code"] == "FORBIDDEN"


def test_invalid_transitions_rejected(client, agent_user, sample_category, db_session):
    agent_headers = get_token_header(agent_user)

    # 1. OPEN -> CLOSED is forbidden
    open_ticket = Ticket(
        title="Direct Close Test",
        description="Testing invalid jump",
        category_id=sample_category.id,
        status=TicketStatus.OPEN,
        created_by=agent_user.id,
    )
    db_session.add(open_ticket)
    db_session.commit()
    db_session.refresh(open_ticket)

    res_open_to_closed = client.post(
        f"/api/v1/tickets/{open_ticket.id}/status",
        headers=agent_headers,
        json={"status": "CLOSED"},
    )
    assert res_open_to_closed.status_code == 400
    assert res_open_to_closed.json()["error"]["code"] == "INVALID_STATUS_TRANSITION"

    # 2. CLOSED -> IN_PROGRESS is forbidden
    closed_ticket = Ticket(
        title="Closed Ticket Jump Test",
        description="Testing invalid jump from closed",
        category_id=sample_category.id,
        status=TicketStatus.CLOSED,
        created_by=agent_user.id,
    )
    db_session.add(closed_ticket)
    db_session.commit()
    db_session.refresh(closed_ticket)

    res_closed_to_inprog = client.post(
        f"/api/v1/tickets/{closed_ticket.id}/status",
        headers=agent_headers,
        json={"status": "IN_PROGRESS"},
    )
    assert res_closed_to_inprog.status_code == 400
    assert res_closed_to_inprog.json()["error"]["code"] == "INVALID_STATUS_TRANSITION"
