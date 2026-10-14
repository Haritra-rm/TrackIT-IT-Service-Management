import pytest
from tests.conftest import get_token_header
from app.models.ticket import TicketStatus


def test_create_ticket_success(client, employee_user, sample_category):
    headers = get_token_header(employee_user)
    payload = {
        "title": "VPN connection drops every 10 minutes",
        "description": "Every time I connect to the internal wireguard VPN, it disconnects after 10 minutes.",
        "category_id": sample_category.id,
        "priority": "HIGH",
    }
    response = client.post("/api/v1/tickets", headers=headers, json=payload)
    assert response.status_code == 201
    body = response.json()
    assert body["success"] is True
    assert body["data"]["title"] == payload["title"]
    assert body["data"]["status"] == "OPEN"
    assert body["data"]["priority"] == "HIGH"
    assert body["data"]["created_by"] == employee_user.id
    assert body["data"]["due_at"] is not None


def test_create_ticket_validation_error(client, employee_user):
    headers = get_token_header(employee_user)
    # Title too short (< 5 chars)
    payload = {
        "title": "VPN",
        "description": "Short desc",
        "category_id": 9999,
    }
    response = client.post("/api/v1/tickets", headers=headers, json=payload)
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


def test_ticket_lifecycle_workflow(client, employee_user, agent_user, admin_user, sample_category):
    # 1. Employee creates ticket (Status: OPEN)
    emp_headers = get_token_header(employee_user)
    create_res = client.post(
        "/api/v1/tickets",
        headers=emp_headers,
        json={
            "title": "Need software license for PyCharm Pro",
            "description": "My trial license expired and I need corporate key for active development.",
            "category_id": sample_category.id,
            "priority": "MEDIUM",
        },
    )
    assert create_res.status_code == 201
    ticket_id = create_res.json()["data"]["id"]
    assert create_res.json()["data"]["status"] == "OPEN"

    # 2. Agent assigns ticket to themselves (Status: ASSIGNED)
    agent_headers = get_token_header(agent_user)
    assign_res = client.post(
        f"/api/v1/tickets/{ticket_id}/assign",
        headers=agent_headers,
        json={"assigned_to": agent_user.id},
    )
    assert assign_res.status_code == 200
    assert assign_res.json()["data"]["status"] == "ASSIGNED"
    assert assign_res.json()["data"]["assigned_to"] == agent_user.id

    # 3. Agent moves ticket to IN_PROGRESS
    status_res = client.post(
        f"/api/v1/tickets/{ticket_id}/status",
        headers=agent_headers,
        json={"status": "IN_PROGRESS"},
    )
    assert status_res.status_code == 200
    assert status_res.json()["data"]["status"] == "IN_PROGRESS"

    # 4. Agent adds a comment
    comment_res = client.post(
        f"/api/v1/tickets/{ticket_id}/comments",
        headers=agent_headers,
        json={"comment": "Procuring license seat from IT vendor portal."},
    )
    assert comment_res.status_code == 201
    assert comment_res.json()["data"]["comment"] == "Procuring license seat from IT vendor portal."

    # 5. Agent resolves ticket
    resolve_res = client.post(
        f"/api/v1/tickets/{ticket_id}/resolve",
        headers=agent_headers,
        json={"resolution_notes": "Assigned license seat key via JetBrains organization hub."},
    )
    assert resolve_res.status_code == 200
    assert resolve_res.json()["data"]["status"] == "RESOLVED"
    assert resolve_res.json()["data"]["resolution_notes"] is not None

    # 6. Admin closes ticket
    admin_headers = get_token_header(admin_user)
    close_res = client.post(
        f"/api/v1/tickets/{ticket_id}/status",
        headers=admin_headers,
        json={"status": "CLOSED"},
    )
    assert close_res.status_code == 200
    assert close_res.json()["data"]["status"] == "CLOSED"

    # 7. Verify status history
    history_res = client.get(f"/api/v1/tickets/{ticket_id}/history", headers=emp_headers)
    assert history_res.status_code == 200
    history = history_res.json()["data"]
    assert len(history) >= 4


