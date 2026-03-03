"""Authentication & user management service."""

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
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

    async def get_user_by_supabase_user_id(self, supabase_user_id: str) -> User | None:
        result = await self.db.execute(
            select(User).where(User.supabase_user_id == supabase_user_id)
        )
        return result.scalar_one_or_none()

    async def get_or_create_user_for_supabase(
        self,
        *,
        supabase_user_id: str,
        email: str,
    ) -> User | None:
        """Return a local user mapped to Supabase identity.

        Strategy:
        - Prefer lookup by `supabase_user_id`
        - Else, if email exists and is not yet linked, link it
        - Else, create a new local user row
        """

        user = await self.get_user_by_supabase_user_id(supabase_user_id)
        if user is not None:
            return user

        by_email = await self.get_user_by_email(email)
        if by_email is not None:
            if by_email.supabase_user_id and by_email.supabase_user_id != supabase_user_id:
                return None
            by_email.supabase_user_id = supabase_user_id
            self.db.add(by_email)
            try:
                await self.db.flush()
                await self.db.refresh(by_email)
                return by_email
            except IntegrityError:
                # Another request likely linked/created the row concurrently.
                await self.db.rollback()
                existing = await self.get_user_by_supabase_user_id(supabase_user_id)
                if existing is not None:
                    return existing
                return await self.get_user_by_email(email)

        user = User(
            email=email,
            hashed_password=None,
            supabase_user_id=supabase_user_id,
            is_active=True,
            is_superuser=False,
        )
        self.db.add(user)
        try:
            await self.db.flush()
            await self.db.refresh(user)
            return user
        except IntegrityError:
            # Two parallel requests can both try to create the same email.
            # Roll back and re-fetch the existing row.
            await self.db.rollback()
            existing = await self.get_user_by_supabase_user_id(supabase_user_id)
            if existing is not None:
                return existing

            existing_by_email = await self.get_user_by_email(email)
            if existing_by_email is None:
                return None

            # If it's an existing user from the old system, link it.
            if not existing_by_email.supabase_user_id:
                existing_by_email.supabase_user_id = supabase_user_id
                self.db.add(existing_by_email)
                try:
                    await self.db.flush()
                    await self.db.refresh(existing_by_email)
                except IntegrityError:
                    await self.db.rollback()
                    return await self.get_user_by_supabase_user_id(supabase_user_id)
            return existing_by_email

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
        if not user or not user.hashed_password:
            return None
        if not verify_password(password, user.hashed_password):
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
