# PROJ-385: Design Document

## Source Audit

This project was created from the legacy-audit at `Reviews/results/2026-05-07_220621_legacy-audit/`.

- **Audit verified:** 32 items overall (across 11 sibling projects)
- **This bundle:** 1 verified, 0 uncertain, 0 INFO, 0 deferred
- **Project siblings:** PROJ-383, PROJ-384, PROJ-386..PROJ-393

## Cluster Identity

**Removal cluster:** `formula_evaluator` backward-compat aliases. Three module-level aliases (`evaluate_math_formula`, `safe_evaluate_math_formula`, `validate_formula`) explicitly documented as "Backward-compatible aliases for existing test imports." Zero production usage; only tests still go through them.

## Severity Breakdown

| Severity | Count |
|----------|-------|
| MAJOR | 1 (LEG-04-001) |

## Risk Notes

- Audit reported "118 test call sites" — Sonnet's third-pass verification reconciled this as ~118 invocations across ~23 distinct import statements in 3 test files. Caller count is large enough that mass find-and-replace is the right tool.
- The aliases are bare-assignment to existing classmethods — no signature differences, so the find-and-replace is mechanical.

## Design Decisions

See [decisions.md](decisions.md) for the full log with rationale.
