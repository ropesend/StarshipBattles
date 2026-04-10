# PROJ-242 Scope Gap Analysis Report
**Date:** 2026-04-10
**Reviewer:** Scope Gap Analyst
**Verdict:** NO BLOCKING GAPS -- project scope is adequately covered

---

## Executive Summary

PROJ-242 (Unified Formula Evaluation System) claims COMPLETE status. This analysis looks for areas within the project's stated scope that were missed, and for changes since completion (2026-04-05) that may have created new gaps. The project's five stated goals are all met in code. I found **6 findings**: 0 blocking, 1 moderate, 5 low/informational. The moderate finding concerns backward-compatible aliases that contradict the project's "eradicate old systems" goal and the CLAUDE.md policy against backward compatibility layers.

---

## Analysis Methodology

1. Searched for remaining callers of old function names (`evaluate_math_formula`, `safe_evaluate_math_formula`, `validate_formula`) in production code
2. Searched for any `eval()` calls across the entire `game/` tree
3. Searched for formula evaluation patterns (string-startswith-equals, `ast.parse`, `ast.literal_eval`) that bypass FormulaEvaluator
4. Verified FormulaEvaluator is importable and properly exported
5. Verified `game/core/formula_evaluator.py` exists (PROJ-257 extraction) and is the canonical location
6. Checked git log for new callers since 2026-04-05
7. Checked `refactor_plan.md` for completion status

---

## Findings

### GAP-01: Backward-Compatible Aliases Still Exist in Two Locations
**Location:** `game/core/formula_evaluator.py:411-413` and `game/simulation/formula_system.py:17-19`
**Related Goal:** Goal 5 -- Eradicate old systems
**Gap Description:** The project goal says "Delete `evaluate_math_formula()`, `safe_evaluate_math_formula()`... once migration complete." The old function *bodies* were deleted, but module-level aliases pointing old names to new FormulaEvaluator methods remain in two files. Three test files (totaling ~100+ call sites) still import and use the old function names:
- `tests/unit/systems/test_formula_system.py` -- imports `evaluate_math_formula`, `safe_evaluate_math_formula`, `validate_formula`
- `tests/unit/systems/test_formula_overflow_underflow.py` -- imports `evaluate_math_formula`, `safe_evaluate_math_formula`
- `tests/unit/simulation/test_formula_exceptions.py` -- imports `evaluate_math_formula`, `safe_evaluate_math_formula`, `validate_formula`

The aliases in `game/core/formula_evaluator.py:411-413` appear to serve no purpose -- no test or production file imports from that path. They are only reachable if someone does `from game.core.formula_evaluator import evaluate_math_formula`, which nothing does.
**Impact:** The old function names remain importable and discoverable, which works against the stated goal. New code could accidentally use the old names. The CLAUDE.md "System Migration Policy" says "DO NOT keep backward compatibility layers 'just in case'." These aliases are exactly that.
**Proposed Resolution:** Remove aliases from `game/core/formula_evaluator.py:411-413` (unreachable). Update the 3 test files to use `FormulaEvaluator.evaluate()` / `.safe_evaluate()` / `.validate()` directly. Then remove aliases from `game/simulation/formula_system.py:17-19`. This is straightforward -- the old names are simple redirects.
**Effort:** Simple (mechanical find-and-replace in 3 test files + delete 6 alias lines)

### GAP-02: Test Files Still Assert Hardcoded String Error Codes
**Location:** `tests/unit/simulation/components/test_modifier_effects.py:167,173,179`
**Related Goal:** Goal 3 -- Consistent error handling with ErrorCode enum values
**Gap Description:** Three test assertions compare error codes against hardcoded strings (`"F001"`, `"F002"`, `"F003"`) instead of using `ErrorCode.FORMULA_SYNTAX_ERROR.value` etc. While these tests pass (the enum values are the same strings), they bypass the ErrorCode enum that PROJ-242 standardized on. If the enum values ever change, these tests would silently test the wrong thing.

