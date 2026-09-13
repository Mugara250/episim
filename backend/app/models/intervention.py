import enum
import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, Float, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class EffectMechanism(str, enum.Enum):
    compartment_shift = "compartment_shift"
    rate_multiplier = "rate_multiplier"


class InterventionType(Base):
    __tablename__ = "intervention_types"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    key: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    effect_mechanism: Mapped[EffectMechanism] = mapped_column(
        Enum(EffectMechanism, name="effect_mechanism"), nullable=False
    )
    default_effect_size: Mapped[float] = mapped_column(Float, nullable=False)
    source_citation: Mapped[str | None] = mapped_column(String, nullable=True)
    is_builtin: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default="now()")


class InterventionPackage(Base):
    __tablename__ = "intervention_packages"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str | None] = mapped_column(String, nullable=True)
    created_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default="now()")


class InterventionItem(Base):
    __tablename__ = "intervention_items"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    package_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("intervention_packages.id", ondelete="CASCADE"), nullable=False
    )
    type_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("intervention_types.id", ondelete="RESTRICT"), nullable=False
    )
    start_day: Mapped[int] = mapped_column(Integer, nullable=False)
    end_day: Mapped[int | None] = mapped_column(Integer, nullable=True)
    coverage: Mapped[float] = mapped_column(Float, nullable=False)
    effectiveness_override: Mapped[float | None] = mapped_column(Float, nullable=True)
