# Phase 2 Checklist: Migrate formula_system.py Callers
**Status:** Not Started

## Task 2.1: Baseline verification [Simple]
**Tests:** `pytest tests/unit/simulation/ tests/unit/strategy/ -v`
- [ ] Run all tests that cover caller files -- establish green baseline
- [ ] No new tests needed; existing tests cover caller behavior
**Notes:**

## Task 2.2: Update component_stats_calculator.py (3 call sites) [Simple]
**File:** `game/simulation/components/component_stats_calculator.py`
**Tests:** `pytest tests/unit/simulation/components/test_component_stats_calculator.py -v`
- [ ] Change import (L16): `from game.simulation.formula_system import safe_evaluate_math_formula` -> `from game.simulation.formula_system import FormulaEvaluator`
- [ ] Replace call (L151): `safe_evaluate_math_formula(formula, eval_context)` -> `FormulaEvaluator.safe_evaluate(formula, eval_context)`
- [ ] Replace call (L177): `safe_evaluate_math_formula(amount[1:], eval_context)` -> `FormulaEvaluator.safe_evaluate(amount[1:], eval_context)`
- [ ] Replace call (L198): `safe_evaluate_math_formula(obj[1:], ctx)` -> `FormulaEvaluator.safe_evaluate(obj[1:], ctx)`
- [ ] Run tests -- confirm pass
**Notes:**

## Task 2.3: Update component_resource_manager.py (1 call site) [Simple]
**File:** `game/simulation/components/component_resource_manager.py`
**Tests:** `pytest tests/unit/simulation/components/test_component_resource_manager.py -v`
- [ ] Change import (L14): `from game.simulation.formula_system import safe_evaluate_math_formula` -> `from game.simulation.formula_system import FormulaEvaluator`
- [ ] Replace call (L112): `safe_evaluate_math_formula(amount[1:], eval_context, default=0)` -> `FormulaEvaluator.safe_evaluate(amount[1:], eval_context, default=0)`
- [ ] Run tests -- confirm pass
**Notes:**

## Task 2.4: Update weapons.py (2 call sites) [Simple]
**File:** `game/simulation/components/abilities/weapons.py`
**Tests:** `pytest tests/unit/simulation/components/abilities/test_weapons_isolation.py -v`
- [ ] Change import (L7): `from game.simulation.formula_system import safe_evaluate_math_formula` -> `from game.simulation.formula_system import FormulaEvaluator`
- [ ] Replace call (L33): `safe_evaluate_math_formula(formula_str, formula_context)` -> `FormulaEvaluator.safe_evaluate(formula_str, formula_context)` (note: `formula_context` here is the caller's variable name for `context` dict, NOT `FormulaContext` -- no rename needed)
- [ ] Replace call (L207): `safe_evaluate_math_formula(self.damage_formula, context)` -> `FormulaEvaluator.safe_evaluate(self.damage_formula, context)`
- [ ] Run tests -- confirm pass
**Notes:**

## Task 2.5: Update ship_stats_calculator.py (1 call site) [Simple]
**File:** `game/strategy/services/ship_stats_calculator.py`
**Tests:** `pytest tests/unit/strategy/ship_stats/ -v`
- [ ] Change import (L36): `from game.simulation.formula_system import safe_evaluate_math_formula` -> `from game.simulation.formula_system import FormulaEvaluator`
- [ ] Replace call (L659): `safe_evaluate_math_formula(val[1:], context, default=default)` -> `FormulaEvaluator.safe_evaluate(val[1:], context, default=default)`
- [ ] Run tests -- confirm pass
**Notes:**

## Task 2.6: Remove vestigial import from component.py [Simple]
**File:** `game/simulation/components/component.py`
**Tests:** `pytest tests/unit/simulation/components/ -v`
- [ ] Remove unused import (L62): `from game.simulation.formula_system import safe_evaluate_math_formula`
- [ ] Run tests -- confirm pass
**Notes:**

## Task 2.7: Verify all formula_system callers migrated [Simple]
**Tests:** `pytest tests/unit/simulation/ tests/unit/strategy/ -v`
- [ ] Grep for `evaluate_math_formula` in `game/` -- only `formula_system.py` itself should remain
- [ ] Grep for `safe_evaluate_math_formula` in `game/` -- only `formula_system.py` itself should remain
- [ ] Grep for `from game.simulation.formula_system import` -- should only import `FormulaEvaluator` (or `FormulaContext`)
- [ ] Run simulation + strategy tests: `pytest tests/unit/simulation/ tests/unit/strategy/ -v`
**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
