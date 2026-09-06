import asyncio
import uuid
from collections.abc import AsyncGenerator
from datetime import datetime, timezone

from fastapi import Depends, HTTPException, Request, status
from fastapi_users import BaseUserManager, FastAPIUsers, UUIDIDMixin
from fastapi_users.authentication import AuthenticationBackend, BearerTransport, JWTStrategy
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.db import get_async_session
from app.models.user import User, UserRole
from app.services.email import send_email


async def get_user_db(session: AsyncSession = Depends(get_async_session)) -> AsyncGenerator[SQLAlchemyUserDatabase, None]:
    yield SQLAlchemyUserDatabase(session, User)


class UserManager(UUIDIDMixin, BaseUserManager[User, uuid.UUID]):
    reset_password_token_secret = settings.jwt_secret
    verification_token_secret = settings.jwt_secret

    async def on_after_register(self, user: User, request: Request | None = None) -> None:
        await self.request_verify(user, request)

    async def on_after_request_verify(self, user: User, token: str, request: Request | None = None) -> None:
        verify_url = f"{settings.frontend_url}/verify-email?token={token}"
        # send_email does blocking socket I/O (stdlib smtplib) - run it off
        # the event loop so it can't stall other requests sharing this
        # worker while a DB transaction from this same request is open.
        await asyncio.to_thread(send_email, user.email, "Verify your EpiSim account", f"Click to verify your email: {verify_url}")

    async def on_after_verify(self, user: User, request: Request | None = None) -> None:
        # Reuse the same session the SQLAlchemyUserDatabase is bound to -
        # `user` is already attached there, and attaching it to a second
        # session raises InvalidRequestError.
        user.email_verified_at = datetime.now(timezone.utc)
        self.user_db.session.add(user)
        await self.user_db.session.commit()

    async def on_after_forgot_password(self, user: User, token: str, request: Request | None = None) -> None:
        reset_url = f"{settings.frontend_url}/reset-password?token={token}"
        await asyncio.to_thread(send_email, user.email, "Reset your EpiSim password", f"Click to reset your password: {reset_url}")


async def get_user_manager(user_db: SQLAlchemyUserDatabase = Depends(get_user_db)) -> AsyncGenerator[UserManager, None]:
    yield UserManager(user_db)


bearer_transport = BearerTransport(tokenUrl="auth/login")


def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=settings.jwt_secret, lifetime_seconds=settings.jwt_lifetime_seconds)


auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)

fastapi_users = FastAPIUsers[User, uuid.UUID](get_user_manager, [auth_backend])

current_active_user = fastapi_users.current_user(active=True)
current_verified_user = fastapi_users.current_user(active=True, verified=True)


def require_role(*roles: UserRole):
    async def _check(user: User = Depends(current_active_user)) -> User:
        if user.role not in roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient role")
        return user

    return _check
