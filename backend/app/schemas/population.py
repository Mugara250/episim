import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.population import DatasetStatus, Granularity


class PopulationDatasetCreate(BaseModel):
    """Metadata supplied alongside the uploaded file on import. `granularity` is
    the user's stated expectation - the import job re-detects it from the file's
    column headers and overrides this if they disagree.
    """

    name: str
    region_id: str
    year: int
    source: str
    granularity: Granularity = Granularity.microdata


class PopulationDatasetRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    region_id: str
    year: int
    source: str
    granularity: Granularity
    version: int
    status: DatasetStatus
    import_report: dict | None
    created_by: uuid.UUID | None
    created_at: datetime


class PopulationDatasetSummary(PopulationDatasetRead):
    """Detail view: dataset row plus computed summary stats. Counts come from
    `population_records` when the dataset has been aggregated, otherwise from
    the raw `population_microdata` tier.
    """

    total_population: int
    row_count: int
    stats_source: str  # "records" | "microdata" | "none"


class PopulationDatasetList(BaseModel):
    items: list[PopulationDatasetRead]
    total: int
    page: int
    page_size: int


class AggregateResponse(BaseModel):
    dataset_id: uuid.UUID
    status: str
    detail: str
