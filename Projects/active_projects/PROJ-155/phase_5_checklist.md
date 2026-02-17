# Phase 5: Structural Improvements

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-155 5`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Relocate misplaced tests and rename directories for better organization.
**Priority:** Normal

---

## Tasks

### Task 5.1: Relocate test_fleet_report_filters.py [Simple]
**From:** `tests/unit/strategy/test_fleet_report_filters.py` (~931 lines)
**To:** `tests/unit/ui/screens/test_fleet_report_filters.py`
**Tests:** `pytest tests/unit/ui/screens/test_fleet_report_filters.py -v`

- [ ] Verify source file exists and imports from `game.ui.screens.fleet_report_filters`
- [ ] Verify no equivalent file exists at the destination
- [ ] Move file: `git mv tests/unit/strategy/test_fleet_report_filters.py tests/unit/ui/screens/test_fleet_report_filters.py`
- [ ] Run tests on the moved file to verify it still passes
- [ ] Run `pytest tests/ -n 12 -q` to verify no regressions

**Notes:** Use `git mv` so git tracks the rename. The file tests UI code but was placed in the strategy directory.

### Task 5.2: Rename refactor/ directory to modifiers/ [Simple]
**From:** `tests/unit/refactor/`
**To:** `tests/unit/modifiers/`
**Tests:** `pytest tests/unit/modifiers/ -q` (after rename)

- [ ] Verify all 23 files in refactor/ are legitimate modifier system tests
- [ ] Rename: `git mv tests/unit/refactor tests/unit/modifiers`
- [ ] Search codebase for any references to `tests/unit/refactor/` and update them
- [ ] Check conftest.py files, pytest.ini, and CLAUDE.md for path references
- [ ] Run tests on the renamed directory to verify all pass
- [ ] Run `pytest tests/ -n 12 -q` to verify no regressions

**Notes:** Use `git mv` for history tracking. All 23 files are permanent TDD tests for the modifier system; the "refactor" name was from the project that created them.

### Task 5.3: Clean up simulation/__init__.py exports [Simple]
**File:** `tests/unit/simulation/__init__.py`
**Tests:** `pytest tests/unit/simulation/ -n 12 -q`

- [ ] Read the file
- [ ] Remove any remaining exports referencing deleted files from Phase 1 (ComponentTestLogger, TestEventType, enable_test_logging, TestLogParser, LogEvent, etc.)
- [ ] If file becomes empty, delete it
- [ ] Run tests to verify no regressions

**Notes:** This may already be done as part of Task 1.1, but verify here.

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Run `pytest tests/ -n 12 -q` — verify no new failures vs baseline (12,790 passed, 143 pre-existing failures)
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to `Complete`
- [ ] Final summary: total lines removed, total files deleted, test count comparison
