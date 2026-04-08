# Phase 2: FormulaEvaluator Extraction + AST Walker

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-257 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Extract FormulaEvaluator from simulation to core layer. Replace eval() with AST tree walker. Add LRU cache for parsed formula ASTs.

---

## Tasks

### Task 2.1: Create `game/core/formula_evaluator.py` with FormulaEvaluator (eval-based, no AST yet) [Medium]
**File:** `game/core/formula_evaluator.py` (new)
**Tests:** `tests/unit/core/test_formula_evaluator.py` (new)

**TDD Steps:**
- [ ] Create test file `tests/unit/core/test_formula_evaluator.py` with tests for core import path:
  - Test `from game.core.formula_evaluator import FormulaEvaluator, FormulaContext`
  - Test basic evaluate: `FormulaEvaluator.evaluate("2 + 3", {})` returns 5
  - Test variable substitution: `FormulaEvaluator.evaluate("x * 2", {"x": 5})` returns 10
  - Test math functions: `FormulaEvaluator.evaluate("sqrt(16)", {})` returns 4.0
  - Test safe_evaluate fallback: `FormulaEvaluator.safe_evaluate("bad!", {}, default=42)` returns 42
  - Test validate: `FormulaEvaluator.validate("x + y", ["x", "y"])` returns empty list
  - Test validate catches undefined: `FormulaEvaluator.validate("z + 1", ["x"])` returns error for "z"
  - Test MODIFIER_CONTEXT caret substitution: `FormulaEvaluator.evaluate("x ^ 2", {"x": 3}, formula_context=FormulaEvaluator.MODIFIER_CONTEXT)` returns 9
  - Test security: evaluate with `__import__` raises FormulaException
- [ ] Run tests, confirm they fail: `pytest tests/unit/core/test_formula_evaluator.py -x`
- [ ] Copy entire content of `game/simulation/formula_system.py` to `game/core/formula_evaluator.py` (lines 1-270, all constants + classes + aliases)
- [ ] Run tests, confirm they pass: `pytest tests/unit/core/test_formula_evaluator.py -x`
- [ ] Run existing formula tests to confirm nothing broke: `pytest tests/unit/simulation/test_formula_evaluator.py tests/unit/systems/test_formula_system.py tests/unit/simulation/test_formula_exceptions.py tests/unit/systems/test_formula_overflow_underflow.py -x`

**Notes:** This task does a pure copy first. The AST walker replacement comes in Task 2.3.

---

### Task 2.2: Convert `game/simulation/formula_system.py` to re-export shim [Simple]
**File:** `game/simulation/formula_system.py`
**Tests:** `pytest tests/unit/simulation/test_formula_evaluator.py tests/unit/systems/test_formula_system.py tests/unit/simulation/test_formula_exceptions.py tests/unit/systems/test_formula_overflow_underflow.py -x`

- [ ] Replace entire content of `game/simulation/formula_system.py` with a re-export shim:
  ```python
  """Formula evaluation system - re-export shim.
  
  Canonical location: game.core.formula_evaluator
  This module re-exports for backward compatibility.
  """
  from game.core.formula_evaluator import (
      FormulaEvaluator,
      FormulaContext,
      ALLOWED_MATH_FUNCTIONS,
      ALLOWED_BUILTINS,
      DANGEROUS_NAMES,
  )

  # Backward-compatible aliases
  evaluate_math_formula = FormulaEvaluator.evaluate
  safe_evaluate_math_formula = FormulaEvaluator.safe_evaluate
  validate_formula = FormulaEvaluator.validate
  ```
- [ ] Run ALL existing formula tests (they import from `game.simulation.formula_system`):
  `pytest tests/unit/simulation/test_formula_evaluator.py tests/unit/systems/test_formula_system.py tests/unit/simulation/test_formula_exceptions.py tests/unit/systems/test_formula_overflow_underflow.py -x`
- [ ] Verify: all tests pass without modification (re-exports work)

**Notes:**

---

