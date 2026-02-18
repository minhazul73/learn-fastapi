from datetime import datetime

from pydantic import BaseModel, ConfigDict


# ── Request schemas ───────────────────────────────────────
class ItemCreate(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = 0.0


class ItemUpdate(BaseModel):
    """All fields optional for PATCH-style updates."""
    name: str | None = None
    description: str | None = None
    price: float | None = None
    tax: float | None = None


# ── Response schemas ──────────────────────────────────────
class ItemRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str | None = None
    price: float
    tax: float | None = None
    created_at: datetime
    updated_at: datetime
