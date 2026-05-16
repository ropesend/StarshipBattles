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
| 1. Migrate 6 callers + delete wrapper | Complete | [phase_1_checklist.md](phase_1_checklist.md) |

## Current State
**Last Updated:** 2026-05-09 (PROJ-406 reconciliation)
**Active Phase:** Closeout
**Last Action:** Phase 1 complete — all 6 production callers migrated, wrapper deleted, dual re-export dropped. Migration extended beyond the original 6-caller estimate to also cover 4 test files (`test_happiness_engine.py`, `test_colony_output.py`, `test_harvesting_engine_habitability.py`, `test_strategy_detail_fmt.py`) and 3 live docs (`colony_demographic_view.py` docstring, `docs/04_SERVICES.md`, `docs/systems/strategy_layer.md`) so the wrapper deletion would not break their imports/monkeypatch targets — recorded in phase_1_checklist.md "Out-of-band cleanup" and reconciled in the manifest.
**Next Action:** Awaiting user verification.
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
- [x] All phase checklists complete
- [x] All tests passing (focused 226-test suite passed; full sharded baseline cleared post-Wave-1)
- [x] No remaining references to `score_planet_for_race` in production / tests / live docs (only history-preserving artifacts under `Reviews/`, `Projects/`, `_marked_for_deletion_*/` retain references)
- [x] Audit passed (`validate_audit_ready.py PROJ-389` PASSED after PROJ-406 reconciliation)
- [ ] User verified
