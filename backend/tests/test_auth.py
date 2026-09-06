"""End-to-end auth tests.

These exercise the real app against the configured DATABASE_URL (see
backend/.env) rather than mocking the database - run them with the dev
stack (`docker-compose up postgres`) already running.
"""

import uuid

import pytest

pytestmark = pytest.mark.asyncio


async def test_register_then_login(client):
    email = f"test-{uuid.uuid4().hex[:8]}@example.com"
    password = "SuperSecret123!"

    register_resp = await client.post(
        "/auth/register",
        json={"email": email, "password": password, "full_name": "Test User", "role": "analyst"},
    )
    assert register_resp.status_code == 201
    assert register_resp.json()["email"] == email

    login_resp = await client.post("/auth/login", json={"email": email, "password": password})
    assert login_resp.status_code == 200
    assert "access_token" in login_resp.json()

    bad_login_resp = await client.post("/auth/login", json={"email": email, "password": "wrong"})
    assert bad_login_resp.status_code == 400


async def test_me_requires_auth(client):
    resp = await client.get("/users/me")
    assert resp.status_code == 401
