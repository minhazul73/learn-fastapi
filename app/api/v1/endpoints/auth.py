"""Authentication endpoints for mobile app (register / login / refresh / me)."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.exceptions import ConflictException, UnauthorizedException
from app.database import get_db
from app.models.user import User
from app.schemas.auth import (
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
    TokenResponse,
    UserRead,
)
from app.services.auth import AuthService
from app.utils.response import success_response

router = APIRouter()


@router.post("/register", status_code=201)
async def register(data: RegisterRequest, db: AsyncSession = Depends(get_db)):
    svc = AuthService(db)
    existing = await svc.get_user_by_email(data.email)
    if existing:
        raise ConflictException("Email already registered")
    user = await svc.register(data)
    tokens = svc.create_tokens(user.id)
    return success_response(
        data=tokens,
        message="User registered successfully",
        response_code=201,
    )


@router.post("/login")
async def login(data: LoginRequest, db: AsyncSession = Depends(get_db)):
    svc = AuthService(db)
    user = await svc.authenticate(data.email, data.password)
    if not user:
        raise UnauthorizedException("Invalid email or password")
    tokens = svc.create_tokens(user.id)
    return success_response(
        data=tokens,
        message="Login successful",
        response_code=200,
    )


@router.post("/refresh")
async def refresh(data: RefreshRequest):
    tokens = AuthService.refresh_access_token(data.refresh_token)
    if tokens is None:
        raise UnauthorizedException("Invalid or expired refresh token")
    return success_response(
        data=tokens,
        message="Token refreshed successfully",
        response_code=200,
    )


@router.get("/me")
async def me(current_user: User = Depends(get_current_user)):
    user_data = UserRead.from_orm(current_user)
    return success_response(
        data=user_data,
        message="User data retrieved successfully",
        response_code=200,
    )
