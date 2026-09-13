import uuid

import pytest

from tests.conftest import register_and_login

pytestmark = pytest.mark.asyncio


def _type_payload() -> dict:
    return {
        "key": f"test-custom-type-{uuid.uuid4().hex[:8]}",
        "name": "Test Custom Type",
        "effect_mechanism": "rate_multiplier",
        "default_effect_size": 0.4,
        "source_citation": "made up for a test",
    }


async def _get_a_builtin(client) -> dict:
    resp = await client.get("/intervention-types")
    return next(t for t in resp.json() if t["is_builtin"])


async def test_list_includes_five_builtins_with_placeholder_citation(client):
    client = await register_and_login(client, role="analyst")
    resp = await client.get("/intervention-types")
    assert resp.status_code == 200
    builtins = [t for t in resp.json() if t["is_builtin"]]
    assert len(builtins) == 5
    keys = {t["key"] for t in builtins}
    assert keys == {"vaccination", "lockdown", "masking", "testing", "contact_tracing"}
    for t in builtins:
        assert t["source_citation"] == "Placeholder — needs literature review before use"

    vaccination = next(t for t in builtins if t["key"] == "vaccination")
    assert vaccination["effect_mechanism"] == "compartment_shift"
    for key in ("lockdown", "masking", "testing", "contact_tracing"):
        assert next(t for t in builtins if t["key"] == key)["effect_mechanism"] == "rate_multiplier"


async def test_any_authenticated_user_can_create_custom_type(client):
    client = await register_and_login(client, role="analyst")
    resp = await client.post("/intervention-types", json=_type_payload())
    assert resp.status_code == 201
    body = resp.json()
    assert body["is_builtin"] is False
    assert body["permissions"]["is_owner"] is True
    assert body["permissions"]["can_edit"] is True


async def test_standard_role_cannot_edit_builtin(client):
    client = await register_and_login(client, role="analyst")
    builtin = await _get_a_builtin(client)
    assert builtin["permissions"]["can_edit"] is False

    resp = await client.put(f"/intervention-types/{builtin['id']}", json={**_type_payload(), "key": builtin["key"]})
    assert resp.status_code == 403


async def test_admin_can_edit_builtin(client):
    client = await register_and_login(client, role="admin")
    builtin = await _get_a_builtin(client)
    assert builtin["permissions"]["can_edit"] is True

    resp = await client.put(
        f"/intervention-types/{builtin['id']}", json={**_type_payload(), "key": builtin["key"], "default_effect_size": 0.6}
    )
    assert resp.status_code == 200
    assert resp.json()["default_effect_size"] == 0.6

    # restore so other tests relying on stable builtin values aren't affected
    original = {
        "key": builtin["key"],
        "name": builtin["name"],
        "effect_mechanism": builtin["effect_mechanism"],
        "default_effect_size": builtin["default_effect_size"],
        "source_citation": builtin["source_citation"],
    }
    await client.put(f"/intervention-types/{builtin['id']}", json=original)


async def test_clone_creates_editable_custom_copy_without_touching_original(client):
    client = await register_and_login(client, role="analyst")
    builtin = await _get_a_builtin(client)

    resp = await client.post(f"/intervention-types/{builtin['id']}/clone", json={})
    assert resp.status_code == 201
    clone = resp.json()
    assert clone["is_builtin"] is False
    assert clone["name"] == f"{builtin['name']} (Custom)"
    assert clone["default_effect_size"] == builtin["default_effect_size"]
    assert clone["permissions"]["is_owner"] is True
    assert clone["permissions"]["can_edit"] is True

    edit_resp = await client.put(
        f"/intervention-types/{clone['id']}", json={**_type_payload(), "key": clone["key"], "default_effect_size": 0.9}
    )
    assert edit_resp.status_code == 200

    original_resp = await client.get(f"/intervention-types/{builtin['id']}")
    assert original_resp.json()["default_effect_size"] == builtin["default_effect_size"]


async def test_clone_accepts_name_override(client):
    client = await register_and_login(client, role="analyst")
    builtin = await _get_a_builtin(client)

    resp = await client.post(f"/intervention-types/{builtin['id']}/clone", json={"name": "My Variant"})
    assert resp.status_code == 201
    assert resp.json()["name"] == "My Variant"


async def test_policy_maker_cannot_clone(client):
    client = await register_and_login(client, role="policy_maker")
    builtin = await _get_a_builtin(client)
    assert builtin["permissions"]["can_clone"] is False

    resp = await client.post(f"/intervention-types/{builtin['id']}/clone", json={})
    assert resp.status_code == 403


async def test_user_cannot_edit_another_users_custom_type(client):
    owner = await register_and_login(client, role="analyst")
    resp = await owner.post("/intervention-types", json=_type_payload())
    body = resp.json()
    type_id, type_key = body["id"], body["key"]

    other = await register_and_login(client, role="analyst")
    edit_resp = await other.put(
        f"/intervention-types/{type_id}", json={**_type_payload(), "key": type_key, "default_effect_size": 0.9}
    )
    assert edit_resp.status_code == 403
