# PROJ-XX: Test Coverage -- Core and Simulation

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-XX` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-XX [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Engine and Core Tests | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. AI Controller Tests | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Simulation Entity Tests | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Simulation Service Tests | Not Started | [phase_4_checklist.md](phase_4_checklist.md) |
| 5. Simulation Component Tests | Not Started | [phase_5_checklist.md](phase_5_checklist.md) |

## Current State
**Last Updated:** 2026-02-11
**Active Phase:** Planning
**Last Action:** Project created from sweep findings
**Next Action:** Begin Phase 1 tasks
**Blockers:** None

## Overview
Write unit and integration tests for all untested classes and methods in the core, engine, AI, research, and simulation layers. These layers form the backbone of the application and need comprehensive test coverage to prevent regressions. The project covers completely untested classes (BattleService, ProjectileManager, AbilityAggregator), missing edge case tests for combat calculations, and missing integration tests for complex workflows.

## Goals
- Achieve unit test coverage for all 8 Critical untested classes/methods
- Write boundary and edge case tests for physics, collision, and spatial systems
- Write integration tests for AIController + StrategyManager workflow
- Write unit tests for all simulation services (BattleService, ModifierService, VehicleDesignService)
- Write unit tests for all simulation entities (ShipFormation, AbilityAggregator, CombatEndurance, etc.)
- Write unit tests for simulation component managers and abilities
- Improve test quality for existing fragile tests (reduce heavy mocking)

## Scope
**In:**
- All TCG findings in FND shard (core, engine, AI, research)
- All TCG findings in SIM shard (simulation)
- New test files and test cases
- Test infrastructure improvements (fragile test fixes)

**Out:**
- Strategy layer test gaps (separate project)
- UI layer test gaps (separate project)
- Code changes beyond what is needed for testability

## Key Files
| Component | File Path |
|-----------|-----------|
| PhysicsBody (untested) | `game/engine/physics.py` |
| CollisionSystem (untested hit detection) | `game/engine/collision.py` |
| AIController (integration gaps) | `game/ai/controller.py` |
| BattleService (no tests) | `game/simulation/services/battle_service.py` |
| ProjectileManager (no tests) | `game/simulation/projectile_manager.py` |
| AbilityAggregator (no tests) | `game/simulation/entities/ability_aggregator.py` |
| ShipPhysicsMixin (no tests) | `game/simulation/entities/ship_physics_mixin.py` |
| ShipFormation (no tests) | `game/simulation/entities/ship_formation.py` |
| BattleEngine (tick processing untested) | `game/simulation/systems/battle_engine.py` |

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log

## Verification
- [ ] All phase checklists complete
- [ ] All 8 Critical findings have test coverage
- [ ] All new tests pass
- [ ] No existing tests broken
- [ ] Full test suite passes (pytest tests/ -n 12)
- [ ] Audit passed
- [ ] User verified
