from __future__ import annotations

import uuid
import enum
from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, Enum, Integer, Numeric, String, func, Boolean
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID


class Base(DeclarativeBase):
    pass


class Item(Base):
    """inv_items — Menu items in the restaurant catalog."""

    __tablename__ = "inv_items"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    restaurant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)
    category: Mapped[str] = mapped_column(String(100), nullable=False, default="uncategorized")
    is_available: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class Stock(Base):
    """inv_stock — Stock levels per item."""

    __tablename__ = "inv_stock"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    item_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, unique=True, index=True)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    reserved_quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    @property
    def available_quantity(self) -> int:
        return self.quantity - self.reserved_quantity