Note: `tests/unit/core/test_exceptions.py:203,206` also uses `"F001"` but this is an exception-infrastructure test, not a formula evaluation test, so it's arguably out of scope.
**Impact:** Low. The tests work today. But they represent a missed consistency sweep -- PROJ-242 moved production code to ErrorCode enum but left test code using raw strings.
**Proposed Resolution:** Update the 3 assertions to use `ErrorCode.FORMULA_SYNTAX_ERROR.value`, `ErrorCode.FORMULA_UNDEFINED_VAR.value`, `ErrorCode.EVAL_ERROR.value`. Add `from game.core.error_codes import ErrorCode` import to the test file.
**Effort:** Simple

### GAP-03: FormulaEvaluator Not Exported from game.core.__init__.py
**Location:** `game/core/__init__.py`
**Related Goal:** Goal 1 -- Single eval path (discoverability)
**Gap Description:** `game/core/__init__.py` exports `FormulaException` and `ErrorCode` (both used by formula evaluation) but does NOT export `FormulaEvaluator` or `FormulaContext`. The `__init__.py` docstring lists the public API for every other core module (exceptions, error codes, math, registry, constants, resources, event logging, validation, config, paths, protocols) but formula evaluation is missing entirely.

All callers currently import directly from `game.core.formula_evaluator` which works fine. But the missing `__init__.py` export means FormulaEvaluator is inconsistent with how every other core API is surfaced.
**Impact:** Low. Everything works. But a developer looking at `game.core.__init__.py` to understand what core provides would not discover FormulaEvaluator. This is a discoverability gap, not a functionality gap.
**Proposed Resolution:** Add FormulaEvaluator and FormulaContext to `game/core/__init__.py` imports and `__all__`, matching the pattern used for all other core modules. Add a "Formula Evaluation" section to the docstring.
**Effort:** Simple

### GAP-04: refactor_plan.md Not Updated to Reflect Completion
**Location:** `Projects/refactor_loop/refactor_plan.md:53`
**Related Goal:** Project tracking / completeness
**Gap Description:** The master project tracker still shows `- [ ] **PROJ-242: Unified Formula Evaluation System**` with status "Ready" and audit "Not Started". This was flagged by the completeness auditor (F-005) but is also a scope gap -- the project's own plan says Phase 4 includes "Final Verification" which should update external tracking.
**Impact:** Low. Anyone consulting refactor_plan.md will believe PROJ-242 has not been started.
**Proposed Resolution:** Update refactor_plan.md line 53 to `[x]` with status "Complete".
**Effort:** Simple

### GAP-05: FormulaContext frozen Dataclass Has Mutable Default (Dict)
**Location:** `game/core/formula_evaluator.py:200`
**Related Goal:** Goal 2 -- Parameterizable context
**Gap Description:** `FormulaContext` is a `frozen=True` dataclass, but `extra_functions` has type `Dict[str, Any]` with `field(default_factory=dict)`. While `frozen=True` prevents reassigning the field, the dict itself is mutable -- callers can do `context.extra_functions['evil'] = ...` and mutate the shared MODIFIER_CONTEXT constant. This could corrupt the global state.

In practice this is not currently exploitable because:
1. MODIFIER_CONTEXT is only used as a read-only argument to `evaluate()` and `validate()`
2. Those methods read from `extra_functions` but never mutate it
3. No code path mutates `extra_functions` after construction

But the type signature allows it, and the `frozen=True` annotation creates a false sense of safety.
**Impact:** Low. No current bug, but a latent vulnerability. If any future code mutates the dict, it would silently corrupt the global MODIFIER_CONTEXT for all subsequent evaluations.
**Proposed Resolution:** Either (a) use `types.MappingProxyType` to make the dict truly immutable, or (b) document in the docstring that extra_functions must not be mutated after construction. Option (a) is cleaner. Note: this may be considered out of scope for PROJ-242 since it's a design improvement rather than a missing migration.
**Effort:** Simple

