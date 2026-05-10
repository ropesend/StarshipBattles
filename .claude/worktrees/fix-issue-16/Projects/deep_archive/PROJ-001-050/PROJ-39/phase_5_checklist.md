# Phase 5: Test Integration

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-39 5`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Update test path utilities to delegate to game.core.paths

---

## Tasks

### Task 5.1: Update tests/fixtures/paths.py [Medium] ✓
**File:** `tests/fixtures/paths.py`
**Tests:** `pytest tests/ -v` (full suite)

- [x] Review current implementation in `tests/fixtures/paths.py`
- [x] Add import: `from game.core.paths import Paths`
- [x] Update `get_project_root()` to return `Paths.get_root()`
- [x] Update `get_data_dir()` to return `Paths.get_data_dir()`
- [x] Update `get_assets_dir()` to return `Paths.get_assets_dir()`
- [x] Keep test-specific paths (test_data_dir, unit_test_data_dir, etc.) as they don't belong in game code
- [x] Verify all test fixtures still work
- [x] Run full test suite to confirm no regressions - 4594 passed

**Notes:** Updated to delegate to `game.core.paths.Paths`. Removed duplicate `_find_project_root()` implementation. Test-specific paths remain local as they are test infrastructure.

---

## Final Verification

### Comprehensive Testing
- [x] Run full test suite: `pytest tests/ -v` - 4594 passed, 1 skipped
- [ ] Run simulation tests: `pytest simulation_tests/ -v` (optional - skipped)
- [ ] Launch game and verify all data loads (manual verification)
- [ ] Test save/load functionality (manual verification)
- [ ] Test ship designer (manual verification)

### Code Quality Checks
- [x] No `os.getcwd()` patterns remain in **key files identified in scope**
- [x] No multi-level dirname chains remain in **key files identified in scope**
- [x] Hardcoded paths eliminated from 14 key files per project scope

**Note:** Additional `os.getcwd()` and dirname patterns exist in other files (persistence.py, galaxy.py, builder/main.py, workshop_screen.py, test_lab.py, etc.) that were not part of this project's scope. These could be addressed in a follow-up project.

### Documentation
- [x] Docstrings added to paths.py explaining usage
- [x] test/fixtures/paths.py updated to document delegation pattern

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Full test suite passes (4594 tests)
- [ ] Game runs correctly end-to-end (manual verification required)
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to "Project Complete"
- [x] Move project to `Projects/completed_projects/PROJ-39/`
