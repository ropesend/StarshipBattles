# PROJ-389: Legacy removal — score_planet_for_race wrapper migration (2026-05-07)

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-389` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-389 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Migrate 6 callers + delete wrapper | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |

## Current State
**Last Updated:** 2026-05-08
**Active Phase:** Phase 1
**Last Action:** Project created from `2026-05-07_220621_legacy-audit` after independent verification
**Next Action:** Begin Phase 1 tasks
**Blockers:** None

## Overview
Migrates 6 production callers of `score_planet_for_race` to the canonical `calculate_habitability`, then deletes the wrapper at `game/strategy/formulas/habitability.py:99` and the dual re-export at `game/strategy/formulas/__init__.py:9`. The wrapper is a 1-line delegate kept for "source-stability of existing callers."

## Goals
- Migrate 6 production call sites in `population_engine.py`, `happiness_engine.py`, `economy_slice.py`, `colony_output.py` (3 sites), `strategy_detail_fmt.py`.
- Drop `score_planet_for_race` from the `formulas/__init__.py` public re-exports.
- Delete the wrapper from `habitability.py`.

## Scope
**In:** LEG-02-009.
**Out:** Other clusters from the same audit (siblings PROJ-383..PROJ-388, PROJ-390..PROJ-393); REJECTED and OUT_OF_SCOPE items recorded in [findings/verification_report.md](findings/verification_report.md) and the shared [findings/bundling_decisions.md](findings/bundling_decisions.md).

## Key Files
| Component | File Path |
|-----------|-----------|
| Wrapper to delete | `game/strategy/formulas/habitability.py` |
| Public re-export to update | `game/strategy/formulas/__init__.py` |
| Caller | `game/strategy/engine/population_engine.py` |
| Caller | `game/strategy/engine/happiness_engine.py` |
| Caller | `game/strategy/facade/slices/economy_slice.py` |
| Caller | `game/strategy/formulas/colony_output.py` |
| Caller | `game/ui/screens/strategy_detail_fmt.py` |

## Related Documents
- [design.md](design.md) — source audit, cluster identity, severity breakdown
- [decisions.md](decisions.md) — full decisions log
- [findings/verification_report.md](findings/verification_report.md) — third-pass verification of audit claims
- [findings/source_audit.md](findings/source_audit.md) — pointer to the originating audit
- [findings/bundling_decisions.md](findings/bundling_decisions.md) — interactive bundling record (shared across siblings)

## Verification
- [ ] All phase checklists complete
- [ ] All tests passing
- [ ] No remaining references to `score_planet_for_race` (`grep -rn "score_planet_for_race" .`)
- [ ] User verified
