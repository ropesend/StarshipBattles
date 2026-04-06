# Phase 6: Sub-Engine Per-Tick Validation

**Objective:** Add input validation to all sub-engines so they detect bad state BEFORE mutating, raising clear exceptions instead of silently corrupting data or hitting unexpected `AttributeError`/`TypeError` mid-operation.

**Key Principle:** Each sub-engine should validate its preconditions at the start of its tick method. If validation fails, raise a descriptive exception. The error boundary from Phase 5 will catch it, halt the turn, and roll back.

**Depends On:** Phase 5 (error boundary catches validation failures and rolls back)

---

## Problem Statement

Currently, only `ProductionEngine` does meaningful per-tick validation (via `_validate_queue_item()`). The other 13 sub-engines assume their inputs are valid. If an empire has a fleet with `None` location, or a planet has a negative energy value, or a facility references a nonexistent component — the engine either silently produces wrong results or throws an unrelated `AttributeError` deep in business logic, with no indication of what precondition was violated.

With the Phase 5 error boundary in place, a validation failure will halt the turn cleanly. The goal here is to make those failures informative rather than cryptic.

## Design

### Validation Strategy: Precondition Checks, Not Exhaustive Audit

This is NOT a full state audit. We add targeted checks for preconditions that:
1. Would cause the engine to produce silently wrong results if violated
2. Would cause cryptic `AttributeError`/`TypeError`/`KeyError` if violated
3. Are fast to check (O(n) in the number of entities, not O(n^2))

Each engine gets a `_validate_tick_inputs()` method called at the start of its tick method. It raises `ValidationException` with a descriptive message if preconditions are violated.

### Per-Engine Validation Specs

#### 1. HarvestingEngine (Phase 0)
**Preconditions:**
- Each empire has a `colonies` iterable
- Each colony has a `planet` with `deposits` dict
- Each facility on a colony planet has `is_operational` attribute
- Resource types in deposits exist in the resource catalog

**Validation:**
```python
def _validate_tick_inputs(self, empires, galaxy):
    for empire in empires:
        for colony in empire.colonies:
            if colony.planet is None:
                raise ValidationException(f"Empire {empire.id}: colony has no planet reference")
```

#### 2. ConsumableManagementEngine (Phase 0b)
**Preconditions:**
- Each fleet's ships have `resources` dict
- Ships flagged as `is_combat_capable()` have valid resource entries

**Validation:** Check ship resources dict exists and has expected keys.

#### 3. ResupplyEngine (Phase 0c, 0d)
**Preconditions:**
- Facilities have `consumable_levels` dict
- Fleets have valid `location` (not None)
- Ships have `resources` dict with fuel key

**Validation:** Check facility consumable_levels exists, fleet locations are not None.

#### 4. PlanetEnergyEngine (Phase 0c1)
**Preconditions:**
- Planets have `energy` and `energy_capacity` (numeric, non-negative)
- Facilities have components with ability data

**Validation:** Check energy values are numeric and non-negative.

#### 5. ProductionEngine (Phase 0e)
**Already has validation** via `_validate_queue_item()`. Minor additions:
- Validate empire `resource_pool` is not None
- Validate colony has construction_queue attribute

#### 6. EnvironmentalHazardEngine (Phase 0f)
**Preconditions:**
- Fleets have valid `location`
- Ships have `current_hp` (numeric, positive for alive ships)

**Validation:** Check fleet locations not None, ship HP numeric.

#### 7. OrderProcessor (Phase 1)
**Preconditions:**
- Fleets have valid `orders` list
- Fleet orders have `order_type` attribute
- JOIN_FLEET targets reference valid fleet IDs

**Validation:** Check orders are well-formed, target fleet exists for JOIN_FLEET.

#### 8. ActionExecutionEngine (Phase 1.5)
**Preconditions:**
- Fleets with action orders have valid `speed` > 0
- Order has `execution_progress` (numeric)

