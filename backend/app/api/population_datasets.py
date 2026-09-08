import uuid

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_session
from app.core.storage import put_object
from app.core.users import current_active_user
from app.models.population import (
    DatasetStatus,
    Granularity,
    PopulationDataset,
    PopulationMicrodata,
    PopulationRecord,
)
from app.models.user import User
from app.schemas.population import (
    AggregateResponse,
    PopulationDatasetList,
    PopulationDatasetRead,
    PopulationDatasetSummary,
    RegionPopulation,
)
from app.workers.tasks import aggregate_population_dataset, import_population_dataset

router = APIRouter(prefix="/population-datasets", tags=["population-datasets"])


async def _get_or_404(db: AsyncSession, dataset_id: uuid.UUID) -> PopulationDataset:
    dataset = await db.get(PopulationDataset, dataset_id)
    if dataset is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Population dataset not found")
    return dataset


@router.get("", response_model=PopulationDatasetList)
async def list_population_datasets(
    db: AsyncSession = Depends(get_async_session),
    _: User = Depends(current_active_user),
    region_id: str | None = None,
    year: int | None = None,
    source: str | None = None,
    dataset_status: DatasetStatus | None = Query(default=None, alias="status"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=25, ge=1, le=200),
):
    filters = []
    if region_id is not None:
        filters.append(PopulationDataset.region_id == region_id)
    if year is not None:
        filters.append(PopulationDataset.year == year)
    if source is not None:
        filters.append(PopulationDataset.source.ilike(f"%{source}%"))
    if dataset_status is not None:
        filters.append(PopulationDataset.status == dataset_status)

    total = await db.scalar(select(func.count()).select_from(PopulationDataset).where(*filters))
    result = await db.execute(
        select(PopulationDataset)
        .where(*filters)
        .order_by(PopulationDataset.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    return PopulationDatasetList(
        items=list(result.scalars().all()),
        total=total or 0,
        page=page,
        page_size=page_size,
    )


@router.get("/{dataset_id}", response_model=PopulationDatasetSummary)
async def get_population_dataset(
    dataset_id: uuid.UUID,
    db: AsyncSession = Depends(get_async_session),
    _: User = Depends(current_active_user),
):
    dataset = await _get_or_404(db, dataset_id)

    record_count = await db.scalar(
        select(func.count()).select_from(PopulationRecord).where(PopulationRecord.dataset_id == dataset_id)
    )
    if record_count:
        total_population = await db.scalar(
            select(func.coalesce(func.sum(PopulationRecord.population_count), 0)).where(
                PopulationRecord.dataset_id == dataset_id
            )
        )
        stats_source, row_count = "records", record_count
    else:
        micro_count = await db.scalar(
            select(func.count()).select_from(PopulationMicrodata).where(PopulationMicrodata.dataset_id == dataset_id)
        )
        # microdata is row-per-person, so the row count is the population count
        total_population = micro_count or 0
        stats_source = "microdata" if micro_count else "none"
        row_count = micro_count or 0

    distribution: list[RegionPopulation] = []
    if record_count:
        by_sub_region = await db.execute(
            select(
                PopulationRecord.sub_region_id,
                func.sum(PopulationRecord.population_count),
            )
            .where(PopulationRecord.dataset_id == dataset_id)
            .group_by(PopulationRecord.sub_region_id)
        )
        # Roll sector codes up to district (leading 2 digits) for a legible chart.
        district_totals: dict[str, int] = {}
        for sub_region_id, pop in by_sub_region.all():
            district = str(sub_region_id)[:2]
            district_totals[district] = district_totals.get(district, 0) + int(pop)
        distribution = [
            RegionPopulation(region=district, population=pop)
            for district, pop in sorted(district_totals.items(), key=lambda kv: kv[1], reverse=True)
        ]

    return PopulationDatasetSummary(
        **PopulationDatasetRead.model_validate(dataset).model_dump(),
        total_population=total_population or 0,
        row_count=row_count,
        stats_source=stats_source,
        distribution=distribution,
    )


@router.post("/import", response_model=PopulationDatasetRead, status_code=status.HTTP_202_ACCEPTED)
async def import_population_dataset_endpoint(
    db: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user),
    name: str = Form(...),
    region_id: str = Form(...),
    year: int = Form(...),
    source: str = Form(...),
    granularity: Granularity = Form(default=Granularity.microdata),
    file: UploadFile = File(...),
):
    """Create a draft dataset, stash the upload, and hand parsing to a Celery
    task. Returns immediately - the request never blocks on the import.
    """
    latest_version = await db.scalar(
        select(func.max(PopulationDataset.version)).where(PopulationDataset.region_id == region_id)
    )

    dataset = PopulationDataset(
        name=name,
        region_id=region_id,
        year=year,
        source=source,
        granularity=granularity,
        version=(latest_version or 0) + 1,
        status=DatasetStatus.draft,
        created_by=user.id,
    )
    db.add(dataset)
    await db.commit()
    await db.refresh(dataset)

    object_key = f"population-imports/{dataset.id}/{file.filename or 'upload.csv'}"
    put_object(object_key, await file.read())
    import_population_dataset.delay(str(dataset.id), object_key)

    return dataset


@router.get("/{dataset_id}/versions", response_model=list[PopulationDatasetRead])
async def list_dataset_versions(
    dataset_id: uuid.UUID,
    db: AsyncSession = Depends(get_async_session),
    _: User = Depends(current_active_user),
):
    dataset = await _get_or_404(db, dataset_id)
    result = await db.execute(
        select(PopulationDataset)
        .where(PopulationDataset.region_id == dataset.region_id)
        .order_by(PopulationDataset.version.desc())
    )
    return list(result.scalars().all())


@router.post("/{dataset_id}/aggregate", response_model=AggregateResponse, status_code=status.HTTP_202_ACCEPTED)
async def aggregate_dataset(
    dataset_id: uuid.UUID,
    db: AsyncSession = Depends(get_async_session),
    _: User = Depends(current_active_user),
):
    dataset = await _get_or_404(db, dataset_id)
    if dataset.granularity is not Granularity.microdata:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            detail="Aggregation only applies to microdata datasets; this dataset is already aggregate-level.",
        )

    aggregate_population_dataset.delay(str(dataset_id))
    return AggregateResponse(
        dataset_id=dataset_id,
        status="queued",
        detail="Aggregation job queued; population_records will be recomputed.",
    )
