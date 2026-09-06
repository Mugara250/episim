import enum
import uuid
from datetime import datetime

from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTableUUID
from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class UserRole(str, enum.Enum):
    analyst = "analyst"
    epidemiologist = "epidemiologist"
    health_officer = "health_officer"
    policy_maker = "policy_maker"
    admin = "admin"


class UserStatus(str, enum.Enum):
    active = "active"
    suspended = "suspended"


class User(SQLAlchemyBaseUserTableUUID, Base):
    """Extends fastapi-users' base user table.

    fastapi-users mandates the `hashed_password`, `is_active`, and
    `is_verified` columns/names (used internally by its auth backends) -
    those serve as the `password_hash` / verification-state columns from the
    spec. `email_verified_at` is kept alongside `is_verified` as an explicit
    timestamp for auditing.
    """

    __tablename__ = "users"

    first_name: Mapped[str] = mapped_column(String, nullable=False)
    last_name: Mapped[str] = mapped_column(String, nullable=False)
    phone: Mapped[str | None] = mapped_column(String, nullable=True)
    institution_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("institutions.id"), nullable=True
    )
    role: Mapped[UserRole] = mapped_column(Enum(UserRole, name="user_role"), nullable=False, default=UserRole.analyst)
    # Grants an epidemiologist the same preset-editing rights as an admin
    # (see app.services.permissions). Not settable via registration/self-
    # update - only ever flipped by an operator/future admin tooling.
    has_admin_privileges: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    email_verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[UserStatus] = mapped_column(
        Enum(UserStatus, name="user_status"), nullable=False, default=UserStatus.active
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default="now()")
