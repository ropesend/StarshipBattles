# Phase 5: Final Audit and Verification

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-19 5`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Verify metrics improvement and document remaining patterns

---

## Tasks

### Task 5.1: Count Remaining Patterns [Simple]
**File:** N/A (measurement task)
**Tests:** N/A

- [ ] Run: `grep -r "hasattr(" --include="*.py" game/ | wc -l`
- [ ] Record count: _____ (target: <100)
- [ ] Run: `grep -r "getattr(" --include="*.py" game/ | wc -l`
- [ ] Record count: _____ (target: <150)
- [ ] If counts exceed targets, identify remaining clusters
- [ ] Document final counts in plan.md

**Notes:**

---

### Task 5.2: Document Remaining Patterns [Simple]
**File:** `decisions.md`
**Tests:** N/A

- [ ] List remaining hasattr patterns and justify each:
  - Lazy initialization patterns (app.py) - KEEP: different pattern
  - UI state checks - KEEP: appropriate use
  - Simulation component checks - OUT OF SCOPE: deferred
- [ ] Document any patterns that could be addressed in future phases
- [ ] Update decisions.md with final justifications

**Notes:**

---

### Task 5.3: Full Test Suite Verification [Simple]
**File:** N/A
**Tests:** `pytest tests/ -v`

- [ ] Run full test suite: `pytest tests/ -v`
- [ ] All tests must pass (except pre-existing failures noted in baseline):
  - Pre-existing: `test_ui_widgets.py` ImportError (Button removed)
  - Pre-existing: `test_intercept_integration` flaky
- [ ] Record test results: _____ passed, _____ failed, _____ errors

**Notes:**

---

### Task 5.4: Manual Application Verification [Simple]
**File:** N/A
**Tests:** Manual testing

- [ ] Launch game: `python -m game.app` (or appropriate command)
- [ ] Navigate strategy map
- [ ] Select StarSystem - verify info displays
- [ ] Select Star - verify info displays
- [ ] Select Planet - verify info displays
- [ ] Select Fleet - verify info displays
- [ ] Select WarpPoint - verify info displays
- [ ] Start combat - verify targeting works
- [ ] Verify: No TypeError or AttributeError in logs

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] hasattr count < 100 (record: _____)
- [ ] All tests passing (except documented pre-existing failures)
- [ ] Manual verification complete
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Verification section - check all boxes
- [ ] Project complete - archive if appropriate
