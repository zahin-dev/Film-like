"""
Auth endpoint tests for the Film-like API.

Covers the /auth/register and /auth/login routes using an in-memory
SQLite database provided by the conftest fixtures. Each test gets a
clean database, so tests are fully isolated from one another.
"""

import pytest
from fastapi import status


VALID_USER = {
    "first_name": "John",
    "last_name": "Doe",
    "email": "JohnDoe@test.com",
    "password": "Test1234!",
    "age": 18
}


# ---------------------------------------------------------------------------
# Register — happy path
# ---------------------------------------------------------------------------

def test_register_valid_user(client):
    """A valid registration payload returns 201 and creates the user."""
    response = client.post("/auth/register", json=VALID_USER)
    assert response.status_code == status.HTTP_201_CREATED


def test_register_response_body(client):
    """The registration response contains a JWT token and the user profile."""
    response = client.post("/auth/register", json=VALID_USER)
    body = response.json()
    assert "token" in body
    assert isinstance(body["token"], str)
    assert len(body["token"]) > 0
    user = body["user"]
    assert user["first_name"] == VALID_USER["first_name"]
    assert user["last_name"] == VALID_USER["last_name"]
    assert user["email"] == VALID_USER["email"]
    assert "id" in user
    assert "created_at" in user
    assert "hashed_password" not in user
    assert "is_admin" not in user


def test_register_without_age(client):
    """Age is optional — registration without it returns 201."""
    payload = {k: v for k, v in VALID_USER.items() if k != "age"}
    response = client.post("/auth/register", json=payload)
    assert response.status_code == status.HTTP_201_CREATED


# ---------------------------------------------------------------------------
# Register — duplicate / conflict
# ---------------------------------------------------------------------------

def test_user_already_registered(client):
    """Registering the same email twice returns 409 with a descriptive message."""
    client.post("/auth/register", json=VALID_USER)
    response = client.post("/auth/register", json=VALID_USER)
    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.json()["detail"] == "Email already registered"


# ---------------------------------------------------------------------------
# Register — email validation
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("bad_email", [
    "InvalidEmail",
    "missing-at-sign.com",
    "@nodomain.com",
    "no-tld@domain",
    "",
])
def test_register_invalid_email(client, bad_email):
    """Malformed email addresses are rejected with 422."""
    payload = {**VALID_USER, "email": bad_email}
    response = client.post("/auth/register", json=payload)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


# ---------------------------------------------------------------------------
# Register — password validation
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("bad_password", [
    "short1!",           # too short (7 chars)
    "NoDigitPassword!",  # missing digit
    "NoSpecial1234",     # missing special character
    "",                  # empty
])
def test_register_invalid_password(client, bad_password):
    """Passwords that fail complexity rules are rejected with 422."""
    payload = {**VALID_USER, "password": bad_password}
    response = client.post("/auth/register", json=payload)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_register_password_too_long(client):
    """A password exceeding 64 characters is rejected with 422."""
    payload = {**VALID_USER, "password": "A1!" + "a" * 62}
    response = client.post("/auth/register", json=payload)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


# ---------------------------------------------------------------------------
# Register — age validation
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("bad_age", [0, -1, 121, 999])
def test_register_invalid_age(client, bad_age):
    """Age values outside 1–120 are rejected with 422."""
    payload = {**VALID_USER, "email": f"user{bad_age}@test.com", "age": bad_age}
    response = client.post("/auth/register", json=payload)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


# ---------------------------------------------------------------------------
# Register — missing required fields
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("missing_field", [
    "first_name", "last_name", "email", "password"
])
def test_register_missing_required_field(client, missing_field):
    """Omitting any required field is rejected with 422."""
    payload = {k: v for k, v in VALID_USER.items() if k != missing_field}
    response = client.post("/auth/register", json=payload)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


# ---------------------------------------------------------------------------
# Login — happy path
# ---------------------------------------------------------------------------

def test_login_valid_user(client):
    """Correct credentials after registration return 200 with a JWT token."""
    client.post("/auth/register", json=VALID_USER)
    response = client.post(
        "/auth/login",
        json={"email": "JohnDoe@test.com", "password": "Test1234!"}
    )
    assert response.status_code == status.HTTP_200_OK


def test_login_response_body(client):
    """The login response contains a JWT token and the user profile."""
    client.post("/auth/register", json=VALID_USER)
    response = client.post(
        "/auth/login",
        json={"email": VALID_USER["email"], "password": VALID_USER["password"]}
    )
    body = response.json()
    assert "token" in body
    assert isinstance(body["token"], str)
    assert len(body["token"]) > 0
    assert body["user"]["email"] == VALID_USER["email"]


# ---------------------------------------------------------------------------
# Login — failure paths
# ---------------------------------------------------------------------------

def test_login_non_registered_user(client):
    """An unknown email returns 401 with a generic 'Invalid credentials' message."""
    client.post("/auth/register", json=VALID_USER)
    response = client.post(
        "/auth/login",
        json={"email": "UnregisteredUser@test.com", "password": "Test1234!"}
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Invalid credentials"


def test_login_wrong_password(client):
    """A wrong password for a registered email returns 401 — same message as
    unknown email to prevent user enumeration."""
    client.post("/auth/register", json=VALID_USER)
    response = client.post(
        "/auth/login",
        json={"email": "JohnDoe@test.com", "password": "!4321tseT"}
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Invalid credentials"


def test_login_invalid_email_format(client):
    """A malformed email at login is rejected with 422 before hitting the DB."""
    response = client.post(
        "/auth/login",
        json={"email": "not-an-email", "password": "Test1234!"}
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
