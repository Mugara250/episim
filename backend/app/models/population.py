import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, Float, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class Granularity(str, enum.Enum):
    """Which storage tier a dataset populates.

    `microdata` datasets land in `population_microdata` (row-per-person) and
    can be aggregated down into `population_records`. `aggregate` datasets are
    imported straight into `population_records` and skip the microdata tier.
    """

    microdata = "microdata"
    aggregate = "aggregate"


class DatasetStatus(str, enum.Enum):
    draft = "draft"
    # Set while the import job is parsing the upload; `import_report` carries
    # running progress (phase / rows_processed / total_rows) during this phase.
    processing = "processing"
    validated = "validated"
    # Import job raised; `import_report["error"]` holds the reason.
    failed = "failed"
    archived = "archived"


class AreaType(str, enum.Enum):
    urban = "urban"
    rural = "rural"


class Sex(str, enum.Enum):
    male = "male"
    female = "female"


class RelationshipToHead(str, enum.Enum):
    head = "head"
    spouse = "spouse"
    child = "child"
    parent = "parent"
    other_relative = "other_relative"
    non_relative = "non_relative"


class MaritalStatus(str, enum.Enum):
    never_married = "never_married"
    married = "married"
    divorced = "divorced"
    widowed = "widowed"
    separated = "separated"


class PopulationDataset(Base):
    """One row per imported dataset/version (see project docs, Module 3)."""

    __tablename__ = "population_datasets"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String, nullable=False)
    # Hierarchical NISR-style code (province / district / sector), not free text,
    # so it aligns with the source census geography.
    region_id: Mapped[str] = mapped_column(String, nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    source: Mapped[str] = mapped_column(String, nullable=False)
    granularity: Mapped[Granularity] = mapped_column(
        Enum(Granularity, name="population_granularity"), nullable=False
    )
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    status: Mapped[DatasetStatus] = mapped_column(
        Enum(DatasetStatus, name="population_dataset_status"),
        nullable=False,
        default=DatasetStatus.draft,
    )
    # Populated by the import job: while status=processing it holds running
    # progress (phase, rows_processed, total_rows); on completion, final counts
    # of rows imported / rejected and a sample of rejection reasons; on failure,
    # an `error` key. Null until an import job has started.
    import_report: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    created_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default="now()")


class PopulationMicrodata(Base):
    """Raw, row-per-person census records, close to the NISR source shape."""

    __tablename__ = "population_microdata"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    dataset_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("population_datasets.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    household_id: Mapped[str] = mapped_column(String, nullable=False)
    person_id: Mapped[int] = mapped_column(Integer, nullable=False)
    province_code: Mapped[int] = mapped_column(Integer, nullable=False)
    district_code: Mapped[int] = mapped_column(Integer, nullable=False)
    sector_code: Mapped[int] = mapped_column(Integer, nullable=False)
    area_type: Mapped[AreaType] = mapped_column(Enum(AreaType, name="population_area_type"), nullable=False)
    sex: Mapped[Sex] = mapped_column(Enum(Sex, name="population_sex"), nullable=False)
    age: Mapped[int] = mapped_column(Integer, nullable=False)
    relationship_to_head: Mapped[RelationshipToHead] = mapped_column(
        Enum(RelationshipToHead, name="population_relationship_to_head"), nullable=False
    )
    marital_status: Mapped[MaritalStatus | None] = mapped_column(
        Enum(MaritalStatus, name="population_marital_status"), nullable=True
    )


class PopulationRecord(Base):
    """Derived aggregation over `population_microdata` (or imported directly for
    aggregate-granularity datasets). Feeds the faster SEIR-level models.
    """

    __tablename__ = "population_records"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    dataset_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("population_datasets.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    sub_region_id: Mapped[str] = mapped_column(String, nullable=False)
    age_band: Mapped[str] = mapped_column(String, nullable=False)
    population_count: Mapped[int] = mapped_column(Integer, nullable=False)
    # Cannot be derived from microdata alone - needs sector land-area data from
    # Module 9 (geographic boundaries), which isn't built yet. Left null by the
    # aggregation job; known gap.
    density_per_km2: Mapped[float | None] = mapped_column(Float, nullable=True)
    urban_rural: Mapped[AreaType] = mapped_column(Enum(AreaType, name="population_area_type"), nullable=False)
