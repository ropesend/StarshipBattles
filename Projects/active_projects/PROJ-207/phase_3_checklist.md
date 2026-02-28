# Phase 3: Execution Path Cleanup

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-207 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Fix dual execution path for JOIN_FLEET and make error handling consistent across execution paths
**Priority:** High

---

## Tasks

### Task 3.1: EP-001 - Remove JOIN_FLEET from Dual Execution Path [Simple]
**Files:**
- `game/strategy/data/fleet.py` (line 54)
- `game/strategy/engine/fleet_order_processor.py` (lines 627-629, 670-704)
**Tests:** `pytest tests/unit/strategy/engine/ -k "fleet_order" && pytest tests/unit/strategy/engine/ -k "join"`

**Problem:** `JOIN_FLEET` is listed in `ACTION_ORDER_TYPES` (fleet.py line 54) AND handled by
`process_instant_orders()` (fleet_order_processor.py lines 691-698). This creates a dual processing
path where JOIN_FLEET could be processed by both the instant path (Phase 1 of tick) and the
tick-based action path (Phase 1.5 via ActionExecutionEngine → process_end_turn_orders).

**Design Decision:** The instant path is the correct one — JOIN_FLEET should fire immediately when
co-located, not go through tick-based action processing.

- [ ] In `fleet.py` line 54: Remove `OrderType.JOIN_FLEET` from `ACTION_ORDER_TYPES`
- [ ] Verify that `process_instant_orders()` (lines 670-704) handles JOIN_FLEET correctly when co-located
- [ ] Verify that `process_end_turn_orders()` JOIN_FLEET branch (lines 627-629) is now dead code for the tick path
- [ ] Remove the JOIN_FLEET branch from `process_end_turn_orders()` (lines 627-629) since instant path handles it
- [ ] Write test: Fleet with JOIN_FLEET order at same location as target → instant merge (not deferred to tick processing)
- [ ] Write test: Fleet with JOIN_FLEET order at different location → order stays queued (waits for MOVE_TO_FLEET to arrive first)
- [ ] Verify: no test regressions

**Notes:** JOIN_FLEET is always preceded by MOVE_TO_FLEET in the queue (see command_handlers.py:354-359). The instant path only fires when co-located, which is the correct behavior.

### Task 3.2: EP-005 - Standardize Error Handling Across Execution Paths [Medium]
**Files:**
- `game/strategy/engine/fleet_movement_engine.py` (lines 153, 165, 170)
- `game/strategy/engine/fleet_order_processor.py` (multiple pop_order calls)
**Tests:** `pytest tests/unit/strategy/engine/ -k "fleet_movement or fleet_order"`

**Problem:** Movement failures call `fleet.clear_orders()` (destroying entire queue), while action
failures call `fleet.pop_order()` (preserving subsequent orders). This means:
- A MOVE order failing due to fuel destroys a queued COLONIZE order
- A COLONIZE order failing preserves a queued TRANSFER order

This inconsistency surprises players — their entire order chain gets wiped by a movement failure.

- [ ] In `fleet_movement_engine.py` line 153 (stranded / no fuel): KEEP `fleet.clear_orders()` — fleet cannot move at all, so preserving subsequent MOVE orders creates false hope. Subsequent action orders would fail validation on the next tick anyway (wrong location).
- [ ] In `fleet_movement_engine.py` line 165 (warp blocked / no capability): Change `fleet.clear_orders()` to `fleet.pop_order()` — fleet can still move normally, so preserve subsequent orders
- [ ] In `fleet_movement_engine.py` line 170 (insufficient warp resources): Change `fleet.clear_orders()` to `fleet.pop_order()` — fleet can still move normally, so preserve subsequent orders
- [ ] Write test: Fleet with [WARP, COLONIZE] queue → WARP fails (no capability) → COLONIZE is preserved
- [ ] Write test: Fleet with [MOVE, COLONIZE] queue → MOVE fails (stranded/no fuel) → entire queue cleared
- [ ] Write test: Fleet with single MOVE order → MOVE fails → order queue is empty
- [ ] Verify: existing movement tests still pass (they may assert clear_orders behavior — update assertions for warp cases)

**Notes:** Stranded fleets (no fuel) cannot execute ANY movement, so clearing all orders is correct — preserving orders just delays their failure by one tick. Warp failures (no capability or insufficient resources) only affect the current warp order; the fleet can still move normally, so subsequent orders should survive.

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Run `pytest tests/ -n 12` — full suite passes
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
