# Phase 3 Checklist: Migrate modifier_effects.py Callers
**Status:** Not Started

## Task 3.1: Update ModifierEffectEvaluator.evaluate_formula [Simple]
**File:** `game/simulation/components/modifier_effects.py`
**Tests:** `pytest tests/unit/simulation/components/test_modifier_effects.py tests/unit/modifiers/test_modifier_effect_evaluator.py -v`
- [ ] Add import at top of file (~L18): `from game.simulation.formula_system import FormulaEvaluator`
- [ ] Replace `evaluate_formula()` method body (L117-184) with delegation:
  ```python
  @staticmethod
  def evaluate_formula(formula: str, context: Dict[str, float]) -> float:
      """Evaluate a formula string with the given context.

      Delegates to FormulaEvaluator with modifier-specific context
      (caret substitution enabled).

      Args:
          formula: Formula string like "param ^ 2" or "2 ^ param"
          context: Dictionary of variable values (e.g., {'param': 2.0})

      Returns:
          Evaluated result as float

      Raises:
          FormulaException: If formula cannot be evaluated.
      """
      result = FormulaEvaluator.evaluate(
          formula, context, FormulaEvaluator.MODIFIER_CONTEXT
      )
      return float(result)
  ```
- [ ] Remove `import math` if no longer used elsewhere in the file (check: `ModifierEffect` doesn't use it; `math` is not referenced after delegation)
- [ ] Remove `from game.core.error_codes import ErrorCode` if no longer used (check: only used in old `evaluate_formula` error handling)
- [ ] Run tests -- confirm ALL pass (especially error code checks in `test_modifier_effects.py` L167-179)
**Notes:**

## Task 3.2: Update ModifierEffectEvaluator.validate_formula [Simple]
**File:** `game/simulation/components/modifier_effects.py`
**Tests:** `pytest tests/unit/modifiers/test_formula_validation.py tests/unit/simulation/components/test_modifier_effects.py -v`
- [ ] Replace `validate_formula()` method body (L255-296) with delegation:
  ```python
  @classmethod
  def validate_formula(cls, formula: str) -> List[str]:
      """Validate a formula string without evaluating it.

      Delegates to FormulaEvaluator with modifier-specific context.

      Args:
          formula: Formula string to validate

      Returns:
          List of error messages (empty if valid)
      """
      # Modifier formulas only allow 'param' plus math functions
      return FormulaEvaluator.validate(
          formula, ['param'], FormulaEvaluator.MODIFIER_CONTEXT
      )
  ```
- [ ] Remove `import ast` (was only used in old validate_formula body, L269)
- [ ] Run tests -- confirm ALL pass
**Notes:**

**IMPORTANT NOTE:** The old `validate_formula` allowed `{'param', 'ln', 'log', 'log10', 'sqrt', 'abs', 'min', 'max', 'pi', 'e', 'True', 'False'}`. The unified `validate()` builds its allowed set from `ALLOWED_MATH_FUNCTIONS | ALLOWED_BUILTINS | {'ln'} | set(allowed_variables)`. Since `ALLOWED_MATH_FUNCTIONS` includes all `math.*` names (which includes `log`, `log10`, `sqrt`, `pi`, `e`) and `ALLOWED_BUILTINS` includes `abs`, `min`, `max`, plus `True`/`False` are Python builtins that pass through `ast.Name` but are actually `ast.Constant` in modern Python (3.8+), this is a superset. Existing valid formulas remain valid. The only behavioral change: more names are now "allowed" in validation, but since `eval()` already had them available, this is correct (validation now matches evaluation capability).

## Task 3.3: Verify all modifier callers working [Simple]
**Tests:** Full modifier + simulation test suite
- [ ] Run: `pytest tests/unit/modifiers/ -v` -- all pass
- [ ] Run: `pytest tests/unit/simulation/components/test_modifier_effects.py -v` -- all pass
- [ ] Run: `pytest tests/unit/simulation/ -v` -- all pass
- [ ] Verify `modifier_schema.py` L237 still works (it calls `ModifierEffectEvaluator.validate_formula()` which now delegates)
**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
