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
| 1. Regression tests (TDD) | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Refactor TestLabScreen | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Update ScreenRouter construction | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Refactor TestLabUIController + delete orphan services | Not Started | [phase_4_checklist.md](phase_4_checklist.md) |
| 5. Update tests | Not Started | [phase_5_checklist.md](phase_5_checklist.md) |
| 6. Documentation cleanup | Not Started | [phase_6_checklist.md](phase_6_checklist.md) |
| 7. Verification | Not Started | [phase_7_checklist.md](phase_7_checklist.md) |

## Current State
**Last Updated:** 2026-05-04 17:25
**Active Phase:** Planning (awaiting user approval)
**Last Action:** Plan drafted from `r002` discussion artifact + amplifications; PROJ-342 scaffolded
**Next Action:** User approval → begin Phase 1 in a new "Continue Project" session
**Blockers:** Awaiting `Plan Approved` from user
**Context for Next Agent:** Plan is the result of a 4-message Claude/Codex discussion (`AgentCoordination/Scratchpad/Discussion/20260505T000631Z_testlab-drop-game-handle/`). Both agents reached `consensus` on `plans/testlab_drop_game_handle_r002.md`. This project plan is r002 verbatim plus the documentation amplifications captured in `arc01_003`.

## Overview

Eliminate the legacy "Game-handle-as-first-arg" coupling in `TestLabScreen` and `TestLabUIController`. Triggered by user crash `AttributeError: 'ScreenRouter' object has no attribute 'screen'` at `game/ui/screens/test_lab/screen.py:382`. After this refactor, both classes receive only the dependencies they actually use, matching the modern screen-constructor pattern documented at `docs/03_CONVENTIONS.md §2.4`. Includes deleting two orphan duplicate services (`TestExecutionService`, `TestResultsService`) whose only callers are inside the controller methods being deleted.

## Goals

- Crash on Combat Lab "Run All" no longer reproduces.
- `TestLabScreen` matches the convention used by every other screen: `(screen_width, screen_height, *deps, scene_callback)` constructor; no `self.game`.
- `TestLabUIController` no longer takes a `game` parameter or holds vestigial duplicate services.
- `BattleStateViewer` receives explicit dimensions and `handle_resize` events, eliminating one related sizing inconsistency.
- Production code path matches Combat Lab documentation (no stale references to deleted services).

## Scope

**In:**
- `game/ui/screens/test_lab/screen.py` — constructor, helpers, all `self.game.*` accesses
- `combat_lab/services/test_lab_controller.py` — drop `game` param, delete orphan methods
- `combat_lab/services/test_execution_service.py` — delete (orphaned by controller-method deletion)
- `combat_lab/services/test_results_service.py` — delete (orphaned by controller-method deletion)
- `combat_lab/services/__init__.py` — remove deleted exports
- `game/screen_router.py` — update `TestLabScreen` construction; remove legacy comment
- Affected test files: `tests/unit/test_lab/test_visual_run.py`, `tests/unit/combat_lab/services/test_controller_init_events.py`, `tests/unit/combat_lab/services/test_controller_execution.py`, `tests/unit/combat_lab/services/test_test_execution_service.py`, `tests/unit/combat_lab/services/conftest.py`
- New regression tests under `tests/unit/test_lab/`
- Doc updates: `combat_lab/COMBAT_LAB_DOCUMENTATION.md`, `combat_lab/runner.py` docstrings, `game/simulation/battle_controller.py` docstrings

**Out (follow-up debt; record but do not address):**
- `TestLabScreen` is 738 LOC vs the 500-LOC ceiling per `docs/03_CONVENTIONS.md §2.4` — split deferred to dedicated refactor.
- Legacy `BattleScreen.{test_mode, test_scenario, test_tick_count, test_completed}` instance variables flagged at `battle_screen.py:117-125` — separate cleanup.
- Attribute-name inconsistency: `battle_scene` attribute vs `BattleScreen` class.
- Migrating Combat Lab off `pygame_gui` patterns — unrelated.
- **Same-layer inter-screen coupling** (Phase B Architecture Analyst flag): `TestLabScreen` retains direct access to `battle_scene` for `engine`, `_battle_service.create_battle()`, `start_battle(controller)`, and test-state reads (`test_scenario`, `test_completed`, `test_tick_count`). Routing all of these through `scene_callback` would be cleaner per the established `BattleScreen → scene_callback` pattern, but eliminating ALL inter-screen access is a larger architectural project than this crash fix. Recorded for follow-up. See [decisions.md](decisions.md) for the trade-off rationale.
- Pre-existing `_ensure_engine` fragility: it dereferences `battle_scene._battle_service` (private attribute). Hardening to take `battle_service` as a parameter is follow-up debt (Risk Assessor finding 3).

## Key Files

| Component | File Path | Class/Function |
|-----------|-----------|----------------|
| Crash site / target screen | `game/ui/screens/test_lab/screen.py` | `TestLabScreen` (line 44) |
| Construction site | `game/screen_router.py` | `ScreenRouter.__init__` (lines 123-127) |
| Target controller | `combat_lab/services/test_lab_controller.py` | `TestLabUIController` (line 22) |
| Orphan service to delete | `combat_lab/services/test_execution_service.py` | `TestExecutionService` |
| Orphan service to delete | `combat_lab/services/test_results_service.py` | `TestResultsService` |
| Service exports | `combat_lab/services/__init__.py` | module exports |
| Adjacent fix | `game/ui/screens/test_lab/screen.py:137-138, 623-628` | `BattleStateViewer` construction + `handle_resize` |
| Canonical exemplar | `game/ui/screens/battle_screen.py` | `BattleScreen.__init__` (line 68) |
| Test: visual run | `tests/unit/test_lab/test_visual_run.py` | various |
| Test: controller init/exec | `tests/unit/combat_lab/services/test_controller_init_events.py`, `test_controller_execution.py` | various |
| Test: orphan service | `tests/unit/combat_lab/services/test_test_execution_service.py` | (delete entire file) |
| Stale docs | `combat_lab/COMBAT_LAB_DOCUMENTATION.md` | `:73-74, :161-162, :222-226, :259` |
| Stale docstrings | `combat_lab/runner.py` | lines 62-64, 88-90 |
| Stale docstrings | `game/simulation/battle_controller.py` | lines 113-116, 254-260 |

## Related Documents

- [design.md](design.md) — architecture analysis (initial review + Codex review summary)
- [decisions.md](decisions.md) — full decisions log
- [Discussion artifact](../../../AgentCoordination/Scratchpad/Discussion/20260505T000631Z_testlab-drop-game-handle/) — Claude/Codex consensus discussion
- [r002 plan revision](../../../AgentCoordination/Scratchpad/Discussion/20260505T000631Z_testlab-drop-game-handle/plans/testlab_drop_game_handle_r002.md) — canonical planning artifact

## Verification

- [ ] All phase checklists complete
- [ ] Targeted tests pass: `pytest tests/unit/test_lab -x` and `pytest tests/unit/combat_lab/services -x`
- [ ] Full sharded suite passes: `python Tools/test_sharded/test_sharded.py`
- [ ] Manual smoke: Combat Lab → "Run All" → original crash does not recur
- [ ] Audit passed (no significant issues)
- [ ] User verified
