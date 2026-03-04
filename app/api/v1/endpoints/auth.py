"""Authentication endpoints.

This project is now Supabase-authenticated: clients authenticate with Supabase,
then send the Supabase-issued JWT (access token) to this API.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.exceptions import AppException
from app.database import get_db
from app.models.user import User
from app.schemas.auth import (
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
    UserRead,
)
from app.utils.response import success_response

router = APIRouter()


@router.post("/register", status_code=201)
async def register(data: RegisterRequest, db: AsyncSession = Depends(get_db)):
    raise AppException(
        status_code=410,
        detail="Local auth is retired. Use Supabase Auth and send the Supabase JWT to this API.",
    )


@router.post("/login")
async def login(data: LoginRequest, db: AsyncSession = Depends(get_db)):
    raise AppException(
        status_code=410,
        detail="Local auth is retired. Use Supabase Auth and send the Supabase JWT to this API.",
    )


@router.post("/refresh")
async def refresh(data: RefreshRequest):
    raise AppException(
        status_code=410,
        detail="Token refresh is handled by Supabase. Send a fresh Supabase access token to this API.",
    )


@router.get("/me")
async def me(current_user: User = Depends(get_current_user)):
    user_data = UserRead.from_orm(current_user)
    return success_response(
        data=user_data,
        message="User data retrieved successfully",
        response_code=200,
    )