### Task 2.3: Update production imports to use core path [Simple]
**Files:** 6 files in `game/simulation/` and `game/strategy/`
**Tests:** `pytest tests/ --testmon`

Update each production file to import from `game.core.formula_evaluator` instead of `game.simulation.formula_system`:

- [ ] `game/simulation/components/modifier_effects.py:19` -- change `from game.simulation.formula_system import FormulaEvaluator` to `from game.core.formula_evaluator import FormulaEvaluator`
- [ ] `game/simulation/components/component_stats_calculator.py:16` -- change `from game.simulation.formula_system import FormulaEvaluator` to `from game.core.formula_evaluator import FormulaEvaluator`
- [ ] `game/simulation/components/component_resource_manager.py:14` -- change `from game.simulation.formula_system import FormulaEvaluator` to `from game.core.formula_evaluator import FormulaEvaluator`
- [ ] `game/simulation/components/abilities/weapons.py:7` -- change `from game.simulation.formula_system import FormulaEvaluator` to `from game.core.formula_evaluator import FormulaEvaluator`
- [ ] `game/strategy/services/ship_stats_calculator.py:36` -- change `from game.simulation.formula_system import FormulaEvaluator` to `from game.core.formula_evaluator import FormulaEvaluator`
- [ ] `game/strategy/services/design_validator.py:83` (late import inside method) -- change `from game.simulation.formula_system import FormulaEvaluator` to `from game.core.formula_evaluator import FormulaEvaluator`
- [ ] Run incremental tests: `pytest tests/ --testmon`
- [ ] Verify: `grep -rn "from game\.simulation\.formula_system import" game/` returns zero results (only test files should import from simulation path)

**Notes:**

---

### Task 2.4: Build AST tree walker - write tests [Medium]
**File:** `game/core/formula_evaluator.py`
**Tests:** `tests/unit/core/test_formula_evaluator.py` (extend)

**TDD Steps - add tests for AST walker behavior:**
- [ ] Test arithmetic: `2 + 3 * 4` returns 14 (operator precedence)
- [ ] Test parentheses: `(2 + 3) * 4` returns 20
- [ ] Test power: `2 ** 3` returns 8
- [ ] Test floor division: `7 // 2` returns 3
- [ ] Test modulo: `7 % 3` returns 1
- [ ] Test unary negation: `-x` with x=5 returns -5
- [ ] Test unary positive: `+x` with x=5 returns 5
- [ ] Test nested function calls: `max(sqrt(16), 2)` returns 4.0
- [ ] Test comparison in formula: formulas with comparisons work (if used in existing formulas)
- [ ] Test no eval() is used: mock or patch `builtins.eval` and verify it is NOT called during evaluate()
- [ ] Test LRU cache hit: evaluate same formula twice, second call reuses cached AST (check `_parse_formula.cache_info()`)
- [ ] Test all 52 production formulas produce identical results to current eval()-based evaluator (capture baseline first)
- [ ] Test rejected AST nodes: attribute access `x.y` raises FormulaException
- [ ] Test rejected AST nodes: subscript `x[0]` raises FormulaException
- [ ] Test error message includes formula string and available variables
- [ ] Run tests, confirm they fail: `pytest tests/unit/core/test_formula_evaluator.py -x`

**Notes:** The "identical results" test is critical -- capture eval() output for all 52 formulas before replacing with AST walker.

---

### Task 2.5: Implement AST tree walker in FormulaEvaluator.evaluate() [Complex]
**File:** `game/core/formula_evaluator.py`
**Tests:** `pytest tests/unit/core/test_formula_evaluator.py tests/unit/simulation/test_formula_evaluator.py tests/unit/systems/test_formula_system.py tests/unit/simulation/test_formula_exceptions.py tests/unit/systems/test_formula_overflow_underflow.py -x`

