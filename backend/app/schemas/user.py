import uuid
from datetime import datetime

from fastapi_users import schemas
from pydantic import BaseModel, ConfigDict

from app.models.user import UserRole, UserStatus


class UserRead(schemas.BaseUser[uuid.UUID]):
    first_name: str
    last_name: str
    phone: str | None
    institution_id: uuid.UUID | None
    role: UserRole
    has_admin_privileges: bool
    status: UserStatus
    email_verified_at: datetime | None
    created_at: datetime


class UserCreate(schemas.BaseUserCreate):
    first_name: str
    last_name: str
    phone: str | None = None
    institution_id: uuid.UUID | None = None
    role: UserRole = UserRole.analyst


class UserUpdate(schemas.BaseUserUpdate):
    first_name: str | None = None
    last_name: str | None = None
    phone: str | None = None
    institution_id: uuid.UUID | None = None


class UserPublic(BaseModel):
    """Minimal, non-sensitive profile shown to other users (e.g. "created by"
    attribution on shared resources) - deliberately excludes email, phone,
    and verification/status fields that UserRead exposes to the user
    themselves.
    """

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    first_name: str
    last_name: str
    role: UserRole


class SessionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    ip_address: str | None
    created_at: datetime
    expires_at: datetime


class LoginAttemptRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID | None
    email_attempted: str
    success: bool
    ip_address: str | None
    attempted_at: datetime
