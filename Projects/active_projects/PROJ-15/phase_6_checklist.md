# Phase 6: Test Directory Rename [Medium]

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-15 6`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Rename test directory from `tests/unit/builder/` to `tests/unit/workshop/` and rename test files

---

## Tasks

### Task 6.1: Merge Test Directories [Medium]
**Source:** `tests/unit/builder/`
**Target:** `tests/unit/workshop/` (already exists with 3 files)
**Tests:** `pytest tests/unit/workshop/ -v`

**Existing files in `tests/unit/workshop/`:**
- `test_workshop_context.py`
- `test_workshop_data_loader.py`
- `test_workshop_viewmodel.py`

**Files to move from `tests/unit/builder/`:**
- [x] `test_builder_data_loader.py` → Deleted (duplicate of workshop version)
- [x] `test_builder_viewmodel.py` → Deleted (duplicate of workshop version)
- [x] Move other files directly (no conflicts)

**Steps:**
- [x] Check for duplicate test coverage between builder and workshop test files
- [x] For `test_builder_data_loader.py`:
  - Deleted - identical tests exist in `test_workshop_data_loader.py`
- [x] For `test_builder_viewmodel.py`:
  - Deleted - identical tests exist in `test_workshop_viewmodel.py`
- [x] Move remaining files from `tests/unit/builder/` to `tests/unit/workshop/`
- [x] Delete empty `tests/unit/builder/` directory
- [x] Verify: Run tests - 123 passed

**Notes:** Both builder_viewmodel.py and builder_data_loader.py were exact duplicates of the workshop versions (identical test functions)

---

### Task 6.2: Rename Test Files [Simple]
**Directory:** `tests/unit/workshop/`
**Tests:** `pytest tests/unit/workshop/ -v`

Rename files with "builder" prefix to "workshop":
- [x] `test_builder_warning_logic.py` → `test_workshop_warning_logic.py`
- [x] `test_builder_structure_features.py` → `test_workshop_structure_features.py`
- [x] `test_builder_io_integration.py` → `test_workshop_io_integration.py`
- [x] `test_builder_improvements.py` → `test_workshop_improvements.py`
- [x] `test_builder_drag_drop_real.py` → `test_workshop_drag_drop_real.py`
- [x] `test_builder_interaction.py` → `test_workshop_interaction.py`
- [x] `test_builder_logic.py` → `test_workshop_logic.py`
- [x] `test_builder_ui_sync.py` → `test_workshop_ui_sync.py`
- [x] `test_builder_validation.py` → `test_workshop_validation.py`
- [x] `test_selection_refinements.py` → Keep as-is (no "builder" prefix)
- [x] `test_multi_selection_logic.py` → Keep as-is (no "builder" prefix)

- [x] Verify: Run tests - 123 passed

**Notes:**

---

### Task 6.3: Update Any Internal References [Simple]
**Tests:** `pytest tests/unit/workshop/ -v`

- [x] Check for any `conftest.py` files that reference `tests/unit/builder/` - None found
- [x] Update any pytest markers or configuration that references builder directory - N/A
- [x] Search for hardcoded paths in test files referencing `tests/unit/builder/` - None
- [x] Verify: Run full test suite - 123 workshop tests pass

**Notes:** No internal references needed updating

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] `tests/unit/builder/` directory no longer exists
- [x] All test files renamed from "builder" to "workshop"
- [x] Run `pytest tests/unit/workshop/ -v` - 123 passed
- [x] Run `pytest tests/ -v --tb=short` - full suite passes
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to indicate project complete
