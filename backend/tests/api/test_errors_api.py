import pytest
from tests.conftest import get_token_header


def test_error_400_bad_request_invalid_transition(client, agent_user, sample_category, db_session):
    from app.models.ticket import Ticket, TicketStatus
    ticket = Ticket(
        title="Bad Transition Test",
        description="Testing 400 response format",
        category_id=sample_category.id,
        status=TicketStatus.OPEN,
        created_by=agent_user.id,
    )
    db_session.add(ticket)
    db_session.commit()
    db_session.refresh(ticket)

    agent_headers = get_token_header(agent_user)
    res = client.post(
        f"/api/v1/tickets/{ticket.id}/status",
        headers=agent_headers,
        json={"status": "CLOSED"},  # OPEN -> CLOSED is illegal
    )
    assert res.status_code == 400
    data = res.json()
    assert data["success"] is False
    assert data["error"]["code"] == "INVALID_STATUS_TRANSITION"
    assert "Cannot transition ticket" in data["error"]["message"]


def test_error_401_unauthorized_missing_token(client):
    res = client.get("/api/v1/auth/me")
    assert res.status_code == 401
    data = res.json()
    assert data["success"] is False
    assert data["error"]["code"] == "MISSING_TOKEN"


def test_error_403_forbidden_insufficient_permissions(client, employee_user):
    emp_headers = get_token_header(employee_user)
    res = client.get("/api/v1/users", headers=emp_headers)
    assert res.status_code == 403
    data = res.json()
    assert data["success"] is False
    assert data["error"]["code"] == "INSUFFICIENT_PERMISSIONS"


def test_error_404_not_found(client, admin_user):
    admin_headers = get_token_header(admin_user)
    res = client.get("/api/v1/tickets/999999", headers=admin_headers)
    assert res.status_code == 404
    data = res.json()
    assert data["success"] is False
    assert data["error"]["code"] == "TICKET_NOT_FOUND"
    assert "999999" in data["error"]["message"]


def test_error_409_conflict_duplicate_email(client, employee_user):
    res = client.post(
        "/api/v1/auth/register",
        json={
            "name": "Clashing Name",
            "email": employee_user.email,
            "password": "Password123!",
        },
    )
    assert res.status_code == 409
    data = res.json()
    assert data["success"] is False
    assert data["error"]["code"] == "EMAIL_ALREADY_EXISTS"


def test_error_422_validation_error_pydantic(client, employee_user):
    emp_headers = get_token_header(employee_user)
    res = client.post(
        "/api/v1/tickets",
        headers=emp_headers,
        json={
            "title": "AB",  # less than 5 characters min_length
            "description": "Short",
            "category_id": 1,
        },
    )
    assert res.status_code == 422
    data = res.json()
    assert data["success"] is False
    assert data["error"]["code"] == "VALIDATION_ERROR"
    assert isinstance(data["error"]["details"], list)
