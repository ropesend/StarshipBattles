# Planetary Complex System

This document describes the planetary complex (facility) building system: design, construction queue, tick-based production, and spawning.

---

## Overview

Players design planetary complexes in the workshop (same UI as ships), queue them for construction at colonies or fleet yards, and production completes mid-turn via tick-based dynamic resource consumption. Completed complexes become `PlanetaryFacility` instances on planets.

### User Workflow

```
1. Design complex in Workshop (select "Planetary Complex" hull tier)
2. Queue complex for building via Build Queue UI
3. ProductionEngine consumes resources per tick (100 ticks/turn)
4. When resource cost fully consumed, facility spawns on planet
5. Shipyard facilities enable ship construction at that colony
```

---

## Architecture

### Layer Separation

- **Strategy layer:** `PlanetaryFacility` data model, `Planet.facilities` list, `ProductionEngine`
- **UI layer:** `BuildQueueScreen` manages queue display and category filtering
- **Simulation layer:** Component abilities (`ResourceHarvesterAbility`, `SpaceShipyardAbility`)

### Key Design Principles

1. **Tick-based production** -- resources consumed dynamically each tick, not turn-counting
2. **Facilities are instances** -- each has a UUID, design_data, and operational status
3. **Parallel construction** -- each shipyard facility has its own queue processed independently
4. **Design data embedded** -- facility stores full design JSON for offline querying

---

## Data Models

### PlanetaryFacility

**File:** `game/strategy/data/planetary_facility.py`

```python
@dataclass
class PlanetaryFacility:
    instance_id: str              # UUID
    design_id: str                # Reference to design file
    name: str                     # Facility name
    design_data: Dict[str, Any]   # Full complex design JSON
    is_operational: bool = True
    construction_queue: List[Dict[str, Any]] = field(default_factory=list)
    resource_levels: Dict[str, float] = field(default_factory=dict)
```

Key properties and methods:
- `is_shipyard` -- checks design_data for `space_shipyard` component or `SpaceShipyard` ability
- `get_fuel_storage()` / `add_fuel()` / `withdraw_fuel()` -- fuel resource management
- `get_max_fuel_storage(registries)` -- scans components for `ResourceStorage` abilities
- `from_dict(data)` -- deserialization with required key validation

### Planet Integration

`Planet.facilities` is a list of `PlanetaryFacility`. The `has_space_shipyard` property checks all operational facilities for a shipyard component.

### Construction Queue Item Format

```python
{
    "design_id": "mining_complex_mk1",
    "type": "complex",             # or "ship", "fighter", "satellite"
    "total_cost": {"metals": 50, "organics": 10},
    "resources_consumed": {"metals": 0, "organics": 0},
    "turns_remaining": 2.5         # Estimated, updated each tick for UI
}
```

---

## Production Model (Tick-Based)

**File:** `game/strategy/engine/production_engine.py`

Production uses dynamic resource consumption per tick, not turn-counting.

### Per-Turn Flow (100 ticks)

```
TurnEngine.process_turn()
  |
  +-- 100-tick subturn loop:
        |
        ProductionEngine.process_construction_tick(tick, empires, galaxy)
          |
          For each empire:
            1. Base queue (complexes only) -- planetary yard rate
            2. Facility queues (each shipyard independently) -- per-facility rate
            3. Fleet queues (if fleet has space yards) -- rate * yard count
```

### Dynamic Resource Consumption Algorithm

Each tick, `_process_queue_tick_dynamic()` processes the head of each queue:

1. **Validate** -- check type constraints (complex-only queue, fleet location).
2. **Calculate remaining cost** -- `total_cost - resources_consumed` per resource.
3. **Find limiting resource** -- resource requiring the most ticks at current production rate.
4. **Calculate tick expenditure** -- `min(available_capacity, ticks_needed)`.
5. **Check affordability** -- `empire.has_resources(cost_this_step)`.
6. **Consume resources** -- deduct from empire, add to `resources_consumed`.
7. **Check completion** -- if all `resources_consumed >= total_cost`, spawn the item.
8. **Carry-over** -- remaining tick capacity continues to next queue item (mid-tick completion).

Items can complete mid-turn when their full resource cost is consumed. Multiple items can complete in a single turn if the first finishes early.

### Production Rates

Production rates are per-turn (divided by 100 for per-tick). Rates come from `BuildQueueSource`:
- `"planetary_yard"` -- default rate for base colony queue
- Per-facility rates for shipyard queues
- `"fleet_space_yard"` -- rate for fleet construction, multiplied by yard count

### Constants

| Constant | Value | Purpose |
|----------|-------|---------|
| `TICKS_PER_TURN` | 100 | Ticks per game turn |
| `TICK_CAPACITY_EPSILON` | 0.0001 | Minimum tick capacity to continue |
| `COMPLETION_EPSILON` | 0.001 | Float tolerance for completion check |
| `MAX_QUEUE_ITERATIONS` | 10 | Safety limit per tick |

---

## Spawning

### Complex Spawning (`_spawn_complex`)

1. Load design_data from `DesignLibrary(save_path, empire_id)`.
2. Create `PlanetaryFacility` with UUID, design_data, `is_operational=True`.
3. Append to `planet.facilities`.
4. Log `COMPLEX_BUILT` event.

Fleet yards can also build complexes (`_spawn_fleet_complex`), spawning on the planet at the fleet's hex location.

### Ship Spawning (`_spawn_ship`)

1. Load design_data from `DesignLibrary`.
2. Create `ShipInstance` via `ShipInstance.create()`.
3. Create new `Fleet` at planet location, add ship.
4. Register fleet via `empire.add_fleet()`.
5. Log `SHIP_BUILT` event.

---

## Components

Six components restricted to `"Planetary Complex"` vehicle type, defined in `data/components.json`:

| Component | Ability |
|-----------|---------|
| `metal_harvester` | `ResourceHarvesterAbility` (Metals) |
| `organic_harvester` | `ResourceHarvesterAbility` (Organics) |
| `vapor_harvester` | `ResourceHarvesterAbility` (Vapors) |
| `radioactive_harvester` | `ResourceHarvesterAbility` (Radioactives) |
| `exotic_harvester` | `ResourceHarvesterAbility` (Exotics) |
| `space_shipyard` | `SpaceShipyardAbility` |

**Ability classes:** `game/simulation/components/abilities/harvester.py`

---

## UI

### BuildQueueScreen

**File:** `game/ui/screens/build_queue_screen.py`

Full-screen UI with three panels:
- **Items List** (left) -- available designs filtered by category
- **Build Queue** (center) -- queued items with estimated turns remaining
- **Filter Panel** (right) -- category buttons (Complexes, Ships, Satellites, Fighters) plus Add/Remove

Accessed from the strategy screen via the "Build Yard" button on owned planets.

---

## Key Files

| Component | File |
|-----------|------|
| PlanetaryFacility | `game/strategy/data/planetary_facility.py` |
| Planet (facilities list) | `game/strategy/data/planet.py` |
| ProductionEngine | `game/strategy/engine/production_engine.py` |
| BuildQueueScreen | `game/ui/screens/build_queue_screen.py` |
| Harvester abilities | `game/simulation/components/abilities/harvester.py` |
| Component definitions | `data/components.json` |
| DesignLibrary | `game/strategy/systems/design_library.py` |
| Strategy screen integration | `game/ui/screens/strategy_screen.py` |
| Build queue data sources | `game/strategy/data/build_queue_source.py` |
| Design cost calculator | `game/strategy/services/design_cost_calculator.py` |
