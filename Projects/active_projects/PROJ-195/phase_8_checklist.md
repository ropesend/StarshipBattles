# Phase 8: Final Audit & Verification [Simple]

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-195 8`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Verify all singleton references accounted for, run full suite, add regression guard

---

## Tasks

### Task 8.1: Audit remaining references [Simple]
**Tests:** N/A — audit only

- [ ] Run `grep -rn "RegistryManager.instance()" game/ tests/ --include="*.py"` and classify every remaining reference
- [ ] Verify every remaining reference is in a legitimate location (composition root, singleton definition, test infrastructure, or singleton-specific tests)
- [ ] Document any references NOT in the expected set

### Task 8.2: Run full test suite [Simple]
**Tests:** `pytest tests/ -n 12`

- [ ] All 12,718 tests pass
- [ ] No new warnings introduced
- [ ] No test isolation failures

### Task 8.3: Create regression guard [Simple]
**File:** `tests/regression/test_deprecated_code_removed.py`
**Tests:** `pytest tests/regression/test_deprecated_code_removed.py -v`

- [ ] Add a new test class `TestSingletonUsageCount` with a test that counts `RegistryManager.instance()` references in `game/` and `tests/`
- [ ] Store the expected count as a constant (determined from Task 8.1 audit)
- [ ] Test asserts `actual_count <= EXPECTED_COUNT` — fails if count increases
- [ ] Include a clear failure message: "RegistryManager.instance() count increased from {expected} to {actual}. If this is legitimate, update the expected count."
- [ ] Run tests to verify guard works

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Full test suite passes (`pytest tests/ -n 12`)
- [ ] Grep audit shows only legitimate singleton references
- [ ] Regression guard installed and passing
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to indicate project complete
