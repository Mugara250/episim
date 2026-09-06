import pytest

from tests.conftest import register_and_login

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


async def _get_a_builtin(client) -> dict:
    resp = await client.get("/disease-presets")
    return next(p for p in resp.json() if p["is_builtin"])


async def test_list_includes_builtins(client):
    client = await register_and_login(client, role="analyst")
    resp = await client.get("/disease-presets")
    assert resp.status_code == 200
    names = [p["name"] for p in resp.json()]
    assert "COVID-19 (wild type)" in names
    assert "Cholera" in names


async def test_admin_can_create_and_edit_own_custom_preset(client):
    client = await register_and_login(client, role="admin")

    create_resp = await client.post("/disease-presets", json=PRESET_PAYLOAD)
    assert create_resp.status_code == 201
    preset = create_resp.json()
    assert preset["is_builtin"] is False
    assert preset["permissions"]["is_owner"] is True
    assert preset["permissions"]["can_edit"] is True

    update_resp = await client.put(f"/disease-presets/{preset['id']}", json={**PRESET_PAYLOAD, "r0": 3.5})
    assert update_resp.status_code == 200
    assert update_resp.json()["r0"] == 3.5


async def test_standard_role_cannot_create_preset(client):
    client = await register_and_login(client, role="analyst")
    resp = await client.post("/disease-presets", json=PRESET_PAYLOAD)
    assert resp.status_code == 403


async def test_epidemiologist_with_admin_privileges_can_create_preset(client):
    client = await register_and_login(client, role="epidemiologist", has_admin_privileges=True)
    resp = await client.post("/disease-presets", json=PRESET_PAYLOAD)
    assert resp.status_code == 201


async def test_standard_role_cannot_edit_builtin(client):
    client = await register_and_login(client, role="analyst")
    builtin = await _get_a_builtin(client)
    assert builtin["permissions"]["can_edit"] is False

    resp = await client.put(f"/disease-presets/{builtin['id']}", json=PRESET_PAYLOAD)
    assert resp.status_code == 403


async def test_admin_can_edit_builtin(client):
    client = await register_and_login(client, role="admin")
    builtin = await _get_a_builtin(client)
    assert builtin["permissions"]["can_edit"] is True

    resp = await client.put(f"/disease-presets/{builtin['id']}", json={**PRESET_PAYLOAD, "r0": 9.9})
    assert resp.status_code == 200
    assert resp.json()["r0"] == 9.9

    # restore so other tests relying on stable builtin values aren't affected
    original = {k: builtin[k] for k in PRESET_PAYLOAD}
    await client.put(f"/disease-presets/{builtin['id']}", json=original)


async def test_clone_creates_editable_custom_copy(client):
    client = await register_and_login(client, role="analyst")
    builtin = await _get_a_builtin(client)

    resp = await client.post(f"/disease-presets/{builtin['id']}/clone", json={})
    assert resp.status_code == 201
    clone = resp.json()
    assert clone["is_builtin"] is False
    assert clone["cloned_from_id"] == builtin["id"]
    assert clone["name"] == f"{builtin['name']} (Custom)"
    assert clone["r0"] == builtin["r0"]
    assert clone["permissions"]["is_owner"] is True
    assert clone["permissions"]["can_edit"] is True

    # the owner (even a standard analyst) can now edit their clone
    edit_resp = await client.put(f"/disease-presets/{clone['id']}", json={**PRESET_PAYLOAD, "r0": 4.2})
    assert edit_resp.status_code == 200


async def test_clone_accepts_name_override(client):
    client = await register_and_login(client, role="analyst")
    builtin = await _get_a_builtin(client)

    resp = await client.post(f"/disease-presets/{builtin['id']}/clone", json={"name": "My Custom Variant"})
    assert resp.status_code == 201
    assert resp.json()["name"] == "My Custom Variant"


async def test_policy_maker_cannot_create_or_clone(client):
    client = await register_and_login(client, role="policy_maker")
    builtin = await _get_a_builtin(client)

    assert builtin["permissions"]["can_clone"] is False

    create_resp = await client.post("/disease-presets", json=PRESET_PAYLOAD)
    assert create_resp.status_code == 403

    clone_resp = await client.post(f"/disease-presets/{builtin['id']}/clone", json={})
    assert clone_resp.status_code == 403


async def test_user_cannot_edit_or_delete_another_users_custom_preset(client):
    owner = await register_and_login(client, role="analyst")
    builtin = await _get_a_builtin(owner)
    clone_resp = await owner.post(f"/disease-presets/{builtin['id']}/clone", json={})
    preset_id = clone_resp.json()["id"]

    other = await register_and_login(client, role="analyst")

    edit_resp = await other.put(f"/disease-presets/{preset_id}", json=PRESET_PAYLOAD)
    assert edit_resp.status_code == 403

    delete_resp = await other.delete(f"/disease-presets/{preset_id}")
    assert delete_resp.status_code == 403


async def test_owner_can_delete_own_custom_preset(client):
    client = await register_and_login(client, role="analyst")
    builtin = await _get_a_builtin(client)
    clone_resp = await client.post(f"/disease-presets/{builtin['id']}/clone", json={})
    preset_id = clone_resp.json()["id"]

    delete_resp = await client.delete(f"/disease-presets/{preset_id}")
    assert delete_resp.status_code == 204

    get_resp = await client.get(f"/disease-presets/{preset_id}")
    assert get_resp.status_code == 404


async def test_builtin_cannot_be_deleted_even_by_admin(client):
    client = await register_and_login(client, role="admin")
    builtin = await _get_a_builtin(client)

    resp = await client.delete(f"/disease-presets/{builtin['id']}")
    assert resp.status_code == 403
