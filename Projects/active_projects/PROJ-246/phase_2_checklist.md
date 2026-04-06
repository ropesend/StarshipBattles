# PROJ-246 Phase 2: Add Tests

> **BEFORE MARKING THIS PHASE COMPLETE:**
> Run tests: `pytest tests/unit/simulation/test_formula_evaluator.py -x`

## Objective
Verify strict mode catches bad formulas during loading, and runtime path still degrades gracefully.

## Status: Not Started

---

### Task 2.1: Test Strict Data Loading Catches Errors [Simple]
**File:** `tests/unit/simulation/test_formula_evaluator.py`
**Tests:** `pytest tests/unit/simulation/test_formula_evaluator.py -x`

- [ ] Add test: `test_strict_evaluate_raises_on_undefined_variable` — call `evaluate()` with `"undefined_var"`, assert `FormulaException` raised
- [ ] Add test: `test_strict_evaluate_raises_on_syntax_error` — call `evaluate()` with `"1 + +"`, assert `FormulaException` raised
- [ ] Add test: `test_strict_evaluate_raises_on_division_by_zero` — call `evaluate()` with `"1 / 0"`, assert `FormulaException` raised

**Notes:** These may already exist in the test file — check first and skip if covered.

---

### Task 2.2: Test Runtime Safe Fallback Unchanged [Simple]
**File:** `tests/unit/simulation/test_formula_evaluator.py`
**Tests:** `pytest tests/unit/simulation/test_formula_evaluator.py -x`

- [ ] Verify existing `TestFormulaEvaluatorSafeEvaluate` tests (lines 351-374) still pass unchanged
- [ ] Add test: `test_get_damage_with_broken_formula_returns_zero` — create a weapon with broken damage_formula, call `get_damage()`, verify returns 0 (not crash)

**Notes:**

---

### Task 2.3: Integration Test — Component Loading With Bad Formula [Simple]
**File:** `tests/unit/simulation/components/test_component_loading.py` (new or existing)
**Tests:** `pytest tests/unit/simulation/components/ -x`

- [ ] Add test: load a component with `"mass": "=invalid_formula"`, verify `FormulaException` raised during `recalculate()`
- [ ] Add test: load a component with valid formulas, verify it loads successfully (regression)

**Notes:**
