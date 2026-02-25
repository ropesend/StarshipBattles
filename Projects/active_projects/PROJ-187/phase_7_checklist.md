# Phase 7: Command Handler Review + Path Projection Update [Medium]

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-187 7`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Review command handlers for tick-awareness, update path projection for action timing.

---

## Tasks

### Task 7.1: Review ColonizeMissionCommandHandler [Simple]
**File:** `game/strategy/engine/command_handlers.py`
**Tests:** `pytest tests/unit/strategy/ -k "colonize"`

- [ ] Verify it already queues: LOAD_POPULATION -> MOVE -> COLONIZE (it does)
- [ ] Verify auto-load behavior works correctly with tick-based execution
- [ ] Document any issues found; fix if needed

**Notes:**

### Task 7.2: Review superweapon mission handlers [Simple]
**File:** `game/strategy/engine/superweapon_command_handlers.py`
**Tests:** `pytest tests/unit/strategy/ -k "superweapon"`

- [ ] Verify mission handlers queue MOVE -> ACTION correctly
- [ ] Verify `_setup_mission_move()` helper still works with tick-based execution
- [ ] Document any issues found; fix if needed

**Notes:**

### Task 7.3: Verify ClearOrdersCommandHandler [Simple]
**File:** `game/strategy/engine/command_handlers.py`
**Tests:** `pytest tests/unit/strategy/ -k "clear"`

- [ ] Verify `fleet.clear_orders()` naturally discards FleetOrder objects with execution_progress
- [ ] Write test: issue multi-tick order -> accumulate some progress -> clear -> verify progress gone

**Notes:**

### Task 7.4: Update FleetNavigationService path projection [Medium]
**File:** `game/strategy/services/fleet_navigation_service.py`
**Tests:** `pytest tests/unit/strategy/services/ -k "navigation or projection"`

- [ ] In `project_path()`: when encountering an action order in the queue, consume `action_time` movement ticks before advancing to next order
- [ ] Account for existing `execution_progress` on current order (reduce remaining ticks)
- [ ] Requires access to ActionTimeResolver or action_time values

**Notes:**

### Task 7.5: Write projection tests with action orders [Simple]
**File:** `tests/unit/strategy/services/test_fleet_navigation_projection.py` (new or extend)
**Tests:** `pytest tests/unit/strategy/services/test_fleet_navigation_projection.py`

- [ ] Test: MOVE -> COLONIZE(action_time=1) shows 1 extra tick of delay
- [ ] Test: MOVE -> STELLERATE_STAR(action_time=5) shows 5 extra ticks of delay
- [ ] Test: In-progress action (execution_progress=2, action_time=5) shows 3 remaining ticks

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `pytest tests/ --testmon` passes
- [ ] Path projection accurately reflects action timing in UI
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
