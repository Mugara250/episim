import pytest

from tests.conftest import register_and_login

pytestmark = pytest.mark.asyncio


async def _get_a_type_id(client) -> str:
    resp = await client.get("/intervention-types")
    return next(t for t in resp.json() if t["key"] == "lockdown")["id"]


async def test_create_package_with_zero_items_is_allowed(client):
    client = await register_and_login(client, role="analyst")
    resp = await client.post("/intervention-packages", json={"name": "Empty Package", "description": None})
    assert resp.status_code == 201
    body = resp.json()
    assert body["item_count"] == 0
    assert body["permissions"]["is_owner"] is True
    assert body["permissions"]["can_edit"] is True


async def test_add_item_with_null_end_day_stores_null(client):
    client = await register_and_login(client, role="analyst")
    type_id = await _get_a_type_id(client)
    package_resp = await client.post("/intervention-packages", json={"name": "Pkg", "description": "d"})
    package_id = package_resp.json()["id"]

    item_resp = await client.post(
        f"/intervention-packages/{package_id}/items",
        json={"type_id": type_id, "start_day": 10, "end_day": None, "coverage": 0.5},
    )
    assert item_resp.status_code == 201
    body = item_resp.json()
    assert body["end_day"] is None
    assert body["type_name"] == "Lockdown"
    assert body["effect_mechanism"] == "rate_multiplier"

    detail = await client.get(f"/intervention-packages/{package_id}")
    assert detail.json()["item_count"] == 1
    assert detail.json()["items"][0]["end_day"] is None


async def test_rejects_coverage_out_of_range(client):
    client = await register_and_login(client, role="analyst")
    type_id = await _get_a_type_id(client)
    package_id = (await client.post("/intervention-packages", json={"name": "Pkg"})).json()["id"]

    resp = await client.post(
        f"/intervention-packages/{package_id}/items",
        json={"type_id": type_id, "start_day": 0, "coverage": 1.5},
    )
    assert resp.status_code == 422


async def test_rejects_invalid_type_id(client):
    client = await register_and_login(client, role="analyst")
    package_id = (await client.post("/intervention-packages", json={"name": "Pkg"})).json()["id"]

    resp = await client.post(
        f"/intervention-packages/{package_id}/items",
        json={"type_id": "00000000-0000-0000-0000-000000000000", "start_day": 0, "coverage": 0.5},
    )
    assert resp.status_code == 422


async def test_rejects_end_day_before_start_day(client):
    client = await register_and_login(client, role="analyst")
    type_id = await _get_a_type_id(client)
    package_id = (await client.post("/intervention-packages", json={"name": "Pkg"})).json()["id"]

    resp = await client.post(
        f"/intervention-packages/{package_id}/items",
        json={"type_id": type_id, "start_day": 20, "end_day": 10, "coverage": 0.5},
    )
    assert resp.status_code == 422


async def test_rejects_out_of_range_effectiveness_override(client):
    client = await register_and_login(client, role="analyst")
    type_id = await _get_a_type_id(client)
    package_id = (await client.post("/intervention-packages", json={"name": "Pkg"})).json()["id"]

    resp = await client.post(
        f"/intervention-packages/{package_id}/items",
        json={"type_id": type_id, "start_day": 0, "coverage": 0.5, "effectiveness_override": 1.2},
    )
    assert resp.status_code == 422


async def test_overlapping_day_ranges_are_both_accepted(client):
    client = await register_and_login(client, role="analyst")
    type_id = await _get_a_type_id(client)
    package_id = (await client.post("/intervention-packages", json={"name": "Pkg"})).json()["id"]

    first = await client.post(
        f"/intervention-packages/{package_id}/items",
        json={"type_id": type_id, "start_day": 0, "end_day": 30, "coverage": 0.5},
    )
    second = await client.post(
        f"/intervention-packages/{package_id}/items",
        json={"type_id": type_id, "start_day": 10, "end_day": 40, "coverage": 0.3},
    )
    assert first.status_code == 201
    assert second.status_code == 201

    detail = await client.get(f"/intervention-packages/{package_id}")
    assert detail.json()["item_count"] == 2


async def test_remove_item_from_package(client):
    client = await register_and_login(client, role="analyst")
    type_id = await _get_a_type_id(client)
    package_id = (await client.post("/intervention-packages", json={"name": "Pkg"})).json()["id"]
    item = await client.post(
        f"/intervention-packages/{package_id}/items",
        json={"type_id": type_id, "start_day": 0, "coverage": 0.5},
    )
    item_id = item.json()["id"]

    delete_resp = await client.delete(f"/intervention-packages/{package_id}/items/{item_id}")
    assert delete_resp.status_code == 204

    detail = await client.get(f"/intervention-packages/{package_id}")
    assert detail.json()["item_count"] == 0


async def test_only_creator_can_add_or_remove_items(client):
    owner = await register_and_login(client, role="analyst")
    type_id = await _get_a_type_id(owner)
    package_id = (await owner.post("/intervention-packages", json={"name": "Pkg"})).json()["id"]

    other = await register_and_login(client, role="analyst")
    resp = await other.post(
        f"/intervention-packages/{package_id}/items",
        json={"type_id": type_id, "start_day": 0, "coverage": 0.5},
    )
    assert resp.status_code == 403


async def test_deleting_package_cascades_to_items(client):
    client = await register_and_login(client, role="analyst")
    type_id = await _get_a_type_id(client)
    package_id = (await client.post("/intervention-packages", json={"name": "Pkg"})).json()["id"]
    await client.post(
        f"/intervention-packages/{package_id}/items",
        json={"type_id": type_id, "start_day": 0, "coverage": 0.5},
    )

    delete_resp = await client.delete(f"/intervention-packages/{package_id}")
    assert delete_resp.status_code == 204

    get_resp = await client.get(f"/intervention-packages/{package_id}")
    assert get_resp.status_code == 404


async def test_deleting_intervention_type_in_use_is_rejected(client):
    import uuid

    client = await register_and_login(client, role="analyst")
    type_resp = await client.post(
        "/intervention-types",
        json={
            "key": f"will-be-referenced-{uuid.uuid4().hex[:8]}",
            "name": "Referenced Type",
            "effect_mechanism": "rate_multiplier",
            "default_effect_size": 0.3,
        },
    )
    type_id = type_resp.json()["id"]
    package_id = (await client.post("/intervention-packages", json={"name": "Pkg"})).json()["id"]
    await client.post(
        f"/intervention-packages/{package_id}/items",
        json={"type_id": type_id, "start_day": 0, "coverage": 0.5},
    )

    # No DELETE /intervention-types/{id} endpoint is exposed at all - the
    # RESTRICT FK is the enforcement point. Confirm it holds at the DB level
    # via the ORM directly rather than skipping this guarantee untested.
    from sqlalchemy.exc import IntegrityError

    from app.core.db import async_session_maker
    from app.models.intervention import InterventionType

    async with async_session_maker() as session:
        obj = await session.get(InterventionType, type_id)
        await session.delete(obj)
        with pytest.raises(IntegrityError):
            await session.commit()
