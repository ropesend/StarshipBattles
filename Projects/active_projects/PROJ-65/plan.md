# PROJ-65: Game Class Scene Protocol Refactor

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-65` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-65 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Foundation — IScene Protocol & WIDTH/HEIGHT | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Standardize Scene Interfaces | Complete | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Extract MenuScene & Scene Dispatch | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Cleanup & Tests | Not Started | [phase_4_checklist.md](phase_4_checklist.md) |

## Current State
**Last Updated:** 2026-02-07
**Active Phase:** Phase 3
**Last Action:** Phase 2 complete - All 8 scene classes now implement IScene protocol (handle_event, update(dt), draw, handle_resize). Added scene_callback pattern to BattleSetupScreen, BattleScreen, StrategyScreen, TestLabScreen. Internalized battle_coordinator logic into BattleScreen.
**Next Action:** Begin Phase 3 — Extract MenuScene & create unified scene dispatch
**Blockers:** None
**Context for Next Agent:** 6244 passed (2 pre-existing failures in bug_15 tests). BattleScreen now handles its own timing/accumulator. Some legacy action flags kept for backward compatibility but callbacks are primary path.

## Overview
Refactor `game/app.py` (759 lines, 43 methods) from a monolithic orchestrator with 5 if/elif chains (10 GameStates, ~45 branches) into a thin coordinator that dispatches to `self.active_scene` via a unified `IScene` protocol. This eliminates Open/Closed Principle violations, removes global WIDTH/HEIGHT state, extracts the menu into its own scene class, and decouples battle coordinator logic.

## Goals
- Define `IScene` protocol with `handle_event()`, `update()`, `draw()`, `handle_resize()`
- Replace all 5 if/elif chains with single `self.active_scene.method()` dispatch
- Standardize all 8 scene classes to implement `IScene` directly
- Extract menu into `MenuScene` implementing `IScene`
- Move battle coordinator logic into `BattleScreen`
- Break `TestLabScreen`'s dependency on Game instance
- Replace global `WIDTH`/`HEIGHT` with instance attributes
- Reduce `app.py` from 759 to <300 lines

## Scope
**In:**
- `game/app.py` — primary target
- `game/core/protocols.py` — add IScene
- All 8 scene classes — standardize interfaces
- `game/battle_coordinator.py` — internalize into BattleScreen
- `game/ui/screens/battle_input_handler.py` — fold into BattleScreen
- New `game/ui/screens/menu_scene.py`
- Tests for Game class

**Out:**
- TestLabScreen internal decomposition (PROJ-57)
- GalaxyTestScreen decomposition (PROJ-60)
- Moving FormationEditorScreen from `Tools/` to `game/`
- New GameState additions
- Scene-specific bugs or feature improvements

## Key Files
| Component | File Path |
|-----------|-----------|
| Game class | `game/app.py` |
| IScene protocol | `game/core/protocols.py` |
| MenuScene (new) | `game/ui/screens/menu_scene.py` |
| BattleScreen | `game/ui/screens/battle_screen.py` |
| BattleSetupScreen | `game/ui/screens/setup_screen.py` |
| StrategyScreen | `game/ui/screens/strategy_screen.py` |
| TestLabScreen | `game/ui/screens/test_lab_screen.py` |
| Workshop | `game/ui/screens/workshop_screen.py` |
| FormationEditor | `Tools/formation_editor.py` |
| ResearchTree | `game/research/ui/research_scene.py` |
| GalaxyTest | `game/ui/screens/galaxy_test_screen.py` |
| BattleCoordinator | `game/battle_coordinator.py` |
| BattleInputHandler | `game/ui/screens/battle_input_handler.py` |
| GameState enum | `game/core/constants.py` |
| App tests | `tests/unit/test_app_integration.py` |
| Main integration | `tests/unit/systems/test_main_integration.py` |

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log

## Verification
- [ ] All phase checklists complete
- [ ] All tests passing (6225+ baseline)
- [ ] app.py < 300 lines
- [ ] Zero if/elif chains on GameState in app.py
- [ ] Zero `global WIDTH` or `global HEIGHT` in codebase
- [ ] Audit passed
- [ ] User verified
