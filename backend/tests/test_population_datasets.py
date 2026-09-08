import io
import uuid

import pytest
from sqlalchemy import func, select

from app.core.db import async_session_maker
from app.models.population import (
    DatasetStatus,
    Granularity,
    PopulationDataset,
    PopulationMicrodata,
    PopulationRecord,
)
from app.services.population_aggregate import age_to_band, aggregate_rows
from app.services.population_import import (
    ImportReport,
    detect_granularity,
    iter_import_batches,
)
from app.services.population_jobs import run_aggregate, run_import
from tests.conftest import register_and_login

# asyncio_mode = auto (pytest.ini) runs the async tests; no module-level mark
# needed, and adding one would wrongly flag the pure-sync unit tests below.

MICRO_HEADER = "household_id,person_id,province_code,district_code,sector_code,area_type,sex,age,relationship_to_head,marital_status"
AGG_HEADER = "sub_region_id,age_band,population_count,urban_rural"


def _micro_row(hh: int, pid: int, age: int, sector: int = 1101, area: str = "urban", sex: str = "male") -> str:
    return f"HH{hh},{pid},1,12,{sector},{area},{sex},{age},head,married"


def micro_csv(n: int) -> str:
    rows = [MICRO_HEADER]
    for i in range(n):
        rows.append(_micro_row(hh=i // 4, pid=i % 4, age=i % 90, sector=1101 + (i % 3), area="urban" if i % 2 else "rural"))
    return "\n".join(rows) + "\n"


def agg_csv() -> str:
    return "\n".join(
        [
            AGG_HEADER,
            "1101,0-4,120,urban",
            "1101,5-9,90,urban",
            "1102,0-4,75,rural",
        ]
    ) + "\n"


async def _make_dataset(granularity: Granularity, region_id: str = "1") -> uuid.UUID:
    async with async_session_maker() as session:
        ds = PopulationDataset(
            name="Test set",
            region_id=region_id,
            year=2022,
            source="NISR Census",
            granularity=granularity,
            version=1,
            status=DatasetStatus.draft,
        )
        session.add(ds)
        await session.commit()
        return ds.id


# --- detection -------------------------------------------------------------

def test_detect_microdata_from_headers():
    assert detect_granularity(MICRO_HEADER.split(",")) is Granularity.microdata


def test_detect_aggregate_from_headers():
    assert detect_granularity(AGG_HEADER.split(",")) is Granularity.aggregate


def test_detect_unknown_headers_raises():
    with pytest.raises(ValueError):
        detect_granularity(["foo", "bar"])


def test_age_bands():
    assert age_to_band(0) == "0-4"
    assert age_to_band(12) == "10-14"
    assert age_to_band(84) == "80-84"
    assert age_to_band(85) == "85+"
    assert age_to_band(122) == "85+"


# --- chunked parsing ------------------------------------------------------

def test_large_parse_is_chunked_and_bounded():
    report = ImportReport()
    batches = list(iter_import_batches(io.StringIO(micro_csv(20_000)), chunk_size=1_000, report=report))
    assert report.imported == 20_000
    assert report.rejected == 0
    assert len(batches) == 20
    assert max(len(b.rows) for b in batches) <= 1_000


def test_invalid_rows_rejected_individually():
    csv = "\n".join(
        [
            MICRO_HEADER,
            _micro_row(1, 1, 30),                       # ok
            "HH2,2,1,12,1101,urban,male,999,head,",     # age out of range
            "HH3,3,1,99,1101,urban,male,30,head,",      # district malformed
            _micro_row(4, 4, 40),                       # ok
            "HH5,5,1,12,1101,alien,male,20,head,",      # bad area_type
        ]
    ) + "\n"
    report = ImportReport()
    batches = list(iter_import_batches(io.StringIO(csv), report=report))
    assert report.imported == 2
    assert report.rejected == 3
    assert len(report.rejection_samples) == 3
    assert sum(len(b.rows) for b in batches) == 2


def test_pure_aggregate_rows_helper():
    rows = [
        {"sector_code": 1101, "age": 3, "area_type": "urban"},
        {"sector_code": 1101, "age": 1, "area_type": "urban"},
        {"sector_code": 1101, "age": 40, "area_type": "urban"},
    ]
    out = aggregate_rows(rows)
    counts = {(r["sub_region_id"], r["age_band"]): r["population_count"] for r in out}
    assert counts[("1101", "0-4")] == 2
    assert counts[("1101", "40-44")] == 1
    assert all(r["density_per_km2"] is None for r in out)


# --- import job ----------------------------------------------------------

async def test_import_microdata_populates_microdata_tier(monkeypatch):
    dataset_id = await _make_dataset(Granularity.microdata)
    monkeypatch.setattr(
        "app.services.population_jobs.get_object",
        lambda key: micro_csv(500).encode(),
    )
    async with async_session_maker() as session:
        report = await run_import(session, dataset_id, "any-key")

    assert report["granularity"] == "microdata"
    assert report["imported"] == 500

    async with async_session_maker() as session:
        ds = await session.get(PopulationDataset, dataset_id)
        assert ds.status is DatasetStatus.validated
        micro = await session.scalar(
            select(func.count()).select_from(PopulationMicrodata).where(PopulationMicrodata.dataset_id == dataset_id)
        )
        records = await session.scalar(
            select(func.count()).select_from(PopulationRecord).where(PopulationRecord.dataset_id == dataset_id)
        )
    assert micro == 500
    assert records == 0


async def test_import_aggregate_skips_microdata_tier(monkeypatch):
    # user stated microdata, but the file is aggregate - detection overrides.
    dataset_id = await _make_dataset(Granularity.microdata, region_id="agg-region")
    monkeypatch.setattr("app.services.population_jobs.get_object", lambda key: agg_csv().encode())
    async with async_session_maker() as session:
        report = await run_import(session, dataset_id, "any-key")

    assert report["granularity"] == "aggregate"
    assert report["imported"] == 3

    async with async_session_maker() as session:
        ds = await session.get(PopulationDataset, dataset_id)
        assert ds.granularity is Granularity.aggregate
        micro = await session.scalar(
            select(func.count()).select_from(PopulationMicrodata).where(PopulationMicrodata.dataset_id == dataset_id)
        )
        total = await session.scalar(
            select(func.sum(PopulationRecord.population_count)).where(PopulationRecord.dataset_id == dataset_id)
        )
    assert micro == 0
    assert total == 285


# --- aggregation job ----------------------------------------------------

async def test_aggregate_is_idempotent(monkeypatch):
    dataset_id = await _make_dataset(Granularity.microdata, region_id="aggrun")
    monkeypatch.setattr("app.services.population_jobs.get_object", lambda key: micro_csv(400).encode())
    async with async_session_maker() as session:
        await run_import(session, dataset_id, "k")

    async def _count_and_total():
        async with async_session_maker() as session:
            await run_aggregate(session, dataset_id)
        async with async_session_maker() as session:
            n = await session.scalar(
                select(func.count()).select_from(PopulationRecord).where(PopulationRecord.dataset_id == dataset_id)
            )
            total = await session.scalar(
                select(func.sum(PopulationRecord.population_count)).where(PopulationRecord.dataset_id == dataset_id)
            )
        return n, total

    first = await _count_and_total()
    second = await _count_and_total()
    assert first == second
    assert first[1] == 400  # every microdata person accounted for exactly once


# --- endpoints --------------------------------------------------------

async def test_import_endpoint_creates_draft_and_enqueues(client, monkeypatch):
    client = await register_and_login(client, role="epidemiologist")

    calls = []
    monkeypatch.setattr(
        "app.api.population_datasets.import_population_dataset.delay",
        lambda *args: calls.append(args),
    )
    monkeypatch.setattr("app.api.population_datasets.put_object", lambda key, data: key)

    region = f"reg-{uuid.uuid4().hex[:6]}"
    resp = await client.post(
        "/population-datasets/import",
        data={"name": "RPHC5 2022", "region_id": region, "year": "2022", "source": "NISR Census", "granularity": "microdata"},
        files={"file": ("census.csv", micro_csv(10), "text/csv")},
    )
    assert resp.status_code == 202
    body = resp.json()
    assert body["status"] == "draft"
    assert body["version"] == 1
    assert len(calls) == 1


async def test_versions_ordered_desc(client, monkeypatch):
    client = await register_and_login(client, role="epidemiologist")
    monkeypatch.setattr("app.api.population_datasets.import_population_dataset.delay", lambda *a: None)
    monkeypatch.setattr("app.api.population_datasets.put_object", lambda key, data: key)

    region = f"reg-{uuid.uuid4().hex[:6]}"
    ids = []
    for _ in range(3):
        r = await client.post(
            "/population-datasets/import",
            data={"name": "v", "region_id": region, "year": "2022", "source": "NISR", "granularity": "microdata"},
            files={"file": ("c.csv", micro_csv(2), "text/csv")},
        )
        ids.append(r.json()["id"])

    versions = (await client.get(f"/population-datasets/{ids[-1]}/versions")).json()
    assert [v["version"] for v in versions] == [3, 2, 1]


async def test_aggregate_endpoint_rejects_aggregate_dataset(client, monkeypatch):
    client = await register_and_login(client, role="epidemiologist")
    dataset_id = await _make_dataset(Granularity.aggregate, region_id=f"r-{uuid.uuid4().hex[:6]}")

    resp = await client.post(f"/population-datasets/{dataset_id}/aggregate")
    assert resp.status_code == 400


async def test_detail_summary_stats(client, monkeypatch):
    client = await register_and_login(client, role="epidemiologist")
    dataset_id = await _make_dataset(Granularity.microdata, region_id=f"r-{uuid.uuid4().hex[:6]}")
    monkeypatch.setattr("app.services.population_jobs.get_object", lambda key: micro_csv(50).encode())
    async with async_session_maker() as session:
        await run_import(session, dataset_id, "k")

    detail = (await client.get(f"/population-datasets/{dataset_id}")).json()
    assert detail["stats_source"] == "microdata"
    assert detail["row_count"] == 50
    assert detail["total_population"] == 50
    assert detail["distribution"] == []

    async with async_session_maker() as session:
        await run_aggregate(session, dataset_id)
    aggregated = (await client.get(f"/population-datasets/{dataset_id}")).json()
    assert aggregated["stats_source"] == "records"
    assert aggregated["total_population"] == 50
    assert sum(d["population"] for d in aggregated["distribution"]) == 50
