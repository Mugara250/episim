"""population import progress: processing / failed dataset statuses

Revision ID: 0006_population_import_progress
Revises: 0005_population_data
Create Date: 2026-09-10

Adds two values to the population_dataset_status enum so the import job can
signal that it is actively parsing a file (`processing`) or that it raised
(`failed`), rather than folding both cases back into `draft`. Running progress
(phase / rows_processed / total_rows) rides inside the existing
population_datasets.import_report JSONB column, so no schema change there.

Postgres will not add an enum value inside a transaction, so upgrade() commits
Alembic's migration transaction first and then issues the ALTER TYPE statements
(each its own implicit transaction). There is no clean downgrade for
ALTER TYPE ... ADD VALUE; downgrade() is a no-op (any rows left at the new
statuses would need manual remediation before the enum could be rebuilt).
"""
from alembic import op

revision = "0006_population_import_progress"
down_revision = "0005_population_data"
branch_labels = None
depends_on = None

_NEW_VALUES = ("processing", "failed")


def upgrade() -> None:
    # End the transaction Alembic opened; ALTER TYPE ... ADD VALUE cannot run
    # inside one. Subsequent statements each auto-commit.
    op.execute("COMMIT")
    for value in _NEW_VALUES:
        op.execute(f"ALTER TYPE population_dataset_status ADD VALUE IF NOT EXISTS '{value}'")


def downgrade() -> None:
    # ALTER TYPE ... ADD VALUE is not reversible; leaving the enum values in
    # place is harmless.
    pass
