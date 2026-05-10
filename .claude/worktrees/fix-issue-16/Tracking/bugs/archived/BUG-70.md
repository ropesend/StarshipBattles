# BUG-70: Colonize Order Should Load Population Before Moving

## Description

When I give a ship a colonize order, they should try to load population before they move, this should be an order in the order queue.

## Priority
High

## Status
Awaiting Confirmation

## Investigation Report

### Code Path Trace
UI (strategy_colonization.py) -> IssueColonizeCommand/QueueColonizeMissionCommand -> StrategySessionFacade.handle_command() -> GameSession.handle_command() -> CommandHandlerRegistry.dispatch() -> ColonizeCommandHandler/ColonizeMissionCommandHandler

### Root Cause (CONFIRMED)
Two issues with the original fix:

1. **`_find_colony_at_fleet()` used wrong lookup method.** It called `galaxy.get_system_of_object(fleet)` which only matched when `fleet.location == system.global_location` (the center hex). Planets orbit at different hexes (`system.global_location + planet.location`), so the fleet was almost never detected as "at" a colony.

2. **Colony lookup at command time was wrong approach.** The LOAD_POPULATION order should be generic — always inserted, with no colony lookup. Colony resolution belongs at execution time (when the order actually runs during turn processing), not at command time.

### Hypothesis Log

#### Hypothesis 1: `_find_colony_at_fleet()` returns None — CONFIRMED
**Theory:** The system-level lookup fails because fleet.location doesn't match system.global_location.
**Evidence For:** `get_system_of_object` checks `obj.location in self._galaxy.systems` — direct dict key lookup. Fleet at a planet hex won't match.
**Evidence Against:** None.
**Result:** Confirmed as root cause. Method deleted; colony resolution moved to execution time.

## Work Log

### Fix Applied (2026-02-07)

**Root Cause:** When issuing colonize commands (both `IssueColonizeCommand` and `QueueColonizeMissionCommand`), no TRANSFER order was automatically inserted to load passengers before moving/colonizing. The fleet would arrive at the target with empty cargo, resulting in only a 100-unit minimum seed population.

**Changes:**

1. **`game/strategy/engine/game_session.py`**:
   - Added `_find_colony_at_fleet(fleet)` helper method - finds an empire colony in the system where the fleet is currently located
   - Updated `_handle_colonize_command()` - auto-inserts TRANSFER (load passengers, amount=0 for max) order before COLONIZE order when fleet is at a colony with population
   - Updated `_handle_colonize_mission_command()` - auto-inserts TRANSFER order before MOVE + COLONIZE orders

**Order Queue Result:**
- Before: `[MOVE, COLONIZE]`
- After: `[TRANSFER(load passengers), MOVE, COLONIZE]`

The TRANSFER order uses `amount=0` which means "load as much as possible" (up to cargo capacity), ensuring the colony ship carries maximum population to the new world.

**Tests:** All 1510 strategy/gameplay tests pass.

---
### ❌ Fix Rejected [2026-03-14 20:16]
**Reason:** Population still does not load before the move order. When the Colonize button is pressed, the expected order queue should be: Load Population → Move → Colonize Planet. Currently only Move and Colonize Planet appear in the queue — the Load Population (TRANSFER) order is missing.
**New Constraints:** The colonize workflow must insert a TRANSFER (load population) order before the MOVE order so the colony ship carries population to the destination. The full order sequence must be: TRANSFER (load passengers) → MOVE → COLONIZE.
---
### Fix Applied (2026-03-14) — Deep Dive Rework

**Root Cause:** Two issues: (1) `_find_colony_at_fleet()` used system-level lookup that never matched fleets at planet hexes. (2) Colony lookup at command time was the wrong approach — should be at execution time.

**Design Change:** LOAD_POPULATION is now a **generic queued order** with no `planet_id`. Colony is resolved dynamically at execution time from the fleet's current hex.

**Changes:**

1. **`game/strategy/engine/command_handlers.py`**:
   - `create_auto_load_population_order()` — removed colony parameter, always returns a generic LOAD_POPULATION order (no `planet_id`, no `species_id`)
   - `ColonizeCommandHandler.execute()` — always inserts LOAD_POPULATION, no colony lookup
   - `ColonizeMissionCommandHandler.execute()` — same
   - `add_move_order_if_needed()` — chain detection now finds last MOVE order (skips non-MOVE orders like LOAD_POPULATION)

2. **`game/strategy/engine/fleet_order_processor.py`**:
   - `process_transfer()` — when processing LOAD_POPULATION with no `planet_id`, auto-resolves: finds owned colony at fleet's exact hex via `galaxy.get_planets_at_global_hex()`. If no colony found, order is a no-op (popped, fleet continues).

3. **`game/strategy/engine/game_session.py`**:
   - Deleted `_find_colony_at_fleet()` — no longer needed.

**Order Queue Result:**
- Direct colonize: `[LOAD_POPULATION, COLONIZE]`
- Colonize mission: `[LOAD_POPULATION, MOVE, COLONIZE]`
- With existing orders: `[existing MOVE, LOAD_POPULATION, new MOVE, COLONIZE]`

**Diagnostic logging added** in command_handlers.py and fleet_order_processor.py for tracing.

**Tests:** All 13,180 tests pass (0 failures, 2 skipped).
---
