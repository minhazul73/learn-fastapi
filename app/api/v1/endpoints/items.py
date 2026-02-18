"""CRUD endpoints for Items."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.exceptions import NotFoundException
from app.database import get_db
from app.models.user import User
from app.schemas.item import ItemCreate, ItemRead, ItemUpdate
from app.services.item import ItemService
from app.utils.response import list_response, success_response

router = APIRouter()


@router.get("")
async def list_items(
    page_no: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    svc = ItemService(db)
    skip = (page_no - 1) * per_page
    items, total = await svc.get_all(skip=skip, limit=per_page)
    items_response = [ItemRead.from_orm(item) for item in items]
    return list_response(
        data=items_response,
        message="Items fetched successfully",
        response_code=200,
        table_name="items",
        current_page=page_no,
        per_page=per_page,
        total=total,
    )


@router.get("/{item_id}")
async def get_item(item_id: int, db: AsyncSession = Depends(get_db)):
    svc = ItemService(db)
    item = await svc.get_by_id(item_id)
    if not item:
        raise NotFoundException("Item")
    item_response = ItemRead.from_orm(item)
    return success_response(
        data=item_response,
        message="Item fetched successfully",
        response_code=200,
        table_name="items",
    )


@router.post("", status_code=201)
async def create_item(
    data: ItemCreate,
    db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(get_current_user),
):
    svc = ItemService(db)
    item = await svc.create(data)
    item_response = ItemRead.from_orm(item)
    return success_response(
        data=item_response,
        message="Item created successfully",
        response_code=201,
        table_name="items",
    )


@router.post("/bulk/import", status_code=201)
async def bulk_create_items(
    items: list[ItemCreate],
    db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(get_current_user),
):
    svc = ItemService(db)
    created_items = await svc.create_bulk(items)
    items_response = [ItemRead.from_orm(item) for item in created_items]
    return success_response(
        data=items_response,
        message=f"{len(items_response)} items created successfully",
        response_code=201,
        table_name="items",
    )


@router.put("/{item_id}")
async def update_item(
    item_id: int,
    data: ItemUpdate,
    db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(get_current_user),
):
    svc = ItemService(db)
    item = await svc.update(item_id, data)
    if not item:
        raise NotFoundException("Item")
    item_response = ItemRead.from_orm(item)
    return success_response(
        data=item_response,
        message="Item updated successfully",
        response_code=200,
        table_name="items",
    )


@router.delete("/{item_id}", status_code=204)
async def delete_item(
    item_id: int,
    db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(get_current_user),
):
    svc = ItemService(db)
    deleted = await svc.delete(item_id)
    if not deleted:
        raise NotFoundException("Item")
