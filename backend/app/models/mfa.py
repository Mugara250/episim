import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class MFAMethod(str, enum.Enum):
    totp = "totp"
    sms = "sms"
    email = "email"


class MFASetting(Base):
    __tablename__ = "mfa_settings"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    method: Mapped[MFAMethod] = mapped_column(Enum(MFAMethod, name="mfa_method"), nullable=False)
    secret: Mapped[str] = mapped_column(String, nullable=False)  # encrypted, see app.core.security
    enabled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
