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
| 1. ConflictResolutionEngine | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. ResourceManagementEngine | Complete | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Validation Module | Complete | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Legacy Cleanup | Complete | [phase_4_checklist.md](phase_4_checklist.md) |
| 5. Test Reorganization | Not Started | [phase_5_checklist.md](phase_5_checklist.md) |

## Current State
**Last Updated:** 2026-01-27 (Session 2)
**Active Phase:** Phase 5 - Test Reorganization
**Last Action:** Phase 4 complete - Removed legacy wrapper methods, cleaned up imports
**Next Action:** Begin Phase 5 - Reorganize tests for new engine structure
**Blockers:** None

### Phase 1 Summary (Complete)
- Created `game/strategy/engine/conflict_resolution_engine.py` (186 lines)
- Created `tests/unit/strategy/test_conflict_resolution_engine.py` (25 tests)
- TurnEngine reduced from 479 → 338 lines (141 lines removed)
- Updated integration tests in `test_gameplay_loop.py`

### Phase 2 Summary (Complete)
- Created `game/strategy/engine/resource_management_engine.py` (116 lines)
- Created `tests/unit/strategy/test_resource_management_engine.py` (24 tests)
- TurnEngine reduced from 338 → 282 lines (56 lines removed)
- Removed `TestPerTurnResources` class from test_turn_engine.py, updated mocking approach
- All tests pass: 49 TurnEngine tests, 24 ResourceManagementEngine tests, 44 integration tests

### Phase 3 Summary (Complete)
- Created `game/strategy/validation/` module with:
  - `__init__.py` - Module exports
  - `base.py` - OrderValidationRule ABC
  - `colonize_validator.py` - ColonizeValidator (54 lines)
- Created `tests/unit/strategy/validation/test_colonize_validator.py` (14 tests)
- TurnEngine.validate_colonize_order reduced from 41 lines to 15 lines (delegation)
- FleetOrderProcessor.process_colonize now uses ColonizeValidator (removed duplicate validation)
- Removed unused `validation_result` import from TurnEngine
- All tests pass: 49 TurnEngine + 14 ColonizeValidator + 17 integration colonization tests

### Phase 4 Summary (Complete)
- Removed legacy wrapper methods: `_calculate_next_hex`, `_spawn_complex`, `_spawn_ship`
- Updated tests in `test_turn_engine.py` and `test_advanced_fleet_orders.py` to use `movement_engine` directly
- Removed unused `OrderType` import from TurnEngine
- Updated module docstring to reflect orchestrator role
- Fixed tests in `test_turn_engine_strategy.py` and `test_resource_system.py`:
  - Changed `engine._process_per_turn_resources` to `engine.resource_engine.process_per_turn_consumption`
  - Changed `engine._auto_disable_components_for_resource` to `engine.resource_engine._auto_disable_components_for_resource`
  - Updated patch locations for `get_component_registry`
- TurnEngine reduced from 257 → 222 lines (35 lines removed)
- All tests pass: 4963 tests total

### Progress Summary
- Original TurnEngine: 479 lines
- After Phase 1: 338 lines (-141 lines, -29%)
- After Phase 2: 282 lines (-56 lines, -12%)
- After Phase 3: 257 lines (-25 lines, -5%)
- After Phase 4: 222 lines (-35 lines, -7%)
- Total reduction: 257 lines (54%)

### Handoff Notes for Next Session
1. Run `pytest tests/ --testmon` to verify baseline (4963 tests should pass)
2. Open `phase_5_checklist.md` for Phase 5 tasks
3. Phase 5 involves test verification and reorganization (mostly optional at this point)
4. TurnEngine is 222 lines - significant improvement from 479 but above ~100 target
5. Core decomposition work is COMPLETE - Phase 5 is primarily verification

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
- [x] Run full test suite: `pytest tests/` - all tests pass (establishes baseline)

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
