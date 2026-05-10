# PROJ-385 — Verification Report

**Source audit:** `Reviews/results/2026-05-07_220621_legacy-audit/`
**Run date:** 2026-05-08
**Cluster:** `formula_evaluator` backward-compat aliases
**Batch summary:** 1 verified / 0 rejected / 0 uncertain / 0 INFO / 0 out-of-scope (within this bundle)

## Verified

| ID | File | Symbols | Replaces | Call sites | Recommendation | Severity |
|---|---|---|---|---|---|---|
| LEG-04-001 | `game/core/formula_evaluator.py:407-413` | `evaluate_math_formula`, `safe_evaluate_math_formula`, `validate_formula` | `FormulaEvaluator.evaluate`, `FormulaEvaluator.safe_evaluate`, `FormulaEvaluator.validate` | 0 prod, ~118 test invocations across ~23 imports in 3 files | migrate_callers_then_delete | MAJOR |

## Rejected

None — Sonnet confirmed against current source. (Audit reported 118 callers; Sonnet reconciled as 118 invocations / 23 import statements — terminology, not a real disagreement.)

## Uncertain (resolved)

None for this bundle.

## INFO (resolved)

None for this bundle.

## Out of Scope

LEG-04-012 was DISPUTED by the audit's own verifier as a duplicate of LEG-04-001 (same file/lines, redundant CRITICAL flag for what was already MAJOR). Recorded in shared [bundling_decisions.md](bundling_decisions.md).
