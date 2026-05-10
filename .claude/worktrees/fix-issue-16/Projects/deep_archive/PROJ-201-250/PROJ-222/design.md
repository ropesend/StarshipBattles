# PROJ-222: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Initial Analysis

**Test Baseline:** 13358 passed, 9 pre-existing failures (all in `test_strategy_detail_fmt.py`, unrelated), 2 skipped.

### Root Cause
When Fleet A is ordered to join Fleet B, two orders are created: `MOVE_TO_FLEET(target=B)` + `JOIN_FLEET(target=B)`. Both hold **direct object references** to Fleet B. When Fleet B merges into Fleet C (or is destroyed), Fleet A still holds a reference to the now-defunct Fleet B object. The current validation only checks `if target_fleet is None`, but merged/destroyed fleets are never set to None — they're orphaned objects.

### Current Order Target Flow
- `JoinCommandHandler` creates MOVE_TO_FLEET + JOIN_FLEET orders with direct Fleet reference
- `InterceptCommandHandler` creates MOVE_TO_FLEET order with direct Fleet reference
- `FleetMovementEngine` recalculates path to `order.target.location` every tick
- `FleetOrderProcessor.process_join_fleet()` checks `target_fleet is None` (insufficient)
- On save: Fleet ref → `{'type': 'fleet_ref', 'id': N}`. On load: marker dict → object via `resolve_order_references()`

### Key File Metrics
- `fleet.py`: 321 lines (within 500-line target)
- `command_handlers.py`: ~800 lines (large but organized by handler)
- `fleet_order_processor.py`: ~680 lines
- `event_types.py`: 30 lines

## Swarm Findings Summary

### Architecture
- Fleet uses delegate pattern with 3 existing delegates (all eagerly instantiated in `__init__`)
- `Empire.remove_fleet()` is the **single choke point** for all fleet removal (8 call sites across 5 files)
- Only 2 sites create MOVE_TO_FLEET orders (InterceptCommandHandler, JoinCommandHandler)
- Only 1 site creates JOIN_FLEET orders (JoinCommandHandler)
- AI does NOT issue join or intercept orders — no AI changes needed
- Strategy layer is single-threaded — no race condition risk on pursuer set

### Key Patterns to Reuse
- **Fleet Delegate Pattern**: `game/strategy/data/fleet_*.py` — constructor takes `fleet: 'Fleet'`, stored as `self._fleet`, accessed via `@property` on Fleet
- **Event Logging**: `log_event(EventType.X, category=EventCategory.Y, empire_id=N, message="...", **details)` in GameSession
- **Order Reference Resolution**: `FleetOrderSerializer.resolve_order_references()` at `game_session.py:349-351` — rebuilds object refs from IDs post-load

### Dependencies & Risks

1. **Direct order list mutations in command handlers** — ClearOrdersHandler uses `fleet.orders = []`, DeleteOrderHandler uses `fleet.orders.pop(index)`, RemoveBuildOrderHandler uses list comprehension. Mitigation: Refactor to use Fleet API methods.

2. **Multi-hop merge chains** — Fleet A → B → C. When B merges into C, A must redirect to C. When C later merges into D, A must redirect to D. Mitigation: `merge_with()` transfers pursuers from source to target before merge. Works naturally for arbitrary chain depth.

3. **Concurrent merges in same tick** — `process_instant_orders()` iterates `list(empire.fleets)` copy. Multiple merges can happen in one pass. Mitigation: Deferred removal pattern (already in place via `fleets_to_remove` list). Pursuer redirect happens synchronously in `merge_with()` before fleet is added to removal list.

4. **Memory leak from orphaned Fleet references** — Pursuers hold strong refs. Mitigation: `Empire.remove_fleet()` calls `fleet.pursuers.notify_target_destroyed()` which clears all pursuer references.

5. **Self-targeting validation gap** — No check prevents fleet from intercepting/joining itself. Mitigation: Add validation in both InterceptCommandHandler and JoinCommandHandler.

### Opportunities Discovered
- `RemoveBuildOrderCommandHandler` directly mutates `fleet.orders` but BUILD orders never target fleets — refactor for consistency but no pursuer impact.

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.
