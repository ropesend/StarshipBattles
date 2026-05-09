# Review Scope: PROJ-385 Formula Evaluator Alias Removal Verification

**Type:** code (delegated by Claude Code)
**Request ID:** req_20260508_225305_4c9ad3
**Branch:** feat/03c-phase-aware-execution
**Review Mode:** full

## Scope

Changes on branch `feat/03c-phase-aware-execution` for PROJ-385:

- `game/core/formula_evaluator.py` (deleted backward-compat aliases at lines 407-413; minor docstring update around line 207)
- `tests/unit/simulation/test_formula_exceptions.py`
- `tests/unit/systems/test_formula_overflow_underflow.py`
- `tests/unit/systems/test_formula_system.py`

Project docs: `Projects/active_projects/PROJ-385/plan.md`, `phase_1_checklist.md`, `manifest.md`.

## Instructions

PROJ-385 removed three module-level backward-compat aliases (`evaluate_math_formula`, `safe_evaluate_math_formula`, `validate_formula`) from `game/core/formula_evaluator.py` and migrated ~23 test import sites / ~118 invocations across 3 test files to call `FormulaEvaluator.*` directly.

Verify:
1. **Completeness of removal** — Confirm no live caller still uses the removed names.
2. **Migration correctness** — Confirm semantics are preserved in each migrated test file.
3. **Test integrity** — Confirm no tests were weakened, skipped, or had assertions softened.
4. **Compat-shim hygiene** — Confirm no new compat wrappers, helpers, or fallbacks were introduced.
5. **Scope discipline** — Confirm no unrelated production behavior changes or refactors.
6. **File size and structure** — Confirm formula_evaluator.py is clean; flag any dead code.
7. **Pre-existing failures** — Confirm 3 known failures are unrelated to PROJ-385.

## Context

PROJ-385 is one of three sibling legacy-removal projects (385, 387, 388) being executed in series. All three target backward-compat shims flagged by audit `Reviews/results/2026-05-07_220621_legacy-audit/`. Repo rule (CLAUDE.md Rule 3): no compat shims, no fallback systems.