**Validation:** Check speed positive, execution_progress numeric.

#### 9. PlanetActionEngine (Phase 1.6)
**Preconditions:**
- Planets with orders have valid `orders` list
- Target facility referenced in order exists on the planet

**Validation:** Check target facility exists (already partially done via `_target_facility_exists()`).

#### 10. ComponentActivationEngine (Phase 1.7)
**Preconditions:**
- Facilities with `component_states` have valid state objects
- Each `ComponentActivationState` has required attributes (phase, progress)

**Validation:** Check component_states entries are valid.

#### 11. FleetMovementEngine (Phase 2, 3)
**Preconditions:**
- Moving fleets have `speed` > 0
- Moving fleets have valid `location` (not None)
- Moving fleets have `path` or valid MOVE order with destination

**Validation:** Check speed and location for fleets with MOVE orders.

#### 12. ConflictResolutionEngine (Phase 4)
**Preconditions:**
- All fleets have valid `location`
- All fleets have `owner_id`
- Battle resolver is not None

**Validation:** Check fleet locations and owner_ids, battle resolver available.

#### 13. PopulationEngine (Post-tick)
**Preconditions:**
- Populations have `count` (numeric, non-negative)
- Colonies have `planet` reference

**Validation:** Check population count is numeric.

#### 14. QualityEngine, AtmosphereEngine (Post-tick)
**Preconditions:**
- Planet deposits have `quality` (numeric)
- Planet atmosphere values are numeric

**Validation:** Check numeric types on quality/atmosphere values.

---

## Checklist

### Approach: Engine-by-Engine, Test-First

Work through each engine in tick execution order. For each engine:
1. Write tests for the validation method
2. Implement the validation method
3. Wire it into the tick method
4. Run tests

### Engine 1: HarvestingEngine
- [ ] Write test: `_validate_tick_inputs` passes for valid empires
- [ ] Write test: raises `ValidationException` when colony.planet is None
- [ ] Write test: raises `ValidationException` when planet.deposits is None
- [ ] Implement `_validate_tick_inputs()` in HarvestingEngine
- [ ] Call it at start of `process_harvesting_tick()`
- [ ] Run harvesting tests — pass

### Engine 2: ConsumableManagementEngine
- [ ] Write test: `_validate_tick_inputs` passes for valid empires
- [ ] Write test: raises `ValidationException` when ship.resources is None
- [ ] Implement `_validate_tick_inputs()` in ConsumableManagementEngine
- [ ] Call it at start of `process_per_turn_consumption()`
- [ ] Run consumable tests — pass

### Engine 3: ResupplyEngine
- [ ] Write test: `_validate_tick_inputs` passes for valid empires
- [ ] Write test: raises `ValidationException` when fleet.location is None
- [ ] Write test: raises `ValidationException` when facility.consumable_levels is None
- [ ] Implement `_validate_tick_inputs()` in ResupplyEngine
- [ ] Call it at start of `process_fuel_generation()` and `process_fleet_resupply()`
- [ ] Run resupply tests — pass

### Engine 4: PlanetEnergyEngine
- [ ] Write test: `_validate_tick_inputs` passes for valid empires
- [ ] Write test: raises `ValidationException` when planet.energy is not numeric
- [ ] Implement `_validate_tick_inputs()` in PlanetEnergyEngine
- [ ] Call it at start of `process_energy_tick()`
- [ ] Run energy tests — pass

### Engine 5: ProductionEngine (extend existing validation)
- [ ] Write test: raises `ValidationException` when empire.resource_pool is None
- [ ] Add resource_pool check to existing validation
- [ ] Run production tests — pass

### Engine 6: EnvironmentalHazardEngine
- [ ] Write test: `_validate_tick_inputs` passes for valid empires
- [ ] Write test: raises `ValidationException` when fleet.location is None
- [ ] Implement `_validate_tick_inputs()` in EnvironmentalHazardEngine
- [ ] Call it at start of `process_environmental_tick()`
- [ ] Run environmental tests — pass

