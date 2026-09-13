"""intervention types: reference library of intervention kinds

Revision ID: 0007_intervention_types
Revises: 0006_population_import_progress
Create Date: 2026-09-12

"""
import uuid

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0007_intervention_types"
down_revision = "0006_population_import_progress"
branch_labels = None
depends_on = None


effect_mechanism = postgresql.ENUM("compartment_shift", "rate_multiplier", name="effect_mechanism")

PLACEHOLDER_CITATION = "Placeholder — needs literature review before use"


def upgrade() -> None:
    op.create_table(
        "intervention_types",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("key", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("effect_mechanism", effect_mechanism, nullable=False),
        sa.Column("default_effect_size", sa.Float(), nullable=False),
        sa.Column("source_citation", sa.String(), nullable=True),
        sa.Column("is_builtin", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_intervention_types_key", "intervention_types", ["key"], unique=True)

    intervention_types_table = sa.table(
        "intervention_types",
        sa.column("id", postgresql.UUID(as_uuid=True)),
        sa.column("key", sa.String()),
        sa.column("name", sa.String()),
        sa.column("effect_mechanism", effect_mechanism),
        sa.column("default_effect_size", sa.Float()),
        sa.column("source_citation", sa.String()),
        sa.column("is_builtin", sa.Boolean()),
    )
    # Placeholder default_effect_size values only - real numbers require a
    # literature review pass by the team, not a guess baked into a migration.
    op.bulk_insert(
        intervention_types_table,
        [
            {
                "id": uuid.uuid4(),
                "key": "vaccination",
                "name": "Vaccination",
                "effect_mechanism": "compartment_shift",
                "default_effect_size": 0.5,
                "source_citation": PLACEHOLDER_CITATION,
                "is_builtin": True,
            },
            {
                "id": uuid.uuid4(),
                "key": "lockdown",
                "name": "Lockdown",
                "effect_mechanism": "rate_multiplier",
                "default_effect_size": 0.5,
                "source_citation": PLACEHOLDER_CITATION,
                "is_builtin": True,
            },
            {
                "id": uuid.uuid4(),
                "key": "masking",
                "name": "Masking",
                "effect_mechanism": "rate_multiplier",
                "default_effect_size": 0.5,
                "source_citation": PLACEHOLDER_CITATION,
                "is_builtin": True,
            },
            {
                "id": uuid.uuid4(),
                "key": "testing",
                "name": "Testing",
                "effect_mechanism": "rate_multiplier",
                "default_effect_size": 0.5,
                "source_citation": PLACEHOLDER_CITATION,
                "is_builtin": True,
            },
            {
                "id": uuid.uuid4(),
                "key": "contact_tracing",
                "name": "Contact Tracing",
                "effect_mechanism": "rate_multiplier",
                "default_effect_size": 0.5,
                "source_citation": PLACEHOLDER_CITATION,
                "is_builtin": True,
            },
        ],
    )


def downgrade() -> None:
    op.drop_index("ix_intervention_types_key", table_name="intervention_types")
    op.drop_table("intervention_types")
    bind = op.get_bind()
    effect_mechanism.drop(bind, checkfirst=True)
