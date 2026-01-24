# PROJ-11 Phase 4: Interface Contracts

## Phase Overview
Define explicit interfaces between layers for clean dependency management.

## Tasks

### Define IBattleResolver Interface
- [ ] Create `game/strategy/interfaces/__init__.py`
- [ ] Create `game/strategy/interfaces/battle_resolver.py`
- [ ] Define `IBattleResolver` abstract base class
- [ ] Define `BattleResult` data transfer object
- [ ] Document interface contract

### Create Simulation Adapter
- [ ] Create `game/strategy/adapters/__init__.py`
- [ ] Create `game/strategy/adapters/simulation_adapter.py`
- [ ] Implement `SimulationBattleResolver` class
- [ ] Handle conversion between strategy and simulation formats
- [ ] Test adapter with real battles

### Update TurnEngine to Use Interface
- [ ] Inject IBattleResolver into TurnEngine (constructor parameter)
- [ ] Update battle resolution to use interface
- [ ] Default to SimulationBattleResolver
- [ ] Test with mock resolver for unit tests

### Define ISimulationDataProvider Interface (Optional)
- [ ] Consider interface for simulation → strategy data
- [ ] Define if needed for ship stat calculations
- [ ] Implement adapter

### Documentation
- [ ] Document layer dependency rules
- [ ] Create ARCHITECTURE.md explaining layer structure
- [ ] Add diagrams showing allowed dependencies
- [ ] Document interface contracts

## Verification
- [ ] TurnEngine works with injected battle resolver
- [ ] Strategy tests can use mock battle resolver
- [ ] Documentation is complete
- [ ] All tests pass
