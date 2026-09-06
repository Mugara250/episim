import uuid

import pytest

pytestmark = pytest.mark.asyncio

PRESET_PAYLOAD = {
    "name": "Test Pathogen",
    "r0": 2.0,
    "incubation_period_days": 3.0,
    "infectious_period_days": 5.0,
    "mortality_rate": 0.01,
    "asymptomatic_fraction": 0.1,
    "transmission_route": "contact",
}


async def _authed_client(client):
    email = f"preset-test-{uuid.uuid4().hex[:8]}@example.com"
    password = "SuperSecret123!"
    await client.post(
        "/auth/register",
        json={"email": email, "password": password, "full_name": "Preset Tester", "role": "admin"},
    )
    login_resp = await client.post("/auth/login", json={"email": email, "password": password})
    token = login_resp.json()["access_token"]
    client.headers["Authorization"] = f"Bearer {token}"
    return client


async def test_list_includes_builtins(client):
    resp = await client.get("/disease-presets")
    assert resp.status_code == 200
    names = [p["name"] for p in resp.json()]
    assert "COVID-19 (wild type)" in names
    assert "Cholera" in names


async def test_create_and_edit_custom_preset(client):
    client = await _authed_client(client)

    create_resp = await client.post("/disease-presets", json=PRESET_PAYLOAD)
    assert create_resp.status_code == 201
    preset = create_resp.json()
    assert preset["is_builtin"] is False

    update_resp = await client.put(f"/disease-presets/{preset['id']}", json={**PRESET_PAYLOAD, "r0": 3.5})
    assert update_resp.status_code == 200
    assert update_resp.json()["r0"] == 3.5


async def test_builtin_cannot_be_edited(client):
    client = await _authed_client(client)

    list_resp = await client.get("/disease-presets")
    builtin = next(p for p in list_resp.json() if p["is_builtin"])

    resp = await client.put(f"/disease-presets/{builtin['id']}", json=PRESET_PAYLOAD)
    assert resp.status_code == 403
