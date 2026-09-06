"""add has_admin_privileges to users, cloned_from_id to disease_presets

Revision ID: 0003_preset_cloning
Revises: 0002_seed_demo_data
Create Date: 2026-09-06

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0003_preset_cloning"
down_revision = "0002_seed_demo_data"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("has_admin_privileges", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.add_column(
        "disease_presets",
        sa.Column("cloned_from_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("disease_presets.id"), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("disease_presets", "cloned_from_id")
    op.drop_column("users", "has_admin_privileges")
