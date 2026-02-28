# Phase 5: Code Hygiene & Dead Code

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-207 5`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
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
- [ ] Delete `complete_order()` (lines 76-93)
- [ ] Delete `cancel_order()` (lines 95-114)
- [ ] Delete `cancel_all_orders()` (lines 116-127)
- [ ] Update any tests that reference these methods
- [ ] Verify: no production code breaks

**Option B — Make authoritative (better long-term, more effort):**
- [ ] Route all `fleet.pop_order()` calls through `complete_order()` or `cancel_order()` as appropriate
- [ ] This gives a single place to add logging, events, cleanup hooks later
- [ ] Update all 12+ calls in `fleet_order_processor.py`, 6 in `superweapon_order_processor.py`, 1 in `action_execution_engine.py`

**Recommended:** Option A for now. If a future project needs lifecycle hooks, that's the time to centralize.

- [ ] Implement chosen option
- [ ] Update test references
- [ ] Verify: no regressions

**Notes:**

### Task 5.2: EP-004 - Remove Duplicate BUILD Auto-Pop Logic [Simple]
**Files:**
- `game/strategy/engine/action_execution_engine.py` (lines 140-145)
- `game/strategy/engine/fleet_order_processor.py` (lines 606-614)
**Tests:** `pytest tests/unit/strategy/engine/ -k "action_execution or build"`

**Problem:** BUILD order auto-pop (when construction queue is empty) exists in both files.
The ActionExecutionEngine path fires first and returns before delegating, making the
FleetOrderProcessor path dead code.

- [ ] Remove the BUILD auto-pop from `fleet_order_processor.py` `process_end_turn_orders()` (lines 606-614) — it's unreachable
- [ ] Keep the BUILD auto-pop in `action_execution_engine.py` (lines 140-145) — this is the authoritative location
- [ ] Write test confirming BUILD order auto-pops via action_execution_engine when queue empty
- [ ] Verify: no regressions

**Notes:**

### Task 5.3: AU-005 - Extract Template Method for SuperweaponOrderProcessor [Medium]
**File:** `game/strategy/engine/superweapon_order_processor.py`
**Tests:** `pytest tests/unit/strategy/engine/ -k "superweapon"`

**Problem:** The `process_*` methods repeat an identical skeleton. 4 of 6 methods fully conform to the pattern:
`process_implode_planet`, `process_open_warp_point`, `process_close_warp_point`, `process_create_dyson_sphere`.
`process_stellerate_star` partially fits (different ship lookup and multi-fleet destruction pattern).
`process_self_destruct` diverges significantly (takes ship ID list, removes multiple ships, no ability lookup).

Common skeleton (steps 1-3 and 5-9 are boilerplate, ~60% of each conforming method):
1. Get current order
2. Validate target
3. Find ship with ability (or fallback — addressed by Task 2.3)
4. Execute unique effect
5. Remove ship from fleet
6. Pop order
7. Check if fleet consumed → **if fleet empty, call `empire.remove_fleet(fleet)`** (SG-003 fix)
8. Log event
9. Return result

- [ ] Extract a `_execute_superweapon(fleet, empire, galaxy, order_type, ability_name, effect_fn, ...)` template method that handles the common skeleton
- [ ] Apply template to the 4 fully-conforming methods (implode, open_warp, close_warp, dyson_sphere)
- [ ] Evaluate whether `process_stellerate_star` can partially use the template (optional steps)
- [ ] Keep `process_self_destruct` standalone (fundamentally different ship selection/removal pattern)
- [ ] In the template method, add fleet cleanup: if `len(fleet.ships) == 0` after ship removal, call `empire.remove_fleet(fleet)` (matching `process_colonize()` and `process_join_fleet()` patterns)
- [ ] Instantiate `SuperweaponOrderProcessor` once in `FleetOrderProcessor.__init__()` instead of per-call at line 647
- [ ] Reduce the 4 conforming methods from ~350 lines to ~120
- [ ] Verify: all superweapon tests pass with identical behavior
- [ ] Verify: no test regressions

**Notes:** This is the single biggest DRY win in the fleet order system. The existing tests should fully cover the refactor. The fleet cleanup (SG-003) prevents ghost fleets after superweapon consumption — currently 4 processors set `fleet_consumed=True` but never call `empire.remove_fleet()`.

### Task 5.4: AU-002 - Replace process_end_turn_orders() God-Method with Registry [Medium]
**File:** `game/strategy/engine/fleet_order_processor.py`
**Tests:** `pytest tests/unit/strategy/engine/ -k "fleet_order"`

**Problem:** `process_end_turn_orders()` (lines 574-668) is a 94-line if/elif dispatch chain
handling 11 order types. The name is also misleading (renamed from actual end-of-turn, but
called during tick processing per docstring at line 589).

- [ ] Rename method to `execute_action_order()` (update IOrderProcessor interface in `engines.py` too)
- [ ] Create an `_action_handlers` dict mapping `OrderType` → handler callable:
  ```python
  self._action_handlers = {
      OrderType.COLONIZE: self.process_colonize,
      OrderType.TRANSFER: self.process_transfer,
      OrderType.LOAD_POPULATION: self.process_transfer,
      OrderType.UNLOAD_POPULATION: self.process_transfer,
      # ... superweapons delegate to SuperweaponOrderProcessor
  }
  ```
- [ ] Replace the if/elif chain with a dict lookup + call
- [ ] After Task 5.2, BUILD branch is already removed
- [ ] After Task 3.1, JOIN_FLEET branch is already removed
- [ ] Update the IOrderProcessor interface name in `engines.py`
- [ ] Update all callers of `process_end_turn_orders()` to use new name
- [ ] Verify: dispatch behavior unchanged, all tests pass

**Notes:** This mirrors the successful CommandHandlerRegistry pattern. Do this task AFTER Tasks 3.1 and 5.2 which remove branches from the method.

Test files that reference `process_end_turn_orders` and need renaming:
1. `tests/unit/strategy/test_fleet_order_processor.py`
2. `tests/integration/strategy/test_colonize_logic.py`
3. `tests/unit/strategy/interfaces/test_engine_interfaces.py`
4. `tests/unit/strategy/mocks/mock_engines.py` (implements IOrderProcessor)
5. `tests/unit/test_advanced_fleet_orders.py`
6. `tests/unit/strategy/turn_engine/test_dependency_injection.py`
7. `tests/unit/strategy/engine/test_action_execution_engine.py`
8. `tests/unit/strategy/engine/test_build_order_processor.py`

### Task 5.5: AU-004 - Unify Mission Move+Action Chaining Pattern [Simple]
**File:** `game/strategy/engine/command_handlers.py`
**Tests:** `pytest tests/unit/strategy/engine/ -k "colonize_mission"`

**Problem:** The "move to target then perform action" pattern is implemented differently:
- `add_move_order_if_needed()` (lines 27-60) — used by Transfer and Warp handlers
- `_setup_mission_move()` (superweapon_command_handlers.py lines 185-220) — used by superweapon missions
- Inline logic in `ColonizeMissionCommandHandler` (lines 417-455) — uses neither helper

- [ ] Add optional `start_hex` parameter to `add_move_order_if_needed()` for chain-aware path calculation. Currently the helper only checks `fleet.location` (line 44), but `ColonizeMissionCommandHandler` (lines 419-422) and `_setup_mission_move()` (lines 199-204) check the last queued MOVE order's target. Without this parameter, multi-order chaining would break.
- [ ] Update `ColonizeMissionCommandHandler` to use the enhanced `add_move_order_if_needed(start_hex=...)` instead of inline path calculation
- [ ] Verify existing callers of `add_move_order_if_needed()` still work (default `start_hex=None` should use `fleet.location`)
- [ ] Verify: colonize mission tests pass with identical behavior, including multi-order chains

**Notes:** The superweapon mission helper `_setup_mission_move()` is in a different file and may stay separate due to different parameter needs. The main win is getting ColonizeMission to use the existing helper. **CRITICAL:** Do NOT naively replace the inline logic without adding chain awareness — `add_move_order_if_needed()` currently only considers `fleet.location`, not the last queued MOVE destination.

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Run `pytest tests/ -n 12` — full suite passes
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
