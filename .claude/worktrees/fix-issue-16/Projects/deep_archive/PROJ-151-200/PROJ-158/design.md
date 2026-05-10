# PROJ-158: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Initial Analysis

### Production System Architecture (Post-PROJ-79)

The production system was refactored by PROJ-79 from turn-based to tick-based dynamic resource consumption. The live system:

1. `TurnEngine.process_turn()` runs 100 ticks per turn
2. Each tick calls `ProductionEngine.process_construction_tick(tick, empires, galaxy, save_path, harvesting_engine)`
3. `process_construction_tick()` processes three queue types:
   - Base queue (complexes only) — uses `planetary_yard` rates
   - Facility queues (shipyard construction) — uses facility-specific rates
   - Fleet queues (fleet yard construction) — uses `fleet_space_yard` rates × yard count
4. `_process_queue_tick_dynamic()` calculates consumption from `production_rates.json` and `total_cost`
5. Items complete mid-turn when `resources_consumed >= total_cost`
6. Carry-over production: unused tick capacity flows to the next queue item

### Dead API Surface

PROJ-79 left these methods as empty stubs:
- `ProductionEngine.process_production()` → `pass`
- `ProductionEngine.process_fleet_production()` → `pass`
- `TurnEngine.process_production()` → delegates to stub
- `IProductionEngine.process_production` → abstract method (dead contract)
- `IProductionEngine.process_fleet_production` → abstract method (dead contract)

### Dead Queue Item Fields

- `cost_per_tick`: Was pre-calculated at queue creation. Dynamic system ignores it — calculates from `production_rates.json` instead.
- `ticks_in_current_turn`: Was an integer tick counter. Dynamic system uses fractional `resources_consumed` tracking instead.

### Live Queue Item Format

Created by `BuildQueueController._build_cost_tracking()`:
```python
{
    "design_id": str,           # Design identifier
    "type": str,                # "ship", "complex", "fighter", "satellite"
    "turns_remaining": int,     # Display estimate (float in dynamic system)
    "total_cost": Dict[str, float],       # Total resources needed
    "resources_consumed": Dict[str, float] # Cumulative resources spent
}
```

### Production Rates

From `data/production_rates.json`:
| Yard Type | Rate per Turn | Rate per Tick |
|-----------|--------------|---------------|
| planetary_yard | 2000/resource | 20/resource |
| space_shipyard | 3000/resource | 30/resource |
| fleet_space_yard | 3000/resource | 30/resource |

### Dynamic Consumption Math

For an item with `total_cost = {"Metals": 500, "Organics": 200}` at planetary yard (20/tick):
1. Remaining: Metals=500, Organics=200
2. Ticks needed: Metals=500/20=25, Organics=200/20=10
3. Limiting resource = Metals (25 ticks — the slowest)
4. Per tick: Metals=20, Organics=200/25=8 (proportional)
5. After 25 ticks: item complete, 500 Metals + 200 Organics consumed

## Swarm Findings Summary

### Architecture
- `process_production()` has zero callers in game code outside TurnEngine
- `process_fleet_production()` has zero callers in game code outside TurnEngine
- No UI code references either method
- No save/load code references either method
- The TurnEngine calls at lines 275/278 execute but accomplish nothing

### Dependencies & Risks
1. **MockProductionEngine** tracks calls to dead methods — must be updated or DI tests may break
2. **Interface contract** (IProductionEngine) defines dead methods — concrete implementations (and any future ones) must not be required to implement them
3. **Documentation** in `docs/systems/planetary_complex.md` references old API — outdated

### Opportunities Discovered
- Removing dead API simplifies the ProductionEngine public surface to just `process_construction_tick()`
- Test count reduction: ~33 dead-API unit tests can be cleanly deleted
- Remaining tests cover the live system more accurately after rewrite

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.
