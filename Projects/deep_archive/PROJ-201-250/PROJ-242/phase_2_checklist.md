# Phase 2 Checklist: Migrate formula_system.py Callers
**Status:** Complete

### Task 2.1: Baseline verification [Simple]
**Tests:** `pytest tests/unit/simulation/ tests/unit/strategy/ -v`
- [x] Run all tests that cover caller files -- establish green baseline
- [x] No new tests needed; existing tests cover caller behavior
**Notes:** 5464 passed. One pre-existing broken file (test_build_order_command_handler.py) excluded -- unrelated to PROJ-242.

### Task 2.2: Update component_stats_calculator.py (3 call sites) [Simple]
**File:** `game/simulation/components/component_stats_calculator.py`
**Tests:** `pytest tests/unit/simulation/components/test_component_stats_calculator.py -v`
- [x] Change import: `safe_evaluate_math_formula` -> `FormulaEvaluator`
- [x] Replace 3 call sites with `FormulaEvaluator.safe_evaluate()`
- [x] Run tests -- 9 passed
**Notes:**

### Task 2.3: Update component_resource_manager.py (1 call site) [Simple]
**File:** `game/simulation/components/component_resource_manager.py`
**Tests:** `pytest tests/unit/simulation/components/test_component_resource_manager.py -v`
- [x] Change import: `safe_evaluate_math_formula` -> `FormulaEvaluator`
- [x] Replace call site with `FormulaEvaluator.safe_evaluate()`
- [x] Run tests -- 43 passed
**Notes:**

### Task 2.4: Update weapons.py (2 call sites) [Simple]
**File:** `game/simulation/components/abilities/weapons.py`
**Tests:** `pytest tests/unit/simulation/components/abilities/test_weapons_isolation.py -v`
- [x] Change import: `safe_evaluate_math_formula` -> `FormulaEvaluator`
- [x] Replace 2 call sites with `FormulaEvaluator.safe_evaluate()`
- [x] Run tests -- 77 passed
**Notes:**

### Task 2.5: Update ship_stats_calculator.py (1 call site) [Simple]
**File:** `game/strategy/services/ship_stats_calculator.py`
**Tests:** `pytest tests/unit/strategy/ship_stats/ -v`
- [x] Change import: `safe_evaluate_math_formula` -> `FormulaEvaluator`
- [x] Replace call site with `FormulaEvaluator.safe_evaluate()`
- [x] Run tests -- 118 passed
**Notes:**

### Task 2.6: Remove vestigial import from component.py [Simple]
**File:** `game/simulation/components/component.py`
**Tests:** `pytest tests/unit/simulation/components/ -v`
- [x] Remove unused import of `safe_evaluate_math_formula`
- [x] Run tests -- 1020 passed
**Notes:**

### Task 2.7: Verify all formula_system callers migrated [Simple]
**Tests:** `pytest tests/unit/simulation/ tests/unit/strategy/ -v`
- [x] Grep for `evaluate_math_formula` in `game/` -- only `formula_system.py` itself remains
- [x] Grep for `safe_evaluate_math_formula` in `game/` -- only `formula_system.py` itself remains
- [x] Grep for `from game.simulation.formula_system import` -- all 4 callers now import `FormulaEvaluator`
- [x] Run simulation + strategy tests -- 5464 passed
**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
