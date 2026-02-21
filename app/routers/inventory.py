from __future__ import annotations

import uuid
from typing import Annotated

import structlog
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.exceptions import InsufficientStockError, ItemNotFoundError, StockNotFoundError
from app.schemas.item import (
    CreateItemRequest,
    DeductStockRequest,
    ItemResponse,
    SetStockRequest,
    StockResponse,
    UpdateItemRequest,
)
from app.services.inventory_service import InventoryService

logger = structlog.get_logger(__name__)
router = APIRouter(prefix="/v1")


def _get_svc(db: Annotated[AsyncSession, Depends(get_db)]) -> InventoryService:
    return InventoryService(db)


# --- Items ---

@router.post("/items", response_model=ItemResponse, status_code=201, operation_id="create_item", tags=["Items"])
async def create_item(body: CreateItemRequest, svc: Annotated[InventoryService, Depends(_get_svc)]) -> ItemResponse:
    return await svc.create_item(body)


@router.get("/items", response_model=list[ItemResponse], operation_id="list_items", tags=["Items"])
async def list_items(
    restaurant_id: uuid.UUID | None = Query(default=None),
    svc: InventoryService = Depends(_get_svc),
) -> list[ItemResponse]:
    return await svc.list_items(restaurant_id)


@router.get("/items/{item_id}", response_model=ItemResponse, operation_id="get_item", tags=["Items"])
async def get_item(item_id: uuid.UUID, svc: Annotated[InventoryService, Depends(_get_svc)]) -> ItemResponse:
    try:
        return await svc.get_item(item_id)
    except ItemNotFoundError as exc:
        raise HTTPException(status_code=404, detail={"error": {"code": "ITEM_NOT_FOUND", "message": str(exc)}}) from exc


@router.patch("/items/{item_id}", response_model=ItemResponse, operation_id="update_item", tags=["Items"])
async def update_item(
    item_id: uuid.UUID, body: UpdateItemRequest, svc: Annotated[InventoryService, Depends(_get_svc)]
) -> ItemResponse:
    try:
        return await svc.update_item(item_id, body)
    except ItemNotFoundError as exc:
        raise HTTPException(status_code=404, detail={"error": {"code": "ITEM_NOT_FOUND", "message": str(exc)}}) from exc


# --- Stock ---

@router.get("/stock/{item_id}", response_model=StockResponse, operation_id="get_stock", tags=["Stock"])
async def get_stock(item_id: uuid.UUID, svc: Annotated[InventoryService, Depends(_get_svc)]) -> StockResponse:
    try:
        return await svc.get_stock(item_id)
    except StockNotFoundError as exc:
        raise HTTPException(status_code=404, detail={"error": {"code": "STOCK_NOT_FOUND", "message": str(exc)}}) from exc


@router.put("/stock", response_model=StockResponse, operation_id="set_stock", tags=["Stock"])
async def set_stock(body: SetStockRequest, svc: Annotated[InventoryService, Depends(_get_svc)]) -> StockResponse:
    return await svc.set_stock(body)

#This is for testing


@router.post(
    "/stock/deduct",
    response_model=StockResponse,
    status_code=200,
    summary="Deduct stock (called by order-service)",
    operation_id="deduct_stock",
    tags=["Stock"],
)
async def deduct_stock(body: DeductStockRequest, svc: Annotated[InventoryService, Depends(_get_svc)]) -> StockResponse:
    try:
        return await svc.deduct_stock(body)
    except InsufficientStockError as exc:
        raise HTTPException(status_code=409, detail={"error": {"code": "INSUFFICIENT_STOCK", "message": str(exc)}}) from exc
    except StockNotFoundError as exc:
        raise HTTPException(status_code=404, detail={"error": {"code": "STOCK_NOT_FOUND", "message": str(exc)}}) from exc
