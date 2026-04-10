# PROJ-242 Plan-Code Alignment Review
**Date:** 2026-04-10
**Reviewer:** Plan-Code Alignment Analyst
**Verdict:** COMPLETE with post-completion architectural drift from PROJ-257

---

## Executive Summary

PROJ-242 (Unified Formula Evaluation System) is genuinely complete. All planned work was executed: FormulaEvaluator class exists with FormulaContext, all callers migrated, old functions deleted, modifier_effects delegates correctly, and backward-compatible aliases are in place. However, a subsequent project (PROJ-257) moved FormulaEvaluator from its PROJ-242 location (`game/simulation/formula_system.py`) to `game/core/formula_evaluator.py` and replaced the `eval()` sandbox with an AST tree walker. This means many file paths, line numbers, and implementation details in the PROJ-242 plan no longer match the current codebase. These are not PROJ-242 failures -- they are expected post-completion drift from a later project.

**Findings: 7 total (0 blocking, 2 moderate, 5 informational)**

---

## Findings

### FIND-01: FormulaEvaluator canonical location moved by PROJ-257
**Task:** All phases
**Plan Reference:** Throughout plan -- FormulaEvaluator described as living in `game/simulation/formula_system.py`
**Actual Code:** FormulaEvaluator lives in `game/core/formula_evaluator.py` (PROJ-257 extraction). `game/simulation/formula_system.py` is now a 20-line re-export shim.
**Impact:** Informational. All callers import from `game.core.formula_evaluator`, not `game.simulation.formula_system`. The plan's file references are stale but the work was done correctly before the move.
**Proposed Fix:** No action needed. Plan is a historical record. If the plan is ever referenced for future work, readers should note PROJ-257 moved the canonical location.

### FIND-02: eval() replaced with AST walker by PROJ-257
**Task:** Task 4.3 (Final verification)
**Plan Reference:** `plan.md:461` -- "Grep for direct `eval(` calls in `game/simulation/` -- should only be in `FormulaEvaluator.evaluate()` in `formula_system.py`"
**Actual Code:** There are ZERO `eval()` calls anywhere in `game/`. PROJ-257 replaced the `eval()` sandbox with an AST tree walker (`_parse_formula()` + `_eval_node()` in `game/core/formula_evaluator.py`). The FormulaEvaluator docstring explicitly states "Uses an AST tree walker for safe evaluation (no eval())."
**Impact:** Informational. This is strictly better than the plan's expected state -- the AST walker is more secure than a sandboxed `eval()`.
**Proposed Fix:** None needed.

### FIND-03: Callers import from game.core.formula_evaluator, not game.simulation.formula_system
**Task:** Tasks 2.2-2.6 (Migrate callers), Task 3.1 (Migrate modifier_effects)
**Plan Reference:** `plan.md:306` -- callers should import `from game.simulation.formula_system import FormulaEvaluator`
**Actual Code:** All 6 production callers import from `game.core.formula_evaluator`:
- `game/simulation/components/component_stats_calculator.py:16` -- `from game.core.formula_evaluator import FormulaEvaluator`
- `game/simulation/components/component_resource_manager.py:14` -- `from game.core.formula_evaluator import FormulaEvaluator`
- `game/simulation/components/abilities/weapons.py:7` -- `from game.core.formula_evaluator import FormulaEvaluator`
- `game/strategy/services/ship_stats_calculator.py:36` -- `from game.core.formula_evaluator import FormulaEvaluator`
- `game/simulation/components/modifier_effects.py:19` -- `from game.core.formula_evaluator import FormulaEvaluator`
- `game/strategy/services/design_validator.py:83` -- `from game.core.formula_evaluator import FormulaEvaluator` (lazy import)
**Impact:** Informational. PROJ-257 moved the canonical location, so callers correctly import from the new location. The `formula_system.py` shim re-exports everything, so either import path would work.
**Proposed Fix:** None needed.

### FIND-04: component_stats_calculator.py uses evaluate() (strict) instead of safe_evaluate()
**Task:** Task 2.2 (Update component_stats_calculator.py)
**Plan Reference:** `plan.md:307-309` -- all 3 call sites should use `FormulaEvaluator.safe_evaluate()`
**Actual Code:** Only 1 of 3 call sites uses `safe_evaluate()` (line 267, abilities recursive evaluator). The other 2 (line 199, line 239) use strict `FormulaEvaluator.evaluate()` with explicit try/except wrapping that re-raises FormulaException with component context.
**Impact:** Moderate (plan inaccuracy). This is actually the better design -- PROJ-246 (Silent Formula Evaluation Failure) deliberately changed these from safe_evaluate to strict evaluate at data load time, so formula errors are caught early rather than silently defaulting to 0. The plan predates PROJ-246's changes.
**Proposed Fix:** Plan is a historical record. The current code is correct per PROJ-246 decisions. No code change needed.

