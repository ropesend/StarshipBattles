# Phase 6: GameSession Initialization Extraction [Simple]

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-87 6`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Extract initialization logic and add fleet lookup optimization

**File:** `game/strategy/engine/game_session.py`
**New File:** `game/strategy/engine/game_initializer.py`
**Tests:** `pytest tests/unit/strategy/ tests/integration/gameplay_loop/ -n 4`

---

## Tasks

### Task 6.1: Create GameInitializer [Simple]
**File:** `game/strategy/engine/game_initializer.py` (NEW)
- [ ] Create `GameInitializer` class
- [ ] Move from GameSession:
  - `_initialize_galaxy()` — galaxy generation logic
  - `_setup_initial_scenario()` — empire/homeworld setup
  - `_adjust_homeworld_to_race()` — race-specific homeworld modifications
- [ ] Provide a single entry point: `GameInitializer.initialize(config) -> (Galaxy, list[Empire])`
- [ ] Wire GameSession `__init__` to call `GameInitializer.initialize()` instead of inline methods

**Notes:**

### Task 6.2: Add Galaxy.get_fleet_by_id() [Simple]
**File:** `game/strategy/data/galaxy.py`
- [ ] Add fleet registry dict to Galaxy (similar to planet registry pattern)
- [ ] Implement `get_fleet_by_id(fleet_id) -> Fleet` with O(1) lookup
- [ ] Update `GameSession._get_fleet_by_id()` to delegate to Galaxy method
- [ ] Ensure fleet registry updates when fleets are created/destroyed/merged

**Notes:** Galaxy already has `get_planet_by_id()` O(1) — follow same pattern.

### Task 6.3: Final verification [Simple]
- [ ] Run `pytest tests/unit/strategy/ -n 4` — all pass
- [ ] Run `pytest tests/integration/strategy/ -n 4` — all pass
- [ ] Run `pytest tests/integration/gameplay_loop/ -n 4` — all pass
- [ ] Run full suite: `pytest tests/ -n 12` — all 7353+ tests pass
- [ ] Verify final line counts:
  - ShipInstance ≤ 550 lines
  - Fleet ≤ 500 lines
  - GameSession ≤ 600 lines
- [ ] Update plan.md Current State

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] All 6 phases complete
- [ ] All tests passing (full suite)
- [ ] No broken import chains
- [ ] Each extracted class has dedicated test file
- [ ] Original classes still serve as facade (public API preserved)
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State
