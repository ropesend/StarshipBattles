# Phase 1: Production Code Cleanup [Simple]

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-195 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Fix the only remaining production code singleton leaks

---

## Tasks

### Task 1.1: Fix ship_loader.py singleton access [Simple]
**File:** `game/simulation/entities/ship_loader.py`
**Tests:** `pytest tests/unit/entities/ tests/unit/core/test_registry_manager_reload.py -v`

- [ ] Line 34: Replace `val = RegistryManager.instance().get_validator()` with call to module-level `get_validator()` function from `game.core.registry`
- [ ] Verify `get_validator()` exists in `game/core/registry.py` — if not, create a thin wrapper: `def get_validator(): return RegistryManager.instance().get_validator()`
- [ ] Remove import `from game.core.registry import RegistryManager` on line 18 (if no longer needed)
- [ ] Run tests to verify

**Notes:**

### Task 1.2: Fix registry_loader.py docstring [Simple]
**File:** `game/simulation/services/registry_loader.py`
**Tests:** `pytest tests/unit/core/test_registry_manager_reload.py -v`

- [ ] Lines 11-14: Update the docstring usage example to show the DI pattern instead of `manager = RegistryManager.instance()`
- [ ] Run tests to verify

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `pytest tests/ --testmon` passes
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
