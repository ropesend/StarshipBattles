# Phase 1: Delete Ghost Code

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-180 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Remove the dead `get_column_visibility_changed()` method from empire_build_queue_sidebar.py

---

## Tasks

### Task 1.1: Delete ghost method from sidebar [Simple]
**File:** `game/ui/screens/empire_build_queue_sidebar.py`
**Tests:** `pytest tests/unit/ui/screens/test_empire_build_queue_window.py -x`

- [ ] Delete the section comment at lines 261-263 (`# Column State Access (for window to rebuild headers)`)
- [ ] Delete method `get_column_visibility_changed()` at lines 265-276
- [ ] Run tests to verify no breakage

**Notes:** [Filled during implementation]

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
