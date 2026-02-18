"""Health-check endpoint – used by Docker HEALTHCHECK & load balancers."""

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.database import get_db
from app.utils.response import success_response

router = APIRouter()
settings = get_settings()


@router.get("")
async def health(db: AsyncSession = Depends(get_db)):
    """
    Returns 200 if the service + DB are reachable.
    """
    try:
        await db.execute(text("SELECT 1"))
        db_ok = True
    except Exception:
        db_ok = False

    return success_response(
        data={
            "status": "healthy" if db_ok else "degraded",
            "environment": settings.ENVIRONMENT,
            "version": settings.APP_VERSION,
            "database": "ok" if db_ok else "unreachable",
        },
        message="Health check completed",
        response_code=200 if db_ok else 503,
    )
