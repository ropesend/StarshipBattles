# Phase 6: GameSession Initialization Extraction [Simple]

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-87 6`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Extract initialization logic and add fleet lookup optimization

**File:** `game/strategy/engine/game_session.py`
**New File:** `game/strategy/engine/game_initializer.py`
**Tests:** `pytest tests/unit/strategy/ tests/integration/gameplay_loop/ -n 4`

---

## Tasks

### Task 6.1: Create GameInitializer [Simple]
**File:** `game/strategy/engine/game_initializer.py` (NEW)
- [x] Create `GameInitializer` class
- [x] Move from GameSession:
  - `_initialize_galaxy()` — galaxy generation logic
  - `_setup_initial_scenario()` — empire/homeworld setup
  - `_adjust_homeworld_to_race()` — race-specific homeworld modifications
- [x] Provide a single entry point: `GameInitializer.initialize(config) -> (Galaxy, list[Empire])`
- [x] Wire GameSession `__init__` to call `GameInitializer.initialize()` instead of inline methods

**Notes:** Created 216-line GameInitializer with all initialization logic extracted. GameSession reduced from 517 to 357 lines (160 lines saved, 31% reduction).

### Task 6.2: Add Galaxy.get_fleet_by_id() [Simple]
**File:** `game/strategy/data/galaxy.py`
- [x] Add fleet registry dict to Galaxy (similar to planet registry pattern)
- [x] Implement `get_fleet_by_id(fleet_id) -> Fleet` with O(1) lookup
- [x] Update `GameSession._get_fleet_by_id()` to delegate to Galaxy method
- [x] Ensure fleet registry updates when fleets are created/destroyed/merged

**Notes:** Added `fleets_by_id` dict, `register_fleet()`, `unregister_fleet()`, and `get_fleet_by_id()` to Galaxy. GameSession._get_fleet_by_id() now uses O(1) registry lookup with O(n) fallback for backward compatibility.

### Task 6.3: Final verification [Simple]
- [x] Run `pytest tests/unit/strategy/ -n 4` — all pass (1537 passed)
- [x] Run `pytest tests/integration/strategy/ -n 4` — all pass
- [x] Run `pytest tests/integration/gameplay_loop/ -n 4` — all pass
- [x] Run full suite: `pytest tests/ -n 12` — 7524 tests pass
- [x] Verify final line counts:
  - ShipInstance: 749 lines (OVER target of 550 - issue from earlier phases)
  - Fleet: 413 lines ✅ (target ≤ 500)
  - GameSession: 357 lines ✅ (target ≤ 600)
- [x] Update plan.md Current State

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] All 6 phases complete
- [x] All tests passing (full suite)
- [x] No broken import chains
- [x] Each extracted class has dedicated test file
- [x] Original classes still serve as facade (public API preserved)
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State

**NOTE:** ShipInstance at 749 lines exceeds the 550-line target from Phase 1-2. This is a pre-existing issue that needs review in a future project.
