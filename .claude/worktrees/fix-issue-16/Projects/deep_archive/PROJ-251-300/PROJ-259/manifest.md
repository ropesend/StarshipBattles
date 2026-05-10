# PROJ-259 File Manifest

> Generated during project planning. Used by /proj-parallel for conflict detection.
> Updated if implementation discovers additional files.

## New Files

| File | Type | Notes |
|------|------|-------|
| `game/core/state_machine.py` | Production | ScreenStateMachine class with transition table, guards, state stack |
| `game/strategy/engine/turn_engine_config.py` | Production | TurnEngineConfig frozen dataclass bundling 13 optional engine parameters |
| `game/simulation/systems/tick_phase.py` | Production | ITickPhase protocol, TickPhaseRegistry, 5 default phase classes |
| `tests/unit/core/test_state_machine.py` | Test | Tests for ScreenStateMachine |
| `tests/unit/strategy/engine/test_turn_engine_config.py` | Test | Tests for TurnEngineConfig dataclass and TurnEngine config integration |
| `tests/unit/simulation/systems/test_tick_phases.py` | Test | Tests for ITickPhase, TickPhaseRegistry, default phases, custom injection |

## Modified Files

| File | Type | Phase | Notes |
|------|------|-------|-------|
| `game/app.py` | Production | 1 | Replace 23 _switch_scene() calls with ScreenStateMachine; remove 3 return-state fields |
| `game/core/__init__.py` | Production | 1 | Add ScreenStateMachine to exports |
| `game/strategy/engine/turn_engine.py` | Production | 2 | Accept TurnEngineConfig; remove 13 individual engine kwargs |
| `game/strategy/engine/game_session.py` | Production | 2 | Update TurnEngine() calls (lines 91, 327) if needed |
| `game/simulation/systems/battle_engine.py` | Production | 3 | Add tick_phases parameter; refactor update() to delegate to TickPhaseRegistry |
| `game/simulation/__init__.py` | Production | 3 | Add ITickPhase, TickPhaseRegistry to exports |
| `tests/unit/strategy/turn_engine/conftest.py` | Test | 2 | Update TurnEngine fixture if needed |
| `tests/unit/strategy/turn_engine/test_dependency_injection.py` | Test | 2 | Migrate engine kwargs to TurnEngineConfig |
| `tests/unit/strategy/mocks/mock_engines.py` | Test | 2 | Update example comment |
| `tests/unit/simulation/systems/test_battle_engine_tick.py` | Test | 3 | Update if mocking assumptions changed |
| `docs/01_ARCHITECTURE.md` | Docs | 4 | Add new files to package tables |
| `docs/02_PATTERNS.md` | Docs | 4 | Add 3 new pattern sections |
| `docs/systems/strategy_layer.md` | Docs | 4 | Update TurnEngine constructor docs |
| `docs/systems/combat_simulation.md` | Docs | 4 | Document ITickPhase and tick phase registry |

## Potentially Modified Files (depends on implementation discoveries)

| File | Type | Phase | Notes |
|------|------|-------|-------|
| `tests/integration/gameplay_loop/conftest.py` | Test | 2 | If it injects individual engines |
| `tests/integration/colonization/conftest.py` | Test | 2 | If it injects individual engines |
| `tests/integration/strategy/production/conftest.py` | Test | 2 | If it injects individual engines |
| `tests/integration/test_complex_workflow.py` | Test | 2 | 5 TurnEngine() calls -- update if they inject engines |
| `tests/integration/strategy/turn_engine/*.py` | Test | 2 | Multiple files with TurnEngine() calls |
| `tests/integration/strategy/test_*.py` | Test | 2 | Multiple files with TurnEngine() calls |
| `tests/integration/resource_system/test_resource_pipeline.py` | Test | 2 | 2 TurnEngine() calls |
| `tests/unit/strategy/engine/test_*.py` | Test | 2 | TurnEngine() calls in engine tests |
| `game/core/exceptions.py` | Production | 1 | Only if StateException doesn't already exist |

## Conflict Risk Assessment

| File | Also Modified By | Risk |
|------|-----------------|------|
| `game/app.py` | PROJ-86 (UI Tier) | Medium -- both touch app.py but for different reasons. PROJ-259 changes transition mechanics, PROJ-86 changes screen internals. |
| `game/strategy/engine/turn_engine.py` | PROJ-87 (Strategy Data Tier) | Low -- PROJ-87 extracts data from strategy, PROJ-259 changes constructor signature. |
| `game/simulation/systems/battle_engine.py` | PROJ-88 (Simulation Core Tier) | Low -- PROJ-88 extracts simulation internals, PROJ-259 changes update() dispatch. |
| `docs/01_ARCHITECTURE.md` | Any active project | Low -- additive changes only (new entries in tables). |
| `docs/02_PATTERNS.md` | Any active project | Low -- additive changes only (new sections). |
