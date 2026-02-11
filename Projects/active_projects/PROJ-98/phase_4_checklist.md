# Phase 4: Final Verification [Simple]

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-98 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Final verification that all 4 issues are resolved and no regressions exist.

---

## Tasks

### Task 4.1: Full test suite [Simple]
**Tests:** `pytest tests/ -n 12`

- [ ] All 7595+ tests pass with 0 failures
- [ ] No new warnings introduced

**Notes:**

### Task 4.2: Issue verification checklist [Simple]

- [ ] Issue 1 (Column toggles): Verify column toggle buttons in sidebar change column visibility (fixed in Phase 1 - event handling)
- [ ] Issue 2 (Sorting/reordering): Verify column headers have [<] [Title ^/v] [>] buttons that sort and reorder (fixed in Phase 3 - ColumnManager)
- [ ] Issue 3 (Broken filters): Verify filter toggle buttons change filter state and update the list (fixed in Phase 1 - same root cause)
- [ ] Issue 4 (Resource columns): Verify 10 resource columns appear showing construction cost data (fixed in Phase 2)

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to "Complete - Ready for Audit"
