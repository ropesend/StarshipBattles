# PROJ-485: Legacy removal — dead CarrierAIController methods (2026-05-20)

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-485` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-485 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Delete dead methods + migrate tests | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Audit remediation (Codex consult 2026-05-23) | Complete | [phase_2_checklist.md](phase_2_checklist.md) |

## Current State
**Last Updated:** 2026-05-23
**Active Phase:** Complete
**Last Action:** Deleted `_find_tactical_launch_ability`, `_pop_fighter_cvs`, `_pop_cvs` from `game/ai/carrier_controller.py` (~83 LOC). No test callers existed; no test migrations required. `pytest tests/unit/ai/` 419 passed.
**Next Action:** User verification, then commit.
**Blockers:** None

## Overview
Three legacy methods on `CarrierAIController` (`_find_tactical_launch_ability`, `_pop_fighter_cvs`, `_pop_cvs`) carry zero production callers per the audit's verifier. Two of them are explicitly documented as "retained for the pre-QA-C integration tests"; `_pop_cvs` is only reached from `_pop_fighter_cvs` (which itself has zero production callers, transitively dead). Production launch decisions go through `_sum_launch_rate` and `_pop_cvs_within_budget`. ~83 LOC of dead code removable as one coherent PR.

## Goals
- Delete `_find_tactical_launch_ability`, `_pop_fighter_cvs`, and `_pop_cvs` from `CarrierAIController` (~83 LOC total).
- Migrate any test callers to the modern surface (`_sum_launch_rate` for ability lookup, `_pop_cvs_within_budget` for mass-budget CV popping).

## Scope
**In:** dead static methods in `game/ai/carrier_controller.py:255-300, 358-390`.
**Out:**
- The modern surface (`_sum_launch_rate`, `_pop_cvs_within_budget`) — those are the canonical replacements and are kept.
- Test rewrites beyond import / call-target updates — if a test introspects the dead helper for behavior that the modern surface does not expose, defer rather than rewrite the test logic (record under Notes for follow-up).
- REJECTED and OUT_OF_SCOPE findings: see [findings/verification_report.md](findings/verification_report.md).
- Other legacy-audit clusters: see siblings PROJ-484, PROJ-486, PROJ-487, PROJ-488, PROJ-489, PROJ-490.

## Key Files
| Component | File Path |
|-----------|-----------|
| `_find_tactical_launch_ability` + `_pop_fighter_cvs` + `_pop_cvs` [EDIT] | `game/ai/carrier_controller.py` |
| Test callers (TBD by grep during implementation) | `tests/unit/ai/...` (any test referencing the dead method names) |

## Related Documents
- [design.md](design.md) — source audit, cluster identity
- [decisions.md](decisions.md) — bundling decision log
- [findings/verification_report.md](findings/verification_report.md) — full verifier output
- [findings/source_audit.md](findings/source_audit.md) — link to source audit
- [findings/bundling_decisions.md](findings/bundling_decisions.md) — Phase D bundling record

## Verification
- [ ] All phase checklists complete
- [ ] All tests passing
- [ ] Audit passed
- [ ] User verified
