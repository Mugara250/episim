from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_session
from app.core.users import require_role
from app.models.login_attempt import LoginAttempt
from app.models.user import UserRole
from app.schemas.user import LoginAttemptRead

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/login-attempts", response_model=list[LoginAttemptRead], dependencies=[Depends(require_role(UserRole.admin))])
async def list_login_attempts(db: AsyncSession = Depends(get_async_session)):
    result = await db.execute(select(LoginAttempt).order_by(LoginAttempt.attempted_at.desc()).limit(200))
    return result.scalars().all()
