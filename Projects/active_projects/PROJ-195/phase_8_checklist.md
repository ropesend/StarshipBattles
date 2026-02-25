# Phase 8: Final Audit & Verification [Simple]

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-195 8`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Verify all singleton references accounted for, run full suite, add regression guard

---

## Tasks

### Task 8.1: Audit remaining references [Simple]
**Tests:** N/A — audit only

- [x] Run `grep -rn "RegistryManager.instance()" game/ tests/ --include="*.py"` and classify every remaining reference
- [x] Verify every remaining reference is in a legitimate location (composition root, singleton definition, test infrastructure, or singleton-specific tests)
- [x] Document any references NOT in the expected set

**Audit Results:**
- game/: 11 references (app.py: 2, registry.py: 9) - ALL LEGITIMATE
- tests/: 77 references - ALL LEGITIMATE (singleton tests, isolation fixtures, registry tests)

### Task 8.2: Run full test suite [Simple]
**Tests:** `pytest tests/ -n 12`

- [x] All 12,722 tests pass (baseline was 12,718 + 2 new regression guards + 2 test variation)
- [x] No new warnings introduced
- [x] No test isolation failures

### Task 8.3: Create regression guard [Simple]
**File:** `tests/regression/test_deprecated_code_removed.py`
**Tests:** `pytest tests/regression/test_deprecated_code_removed.py -v`

- [x] Add a new test class `TestSingletonUsageCount` with a test that counts `RegistryManager.instance()` references in `game/` and `tests/`
- [x] Store the expected count as a constant (determined from Task 8.1 audit)
- [x] Test asserts `actual_count <= EXPECTED_COUNT` — fails if count increases
- [x] Include a clear failure message: "RegistryManager.instance() count increased from {expected} to {actual}. If this is legitimate, update the expected count."
- [x] Run tests to verify guard works

**Notes:** Added TestSingletonUsageCount class with EXPECTED_GAME_COUNT=11, EXPECTED_TESTS_COUNT=77

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Full test suite passes (`pytest tests/ -n 12`)
- [x] Grep audit shows only legitimate singleton references
- [x] Regression guard installed and passing
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to indicate project complete
