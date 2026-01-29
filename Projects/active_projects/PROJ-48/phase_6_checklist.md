# Phase 6: Directory Structure Reorganization

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-48 6`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Mirror source directory structure in tests.
**Issues Addressed:** TSR-008, TNC-002, TNC-004, TNC-005

---

## Tasks

### Task 6.1: Create Missing Test Directories [Simple]
**Tests:** N/A - structure only

- [ ] Create `tests/unit/assets/`
  - Add `__init__.py`
  - Add placeholder `README.md` explaining purpose
- [ ] Create `tests/unit/simulation/managers/`
  - Add `__init__.py`
- [ ] Create `tests/unit/simulation/services/`
  - Add `__init__.py`
- [ ] Create `tests/unit/research/data/`
  - Add `__init__.py`
- [ ] Create `tests/unit/research/systems/`
  - Add `__init__.py`
- [ ] Create `tests/unit/research/ui/`
  - Add `__init__.py`

**Notes:**

---

### Task 6.2: Consolidate Duplicate Directories [Medium]
**Tests:** `pytest tests/ -v --tb=short`

#### 6.2.1: Move tests/strategy/ -> tests/integration/strategy/
- [ ] Create `tests/integration/strategy/` directory
- [ ] Move all files from `tests/strategy/` to `tests/integration/strategy/`:
  ```bash
  # List files first
  ls tests/strategy/
  # Move each file
  ```
- [ ] Update imports in moved files if needed
- [ ] Create `conftest.py` if needed
- [ ] Verify: `pytest tests/integration/strategy/ -v`
- [ ] Delete empty `tests/strategy/` directory

#### 6.2.2: Move tests/ui/ -> tests/integration/ui/
- [ ] Create `tests/integration/ui/` directory
- [ ] Move all files from `tests/ui/` to `tests/integration/ui/`
- [ ] Update imports in moved files
- [ ] Verify: `pytest tests/integration/ui/ -v`
- [ ] Delete empty `tests/ui/` directory

#### 6.2.3: Move tests/test_framework/ -> tests/unit/test_framework/
- [ ] Move `tests/test_framework/` to `tests/unit/test_framework/`
- [ ] Update conftest imports if needed
- [ ] Verify: `pytest tests/unit/test_framework/ -v`

**Notes:**

---

### Task 6.3: Rename Duplicate Test File [Simple]
**File:** `tests/unit/simulation/test_logger.py`
**Tests:** `pytest tests/unit/simulation/ tests/unit/core/ -v --tb=short`

- [ ] Check for duplicate: `tests/unit/core/test_logger.py` exists?
- [ ] If both exist, rename simulation version:
  - `tests/unit/simulation/test_logger.py` -> `test_simulation_logger.py`
- [ ] Update any imports referencing the old name
- [ ] Verify: Both test files run correctly

**Notes:**

---

### Task 6.4: Update pytest.ini for New Structure [Simple]
**File:** `pytest.ini`
**Tests:** `pytest tests/ -v --tb=short`

- [ ] Review pytest.ini for hardcoded paths
- [ ] Update any paths affected by directory moves
- [ ] Verify: `pytest tests/` still discovers all tests

**Notes:**

---

### Task 6.5: Update Documentation for New Structure [Simple]
**Files:** `tests/README.md`
**Tests:** N/A - documentation only

- [ ] Update fixture hierarchy diagram in `tests/README.md`
- [ ] Update directory listing to reflect new structure
- [ ] Add notes about which directories mirror source structure

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Missing directories created with `__init__.py`
- [ ] `tests/strategy/` moved to `tests/integration/strategy/`
- [ ] `tests/ui/` moved to `tests/integration/ui/`
- [ ] `tests/test_framework/` moved to `tests/unit/test_framework/`
- [ ] No duplicate test filenames remain
- [ ] pytest.ini updated if needed
- [ ] Documentation updated
- [ ] Run `pytest tests/ -v --tb=short` - all tests pass
- [ ] Same total test count as baseline
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 7