### Engine 7: OrderProcessor
- [ ] Write test: `_validate_tick_inputs` passes for valid empires
- [ ] Write test: raises `ValidationException` when fleet.orders is None
- [ ] Implement `_validate_tick_inputs()` in OrderProcessor
- [ ] Call it at start of `process_instant_orders()`
- [ ] Run order tests — pass

### Engine 8: ActionExecutionEngine
- [ ] Write test: `_validate_tick_inputs` passes for valid empires
- [ ] Write test: raises `ValidationException` when order.execution_progress is None
- [ ] Implement `_validate_tick_inputs()` in ActionExecutionEngine
- [ ] Call it at start of `process_action_ticks()`
- [ ] Run action tests — pass

### Engine 9: PlanetActionEngine
- [ ] Write test: `_validate_tick_inputs` passes for valid empires
- [ ] Write test: raises `ValidationException` when target facility missing
- [ ] Implement `_validate_tick_inputs()` in PlanetActionEngine
- [ ] Call it at start of `process_planet_actions_tick()`
- [ ] Run planet action tests — pass

### Engine 10: ComponentActivationEngine
- [ ] Write test: `_validate_tick_inputs` passes for valid empires
- [ ] Write test: raises `ValidationException` when component_state is malformed
- [ ] Implement `_validate_tick_inputs()` in ComponentActivationEngine
- [ ] Call it at start of `process_activation_tick()`
- [ ] Run activation tests — pass

### Engine 11: FleetMovementEngine
- [ ] Write test: `_validate_tick_inputs` passes for valid empires
- [ ] Write test: raises `ValidationException` when moving fleet has None location
- [ ] Write test: raises `ValidationException` when moving fleet has speed <= 0
- [ ] Implement `_validate_tick_inputs()` in FleetMovementEngine
- [ ] Call it at start of `collect_movements()`
- [ ] Run movement tests — pass

### Engine 12: ConflictResolutionEngine
- [ ] Write test: `_validate_tick_inputs` passes for valid empires
- [ ] Write test: raises `ValidationException` when fleet.location is None
- [ ] Write test: raises `ValidationException` when battle_resolver is None
- [ ] Implement `_validate_tick_inputs()` in ConflictResolutionEngine
- [ ] Call it at start of `resolve_all_conflicts()`
- [ ] Run conflict tests — pass

### Engine 13: PopulationEngine
- [ ] Write test: `_validate_tick_inputs` passes for valid empires
- [ ] Write test: raises `ValidationException` when population.count is not numeric
- [ ] Implement `_validate_tick_inputs()` in PopulationEngine
- [ ] Call it at start of `process_population_growth()`
- [ ] Run population tests — pass

### Engine 14: QualityEngine + AtmosphereEngine
- [ ] Write test: `_validate_tick_inputs` passes for valid empires
- [ ] Write test: raises `ValidationException` when deposit quality is not numeric
- [ ] Write test: raises `ValidationException` when atmosphere value is not numeric
- [ ] Implement `_validate_tick_inputs()` in both engines
- [ ] Call at start of respective methods
- [ ] Run quality/atmosphere tests — pass

### Integration Tests
- [ ] Write test: full turn with one engine receiving invalid state → EnginePhaseError with validation detail
- [ ] Write test: validation failure at tick 1 triggers immediate rollback (no partial processing)
- [ ] Write test: validation messages include empire_id, fleet_id, or planet_id for debugging

### Performance
- [ ] Benchmark: measure per-tick validation overhead across all 14 engines
- [ ] Verify overhead is < 1ms per tick (100ms per turn budget for validation)
- [ ] If any engine's validation is slow, optimize by caching or reducing check scope

### Verification
- [ ] Run full test suite — no regressions
- [ ] All 14 engines have `_validate_tick_inputs()` methods
- [ ] All tick entry points call validation before mutation
