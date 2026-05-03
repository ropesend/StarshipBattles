# Plan: Test Coverage - Simulation Core

## Project Information
- **Project ID:** TBD (will be assigned on creation)
- **Created:** 2026-02-14
- **Source:** Sweep 2026-02-14_031258

## Objective

Add comprehensive test coverage to core simulation systems including Ship entity, propulsion abilities, combat systems, and battle services.

## Current State

The simulation layer has significant test gaps:
- Ship class (800+ lines, 40+ methods) has no dedicated test file
- 4 propulsion ability classes have zero tests
- Combat edge cases are untested
- Battle serialization/deserialization is untested

## Target State

- Ship entity has >80% coverage for public methods
- All ability classes have dedicated test files
- Combat systems have edge case and boundary tests
- Save/load roundtrip is verified for battle state

## Phases

### Phase 1: Ship Entity Core Tests
**Files to create:**
- `tests/unit/simulation/entities/test_ship.py`

**Methods to test:**
- `die()` - death logic and state transitions
- `update()` - per-tick updates with context handling
- `recalculate_stats()` - stat aggregation pipeline
- `add_component()` / `remove_component()` - component management
- `change_class()` - class migration logic
- `get_missing_requirements()` / `get_validation_warnings()` - validation

### Phase 2: Propulsion Abilities
**Files to create:**
- `tests/unit/simulation/components/abilities/test_propulsion.py`

**Classes to test:**
- `CombatPropulsion` - thrust calculation
- `ManeuveringThruster` - turn rate calculation
- `StrategicMovement` - movement point calculation
- `WarpJump` - warp capability with tonnage limit, `can_jump()` boundary conditions

### Phase 3: Resource Abilities Expansion
**Files to update:**
- `tests/unit/simulation/components/abilities/test_resource_consumption.py`

**Coverage to add:**
- `ResourceConsumption.get_strategic_cost()` method
- "strategic_per_hex" trigger type
- `ResourceGeneration` class tests
- `ResourceStorage` recalculate with CAPACITY_MULT modifier

### Phase 4: Combat System Edge Cases
**Files to update:**
- `tests/unit/simulation/combat/test_weapon_firing_system.py`
- `tests/unit/simulation/systems/test_battle_engine_tick.py`

**Edge cases to add:**
- Negative damage values
- Zero projectile speed
- Dead target handling
- Resource consumption failure mid-burst
- Concurrent ship death during tick
- Mid-tick target invalidation

### Phase 5: Service Layer Tests
**Files to create/update:**
- `tests/unit/simulation/services/test_battle_service.py` (serialization)
- `tests/unit/simulation/services/test_simulation_design_loader.py` (error recovery)

**Coverage to add:**
- Save/load roundtrip
- Battle continuation after load
- Projectile state preservation
- Malformed JSON handling
- Missing required fields
- Invalid component references

### Phase 6: Helper Class Tests
**Files to create:**
- `tests/unit/simulation/entities/test_ship_stat_querier.py`
- `tests/unit/simulation/entities/test_ship_validator_helper.py`

## Checklist

### Phase 1: Ship Entity
- [ ] Create test_ship.py
- [ ] Test die() state transitions
- [ ] Test update() with various contexts
- [ ] Test recalculate_stats() with component configurations
- [ ] Test add_component() success/failure paths
- [ ] Test remove_component()
- [ ] Test change_class()
- [ ] Test validation helpers

### Phase 2: Propulsion
- [ ] Create test_propulsion.py
- [ ] Test CombatPropulsion
- [ ] Test ManeuveringThruster
- [ ] Test StrategicMovement
- [ ] Test WarpJump.can_jump() boundaries

### Phase 3: Resources
- [ ] Test get_strategic_cost()
- [ ] Test strategic_per_hex trigger
- [ ] Create ResourceGeneration tests
- [ ] Test CAPACITY_MULT modifier

### Phase 4: Combat
- [ ] Add negative damage tests
- [ ] Add zero speed tests
- [ ] Add dead target tests
- [ ] Add resource failure tests
- [ ] Add concurrent death tests

### Phase 5: Services
- [ ] Test save/load roundtrip
- [ ] Test malformed JSON handling
- [ ] Test missing fields
- [ ] Test invalid references

### Phase 6: Helpers
- [ ] Create stat querier tests
- [ ] Create validator helper tests
- [ ] Test config edge cases

## Dependencies

- None - tests can be written independently

## Risks

- Ship entity is complex; tests may reveal latent bugs that need fixing
- Some tests may require mock setup for game state
