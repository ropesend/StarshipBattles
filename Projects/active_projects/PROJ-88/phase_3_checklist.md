# Phase 3: Ship Validation Extraction [Simple]

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-88 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Extract validation methods from Ship into `ship_validator_helper.py`. Ship retains facade methods. Target: ~30 lines of logic moved, Ship reduced by ~20 lines net.

**File:** `game/simulation/entities/ship.py`
**New File:** `game/simulation/entities/ship_validator_helper.py`
**Tests:** `pytest tests/unit/entities/ tests/unit/builder/ -n 12`

---

## Tasks

### Task 3.1: Create ShipValidatorHelper Class [Simple]
**File:** `game/simulation/entities/ship_validator_helper.py`
- [ ] Create `ship_validator_helper.py` in `game/simulation/entities/`
- [ ] Define `ShipValidatorHelper` class that takes a ship reference in `__init__`
- [ ] Move `check_validity()` logic (ship.py lines 798-804): calls `recalculate_stats()`, runs `validate_design()`, sets `mass_limits_ok` flag
- [ ] Move `get_validation_warnings()` logic (ship.py lines 602-605): runs `validate_design()`, returns `result.warnings`
- [ ] Move `get_missing_requirements()` logic (ship.py lines 593-600): runs `validate_design()`, returns formatted error list
- [ ] Import `get_or_create_validator` from `ship_loader` (same import Ship currently uses)
- [ ] Add type hints and docstrings

**Notes:** The helper needs to call `ship.recalculate_stats()` in `check_validity()` and set `ship.mass_limits_ok`. This is a side effect on the ship -- the helper writes back to the ship reference.

---

### Task 3.2: Write Tests for ShipValidatorHelper [Simple]
**File:** `tests/unit/entities/test_ship_validator_helper.py`
- [ ] Create test file `tests/unit/entities/test_ship_validator_helper.py`
- [ ] Test `check_validity()` returns True for valid ship design
- [ ] Test `check_validity()` returns False for invalid ship (e.g., over mass budget)
- [ ] Test `check_validity()` sets `ship.mass_limits_ok` flag correctly
- [ ] Test `get_validation_warnings()` returns list of strings
- [ ] Test `get_missing_requirements()` returns empty list for valid ship
- [ ] Test `get_missing_requirements()` returns error strings for invalid ship
- [ ] Run tests: `pytest tests/unit/entities/test_ship_validator_helper.py -v`

**Notes:**

---

### Task 3.3: Wire Ship Facade Methods [Simple]
**File:** `game/simulation/entities/ship.py`
- [ ] Add lazy `_validator_helper` property to Ship (creates ShipValidatorHelper on first access)
- [ ] Replace `check_validity()` body with delegation to `self._validator_helper.check_validity()`
- [ ] Replace `get_validation_warnings()` body with `return self._validator_helper.get_validation_warnings()`
- [ ] Replace `get_missing_requirements()` body with `return self._validator_helper.get_missing_requirements()`
- [ ] Remove the `_format_ability_name()` method if confirmed unused in Phase 2 (or verify and remove here)

**Notes:**

---

### Task 3.4: Run Full Test Suite [Simple]
**Tests:** `pytest tests/ -n 12 --tb=short`
- [ ] Run full test suite: `pytest tests/ -n 12 --tb=short`
- [ ] Confirm all tests pass with zero new failures
- [ ] Verify Ship importers (136 files) are unaffected
- [ ] Record test count: _____ passed, _____ failed

**Notes:**

---

## Phase Completion Checklist
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
