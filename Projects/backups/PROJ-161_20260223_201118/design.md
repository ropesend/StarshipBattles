# PROJ-161: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Initial Analysis

### Current Turn Processing Order
```
Turn Start (before loop):
  Line 258: harvesting_engine.process_harvesting(empires)      <-- ALL at once
  Line 261: maintenance_engine.process_maintenance(empires)     <-- ALL at once

Ticks 1-100 Loop (_process_tick):
  Phase 0:  ResourceManagementEngine.process_per_turn_consumption(tick)  -- 1/100th
  Phase 0a: ResupplyEngine.process_fuel_generation(tick)                 -- 1/100th
  Phase 0b: ResupplyEngine.process_fleet_resupply(tick)                  -- per tick
  Phase 0c: ProductionEngine.process_construction_tick(tick, ..., harvesting_engine)  -- 1/100th
  Phase 1:  Instant Orders (JOIN_FLEET)
  Phase 2:  Calculate Moves
  Phase 3:  Apply Moves
  Phase 4:  Combat

Turn End (after loop):
  End-of-turn orders (colonize, superweapons)
  PopulationEngine.process_population_growth()
```

### Problem
Harvesting dumps 100% of resources at tick 1. Maintenance deducts 100% at tick 1. All other economy engines spread across 100 ticks. This means:
- Construction never stalls mid-turn waiting for resources (they're all front-loaded)
- Maintenance removes entities before any per-tick harvesting could save them
- The tick-by-tick model is undermined

### Target Turn Processing Order
```
Turn Start:
  self.last_scuttle_events = []  (initialize accumulator)

Ticks 1-100 Loop (_process_tick):
  Phase 0:  HarvestingEngine.process_harvesting_tick(tick)               -- 1/100th  NEW
  Phase 0a: MaintenanceEngine.process_maintenance_tick(tick)             -- 1/100th  MOVED
  Phase 0b: ResourceManagementEngine.process_per_turn_consumption(tick)  -- 1/100th
  Phase 0c: ResupplyEngine.process_fuel_generation(tick)                 -- 1/100th
  Phase 0d: ResupplyEngine.process_fleet_resupply(tick)                  -- per tick
  Phase 0e: ProductionEngine.process_construction_tick(tick)             -- 1/100th  (no harvesting_engine param)
  Phase 1:  Instant Orders (JOIN_FLEET)
  Phase 2:  Calculate Moves
  Phase 3:  Apply Moves
  Phase 4:  Combat

Turn End (after loop):
  End-of-turn orders (colonize, superweapons)
  PopulationEngine.process_population_growth()
```

## Existing Per-Tick Pattern to Reuse

All per-tick engines follow the same pattern. Reference: `ResupplyEngine.process_fuel_generation()`:

```python
def process_fuel_generation(self, tick: int, empires) -> List[ResupplyEvent]:
    """Generate 1/100th of per-turn fuel output each tick."""
    for empire in empires:
        for colony in empire.colonies:
            for facility in colony.facilities:
                fuel_gen_rate = self._get_fuel_generation_rate(facility)  # per-turn total
                tick_generation = fuel_gen_rate / 100.0  # KEY: divide by 100
                overflow = facility.add_fuel(tick_generation, self._registries)
```

### Key Patterns to Reuse
- **Per-tick division**: `game/strategy/engine/resupply_engine.py:109` - `tick_generation = fuel_gen_rate / 100.0`
- **Per-tick division**: `game/strategy/engine/resource_management_engine.py:88` - `tick_cost = total_cost / 100.0`
- **Harvest formula**: `game/strategy/engine/harvesting_engine.py:306-314` - `harvest = base_rate * quality`
- **Maintenance formula**: `game/strategy/engine/maintenance_engine.py:234-245` - `calculate_maintenance_cost(design_data, MAINTENANCE_RATE)`
- **Storage cap enforcement**: `game/strategy/data/empire.py` - `empire.add_resources()` returns overflow
- **Scuttle event accumulation**: `game/strategy/engine/turn_engine.py:167` - `self.last_scuttle_events`

## Legacy Code to Remove

### `_apply_partial_harvest` (ProductionEngine)
**File:** `game/strategy/engine/production_engine.py:386-441`
**Why redundant:** With per-tick harvesting, newly-built facilities naturally start harvesting on the next tick. The proportional-fraction calculation is no longer needed.

### `harvesting_engine` parameter threading
The `harvesting_engine` parameter is threaded through 7 locations in ProductionEngine solely to support `_apply_partial_harvest`:
1. `process_construction_tick` signature (line 90)
2. `_process_queue_tick_dynamic` call x3 (lines 115, 126, 175)
3. `_process_queue_tick_dynamic` signature (line 188)
4. `_complete_item` call x2 (lines 276, 350)
5. `_complete_item` signature (line 353)
6. `_apply_partial_harvest` call (lines 378-382)

All of these will be removed.

## Dependencies & Risks
1. **Floating-point accumulation** - 100 divisions by 100 then summed may differ slightly from single calculation. Mitigation: Use `pytest.approx` in tests.
2. **Scuttle timing change** - Scuttling can happen at any tick, not just turn-start. An empire that would have been scuttled at turn-start might harvest some resources first. This is actually more correct.
3. **Storage recalc every tick** - 100x per turn is more work, but the operation is lightweight (scanning facility abilities).
4. **UI `last_scuttle_events`** - Must accumulate across all 100 ticks. UI code at `game/ui/screens/strategy_screen.py:344` reads it at turn end -- unchanged.

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.
