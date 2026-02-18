"""
Application entry-point.
Creates the FastAPI app with lifespan, middleware, and routers.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from app.config import get_settings
from app.core.exceptions import register_exception_handlers

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup / shutdown logic (connection pools, caches, etc.)."""
    # ── Startup ───────────────────────────────────────────
    # e.g. warm up DB pool, load ML models, start schedulers
    yield
    # ── Shutdown ──────────────────────────────────────────
    from app.database import engine

    await engine.dispose()


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    docs_url="/docs" if not settings.is_prod else None,
    redoc_url="/redoc" if not settings.is_prod else None,
    openapi_url="/openapi.json" if not settings.is_prod else None,
    lifespan=lifespan,
)

# ── Middleware (order matters – outermost first) ──────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if settings.is_prod:
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])

# ── Exception handlers ───────────────────────────────────
register_exception_handlers(app)

# ── Routers ───────────────────────────────────────────────
from app.api.v1.router import api_router  # noqa: E402

app.include_router(api_router, prefix="/api/v1")
