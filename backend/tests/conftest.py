import uuid

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import update

from app.core.db import async_session_maker
from app.main import app
from app.models.user import User

DEFAULT_PASSWORD = "SuperSecret123!"


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


async def register_and_login(client: AsyncClient, role: str = "analyst", has_admin_privileges: bool = False) -> AsyncClient:
    """Registers a fresh user, optionally grants admin privileges directly in
    the DB (not exposed via the API, by design - see UserCreate), logs in,
    and attaches the bearer token to the client for subsequent calls.
    """
    email = f"test-{uuid.uuid4().hex[:10]}@example.com"
    register_resp = await client.post(
        "/auth/register",
        json={"email": email, "password": DEFAULT_PASSWORD, "first_name": "Test", "last_name": "User", "role": role},
    )
    user_id = register_resp.json()["id"]

    if has_admin_privileges:
        async with async_session_maker() as session:
            await session.execute(update(User).where(User.id == uuid.UUID(user_id)).values(has_admin_privileges=True))
            await session.commit()

    login_resp = await client.post("/auth/login", json={"email": email, "password": DEFAULT_PASSWORD})
    token = login_resp.json()["access_token"]
    client.headers["Authorization"] = f"Bearer {token}"
    client.user_id = user_id  # type: ignore[attr-defined]
    return client
