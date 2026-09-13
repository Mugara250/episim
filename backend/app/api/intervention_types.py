import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_session
from app.core.users import current_active_user
from app.models.intervention import InterventionType
from app.models.user import User
from app.schemas.intervention import (
    InterventionTypeCloneRequest,
    InterventionTypeCreate,
    InterventionTypePermissions,
    InterventionTypeRead,
    InterventionTypeUpdate,
)
from app.services.permissions import (
    can_clone_intervention_types,
    can_create_intervention_types,
    can_edit_builtin_intervention_types,
    can_edit_custom_intervention_type,
    can_edit_intervention_type,
)

router = APIRouter(prefix="/intervention-types", tags=["intervention-types"])


def _build_read(intervention_type: InterventionType, user: User) -> InterventionTypeRead:
    permissions = InterventionTypePermissions(
        can_edit=can_edit_intervention_type(user, intervention_type),
        can_clone=can_clone_intervention_types(user),
        is_owner=user.id == intervention_type.created_by,
    )
    return InterventionTypeRead(
        id=intervention_type.id,
        key=intervention_type.key,
        name=intervention_type.name,
        effect_mechanism=intervention_type.effect_mechanism,
        default_effect_size=intervention_type.default_effect_size,
        source_citation=intervention_type.source_citation,
        is_builtin=intervention_type.is_builtin,
        created_by=intervention_type.created_by,
        created_at=intervention_type.created_at,
        permissions=permissions,
    )


async def _get_or_404(db: AsyncSession, type_id: uuid.UUID) -> InterventionType:
    intervention_type = await db.get(InterventionType, type_id)
    if intervention_type is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Intervention type not found")
    return intervention_type


@router.get("", response_model=list[InterventionTypeRead])
async def list_intervention_types(
    db: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user),
):
    result = await db.execute(select(InterventionType).order_by(InterventionType.name))
    return [_build_read(intervention_type, user) for intervention_type in result.scalars().all()]


@router.get("/{type_id}", response_model=InterventionTypeRead)
async def get_intervention_type(
    type_id: uuid.UUID,
    db: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user),
):
    intervention_type = await _get_or_404(db, type_id)
    return _build_read(intervention_type, user)


@router.post("", response_model=InterventionTypeRead, status_code=status.HTTP_201_CREATED)
async def create_intervention_type(
    payload: InterventionTypeCreate,
    db: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user),
):
    if not can_create_intervention_types(user):
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="You cannot create intervention types.")

    intervention_type = InterventionType(**payload.model_dump(), is_builtin=False, created_by=user.id)
    db.add(intervention_type)
    await db.commit()
    await db.refresh(intervention_type)
    return _build_read(intervention_type, user)


@router.post("/{type_id}/clone", response_model=InterventionTypeRead, status_code=status.HTTP_201_CREATED)
async def clone_intervention_type(
    type_id: uuid.UUID,
    payload: InterventionTypeCloneRequest,
    db: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user),
):
    if not can_clone_intervention_types(user):
        raise HTTPException(
            status.HTTP_403_FORBIDDEN, detail="Policy makers have read-only access and cannot clone intervention types."
        )

    source = await _get_or_404(db, type_id)

    clone = InterventionType(
        key=f"{source.key}-{uuid.uuid4().hex[:8]}",
        name=payload.name or f"{source.name} (Custom)",
        effect_mechanism=source.effect_mechanism,
        default_effect_size=source.default_effect_size,
        source_citation=source.source_citation,
        is_builtin=False,
        created_by=user.id,
    )
    db.add(clone)
    await db.commit()
    await db.refresh(clone)
    return _build_read(clone, user)


@router.put("/{type_id}", response_model=InterventionTypeRead)
async def update_intervention_type(
    type_id: uuid.UUID,
    payload: InterventionTypeUpdate,
    db: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user),
):
    intervention_type = await _get_or_404(db, type_id)

    if intervention_type.is_builtin:
        if not can_edit_builtin_intervention_types(user):
            raise HTTPException(
                status.HTTP_403_FORBIDDEN,
                detail=(
                    "This is a built-in intervention type. Clone it to create an editable copy, or contact an "
                    "administrator or epidemiologist with admin privileges to modify the original."
                ),
            )
    elif not can_edit_custom_intervention_type(user, intervention_type):
        raise HTTPException(
            status.HTTP_403_FORBIDDEN,
            detail="You can only edit intervention types you created. Clone this type to create your own editable copy.",
        )

    for field, value in payload.model_dump().items():
        setattr(intervention_type, field, value)
    await db.commit()
    await db.refresh(intervention_type)
    return _build_read(intervention_type, user)
