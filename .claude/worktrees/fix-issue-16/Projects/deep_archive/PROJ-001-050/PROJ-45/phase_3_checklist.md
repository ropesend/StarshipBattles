# Phase 3: Simulation Layer - Components & Formulas

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-45 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Fix error handling in simulation layer, especially formula evaluation and component loading.

---

## Tasks

### Task 3.1: Update formula_system.py - Raise Exceptions [Complex]
**File:** `game/simulation/formula_system.py`
**Tests:** `pytest tests/unit/simulation/test_formula_system.py tests/unit/refactor/test_formula_error_handling.py`

- [x] Fix ERR-004: line 92 - Change from `log_warning()` + return 0 to raising `FormulaException`
- [x] Create `safe_evaluate_math_formula` wrapper for backward compatibility
- [x] Include formula string, context variables, and original error in exception
- [x] Update `validate_formula()` to return detailed error info
- [x] Add error codes for different formula failure types (syntax, undefined var, runtime)
- [x] Verify: Tests pass

**Notes:** Added `safe_evaluate_math_formula()` as backward-compatible wrapper. Updated all callers.

---

### Task 3.2: Update component.py Error Handling [Complex]
**File:** `game/simulation/components/component.py`
**Tests:** `pytest tests/unit/simulation/components/`

- [x] Fix ERR-001: Replace `except Exception as e:` with specific types
- [x] Fix ERR-012: Added error collection pattern with summary warnings
- [x] Fix ERR-006: Use `raise from e` for exception chaining
- [x] Update `load_components_data()` with specific exception types and context
- [x] Update `load_modifiers_data()` with proper error handling
- [x] Add component ID and context to all error messages
- [x] Verify: Tests pass

**Notes:** Updated formula evaluation calls to use `safe_evaluate_math_formula`

---

### Task 3.3: Update modifier_effects.py Error Handling [Medium]
**File:** `game/simulation/components/modifier_effects.py`
**Tests:** `pytest tests/unit/refactor/test_formula_error_handling.py`

- [x] Fix ERR-04: Include modifier ID, component ID, formula in errors
- [x] Update `evaluate_modifier()` to catch `FormulaException`
- [x] Update `evaluate_formula()` to raise `FormulaException` instead of `ValueError`
- [x] Add `raise from e` for exception chaining
- [x] Verify: Tests pass

**Notes:**

---

### Task 3.4: Update battle_controller.py Error Handling [Medium]
**File:** `game/simulation/battle_controller.py`
**Tests:** `pytest tests/unit/simulation/test_battle_controller.py`

- [x] Fix ERR-005: Replaced `RuntimeError` with `StateException`
- [x] Added error context (operation name)
- [x] Updated tests to expect `StateException`
- [x] Verify: Tests pass

**Notes:**

---

### Task 3.5: Update battle_state.py Error Handling [Simple]
**File:** `game/simulation/battle_state.py`
**Tests:** `pytest tests/unit/simulation/`

- [x] Fix ERR-08/ERR-015: Log missing key with context before skipping
- [x] Add context (layer type, valid layers, ship ID) to warning message
- [x] Verify: Tests pass

**Notes:**

---

### Task 3.6: Update ship.py Error Handling [Medium]
**File:** `game/simulation/entities/ship.py`
**Tests:** `pytest tests/unit/entities/test_ship.py`

- [x] Enhanced logging when unknown layer type encountered
- [x] Added context (valid layers, ship class) to warning
- [x] Verify: Tests pass

**Notes:** Hull component creation already had logging at line 117

---

### Task 3.7: Update projectile.py Input Validation [Simple]
**File:** `game/simulation/entities/projectile.py`
**Tests:** `pytest tests/unit/simulation/`

- [x] Fix ERR-009: Added validation for damage, range, and endurance
- [x] Raise `ValidationException` for invalid projectile data
- [x] Endurance can be None for range-limited projectiles
- [x] Verify: Tests pass

**Notes:** Fixed tests to provide valid data

---

### Task 3.8: Update validator.py Error Handling [Simple]
**File:** `game/simulation/ship_validator.py` (canonical location)
**Tests:** `pytest tests/unit/simulation/ -k valid`

- [x] Update validation rules to use `ErrorCode` enum
- [x] Add error codes to `ValidationResult.add_error()` calls
- [x] Verify: Tests pass

**Notes:**

---

### Task 3.9: Update design_loader.py Exception Chaining [Simple]
**File:** `game/simulation/services/design_loader.py`
**Tests:** `pytest tests/unit/simulation/services/`

- [x] Added specific exception types (JSONDecodeError, KeyError, TypeError, OSError)
- [x] Enhanced error messages with context
- [x] Verify: Tests pass

**Notes:**

---

### Task 3.10: Update battle_engine.py Finally Blocks [Simple]
**File:** `game/simulation/systems/battle_engine.py`
**Tests:** `pytest tests/unit/simulation/`

- [x] Fix ERR-010: Added proper cleanup on start_session failure
- [x] Verify: Tests pass

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] All tests pass: `pytest tests/unit/simulation/` - 526 passed
- [x] No regressions: `pytest tests/` - 5758 passed, 3 skipped
- [x] Test component with invalid formula - verify FormulaException raised
- [x] Test ship builder with broken modifier - verify error message includes context
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
