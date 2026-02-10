# Phase 3: Verification & Regression Guard

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-83 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Validate zero warnings remain and add enforcement to prevent regression

---

## Tasks

### Task 3.1: Run Full Test Suite and Fix Remaining Warnings [Simple]
**Tests:** `pytest tests/ -n 12 --tb=short`

- [ ] Run full test suite and check warning count
- [ ] If any label overflow warnings remain, abbreviate further in `data/stats_layout.json`
- [ ] If any deprecation warnings remain, add ai_factory to the offending test
- [ ] Target: 0 warnings (excluding the filtered pygame_gui cosmetic ones)

**Notes:**

---

### Task 3.2: Add DeprecationWarning Enforcement [Simple]
**File:** `pytest.ini`
**Tests:** `pytest tests/ -n 12`

- [ ] Add `error::DeprecationWarning` to the `filterwarnings` section (at the TOP, before ignore rules):
  ```ini
  filterwarnings =
      error::DeprecationWarning
      ignore:Clamping shadow_width:UserWarning
      ignore:Clamping border_width:UserWarning
      ignore:Finding font with id.*not already loaded:UserWarning
  ```
- [ ] Verify: Run `pytest tests/ -n 12` — all tests pass (no DeprecationWarnings converted to errors)

**Notes:** This makes any future DeprecationWarning a test failure, preventing regression.

---

### Task 3.3: Final Verification [Simple]
**Tests:** `pytest tests/ -n 12 --tb=short -q`

- [ ] Run final test suite: `pytest tests/ -n 12 --tb=short -q`
- [ ] Confirm: 7353+ passed, 0 warnings (filtered ones silenced)
- [ ] Confirm: No test failures from any changes made in Phases 1-2

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Final test suite shows 0 warnings
- [ ] DeprecationWarning enforcement is active in pytest.ini
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to `Complete`
- [ ] Update plan.md Completion Checklist
