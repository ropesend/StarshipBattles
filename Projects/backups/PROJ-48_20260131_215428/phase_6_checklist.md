# Phase 6: Directory Structure Reorganization

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-48 6`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Mirror source directory structure in tests.
**Issues Addressed:** TSR-008, TNC-002, TNC-004, TNC-005

---

## Tasks

### Task 6.1: Create Missing Test Directories [Simple]
**Tests:** N/A - structure only

- [x] Create `tests/unit/assets/`
  - Add `__init__.py`
  - Add placeholder `README.md` explaining purpose
- [x] Create `tests/unit/simulation/managers/`
  - Add `__init__.py`
- [x] Create `tests/unit/simulation/services/`
  - Add `__init__.py`
- [x] Create `tests/unit/research/data/`
  - Add `__init__.py`
- [x] Create `tests/unit/research/systems/`
  - Add `__init__.py`
- [x] Create `tests/unit/research/ui/`
  - Add `__init__.py`

**Notes:** All 6 directories created with __init__.py. Added README.md to assets/ for documentation.

---

### Task 6.2: Consolidate Duplicate Directories [Medium]
**Tests:** `pytest tests/ -v --tb=short`

#### 6.2.1: Move tests/strategy/ -> tests/integration/strategy/
- [x] Create `tests/integration/strategy/` directory
- [x] Move all files from `tests/strategy/` to `tests/integration/strategy/`
- [x] Update imports in moved files if needed
- [x] Create `conftest.py` if needed (not needed - already existed)
- [x] Verify: `pytest tests/integration/strategy/ -v` - 249 passed
- [x] Delete empty `tests/strategy/` directory

#### 6.2.2: Move tests/ui/ -> tests/integration/ui/
- [x] Create `tests/integration/ui/` directory
- [x] Move all files from `tests/ui/` to `tests/integration/ui/`
- [x] Update imports in moved files (no changes needed)
- [x] Verify: `pytest tests/integration/ui/ -v` - 115 passed
- [x] Delete empty `tests/ui/` directory

#### 6.2.3: Move tests/test_framework/ -> tests/unit/test_framework/
- [x] Move `tests/test_framework/` to `tests/unit/test_framework/`
- [x] Update conftest imports if needed (updated 3 files with import path changes)
- [x] Verify: `pytest tests/unit/test_framework/ -v` - 137 passed

**Notes:** All 3 directories consolidated. Updated imports in:
- test_scenario_data_service.py
- test_metadata_management_service.py
- test_controller_execution.py

---

### Task 6.3: Rename Duplicate Test File [Simple]
**File:** `tests/unit/simulation/test_logger.py`
**Tests:** `pytest tests/unit/simulation/ tests/unit/core/ -v --tb=short`

- [x] Check for duplicate: `tests/unit/core/test_logger.py` exists?
- [x] NO RENAMING NEEDED: `tests/unit/simulation/test_logger.py` is NOT a test file
  - It's a utility module (ComponentTestLogger class)
  - Core logger tests are in `tests/unit/core/logger/` directory
  - No actual duplicate exists

**Notes:** File examined - contains ComponentTestLogger utility class, not tests. Not a duplicate.

---

### Task 6.4: Update pytest.ini for New Structure [Simple]
**File:** `pytest.ini`
**Tests:** `pytest tests/ -v --tb=short`

- [x] Review pytest.ini for hardcoded paths
- [x] Update any paths affected by directory moves (none needed)
- [x] Verify: `pytest tests/` still discovers all tests - 5809 collected

**Notes:** pytest.ini only uses `testpaths = tests` which works with new structure. No changes needed.

---

### Task 6.5: Update Documentation for New Structure [Simple]
**Files:** `tests/README.md`
**Tests:** N/A - documentation only

- [x] Update fixture hierarchy diagram in `tests/README.md`
- [x] Update directory listing to reflect new structure
- [x] Add notes about which directories mirror source structure

**Notes:** Updated directory tree to show:
- New unit/ subdirectories (assets/, simulation/managers/, etc.)
- Moved test_framework to unit/test_framework/
- integration/ subdirectories including strategy/ and ui/

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Missing directories created with `__init__.py`
- [x] `tests/strategy/` moved to `tests/integration/strategy/`
- [x] `tests/ui/` moved to `tests/integration/ui/`
- [x] `tests/test_framework/` moved to `tests/unit/test_framework/`
- [x] No duplicate test filenames remain (none existed)
- [x] pytest.ini updated if needed (no changes needed)
- [x] Documentation updated
- [x] Run `pytest tests/ -v --tb=short` - 5746 passed (same as baseline)
- [x] Same total test count as baseline - 5809 collected
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 7
