from __future__ import annotations

import uuid

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import InsufficientStockError, ItemNotFoundError, StockNotFoundError
from app.models.item import Item, Stock
from app.schemas.item import (
    CreateItemRequest,
    DeductStockRequest,
    ItemResponse,
    SetStockRequest,
    StockResponse,
    UpdateItemRequest,
)

logger = structlog.get_logger(__name__)


class InventoryService:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def create_item(self, request: CreateItemRequest) -> ItemResponse:
        item = Item(**request.model_dump())
        stock = Stock(item_id=item.id, quantity=0)
        self._db.add(item)
        self._db.add(stock)
        await self._db.commit()
        await self._db.refresh(item)
        logger.info("item_created", item_id=str(item.id), name=item.name)
        return ItemResponse.model_validate(item)

    async def get_item(self, item_id: uuid.UUID) -> ItemResponse:
        result = await self._db.execute(select(Item).where(Item.id == item_id))
        item = result.scalar_one_or_none()
        if not item:
            raise ItemNotFoundError(f"Item {item_id} not found")
        return ItemResponse.model_validate(item)

    async def list_items(self, restaurant_id: uuid.UUID | None = None) -> list[ItemResponse]:
        q = select(Item)
        if restaurant_id:
            q = q.where(Item.restaurant_id == restaurant_id)
        result = await self._db.execute(q.order_by(Item.name))
        return [ItemResponse.model_validate(i) for i in result.scalars().all()]

    async def update_item(self, item_id: uuid.UUID, request: UpdateItemRequest) -> ItemResponse:
        result = await self._db.execute(select(Item).where(Item.id == item_id))
        item = result.scalar_one_or_none()
        if not item:
            raise ItemNotFoundError(f"Item {item_id} not found")
        for field, value in request.model_dump(exclude_none=True).items():
            setattr(item, field, value)
        await self._db.commit()
        await self._db.refresh(item)
        return ItemResponse.model_validate(item)

    async def get_stock(self, item_id: uuid.UUID) -> StockResponse:
        result = await self._db.execute(select(Stock).where(Stock.item_id == item_id))
        stock = result.scalar_one_or_none()
        if not stock:
            raise StockNotFoundError(f"Stock record for item {item_id} not found")
        return StockResponse(
            item_id=stock.item_id,
            quantity=stock.quantity,
            reserved_quantity=stock.reserved_quantity,
            available_quantity=stock.available_quantity,
        )

    async def set_stock(self, request: SetStockRequest) -> StockResponse:
        result = await self._db.execute(select(Stock).where(Stock.item_id == request.item_id))
        stock = result.scalar_one_or_none()
        if stock:
            stock.quantity = request.quantity
        else:
            stock = Stock(item_id=request.item_id, quantity=request.quantity)
            self._db.add(stock)
        await self._db.commit()
        await self._db.refresh(stock)
        logger.info("stock_set", item_id=str(request.item_id), quantity=request.quantity)
        return StockResponse(
            item_id=stock.item_id,
            quantity=stock.quantity,
            reserved_quantity=stock.reserved_quantity,
            available_quantity=stock.available_quantity,
        )

    async def deduct_stock(self, request: DeductStockRequest) -> StockResponse:
        result = await self._db.execute(select(Stock).where(Stock.item_id == request.item_id))
        stock = result.scalar_one_or_none()
        if not stock:
            raise StockNotFoundError(f"Stock record for item {request.item_id} not found")
        if stock.available_quantity < request.quantity:
            raise InsufficientStockError(
                f"Insufficient stock for item {request.item_id}: "
                f"requested {request.quantity}, available {stock.available_quantity}"
            )
        stock.quantity -= request.quantity
        await self._db.commit()
        await self._db.refresh(stock)
        logger.info("stock_deducted", item_id=str(request.item_id), deducted=request.quantity, remaining=stock.quantity)
        return StockResponse(
            item_id=stock.item_id,
            quantity=stock.quantity,
            reserved_quantity=stock.reserved_quantity,
            available_quantity=stock.available_quantity,
        )
