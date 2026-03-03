"""
Shared FastAPI dependencies for the API layer.
"""

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import UnauthorizedException
from app.core.supabase_security import decode_supabase_jwt
from app.database import get_db
from app.models.user import User
from app.services.auth import AuthService

security_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Extracts & validates the JWT from the Authorization header.
    Returns the authenticated User or raises 401.
    """
    if credentials is None:
        raise UnauthorizedException()

    payload = await decode_supabase_jwt(credentials.credentials)
    supabase_user_id = payload.get("sub")
    email = payload.get("email")

    if not supabase_user_id or not isinstance(supabase_user_id, str):
        raise UnauthorizedException("Token missing subject")

    svc = AuthService(db)

    # If the token doesn't include email (can happen depending on provider/claims),
    # still allow authentication for already-provisioned users.
    existing = await svc.get_user_by_supabase_user_id(supabase_user_id)
    if existing is not None:
        if not existing.is_active:
            raise UnauthorizedException("User not found or inactive")
        return existing

    if not email or not isinstance(email, str):
        # We need an email to create/link a local user record.
        raise UnauthorizedException("Token missing email")

    user = await svc.get_or_create_user_for_supabase(
        supabase_user_id=supabase_user_id,
        email=email,
    )
    if user is None or not user.is_active:
        raise UnauthorizedException("User not found or inactive")

    return user