### FIND-05: weapons.py line 33 uses evaluate() (strict), not safe_evaluate()
**Task:** Task 2.4 (Update weapons.py)
**Plan Reference:** `plan.md:323` -- L33 should use `FormulaEvaluator.safe_evaluate()`
**Actual Code:** Line 33 uses `FormulaEvaluator.evaluate()` (strict). Line 216 correctly uses `FormulaEvaluator.safe_evaluate()` for runtime damage formulas.
**Impact:** Moderate (plan inaccuracy). Same root cause as FIND-04: PROJ-246 made load-time formula evaluation strict. The `_parse_formula_field` function at line 33 is called during weapon initialization (data load), so strict is correct. Line 216 (`calculate_damage`) is runtime, so safe_evaluate is correct.
**Proposed Fix:** None needed. Plan is historical; code is correct per PROJ-246.

### FIND-06: design_validator.py is an uncatalogued caller
**Task:** Plan scope / Key Files Reference
**Plan Reference:** `plan.md:58-78` -- Key Files Reference lists 5 production callers + 1 vestigial import. `design_validator.py` is not mentioned.
**Actual Code:** `game/strategy/services/design_validator.py:83` has a lazy import of FormulaEvaluator. This file was likely added after PROJ-242 was planned (or after it completed).
**Impact:** Informational. The file correctly imports from `game.core.formula_evaluator`, so it uses the unified evaluator. No missed migration.
**Proposed Fix:** None needed. The file was not a migration target for PROJ-242.

### FIND-07: All line numbers in plan are stale
**Task:** All tasks referencing specific line numbers
**Plan Reference:** Numerous line references throughout (e.g., L62 for component.py vestigial import, L151/L177/L198 for component_stats_calculator.py, L117-184 for modifier_effects evaluate_formula, etc.)
**Actual Code:** All line numbers are shifted due to PROJ-242's own changes plus subsequent PROJ-246, PROJ-257, and other projects. Examples:
- Plan says `component.py:L62` had vestigial import -- import is now gone (correctly removed)
- Plan says `modifier_effects.py:L117-184` for old evaluate_formula -- actual evaluate_formula is now at L116-135 (thin delegation)
- Plan says `error_codes.py:L120` for FORMULA_SYNTAX_ERROR -- actual is L121 (close, minor shift)
- Plan says `modifier_schema.py:L237` for validate_formula call -- actual is L237 (exact match)
**Impact:** Informational. Line numbers in plans always drift. The plan's line numbers were correct at the time of writing.
**Proposed Fix:** None needed. Plans are point-in-time artifacts.

---

## Verification Summary

| Verification Point | Status | Notes |
|---|---|---|
| FormulaEvaluator class exists | PASS | In `game/core/formula_evaluator.py` (moved from formula_system.py by PROJ-257) |
| FormulaContext frozen dataclass | PASS | `caret_as_power`, `extra_functions` fields present |
| evaluate() classmethod | PASS | With AST walker (upgraded from eval() by PROJ-257) |
| safe_evaluate() classmethod | PASS | Wraps evaluate() with try/except, returns default |
| validate() classmethod | PASS | AST walk with allowed names check |
| DEFAULT_CONTEXT constant | PASS | `FormulaContext()` |
| MODIFIER_CONTEXT constant | PASS | `FormulaContext(caret_as_power=True, extra_functions={'ln': math.log})` |
| Old string constants deleted | PASS | No FORMULA_ERROR_SYNTAX etc. in production code |
| Old functions deleted | PASS | formula_system.py is now a re-export shim |
| Module-level aliases exist | PASS | Both in formula_system.py and formula_evaluator.py |
| component_stats_calculator.py migrated | PASS | Imports FormulaEvaluator from game.core.formula_evaluator |
| component_resource_manager.py migrated | PASS | Imports FormulaEvaluator from game.core.formula_evaluator |
| weapons.py migrated | PASS | Imports FormulaEvaluator from game.core.formula_evaluator |
| ship_stats_calculator.py migrated | PASS | Imports FormulaEvaluator from game.core.formula_evaluator |
| Vestigial import removed from component.py | PASS | No formula imports in component.py |
| modifier_effects.py evaluate_formula delegates | PASS | Calls FormulaEvaluator.evaluate() with MODIFIER_CONTEXT, wraps float() |
| modifier_effects.py validate_formula delegates | PASS | Calls FormulaEvaluator.validate() with ['param'] and MODIFIER_CONTEXT |
| No direct eval() calls in modifier_effects.py | PASS | Zero eval() calls |
| import math removed from modifier_effects.py | PASS | Not present |
| import ast removed from modifier_effects.py | PASS | Not present |
| ErrorCode import removed from modifier_effects.py | PASS | Not present |
| Test file exists | PASS | `tests/unit/simulation/test_formula_evaluator.py` |
| modifier_schema.py L237 still delegates | PASS | `ModifierEffectEvaluator.validate_formula(effect['formula'])` at L237 |
| No production code imports old function names | PASS | Only aliases in formula_system.py and formula_evaluator.py |

---

## Conclusion

PROJ-242 is genuinely complete. Every planned deliverable was implemented. The discrepancies found are all attributable to subsequent projects (PROJ-246 for strict evaluation, PROJ-257 for core extraction and AST walker) that improved upon PROJ-242's work. No code changes are needed.
