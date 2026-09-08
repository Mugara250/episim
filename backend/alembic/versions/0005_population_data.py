"""population data management (Module 3): datasets, microdata, records

Revision ID: 0005_population_data
Revises: 0004_split_full_name
Create Date: 2026-09-08

Added assumption (not explicit in the project docs): population_microdata and
population_records reference population_datasets with ON DELETE CASCADE, so
deleting a dataset removes its dependent raw/aggregate rows rather than
orphaning them or blocking the delete.
"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0005_population_data"
down_revision = "0004_split_full_name"
branch_labels = None
depends_on = None


# create_type=False: these are created explicitly in upgrade() (one is shared by
# two tables, so letting op.create_table auto-create would double-issue CREATE TYPE).
granularity = postgresql.ENUM("microdata", "aggregate", name="population_granularity", create_type=False)
dataset_status = postgresql.ENUM("draft", "validated", "archived", name="population_dataset_status", create_type=False)
area_type = postgresql.ENUM("urban", "rural", name="population_area_type", create_type=False)
sex = postgresql.ENUM("male", "female", name="population_sex", create_type=False)
relationship_to_head = postgresql.ENUM(
    "head", "spouse", "child", "parent", "other_relative", "non_relative",
    name="population_relationship_to_head", create_type=False,
)
marital_status = postgresql.ENUM(
    "never_married", "married", "divorced", "widowed", "separated",
    name="population_marital_status", create_type=False,
)


def upgrade() -> None:
    bind = op.get_bind()
    for enum_type in (granularity, dataset_status, area_type, sex, relationship_to_head, marital_status):
        enum_type.create(bind, checkfirst=True)

    op.create_table(
        "population_datasets",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("region_id", sa.String(), nullable=False),
        sa.Column("year", sa.Integer(), nullable=False),
        sa.Column("source", sa.String(), nullable=False),
        sa.Column("granularity", granularity, nullable=False),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("status", dataset_status, nullable=False, server_default="draft"),
        sa.Column("import_report", postgresql.JSONB(), nullable=True),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_population_datasets_region_id", "population_datasets", ["region_id"])

    op.create_table(
        "population_microdata",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "dataset_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("population_datasets.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("household_id", sa.String(), nullable=False),
        sa.Column("person_id", sa.Integer(), nullable=False),
        sa.Column("province_code", sa.Integer(), nullable=False),
        sa.Column("district_code", sa.Integer(), nullable=False),
        sa.Column("sector_code", sa.Integer(), nullable=False),
        sa.Column("area_type", area_type, nullable=False),
        sa.Column("sex", sex, nullable=False),
        sa.Column("age", sa.Integer(), nullable=False),
        sa.Column("relationship_to_head", relationship_to_head, nullable=False),
        sa.Column("marital_status", marital_status, nullable=True),
    )
    op.create_index("ix_population_microdata_dataset_id", "population_microdata", ["dataset_id"])

    op.create_table(
        "population_records",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "dataset_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("population_datasets.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("sub_region_id", sa.String(), nullable=False),
        sa.Column("age_band", sa.String(), nullable=False),
        sa.Column("population_count", sa.Integer(), nullable=False),
        sa.Column("density_per_km2", sa.Float(), nullable=True),
        sa.Column("urban_rural", area_type, nullable=False),
    )
    op.create_index("ix_population_records_dataset_id", "population_records", ["dataset_id"])


def downgrade() -> None:
    op.drop_table("population_records")
    op.drop_table("population_microdata")
    op.drop_index("ix_population_datasets_region_id", table_name="population_datasets")
    op.drop_table("population_datasets")

    bind = op.get_bind()
    for enum_type in (marital_status, relationship_to_head, sex, area_type, dataset_status, granularity):
        enum_type.drop(bind, checkfirst=True)
