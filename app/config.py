"""
Application configuration using pydantic-settings.
Loads from .env file and environment variables.
Environment variables always override .env file values.
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # ── App ───────────────────────────────────────────────
    APP_NAME: str = "MyApp API"
    APP_VERSION: str = "0.1.0"
    ENVIRONMENT: str = "dev"  # dev | stage | prod
    DEBUG: bool = False

    # ── Server ────────────────────────────────────────────
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    # Keep workers LOW for Oracle free tier (1 OCPU / 1 GB RAM)
    WORKERS: int = 1

    # ── Database (PostgreSQL + asyncpg) ───────────────────
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/myapp"
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 0  # 0 = no overflow; keeps memory bounded
    DB_POOL_TIMEOUT: int = 30
    DB_POOL_RECYCLE: int = 300  # recycle stale connections every 5 min

    # ── Auth / JWT ────────────────────────────────────────
    SECRET_KEY: str = "CHANGE-ME-in-production-use-openssl-rand-hex-32"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # ── CORS ──────────────────────────────────────────────
    CORS_ORIGINS: list[str] = ["*"]

    # ── n8n (future) ─────────────────────────────────────
    N8N_WEBHOOK_URL: str = ""
    N8N_API_KEY: str = ""

    # ── Helpers ───────────────────────────────────────────
    @property
    def is_prod(self) -> bool:
        return self.ENVIRONMENT == "prod"

    @property
    def is_dev(self) -> bool:
        return self.ENVIRONMENT == "dev"


@lru_cache
def get_settings() -> Settings:
    """Cached settings instance – import this wherever you need config."""
    return Settings()
