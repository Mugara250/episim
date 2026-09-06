from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_session
from app.models.institution import Institution
from app.schemas.institution import InstitutionRead

router = APIRouter(prefix="/institutions", tags=["institutions"])


@router.get("", response_model=list[InstitutionRead])
async def list_institutions(db: AsyncSession = Depends(get_async_session)):
    result = await db.execute(select(Institution).order_by(Institution.name))
    return result.scalars().all()
