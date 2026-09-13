import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.intervention import EffectMechanism


class InterventionTypeBase(BaseModel):
    key: str
    name: str
    effect_mechanism: EffectMechanism
    default_effect_size: float = Field(ge=0, le=1)
    source_citation: str | None = None


class InterventionTypeCreate(InterventionTypeBase):
    pass


class InterventionTypeUpdate(InterventionTypeBase):
    pass


class InterventionTypeCloneRequest(BaseModel):
    name: str | None = None


class InterventionTypePermissions(BaseModel):
    can_edit: bool
    can_clone: bool
    is_owner: bool


class InterventionTypeRead(InterventionTypeBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    is_builtin: bool
    created_by: uuid.UUID | None
    created_at: datetime
    permissions: InterventionTypePermissions


class InterventionItemBase(BaseModel):
    type_id: uuid.UUID
    start_day: int = Field(ge=0)
    end_day: int | None = Field(default=None, ge=0)
    coverage: float = Field(ge=0, le=1)
    effectiveness_override: float | None = Field(default=None, ge=0, le=1)


class InterventionItemCreate(InterventionItemBase):
    pass


class InterventionItemRead(InterventionItemBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    package_id: uuid.UUID
    type_name: str
    effect_mechanism: EffectMechanism


class InterventionPackagePermissions(BaseModel):
    can_edit: bool
    can_delete: bool
    is_owner: bool


class InterventionPackageCreate(BaseModel):
    name: str
    description: str | None = None


class InterventionPackageRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    description: str | None
    created_by: uuid.UUID
    created_at: datetime
    item_count: int
    permissions: InterventionPackagePermissions


class InterventionPackageDetail(InterventionPackageRead):
    items: list[InterventionItemRead]


class InterventionPackageList(BaseModel):
    items: list[InterventionPackageRead]
    total: int
    page: int
    page_size: int
