# ka-chow-inventory-service

> **Service:** Inventory & Catalog  
> **Port:** 8003  
> **Team:** Commerce  
> **Database:** `fb_inventory` (PostgreSQL)

## Service Overview

Owns the restaurant menu catalog (items, pricing, availability) and real-time stock levels. Exposes a `POST /v1/stock/deduct` endpoint called synchronously by order-service during order creation.

## Architecture Role

```
API Gateway → [Inventory Service :8003] → PostgreSQL (fb_inventory)
                       ↑
           Called by order-service for stock checks and deduction
```

## Dependencies

| Dependency | Type | Purpose |
|------------|------|---------|
| PostgreSQL | Database | Item catalog + stock records |
| order-service | Downstream caller | Calls `POST /v1/stock/deduct` |

## API Reference

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/v1/items` | Create catalog item |
| `GET` | `/v1/items` | List items (filter by restaurant_id) |
| `GET` | `/v1/items/{id}` | Get item detail |
| `PATCH` | `/v1/items/{id}` | Update item |
| `GET` | `/v1/stock/{item_id}` | Get stock level |
| `PUT` | `/v1/stock` | Set stock level (admin) |
| `POST` | `/v1/stock/deduct` | Deduct stock (order-service) |

## Data Model

**`inv_items`** — Menu catalog entries  
**`inv_stock`** — Per-item stock levels with available_quantity = quantity - reserved_quantity

## Configuration

| Variable | Required | Description |
|----------|----------|-------------|
| `INV_DATABASE_URL` | ✅ | PostgreSQL async DSN |
| `INV_ENV` | — | Default: `development` |

## Running Locally

```bash
cp .env.example .env
docker-compose up -d
curl http://localhost:8003/health/live
```

## ADRs

- [ADR-001: Stock deduction strategy](docs/adr/ADR-001-stock-deduction-strategy.md)
