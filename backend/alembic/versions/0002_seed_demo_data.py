"""seed demo institutions and a demo login account

Revision ID: 0002_seed_demo_data
Revises: 0001_initial
Create Date: 2026-09-06

"""
import uuid
from datetime import datetime, timezone

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0002_seed_demo_data"
down_revision = "0001_initial"
branch_labels = None
depends_on = None

institution_type = postgresql.ENUM(
    "district_health_office", "hospital", "research_institute", name="institution_type", create_type=False
)
user_role = postgresql.ENUM(
    "analyst", "epidemiologist", "health_officer", "policy_maker", "admin", name="user_role", create_type=False
)
user_status = postgresql.ENUM("active", "suspended", name="user_status", create_type=False)

# Generic institution archetypes, not real organizations - see the note in
# the frontend's TrustBar component for why real institution names/logos
# are avoided in this unaffiliated academic prototype.
DEMO_INSTITUTIONS = [
    {"id": uuid.uuid4(), "name": "Ministry of Health", "type": "district_health_office"},
    {"id": uuid.uuid4(), "name": "City General Hospital", "type": "hospital"},
    {"id": uuid.uuid4(), "name": "National Public Health Institute", "type": "research_institute"},
]

DEMO_USER_ID = uuid.uuid4()
# Password: Demo1234! - hashed with fastapi-users' PasswordHelper (argon2).
# Shown on the frontend's login page "Show demo credentials" toggle.
DEMO_USER_PASSWORD_HASH = "$argon2id$v=19$m=65536,t=3,p=4$9vV91X0uEZ2iyKD3VfZLvQ$Vfhgygn/E8uY+lr8WnDEkp+IP9IFBmnniYXHn/btMNo"


def upgrade() -> None:
    institutions_table = sa.table(
        "institutions",
        sa.column("id", postgresql.UUID(as_uuid=True)),
        sa.column("name", sa.String()),
        sa.column("type", institution_type),
    )
    op.bulk_insert(institutions_table, DEMO_INSTITUTIONS)

    users_table = sa.table(
        "users",
        sa.column("id", postgresql.UUID(as_uuid=True)),
        sa.column("email", sa.String()),
        sa.column("hashed_password", sa.String()),
        sa.column("is_active", sa.Boolean()),
        sa.column("is_superuser", sa.Boolean()),
        sa.column("is_verified", sa.Boolean()),
        sa.column("full_name", sa.String()),
        sa.column("institution_id", postgresql.UUID(as_uuid=True)),
        sa.column("role", user_role),
        sa.column("email_verified_at", sa.DateTime(timezone=True)),
        sa.column("status", user_status),
    )
    op.bulk_insert(
        users_table,
        [
            {
                "id": DEMO_USER_ID,
                "email": "demo@episim.dev",
                "hashed_password": DEMO_USER_PASSWORD_HASH,
                "is_active": True,
                "is_superuser": False,
                "is_verified": True,
                "full_name": "Demo Analyst",
                "institution_id": DEMO_INSTITUTIONS[0]["id"],
                "role": "analyst",
                "email_verified_at": datetime.now(timezone.utc),
                "status": "active",
            }
        ],
    )


def downgrade() -> None:
    op.execute(f"DELETE FROM users WHERE id = '{DEMO_USER_ID}'")
    for inst in DEMO_INSTITUTIONS:
        op.execute(f"DELETE FROM institutions WHERE id = '{inst['id']}'")
