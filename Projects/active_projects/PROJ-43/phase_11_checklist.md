# Phase 11: Validation Consolidation (AR-10)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-43 11`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Unify validation logic into core layer

---

## Prerequisites
- [ ] Core phases complete

## Background

**Problem (AR-10):**
- Validation rules scattered across simulation, UI, and strategy layers:
  - `game/simulation/systems/validator.py` - Ship/component validation
  - `game/ui/screens/race_validator.py` - Race setup validation
  - `game/strategy/validation/base.py` - Strategy validation
- Consistency issues: UI might allow invalid state that simulation rejects
- No unified validation interface

**Target:** Create unified ValidationEngine in core layer with domain-specific rules in their layers.

---

## Tasks

### Task 11.1: Audit Existing Validation [Simple]
**Files:** All validation files
**Tests:** N/A (analysis)

- [ ] Review `game/simulation/systems/validator.py`:
  - What rules does it enforce?
  - What interface does it use?
- [ ] Review `game/ui/screens/race_validator.py`:
  - What rules does it enforce?
  - What interface does it use?
- [ ] Review `game/strategy/validation/base.py`:
  - What rules does it enforce?
  - What interface does it use?
- [ ] Document in findings/phase_11_audit.md
- [ ] Identify common patterns

**Notes:**

---

### Task 11.2: Create Core Validation Interface [Medium]
**File:** `game/core/validation_engine.py` (NEW)
**Tests:** `pytest tests/unit/core/test_validation_engine.py`

- [ ] Create `IValidationRule` protocol:
  ```python
  class IValidationRule(Protocol):
      def validate(self, context: Any) -> ValidationResult:
          ...
  ```
- [ ] Create `ValidationEngine` class:
  - `register_rule(rule: IValidationRule)`
  - `validate(context) -> ValidationResult`
  - `validate_all(contexts) -> List[ValidationResult]`
- [ ] Use existing `ValidationResult` from `game/core/validation.py`
- [ ] Create unit tests

**Notes:**

---

### Task 11.3: Migrate Simulation Validation Rules [Medium]
**File:** `game/simulation/systems/validator.py`
**Tests:** `pytest tests/unit/simulation/systems/test_validator.py`

- [ ] Create rule classes implementing IValidationRule:
  - ComponentAdditionRule
  - ComponentRemovalRule
  - ShipClassConstraintRule
  - etc.
- [ ] Update validator to use ValidationEngine internally
- [ ] Maintain backward-compatible interface
- [ ] Run validation tests

**Notes:**

---

### Task 11.4: Migrate UI Validation Rules [Medium]
**File:** `game/ui/screens/race_validator.py`
**Tests:** `pytest tests/unit/ui/screens/test_race_validator.py`

- [ ] Create rule classes implementing IValidationRule:
  - RaceNameRule
  - RacePointsRule
  - etc.
- [ ] Update race_validator to use ValidationEngine internally
- [ ] Maintain backward-compatible interface
- [ ] Run validation tests

**Notes:**

---

### Task 11.5: Migrate Strategy Validation Rules [Medium]
**File:** `game/strategy/validation/base.py`
**Tests:** `pytest tests/unit/strategy/validation/`

- [ ] Create rule classes implementing IValidationRule:
  - FleetOrderRule
  - ColonizationRule
  - etc.
- [ ] Update strategy validation to use ValidationEngine internally
- [ ] Maintain backward-compatible interface
- [ ] Run validation tests

**Notes:**

---

### Task 11.6: Add Cross-Layer Validation [Simple]
**File:** `game/core/validation_engine.py`
**Tests:** `pytest tests/unit/core/test_validation_engine.py`

- [ ] Add ability to run validation from multiple layers
- [ ] Create composite validator that combines rules
- [ ] Document usage pattern
- [ ] Add tests for cross-layer validation

**Notes:**

---

### Task 11.7: Update ValidationResult Usage [Simple]
**Files:** All files using validation
**Tests:** Full test suite

- [ ] Ensure all validators return `ValidationResult`
- [ ] Standardize error message format
- [ ] Standardize warning message format
- [ ] Verify consistency

**Notes:**

---

### Task 11.8: Integration Testing [Simple]
**Tests:** `pytest tests/integration/`

- [ ] Run integration tests for ship validation
- [ ] Run integration tests for race validation
- [ ] Run integration tests for strategy validation
- [ ] Verify UI can't create invalid states
- [ ] Run full test suite

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] IValidationRule protocol in core layer
- [ ] ValidationEngine in core layer
- [ ] Domain-specific rules implement IValidationRule
- [ ] All validators use ValidationResult consistently
- [ ] All tests pass
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 12
