# Standardized API Response Format

This document explains how to use the standardized response format for all API endpoints in this FastAPI application.

## Overview

All API responses follow a consistent JSON structure with:
- `success`: Boolean indicating success/failure
- `response_code`: HTTP status code
- `message`: Human-readable message
- `table_name`: Optional table name (useful for database operations)
- `data`: The actual response data
- `pagination`: Optional pagination metadata for list endpoints

## Response Format Examples

### Success Response (Single Item)

```json
{
  "success": true,
  "response_code": 200,
  "message": "Item fetched successfully",
  "table_name": "items",
  "data": {
    "id": 1,
    "name": "Product Name",
    "description": "Product Description"
  }
}
```

### Success Response (List with Pagination)

```json
{
  "success": true,
  "response_code": 200,
  "message": "Items fetched successfully",
  "table_name": "items",
  "pagination": {
    "current_page": 1,
    "per_page": 10,
    "last_page": 50,
    "total": 500
  },
  "data": [
    {
      "id": 1,
      "name": "Product 1"
    },
    {
      "id": 2,
      "name": "Product 2"
    }
  ]
}
```

### Error Response

```json
{
  "success": false,
  "response_code": 404,
  "message": "Item not found",
  "table_name": "items",
  "data": null
}
```

## Using Response Utilities

### 1. Basic Success Response

```python
from app.utils.response import success_response

@router.get("/items/{item_id}")
async def get_item(item_id: int):
    item = await get_item_from_db(item_id)
    return success_response(
        data=item,
        message="Item fetched successfully",
        response_code=200,
        table_name="items",
    )
```

### 2. List Response with Pagination

```python
from app.utils.response import list_response

@router.get("/items")
async def list_items(skip: int = 0, limit: int = 50):
    items, total = await get_items_from_db(skip=skip, limit=limit)
    current_page = (skip // limit) + 1 if limit > 0 else 1
    
    return list_response(
        data=items,
        message="Items fetched successfully",
        response_code=200,
        table_name="items",
        current_page=current_page,
        per_page=limit,
        total=total,
    )
```

### 3. Create Response

```python
from app.utils.response import success_response

@router.post("/items", status_code=201)
async def create_item(item_data: ItemCreate):
    new_item = await create_item_in_db(item_data)
    return success_response(
        data=new_item,
        message="Item created successfully",
        response_code=201,
        table_name="items",
    )
```

### 4. Error Response

```python
from app.utils.response import error_response

# In exception handlers or custom error cases
return JSONResponse(
    status_code=404,
    content=error_response(
        message="Item not found",
        response_code=404,
        table_name="items",
    ),
)
```

## Response Utilities API Reference

### `success_response()`

Creates a standardized success response.

**Parameters:**
- `data` (Optional[T]): Response data
- `message` (str): Success message (default: "Operation successful")
- `response_code` (int): HTTP status code (default: 200)
- `table_name` (str): Optional table name (default: "")
- `pagination` (Optional[PaginationMetadata]): Pagination metadata if applicable

**Returns:** `APIResponse[T]`

### `list_response()`

Creates a paginated list response.

**Parameters:**
- `data` (list[T]): List of items
- `message` (str): Response message (default: "Data fetched successfully")
- `response_code` (int): HTTP status code (default: 200)
- `table_name` (str): Optional table name (default: "")
- `current_page` (int): Current page number (1-based, default: 1)
- `per_page` (int): Items per page (default: 50)
- `total` (int): Total number of items (default: 0)

**Returns:** `APIResponse[list[T]]`

**Auto-calculates:** `last_page` = ceil(total / per_page)

### `error_response()`

Creates a standardized error response.

**Parameters:**
- `message` (str): Error message (default: "An error occurred")
- `response_code` (int): HTTP status code (default: 400)
- `table_name` (str): Optional table name (default: "")
- `data` (Optional[Any]): Optional error details (default: None)

**Returns:** `dict`

## Exception Handling

All custom exceptions are automatically converted to standardized error responses:

- **404 Not Found**: `NotFoundException(resource_name)`
- **401 Unauthorized**: `UnauthorizedException(message)`
- **403 Forbidden**: `ForbiddenException(message)`
- **409 Conflict**: `ConflictException(message)`

Example:
```python
from app.core.exceptions import NotFoundException

if not item:
    raise NotFoundException("Item")
    # Returns:
    # {
    #   "success": false,
    #   "response_code": 404,
    #   "message": "Item not found",
    #   "table_name": "",
    #   "data": null
    # }
```

## Best Practices

1. **Always use response utilities** for consistency
2. **Include meaningful messages** that describe what happened
3. **Set appropriate status codes** (201 for created, 200 for success, etc.)
4. **Include table_name** when the operation involves a specific table
5. **Use pagination** for list endpoints to handle large datasets
6. **Filter sensitive data** before returning in responses

## Migration Guide

### Before:
```python
@router.get("/items")
async def list_items():
    items = await get_items()
    return items
```

### After:
```python
from app.utils.response import list_response

@router.get("/items")
async def list_items():
    items, total = await get_items()
    return list_response(
        data=items,
        message="Items fetched successfully",
        table_name="items",
        total=total,
    )
```
