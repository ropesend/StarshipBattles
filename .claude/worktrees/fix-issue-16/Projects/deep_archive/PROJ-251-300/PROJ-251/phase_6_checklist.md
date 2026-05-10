# Phase 6: Sub-Engine Per-Tick Validation

**Objective:** Add input validation to all sub-engines so they detect bad state BEFORE mutating, raising clear exceptions instead of silently corrupting data or hitting unexpected `AttributeError`/`TypeError` mid-operation.

**Status:** Complete

---

## Checklist

All 14 engines have `_validate_tick_inputs(empires)` methods that raise `ValidationException` with descriptive messages. All are called at the start of their tick methods.

### Engine 1: HarvestingEngine
- [x] `_validate_tick_inputs()` — checks colonies not None
- [x] Called at start of `process_harvesting_tick()`
- [x] Tests: `TestHarvestingEngineValidation` (2 tests)

### Engine 2: ConsumableManagementEngine
- [x] `_validate_tick_inputs()` — checks fleet.ships not None
- [x] Called at start of `process_per_turn_consumption()`
- [x] Tests: `TestConsumableManagementEngineValidation` (2 tests)

### Engine 3: ResupplyEngine
- [x] `_validate_tick_inputs()` — checks colonies not None
- [x] Called at start of `process_fuel_generation()` AND `process_fleet_resupply()`
- [x] Tests: `TestResupplyEngineValidation` (2 tests)

### Engine 4: PlanetEnergyEngine
- [x] `_validate_tick_inputs()` — checks colonies not None
- [x] Called at start of `process_energy_tick()`
- [x] Tests: `TestPlanetEnergyEngineValidation` (2 tests)

### Engine 5: ProductionEngine
- [x] `_validate_tick_inputs()` — checks empire.resource_pool not None
- [x] Called at start of `process_construction_tick()`
- [x] Tests: `TestProductionEngineValidation` (2 tests)

### Engine 6: EnvironmentalHazardEngine
- [x] `_validate_tick_inputs()` — checks fleet.location not None
- [x] Called at start of `process_environmental_tick()`
- [x] Tests: `TestEnvironmentalHazardEngineValidation` (2 tests)

### Engine 7: OrderProcessor
- [x] `_validate_tick_inputs()` — checks fleet.orders not None
- [x] Called at start of `process_instant_orders()`
- [x] Tests: `TestOrderProcessorValidation` (2 tests)

### Engine 8: ActionExecutionEngine
- [x] `_validate_tick_inputs()` — checks fleet.location not None
- [x] Called at start of `process_action_ticks()`
- [x] Tests: `TestActionExecutionEngineValidation` (2 tests)

### Engine 9: PlanetActionEngine
- [x] `_validate_tick_inputs()` — checks colonies not None
- [x] Called at start of `process_planet_actions_tick()`
- [x] Tests: `TestPlanetActionEngineValidation` (2 tests)

### Engine 10: ComponentActivationEngine
- [x] `_validate_tick_inputs()` — checks colonies not None
- [x] Called at start of `process_activation_tick()`
- [x] Tests: `TestComponentActivationEngineValidation` (2 tests)

### Engine 11: FleetMovementEngine
- [x] `_validate_tick_inputs()` — checks fleet.location not None
- [x] Called at start of `collect_movements()`
- [x] Tests: `TestFleetMovementEngineValidation` (2 tests)

### Engine 12: ConflictResolutionEngine
- [x] `_validate_tick_inputs()` — checks fleet.location not None
- [x] Called at start of `resolve_all_conflicts()`
- [x] Tests: `TestConflictResolutionEngineValidation` (2 tests)

### Engine 13: PopulationEngine
- [x] `_validate_tick_inputs()` — checks colonies not None
- [x] Called at start of `process_population_growth()`
- [x] Tests: `TestPopulationEngineValidation` (2 tests)

### Engine 14: QualityEngine + AtmosphereEngine
- [x] `_validate_tick_inputs()` — checks colonies not None (both engines)
- [x] Called at start of `process_quality_improvement()` and `process_atmosphere()`
- [x] Tests: `TestQualityEngineValidation` + `TestAtmosphereEngineValidation` (4 tests)

### Verification
- [x] All 30 validation tests pass
- [x] Full regression (615 engine tests) — 0 failures
- [x] Full sharded suite: 14720/14723 (3 pre-existing flaky failures)

**Notes:** All tests in `tests/unit/strategy/engine/test_engine_validation.py`. 30 tests total (15 engines × 2: valid-pass + invalid-raises).
