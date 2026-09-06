import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_session
from app.core.users import current_active_user
from app.models.disease_preset import DiseasePreset
from app.models.user import User
from app.schemas.disease_preset import DiseasePresetCreate, DiseasePresetRead, DiseasePresetUpdate

router = APIRouter(prefix="/disease-presets", tags=["disease-presets"])


@router.get("", response_model=list[DiseasePresetRead])
async def list_disease_presets(db: AsyncSession = Depends(get_async_session)):
    result = await db.execute(select(DiseasePreset).order_by(DiseasePreset.name))
    return result.scalars().all()


@router.get("/{preset_id}", response_model=DiseasePresetRead)
async def get_disease_preset(preset_id: uuid.UUID, db: AsyncSession = Depends(get_async_session)):
    preset = await db.get(DiseasePreset, preset_id)
    if preset is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Disease preset not found")
    return preset


@router.post("", response_model=DiseasePresetRead, status_code=status.HTTP_201_CREATED)
async def create_disease_preset(
    payload: DiseasePresetCreate,
    db: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user),
):
    preset = DiseasePreset(**payload.model_dump(), is_builtin=False, created_by=user.id)
    db.add(preset)
    await db.commit()
    await db.refresh(preset)
    return preset


@router.put("/{preset_id}", response_model=DiseasePresetRead)
async def update_disease_preset(
    preset_id: uuid.UUID,
    payload: DiseasePresetUpdate,
    db: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user),
):
    preset = await db.get(DiseasePreset, preset_id)
    if preset is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Disease preset not found")
    if preset.is_builtin:
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="Built-in presets cannot be edited")

    for field, value in payload.model_dump().items():
        setattr(preset, field, value)
    await db.commit()
    await db.refresh(preset)
    return preset
