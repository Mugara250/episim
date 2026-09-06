import enum
import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, Float, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class TransmissionRoute(str, enum.Enum):
    airborne = "airborne"
    waterborne = "waterborne"
    contact = "contact"
    vector = "vector"


class DiseasePreset(Base):
    __tablename__ = "disease_presets"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String, nullable=False)
    r0: Mapped[float] = mapped_column(Float, nullable=False)
    incubation_period_days: Mapped[float] = mapped_column(Float, nullable=False)
    infectious_period_days: Mapped[float] = mapped_column(Float, nullable=False)
    mortality_rate: Mapped[float] = mapped_column(Float, nullable=False)
    asymptomatic_fraction: Mapped[float] = mapped_column(Float, nullable=False)
    transmission_route: Mapped[TransmissionRoute] = mapped_column(
        Enum(TransmissionRoute, name="transmission_route"), nullable=False
    )
    is_builtin: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    source_citation: Mapped[str | None] = mapped_column(String, nullable=True)
    created_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    cloned_from_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("disease_presets.id"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default="now()")
