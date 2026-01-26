# Phase 2: Delete DataService

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-18 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Remove unused DataService class and its test file

---

## Tasks

### Task 2.1: Verify No Production Usage [Simple]
**File:** N/A
**Tests:** N/A

- [ ] Run grep to confirm no production imports:
  ```bash
  grep -r "DataService" --include="*.py" game/ --exclude-dir=__pycache__
  ```
- [ ] Expected output: Only `game/simulation/services/__init__.py` and `game/simulation/services/data_service.py`
- [ ] Verify: No other production files import DataService

**Notes:**

---

### Task 2.2: Remove DataService from exports [Simple]
**File:** `game/simulation/services/__init__.py`
**Tests:** `python -c "from game.simulation.services import ModifierService, VehicleDesignService; print('OK')"`

- [ ] Line 5: Remove `from .data_service import DataService`
- [ ] Line 13: Remove `'DataService'` from `__all__` list
- [ ] Verify: Services package imports without error

**Notes:**

---

### Task 2.3: Delete DataService file [Simple]
**File:** `game/simulation/services/data_service.py`
**Tests:** N/A

- [ ] Delete file: `game/simulation/services/data_service.py`
- [ ] Verify: File no longer exists

**Notes:**

---

### Task 2.4: Delete DataService test file [Simple]
**File:** `tests/unit/services/test_data_service.py`
**Tests:** `pytest tests/unit/services/ -v --ignore=tests/unit/services/test_data_service.py`

- [ ] Delete file: `tests/unit/services/test_data_service.py`
- [ ] Run remaining services tests
- [ ] All remaining services tests pass

**Notes:**

---

### Task 2.5: Verify Clean Import [Simple]
**File:** N/A
**Tests:** Various

- [ ] Run: `python -c "from game.simulation.services import *; print('OK')"`
- [ ] Run: `pytest tests/unit/services/ -v`
- [ ] All services work correctly without DataService

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] DataService file deleted
- [ ] DataService test file deleted
- [ ] DataService removed from exports
- [ ] Remaining services tests pass
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 3
