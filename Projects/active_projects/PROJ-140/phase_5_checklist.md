# Phase 5: Full Regression + Cleanup

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-140 5`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Full test suite regression, verify all fixes work together, update project files.

---

## Tasks

### Task 5.1: Full Test Suite Regression [Simple]
**Tests:** `pytest tests/ -n 12`

- [ ] Run full test suite: `pytest tests/ -n 12`
- [ ] All tests pass (baseline was 11852 passed, 1 pre-existing import error)
- [ ] No new warnings introduced

**Notes:**

### Task 5.2: Manual Code Review [Simple]

- [ ] Verify: Every code path that creates a colony validates pod match (grep for `empire.add_colony`)
- [ ] Verify: Every successful colonization removes the colony ship (check `process_colonize()`)
- [ ] Verify: UI prevents targeting planets without matching pods (both `on_colonize_click` and `handle_colonize_designation`)
- [ ] Verify: Mission command handler rejects mismatched pods before queuing

### Task 5.3: Update Project Files [Simple]

- [ ] Update `PROJ-140/plan.md` Current State to "Complete"
- [ ] Update `Projects/projects_index.md` status to "Complete"

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to "Complete"
