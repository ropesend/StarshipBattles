# Phase 3: Fix Log Level Misuses

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-183 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Fix log level misuses where errors/failures are logged at INFO level instead of WARNING

---

## Tasks

### Task 3.1: Fix validation_manager.py [Simple]
**File:** `game/ui/screens/test_lab/validation_manager.py`
**Tests:** `pytest tests/unit/ui/ -k validation --tb=short`

- [ ] At line 103, change `logger.info(f"  {test_id}: Validation error - {e}")` to `logger.warning(f"  {test_id}: Validation error - {e}")`

**Notes:**

### Task 3.2: Fix galaxy_test/system_mode.py [Simple]
**File:** `game/ui/screens/galaxy_test/system_mode.py`
**Tests:** `pytest tests/unit/ui/ -k galaxy --tb=short`

- [ ] At line 198, change `logger.info(f"Failed to load blueprints: {e}")` to `logger.warning(f"Failed to load blueprints: {e}")`
- [ ] At line 238, change `logger.info(f"Failed to load blueprint '{self.selected_blueprint}': {e}")` to `logger.warning(f"Failed to load blueprint '{self.selected_blueprint}': {e}")`

**Notes:**

### Task 3.3: Run Full Test Suite [Simple]
**Tests:** `pytest tests/ -n 12`

- [ ] Run full test suite to verify zero regressions
- [ ] Confirm baseline: 12338 passed, 1 skipped

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Full test suite passes: `pytest tests/ -n 12`
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to "Project Complete"
