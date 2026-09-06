from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi_users.exceptions import (
    InvalidPasswordException,
    InvalidResetPasswordToken,
    InvalidVerifyToken,
    UserAlreadyExists,
    UserAlreadyVerified,
    UserInactive,
    UserNotExists,
)
from pydantic import BaseModel, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.db import get_async_session
from app.core.security import decrypt_secret, encrypt_secret, generate_totp_secret, get_totp_uri, hash_token, verify_totp
from app.core.users import current_active_user, get_jwt_strategy, get_user_manager
from app.models.login_attempt import LoginAttempt
from app.models.mfa import MFAMethod, MFASetting
from app.models.session import Session as SessionModel
from app.models.user import User
from app.schemas.auth import ForgotPasswordRequest, MFASetupResponse, MFAVerifyRequest, ResetPasswordRequest, VerifyEmailRequest
from app.schemas.user import UserCreate, UserRead

router = APIRouter(prefix="/auth", tags=["auth"])


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class _Credentials:
    def __init__(self, username: str, password: str) -> None:
        self.username = username
        self.password = password


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def register(request: Request, user_create: UserCreate, user_manager=Depends(get_user_manager)):
    try:
        user = await user_manager.create(user_create, safe=True, request=request)
    except UserAlreadyExists:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="REGISTER_USER_ALREADY_EXISTS")
    except InvalidPasswordException as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail={"code": "REGISTER_INVALID_PASSWORD", "reason": exc.reason})
    return user


@router.post("/verify-email", response_model=UserRead)
async def verify_email(payload: VerifyEmailRequest, request: Request, user_manager=Depends(get_user_manager)):
    try:
        user = await user_manager.verify(payload.token, request=request)
    except (InvalidVerifyToken, UserNotExists):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="VERIFY_USER_BAD_TOKEN")
    except UserAlreadyVerified:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="VERIFY_USER_ALREADY_VERIFIED")
    return user


@router.post("/login")
async def login(
    request: Request,
    credentials: LoginRequest,
    db: AsyncSession = Depends(get_async_session),
    user_manager=Depends(get_user_manager),
    strategy=Depends(get_jwt_strategy),
):
    ip_address = request.client.host if request.client else None
    user = await user_manager.authenticate(_Credentials(credentials.email, credentials.password))

    success = user is not None and user.is_active
    db.add(
        LoginAttempt(
            user_id=user.id if user else None,
            email_attempted=credentials.email,
            success=bool(success),
            ip_address=ip_address,
        )
    )
    await db.commit()

    if user is None or not user.is_active:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="LOGIN_BAD_CREDENTIALS")

    token = await strategy.write_token(user)
    db.add(
        SessionModel(
            user_id=user.id,
            token=hash_token(token),
            ip_address=ip_address,
            expires_at=datetime.now(timezone.utc) + timedelta(seconds=settings.jwt_lifetime_seconds),
        )
    )
    await db.commit()

    return {"access_token": token, "token_type": "bearer", "role": user.role}


@router.post("/logout")
async def logout(
    request: Request,
    db: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user),
):
    """Removes the tracked session row for this token.

    The JWT strategy is stateless: the token itself stays cryptographically
    valid until it expires. A production deployment that needs hard
    revocation would check issued tokens against a blacklist/allowlist on
    every request; out of scope for this prototype slice.
    """
    auth_header = request.headers.get("authorization", "")
    if auth_header.lower().startswith("bearer "):
        token = auth_header[7:]
        from sqlalchemy import delete

        await db.execute(delete(SessionModel).where(SessionModel.token == hash_token(token)))
        await db.commit()
    return {"detail": "logged out"}


@router.post("/mfa/setup", response_model=MFASetupResponse)
async def mfa_setup(db: AsyncSession = Depends(get_async_session), user: User = Depends(current_active_user)):
    secret = generate_totp_secret()
    db.add(MFASetting(user_id=user.id, method=MFAMethod.totp, secret=encrypt_secret(secret), enabled_at=None))
    await db.commit()
    return MFASetupResponse(secret=secret, otpauth_uri=get_totp_uri(secret, user.email))


@router.post("/mfa/verify")
async def mfa_verify(
    payload: MFAVerifyRequest,
    db: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user),
):
    from sqlalchemy import select

    result = await db.execute(
        select(MFASetting)
        .where(MFASetting.user_id == user.id, MFASetting.enabled_at.is_(None))
        .order_by(MFASetting.id.desc())
    )
    setting = result.scalars().first()
    if setting is None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="No pending MFA setup for this user")

    secret = decrypt_secret(setting.secret)
    if not verify_totp(secret, payload.code):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Invalid MFA code")

    setting.enabled_at = datetime.now(timezone.utc)
    await db.commit()
    return {"detail": "MFA enabled"}


@router.post("/password/forgot")
async def forgot_password(payload: ForgotPasswordRequest, request: Request, user_manager=Depends(get_user_manager)):
    try:
        user = await user_manager.get_by_email(payload.email)
    except UserNotExists:
        return {"detail": "If that email exists, a reset link has been sent"}

    try:
        await user_manager.forgot_password(user, request=request)
    except UserInactive:
        pass
    return {"detail": "If that email exists, a reset link has been sent"}


@router.post("/password/reset")
async def reset_password(payload: ResetPasswordRequest, request: Request, user_manager=Depends(get_user_manager)):
    try:
        await user_manager.reset_password(payload.token, payload.password, request=request)
    except (InvalidResetPasswordToken, UserNotExists):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="RESET_PASSWORD_BAD_TOKEN")
    except InvalidPasswordException as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail={"code": "RESET_PASSWORD_INVALID_PASSWORD", "reason": exc.reason})
    return {"detail": "Password reset"}
