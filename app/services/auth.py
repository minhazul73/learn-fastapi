"""Authentication & user management service."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.models.user import User
from app.schemas.auth import RegisterRequest


class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_user_by_email(self, email: str) -> User | None:
        result = await self.db.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()

    async def get_user_by_id(self, user_id: int) -> User | None:
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()

    async def register(self, data: RegisterRequest) -> User:
        user = User(
            email=data.email,
            hashed_password=hash_password(data.password),
        )
        self.db.add(user)
        await self.db.flush()
        await self.db.refresh(user)
        return user

    async def authenticate(self, email: str, password: str) -> User | None:
        user = await self.get_user_by_email(email)
        if not user or not verify_password(password, user.hashed_password):
            return None
        return user

    @staticmethod
    def create_tokens(user_id: int) -> dict:
        return {
            "access_token": create_access_token({"sub": str(user_id)}),
            "refresh_token": create_refresh_token({"sub": str(user_id)}),
            "token_type": "bearer",
        }

    @staticmethod
    def refresh_access_token(refresh_token: str) -> dict | None:
        payload = decode_token(refresh_token)
        if payload is None or payload.get("type") != "refresh":
            return None
        return {
            "access_token": create_access_token({"sub": payload["sub"]}),
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }
