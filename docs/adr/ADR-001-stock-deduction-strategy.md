# ADR-001: Immediate Stock Deduction vs Reservation

**Status:** ACCEPTED  
**Date:** 2026-01-20  
**Author(s):** @prasham-dev  

---

## Context

When an order is placed, should we immediately reduce `quantity`, or use a `reserved_quantity` field and finalize on delivery?

## Decision

Use **immediate deduction** (reduce `quantity` directly) for MVP. The `reserved_quantity` field exists and is available for a future reservation model.

## Rationale

| Option | Pros | Cons | Decision |
|--------|------|------|----------|
| Immediate deduction | Simple, prevents overselling | Cannot hold stock during checkout timeout | ✅ Selected (MVP) |
| Reservation model | Better UX for concurrent checkout | More complex state, needs cleanup job | ❌ Deferred |

## Consequences

- Straightforward: `quantity -= requested`
- At scale with concurrent orders: transition to reservation model (ADR-002, TBD)
- Clients should handle HTTP 409 INSUFFICIENT_STOCK gracefully
