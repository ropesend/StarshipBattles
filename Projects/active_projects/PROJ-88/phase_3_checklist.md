# Phase 3: Ship Validation Extraction [Simple]

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-88 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Extract validation methods from Ship into `ship_validator_helper.py`. Ship retains facade methods. Target: ~30 lines of logic moved, Ship reduced by ~20 lines net.

**File:** `game/simulation/entities/ship.py`
**New File:** `game/simulation/entities/ship_validator_helper.py`
**Tests:** `pytest tests/unit/entities/ tests/unit/builder/ -n 12`

---

## Tasks

### Task 3.1: Create ShipValidatorHelper Class [Simple]
**File:** `game/simulation/entities/ship_validator_helper.py`
- [x] Create `ship_validator_helper.py` in `game/simulation/entities/`
- [x] Define `ShipValidatorHelper` class that takes a ship reference in `__init__`
- [x] Move `check_validity()` logic (ship.py lines 798-804): calls `recalculate_stats()`, runs `validate_design()`, sets `mass_limits_ok` flag
- [x] Move `get_validation_warnings()` logic (ship.py lines 602-605): runs `validate_design()`, returns `result.warnings`
- [x] Move `get_missing_requirements()` logic (ship.py lines 593-600): runs `validate_design()`, returns formatted error list
- [x] Import `get_or_create_validator` from `ship_loader` (same import Ship currently uses)
- [x] Add type hints and docstrings

**Notes:** Created 67-line helper class with full type hints and docstrings.

---

### Task 3.2: Write Tests for ShipValidatorHelper [Simple]
**File:** `tests/unit/entities/test_ship_validator_helper.py`
- [x] Create test file `tests/unit/entities/test_ship_validator_helper.py`
- [x] Test `check_validity()` returns True for valid ship design
- [x] Test `check_validity()` returns False for invalid ship (e.g., over mass budget)
- [x] Test `check_validity()` sets `ship.mass_limits_ok` flag correctly
- [x] Test `get_validation_warnings()` returns list of strings
- [x] Test `get_missing_requirements()` returns empty list for valid ship
- [x] Test `get_missing_requirements()` returns error strings for invalid ship
- [x] Run tests: `pytest tests/unit/entities/test_ship_validator_helper.py -v`

**Notes:** 9 tests written and passing.

---

### Task 3.3: Wire Ship Facade Methods [Simple]
**File:** `game/simulation/entities/ship.py`
- [x] Add lazy `_validator_helper` property to Ship (creates ShipValidatorHelper on first access)
- [x] Replace `check_validity()` body with delegation to `self._validator_helper.check_validity()`
- [x] Replace `get_validation_warnings()` body with `return self._validator_helper.get_validation_warnings()`
- [x] Replace `get_missing_requirements()` body with `return self._validator_helper.get_missing_requirements()`
- [N/A] Remove the `_format_ability_name()` method if confirmed unused in Phase 2 (or verify and remove here)

**Notes:** Used `self.validator_helper` property (public) for delegation. _format_ability_name was removed in Phase 2.

---

### Task 3.4: Run Full Test Suite [Simple]
**Tests:** `pytest tests/ -n 12 --tb=short`
- [x] Run full test suite: `pytest tests/ -n 12 --tb=short`
- [x] Confirm all tests pass with zero new failures
- [x] Verify Ship importers (136 files) are unaffected
- [x] Record test count: 7512 passed, 0 failed

**Notes:** +9 tests from new test file.

---

## Phase Completion Checklist
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
