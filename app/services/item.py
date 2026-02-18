"""Item business logic – keeps endpoints thin."""

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.item import Item
from app.schemas.item import ItemCreate, ItemUpdate


class ItemService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(
        self, *, skip: int = 0, limit: int = 100
    ) -> tuple[list[Item], int]:
        """Return (items, total_count) for pagination."""
        total = await self.db.scalar(select(func.count(Item.id)))
        result = await self.db.execute(
            select(Item).offset(skip).limit(limit).order_by(Item.id)
        )
        return list(result.scalars().all()), total or 0

    async def get_by_id(self, item_id: int) -> Item | None:
        result = await self.db.execute(
            select(Item).where(Item.id == item_id)
        )
        return result.scalar_one_or_none()

    async def create(self, data: ItemCreate) -> Item:
        item = Item(**data.model_dump())
        self.db.add(item)
        await self.db.flush()
        await self.db.refresh(item)
        return item

    async def create_bulk(self, items_data: list[ItemCreate]) -> list[Item]:
        """Create multiple items at once."""
        items = [Item(**item.model_dump()) for item in items_data]
        self.db.add_all(items)
        await self.db.flush()
        for item in items:
            await self.db.refresh(item)
        return items

    async def update(self, item_id: int, data: ItemUpdate) -> Item | None:
        item = await self.get_by_id(item_id)
        if not item:
            return None
        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(item, key, value)
        await self.db.flush()
        await self.db.refresh(item)
        return item

    async def delete(self, item_id: int) -> bool:
        item = await self.get_by_id(item_id)
        if not item:
            return False
        await self.db.delete(item)
        return True
