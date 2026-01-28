# Phase 1: Critical Fixes

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-30 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Address critical severity findings that pose immediate risk
**Priority:** Immediate

---

## Tasks

### Task 1.1: STRAT-01 - Cross-layer import violation [Complete]
**File:** `game/strategy/systems/design_library.py:14`
**Tests:** `pytest tests/unit/simulation/test_simulation_design_loader.py tests/unit/strategy/test_design_library.py`

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix (test_simulation_design_loader.py - 8 tests)
- [x] Implement the fix (SimulationDesignLoader class created)
- [x] Apply remaining changes (removed Ship import, removed load_design() method, updated UI callers)
- [x] Verify: tests pass, no regressions (32 tests passing, 991 total tests passing)

**Notes:**
- Issue: `DesignLibrary` imports `Ship` from simulation layer (line 14)
- Root cause: `load_design()` method creates Ship objects but belongs in strategy layer
- Solution: Created `SimulationDesignLoader` in `game/simulation/services/design_loader.py`
- Changes applied:
  - Removed `from game.simulation.entities.ship import Ship` from design_library.py
  - Removed `load_design()` method from design_library.py
  - Added `SimulationDesignLoader` import to workshop_screen.py and build_queue_screen.py
  - Updated 3 call sites to use `load_design_data()` + `SimulationDesignLoader`
  - Removed 2 obsolete tests from test_design_library.py


---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