def test_invalid_status_transition_prevented(client, employee_user, agent_user, sample_category):
    emp_headers = get_token_header(employee_user)
    create_res = client.post(
        "/api/v1/tickets",
        headers=emp_headers,
        json={
            "title": "Printer paper tray broken on floor 3",
            "description": "Plastic hinge on bottom tray is snapped off completely.",
            "category_id": sample_category.id,
            "priority": "LOW",
        },
    )
    ticket_id = create_res.json()["data"]["id"]

    agent_headers = get_token_header(agent_user)
    # Attempting to jump directly from OPEN to CLOSED is not allowed in state machine
    bad_transition = client.post(
        f"/api/v1/tickets/{ticket_id}/status",
        headers=agent_headers,
        json={"status": "RESOLVED"},  # Must be ASSIGNED or IN_PROGRESS first
    )
    assert bad_transition.status_code == 400
    assert bad_transition.json()["error"]["code"] == "INVALID_STATUS_TRANSITION"


def test_reopen_ticket_flow(client, employee_user, agent_user, sample_category):
    emp_headers = get_token_header(employee_user)
    agent_headers = get_token_header(agent_user)

    # Create ticket
    create_res = client.post(
        "/api/v1/tickets",
        headers=emp_headers,
        json={
            "title": "Email search index broken",
            "description": "Searching past messages in web client returns error 500.",
            "category_id": sample_category.id,
            "priority": "MEDIUM",
        },
    )
    ticket_id = create_res.json()["data"]["id"]

    # Assign & move to in-progress & resolve
    client.post(f"/api/v1/tickets/{ticket_id}/assign", headers=agent_headers, json={"assigned_to": agent_user.id})
    client.post(f"/api/v1/tickets/{ticket_id}/status", headers=agent_headers, json={"status": "IN_PROGRESS"})
    client.post(f"/api/v1/tickets/{ticket_id}/resolve", headers=agent_headers, json={"resolution_notes": "Re-indexed mailbox cache."})

    # Employee reopens ticket because issue persisted
    reopen_res = client.post(
        f"/api/v1/tickets/{ticket_id}/reopen",
        headers=emp_headers,
        json={"reason": "Search is still throwing 500 when searching messages older than 30 days."},
    )
    assert reopen_res.status_code == 200
    assert reopen_res.json()["data"]["status"] == "REOPENED"


def test_support_agent_can_create_ticket_on_behalf_of_employee(client, employee_user, agent_user, sample_category):
    agent_headers = get_token_header(agent_user)
    payload = {
        "title": "Hardware keyboard replacement for Alice",
        "description": "Alice reported spacebar is sticking on her ThinkPad during morning standup.",
        "category_id": sample_category.id,
        "priority": "LOW",
        "on_behalf_of_id": employee_user.id,
    }
    response = client.post("/api/v1/tickets", headers=agent_headers, json=payload)
    assert response.status_code == 201
    data = response.json()["data"]
    # Ticket creator must be set to the target employee
    assert data["created_by"] == employee_user.id
    assert data["status"] == "OPEN"


def test_employee_cannot_create_ticket_on_behalf_of_others(client, employee_user, agent_user, sample_category):
    emp_headers = get_token_header(employee_user)
    payload = {
        "title": "Unauthorized attempt to raise on behalf of another user",
        "description": "Employee trying to spoof requester ID should be forbidden.",
        "category_id": sample_category.id,
        "priority": "LOW",
        "on_behalf_of_id": agent_user.id,
    }
    response = client.post("/api/v1/tickets", headers=emp_headers, json=payload)
    assert response.status_code == 403
    assert response.json()["error"]["code"] == "FORBIDDEN"

