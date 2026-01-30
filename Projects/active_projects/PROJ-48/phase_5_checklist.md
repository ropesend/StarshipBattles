# Phase 5: Naming Convention Standardization

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-48 5`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Standardize all test file, class, and method naming.
**Issues Addressed:** TNC-001, TNC-006, TNC-007, TNC-011

---

## Tasks

### Task 5.1: Rename Non-Standard Test Files [Simple]
**Tests:** `pytest tests/ -v --tb=short`

#### Files to Rename (test_*.py pattern)
- [x] Rename `tests/repro_issues/repro_bug_05_deep.py` -> `test_bug_05_deep_repro.py`
  - Added @pytest.mark.xfail for expected bug reproduction failures
  - Verify: `pytest tests/repro_issues/test_bug_05_deep_repro.py -v` runs tests (2 xfailed)

#### Files to Move to scripts/ (not pytest tests)
- [x] Move `tests/unit/performance/repro_energy_stats.py` -> `scripts/repro_energy_stats.py`
- [x] Move `tests/unit/performance/repro_shield.py` -> `scripts/repro_shield.py`
- [x] Move `tests/reproduce_cycling.py` -> `scripts/reproduce_cycling.py`
- [x] Move `tests/unit/performance/verify_determinism_current.py` -> `scripts/verify_determinism_current.py`
- [x] Move `tests/unit/verify_themes.py` -> `scripts/verify_themes.py`

#### Files to Keep As-Is (with documentation)
- [x] Keep `tests/performance/benchmark_planet_list.py` (benchmark, not test)
  - Added docstring explaining this is a benchmark script

**Notes:** All non-test scripts moved to scripts/ directory using git mv.

---

### Task 5.2: Fix Non-Pytest-Compatible Files [Medium]
**Tests:** `pytest tests/unit/combat/ -v --tb=short`

#### test_lead.py
**File:** `tests/unit/combat/test_lead.py`

- [x] Read file to understand current structure
  - Was module-level code with print statements, no test class
- [x] Converted to pytest test class
  - Added `class TestLeadCalculation:` wrapper
  - Added 5 test methods for different scenarios
  - Added proper docstrings and type hints
- [x] Verify: `pytest tests/unit/combat/test_lead.py -v` - 5 passed

#### test_ccd.py
**File:** `tests/unit/combat/test_ccd.py`

- [x] Read file to understand current structure
  - Was module-level code with print statements, no test class
- [x] Converted to pytest test class
  - Added `class TestContinuousCollisionDetection:` wrapper
  - Added 7 test methods covering tunneling, miss, stationary, edge cases
  - Added proper docstrings and type hints
- [x] Verify: `pytest tests/unit/combat/test_ccd.py -v` - 7 passed

**Notes:** Both files were utility scripts used for debugging, now proper pytest tests.

---

### Task 5.3: Standardize Mock Naming [Simple]
**Tests:** `pytest tests/ -v --tb=short`

- [x] Search for mock class definitions
  - Found 60+ mock classes across test suite
  - All already follow `Mock*` prefix pattern
  - No `Stub*` or `Fake*` classes found
- [x] Ensure all mock classes use `Mock*` prefix consistently - already compliant
- [x] Document mock naming convention in `tests/README.md`
  - Added "Mock Classes" section under "Naming Conventions"

**Notes:** Mock naming was already standardized, documentation added.

---

### Task 5.4: Document Test Class Naming Convention [Simple]
**File:** `tests/README.md`
**Tests:** N/A - documentation only

- [x] Add test class naming guidelines
  - Added "Test Classes" section
- [x] Add test method naming guidelines
  - Added "Test Methods" section
- [x] Added "Test Files" section for completeness

**Notes:** Added full "Naming Conventions" section to tests/README.md.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] All test files follow `test_*.py` naming
- [x] Non-test scripts moved to `scripts/`
- [x] test_lead.py and test_ccd.py are pytest-compatible
- [x] Mock naming documented
- [x] Test class/method naming documented
- [x] Run `pytest tests/ -v --tb=short` - 5746 passed (pre-existing failures in repro/other tests excluded)
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 6
