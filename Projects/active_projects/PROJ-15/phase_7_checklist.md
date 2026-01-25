# Phase 7: Audit Fix [Simple]

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-15 7`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Pending
**Objective:** Fix test file missed during Phase 3 audit

---

## Audit Finding

**Issue ID:** A-01
**Severity:** Critical
**Found By:** Skeptical Reviewer audit on 2026-01-25

**Problem:** Phase 3 Task 3.2 removed the `'hex'` key from `PathSegment.to_dict()` but missed updating `tests/strategy/test_path_projection.py`. The test still expects `segments[0]['hex']` but the dict now only has `'end'`.

**Evidence:**
```
FAILED tests/strategy/test_path_projection.py::test_project_chained_orders - KeyError: 'hex'
```

---

## Tasks

### Task 7.1: Fix test_path_projection.py [Simple]
**File:** `tests/strategy/test_path_projection.py`
**Tests:** `pytest tests/strategy/test_path_projection.py -v`

- [ ] Update lines 81-84 in `test_project_chained_orders()`:
  - Change `segments[0]['hex']` to `segments[0]['end']`
  - Change `segments[1]['hex']` to `segments[1]['end']`
  - Change `segments[2]['hex']` to `segments[2]['end']`
  - Change `segments[3]['hex']` to `segments[3]['end']`
- [ ] Verify: Run `pytest tests/strategy/test_path_projection.py -v` - should pass

**Notes:**

---

### Task 7.2: Run Full Test Suite [Simple]
**Tests:** `pytest tests/ simulation_tests/ --tb=short`

- [ ] Run full test suite to confirm no other missed files
- [ ] Verify: All tests pass

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Run `pytest tests/strategy/test_path_projection.py -v` - passes
- [ ] Run `pytest tests/ -x --tb=short` - all pass
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to indicate ready for re-audit
