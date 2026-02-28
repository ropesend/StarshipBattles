# Phase 3: Validation Module

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-36 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Centralize order validation in new module

---

## Tasks

### Task 3.1: Create validation module structure [Simple]
**Files:** `game/strategy/validation/` (NEW directory)
**Tests:** `pytest tests/unit/strategy/validation/`

- [x] Create directory `game/strategy/validation/`
- [x] Create `__init__.py`:
  ```python
  """
  Strategy Layer Validation Module

  PROJ-36: Centralized validation for fleet orders.

  Usage:
      from game.strategy.validation import ColonizeValidator
      result = ColonizeValidator.validate(galaxy, fleet, target_planet)
  """
  from .colonize_validator import ColonizeValidator

  __all__ = ['ColonizeValidator']
  ```
- [x] Create `base.py` with OrderValidationRule ABC (optional, for future expansion):
  ```python
  from abc import ABC, abstractmethod
  from game.core.validation import ValidationResult

  class OrderValidationRule(ABC):
      """Base class for order validation rules."""

      @abstractmethod
      def validate(self, fleet, galaxy, **kwargs) -> ValidationResult:
          """Validate an order for the given fleet."""
          pass
  ```
- [x] Verify: Module structure matches `game/simulation/validation/`

**Notes:** Created `game/strategy/validation/` with `__init__.py`, `base.py`, and `colonize_validator.py`.

---

### Task 3.2: Create ColonizeValidator [Simple]
**File:** `game/strategy/validation/colonize_validator.py` (NEW)
**Tests:** `pytest tests/unit/strategy/validation/test_colonize_validator.py`

- [x] Create file with module docstring
- [x] Add imports: `typing`, `game.core.validation`
- [x] Create `ColonizeValidator` class:
  ```python
  class ColonizeValidator:
      """Validates COLONIZE orders for fleets."""

      @staticmethod
      def validate(galaxy, fleet, target_planet) -> ValidationResult:
          """
          Validate if a fleet can colonize a specific planet.

          Args:
              galaxy: The Galaxy object
              fleet: The Fleet object attempting to colonize
              target_planet: The Planet object or None for 'Any'

          Returns:
              ValidationResult with error codes:
              - NO_CANDIDATES: No colonizable planets at location
              - ALREADY_OWNED: Target planet is already owned
              - WRONG_LOCATION: Target planet is not at fleet location
          """
  ```
- [x] Move validation logic from TurnEngine.validate_colonize_order (lines 142-182)
- [x] Preserve error codes: `NO_CANDIDATES`, `ALREADY_OWNED`, `WRONG_LOCATION`
- [x] Verify: Logic is identical to original

**Notes:** Created `game/strategy/validation/colonize_validator.py` (54 lines) with exact logic from TurnEngine.

---

### Task 3.3: Update callers to use new validator [Simple]
**Files:** Multiple files
**Tests:** `pytest tests/ -k colonize`

- [x] Update `TurnEngine.validate_colonize_order` (keep method, delegate to validator):
  ```python
  def validate_colonize_order(self, galaxy, fleet, target_planet) -> ValidationResult:
      from game.strategy.validation import ColonizeValidator
      return ColonizeValidator.validate(galaxy, fleet, target_planet)
  ```
- [x] Update `GameSession._handle_colonize_command` (line 269) - already calls TurnEngine, no change needed
- [x] Update `strategy_colonization.py` (line 88) - already calls TurnEngine, no change needed
- [x] Update `FleetOrderProcessor.process_colonize` to use ColonizeValidator:
  - Remove duplicate validation at lines 177-191
  - Call `ColonizeValidator.validate()` instead
- [x] Verify: All callers work correctly

**Notes:** TurnEngine.validate_colonize_order reduced from 41 lines to 15 lines (delegation only). FleetOrderProcessor.process_colonize now uses ColonizeValidator instead of duplicate logic. Removed unused `validation_result` import from TurnEngine.

---

### Task 3.4: Create validation tests [Simple]
**File:** `tests/unit/strategy/validation/test_colonize_validator.py` (NEW)
**Tests:** `pytest tests/unit/strategy/validation/test_colonize_validator.py`

- [x] Create directory `tests/unit/strategy/validation/`
- [x] Create `__init__.py` in test directory
- [x] Create test file with fixtures
- [x] Tests for ColonizeValidator:
  - `test_validate_no_fleet`
  - `test_validate_unowned_planet`
  - `test_validate_owned_planet_fails`
  - `test_validate_wrong_location`
  - `test_validate_any_planet_success`
  - `test_validate_any_no_candidates`
  - `test_validate_any_skips_owned_planets`
  - `test_multiple_planets_finds_valid_candidate`
  - `test_validate_specific_planet_not_at_location`
- [x] Add test: Fleet moves between validation and execution (stale validation)
- [x] Add test: Planet colonized by another empire between validation and execution
- [x] Update test imports to use ColonizeValidator
- [x] Verify: All tests pass

**Notes:** Created `tests/unit/strategy/validation/test_colonize_validator.py` with 14 tests. Kept existing TurnEngine colonize tests in `test_turn_engine.py` as they test the TurnEngine public API (which now delegates to ColonizeValidator).

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Run `pytest tests/unit/strategy/test_turn_engine.py` - passes (49 tests)
- [x] Run `pytest tests/unit/strategy/validation/` - passes (14 tests)
- [x] Run `pytest tests/integration/test_colonization.py` - passes (17 tests)
- [x] Validation is single source of truth (no duplicate logic)
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 4
