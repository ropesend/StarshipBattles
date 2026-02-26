# Phase 7: Command Handler Review + Path Projection Update [Medium]

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-187 7`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Review command handlers for tick-awareness, update path projection for action timing.

---

## Tasks

### Task 7.1: Review ColonizeMissionCommandHandler [Simple]
**File:** `game/strategy/engine/command_handlers.py`
**Tests:** `pytest tests/unit/strategy/ -k "colonize"`

- [x] Verify it already queues: LOAD_POPULATION -> MOVE -> COLONIZE (it does)
- [x] Verify auto-load behavior works correctly with tick-based execution
- [x] Document any issues found; fix if needed

**Notes:** ColonizeMissionCommandHandler verified at line 276-377. Correctly queues LOAD_POPULATION from origin colony, then MOVE to target, then COLONIZE. Works with tick-based execution.

### Task 7.2: Review superweapon mission handlers [Simple]
**File:** `game/strategy/engine/superweapon_command_handlers.py`
**Tests:** `pytest tests/unit/strategy/ -k "superweapon"`

- [x] Verify mission handlers queue MOVE -> ACTION correctly
- [x] Verify `_setup_mission_move()` helper still works with tick-based execution
- [x] Document any issues found; fix if needed

**Notes:** All 5 mission handlers (ImplodePlanetMission, StellerateStarMission, OpenWarpPointMission, CloseWarpPointMission, CreateDysonSphereMission) use shared `_setup_mission_move()` helper which correctly queues MOVE -> ACTION. No issues found.

### Task 7.3: Verify ClearOrdersCommandHandler [Simple]
**File:** `game/strategy/engine/command_handlers.py`
**Tests:** `pytest tests/unit/strategy/ -k "clear"`

- [x] Verify `fleet.clear_orders()` naturally discards FleetOrder objects with execution_progress
- [x] Write test: issue multi-tick order -> accumulate some progress -> clear -> verify progress gone

**Notes:** ClearOrdersCommandHandler at line 380-395 sets `fleet.orders = []` directly, which naturally discards FleetOrder objects along with any execution_progress. Added test `test_clear_orders_discards_execution_progress` in `tests/integration/strategy/test_command_handlers.py`.

### Task 7.4: Update FleetNavigationService path projection [Medium]
**File:** `game/strategy/services/fleet_navigation_service.py`
**Tests:** `pytest tests/unit/strategy/services/ -k "navigation or projection"`

- [x] In `project_path()`: when encountering an action order in the queue, consume `action_time` movement ticks before advancing to next order
- [x] Account for existing `execution_progress` on current order (reduce remaining ticks)
- [x] Requires access to ActionTimeResolver or action_time values

**Notes:** Updated `project_path()` to:
1. Detect non-movement orders (using `MOVEMENT_ORDER_TYPES`)
2. Look up action_time via `_get_action_time_for_projection()` -> `ActionTimeResolver.resolve_action_time()`
3. Account for `execution_progress` on first order (reduce remaining ticks)
4. Consume action_time ticks from `moves_left_in_turn`, advancing turns as needed
5. Added optional `component_registry` parameter for action time lookup

### Task 7.5: Write projection tests with action orders [Simple]
**File:** `tests/unit/strategy/services/test_fleet_navigation_action_timing.py` (new)
**Tests:** `pytest tests/unit/strategy/services/test_fleet_navigation_action_timing.py`

- [x] Test: MOVE -> COLONIZE(action_time=1) shows 1 extra tick of delay
- [x] Test: MOVE -> STELLERATE_STAR(action_time=5) shows 5 extra ticks of delay
- [x] Test: In-progress action (execution_progress=2, action_time=5) shows 3 remaining ticks

**Notes:** Created `tests/unit/strategy/services/test_fleet_navigation_action_timing.py` with 6 tests covering:
- `test_move_colonize_shows_action_delay` - 1 tick action delay
- `test_stellerate_star_shows_multi_tick_delay` - 5 tick action delay
- `test_in_progress_action_shows_remaining_ticks` - partial progress handling
- `test_instant_action_no_delay` - movement-only orders
- `test_multiple_actions_accumulate_delay` - cumulative delays
- `test_action_timing_respects_max_turns` - bounds checking

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] `pytest tests/ -n 12` passes (12466 passed, 1 skipped)
- [x] Path projection accurately reflects action timing in UI
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
