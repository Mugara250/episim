import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_session
from app.core.users import current_active_user
from app.models.intervention import InterventionItem, InterventionPackage, InterventionType
from app.models.user import User
from app.schemas.intervention import (
    InterventionItemCreate,
    InterventionItemRead,
    InterventionPackageCreate,
    InterventionPackageDetail,
    InterventionPackageList,
    InterventionPackagePermissions,
    InterventionPackageRead,
)
from app.services.permissions import can_delete_package, can_edit_package

router = APIRouter(prefix="/intervention-packages", tags=["intervention-packages"])


async def _get_package_or_404(db: AsyncSession, package_id: uuid.UUID) -> InterventionPackage:
    package = await db.get(InterventionPackage, package_id)
    if package is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Intervention package not found")
    return package


def _build_package_read(package: InterventionPackage, item_count: int, user: User) -> InterventionPackageRead:
    permissions = InterventionPackagePermissions(
        can_edit=can_edit_package(user, package),
        can_delete=can_delete_package(user, package),
        is_owner=user.id == package.created_by,
    )
    return InterventionPackageRead(
        id=package.id,
        name=package.name,
        description=package.description,
        created_by=package.created_by,
        created_at=package.created_at,
        item_count=item_count,
        permissions=permissions,
    )


def _build_item_read(item: InterventionItem, intervention_type: InterventionType) -> InterventionItemRead:
    return InterventionItemRead(
        id=item.id,
        package_id=item.package_id,
        type_id=item.type_id,
        start_day=item.start_day,
        end_day=item.end_day,
        coverage=item.coverage,
        effectiveness_override=item.effectiveness_override,
        type_name=intervention_type.name,
        effect_mechanism=intervention_type.effect_mechanism,
    )


@router.get("", response_model=InterventionPackageList)
async def list_intervention_packages(
    db: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user),
    created_by: uuid.UUID | None = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=25, ge=1, le=200),
):
    filters = []
    if created_by is not None:
        filters.append(InterventionPackage.created_by == created_by)

    total = await db.scalar(select(func.count()).select_from(InterventionPackage).where(*filters))
    result = await db.execute(
        select(InterventionPackage)
        .where(*filters)
        .order_by(InterventionPackage.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    packages = list(result.scalars().all())

    item_counts: dict[uuid.UUID, int] = {}
    if packages:
        count_rows = await db.execute(
            select(InterventionItem.package_id, func.count())
            .where(InterventionItem.package_id.in_([p.id for p in packages]))
            .group_by(InterventionItem.package_id)
        )
        item_counts = dict(count_rows.all())

    return InterventionPackageList(
        items=[
            _build_package_read(package, item_counts.get(package.id, 0), user)
            for package in packages
        ],
        total=total or 0,
        page=page,
        page_size=page_size,
    )


@router.get("/{package_id}", response_model=InterventionPackageDetail)
async def get_intervention_package(
    package_id: uuid.UUID,
    db: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user),
):
    package = await _get_package_or_404(db, package_id)

    result = await db.execute(
        select(InterventionItem, InterventionType)
        .join(InterventionType, InterventionItem.type_id == InterventionType.id)
        .where(InterventionItem.package_id == package_id)
        .order_by(InterventionItem.start_day)
    )
    rows = result.all()

    base = _build_package_read(package, len(rows), user)
    return InterventionPackageDetail(
        **base.model_dump(),
        items=[_build_item_read(item, intervention_type) for item, intervention_type in rows],
    )


@router.post("", response_model=InterventionPackageRead, status_code=status.HTTP_201_CREATED)
async def create_intervention_package(
    payload: InterventionPackageCreate,
    db: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user),
):
    package = InterventionPackage(**payload.model_dump(), created_by=user.id)
    db.add(package)
    await db.commit()
    await db.refresh(package)
    return _build_package_read(package, 0, user)


@router.post("/{package_id}/items", response_model=InterventionItemRead, status_code=status.HTTP_201_CREATED)
async def add_intervention_item(
    package_id: uuid.UUID,
    payload: InterventionItemCreate,
    db: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user),
):
    package = await _get_package_or_404(db, package_id)
    if not can_edit_package(user, package):
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="You can only add items to packages you created.")

    if payload.end_day is not None and payload.end_day < payload.start_day:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, detail="end_day must be >= start_day.")

    intervention_type = await db.get(InterventionType, payload.type_id)
    if intervention_type is None:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, detail="type_id does not reference an existing intervention type.")

    item = InterventionItem(**payload.model_dump(), package_id=package_id)
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return _build_item_read(item, intervention_type)


@router.delete("/{package_id}/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_intervention_item(
    package_id: uuid.UUID,
    item_id: uuid.UUID,
    db: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user),
):
    package = await _get_package_or_404(db, package_id)
    if not can_edit_package(user, package):
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="You can only remove items from packages you created.")

    item = await db.get(InterventionItem, item_id)
    if item is None or item.package_id != package_id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Intervention item not found")

    await db.delete(item)
    await db.commit()


@router.delete("/{package_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_intervention_package(
    package_id: uuid.UUID,
    db: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user),
):
    package = await _get_package_or_404(db, package_id)
    if not can_delete_package(user, package):
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="You can only delete packages you created.")

    await db.delete(package)
    await db.commit()
