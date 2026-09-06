import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_session
from app.core.users import current_active_user
from app.models.session import Session as SessionModel
from app.models.user import User
from app.schemas.user import SessionRead, UserRead, UserUpdate

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserRead)
async def read_me(user: User = Depends(current_active_user)):
    return user


@router.put("/me", response_model=UserRead)
async def update_me(
    payload: UserUpdate,
    db: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user),
):
    update_data = payload.model_dump(exclude_unset=True, exclude={"password"})
    for field, value in update_data.items():
        setattr(user, field, value)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@router.get("/me/sessions", response_model=list[SessionRead])
async def list_my_sessions(
    db: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user),
):
    result = await db.execute(select(SessionModel).where(SessionModel.user_id == user.id))
    return result.scalars().all()


@router.delete("/me/sessions/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def revoke_my_session(
    session_id: uuid.UUID,
    db: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user),
):
    result = await db.execute(
        select(SessionModel).where(SessionModel.id == session_id, SessionModel.user_id == user.id)
    )
    session_row = result.scalars().first()
    if session_row is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Session not found")
    await db.execute(delete(SessionModel).where(SessionModel.id == session_id))
    await db.commit()
