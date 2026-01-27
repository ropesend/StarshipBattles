# Phase 6: Deprecate Old Classes

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-35 6`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Clean up deprecated code

---

## Tasks

### Task 6.1: Deprecate FleetMovementSimulator [Simple]
**File:** `game/strategy/engine/fleet_movement.py`
**Tests:** `pytest tests/ -v`

- [ ] Add deprecation warning in __init__:
  ```python
  import warnings
  warnings.warn(
      "FleetMovementSimulator is deprecated. Use FleetNavigationService instead.",
      DeprecationWarning,
      stacklevel=2
  )
  ```
- [ ] Delegate all methods to FleetNavigationService
- [ ] Update module docstring to indicate deprecation

**Notes:**

---

### Task 6.2: Update Documentation [Simple]

- [ ] Update any docstrings referencing old classes
- [ ] Update design.md with final architecture notes
- [ ] Add completion notes to decisions.md

**Notes:**

---

### Task 6.3: Final Verification [Simple]
**Tests:** `pytest tests/`

- [ ] All tests pass
- [ ] Manual verification: path projection in UI matches turn execution
  - [ ] Test: Create fleet with MOVE order, verify UI path matches actual movement
  - [ ] Test: Create fleet with MOVE_TO_FLEET order, verify intercept works
  - [ ] Test: Create fleet with warp-capable path, verify warp segments correct

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] All tests pass: `pytest tests/`
- [ ] Manual verification complete
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to indicate PROJECT COMPLETE
- [ ] Move project folder to `Projects/completed_projects/`
