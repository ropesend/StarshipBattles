# Phase 3: Simulation Layer - Components & Formulas

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-45 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Fix error handling in simulation layer, especially formula evaluation and component loading.

---

## Tasks

### Task 3.1: Update formula_system.py - Raise Exceptions [Complex]
**File:** `game/simulation/formula_system.py`
**Tests:** `pytest tests/unit/simulation/test_formula_system.py tests/unit/refactor/test_formula_error_handling.py`

- [ ] Fix ERR-004: line 92 - Change from `log_warning()` + return 0 to raising `FormulaException`
- [ ] Create `FormulaEvaluationError` subclass of `FormulaException`
- [ ] Include formula string, context variables, and original error in exception
- [ ] Update `validate_formula()` to return detailed error info
- [ ] Add error codes for different formula failure types (syntax, undefined var, runtime)
- [ ] Verify: Tests pass

**Notes:** This is a breaking change - all callers must be updated to handle exceptions

---

### Task 3.2: Update component.py Error Handling [Complex]
**File:** `game/simulation/components/component.py`
**Tests:** `pytest tests/unit/simulation/components/`

- [ ] Fix ERR-001: line 725 - Replace `except Exception as e:` with specific types
- [ ] Fix ERR-012: lines 725-726, 810-811 - Decide fail-fast vs collect errors
- [ ] Fix ERR-006: Use `raise from e` for exception chaining
- [ ] Fix CQ-05: lines 335-357 - Add logging for `try_activate()`, `consume_activation()` failures
- [ ] Fix ERR-12: lines 99-101 - Log or raise when registries not available
- [ ] Update `load_components_data()` to raise `ComponentException` on critical failures
- [ ] Update `load_modifiers_data()` to raise on failures
- [ ] Add component ID and context to all error messages
- [ ] Verify: Tests pass

**Notes:**

---

### Task 3.3: Update modifier_effects.py Error Handling [Medium]
**File:** `game/simulation/components/modifier_effects.py`
**Tests:** `pytest tests/unit/simulation/components/test_modifier_effects.py`

- [ ] Fix ERR-04: lines 148, 198, 251 - Include modifier ID, component ID, formula in errors
- [ ] Update `evaluate_modifier()` to propagate `FormulaException`
- [ ] Update `evaluate_formula()` to raise `FormulaException` instead of `ValueError`
- [ ] Add `raise from e` for exception chaining
- [ ] Verify: Tests pass

**Notes:**

---

### Task 3.4: Update battle_controller.py Error Handling [Medium]
**File:** `game/simulation/battle_controller.py`
**Tests:** `pytest tests/unit/simulation/test_battle_controller.py`

- [ ] Fix ERR-005: line 276 - Standardize to `StateException`
- [ ] Replace `RuntimeError` with custom `SimulationException` types
- [ ] Add `raise from e` for any exception re-raises
- [ ] Add context to all error messages (battle state, turn number)
- [ ] Verify: Tests pass

**Notes:**

---

### Task 3.5: Update battle_state.py Error Handling [Simple]
**File:** `game/simulation/battle_state.py`
**Tests:** `pytest tests/unit/simulation/test_battle_state.py`

- [ ] Fix ERR-08/ERR-015: line 271 - Log missing key before skipping
- [ ] Add context (layer type, expected key) to warning message
- [ ] Verify: Tests pass

**Notes:**

---

### Task 3.6: Update ship.py Error Handling [Medium]
**File:** `game/simulation/entities/ship.py`
**Tests:** `pytest tests/unit/simulation/entities/test_ship.py`

- [ ] Update component addition to handle `ComponentException`
- [ ] Add logging when hull component creation fails (line 96)
- [ ] Propagate formula exceptions from stat calculations
- [ ] Add ship ID context to all error messages
- [ ] Verify: Tests pass

**Notes:**

---

### Task 3.7: Update projectile.py Input Validation [Simple]
**File:** `game/simulation/entities/projectile.py`
**Tests:** `pytest tests/unit/simulation/entities/test_projectile.py`

- [ ] Fix ERR-009: line 34 - Add validation after `.get()` calls
- [ ] Raise `ValidationException` for invalid projectile data
- [ ] Verify: Tests pass

**Notes:**

---

### Task 3.8: Update validator.py Error Handling [Simple]
**File:** `game/simulation/systems/validator.py`
**Tests:** `pytest tests/unit/simulation/systems/test_validator.py`

- [ ] Update validation rules to use `ErrorCode` enum
- [ ] Add error codes to `ValidationResult.add_error()` calls
- [ ] Verify: Tests pass

**Notes:**

---

### Task 3.9: Update design_loader.py Exception Chaining [Simple]
**File:** `game/simulation/services/design_loader.py`
**Tests:** `pytest tests/unit/simulation/services/test_design_loader.py`

- [ ] Fix ERR-006: Add `raise from e` for exception chaining
- [ ] Replace generic `Exception` with specific types
- [ ] Verify: Tests pass

**Notes:**

---

### Task 3.10: Update battle_engine.py Finally Blocks [Simple]
**File:** `game/simulation/systems/battle_engine.py`
**Tests:** `pytest tests/unit/simulation/systems/test_battle_engine.py`

- [ ] Fix ERR-010: lines 118-124 - Add finally block for cleanup
- [ ] Use context managers where appropriate
- [ ] Verify: Tests pass

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] All tests pass: `pytest tests/unit/simulation/`
- [ ] No regressions: `pytest tests/ --testmon`
- [ ] Test component with invalid formula - verify FormulaException raised
- [ ] Test ship builder with broken modifier - verify error message includes context
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
