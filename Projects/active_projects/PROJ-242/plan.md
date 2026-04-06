# PROJ-242: Unified Formula Evaluation System

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-242` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-242 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Create Unified FormulaEvaluator | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Migrate formula_system.py Callers | Complete | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Migrate modifier_effects.py Callers | Complete | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Delete Old Code and Final Cleanup | Complete | [phase_4_checklist.md](phase_4_checklist.md) |

## Current State
**Last Updated:** 2026-04-05
**Active Phase:** Complete
**Last Action:** All 4 phases complete. Full test suite passes (14403 passed, 0 failures).
**Next Action:** None -- project complete.
**Blockers:** None
**Context for Next Agent:** Project is fully implemented. FormulaEvaluator is the single eval path. Old functions deleted and replaced with aliases. ModifierEffectEvaluator delegates to FormulaEvaluator. No docs updates needed (public API surface unchanged).

## Overview
Two nearly identical safe-eval formula evaluation systems exist in the simulation layer:
- **`formula_system.py`** (173 lines) -- module-level functions `evaluate_math_formula()`, `safe_evaluate_math_formula()`, `validate_formula()`
- **`modifier_effects.py`** (327 lines) -- static/class methods `ModifierEffectEvaluator.evaluate_formula()`, `.validate_formula()`, `.validate_modifier_definition()`

Both use the same `eval()` sandbox pattern with whitelisted math functions but differ in error codes, context building, allowed names, and caret substitution. This project merges them into a single `FormulaEvaluator` class with a parameterizable `FormulaContext`, so all formula evaluation flows through one code path.

## Goals
- **Single eval path:** One `FormulaEvaluator.evaluate()` method used by all callers
- **Parameterizable context:** `FormulaContext` dataclass specifies caret substitution and extra functions per use case
- **Consistent error handling:** All formula errors raise `FormulaException` with `ErrorCode` enum values (not string codes)
- **No behavioral changes:** All existing tests pass without modification; formulas produce identical results
- **Eradicate old systems:** Delete `evaluate_math_formula()`, `safe_evaluate_math_formula()`, and `ModifierEffectEvaluator.evaluate_formula()` / `validate_formula()` once migration is complete

## Scope
**In Scope:**
- `game/simulation/formula_system.py` -- replace module-level functions with unified class
- `game/simulation/components/modifier_effects.py` -- delegate to unified evaluator
- All callers of `evaluate_math_formula` / `safe_evaluate_math_formula` (5 production files, 1 vestigial import)
- All callers of `ModifierEffectEvaluator.evaluate_formula` / `validate_formula` (internal + `modifier_schema.py`)
- Error code consolidation (string codes `"F001"`-`"F004"` -> `ErrorCode` enum)
- Validation functions (`validate_formula` in both modules)

**Out of Scope:**
- `ModifierEffect` dataclass (unchanged -- it's a data object, not an evaluator)
- `ModifierEffectEvaluator.evaluate_modifier()` business logic (stays, just delegates formula eval)
- `ModifierEffectEvaluator.validate_modifier_definition()` (stays, just delegates formula validation)
- Changes to formula strings in data files
- Changes to test data or test scenarios

## Key Files Reference
| Component | File Path | Lines | Class/Function |
|-----------|-----------|-------|----------------|
| Formula system (primary target) | `game/simulation/formula_system.py` | 173 | `evaluate_math_formula()`, `safe_evaluate_math_formula()`, `validate_formula()` |
| Modifier effects (secondary target) | `game/simulation/components/modifier_effects.py` | 327 | `ModifierEffectEvaluator.evaluate_formula()` (L117-184), `.validate_formula()` (L255-296), `.validate_modifier_definition()` (L298-327) |
| Error codes | `game/core/error_codes.py` | - | `ErrorCode.FORMULA_SYNTAX_ERROR` (L120), `.FORMULA_UNDEFINED_VAR` (L123), `.EVAL_ERROR` (L126), `.FORMULA_GENERAL_ERROR` (L129) |
| Exceptions | `game/core/exceptions.py` | - | `FormulaException` |
| Caller: Component (vestigial import) | `game/simulation/components/component.py` | L62 | Import only, never called directly |
| Caller: Resource manager | `game/simulation/components/component_resource_manager.py` | L14, L112 | `safe_evaluate_math_formula()` |
| Caller: Stats calculator | `game/simulation/components/component_stats_calculator.py` | L16, L151, L177, L198 | `safe_evaluate_math_formula()` (3 call sites) |
| Caller: Weapons | `game/simulation/components/abilities/weapons.py` | L7, L33, L207 | `safe_evaluate_math_formula()` (2 call sites) |
| Caller: Ship stats calculator | `game/strategy/services/ship_stats_calculator.py` | L36, L659 | `safe_evaluate_math_formula()` (1 call site) |
| Caller: Modifier schema | `game/simulation/components/modifier_schema.py` | L237 | `ModifierEffectEvaluator.validate_formula()` |
| Tests: Formula system (security+func) | `tests/unit/systems/test_formula_system.py` | 255 | `TestFormulaSystemSecurity`, `TestFormulaSystemFunctionality`, etc. |
| Tests: Formula exceptions | `tests/unit/simulation/test_formula_exceptions.py` | 174 | `TestFormulaExceptionRaising`, `TestFormulaExceptionErrorCodes` |
| Tests: Formula overflow/underflow | `tests/unit/systems/test_formula_overflow_underflow.py` | 286 | `TestFloatOverflow`, `TestNaNHandling`, etc. |
| Tests: Modifier effects | `tests/unit/simulation/components/test_modifier_effects.py` | 336 | `TestEvaluateFormula`, `TestValidateFormula`, etc. |
| Tests: Modifier evaluator | `tests/unit/modifiers/test_modifier_effect_evaluator.py` | 212 | `TestModifierEffectEvaluator` |
| Tests: Formula validation | `tests/unit/modifiers/test_formula_validation.py` | 163 | `TestFormulaValidation`, `TestModifierLoadValidation` |
| Tests: Formula edge cases | `tests/unit/modifiers/test_formula_edge_cases.py` | 319 | `TestFormulaDivisionByZero`, `TestRealWorldFormulas`, etc. |
| Tests: Formula error handling | `tests/unit/modifiers/test_formula_error_handling.py` | 164 | `TestFormulaErrorHandling` |

## Decisions Log
| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-04-05 | Keep unified evaluator in `formula_system.py` | It's the existing home for formula evaluation; modifier_effects.py is about modifier business logic, not eval |
| 2026-04-05 | Use `ErrorCode` enum (not string constants) | modifier_effects.py already uses this; formula_system.py's string codes `"F001"`-`"F004"` are the older pattern |
| 2026-04-05 | Support caret substitution as a context option | Modifier formulas use `^` for exponentiation; component formulas don't. Must be opt-in per context. |
| 2026-04-05 | Superset of allowed functions | Unified evaluator allows the union of both sets. No formula breaks from having more available functions. |
| 2026-04-05 | Keep `safe_evaluate` as thin wrapper on the class | 7 call sites across 5 files use it -- replacing all with try/except is churn for no gain. |
| 2026-04-05 | `FormulaContext` as a frozen dataclass | Two fields: `caret_as_power: bool = False`, `extra_functions: Dict[str, Any] = field(default_factory=dict)`. Simple and sufficient. |
| 2026-04-05 | Modifier `evaluate_formula`/`validate_formula` become thin delegations | Keep method signatures identical so `evaluate_modifier()` and `validate_modifier_definition()` don't change at all |
| 2026-04-05 | Remove vestigial import from `component.py` | Line 62 imports `safe_evaluate_math_formula` but it's never called -- leftover from PROJ-44 extraction |

## Initial Analysis

### Side-by-Side Comparison

| Aspect | `formula_system.py` | `modifier_effects.py` | Unified Behavior |
|--------|---------------------|----------------------|------------------|
| **Entry point** | `evaluate_math_formula(formula, context)` (L81) | `ModifierEffectEvaluator.evaluate_formula(formula, context)` (L117) | `FormulaEvaluator.evaluate(formula, context, formula_context)` |
| **Safe wrapper** | `safe_evaluate_math_formula(formula, context, default)` (L149) | None (caller catches in `evaluate_modifier` L231-239) | `FormulaEvaluator.safe_evaluate(formula, context, default, formula_context)` |
| **Validation** | `validate_formula(formula, allowed_variables)` (L39) | `ModifierEffectEvaluator.validate_formula(formula)` (L255) | `FormulaEvaluator.validate(formula, allowed_variables, formula_context)` |
| **Caret `^`** | No substitution (Python XOR) | Replaced with `**` (L157) | Controlled by `FormulaContext.caret_as_power` |
| **Allowed math** | All `math.*` (L106) | Only `ln, log, log10, sqrt, abs, min, max, pi, e` (L135-146) | All `math.*` + `ln` alias (superset) |
| **Allowed builtins** | `abs, min, max, round, sum, len, int, float, pow` (L22) | `abs, min, max` only (via hand-picked context) | Full `ALLOWED_BUILTINS` set (superset) |
| **Security check** | `DANGEROUS_NAMES` set (L26-30) used in validate + broad catch | None explicit (relies on `__builtins__: {}`) | `DANGEROUS_NAMES` check in validate, `__builtins__: {}` in eval |
| **Error: syntax** | `FormulaException(code="F001")` (L124) | `FormulaException(code=ErrorCode.FORMULA_SYNTAX_ERROR.value)` (L162) | `ErrorCode.FORMULA_SYNTAX_ERROR` |
| **Error: undefined** | `FormulaException(code="F002")` (L130) | `FormulaException(code=ErrorCode.FORMULA_UNDEFINED_VAR.value)` (L169) | `ErrorCode.FORMULA_UNDEFINED_VAR` |
| **Error: runtime** | `FormulaException(code="F003")` (L136) | `FormulaException(code=ErrorCode.EVAL_ERROR.value)` (L174) | `ErrorCode.EVAL_ERROR` |
| **Error: general** | `FormulaException(code="F004")` (L142) | `FormulaException(code=ErrorCode.FORMULA_GENERAL_ERROR.value)` (L180) | `ErrorCode.FORMULA_GENERAL_ERROR` |
| **Return type** | `Union[int, float]` (preserves eval result type) | `float` (always `float(result)` L160) | `Union[int, float]` (preserve native type; modifier path wraps in `float()`) |
| **Context build** | `math.__dict__` + builtins module lookup (L106-112) | Hand-picked dict (L135-146) | `math.__dict__` + builtins + `ln` alias |

### What's Identical
1. Both disable `__builtins__` in eval: `{"__builtins__": {}}` (formula_system L122, modifier_effects L159)
2. Both build an `error_context` dict with `formula` and `available_vars` keys
3. Both catch the same 4 exception categories: `SyntaxError`, `NameError`, `(ZeroDivision/Value/Arithmetic)Error`, broad `Exception`
4. Both raise `FormulaException` with code + context for all error paths
5. Both use AST walking for validation (check `ast.Name` nodes)

### What Differs
1. **Caret substitution** -- only modifier_effects does `formula.replace('^', '**')` (L157)
2. **Function availability** -- modifier_effects has `ln` alias for `math.log`; formula_system has full `math.*` + more builtins
3. **Error code format** -- formula_system uses bare strings `"F001"`, modifier_effects uses `ErrorCode.FORMULA_SYNTAX_ERROR.value` (both resolve to the same string values: `"F001"`, `"F002"`, `"F003"`, `"F004"`)
4. **Return type** -- modifier_effects forces `float()`, formula_system preserves native type
5. **Validation allowed names** -- formula_system accepts caller-provided list; modifier_effects hardcodes `{param, ln, log, ...}`

## Swarm Findings Summary

### Architecture
- `FormulaException` is defined in `game/core/exceptions.py` and used by both systems
- `ErrorCode` enum is in `game/core/error_codes.py` -- formula codes are `F001`-`F004` at lines 120-129
- The string constants in `formula_system.py` (`FORMULA_ERROR_SYNTAX = "F001"` etc.) are redundant with `ErrorCode.FORMULA_SYNTAX_ERROR.value = "F001"` -- they produce identical string values
- No circular dependency risk: `formula_system.py` imports from `game.core` only; `modifier_effects.py` imports from `game.core` only

### Dependency Map

**formula_system.py callers (7 call sites across 5 files + 1 vestigial):**
| File | Line | Function Called | Context |
|------|------|----------------|---------|
| `component.py` | L62 | `safe_evaluate_math_formula` (import only) | Vestigial -- never called. Remove. |
| `component_stats_calculator.py` | L151 | `safe_evaluate_math_formula(formula, eval_context)` | Evaluating component attribute formulas |
| `component_stats_calculator.py` | L177 | `safe_evaluate_math_formula(amount[1:], eval_context)` | Evaluating resource cost formulas |
| `component_stats_calculator.py` | L198 | `safe_evaluate_math_formula(obj[1:], ctx)` | Recursive formula eval in abilities |
| `component_resource_manager.py` | L112 | `safe_evaluate_math_formula(amount[1:], eval_context, default=0)` | Runtime resource cost eval |
| `weapons.py` | L33 | `safe_evaluate_math_formula(formula_str, formula_context)` | Weapon stat formula eval |
| `weapons.py` | L207 | `safe_evaluate_math_formula(self.damage_formula, context)` | Seeker damage formula eval |
| `ship_stats_calculator.py` | L659 | `safe_evaluate_math_formula(val[1:], context, default=default)` | Strategy-layer stat formulas |

**modifier_effects.py internal callers:**
| File | Line | Function Called | Context |
|------|------|----------------|---------|
| `modifier_effects.py` | L232 | `cls.evaluate_formula(formula, context)` | Inside `evaluate_modifier()` |
| `modifier_effects.py` | L322 | `cls.validate_formula(formula)` | Inside `validate_modifier_definition()` |
| `modifier_schema.py` | L237 | `ModifierEffectEvaluator.validate_formula(effect['formula'])` | Schema validation at load time |

### Test Impact
- **13 test files** cover formula evaluation (see Key Files Reference)
- All tests import from either `formula_system` or `modifier_effects` directly
- Tests that check error codes use string values (`"F001"`, `"F002"`, `"F003"`) -- these match `ErrorCode` enum `.value` so no change needed
- The overflow/underflow tests (286 lines) are thorough and test edge cases well
- No tests directly test the integration between the two systems (they're independent)

### Key Patterns to Reuse
- **Facade/Delegate pattern** (from `docs/02_PATTERNS.md`): `ModifierEffectEvaluator.evaluate_formula()` becomes a thin delegation to `FormulaEvaluator.evaluate()` -- same pattern used in Ship -> ShipCombatEngine
- **CQRS-lite**: `FormulaEvaluator.evaluate()` is a pure query with no side effects

### Risks Identified
1. **Error code string comparison in tests** -- Tests like `test_modifier_effects.py` L167 check `exc_info.value.code == "F001"`. Since `ErrorCode.FORMULA_SYNTAX_ERROR.value == "F001"`, this is safe. **No risk.** Mitigation: verify all tests pass.
2. **Return type difference** -- `modifier_effects.py` wraps result in `float()` (L160). If unified evaluator preserves native type (int for `pow(2,3)`), the `float()` wrapping must happen in the delegation layer. **Low risk.** Mitigation: modifier's `evaluate_formula` wraps `float()` around the delegation result.
3. **`ln` alias** -- `formula_system.py` doesn't have `ln` as an alias for `math.log`. Adding it to the unified evaluator is safe (no existing formula uses `ln` via formula_system). **No risk.**

### Opportunities Discovered
- `component.py` line 62 has a vestigial import that can be cleaned up
- The four string constants (`FORMULA_ERROR_SYNTAX` etc.) in `formula_system.py` lines 33-36 can be deleted since `ErrorCode` enum covers them

---

## Phases

### Phase 1: Create Unified FormulaEvaluator [Medium]
**Objective:** Create the unified `FormulaEvaluator` class with `FormulaContext` dataclass in `formula_system.py`, with full test coverage. Old functions remain working and unchanged during this phase.

#### Task 1.1: Write tests for FormulaEvaluator [Medium]
**File:** `tests/unit/simulation/test_formula_evaluator.py` (new)
**Tests:** TDD -- these ARE the tests. Run: `pytest tests/unit/simulation/test_formula_evaluator.py -v`
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

#### Task 1.2: Implement FormulaContext dataclass [Simple]
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

#### Task 1.3: Implement FormulaEvaluator class [Medium]
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

#### Task 1.4: Verify no regressions [Simple]
**Tests:** Full test suite
- [ ] Run existing formula tests: `pytest tests/unit/systems/test_formula_system.py tests/unit/systems/test_formula_overflow_underflow.py tests/unit/simulation/test_formula_exceptions.py -v`
- [ ] Run modifier tests: `pytest tests/unit/modifiers/ tests/unit/simulation/components/test_modifier_effects.py -v`
- [ ] Run full test suite: `python scripts/test_sharded.py`
- [ ] Confirm zero test failures and zero test changes

---

### Phase 2: Migrate formula_system.py Callers [Medium]
**Objective:** Update all callers of `evaluate_math_formula` / `safe_evaluate_math_formula` to use the new `FormulaEvaluator`. Old module-level functions still exist but are no longer imported by production code.

#### Task 2.1: Baseline verification [Simple]
**Tests:** `pytest tests/unit/simulation/ tests/unit/strategy/ -v`
- [ ] Run all tests that cover caller files -- establish green baseline
- [ ] No new tests needed; existing tests cover caller behavior

#### Task 2.2: Update component_stats_calculator.py (3 call sites) [Simple]
**File:** `game/simulation/components/component_stats_calculator.py`
**Tests:** `pytest tests/unit/simulation/components/test_component_stats_calculator.py -v`
- [ ] Change import (L16): `from game.simulation.formula_system import safe_evaluate_math_formula` -> `from game.simulation.formula_system import FormulaEvaluator`
- [ ] Replace call (L151): `safe_evaluate_math_formula(formula, eval_context)` -> `FormulaEvaluator.safe_evaluate(formula, eval_context)`
- [ ] Replace call (L177): `safe_evaluate_math_formula(amount[1:], eval_context)` -> `FormulaEvaluator.safe_evaluate(amount[1:], eval_context)`
- [ ] Replace call (L198): `safe_evaluate_math_formula(obj[1:], ctx)` -> `FormulaEvaluator.safe_evaluate(obj[1:], ctx)`
- [ ] Run tests -- confirm pass

#### Task 2.3: Update component_resource_manager.py (1 call site) [Simple]
**File:** `game/simulation/components/component_resource_manager.py`
**Tests:** `pytest tests/unit/simulation/components/test_component_resource_manager.py -v`
- [ ] Change import (L14): `from game.simulation.formula_system import safe_evaluate_math_formula` -> `from game.simulation.formula_system import FormulaEvaluator`
- [ ] Replace call (L112): `safe_evaluate_math_formula(amount[1:], eval_context, default=0)` -> `FormulaEvaluator.safe_evaluate(amount[1:], eval_context, default=0)`
- [ ] Run tests -- confirm pass

#### Task 2.4: Update weapons.py (2 call sites) [Simple]
**File:** `game/simulation/components/abilities/weapons.py`
**Tests:** `pytest tests/unit/simulation/components/abilities/test_weapons_isolation.py -v`
- [ ] Change import (L7): `from game.simulation.formula_system import safe_evaluate_math_formula` -> `from game.simulation.formula_system import FormulaEvaluator`
- [ ] Replace call (L33): `safe_evaluate_math_formula(formula_str, formula_context)` -> `FormulaEvaluator.safe_evaluate(formula_str, formula_context)` (note: `formula_context` here is the caller's variable name for `context` dict, NOT `FormulaContext` -- no rename needed)
- [ ] Replace call (L207): `safe_evaluate_math_formula(self.damage_formula, context)` -> `FormulaEvaluator.safe_evaluate(self.damage_formula, context)`
- [ ] Run tests -- confirm pass

#### Task 2.5: Update ship_stats_calculator.py (1 call site) [Simple]
**File:** `game/strategy/services/ship_stats_calculator.py`
**Tests:** `pytest tests/unit/strategy/ship_stats/ -v`
- [ ] Change import (L36): `from game.simulation.formula_system import safe_evaluate_math_formula` -> `from game.simulation.formula_system import FormulaEvaluator`
- [ ] Replace call (L659): `safe_evaluate_math_formula(val[1:], context, default=default)` -> `FormulaEvaluator.safe_evaluate(val[1:], context, default=default)`
- [ ] Run tests -- confirm pass

#### Task 2.6: Remove vestigial import from component.py [Simple]
**File:** `game/simulation/components/component.py`
**Tests:** `pytest tests/unit/simulation/components/ -v`
- [ ] Remove unused import (L62): `from game.simulation.formula_system import safe_evaluate_math_formula`
- [ ] Run tests -- confirm pass

#### Task 2.7: Verify all formula_system callers migrated [Simple]
**Tests:** `pytest tests/unit/simulation/ tests/unit/strategy/ -v`
- [ ] Grep for `evaluate_math_formula` in `game/` -- only `formula_system.py` itself should remain
- [ ] Grep for `safe_evaluate_math_formula` in `game/` -- only `formula_system.py` itself should remain
- [ ] Grep for `from game.simulation.formula_system import` -- should only import `FormulaEvaluator` (or `FormulaContext`)
- [ ] Run simulation + strategy tests: `pytest tests/unit/simulation/ tests/unit/strategy/ -v`

---

### Phase 3: Migrate modifier_effects.py Callers [Medium]
**Objective:** Replace `ModifierEffectEvaluator.evaluate_formula()` and `validate_formula()` with thin delegations to `FormulaEvaluator`.

#### Task 3.1: Update ModifierEffectEvaluator.evaluate_formula [Simple]
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

#### Task 3.2: Update ModifierEffectEvaluator.validate_formula [Simple]
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

**IMPORTANT NOTE:** The old `validate_formula` allowed `{'param', 'ln', 'log', 'log10', 'sqrt', 'abs', 'min', 'max', 'pi', 'e', 'True', 'False'}`. The unified `validate()` builds its allowed set from `ALLOWED_MATH_FUNCTIONS | ALLOWED_BUILTINS | {'ln'} | set(allowed_variables)`. Since `ALLOWED_MATH_FUNCTIONS` includes all `math.*` names (which includes `log`, `log10`, `sqrt`, `pi`, `e`) and `ALLOWED_BUILTINS` includes `abs`, `min`, `max`, plus `True`/`False` are Python builtins that pass through `ast.Name` but are actually `ast.Constant` in modern Python (3.8+), this is a superset. Existing valid formulas remain valid. The only behavioral change: more names are now "allowed" in validation, but since `eval()` already had them available, this is correct (validation now matches evaluation capability).

#### Task 3.3: Verify all modifier callers working [Simple]
**Tests:** Full modifier + simulation test suite
- [ ] Run: `pytest tests/unit/modifiers/ -v` -- all pass
- [ ] Run: `pytest tests/unit/simulation/components/test_modifier_effects.py -v` -- all pass
- [ ] Run: `pytest tests/unit/simulation/ -v` -- all pass
- [ ] Verify `modifier_schema.py` L237 still works (it calls `ModifierEffectEvaluator.validate_formula()` which now delegates)

---

### Phase 4: Delete Old Code and Final Cleanup [Simple]
**Objective:** Remove duplicated code, old string error code constants, and verify everything works through one code path.

#### Task 4.1: Clean up formula_system.py [Simple]
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

**CRITICAL DECISION POINT:** The 3 existing test files import `evaluate_math_formula`, `safe_evaluate_math_formula`, and `validate_formula` by name. Two options:
1. **Module-level aliases** (above) -- zero test changes needed
2. **Update test imports** -- change all 3 test files to use `FormulaEvaluator.*`

Recommendation: Use aliases. The test files are testing formula evaluation behavior, not API surface. Changing imports is churn that doesn't improve test quality. If preferred, update test imports in a follow-up.

#### Task 4.2: Clean up modifier_effects.py [Simple]
**File:** `game/simulation/components/modifier_effects.py`
**Tests:** `pytest tests/unit/simulation/components/test_modifier_effects.py tests/unit/modifiers/ -v`
- [ ] Verify `evaluate_formula` and `validate_formula` are thin delegations (should be from Task 3.1/3.2)
- [ ] Verify no direct `eval(` call remains in file
- [ ] Verify `import math` is removed (if not needed)
- [ ] Verify `import ast` is removed (if not needed)
- [ ] Verify `from game.core.error_codes import ErrorCode` is removed (if not needed)
- [ ] Run tests -- confirm pass

#### Task 4.3: Final verification [Simple]
**Tests:** Full test suite
- [ ] Grep for direct `eval(` calls in `game/simulation/` -- should only be in `FormulaEvaluator.evaluate()` in `formula_system.py`
- [ ] Grep for `FORMULA_ERROR_SYNTAX` / `FORMULA_ERROR_UNDEFINED` etc. -- should not exist anywhere
- [ ] Grep for old function imports: `from game.simulation.formula_system import evaluate_math_formula` -- should not appear in `game/` (only in `tests/` via aliases)
- [ ] Run full test suite: `python scripts/test_sharded.py`
- [ ] Check if any docs reference formula evaluation: search `docs/` for "formula" and update if needed
- [ ] Update `docs/01_ARCHITECTURE.md` or `docs/02_PATTERNS.md` if formula evaluation is documented there

---

## Verification Checklist

### Project Start (REQUIRED)
- [ ] Read `docs/` foundation docs (01_ARCHITECTURE, 02_PATTERNS, 03_CONVENTIONS)
- [ ] Run full test suite -- establish baseline

### After Each Phase
- [ ] Run targeted tests for changed files
- [ ] No new `eval()` calls outside FormulaEvaluator
- [ ] All error paths raise FormulaException with ErrorCode enum values

### Final Verification
- [ ] `pytest tests/unit/simulation/ -v` -- all pass
- [ ] `pytest tests/unit/modifiers/ -v` -- all pass
- [ ] `pytest tests/unit/systems/test_formula_system.py tests/unit/systems/test_formula_overflow_underflow.py -v` -- all pass
- [ ] `pytest tests/unit/strategy/ -v` -- all pass
- [ ] `python scripts/test_sharded.py` -- full suite green
- [ ] Grep confirms single `eval()` call site in FormulaEvaluator
- [ ] No imports of old function names remain in `game/` (only in `tests/` via aliases)
- [ ] `modifier_effects.py` has no direct `eval()` call
- [ ] `formula_system.py` has no string error code constants

---

## Audit Log
| Cycle | Date | Findings | Resolution |
|-------|------|----------|------------|
| 1 | | | |

## Completion Checklist
- [ ] All Phase 1 tasks checked off
- [ ] All Phase 2 tasks checked off
- [ ] All Phase 3 tasks checked off
- [ ] All Phase 4 tasks checked off
- [ ] All tests passing
- [ ] Regression tests passing
- [ ] Audit passed (no significant issues)
- [ ] User verified

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log
