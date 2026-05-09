# PROJ-409: Tier 5 — Close PROJ-395 deferred items (MAJ-013, MAJ-014)

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Investigate + close MAJ-013 and MAJ-014 | Complete | [phase_1_checklist.md](phase_1_checklist.md) |

## Current State
**Last Updated:** 2026-05-09
**Active Phase:** Phase 1
**Last Action:** Phase 1 complete. MAJ-014 actively deleted in commit `c0ff79f92` (defensive raw `EnginePhaseError` catch removed; integration + unit test contracts updated). MAJ-013 ratified — investigation found PROJ-390 already retired the module-level EventBus shim; the PROJ-395 reviewer simply did not pick up the prior closure. See `decisions.md`.
**Next Action:** User verification + final closeout commit.
**Blockers:** None

## Overview
PROJ-395's review documented two MAJOR findings that the original project deferred without closing: MAJ-013 (EventBus Pattern #10 shim — pre-existing, not a PROJ-381 regression) and MAJ-014 (UI defensive raw `EnginePhaseError` catch — architectural decision pending). Wave 5 ratifies or actively closes both. Now that PROJ-408 C-02 has direct unit coverage on the facade conversion (`EnginePhaseError` → `TurnFailedError`), MAJ-014 has a clear path to resolution.

## Goals
- **MAJ-013**: read PROJ-395's writeup; locate the shim. If it can be deleted without affecting downstream callers, delete it. If it can't, ratify as a documented won't-fix or roll into a future cleanup project.
- **MAJ-014**: now that the facade conversion is well-tested (PROJ-408 C-02), the defensive raw `EnginePhaseError` catch in `game/ui/screens/strategy_game_state_manager.py:19, 149-158` is provably dead code. Per CLAUDE.md Rule 4 (no fallbacks for scenarios that can't happen), remove the import + catch. Add a unit test confirming the UI receives only `TurnFailedError` (not `EnginePhaseError`).

## Scope
**In:**
- Read `Reviews/results/2026-05-09_proj-380-399-implementation-review/PROJ-395_report.md` and `Projects/active_projects/PROJ-395/findings/` for the original MAJ-013/MAJ-014 context.
- For MAJ-013: investigate, decide, document.
- For MAJ-014: remove the defensive import + catch in `strategy_game_state_manager.py`; add a unit test covering the now-canonical path.
- Both decisions logged in `decisions.md` with full rationale.

**Out:**
- Any other deferred MINOR/INFO items from the future-cleanup buckets in REMEDIATION_PLAN Tier 5. The brief explicitly scopes those out.

## Key Files
| Component | File Path |
|-----------|-----------|
| MAJ-014 production | `game/ui/screens/strategy_game_state_manager.py:19, 149-158` |
| MAJ-014 facade reference (read-only) | `game/strategy/facade/strategy_session_facade.py:194-201` |
| MAJ-014 test | `tests/unit/ui/screens/test_strategy_game_state_manager.py` (or wherever) |
| MAJ-013 source | TBD — discover during investigation |
| Decisions | `Projects/active_projects/PROJ-409/decisions.md` |

## Source Evidence
- `Reviews/results/2026-05-09_proj-380-399-implementation-review/REMEDIATION_PLAN.md` Tier 5 section.
- `Reviews/results/2026-05-09_proj-380-399-implementation-review/PROJ-395_report.md`.
- PROJ-395 verification report (if it exists).

## Verification
- [x] Phase 1 checklist complete
- [x] MAJ-013 closure documented (ratified — already actively closed by PROJ-390)
- [x] MAJ-014 catch removed; new regression test passes
- [x] `pytest tests/unit/ui/screens/test_strategy_game_state_manager.py -v` passes (24/24)
- [x] `python Projects/scripts/validate_audit_ready.py PROJ-409` passes
- [ ] User verified
