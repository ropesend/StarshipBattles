# PROJ-17: Enforce Layer Boundaries

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-17` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-17 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Quick Wins | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Move LayerType to Core | Complete | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Move ShipThemeManager | Complete | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Create BattleOrchestrator | Complete | [phase_4_checklist.md](phase_4_checklist.md) |

## Current State
**Last Updated:** 2026-01-26 Session 2
**Active Phase:** Project Complete - Final Verification Pending
**Last Action:** Completed Phase 4 - BattleOrchestrator created and integrated
**Next Action:** Manual verification (launch game, test battle and builder)
**Blockers:** None

**Phase 4 Summary:**
- Created game/ui/orchestration/ directory with BattleOrchestrator class
- Modified BattleEngine.start() to accept optional ai_controllers parameter
- Modified add_ship_mid_battle() to accept optional ai_controller parameter
- Moved AIController imports to TYPE_CHECKING and legacy paths
- All callers work via backward-compatible legacy path
- 13 tests for BattleOrchestrator and BattleEngine injection (9 + 4)
- Full test suite: 5007 passed, 13 failed (pre-existing)

**Phase 3 Summary:**
- Created game/ui/assets/ directory with __init__.py
- Moved ShipThemeManager to game/ui/assets/ship_theme_manager.py
- Created backward-compatible re-export with deprecation warning in ship_theme.py
- Updated 10 direct importers to use new path
- All 469 UI tests pass (+ ship theme logic tests)

**Phase 2 Summary:**
- Added LayerType enum to game/core/constants.py (line 82)
- Updated component_constants.py to re-export from core

**Phase 1 Summary:**
- Removed unused `import pygame` from ship.py
- Replaced pygame.math.Vector2 with game.core.math.Vector2 in 5 AI files
- Removed Fleet TYPE_CHECKING import from battle_controller.py
- No pygame imports remain in game/ai/

**Pre-existing Test Failures (not caused by this project):**
- Note: 13 tests fail when running full suite due to test interference (pass individually)
- Known pre-existing: `test_intercept_integration`, planetary complex tests, etc.

## Overview
Phase 4 of the Legacy Code Cleanup project. Enforce strict architectural layer boundaries by removing cross-layer violations, particularly pygame dependencies in non-UI layers and improper import directions. This enables headless deployment of the simulation layer.

## Goals
- Remove pygame from simulation layer (enable headless deployment)
- Remove pygame from AI layer
- Move LayerType enum to core layer
- Create BattleOrchestrator in UI layer to handle AI controller creation
- Move ShipThemeManager from simulation to UI layer

## Scope
**In Scope:**
- Remove unused pygame import from ship.py
- Replace pygame.math.Vector2 with game.core.math.Vector2 in AI layer
- Move LayerType enum to game/core/constants.py
- Create BattleOrchestrator in game/ui/orchestration/
- Modify BattleEngine.start() to accept pre-created AI controllers
- Move ShipThemeManager to game/ui/assets/
- Fix Fleet TYPE_CHECKING import in battle_controller.py

**Out of Scope:**
- Moving BattleController to UI layer (future project)
- Full headless test infrastructure beyond basic import test
- Removing backward compatibility re-exports (kept for safety)

## Key Files
| Component | File Path | Change |
|-----------|-----------|--------|
| Ship | `game/simulation/entities/ship.py` | Remove unused pygame import |
| AIController | `game/ai/controller.py` | Fix Vector2 imports |
| TargetEvaluator | `game/ai/target_evaluator.py` | Fix Vector2 imports |
| Behaviors | `game/ai/behaviors.py` | Fix Vector2 imports |
| LayerType | `game/core/constants.py` | ADD enum here |
| LayerType (old) | `game/simulation/components/component_constants.py` | Re-export from core |
| ShipThemeManager | `game/simulation/ship_theme.py` → `game/ui/assets/` | Move to UI |
| BattleEngine | `game/simulation/systems/battle_engine.py` | Accept pre-created AI controllers |
| BattleOrchestrator | `game/ui/orchestration/battle_orchestrator.py` | NEW file |
| BattleController | `game/simulation/battle_controller.py` | Fix Fleet TYPE_CHECKING |

## Related Documents
- [design.md](design.md) - Architecture analysis and swarm findings
- [decisions.md](decisions.md) - Full decisions log
- [Legacy Cleanup Phase 4](../../legacy_cleanup/PHASE_4_ENFORCE_LAYER_BOUNDARIES.md) - Original spec

## Verification
### After Each Phase
- [ ] Run `pytest tests/ --testmon` - affected tests pass
- [ ] Run `python -c "from game.simulation.systems.battle_engine import BattleEngine"` - no errors

### Final Verification
- [ ] Run full test suite: `pytest tests/`
- [ ] Run simulation tests: `pytest simulation_tests/`
- [ ] Manual test: Launch game, enter battle, verify combat works
- [ ] Manual test: Open ship builder, verify images display
- [ ] Verify no pygame imports in simulation layer:
  ```bash
  grep -rn "import pygame" game/simulation/ --include="*.py"
  ```
  (Should only return backward-compat re-export in ship_theme.py)

### Layer Boundary Verification
- [ ] `game/simulation/` has no `from game.ai` imports (except in legacy path)
- [ ] `game/simulation/` has no `from game.strategy` imports (TYPE_CHECKING allowed)
- [ ] `game/ai/` has no `import pygame`
- [ ] `game/core/` has no imports from other game layers

## Completion Checklist
- [x] Phase 1 complete
- [x] Phase 2 complete
- [x] Phase 3 complete
- [x] Phase 4 complete
- [x] All tests passing (5007 passed, 13 pre-existing failures)
- [ ] Audit passed
- [ ] User verified
