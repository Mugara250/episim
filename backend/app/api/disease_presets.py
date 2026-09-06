import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_session
from app.core.users import current_active_user
from app.models.disease_preset import DiseasePreset
from app.models.user import User
from app.schemas.disease_preset import (
    DiseasePresetCloneRequest,
    DiseasePresetCreate,
    DiseasePresetPermissions,
    DiseasePresetRead,
    DiseasePresetUpdate,
)
from app.services.permissions import (
    can_clone_presets,
    can_create_presets,
    can_delete_preset,
    can_edit_builtin_presets,
    can_edit_custom_preset,
    can_edit_preset,
)

router = APIRouter(prefix="/disease-presets", tags=["disease-presets"])


def _build_read(preset: DiseasePreset, user: User) -> DiseasePresetRead:
    permissions = DiseasePresetPermissions(
        can_edit=can_edit_preset(user, preset),
        can_clone=can_clone_presets(user),
        can_delete=can_delete_preset(user, preset),
        is_owner=user.id == preset.created_by,
    )
    return DiseasePresetRead(
        id=preset.id,
        name=preset.name,
        r0=preset.r0,
        incubation_period_days=preset.incubation_period_days,
        infectious_period_days=preset.infectious_period_days,
        mortality_rate=preset.mortality_rate,
        asymptomatic_fraction=preset.asymptomatic_fraction,
        transmission_route=preset.transmission_route,
        source_citation=preset.source_citation,
        is_builtin=preset.is_builtin,
        created_by=preset.created_by,
        cloned_from_id=preset.cloned_from_id,
        created_at=preset.created_at,
        permissions=permissions,
    )


async def _get_preset_or_404(db: AsyncSession, preset_id: uuid.UUID) -> DiseasePreset:
    preset = await db.get(DiseasePreset, preset_id)
    if preset is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Disease preset not found")
    return preset


@router.get("", response_model=list[DiseasePresetRead])
async def list_disease_presets(
    db: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user),
):
    result = await db.execute(select(DiseasePreset).order_by(DiseasePreset.name))
    return [_build_read(preset, user) for preset in result.scalars().all()]


@router.get("/{preset_id}", response_model=DiseasePresetRead)
async def get_disease_preset(
    preset_id: uuid.UUID,
    db: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user),
):
    preset = await _get_preset_or_404(db, preset_id)
    return _build_read(preset, user)


@router.post("", response_model=DiseasePresetRead, status_code=status.HTTP_201_CREATED)
async def create_disease_preset(
    payload: DiseasePresetCreate,
    db: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user),
):
    if not can_create_presets(user):
        raise HTTPException(
            status.HTTP_403_FORBIDDEN,
            detail=(
                "Only administrators and epidemiologists with admin privileges can create new disease "
                "presets. Standard epidemiologists can clone existing presets and edit their copies."
            ),
        )

    preset = DiseasePreset(**payload.model_dump(), is_builtin=False, created_by=user.id)
    db.add(preset)
    await db.commit()
    await db.refresh(preset)
    return _build_read(preset, user)


@router.post("/{preset_id}/clone", response_model=DiseasePresetRead, status_code=status.HTTP_201_CREATED)
async def clone_disease_preset(
    preset_id: uuid.UUID,
    payload: DiseasePresetCloneRequest,
    db: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user),
):
    if not can_clone_presets(user):
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="Policy makers have read-only access and cannot clone presets.")

    source = await _get_preset_or_404(db, preset_id)

    clone = DiseasePreset(
        name=payload.name or f"{source.name} (Custom)",
        r0=source.r0,
        incubation_period_days=source.incubation_period_days,
        infectious_period_days=source.infectious_period_days,
        mortality_rate=source.mortality_rate,
        asymptomatic_fraction=source.asymptomatic_fraction,
        transmission_route=source.transmission_route,
        source_citation=source.source_citation,
        is_builtin=False,
        created_by=user.id,
        cloned_from_id=source.id,
    )
    db.add(clone)
    await db.commit()
    await db.refresh(clone)
    return _build_read(clone, user)


@router.put("/{preset_id}", response_model=DiseasePresetRead)
async def update_disease_preset(
    preset_id: uuid.UUID,
    payload: DiseasePresetUpdate,
    db: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user),
):
    preset = await _get_preset_or_404(db, preset_id)

    if preset.is_builtin:
        if not can_edit_builtin_presets(user):
            raise HTTPException(
                status.HTTP_403_FORBIDDEN,
                detail=(
                    "This is a built-in preset. Clone it to create an editable copy, or contact an "
                    "administrator or epidemiologist with admin privileges to modify the original."
                ),
            )
    elif not can_edit_custom_preset(user, preset):
        raise HTTPException(
            status.HTTP_403_FORBIDDEN,
            detail="You can only edit presets you created. Clone this preset to create your own editable copy.",
        )

    for field, value in payload.model_dump().items():
        setattr(preset, field, value)
    await db.commit()
    await db.refresh(preset)
    return _build_read(preset, user)


@router.delete("/{preset_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_disease_preset(
    preset_id: uuid.UUID,
    db: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user),
):
    preset = await _get_preset_or_404(db, preset_id)

    if preset.is_builtin:
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="Built-in presets cannot be deleted.")
    if not can_delete_preset(user, preset):
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="You can only delete presets you created.")

    await db.execute(delete(DiseasePreset).where(DiseasePreset.id == preset_id))
    await db.commit()
