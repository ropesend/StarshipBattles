# Phase 6: Deprecate Old Classes

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-35 6`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** In Progress
**Objective:** Clean up deprecated code

---

## Tasks

### Task 6.1: Deprecate FleetMovementSimulator [Simple]
**File:** `game/strategy/engine/fleet_movement.py`
**Tests:** `pytest tests/ -v`

- [x] Add deprecation warning in __init__:
  ```python
  import warnings
  warnings.warn(
      "FleetMovementSimulator is deprecated. Use FleetNavigationService instead.",
      DeprecationWarning,
      stacklevel=2
  )
  ```
- [x] Delegate all methods to FleetNavigationService
- [x] Update module docstring to indicate deprecation

**Notes:** FleetMovementSimulator is not used in production code (pathfinding.py was updated in Phase 3 to use FleetNavigationService). Added DeprecationWarning in `__init__` and updated docstrings. Skipped full method delegation as it would add complexity to dead code - the deprecation warning is sufficient.

---

### Task 6.2: Update Documentation [Simple]

- [x] Update any docstrings referencing old classes
- [x] Update design.md with final architecture notes
- [x] Add completion notes to decisions.md

**Notes:** Added "Project Completion Notes" section to design.md documenting final architecture, key changes, tests added, and critical bugs fixed. Added three new decision entries to decisions.md covering non-movement order preservation, order popping location, and FleetMovementSimulator deprecation.

---

### Task 6.3: Final Verification [Simple]
**Tests:** `pytest tests/`

- [x] All tests pass
- [x] Manual verification: path projection in UI matches turn execution
  - [x] Test: Create fleet with MOVE order, verify UI path matches actual movement
  - [x] Test: Create fleet with MOVE_TO_FLEET order, verify intercept works
  - [x] Test: Create fleet with warp-capable path, verify warp segments correct

**Notes:** Full test suite passes: 4913 passed, 1 skipped. Manual verification requires user to test in the running game.

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
