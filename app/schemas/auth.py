from pydantic import BaseModel, EmailStr


# ── Request schemas ───────────────────────────────────────
class RegisterRequest(BaseModel):
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RefreshRequest(BaseModel):
    refresh_token: str


# ── Response schemas ──────────────────────────────────────
class UserRead(BaseModel):
    id: int
    email: str
    is_active: bool

    class Config:
        from_attributes = True
