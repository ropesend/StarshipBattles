# Phase 1 Checklist: Create Unified FormulaEvaluator
**Status:** Not Started

## Task 1.1: Write tests for FormulaEvaluator [Medium]
**File:** `tests/unit/simulation/test_formula_evaluator.py` (new)
**Tests:** `pytest tests/unit/simulation/test_formula_evaluator.py -v`
- [ ] Create new test file `tests/unit/simulation/test_formula_evaluator.py`
- [ ] `TestFormulaContext`: test dataclass defaults (`caret_as_power=False`, `extra_functions={}`)
- [ ] `TestFormulaContext`: test creating with `caret_as_power=True`
- [ ] `TestFormulaEvaluatorBasic`: test arithmetic (`1 + 1`, `10 - 3`, `4 * 5`, `15 / 3`)
- [ ] `TestFormulaEvaluatorBasic`: test context variables (`x + y` with `{'x': 10, 'y': 5}`)
- [ ] `TestFormulaEvaluatorBasic`: test complex formula (`50 * sqrt(ship_class_mass / 1000)` with `{'ship_class_mass': 1000}`)
- [ ] `TestFormulaEvaluatorMathFunctions`: test all math module functions (`sqrt`, `sin`, `cos`, `log`, `floor`, `ceil`, `exp`, etc.)
- [ ] `TestFormulaEvaluatorMathFunctions`: test `ln` alias maps to `math.log`
- [ ] `TestFormulaEvaluatorMathFunctions`: test `pi` and `e` constants available
- [ ] `TestFormulaEvaluatorBuiltins`: test `abs`, `min`, `max`, `round`, `sum`, `len`, `int`, `float`, `pow`
- [ ] `TestFormulaEvaluatorCaret`: test `^` as XOR when `caret_as_power=False` (e.g., `3 ^ 1` == `2`)
- [ ] `TestFormulaEvaluatorCaret`: test `^` as power when `caret_as_power=True` (e.g., `3 ^ 2` == `9`)
- [ ] `TestFormulaEvaluatorCaret`: test `param ^ 2` with `caret_as_power=True` and `{'param': 3.0}` == `9.0`
- [ ] `TestFormulaEvaluatorCaret`: test `2 ^ param` with `caret_as_power=True` and `{'param': 3.0}` == `8.0`
- [ ] `TestFormulaEvaluatorErrors`: test `SyntaxError` raises `FormulaException` with `code=ErrorCode.FORMULA_SYNTAX_ERROR.value`
- [ ] `TestFormulaEvaluatorErrors`: test `NameError` raises `FormulaException` with `code=ErrorCode.FORMULA_UNDEFINED_VAR.value`
- [ ] `TestFormulaEvaluatorErrors`: test `ZeroDivisionError` raises `FormulaException` with `code=ErrorCode.EVAL_ERROR.value`
- [ ] `TestFormulaEvaluatorErrors`: test security (dangerous names like `eval`, `exec`, `open`) raises `FormulaException` with `code=ErrorCode.FORMULA_GENERAL_ERROR.value`
- [ ] `TestFormulaEvaluatorErrors`: test exception includes `context` dict with `formula` and `available_vars`
- [ ] `TestFormulaEvaluatorErrors`: test exception chains from original error (`__cause__` is not None)
- [ ] `TestFormulaEvaluatorValidate`: test valid formula returns empty error list
- [ ] `TestFormulaEvaluatorValidate`: test syntax error returns error list
- [ ] `TestFormulaEvaluatorValidate`: test undefined variable detected
- [ ] `TestFormulaEvaluatorValidate`: test math functions allowed
- [ ] `TestFormulaEvaluatorValidate`: test dangerous functions blocked
- [ ] `TestFormulaEvaluatorValidate`: test caret substitution in validation when `caret_as_power=True`
- [ ] `TestFormulaEvaluatorValidate`: test `allowed_variables` parameter restricts variable names
- [ ] `TestFormulaEvaluatorSafeEvaluate`: test returns computed value on success
- [ ] `TestFormulaEvaluatorSafeEvaluate`: test returns `default` on error
- [ ] `TestFormulaEvaluatorSafeEvaluate`: test returns custom default value
- [ ] `TestFormulaEvaluatorSafeEvaluate`: test logs warning on error
- [ ] Run tests -- confirm they ALL FAIL (class doesn't exist yet)
**Notes:**

## Task 1.2: Implement FormulaContext dataclass [Simple]
**File:** `game/simulation/formula_system.py`
**Tests:** `pytest tests/unit/simulation/test_formula_evaluator.py::TestFormulaContext -v`
- [ ] Add import: `from dataclasses import dataclass, field` (top of file)
- [ ] Add import: `from game.core.error_codes import ErrorCode` (after existing imports, ~L12)
- [ ] Add `FormulaContext` dataclass after the module-level constants (~after L36):
  ```python
  @dataclass(frozen=True)
  class FormulaContext:
      """Configuration for formula evaluation behavior.

      Attributes:
          caret_as_power: If True, replace '^' with '**' before eval.
              Used by modifier formulas which use '^' for exponentiation.
          extra_functions: Additional name->callable mappings to add to eval context.
              E.g., {'ln': math.log} for modifier formulas.
      """
      caret_as_power: bool = False
      extra_functions: Dict[str, Any] = field(default_factory=dict)
  ```
- [ ] Run FormulaContext tests -- confirm they pass
**Notes:**

## Task 1.3: Implement FormulaEvaluator class [Medium]
**File:** `game/simulation/formula_system.py`
**Tests:** `pytest tests/unit/simulation/test_formula_evaluator.py -v`
- [ ] Add `FormulaEvaluator` class after `FormulaContext` (~L52):
  ```python
  class FormulaEvaluator:
      """Unified formula evaluation with configurable context.

      Provides a single eval() sandbox for all formula evaluation in the game.
      Replaces both module-level evaluate_math_formula() and
      ModifierEffectEvaluator.evaluate_formula().
      """

      # Default context used when none specified
      DEFAULT_CONTEXT = FormulaContext()

      # Modifier context with caret substitution and ln alias
      MODIFIER_CONTEXT = FormulaContext(
          caret_as_power=True,
          extra_functions={'ln': math.log}
      )
  ```
- [ ] Implement `evaluate(cls, formula, context, formula_context=None)` as classmethod:
  - Build namespace from `math.__dict__` (exclude `__` prefixed)
  - Add `ALLOWED_BUILTINS` from builtins module
  - Add `ln` alias: `names['ln'] = math.log`
  - Add `formula_context.extra_functions` if provided
  - Add caller's `context` dict
  - If `formula_context.caret_as_power`: replace `^` with `**`
  - `eval(formula, {"__builtins__": {}}, names)`
  - Catch `SyntaxError` -> `FormulaException(code=ErrorCode.FORMULA_SYNTAX_ERROR.value)`
  - Catch `NameError` -> `FormulaException(code=ErrorCode.FORMULA_UNDEFINED_VAR.value)`
  - Catch `(ZeroDivisionError, ValueError, ArithmeticError)` -> `FormulaException(code=ErrorCode.EVAL_ERROR.value)`
  - Catch `Exception` -> `FormulaException(code=ErrorCode.FORMULA_GENERAL_ERROR.value)`
- [ ] Implement `validate(cls, formula, allowed_variables, formula_context=None)` as classmethod:
  - If `formula_context.caret_as_power`: replace `^` with `**` before AST parse
  - AST walk checking `ast.Name` nodes against allowed set
  - Allowed set = `ALLOWED_MATH_FUNCTIONS | ALLOWED_BUILTINS | {'ln'} | set(allowed_variables)`
  - Check `DANGEROUS_NAMES` and log warnings
- [ ] Implement `safe_evaluate(cls, formula, context, default=0, formula_context=None)` as classmethod:
  - Try `cls.evaluate(formula, context, formula_context)`
  - Catch `FormulaException`, log warning, return `default`
- [ ] Run ALL new tests -- confirm they pass
- [ ] Add `FormulaEvaluator` and `FormulaContext` to module `__all__` or exports
**Notes:**

## Task 1.4: Verify no regressions [Simple]
**Tests:** Full test suite
- [ ] Run existing formula tests: `pytest tests/unit/systems/test_formula_system.py tests/unit/systems/test_formula_overflow_underflow.py tests/unit/simulation/test_formula_exceptions.py -v`
- [ ] Run modifier tests: `pytest tests/unit/modifiers/ tests/unit/simulation/components/test_modifier_effects.py -v`
- [ ] Run full test suite: `python scripts/test_sharded.py`
- [ ] Confirm zero test failures and zero test changes
**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
