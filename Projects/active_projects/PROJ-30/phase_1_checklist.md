# Phase 1: Critical Fixes

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-30 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** In Progress
**Objective:** Address critical severity findings that pose immediate risk
**Priority:** Immediate

---

## Tasks

### Task 1.1: STRAT-01 - Cross-layer import violation [In Progress]
**File:** `game/strategy/systems/design_library.py:14`
**Tests:** `pytest tests/unit/simulation/test_simulation_design_loader.py tests/unit/strategy/test_design_library.py`

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix (test_simulation_design_loader.py - 9 tests)
- [x] Implement the fix (SimulationDesignLoader class created)
- [ ] Apply remaining changes (IDE keeps reverting - see plan.md Current State)
- [ ] Verify: tests pass, no regressions

**Notes:**
- Issue: `DesignLibrary` imports `Ship` from simulation layer (line 14)
- Root cause: `load_design()` method creates Ship objects but belongs in strategy layer
- Solution: Created `SimulationDesignLoader` in `game/simulation/services/design_loader.py`
- Implementation complete but IDE auto-reverts changes to design_library.py
- See plan.md Current State for detailed implementation notes and code patterns


---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
