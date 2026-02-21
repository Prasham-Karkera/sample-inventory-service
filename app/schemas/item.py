from __future__ import annotations

import uuid
from decimal import Decimal

from pydantic import BaseModel, Field


class CreateItemRequest(BaseModel):
    name: str = Field(..., example="Paneer Tikka")
    description: str | None = Field(default=None)
    price: Decimal = Field(..., gt=0, example=149.99)
    restaurant_id: uuid.UUID
    category: str = Field(default="uncategorized", example="starters")


class UpdateItemRequest(BaseModel):
    name: str | None = None
    description: str | None = None
    price: Decimal | None = Field(default=None, gt=0)
    is_available: bool | None = None


class ItemResponse(BaseModel):
    model_config = {"from_attributes": True}
    id: uuid.UUID
    name: str
    description: str | None
    price: Decimal
    restaurant_id: uuid.UUID
    category: str
    is_available: bool


class StockResponse(BaseModel):
    model_config = {"from_attributes": True}
    item_id: uuid.UUID
    quantity: int
    reserved_quantity: int
    available_quantity: int


class DeductStockRequest(BaseModel):
    item_id: uuid.UUID
    quantity: int = Field(..., ge=1)


class SetStockRequest(BaseModel):
    item_id: uuid.UUID
    quantity: int = Field(..., ge=0)
