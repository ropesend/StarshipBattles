# PROJ-11 Phase 4: Interface Contracts

## Phase Overview
Define explicit interfaces between layers for clean dependency management.

## Tasks

### Define IBattleResolver Interface
- [x] Create `game/strategy/interfaces/__init__.py`
- [x] Create `game/strategy/interfaces/battle_resolver.py`
- [x] Define `IBattleResolver` abstract base class
- [x] Define `BattleResult` data transfer object
- [x] Document interface contract
  - Docstrings in interface file
  - Example usage in ARCHITECTURE.md

### Create Simulation Adapter
- [x] Create `game/strategy/adapters/__init__.py`
- [x] Create `game/strategy/adapters/simulation_adapter.py`
- [x] Implement `SimulationBattleResolver` class
- [x] Handle conversion between strategy and simulation formats
  - Converts fleets to battle ships with team assignments
  - Converts surviving ShipState objects back to ships
- [x] Test adapter with real battles
  - 13 tests in `tests/unit/strategy/adapters/test_simulation_adapter.py`

### Update TurnEngine to Use Interface
- [x] Inject IBattleResolver into TurnEngine (constructor parameter)
- [x] Update battle resolution to use interface
  - `_resolve_combat_simulated()` now uses injected resolver
- [x] Default to SimulationBattleResolver
- [x] Test with mock resolver for unit tests
  - 7 tests in `TestBattleResolverInjection` class

### Define ISimulationDataProvider Interface (Optional)
- [N/A] Consider interface for simulation → strategy data
  - Not needed: Core layer provides shared data (PLANET_RESOURCES, Vector2)
  - Ship stats calculated in strategy layer via ShipStatsService
- [N/A] Define if needed for ship stat calculations
- [N/A] Implement adapter

### Documentation
- [x] Document layer dependency rules
- [x] Create ARCHITECTURE.md explaining layer structure
  - Created at `docs/ARCHITECTURE.md`
- [x] Add diagrams showing allowed dependencies
  - ASCII diagram of layer hierarchy
- [x] Document interface contracts
  - Interface usage examples in ARCHITECTURE.md

## Verification
- [x] TurnEngine works with injected battle resolver
  - 61 TurnEngine tests pass (including 7 new DI tests)
- [x] Strategy tests can use mock battle resolver
  - TestBattleResolverInjection demonstrates mock usage
- [x] Documentation is complete
- [x] All tests pass
  - 4221 passed, 1 pre-existing failure (unrelated)

## New Tests Added
- `tests/unit/strategy/interfaces/__init__.py`
- `tests/unit/strategy/interfaces/test_battle_resolver.py` (15 tests)
- `tests/unit/strategy/adapters/__init__.py`
- `tests/unit/strategy/adapters/test_simulation_adapter.py` (13 tests)
- `tests/unit/strategy/test_turn_engine.py::TestBattleResolverInjection` (7 tests)

Total: 35 new tests for Phase 4
