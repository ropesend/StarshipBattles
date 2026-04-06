# Phase 3 Checklist: Migrate modifier_effects.py Callers
**Status:** Complete

### Task 3.1: Update ModifierEffectEvaluator.evaluate_formula [Simple]
**File:** `game/simulation/components/modifier_effects.py`
**Tests:** `pytest tests/unit/simulation/components/test_modifier_effects.py tests/unit/modifiers/test_modifier_effect_evaluator.py -v`
- [x] Add import: `from game.simulation.formula_system import FormulaEvaluator`
- [x] Replace `evaluate_formula()` body with delegation to `FormulaEvaluator.evaluate()` with `MODIFIER_CONTEXT`
- [x] Remove `import math` (no longer used)
- [x] Remove `from game.core.error_codes import ErrorCode` (no longer used)
- [x] Run tests -- 46 passed
**Notes:** `FormulaException` import kept -- still used in `evaluate_modifier` catch block.

### Task 3.2: Update ModifierEffectEvaluator.validate_formula [Simple]
**File:** `game/simulation/components/modifier_effects.py`
**Tests:** `pytest tests/unit/modifiers/test_formula_validation.py tests/unit/simulation/components/test_modifier_effects.py -v`
- [x] Replace `validate_formula()` body with delegation to `FormulaEvaluator.validate()`
- [x] Remove `import ast` (was inline import, removed with old body)
- [x] Run tests -- 42 passed
**Notes:**

### Task 3.3: Verify all modifier callers working [Simple]
**Tests:** Full modifier + simulation test suite
- [x] Run: `pytest tests/unit/modifiers/` -- 252 passed
- [x] Run: `pytest tests/unit/simulation/components/test_modifier_effects.py` -- all pass
- [x] Run: `pytest tests/unit/simulation/` -- 2829 passed
- [x] Verify `modifier_schema.py` L237 still works (calls delegated `validate_formula`)
**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
