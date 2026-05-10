# Phase 3: Delete Old Tests and Verify

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-159 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Remove old failing tests, verify full suite passes

---

## Tasks

### Task 3.1: Delete old test file [Simple]
**File:** `tests/unit/strategy/validation/test_transfer_validator.py` (DELETE)
**Tests:** `pytest tests/ -k transfer -v`

- [ ] Delete file: `tests/unit/strategy/validation/test_transfer_validator.py`
- [ ] Check if `tests/unit/strategy/validation/` directory is empty
- [ ] If empty, delete the directory
- [ ] Run `pytest tests/ -k transfer -v` to verify new tests are found
- [ ] Verify old tests no longer appear in test collection

**Notes:**

---

### Task 3.2: Run full test suite verification [Simple]
**File:** N/A
**Tests:** `pytest tests/ -n 12`

- [ ] Run full test suite: `pytest tests/ -n 12`
- [ ] Verify no new failures introduced
- [ ] Previous baseline: 6246 tests, 20 failing (transfer validator)
- [ ] Expected result: All tests pass (20 failing tests replaced with 12 passing)
- [ ] Document final test count in notes below

**Notes:**

---

### Task 3.3: Final cleanup [Simple]
**File:** N/A
**Tests:** N/A

- [ ] Update `plan.md` Current State to indicate project complete
- [ ] Update all phase statuses to Complete
- [ ] Run `pytest tests/integration/strategy/transfer/ -v` one final time
- [ ] Commit changes with message: `[PROJ-159] Rewrite transfer validator tests as integration tests`

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Old `test_transfer_validator.py` deleted
- [ ] Full test suite passes: `pytest tests/ -n 12`
- [ ] No regressions introduced
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table rows to `Complete`
- [ ] Update plan.md Current State to `Project Complete`