- [ ] Add `import functools` and `import operator` to imports
- [ ] Create module-level `_BINARY_OPS` dict mapping `ast.Add` -> `operator.add`, `ast.Sub` -> `operator.sub`, etc.
- [ ] Create module-level `_UNARY_OPS` dict mapping `ast.UAdd` -> `operator.pos`, `ast.USub` -> `operator.neg`
- [ ] Create module-level `_COMPARE_OPS` dict mapping `ast.Lt` -> `operator.lt`, etc.
- [ ] Add cached parse function:
  ```python
  @functools.lru_cache(maxsize=256)
  def _parse_formula(formula: str) -> ast.Expression:
      return ast.parse(formula, mode='eval')
  ```
- [ ] Add `_eval_node(node, names)` recursive method that dispatches on AST node type:
  - `ast.Expression`: evaluate `.body`
  - `ast.Constant`: return `.value` (reject non-numeric)
  - `ast.Name`: look up `.id` in names, raise FormulaException if not found
  - `ast.BinOp`: evaluate left and right, apply `_BINARY_OPS[type(node.op)]`
  - `ast.UnaryOp`: evaluate operand, apply `_UNARY_OPS[type(node.op)]`
  - `ast.Call`: look up function name, evaluate args, call function
  - `ast.Compare`: evaluate comparands, apply comparison ops
  - `ast.IfExp`: evaluate test, return body or orelse
  - Default: raise FormulaException with descriptive message
- [ ] Replace the `eval()` call in `FormulaEvaluator.evaluate()` with:
  1. Build names dict (same as before)
  2. Apply caret substitution (same as before)
  3. Call `_parse_formula(eval_formula)` (cached)
  4. Call `_eval_node(tree.body, names)`
- [ ] Run all formula tests:
  `pytest tests/unit/core/test_formula_evaluator.py tests/unit/simulation/test_formula_evaluator.py tests/unit/systems/test_formula_system.py tests/unit/simulation/test_formula_exceptions.py tests/unit/systems/test_formula_overflow_underflow.py -x`
- [ ] Verify: `grep -rn "eval(" game/core/formula_evaluator.py` returns zero results (no eval() calls)
- [ ] Verify: all existing formula tests pass identically

**Notes:** The error handling must produce the same exception types (FormulaException) with the same error codes. The AST walker catches NameError/SyntaxError/etc. the same way eval() did, mapped to the same FormulaException subtypes.

---

### Task 2.6: Add LRU cache and verify performance [Simple]
**File:** `game/core/formula_evaluator.py`
**Tests:** `tests/unit/core/test_formula_evaluator.py` (extend)

- [ ] Verify `_parse_formula` is decorated with `@functools.lru_cache(maxsize=256)` (done in 2.5)
- [ ] Add test: call evaluate() with same formula 10 times, check `_parse_formula.cache_info().hits >= 9`
- [ ] Add test: call evaluate() with different formula strings, check cache grows
- [ ] Add test: caret_as_power=True produces different cache entry than False for same formula string containing `^`
- [ ] Run tests: `pytest tests/unit/core/test_formula_evaluator.py -x`

**Notes:** If caret substitution is done before caching, the cache key is the substituted formula string. This is correct since `"x ^ 2"` with caret_as_power becomes `"x ** 2"` and should cache under that key.

---

### Task 2.7: Phase 2 regression test [Simple]
**Tests:** `pytest tests/ --testmon`

- [ ] Run incremental test suite: `pytest tests/ --testmon`
- [ ] Fix any regressions
- [ ] Verify test count is >= 14783
- [ ] Verify: `grep -rn "from game\.simulation\.formula_system import" game/` shows zero hits in production code (only in tests via re-exports)
- [ ] Verify: `grep -rn "eval(" game/core/formula_evaluator.py` returns zero results

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] FormulaEvaluator importable from `game.core.formula_evaluator`
- [ ] `game/simulation/formula_system.py` is a thin re-export shim
- [ ] No production code in `game/` imports FormulaEvaluator from simulation path
- [ ] No `eval()` calls in `game/core/formula_evaluator.py`
- [ ] LRU cache functioning (cache_info shows hits)
- [ ] All existing formula tests pass unchanged
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 3
