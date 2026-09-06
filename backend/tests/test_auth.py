"""End-to-end auth tests.

These exercise the real app against the configured DATABASE_URL (see
backend/.env) rather than mocking the database - run them with the dev
stack (`docker-compose up postgres`) already running.
"""

import uuid

import pytest

from tests.conftest import register_and_login

pytestmark = pytest.mark.asyncio


async def test_register_then_login(client):
    email = f"test-{uuid.uuid4().hex[:8]}@example.com"
    password = "SuperSecret123!"

    register_resp = await client.post(
        "/auth/register",
        json={"email": email, "password": password, "first_name": "Test", "last_name": "User", "role": "analyst"},
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


async def test_get_public_user_profile(client):
    viewer = await register_and_login(client, role="analyst")
    other = await register_and_login(client, role="epidemiologist")
    other_id = other.user_id  # type: ignore[attr-defined]

    resp = await viewer.get(f"/users/{other_id}")
    assert resp.status_code == 200
    body = resp.json()
    assert body["id"] == other_id
    assert body["first_name"] == "Test"
    assert body["last_name"] == "User"
    assert body["role"] == "epidemiologist"
    # public profile must not leak sensitive fields
    assert "email" not in body
    assert "phone" not in body


async def test_me_route_not_shadowed_by_user_id_route(client):
    client = await register_and_login(client, role="analyst")
    resp = await client.get("/users/me")
    assert resp.status_code == 200
    assert resp.json()["id"] == client.user_id  # type: ignore[attr-defined]


async def test_get_public_user_profile_404_for_unknown_id(client):
    client = await register_and_login(client, role="analyst")
    resp = await client.get(f"/users/{uuid.uuid4()}")
    assert resp.status_code == 404
