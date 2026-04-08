# PROJ-246 Phase 2: Add Tests

> **BEFORE MARKING THIS PHASE COMPLETE:**
> Run tests: `pytest tests/unit/simulation/test_formula_evaluator.py -x`

## Objective
Verify strict mode catches bad formulas during loading, and runtime path still degrades gracefully.

## Status: Complete

---

### Task 2.1: Test Strict Data Loading Catches Errors [Simple]
**File:** `tests/unit/simulation/test_formula_evaluator.py`
**Tests:** `pytest tests/unit/simulation/test_formula_evaluator.py -x`

- [x] ~~Add test: `test_strict_evaluate_raises_on_undefined_variable`~~ — **ALREADY EXISTS** as `TestFormulaEvaluatorErrors::test_name_error_raises_formula_exception`
- [x] ~~Add test: `test_strict_evaluate_raises_on_syntax_error`~~ — **ALREADY EXISTS** as `TestFormulaEvaluatorErrors::test_syntax_error_raises_formula_exception`
- [x] ~~Add test: `test_strict_evaluate_raises_on_division_by_zero`~~ — **ALREADY EXISTS** as `TestFormulaEvaluatorErrors::test_zero_division_raises_formula_exception`

**Notes:** All three tests already existed in `TestFormulaEvaluatorErrors` class (lines 234-282). Skipped as covered.

---

### Task 2.2: Test Runtime Safe Fallback Unchanged [Simple]
**File:** `tests/unit/simulation/components/abilities/test_weapons_isolation.py`
**Tests:** `pytest tests/unit/simulation/components/abilities/test_weapons_isolation.py -x`

- [x] Verify existing `TestFormulaEvaluatorSafeEvaluate` tests (lines 351-374) still pass unchanged — all 4 tests pass
- [x] Add test: `test_get_damage_with_broken_formula_returns_zero` — weapon with broken `damage_formula` returns 0 at runtime (not crash)

**Notes:** Test sets up a valid weapon, then injects a broken formula string to simulate runtime corruption. Verifies `get_damage()` returns 0.0 via `safe_evaluate` fallback.

---

### Task 2.3: Integration Test — Component Loading With Bad Formula [Simple]
**File:** `tests/unit/simulation/components/test_component_stats_calculator.py`
**Tests:** `pytest tests/unit/simulation/components/test_component_stats_calculator.py -x`

- [x] Add test: `test_bad_attribute_formula_raises_on_recalculate` — component with `"mass": "=invalid_formula"` raises FormulaException
- [x] Add test: `test_bad_resource_cost_formula_raises_on_recalculate` — component with invalid resource_cost formula raises FormulaException
- [x] Add test: `test_valid_formulas_load_successfully` — bridge component with valid formulas loads without error (regression)

**Notes:** All 3 tests added to new `TestStrictFormulaEvaluation` class. All pass.
