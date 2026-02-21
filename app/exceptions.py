from __future__ import annotations


class FleetBiteError(Exception):
    pass


class ItemNotFoundError(FleetBiteError):
    pass


class StockNotFoundError(FleetBiteError):
    pass


class InsufficientStockError(FleetBiteError):
    pass
