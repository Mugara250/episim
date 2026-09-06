"""initial schema: institutions, users, auth support tables, disease presets

Revision ID: 0001_initial
Revises:
Create Date: 2026-09-06

"""
import uuid

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


institution_type = postgresql.ENUM(
    "district_health_office", "hospital", "research_institute", name="institution_type"
)
user_role = postgresql.ENUM(
    "analyst", "epidemiologist", "health_officer", "policy_maker", "admin", name="user_role"
)
user_status = postgresql.ENUM("active", "suspended", name="user_status")
mfa_method = postgresql.ENUM("totp", "sms", "email", name="mfa_method")
transmission_route = postgresql.ENUM("airborne", "waterborne", "contact", "vector", name="transmission_route")


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS postgis")

    # Enum types are created automatically the first time each is used as a
    # column type below (op.create_table fires a CREATE TYPE for a
    # postgresql.ENUM the first time it sees it) - no separate create() call.

    op.create_table(
        "institutions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("type", institution_type, nullable=False),
    )

    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column("hashed_password", sa.String(length=1024), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("is_superuser", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("is_verified", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("full_name", sa.String(), nullable=False),
        sa.Column("phone", sa.String(), nullable=True),
        sa.Column("institution_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("institutions.id"), nullable=True),
        sa.Column("role", user_role, nullable=False, server_default="analyst"),
        sa.Column("email_verified_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("status", user_status, nullable=False, server_default="active"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    op.create_table(
        "sessions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("token", sa.String(), nullable=False),
        sa.Column("ip_address", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        "mfa_settings",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("method", mfa_method, nullable=False),
        sa.Column("secret", sa.String(), nullable=False),
        sa.Column("enabled_at", sa.DateTime(timezone=True), nullable=True),
    )

    op.create_table(
        "login_attempts",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("email_attempted", sa.String(), nullable=False),
        sa.Column("success", sa.Boolean(), nullable=False),
        sa.Column("ip_address", sa.String(), nullable=True),
        sa.Column("attempted_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )

    op.create_table(
        "password_reset_tokens",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("token", sa.String(), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("used_at", sa.DateTime(timezone=True), nullable=True),
    )

    op.create_table(
        "disease_presets",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("r0", sa.Float(), nullable=False),
        sa.Column("incubation_period_days", sa.Float(), nullable=False),
        sa.Column("infectious_period_days", sa.Float(), nullable=False),
        sa.Column("mortality_rate", sa.Float(), nullable=False),
        sa.Column("asymptomatic_fraction", sa.Float(), nullable=False),
        sa.Column("transmission_route", transmission_route, nullable=False),
        sa.Column("is_builtin", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("source_citation", sa.String(), nullable=True),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )

    disease_presets_table = sa.table(
        "disease_presets",
        sa.column("id", postgresql.UUID(as_uuid=True)),
        sa.column("name", sa.String()),
        sa.column("r0", sa.Float()),
        sa.column("incubation_period_days", sa.Float()),
        sa.column("infectious_period_days", sa.Float()),
        sa.column("mortality_rate", sa.Float()),
        sa.column("asymptomatic_fraction", sa.Float()),
        sa.column("transmission_route", transmission_route),
        sa.column("is_builtin", sa.Boolean()),
        sa.column("source_citation", sa.String()),
    )
    op.bulk_insert(
        disease_presets_table,
        [
            {
                "id": uuid.uuid4(),
                "name": "COVID-19 (wild type)",
                "r0": 2.8,
                "incubation_period_days": 5.1,
                "infectious_period_days": 10.0,
                "mortality_rate": 0.01,
                "asymptomatic_fraction": 0.3,
                "transmission_route": "airborne",
                "is_builtin": True,
                "source_citation": "Li et al. 2020, NEJM; CDC COVID-19 Pandemic Planning Scenarios",
            },
            {
                "id": uuid.uuid4(),
                "name": "Cholera",
                "r0": 2.0,
                "incubation_period_days": 1.4,
                "infectious_period_days": 7.0,
                "mortality_rate": 0.02,
                "asymptomatic_fraction": 0.5,
                "transmission_route": "waterborne",
                "is_builtin": True,
                "source_citation": "WHO Cholera Fact Sheet; King et al. 2008, Nature",
            },
            {
                "id": uuid.uuid4(),
                "name": "Seasonal Influenza",
                "r0": 1.3,
                "incubation_period_days": 2.0,
                "infectious_period_days": 5.0,
                "mortality_rate": 0.001,
                "asymptomatic_fraction": 0.2,
                "transmission_route": "airborne",
                "is_builtin": True,
                "source_citation": "CDC Seasonal Flu Burden Estimates",
            },
        ],
    )


def downgrade() -> None:
    op.drop_table("disease_presets")
    op.drop_table("password_reset_tokens")
    op.drop_table("login_attempts")
    op.drop_table("mfa_settings")
    op.drop_table("sessions")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")
    op.drop_table("institutions")

    bind = op.get_bind()
    transmission_route.drop(bind, checkfirst=True)
    mfa_method.drop(bind, checkfirst=True)
    user_status.drop(bind, checkfirst=True)
    user_role.drop(bind, checkfirst=True)
    institution_type.drop(bind, checkfirst=True)
