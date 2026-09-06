import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.disease_preset import TransmissionRoute


class DiseasePresetBase(BaseModel):
    name: str
    r0: float = Field(gt=0)
    incubation_period_days: float = Field(gt=0)
    infectious_period_days: float = Field(gt=0)
    mortality_rate: float = Field(ge=0, le=1)
    asymptomatic_fraction: float = Field(ge=0, le=1)
    transmission_route: TransmissionRoute
    source_citation: str | None = None


class DiseasePresetCreate(DiseasePresetBase):
    pass


class DiseasePresetUpdate(DiseasePresetBase):
    pass


class DiseasePresetCloneRequest(BaseModel):
    name: str | None = None


class DiseasePresetPermissions(BaseModel):
    can_edit: bool
    can_clone: bool
    can_delete: bool
    is_owner: bool


class DiseasePresetRead(DiseasePresetBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    is_builtin: bool
    created_by: uuid.UUID | None
    cloned_from_id: uuid.UUID | None
    created_at: datetime
    permissions: DiseasePresetPermissions
