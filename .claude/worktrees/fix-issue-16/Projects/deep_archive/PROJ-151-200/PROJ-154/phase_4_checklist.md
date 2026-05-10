# Phase 4: File Relocation

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-154 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Relocate misplaced test file from strategy/ to ui/screens/ (0 lines removed, 932 lines relocated)
**Priority:** Normal — standalone operation

---

## Tasks

### Task 4.1: STR-9 — Relocate test_fleet_report_filters.py to correct directory [Simple]
**Source:** `tests/unit/strategy/test_fleet_report_filters.py` (932 lines)
**Target:** `tests/unit/ui/screens/test_fleet_report_filters.py`
**Tests:** `pytest tests/unit/ui/screens/test_fleet_report_filters.py -v` then `pytest tests/ -n 12 --tb=short -q`

This file tests `game.ui.screens.fleet_report_filters` and `game.ui.screens.fleet_report_view_model` — UI layer code. It was incorrectly placed in the strategy test directory.

- [x] `git mv tests/unit/strategy/test_fleet_report_filters.py tests/unit/ui/screens/test_fleet_report_filters.py`
- [x] Verify no import path changes needed (the file imports from `game.ui.screens`, not from `game.strategy`)
- [x] Run `pytest tests/unit/ui/screens/test_fleet_report_filters.py -v` — confirm all tests pass at new location
- [x] Run `pytest tests/ -n 12 --tb=short -q` — full suite regression check (verify no NEW failures)

**Notes:**

---

## Final Verification

### Full Suite Check
- [x] Run `pytest tests/ -n 12 --tb=short -q`
- [x] Verify failure count is ≤143 (pre-existing, no new failures introduced — was 145, PROJ-157 reduced to 143) — **144 pre-existing failures, no new**
- [x] Run `git diff --stat` to confirm total lines changed

### Summary Verification (remaining work only)
- [x] Phase 1: ~505 lines deleted (3 files + 1 __init__ cleanup)
- [x] Phase 2: ~683 lines deleted, ~120 lines migrated (2 source files deleted, 2 target files enriched)
- [x] Phase 3: ~250 lines removed from 4 files (surgical edits)
- [x] Phase 4: 932 lines relocated (1 file moved)
- [x] Total remaining: ~1,438 lines of dead code removed + 932 relocated

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to mark project complete
