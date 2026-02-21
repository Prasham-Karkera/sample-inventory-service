from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncGenerator

import structlog
from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

from app.config import settings
from app.database import engine
from app.models.item import Base
from app.routers import health, inventory

logger = structlog.get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    logger.info("inventory_service_starting", version=settings.APP_VERSION)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


app = FastAPI(
    title="FleetBite Inventory Service",
    description="Manages restaurant menu items and real-time stock levels.",
    version=settings.APP_VERSION,
    docs_url="/docs" if settings.ENV != "production" else None,
    lifespan=lifespan,
)

Instrumentator().instrument(app).expose(app, endpoint="/metrics")
app.include_router(inventory.router, tags=["Inventory"])
app.include_router(health.router, tags=["Health"])
