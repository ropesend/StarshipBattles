# PROJ-342: Drop self.game handle from TestLab UI

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-342` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-342 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Regression tests (TDD) | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Refactor TestLabScreen | Complete | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Update ScreenRouter construction | Complete | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Refactor TestLabUIController + delete orphan services | Complete | [phase_4_checklist.md](phase_4_checklist.md) |
| 5. Update tests | Complete | [phase_5_checklist.md](phase_5_checklist.md) |
| 6. Documentation cleanup | Complete | [phase_6_checklist.md](phase_6_checklist.md) |
| 7. Verification | Complete (manual smoke pending user) | [phase_7_checklist.md](phase_7_checklist.md) |

## Current State
**Last Updated:** 2026-05-04 17:55
**Active Phase:** awaiting-confirmation (manual smoke pending user)
**Last Action:** All seven phases executed in one session. Targeted suites green (4234 passed), full sharded suite green (17,216 / 17,212 passed / 0 failed / 4 skipped / 52.0s; baseline was 17,202/17,198/4/53.1s — net +14 tests).
**Next Action:** User runs `python launcher.py` → Combat Lab → "Run All" to confirm the original `AttributeError: 'ScreenRouter' object has no attribute 'screen'` no longer reproduces.
**Blockers:** None
**Context for Next Agent:** Implementation completed in the same session that planned it (user said "proceed with the plan"). All production code, tests, and docs landed. The Architecture Analyst's flag (route `start_battle` through `scene_callback`) was knowingly deferred per `decisions.md` and recorded as follow-up debt in the Out-of-Scope section.

## Overview

Eliminate the legacy "Game-handle-as-first-arg" coupling in `TestLabScreen` and `TestLabUIController`. Triggered by user crash `AttributeError: 'ScreenRouter' object has no attribute 'screen'` at `game/ui/screens/test_lab/screen.py:382`. After this refactor, both classes receive only the dependencies they actually use, matching the modern screen-constructor pattern documented at `docs/03_CONVENTIONS.md §2.4`. Includes deleting two orphan duplicate services (`TestExecutionService`, `TestResultsService`) whose only callers were inside the controller methods being deleted.

## Goals

- Crash on Combat Lab "Run All" no longer reproduces. ✓
- `TestLabScreen` matches the convention used by every other screen: `(screen_width, screen_height, *deps, scene_callback)` constructor; no `self.game`. ✓
- `TestLabUIController` no longer takes a `game` parameter or holds vestigial duplicate services. ✓
- `BattleStateViewer` receives explicit dimensions and `handle_resize` events, eliminating one related sizing inconsistency. ✓
- Production code path matches Combat Lab documentation (no stale references to deleted services). ✓

## Scope

**In:** Done.
- `game/ui/screens/test_lab/screen.py` — constructor, helpers, all `self.game.*` accesses
- `combat_lab/services/test_lab_controller.py` — drop `game` param, delete orphan methods
- `combat_lab/services/test_execution_service.py` — DELETED
- `combat_lab/services/test_results_service.py` — DELETED
- `combat_lab/services/__init__.py` — exports updated
- `game/screen_router.py` — updated `TestLabScreen` construction; removed legacy comment
- Tests updated/deleted per `phase_5_checklist.md`
- Doc updates: `combat_lab/COMBAT_LAB_DOCUMENTATION.md`, `combat_lab/runner.py`, `game/simulation/battle_controller.py`, `combat_lab/services/scenario_run_helper.py`, `docs/04_SERVICES.md`, `docs/systems/combat_simulation.md`

**Out (follow-up debt; recorded but not addressed):**
- `TestLabScreen` is 738 LOC vs the 500-LOC ceiling per `docs/03_CONVENTIONS.md §2.4` — split deferred to dedicated refactor.
- Legacy `BattleScreen.{test_mode, test_scenario, test_tick_count, test_completed}` instance variables flagged at `battle_screen.py:117-125` — separate cleanup.
- Attribute-name inconsistency: `battle_scene` attribute vs `BattleScreen` class.
- Migrating Combat Lab off `pygame_gui` patterns — unrelated.
- **Same-layer inter-screen coupling** (Phase B Architecture Analyst flag): `TestLabScreen` retains direct access to `battle_scene` for `engine`, `_battle_service.create_battle()`, `start_battle(controller)`, and test-state reads (`test_scenario`, `test_completed`, `test_tick_count`). Routing all of these through `scene_callback` would be cleaner per the established `BattleScreen → scene_callback` pattern, but eliminating ALL inter-screen access is a larger architectural project than this crash fix. Recorded for follow-up. See [decisions.md](decisions.md) for the trade-off rationale.
- Pre-existing `_ensure_engine` fragility: it dereferences `battle_scene._battle_service` (private attribute). Hardening to take `battle_service` as a parameter is follow-up debt (Risk Assessor finding 3).

## Key Files

| Component | File Path | Class/Function |
|-----------|-----------|----------------|
| Crash site / target screen | `game/ui/screens/test_lab/screen.py` | `TestLabScreen` |
| Construction site | `game/screen_router.py` | `ScreenRouter.__init__` |
| Target controller | `combat_lab/services/test_lab_controller.py` | `TestLabUIController` |
| Orphan service deleted | `combat_lab/services/test_execution_service.py` | (deleted) |
| Orphan service deleted | `combat_lab/services/test_results_service.py` | (deleted) |
| Service exports | `combat_lab/services/__init__.py` | module exports |
| Adjacent fix | `game/ui/screens/test_lab/screen.py` | `BattleStateViewer` construction + `handle_resize` |
| Canonical exemplar | `game/ui/screens/battle_screen.py` | `BattleScreen.__init__` |

## Related Documents

- [design.md](design.md) — architecture analysis
- [decisions.md](decisions.md) — full decisions log
- [Discussion artifact](../../../AgentCoordination/Scratchpad/Discussion/20260505T000631Z_testlab-drop-game-handle/) — Claude/Codex consensus discussion
- [r002 plan revision](../../../AgentCoordination/Scratchpad/Discussion/20260505T000631Z_testlab-drop-game-handle/plans/testlab_drop_game_handle_r002.md) — canonical planning artifact
- [findings/](findings/) — Phase B swarm review reports

## Verification

- [x] All phase checklists complete
- [x] Targeted tests pass: `pytest tests/unit/test_lab tests/unit/combat_lab/services tests/unit/ui -x` — 4234 passed
- [x] Full sharded suite passes: 17,216 / 17,212 passed / 0 failed / 4 skipped / 52.0s (baseline 17,202/17,198/4/53.1s — +14 tests, no regressions)
- [ ] Manual smoke (user): Combat Lab → "Run All" → original crash does not recur
- [ ] Audit passed (no significant issues)
- [ ] User verified
