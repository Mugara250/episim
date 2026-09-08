import asyncio
import uuid

from app.services.population_jobs import run_aggregate, run_import
from app.workers import celery_app
from app.workers.db import worker_session


@celery_app.task(name="app.workers.tasks.ping")
def ping() -> str:
    """Smoke-test task confirming the worker can pick up jobs from Redis."""
    return "pong"


@celery_app.task(name="app.workers.tasks.import_population_dataset")
def import_population_dataset(dataset_id: str, object_key: str) -> dict:
    """Parse an uploaded census file (chunked) and populate the matching
    storage tier. Sets status=validated on success, leaves it draft on failure.
    """
    return asyncio.run(_import_population_dataset(dataset_id, object_key))


async def _import_population_dataset(dataset_id: str, object_key: str) -> dict:
    async with worker_session() as session:
        return await run_import(session, uuid.UUID(dataset_id), object_key)


@celery_app.task(name="app.workers.tasks.aggregate_population_dataset")
def aggregate_population_dataset(dataset_id: str) -> dict:
    """(Re)compute population_records from population_microdata for a dataset."""
    return asyncio.run(_aggregate_population_dataset(dataset_id))


async def _aggregate_population_dataset(dataset_id: str) -> dict:
    async with worker_session() as session:
        return await run_aggregate(session, uuid.UUID(dataset_id))
