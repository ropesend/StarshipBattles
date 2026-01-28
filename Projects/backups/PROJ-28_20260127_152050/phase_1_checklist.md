# Phase 1: Critical Fixes

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-28 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Address critical severity findings that pose immediate risk
**Priority:** Immediate

---

## Tasks

### Task 1.1: PHYS-01 - Physics constants duplication [Complete]
**File:** `game/simulation/systems/stats.py`
**Tests:** `pytest tests/unit/systems/test_physics.py::TestPhysicsConstantsConsolidation`

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:**
- Found K_SPEED, K_THRUST, K_TURN hardcoded in stats.py lines 243-244, 251
- Added import from physics_constants.py at top of stats.py
- Removed local constant definitions inside calculate() method
- Added 2 regression tests in TestPhysicsConstantsConsolidation:
  - test_stats_uses_physics_constants_module: verifies import
  - test_physics_constants_values: documents expected values
- All 4605 tests pass (2 new tests added)


---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
