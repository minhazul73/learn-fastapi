"""Standardized API response schemas."""

from typing import Any, Generic, Optional, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class PaginationMetadata(BaseModel):
    """Pagination metadata for list responses."""
    current_page: int = Field(..., ge=1, description="Current page number (1-based)")
    per_page: int = Field(..., ge=1, description="Items per page")
    last_page: int = Field(..., ge=1, description="Total number of pages")
    total: int = Field(..., ge=0, description="Total number of items")


class APIResponse(BaseModel, Generic[T]):
    """
    Standard API response wrapper.
    
    Examples:
        Basic response with data:
        {
            "success": true,
            "response_code": 200,
            "message": "Operation successful",
            "table_name": "",
            "data": [...]
        }
        
        Paginated response:
        {
            "success": true,
            "response_code": 200,
            "message": "Data fetched successfully",
            "table_name": "",
            "pagination": {...},
            "data": [...]
        }
    """
    success: bool
    response_code: int
    message: str
    table_name: str = ""
    pagination: Optional[PaginationMetadata] = None
    data: Optional[T] = None

    class Config:
        exclude_none = True
        json_encoders = {type(None): lambda v: None}
        json_schema_extra = {
            "example": {
                "success": True,
                "response_code": 200,
                "message": "Operation successful",
                "table_name": "",
                "data": []
            }
        }


class ErrorResponse(BaseModel):
    """Standard error response."""
    success: bool = False
    response_code: int
    message: str
    table_name: str = ""
    data: Optional[Any] = None

    class Config:
        exclude_none = True


# Convenience type aliases
SuccessResponse = APIResponse
