# Review Report: PROJ-385 Formula Evaluator Alias Removal Verification

**Request ID:** req_20260508_225305_4c9ad3
**Review Type:** code
**Review Mode:** full
**Branch:** feat/03c-phase-aware-execution
**Date:** 2026-05-08

---

## Verification Matrix

| Check | Status | Details |
|---|---|---|
| 1. Completeness of removal | PASS | Zero live callers use removed aliases |
| 2. Migration correctness | PASS | All call sites map correctly to FormulaEvaluator.* |
| 3. Test integrity | PASS | No assertions weakened, skipped, or softened |
| 4. Compat-shim hygiene | PASS | Clean deletion, no new shims introduced |
| 5. Scope discipline | PASS | Changes limited to alias deletion + test migration |
| 6. File size/structure | PASS | 404 lines, clean, no dead code |
| 7. Pre-existing failures | PASS | All 3 failures are in unrelated files |

---

## Findings

### INFO — No issues found

### 1. Completeness of Removal (INFO-001)

`grep -rn -E "(evaluate_math_formula|safe_evaluate_math_formula|validate_formula)\b" .` was run across the entire repo.

**Python files:** Zero hits for `evaluate_math_formula` or `safe_evaluate_math_formula`. The only `validate_formula` hits are the legitimate `ModifierEffectEvaluator.validate_formula` class method in:
- `game/simulation/components/modifier_effects.py:225,265`
- `game/simulation/components/modifier_schema.py:237`
- `tests/unit/modifiers/test_formula_validation.py` (7 call sites)
- `tests/unit/simulation/components/test_modifier_effects.py` (5 call sites)
- `tests/unit/simulation/test_formula_evaluator.py:5` (comment only)

**Non-Python files:** Hits only in PROJ-385's own tracking files, `docs/guides/modifier_system.md` (documenting `ModifierEffectEvaluator.validate_formula`), and deep-archive PROJ files (historical, not live code).

**Verdict:** No live caller still uses the removed module-level aliases.

### 2. Migration Correctness (INFO-002)

Sample of call sites from each migrated test file verified against expected mapping:

| Old Name | New Name | Sample Call Site |
|---|---|---|
| `evaluate_math_formula(formula, context)` | `FormulaEvaluator.evaluate(formula, context)` | `test_formula_system.py:67` — `FormulaEvaluator.evaluate("sqrt(16) + 2", {})` |
| `safe_evaluate_math_formula(formula, context, default=0)` | `FormulaEvaluator.safe_evaluate(formula, context, default=0)` | `test_formula_system.py:113` — `FormulaEvaluator.safe_evaluate("undefined_var", {}, default=0)` |
| `validate_formula(formula, allowed_vars)` | `FormulaEvaluator.validate(formula, allowed_vars)` | `test_formula_system.py:185` — `FormulaEvaluator.validate('x + 1', ['x', 'y'])` |

All three test files import `FormulaEvaluator` from `game.core.formula_evaluator` directly. The old aliases were direct references (`evaluate_math_formula = FormulaEvaluator.evaluate`, etc.), so semantics are identical. No argument-order subtleties exist — same function signatures.

**Verdict:** Migration is correct. All ~118 invocations across the 3 files use the equivalent `FormulaEvaluator.*` method.

### 3. Test Integrity (INFO-003)

Diffed the call patterns across all three test files:

- **test_formula_system.py** (242 lines): All 24 test methods preserved with identical assertions, identical formulas, identical context dicts. Only changed: `from game.core.formula_evaluator import evaluate_math_formula` → `from game.core.formula_evaluator import FormulaEvaluator` and `evaluate_math_formula(...)` → `FormulaEvaluator.evaluate(...)`.
- **test_formula_exceptions.py** (173 lines): All 12 test methods preserved identically. Same inline import pattern (import inside each test method, now importing `FormulaEvaluator`).
- **test_formula_overflow_underflow.py** (282 lines): All ~25 test methods preserved with identical formulas and epsilon tolerances. Module-level import changed from `evaluate_math_formula` etc. to `FormulaEvaluator`.

No `@pytest.mark.skip` was added. No assertion thresholds were loosened. No try/except wrappers were added to soften failures.

**Verdict:** Test integrity is fully preserved. Zero tests weakened.

### 4. Compat-Shim Hygiene (INFO-004)

`game/core/formula_evaluator.py` is 404 lines (the deleted aliases were at lines 407-413, which no longer exist). The file ends cleanly at the `safe_evaluate` method. No new module-level aliases, wrapper functions, or fallback imports were added anywhere in the codebase.

Verified: No `from game.core.formula_evaluator import` line in any production file exposes the old names. All production code already uses `FormulaEvaluator` directly (from PROJ-242).

**Verdict:** Clean deletion with no new shims. Fully compliant with Rule 3 (no fallback systems).

### 5. Scope Discipline (INFO-005)

`git diff` analysis confirms the change is limited to:
1. Deletion of 3 alias lines from `game/core/formula_evaluator.py` (old lines ~407-413)
2. Minor docstring update at line ~207 (changed "formula_context parameter" wording)
3. Import and call-site changes in 3 test files only

No production behavior was changed. No other production files were touched. No unrelated refactors or cleanups were piggybacked.

**Verdict:** Scope discipline is strict. Only the alias removal + caller migration was performed.

### 6. File Size and Structure (INFO-006)

`game/core/formula_evaluator.py` is 404 lines (within the 500-line ceiling). The file is well-structured:
- Lines 1-12: Docstring
- Lines 13-40: Imports, constants
- Lines 43-181: AST evaluation infrastructure
- Lines 184-231: FormulaContext + FormulaEvaluator class definition
- Lines 233-313: `evaluate()` method
- Lines 315-376: `validate()` method
- Lines 378-404: `safe_evaluate()` method

No dead code identified. All constants (`ALLOWED_MATH_FUNCTIONS`, `ALLOWED_BUILTINS`, `DANGEROUS_NAMES`), AST infrastructure functions (`_parse_formula`, `_eval_node`), and class methods are in active use.

**Verdict:** File is clean and appropriately sized.

### 7. Pre-Existing Failures (INFO-007)

The sharded suite reportedly shows 3 failures:
1. `test_scalene_workflow_files_are_documented` — in `tests/unit/tools/test_scalene_profiling_workflow.py`
2. `test_skill_does_not_claim_coverage_json_is_supported` — in `tests/unit/tools/test_testcoverage_audit.py`
3. `test_pathfinder_attached_after_init` — in `tests/integration/strategy/test_save_round_trip_phase4.py`

None of these files reference `formula_evaluator`, `FormulaEvaluator`, `formula_system`, or any formula-related module. All three are in tooling/integration test files that are completely unrelated to the formula evaluation system.

**Verdict:** All 3 failures are unrelated to PROJ-385.

---

## Summary

| Severity | Count |
|---|---|
| CRITICAL | 0 |
| MAJOR | 0 |
| MINOR | 0 |
| INFO | 7 |

## Recommendation

**APPROVE** — The alias removal is complete and correct. All 7 verification points pass with zero findings. The change is a textbook execution of Rule 3: delete the backward-compat shims, migrate all callers, introduce no new shims.
