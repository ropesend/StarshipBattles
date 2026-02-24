# Phase 1: Delete Ghost Code

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-180 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Remove the dead `get_column_visibility_changed()` method from empire_build_queue_sidebar.py

---

## Tasks

### Task 1.1: Delete ghost method from sidebar [Simple]
**File:** `game/ui/screens/empire_build_queue_sidebar.py`
**Tests:** `pytest tests/unit/ui/screens/test_empire_build_queue_window.py -x`

- [x] Delete the section comment at lines 261-263 (`# Column State Access (for window to rebuild headers)`)
- [x] Delete method `get_column_visibility_changed()` at lines 265-276
- [x] Run tests to verify no breakage

**Notes:** Ghost code deleted. Zero callers verified. 118 tests pass.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
