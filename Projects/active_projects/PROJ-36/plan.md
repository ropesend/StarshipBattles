# PROJ-36: TurnEngine God Class Decomposition

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-36` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-36 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. ConflictResolutionEngine | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. ResourceManagementEngine | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Validation Module | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Legacy Cleanup | Not Started | [phase_4_checklist.md](phase_4_checklist.md) |
| 5. Test Reorganization | Not Started | [phase_5_checklist.md](phase_5_checklist.md) |

## Current State
**Last Updated:** 2026-01-27 13:00
**Active Phase:** Planning Complete - Ready to Start
**Last Action:** Project documents created with full plan and swarm analysis
**Next Action:** Run `pytest tests/` to establish baseline, then begin Phase 1
**Blockers:** None

## Overview
Complete the decomposition of `TurnEngine` (479 lines) into a lightweight orchestrator (~100 lines) that delegates to specialized subsystems. This continues the work started in PROJ-12 Phase 3, addressing the code review finding that TurnEngine remains a "God Class" that orchestrates too much directly.

## Goals
1. Extract combat resolution to `ConflictResolutionEngine`
2. Extract resource management to `ResourceManagementEngine`
3. Create validation module at `game/strategy/validation/`
4. Remove legacy wrapper methods and unused code
5. Maintain 100% test coverage with reorganized tests

## Scope
**In:**
- Extract `_resolve_conflicts`, `_resolve_combat_at_hex`, `_resolve_combat`, `_resolve_combat_simulated` to ConflictResolutionEngine
- Extract `_process_per_turn_resources`, `_auto_disable_components_for_resource` to ResourceManagementEngine
- Move `validate_colonize_order` to `game/strategy/validation/colonize_validator.py`
- Remove unused `_apply_battle_results` method (lines 433-467)
- Remove legacy wrappers: `_calculate_next_hex`, `_spawn_complex`, `_spawn_ship`
- Consolidate duplicate validation in FleetOrderProcessor

**Out:**
- Creating ISubSystem interface (decided: keep explicit delegation)
- Refactoring the 5-phase tick structure
- Adding new functionality

## Key Files
| Component | File Path |
|-----------|-----------|
| TurnEngine (source) | `game/strategy/engine/turn_engine.py` |
| FleetMovementEngine (pattern) | `game/strategy/engine/fleet_movement_engine.py` |
| FleetOrderProcessor (pattern) | `game/strategy/engine/fleet_order_processor.py` |
| ProductionEngine (pattern) | `game/strategy/engine/production_engine.py` |
| IBattleResolver interface | `game/strategy/interfaces/battle_resolver.py` |
| SimulationBattleResolver | `game/strategy/adapters/simulation_adapter.py` |
| ValidationResult | `game/core/validation.py` |
| GameSession (caller) | `game/strategy/engine/game_session.py` (line 269) |
| UI colonization (caller) | `game/ui/screens/strategy_colonization.py` (line 88) |

## Related Documents
- [design.md](design.md) - Architecture analysis and swarm findings
- [decisions.md](decisions.md) - Full decisions log

## New Files to Create
```
game/strategy/engine/
├─ conflict_resolution_engine.py    (NEW - ~150 lines)
├─ resource_management_engine.py    (NEW - ~80 lines)
└─ turn_engine.py                   (MODIFIED - ~100 lines, down from 479)

game/strategy/validation/           (NEW directory)
├─ __init__.py
├─ base.py
└─ colonize_validator.py

tests/unit/strategy/
├─ test_conflict_resolution_engine.py  (NEW)
├─ test_resource_management_engine.py  (NEW)
└─ validation/
   └─ test_colonize_validator.py       (NEW)
```

## Architecture After Completion
```
TurnEngine (Lightweight Orchestrator, ~100 lines)
├─ FleetMovementEngine (existing)
├─ ProductionEngine (existing)
├─ FleetOrderProcessor (existing)
├─ ConflictResolutionEngine (NEW)
│   └─ IBattleResolver (injected)
├─ ResourceManagementEngine (NEW)
└─ ColonizeValidator (NEW, in game/strategy/validation/)
```

## Verification
### Project Start (REQUIRED)
- [ ] Run full test suite: `pytest tests/` - all tests pass (establishes baseline)

### After Each Phase
- [ ] Run `pytest tests/ --testmon` - all affected tests pass
- [ ] Manual: Load a strategy game, advance turn, verify no crashes

### Final Verification
- [ ] TurnEngine is ~100 lines (orchestration only)
- [ ] Run full test suite: `pytest tests/` (NOT --testmon)
- [ ] Run `pytest tests/ --cov=game/strategy/engine` - verify coverage maintained
- [ ] Manual: Play through 5 turns of strategy game
- [ ] All phase checklists complete
- [ ] Audit passed
- [ ] User verified
