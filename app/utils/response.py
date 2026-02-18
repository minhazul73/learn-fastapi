"""Response formatting utilities for standardized API responses."""

from typing import Any, Generic, Optional, TypeVar

from app.schemas.response import APIResponse, PaginationMetadata

T = TypeVar("T")


def success_response(
    data: Optional[T] = None,
    message: str = "Operation successful",
    response_code: int = 200,
    table_name: str = "",
    pagination: Optional[PaginationMetadata] = None,
) -> APIResponse[T]:
    """
    Create a standardized success response.
    
    Args:
        data: Response data
        message: Success message
        response_code: HTTP response code
        table_name: Optional table name for database operations
        pagination: Pagination metadata if applicable
        
    Returns:
        APIResponse with success=True
    """
    return APIResponse(
        success=True,
        response_code=response_code,
        message=message,
        table_name=table_name,
        data=data,
        pagination=pagination,
    )


def error_response(
    message: str = "An error occurred",
    response_code: int = 400,
    table_name: str = "",
    data: Optional[Any] = None,
) -> dict:
    """
    Create a standardized error response.
    
    Args:
        message: Error message
        response_code: HTTP response code
        table_name: Optional table name
        data: Optional error details
        
    Returns:
        Error response dict
    """
    return {
        "success": False,
        "response_code": response_code,
        "message": message,
        "table_name": table_name,
        "data": data,
    }


def list_response(
    data: list[T],
    message: str = "Data fetched successfully",
    response_code: int = 200,
    table_name: str = "",
    current_page: int = 1,
    per_page: int = 50,
    total: int = 0,
) -> APIResponse[list[T]]:
    """
    Create a paginated list response.
    
    Args:
        data: List of items
        message: Response message
        response_code: HTTP response code
        table_name: Optional table name
        current_page: Current page number (1-based)
        per_page: Items per page
        total: Total number of items
        
    Returns:
        APIResponse with pagination metadata
    """
    last_page = (total + per_page - 1) // per_page if total > 0 else 1
    
    pagination = PaginationMetadata(
        current_page=current_page,
        per_page=per_page,
        last_page=last_page,
        total=total,
    )
    
    return APIResponse(
        success=True,
        response_code=response_code,
        message=message,
        table_name=table_name,
        data=data,
        pagination=pagination,
    )
