# Phase 5: Naming Convention Standardization

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-48 5`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Standardize all test file, class, and method naming.
**Issues Addressed:** TNC-001, TNC-006, TNC-007, TNC-011

---

## Tasks

### Task 5.1: Rename Non-Standard Test Files [Simple]
**Tests:** `pytest tests/ -v --tb=short`

#### Files to Rename (test_*.py pattern)
- [ ] Rename `tests/repro_issues/repro_bug_05_deep.py` -> `test_bug_05_deep_repro.py`
  - Update any imports referencing this file
  - Verify: `pytest tests/repro_issues/ -v`

#### Files to Move to scripts/ (not pytest tests)
- [ ] Move `tests/unit/performance/repro_energy_stats.py` -> `scripts/repro_energy_stats.py`
- [ ] Move `tests/unit/performance/repro_shield.py` -> `scripts/repro_shield.py`
- [ ] Move `tests/reproduce_cycling.py` -> `scripts/reproduce_cycling.py`
- [ ] Move `tests/unit/performance/verify_determinism_current.py` -> `scripts/verify_determinism_current.py`
- [ ] Move `tests/unit/verify_themes.py` -> `scripts/verify_themes.py`

#### Files to Keep As-Is (with documentation)
- [ ] Keep `tests/performance/benchmark_planet_list.py` (benchmark, not test)
  - Add comment at top explaining this is a benchmark script

**Notes:**

---

### Task 5.2: Fix Non-Pytest-Compatible Files [Medium]
**Tests:** `pytest tests/unit/combat/ -v --tb=short`

#### test_lead.py
**File:** `tests/unit/combat/test_lead.py`

- [ ] Read file to understand current structure
- [ ] If it contains only module-level code and helpers:
  - Convert to pytest test class
  - Add `class TestLeadCalculation:` wrapper
  - Convert functions to test methods `test_*`
- [ ] If it's a utility module, rename to `lead_helpers.py`
- [ ] Verify: `pytest tests/unit/combat/test_lead.py -v` runs tests

#### test_ccd.py
**File:** `tests/unit/combat/test_ccd.py`

- [ ] Read file to understand current structure
- [ ] If it contains only Vector class and check_collision function:
  - Either convert to test class with test methods
  - Or move to `tests/fixtures/` as helper utilities
- [ ] Verify: `pytest tests/unit/combat/test_ccd.py -v` runs tests

**Notes:**

---

### Task 5.3: Standardize Mock Naming [Simple]
**Tests:** `pytest tests/ -v --tb=short`

- [ ] Search for mock class definitions:
  ```bash
  grep -r "class Mock" tests/
  grep -r "class Stub" tests/
  grep -r "class Fake" tests/
  ```
- [ ] Ensure all mock classes use `Mock*` prefix consistently
- [ ] Document mock naming convention in `tests/README.md`:
  ```markdown
  ## Mock Naming Convention
  - Test doubles should be named `Mock<OriginalClassName>`
  - Example: `MockBattleEngine`, `MockShip`, `MockComponent`
  ```
- [ ] Verify: All mocks follow pattern

**Notes:**

---

### Task 5.4: Document Test Class Naming Convention [Simple]
**File:** `tests/README.md`
**Tests:** N/A - documentation only

- [ ] Add test class naming guidelines:
  ```markdown
  ## Test Class Naming
  - Name: `Test<SourceClassName>` or `Test<Feature>`
  - One test class per source class when possible
  - Example: `TestShip` for `Ship` class tests
  ```
- [ ] Add test method naming guidelines:
  ```markdown
  ## Test Method Naming
  - Pattern: `test_<what>_<condition>` or `test_<feature>_<expected_result>`
  - Example: `test_add_component_invalid_layer_raises_error`
  - Keep names descriptive but not excessively long
  ```

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] All test files follow `test_*.py` naming
- [ ] Non-test scripts moved to `scripts/`
- [ ] test_lead.py and test_ccd.py are pytest-compatible
- [ ] Mock naming documented
- [ ] Test class/method naming documented
- [ ] Run `pytest tests/ -v --tb=short` - all tests pass
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 6
