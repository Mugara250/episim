"""split users.full_name into first_name / last_name

Revision ID: 0004_split_full_name
Revises: 0003_preset_cloning
Create Date: 2026-09-06

"""
import sqlalchemy as sa
from alembic import op

revision = "0004_split_full_name"
down_revision = "0003_preset_cloning"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("users", sa.Column("first_name", sa.String(), nullable=True))
    op.add_column("users", sa.Column("last_name", sa.String(), nullable=True))

    # Backfill from the existing full_name for any already-seeded/registered
    # users: everything before the first space is the first name, the rest
    # (or an empty string if there's no space) is the last name.
    op.execute(
        """
        UPDATE users
        SET first_name = split_part(full_name, ' ', 1),
            last_name = CASE
                WHEN position(' ' in full_name) > 0
                THEN substring(full_name from position(' ' in full_name) + 1)
                ELSE ''
            END
        """
    )

    op.alter_column("users", "first_name", nullable=False)
    op.alter_column("users", "last_name", nullable=False)
    op.drop_column("users", "full_name")


def downgrade() -> None:
    op.add_column("users", sa.Column("full_name", sa.String(), nullable=True))
    op.execute("UPDATE users SET full_name = trim(first_name || ' ' || last_name)")
    op.alter_column("users", "full_name", nullable=False)
    op.drop_column("users", "last_name")
    op.drop_column("users", "first_name")
