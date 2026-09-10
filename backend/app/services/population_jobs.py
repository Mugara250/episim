"""Async bodies of the population import / aggregation jobs.

Split out from the Celery tasks so they can be driven directly from tests with
a normal AsyncSession.
"""
from __future__ import annotations

import io
import uuid

from sqlalchemy import delete, insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.storage import get_object
from app.models.population import (
    DatasetStatus,
    Granularity,
    PopulationDataset,
    PopulationMicrodata,
    PopulationRecord,
)
from app.services.population_aggregate import aggregation_query
from app.services.population_import import ImportReport, iter_import_batches

BATCH_INSERT_SIZE = 5_000

# Persist running progress to the dataset row roughly this often (in rows seen),
# so a polling client sees the bar move without a commit per insert batch.
PROGRESS_COMMIT_EVERY = 25_000

_TIER_MODEL = {"microdata": PopulationMicrodata, "records": PopulationRecord}


def _estimate_total_rows(data: bytes) -> int | None:
    """Cheap up-front data-row count: newlines minus the header. The file is
    already fully in memory, so this is a single C-level scan. Returns None for
    an empty file or one with no trailing newline ambiguity worth reporting.
    """
    newlines = data.count(b"\n")
    if newlines <= 1:
        return None
    # If the file doesn't end in a newline the last row isn't counted; add it.
    trailing = 0 if data.endswith(b"\n") else 1
    return newlines - 1 + trailing


async def _bulk_insert(session: AsyncSession, model, dataset_id: uuid.UUID, rows: list[dict]) -> None:
    for start in range(0, len(rows), BATCH_INSERT_SIZE):
        window = rows[start : start + BATCH_INSERT_SIZE]
        await session.execute(insert(model), [{"dataset_id": dataset_id, **row} for row in window])


async def run_import(session: AsyncSession, dataset_id: uuid.UUID, object_key: str) -> dict:
    dataset = await session.get(PopulationDataset, dataset_id)
    if dataset is None:
        return {"error": "dataset not found"}

    report = ImportReport()
    try:
        data = get_object(object_key)
        report.total_rows = _estimate_total_rows(data)

        # Mark the dataset in-progress before the (potentially long) parse so a
        # polling client can distinguish "running" from "queued" or "failed".
        dataset.status = DatasetStatus.processing
        dataset.import_report = report.as_dict()
        await session.commit()

        last_committed = 0
        for batch in iter_import_batches(io.BytesIO(data), dataset.granularity, report=report):
            await _bulk_insert(session, _TIER_MODEL[batch.tier], dataset_id, batch.rows)
            if report.rows_processed - last_committed >= PROGRESS_COMMIT_EVERY:
                dataset.import_report = report.as_dict()
                await session.commit()
                last_committed = report.rows_processed

        report.phase = "done"
        # Detection from the file's headers wins over what the user selected.
        dataset.granularity = Granularity(report.granularity)
        dataset.status = DatasetStatus.validated
        dataset.import_report = report.as_dict()
        await session.commit()
        return report.as_dict()
    except Exception as exc:  # noqa: BLE001 - failure must be recorded, not swallowed
        await session.rollback()
        # Progress commits above may have persisted partial tier rows; clear them
        # so a failed import leaves no half-loaded data behind.
        await session.execute(
            delete(PopulationMicrodata).where(PopulationMicrodata.dataset_id == dataset_id)
        )
        await session.execute(
            delete(PopulationRecord).where(PopulationRecord.dataset_id == dataset_id)
        )
        report.phase = "done"
        dataset = await session.get(PopulationDataset, dataset_id)
        if dataset is not None:
            dataset.status = DatasetStatus.failed
            dataset.import_report = {**report.as_dict(), "error": str(exc)}
        await session.commit()
        raise


async def run_aggregate(session: AsyncSession, dataset_id: uuid.UUID) -> dict:
    dataset = await session.get(PopulationDataset, dataset_id)
    if dataset is None:
        return {"error": "dataset not found"}
    if dataset.granularity is not Granularity.microdata:
        raise ValueError("Aggregation only applies to microdata datasets")

    # Idempotent: clear the previous aggregate before recomputing so a re-run
    # after a data correction doesn't leave stale rows.
    await session.execute(delete(PopulationRecord).where(PopulationRecord.dataset_id == dataset_id))

    result = await session.execute(aggregation_query(dataset_id))
    rows = [
        {
            "sub_region_id": row.sub_region_id,
            "age_band": row.age_band,
            "urban_rural": row.urban_rural,
            "population_count": row.population_count,
            "density_per_km2": None,
        }
        for row in result.all()
    ]
    await _bulk_insert(session, PopulationRecord, dataset_id, rows)
    await session.commit()
    return {"groups": len(rows)}
