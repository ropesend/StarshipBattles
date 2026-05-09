# PROJ-393: Legacy removal — Test-injection fallbacks + comment cleanups (2026-05-07)

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-393` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-393 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Minor — comment-only cleanups + doc-tag fixes | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Major — test-injection legacy fallbacks | Complete | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Major — backward-compat fields + misc legacy paths | Complete (3 tasks deferred) | [phase_3_checklist.md](phase_3_checklist.md) |

## Current State
**Last Updated:** 2026-05-08
**Active Phase:** Closed — all 3 phases complete (with 3 Phase 3 tasks deferred)
**Last Action:** Phase 3 commit (8fa9887d3): tasks 3.1, 3.4, 3.6, 3.7 complete; 3.2 partial (tag removal only); 3.3, 3.5 deferred with rationale
**Next Action:** Project closeout — 3 phases shipped, deferrals logged for follow-up
**Blockers:** None

## Overview
Catch-all project for ~16 small legacy items across the codebase: comment-only deletions, test-injection fallback branches that exist only because tests don't always inject deps, and backward-compat fields/paths held for save-format compatibility (but not save-migration code per se — those live in PROJ-386). Phases ordered by removal-risk: Phase 1 ships in minutes (comment edits), Phase 2 requires test audit, Phase 3 is the broadest with mixed shapes.

## Goals

### Phase 1
- Delete 4 documentation comments that reference removed/legacy code (no logic change).

### Phase 2
- Migrate `RESEARCH_TREE`/`GALAXY_TEST` scenes to `IScene.handle_event()` and delete the legacy `handle_input()` branch in `run_loop.py`.
- Delete 4 "Legacy fallback for tests without injection" branches once test coverage is audited.

### Phase 3
- Delete `'PlanetaryShield'` hardcoded fallback in `planet_action_engine`.
- Migrate callers off the `fleet_id` backward-compat field on 3 command classes.
- Migrate callers off `view=None` in `format_planet_info` (UNCERTAIN-included).
- Replace module-level `ResourceCatalog.from_json()` with lazy init.
- Reclaim Combat Lab instance vars on `BattleScreen` (UNCERTAIN-included, PROJ-270 archived).
- Confirm-then-delete `_LEGACY_PATTERN` sprite regex via asset scan (UNCERTAIN-included).
- Delete first-species `Legacy/Default` fallback in `transfer_branches`.

## Scope
**In:** LEG-02-002, LEG-02-003, LEG-02-004, LEG-02-005 (INFO), LEG-02-006 (UNCERTAIN), LEG-02-013, LEG-02-017 (INFO), LEG-03-002, LEG-03-003, LEG-03-004, LEG-03-005, LEG-03-006, LEG-03-007, LEG-03-023 (UNCERTAIN), LEG-03-024 (UNCERTAIN), LEG-04-004.
**Out:** Other clusters (siblings PROJ-383..PROJ-392); REJECTED and OUT_OF_SCOPE items recorded in [findings/verification_report.md](findings/verification_report.md) and the shared [findings/bundling_decisions.md](findings/bundling_decisions.md). UNCERTAIN-excluded: LEG-02-001 (`Game.running` test backdoor still needed).

## Key Files
| Component | File Path |
|-----------|-----------|
| Phase 1 — comments | `game/simulation/combat/formation.py`, `game/strategy/combat/spec_compiler.py`, `game/strategy/systems/save_game_service.py`, `game/context.py` |
| Phase 2 — scene migration | `game/run_loop.py` |
| Phase 2 — validator fallbacks | `game/strategy/validation/planet_order_validator.py` |
| Phase 2 — test fallbacks | `game/ui/panels/build_queue_drag_handler.py`, `game/ui/screens/empire_build_queue_window.py` |
| Phase 3 — facility fallback | `game/strategy/engine/planet_action_engine.py` |
| Phase 3 — fleet_id field | `game/strategy/engine/commands/__init__.py` |
| Phase 3 — view=None | `game/ui/screens/strategy_detail_fmt.py` |
| Phase 3 — ResourceCatalog | `game/ui/screens/build_queue_helpers.py`, `game/ui/screens/strategy_ui.py` |
| Phase 3 — Combat Lab vars | `game/ui/screens/battle_screen.py` |
| Phase 3 — sprite pattern | `game/ui/renderer/sprites.py` |
| Phase 3 — first-species | `game/strategy/engine/order_handlers/transfer_branches.py` |

## Related Documents
- [design.md](design.md) — source audit, cluster identity, severity breakdown
- [decisions.md](decisions.md) — full decisions log
- [findings/verification_report.md](findings/verification_report.md) — third-pass verification of audit claims
- [findings/source_audit.md](findings/source_audit.md) — pointer to the originating audit
- [findings/bundling_decisions.md](findings/bundling_decisions.md) — interactive bundling record (shared across siblings)

## Verification
- [x] All phase checklists complete (3 Phase 3 tasks deferred with rationale in findings/verification_report.md)
- [x] Phase-scoped focused tests passing (full sharded suite deferred to orchestrator)
- [ ] User verified
