# Phase 4 Checklist: Delete Old Code and Final Cleanup
**Status:** Not Started

## Task 4.1: Clean up formula_system.py [Simple]
**File:** `game/simulation/formula_system.py`
**Tests:** `pytest tests/unit/simulation/test_formula_evaluator.py tests/unit/systems/test_formula_system.py -v`
- [ ] Delete string constant `FORMULA_ERROR_SYNTAX = "F001"` (L33)
- [ ] Delete string constant `FORMULA_ERROR_UNDEFINED = "F002"` (L34)
- [ ] Delete string constant `FORMULA_ERROR_RUNTIME = "F003"` (L35)
- [ ] Delete string constant `FORMULA_ERROR_SECURITY = "F004"` (L36)
- [ ] Delete old `validate_formula()` function (L39-78)
- [ ] Delete old `evaluate_math_formula()` function (L81-146)
- [ ] Delete old `safe_evaluate_math_formula()` function (L149-173)
- [ ] Update module docstring to describe FormulaEvaluator as the primary API
- [ ] Add module-level convenience aliases for backward compatibility with test imports:
  ```python
  # Backward-compatible aliases for existing tests
  evaluate_math_formula = FormulaEvaluator.evaluate
  safe_evaluate_math_formula = FormulaEvaluator.safe_evaluate
  validate_formula = FormulaEvaluator.validate
  ```
- [ ] Run: `pytest tests/unit/simulation/test_formula_evaluator.py tests/unit/systems/test_formula_system.py tests/unit/systems/test_formula_overflow_underflow.py tests/unit/simulation/test_formula_exceptions.py -v`
**Notes:**

**CRITICAL DECISION POINT:** The 3 existing test files import `evaluate_math_formula`, `safe_evaluate_math_formula`, and `validate_formula` by name. Two options:
1. **Module-level aliases** (above) -- zero test changes needed
2. **Update test imports** -- change all 3 test files to use `FormulaEvaluator.*`

Recommendation: Use aliases. The test files are testing formula evaluation behavior, not API surface. Changing imports is churn that doesn't improve test quality. If preferred, update test imports in a follow-up.

## Task 4.2: Clean up modifier_effects.py [Simple]
**File:** `game/simulation/components/modifier_effects.py`
**Tests:** `pytest tests/unit/simulation/components/test_modifier_effects.py tests/unit/modifiers/ -v`
- [ ] Verify `evaluate_formula` and `validate_formula` are thin delegations (should be from Task 3.1/3.2)
- [ ] Verify no direct `eval(` call remains in file
- [ ] Verify `import math` is removed (if not needed)
- [ ] Verify `import ast` is removed (if not needed)
- [ ] Verify `from game.core.error_codes import ErrorCode` is removed (if not needed)
- [ ] Run tests -- confirm pass
**Notes:**

## Task 4.3: Final verification [Simple]
**Tests:** Full test suite
- [ ] Grep for direct `eval(` calls in `game/simulation/` -- should only be in `FormulaEvaluator.evaluate()` in `formula_system.py`
- [ ] Grep for `FORMULA_ERROR_SYNTAX` / `FORMULA_ERROR_UNDEFINED` etc. -- should not exist anywhere
- [ ] Grep for old function imports: `from game.simulation.formula_system import evaluate_math_formula` -- should not appear in `game/` (only in `tests/` via aliases)
- [ ] Run full test suite: `python scripts/test_sharded.py`
- [ ] Check if any docs reference formula evaluation: search `docs/` for "formula" and update if needed
- [ ] Update `docs/01_ARCHITECTURE.md` or `docs/02_PATTERNS.md` if formula evaluation is documented there
**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
