# Phase 3: Validation Module

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-36 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Centralize order validation in new module

---

## Tasks

### Task 3.1: Create validation module structure [Simple]
**Files:** `game/strategy/validation/` (NEW directory)
**Tests:** `pytest tests/unit/strategy/validation/`

- [ ] Create directory `game/strategy/validation/`
- [ ] Create `__init__.py`:
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
- [ ] Create `base.py` with OrderValidationRule ABC (optional, for future expansion):
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
- [ ] Verify: Module structure matches `game/simulation/validation/`

**Notes:**

---

### Task 3.2: Create ColonizeValidator [Simple]
**File:** `game/strategy/validation/colonize_validator.py` (NEW)
**Tests:** `pytest tests/unit/strategy/validation/test_colonize_validator.py`

- [ ] Create file with module docstring
- [ ] Add imports: `typing`, `game.core.validation`
- [ ] Create `ColonizeValidator` class:
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
- [ ] Move validation logic from TurnEngine.validate_colonize_order (lines 142-182)
- [ ] Preserve error codes: `NO_CANDIDATES`, `ALREADY_OWNED`, `WRONG_LOCATION`
- [ ] Verify: Logic is identical to original

**Notes:**

---

### Task 3.3: Update callers to use new validator [Simple]
**Files:** Multiple files
**Tests:** `pytest tests/ -k colonize`

- [ ] Update `TurnEngine.validate_colonize_order` (keep method, delegate to validator):
  ```python
  def validate_colonize_order(self, galaxy, fleet, target_planet) -> ValidationResult:
      from game.strategy.validation import ColonizeValidator
      return ColonizeValidator.validate(galaxy, fleet, target_planet)
  ```
- [ ] Update `GameSession._handle_colonize_command` (line 269) - already calls TurnEngine, no change needed
- [ ] Update `strategy_colonization.py` (line 88) - already calls TurnEngine, no change needed
- [ ] Update `FleetOrderProcessor.process_colonize` to use ColonizeValidator:
  - Remove duplicate validation at lines 177-191
  - Call `ColonizeValidator.validate()` instead
- [ ] Verify: All callers work correctly

**Notes:**

---

### Task 3.4: Create validation tests [Simple]
**File:** `tests/unit/strategy/validation/test_colonize_validator.py` (NEW)
**Tests:** `pytest tests/unit/strategy/validation/test_colonize_validator.py`

- [ ] Create directory `tests/unit/strategy/validation/`
- [ ] Create `__init__.py` in test directory
- [ ] Create test file with fixtures
- [ ] Move colonize validation tests from test_turn_engine.py:
  - `test_validate_colonize_no_fleet`
  - `test_validate_colonize_no_planets`
  - `test_validate_colonize_any_finds_planet`
  - `test_validate_colonize_specific_planet`
  - `test_validate_colonize_already_owned`
  - `test_validate_colonize_wrong_location`
  - `test_validate_colonize_error_codes`
- [ ] Add test: Fleet moves between validation and execution (stale validation)
- [ ] Add test: Planet colonized by another empire between validation and execution
- [ ] Update test imports to use ColonizeValidator
- [ ] Verify: All tests pass

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Run `pytest tests/unit/strategy/test_turn_engine.py` - passes
- [ ] Run `pytest tests/unit/strategy/validation/` - passes
- [ ] Run `pytest tests/integration/test_colonization.py` - passes
- [ ] Validation is single source of truth (no duplicate logic)
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 4
