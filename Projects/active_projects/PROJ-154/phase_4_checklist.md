# Phase 4: File Relocation

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-154 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Relocate misplaced test file from strategy/ to ui/screens/ (0 lines removed, 932 lines relocated)
**Priority:** Normal — standalone operation

---

## Tasks

### Task 4.1: STR-9 — Relocate test_fleet_report_filters.py to correct directory [Simple]
**Source:** `tests/unit/strategy/test_fleet_report_filters.py` (932 lines)
**Target:** `tests/unit/ui/screens/test_fleet_report_filters.py`
**Tests:** `pytest tests/unit/ui/screens/test_fleet_report_filters.py -v` then `pytest tests/ -n 12 --tb=short -q`

This file tests `game.ui.screens.fleet_report_filters` and `game.ui.screens.fleet_report_view_model` — UI layer code. It was incorrectly placed in the strategy test directory.

- [ ] `git mv tests/unit/strategy/test_fleet_report_filters.py tests/unit/ui/screens/test_fleet_report_filters.py`
- [ ] Verify no import path changes needed (the file imports from `game.ui.screens`, not from `game.strategy`)
- [ ] Run `pytest tests/unit/ui/screens/test_fleet_report_filters.py -v` — confirm all tests pass at new location
- [ ] Run `pytest tests/ -n 12 --tb=short -q` — full suite regression check (verify no NEW failures)

**Notes:**

---

## Final Verification

### Full Suite Check
- [ ] Run `pytest tests/ -n 12 --tb=short -q`
- [ ] Verify failure count is ≤145 (pre-existing, no new failures introduced)
- [ ] Run `git diff --stat` to confirm total lines changed

### Summary Verification
- [ ] Phase 1: ~1,082 lines deleted (8 files + 1 __init__ cleanup)
- [ ] Phase 2: ~1,040 lines deleted, ~175 lines migrated (4 source files deleted, 4 target files enriched)
- [ ] Phase 3: ~820 lines removed from 8 files (surgical edits)
- [ ] Phase 4: 932 lines relocated (1 file moved)
- [ ] Total: ~2,942 lines of dead code removed

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to mark project complete
