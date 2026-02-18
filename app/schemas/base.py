"""Common response schemas used across the API."""

from pydantic import BaseModel


class MessageResponse(BaseModel):
    message: str


class ErrorResponse(BaseModel):
    detail: str


class PaginatedResponse(BaseModel):
    """Wrap any list endpoint with pagination metadata."""
    total: int
    page: int
    per_page: int
    pages: int
