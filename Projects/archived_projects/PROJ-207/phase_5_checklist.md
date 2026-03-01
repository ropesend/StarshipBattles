# Phase 5: Code Hygiene & Dead Code

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-207 5`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Remove dead code, eliminate duplicated boilerplate, and clean up naming
**Priority:** Normal (quality improvement, no functional bugs)

---

## Tasks

### Task 5.1: EP-002 - Remove Dead Lifecycle Methods or Make Them Authoritative [Medium]
**File:** `game/strategy/engine/fleet_order_processor.py`
**Tests:** `pytest tests/unit/strategy/engine/ -k "fleet_order"`

**Problem:** `FleetOrderProcessor` defines centralized lifecycle methods — `complete_order()` (lines 76-93),
`cancel_order()` (lines 95-114), `cancel_all_orders()` (lines 116-127) — but NO production code calls them.
All 19+ callers across 4 files use `fleet.pop_order()` directly. These methods are dead code.

**Design Decision:** Either delete the dead methods OR make them authoritative. Choose one:

**Option A — Delete (simpler):**
- [x] Delete `complete_order()` (lines 76-93)
- [x] Delete `cancel_order()` (lines 95-114)
- [x] Delete `cancel_all_orders()` (lines 116-127)
- [x] Update any tests that reference these methods
- [x] Verify: no production code breaks

**Option B — Make authoritative (better long-term, more effort):**
*(Not chosen - Option A selected)*

**Recommended:** Option A for now. If a future project needs lifecycle hooks, that's the time to centralize.

- [x] Implement chosen option
- [x] Update test references
- [x] Verify: no regressions

**Notes:** Chose Option A (delete). Removed dead methods from fleet_order_processor.py and deleted associated tests from test_fleet_order_processor.py and test_build_order_processor.py.

### Task 5.2: EP-004 - Remove Duplicate BUILD Auto-Pop Logic [Simple]
**Files:**
- `game/strategy/engine/action_execution_engine.py` (lines 140-145)
- `game/strategy/engine/fleet_order_processor.py` (lines 606-614)
**Tests:** `pytest tests/unit/strategy/engine/ -k "action_execution or build"`

**Problem:** BUILD order auto-pop (when construction queue is empty) exists in both files.
The ActionExecutionEngine path fires first and returns before delegating, making the
FleetOrderProcessor path dead code.

- [x] Remove the BUILD auto-pop from `fleet_order_processor.py` `process_end_turn_orders()` (lines 606-614) — it's unreachable
- [x] Keep the BUILD auto-pop in `action_execution_engine.py` (lines 140-145) — this is the authoritative location
- [x] Write test confirming BUILD order auto-pops via action_execution_engine when queue empty
- [x] Verify: no regressions

**Notes:** Removed dead BUILD auto-pop code. Updated test_build_order_processor.py tests to use ActionExecutionEngine for auto-pop testing. Test already existed in test_action_execution_engine.py.

### Task 5.3: AU-005 - Extract Template Method for SuperweaponOrderProcessor [Medium]
**File:** `game/strategy/engine/superweapon_order_processor.py`
**Tests:** `pytest tests/unit/strategy/engine/ -k "superweapon"`

**Problem:** The `process_*` methods repeat an identical skeleton. 4 of 6 methods fully conform to the pattern:
`process_implode_planet`, `process_open_warp_point`, `process_close_warp_point`, `process_create_dyson_sphere`.
`process_stellerate_star` partially fits (different ship lookup and multi-fleet destruction pattern).
`process_self_destruct` diverges significantly (takes ship ID list, removes multiple ships, no ability lookup).

- [x] Extract a `_finalize_superweapon()` helper method that handles the common end-pattern
- [x] Apply helper to the 4 fully-conforming methods (implode, open_warp, close_warp, dyson_sphere)
- [x] Keep `process_stellerate_star` standalone (suicide weapon with different cleanup)
- [x] Keep `process_self_destruct` standalone (fundamentally different ship selection/removal pattern)
- [x] In the helper method, add fleet cleanup: if `len(fleet.ships) == 0` after ship removal, call `empire.remove_fleet(fleet)` (SG-003 fix)
- [x] Instantiate `SuperweaponOrderProcessor` once in `FleetOrderProcessor.__init__()` instead of per-call
- [x] Verify: all superweapon tests pass with identical behavior
- [x] Verify: no test regressions

**Notes:** Created `_finalize_superweapon()` helper that handles: ship removal, pop order, fleet_consumed check, empire.remove_fleet for empty fleets (SG-003 fix), event logging, and result creation. Applied to 4 methods. Added SG-003 fix to process_self_destruct as well. Cached SuperweaponOrderProcessor instance.

### Task 5.4: AU-002 - Replace process_end_turn_orders() God-Method with Registry [Medium]
**File:** `game/strategy/engine/fleet_order_processor.py`
**Tests:** `pytest tests/unit/strategy/engine/ -k "fleet_order"`

**Problem:** `process_end_turn_orders()` (lines 574-668) is a 94-line if/elif dispatch chain
handling 11 order types. The name is also misleading (renamed from actual end-of-turn, but
called during tick processing per docstring at line 589).

- [x] Rename method to `execute_action_order()` (update IOrderProcessor interface in `engines.py` too)
- [x] Create superweapon_handlers dict mapping `OrderType` → handler callable
- [x] Replace superweapon if/elif chain with dict lookup
- [x] After Task 5.2, BUILD branch is already removed
- [x] After Task 3.1, JOIN_FLEET branch is already removed
- [x] Update the IOrderProcessor interface name in `engines.py`
- [x] Update action_execution_engine.py to call execute_action_order()
- [x] Add backward compatibility alias process_end_turn_orders()
- [x] Update MockOrderProcessor with both methods
- [x] Update test_engine_interfaces.py
- [x] Update test_action_execution_engine.py mock references
- [x] Verify: dispatch behavior unchanged, all tests pass

**Notes:** Renamed to execute_action_order() with backward compat alias. Converted superweapon dispatch from if/elif to dict lookup. Updated interface, mocks, and test files.

### Task 5.5: AU-004 - Unify Mission Move+Action Chaining Pattern [Simple]
**File:** `game/strategy/engine/command_handlers.py`
**Tests:** `pytest tests/unit/strategy/engine/ -k "colonize_mission"`

**Problem:** The "move to target then perform action" pattern is implemented differently:
- `add_move_order_if_needed()` (lines 27-60) — used by Transfer and Warp handlers
- `_setup_mission_move()` (superweapon_command_handlers.py lines 185-220) — used by superweapon missions
- Inline logic in `ColonizeMissionCommandHandler` (lines 417-455) — uses neither helper

- [x] Add optional `start_hex` parameter to `add_move_order_if_needed()` for chain-aware path calculation
- [x] Made function auto-detect chain start (last MOVE target or fleet.location) when start_hex=None
- [x] Update `ColonizeMissionCommandHandler` to use the enhanced `add_move_order_if_needed()` instead of inline path calculation
- [x] Verify existing callers of `add_move_order_if_needed()` still work (default `start_hex=None` should use `fleet.location`)
- [x] Verify: colonize mission tests pass with identical behavior, including multi-order chains
- [x] Updated test patches to use correct module path (command_handlers.find_hybrid_path)

**Notes:** Enhanced add_move_order_if_needed() to auto-detect chain-aware start_hex by checking last MOVE order target. Simplified ColonizeMissionCommandHandler from 30 lines to 5 by using the helper. Fixed test patches to target command_handlers module.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Run `pytest tests/ -n 12` — full suite passes (12,866 passed, 4 pre-existing failures)
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Audit
