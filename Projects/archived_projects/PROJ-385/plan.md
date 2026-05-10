# PROJ-385: Legacy removal — formula_evaluator backward-compat aliases (2026-05-07)

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-385` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-385 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Migrate test imports + delete aliases | Complete | [phase_1_checklist.md](phase_1_checklist.md) |

## Current State
**Last Updated:** 2026-05-08
**Active Phase:** Phase 1
**Last Action:** Phase 1 complete — migrated 3 test files to canonical `FormulaEvaluator.*` API and deleted the 3 backward-compat aliases from `game/core/formula_evaluator.py`. Full sharded suite: 19084 passed, 3 pre-existing unrelated failures.
**Next Action:** Project verification (run `validate_phase.py PROJ-385 1`, then user-verify and close out)
**Blockers:** None

## Overview
Removes three module-level aliases at `game/core/formula_evaluator.py:407-413` (`evaluate_math_formula`, `safe_evaluate_math_formula`, `validate_formula`) that explicitly state in comments: "Backward-compatible aliases for existing test imports." Zero production callers; ~118 test invocations across 3 test files (~23 import sites). Violates CLAUDE.md Rule 3.

## Goals
- Migrate ~23 test import sites across `test_formula_system.py`, `test_formula_overflow_underflow.py`, `test_formula_exceptions.py` to call `FormulaEvaluator.*` directly.
- Delete the 3 aliases (lines 407-413) plus the comment header.

## Scope
**In:** LEG-04-001 (the 3 aliases + their callers).
**Out:** Other clusters from the same audit (siblings PROJ-383, PROJ-384, PROJ-386..PROJ-393); REJECTED and OUT_OF_SCOPE items recorded in [findings/verification_report.md](findings/verification_report.md) and the shared [findings/bundling_decisions.md](findings/bundling_decisions.md).

## Key Files
| Component | File Path |
|-----------|-----------|
| Production target | `game/core/formula_evaluator.py` |
| Test migration | `tests/.../test_formula_system.py` |
| Test migration | `tests/.../test_formula_overflow_underflow.py` |
| Test migration | `tests/.../test_formula_exceptions.py` |

## Related Documents
- [design.md](design.md) — source audit, cluster identity, severity breakdown
- [decisions.md](decisions.md) — full decisions log
- [findings/verification_report.md](findings/verification_report.md) — third-pass verification of audit claims
- [findings/source_audit.md](findings/source_audit.md) — pointer to the originating audit
- [findings/bundling_decisions.md](findings/bundling_decisions.md) — interactive bundling record (shared across siblings)

## Verification
- [ ] All phase checklists complete
- [ ] All tests passing
- [ ] No remaining references to `evaluate_math_formula`, `safe_evaluate_math_formula`, `validate_formula` (`grep -rn -E "(evaluate_math_formula|safe_evaluate_math_formula|validate_formula)\b" .`)
- [ ] User verified
