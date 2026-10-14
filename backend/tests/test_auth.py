import pytest
from app.core.security import verify_password, get_password_hash, create_access_token, decode_access_token
from tests.conftest import get_token_header


def test_password_hashing():
    raw = "SecurePassword#2026"
    hashed = get_password_hash(raw)
    assert hashed != raw
    assert verify_password(raw, hashed) is True
    assert verify_password("WrongPassword", hashed) is False


def test_jwt_token_creation_and_decoding():
    data = {"sub": "42", "email": "test@example.com", "role": "EMPLOYEE"}
    token = create_access_token(data)
    payload = decode_access_token(token)
    assert payload["sub"] == "42"
    assert payload["email"] == "test@example.com"
    assert payload["role"] == "EMPLOYEE"


def test_user_registration_success(client):
    payload = {
        "name": "Jane Developer",
        "email": "jane.dev@trackit.internal",
        "password": "Password123!",
        "role": "EMPLOYEE",
    }
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 201
    body = response.json()
    assert body["success"] is True
    assert body["data"]["email"] == "jane.dev@trackit.internal"
    assert body["data"]["name"] == "Jane Developer"
    assert "password_hash" not in body["data"]


def test_user_registration_duplicate_email(client, employee_user):
    payload = {
        "name": "Duplicate Tester",
        "email": employee_user.email,
        "password": "AnotherPassword123!",
    }
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 409
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "EMAIL_ALREADY_EXISTS"


def test_user_login_success(client, employee_user):
    payload = {
        "email": employee_user.email,
        "password": "Password@123",
    }
    response = client.post("/api/v1/auth/login", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert "access_token" in body["data"]
    assert body["data"]["user"]["email"] == employee_user.email


def test_user_login_invalid_credentials(client, employee_user):
    payload = {
        "email": employee_user.email,
        "password": "WrongPassword!",
    }
    response = client.post("/api/v1/auth/login", json=payload)
    assert response.status_code == 401
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "INVALID_CREDENTIALS"


def test_get_current_user_profile(client, employee_user):
    headers = get_token_header(employee_user)
    response = client.get("/api/v1/auth/me", headers=headers)
    assert response.status_code == 200
    body = response.json()
    assert body["data"]["id"] == employee_user.id
    assert body["data"]["email"] == employee_user.email