### GAP-06: design_validator.py Caller Not in PROJ-242 Plan
**Location:** `game/strategy/services/design_validator.py:83`
**Related Goal:** Goal 1 -- Single eval path
**Gap Description:** `design_validator.py` uses `FormulaEvaluator.safe_evaluate()` via a lazy import at line 83. This caller was NOT listed in PROJ-242's plan (Key Files Reference lists 5 production callers + 1 vestigial import; design_validator.py is absent). The file was likely added after PROJ-242 was planned or completed.

Critically, this caller already uses `FormulaEvaluator` correctly (imports from `game.core.formula_evaluator`), so there is no actual migration gap. It just wasn't catalogued.
**Impact:** None functionally. The caller correctly uses the unified evaluator. The only gap is in the plan documentation.
**Proposed Resolution:** Close as non-issue. The caller was added post-plan and correctly adopted the new API.
**Effort:** N/A

---

## Summary Table

| Finding | Related Goal | Severity | Action Needed |
|---------|-------------|----------|---------------|
| GAP-01 | Eradicate old systems | Moderate | Remove aliases, update 3 test files |
| GAP-02 | Consistent error handling | Low | Update 3 test assertions to use ErrorCode enum |
| GAP-03 | Single eval path (discoverability) | Low | Add to core __init__.py exports |
| GAP-04 | Project tracking | Low | Update refactor_plan.md |
| GAP-05 | Parameterizable context | Low | Consider MappingProxyType or document immutability |
| GAP-06 | Single eval path | Non-issue | Close -- correctly using new API |

**Critical gaps:** 0
**Moderate gaps:** 1 (GAP-01 backward compat aliases)
**Low gaps:** 4
**Non-issues:** 1

---

## Areas Verified as Clean (No Gap Found)

1. **No remaining callers of old functions in production code** -- Grep for `evaluate_math_formula` and `safe_evaluate_math_formula` in `game/` finds only the alias definitions in the two shim files. Zero production call sites use old names.

2. **No eval() calls anywhere in game/** -- Only occurrence is a docstring comment in `formula_evaluator.py` saying "no eval()". The AST walker (PROJ-257) fully replaced eval().

3. **No formula patterns bypassing FormulaEvaluator** -- All 8 sites using `startswith("=")` formula detection go through `FormulaEvaluator.evaluate()` or `.safe_evaluate()`. No `ast.parse` or `ast.literal_eval` calls exist outside the evaluator.

4. **No exec() or compile() calls** -- Clean across entire `game/` tree (compile only appears in `re.compile` for regex patterns in sprites.py).

5. **No new callers since completion** -- Git log since 2026-04-05 shows several commits touching `game/`, but none introduced new FormulaEvaluator call sites. The `design_validator.py` caller (GAP-06) predates the completion date.

6. **FormulaEvaluator properly located in core** -- PROJ-257 extracted it to `game/core/formula_evaluator.py`. The `game/simulation/formula_system.py` file is a thin re-export shim. All production callers import from the canonical `game.core.formula_evaluator` location.

7. **Error code consolidation complete** -- All FormulaException raises in `formula_evaluator.py` use `ErrorCode.XXX.value`. The old string constants (`FORMULA_ERROR_SYNTAX = "F001"` etc.) are deleted from production code. Only `error_codes.py` defines these values.

---

## Conclusion

PROJ-242's scope is well-covered. The single genuine scope gap (GAP-01: backward-compatible aliases) is moderate because it directly contradicts the stated "eradicate old systems" goal and the project's CLAUDE.md migration policy. The remaining findings are minor consistency/discoverability improvements. No new callers or patterns have appeared since completion that would reopen the project's scope.

**Recommended priority:** Address GAP-01 (alias removal) as a cleanup task. The other findings can be addressed opportunistically.
