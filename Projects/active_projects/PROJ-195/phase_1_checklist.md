# Phase 1: Production Code Cleanup [Simple]

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-195 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Fix the only remaining production code singleton leaks

---

## Tasks

### Task 1.1: Fix ship_loader.py singleton access [Simple]
**File:** `game/simulation/entities/ship_loader.py`
**Tests:** `pytest tests/unit/entities/ tests/unit/core/test_registry_manager_reload.py -v`

- [x] Line 34: Replace `val = RegistryManager.instance().get_validator()` with call to module-level `get_validator()` function from `game.core.registry`
- [x] Verify `get_validator()` exists in `game/core/registry.py` — if not, create a thin wrapper: `def get_validator(): return RegistryManager.instance().get_validator()`
- [x] Remove import `from game.core.registry import RegistryManager` on line 18 (if no longer needed)
- [x] Run tests to verify

**Notes:**
- Created new `get_validator()` module-level wrapper in `game/core/registry.py`
- Updated ship_loader.py to use `get_validator()` import instead of `RegistryManager`
- Fixed 4 tests in `test_ship_loader.py` that were patching `ship_loader.RegistryManager` - updated to patch `get_validator` instead
- Removed obsolete regression test `test_get_validator_global_removed` since PROJ-195 intentionally adds this function

### Task 1.2: Fix registry_loader.py docstring [Simple]
**File:** `game/simulation/services/registry_loader.py`
**Tests:** `pytest tests/unit/core/test_registry_manager_reload.py -v`

- [x] Lines 11-14: Update the docstring usage example to show the DI pattern instead of `manager = RegistryManager.instance()`
- [x] Run tests to verify

**Notes:**
- Updated docstring to show DI pattern: pass `registry_manager` as parameter

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] `pytest tests/ -n 12` passes (12720 passed, 1 skipped)
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
