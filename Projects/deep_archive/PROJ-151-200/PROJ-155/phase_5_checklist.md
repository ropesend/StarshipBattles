# Phase 5: Structural Improvements

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-155 5`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Relocate misplaced tests and rename directories for better organization.
**Priority:** Normal

---

## PROJ-154 / PROJ-157 Overlap Summary

PROJ-154 completed Task 5.1 (relocated test_fleet_report_filters.py from strategy/ to ui/screens/).
PROJ-157 completed Task 5.3 (cleaned simulation/__init__.py exports).
Only Task 5.2 (rename refactor/ → modifiers/) remains.

---

## Tasks

### Task 5.1: Relocate test_fleet_report_filters.py [Simple] — DONE by PROJ-154

- [x] Moved via `git mv` from `tests/unit/strategy/` to `tests/unit/ui/screens/` — PROJ-154
- [x] Tests verified at new location — PROJ-154
- [x] Full suite regression check passed — PROJ-154

### Task 5.2: Rename refactor/ directory to modifiers/ [Simple] — REMAINING
**From:** `tests/unit/refactor/` (23 test files)
**To:** `tests/unit/modifiers/`
**Tests:** `pytest tests/unit/modifiers/ -q` (after rename)

- [x] Verify all 23 files in refactor/ are legitimate modifier system tests — confirmed
- [x] Rename: `git mv tests/unit/refactor tests/unit/modifiers` — done
- [x] Search codebase for any references to `tests/unit/refactor/` and update them — only VSCodeCounter (auto-gen), no code refs
- [x] Check conftest.py files, pytest.ini, and CLAUDE.md for path references — none found
- [x] Run tests on the renamed directory to verify all pass — 253 passed
- [x] Run `pytest tests/ -n 12 -q` to verify no regressions — 11984 passed

**Notes:** Use `git mv` for history tracking. All 23 files are permanent TDD tests for the modifier system; the "refactor" name was from the project that created them.

### Task 5.3: Clean up simulation/__init__.py exports [Simple] — DONE by PROJ-157

- [x] Dead exports removed, file contains only docstring — PROJ-157 Phase 1

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Run `pytest tests/ -n 12 -q` — verify no new failures vs baseline
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to `Complete`
- [ ] Final summary: total lines removed, total files deleted, test count comparison
