"""
Shared FastAPI dependencies for the API layer.
"""

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import UnauthorizedException
from app.core.security import decode_token
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

    payload = decode_token(credentials.credentials)
    if payload is None or payload.get("type") != "access":
        raise UnauthorizedException("Invalid or expired token")

    user_id = payload.get("sub")
    if user_id is None:
        raise UnauthorizedException()

    svc = AuthService(db)
    user = await svc.get_user_by_id(int(user_id))
    if user is None or not user.is_active:
        raise UnauthorizedException("User not found or inactive")

    return user
