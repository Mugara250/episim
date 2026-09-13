"""intervention packages and items: reusable, time-boxed intervention bundles

Revision ID: 0008_intervention_packages
Revises: 0007_intervention_types
Create Date: 2026-09-12

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0008_intervention_packages"
down_revision = "0007_intervention_types"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "intervention_packages",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("description", sa.String(), nullable=True),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )

    op.create_table(
        "intervention_items",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "package_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("intervention_packages.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "type_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("intervention_types.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("start_day", sa.Integer(), nullable=False),
        sa.Column("end_day", sa.Integer(), nullable=True),
        sa.Column("coverage", sa.Float(), nullable=False),
        sa.Column("effectiveness_override", sa.Float(), nullable=True),
    )
    op.create_index("ix_intervention_items_package_id", "intervention_items", ["package_id"])


def downgrade() -> None:
    op.drop_index("ix_intervention_items_package_id", table_name="intervention_items")
    op.drop_table("intervention_items")
    op.drop_table("intervention_packages")
