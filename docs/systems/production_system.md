# Production System

This document describes the unified construction/production system: build queues, tick-based resource consumption, turn estimation, and item spawning. The same `ProductionEngine` algorithm handles all build contexts — planet base queues (complexes), planet shipyard facility queues (ships), and fleet space yard queues (ships and complexes).

---

## Overview

Players design items in the Workshop (ships, complexes, satellites, fighters), queue them for construction via the Build Queue UI, and `ProductionEngine` consumes resources per tick (100 ticks/turn) until completion. The system is context-agnostic: one algorithm processes all queue types with parameterized production rates and context-specific spawning.

### Build Contexts

| Context | Queue Source | Can Build | Production Rate | Requirement |
|---------|-------------|-----------|-----------------|-------------|
| Planet base queue | `planet.construction_queue` | Complexes only | `planetary_yard` (2000/resource/turn) | Facility with `PlanetaryYard` ability |
| Planet shipyard facility | `facility.construction_queue` | Ships + complexes | Per-facility rate (default 30000, with bonus) | `SpaceShipyard` ability on facility |
| Fleet space yard | `fleet.construction_queue` | Ships + complexes | `space_shipyard` rate × yard count | `SpaceShipyard` ability on fleet ship |

### User Workflow

```
1. Design item in Workshop (ship hull, planetary complex, fighter, satellite)
2. Queue item at a build location via Build Queue UI
3. turns_remaining pre-calculated using estimate_build_turns() (limiting-resource formula)
4. ProductionEngine consumes resources per tick (100 ticks/turn)
5. When resource cost fully consumed, item spawns:
   - Complex → PlanetaryFacility on planet
   - Ship from planet shipyard → new Fleet at planet
   - Ship from fleet yard → added to existing fleet
   - Complex from fleet yard → PlanetaryFacility on planet at fleet's hex
6. Shipyard facilities enable ship construction at that colony
```

---

## Architecture

### Layer Separation

- **Strategy layer:** `ProductionEngine`, `BuildQueueSource`, `PlanetaryFacility`, queue data on Planet/Fleet
- **UI layer:** `BuildQueueScreen` / `EmpireBuildQueueWindow` manage queue display and category filtering
- **Simulation layer:** Component abilities (`ResourceHarvesterAbility`, `SpaceShipyardAbility`)

### Key Design Principles

1. **Unified algorithm** -- one `_process_queue_tick_dynamic()` handles all queue types
2. **Parameterized behavior** -- production rate and spawning context vary, not the algorithm
3. **Tick-based production** -- resources consumed dynamically each tick, not turn-counting
4. **Facilities are instances** -- each has a UUID, design_data, and operational status
5. **Parallel construction** -- each shipyard facility has its own queue processed independently
6. **Data holders, not processors** -- Planet, Fleet, and PlanetaryFacility hold queue lists; ProductionEngine processes them

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
    consumable_levels: Dict[str, float] = field(default_factory=dict)
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
    "turns_remaining": 2.5         # Pre-calculated at queue-add time, updated each tick
}
```

`turns_remaining` is pre-calculated when the item is added to the queue using
`estimate_build_turns()` from `build_queue_source.py`, which applies the same
limiting-resource formula as `ProductionEngine`. This ensures the UI shows a
correct estimate immediately, before the first production tick recalculates it.

---

## Production Model (Tick-Based)

**Files:**
- `game/strategy/engine/production_engine.py` -- queue processing and resource consumption
- `game/strategy/engine/production_spawner.py` -- entity spawning on completion
- `game/strategy/engine/production_math.py` -- shared limiting-resource formula

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
5. **Check affordability** -- `planet.has_stockpile(cost_this_step)` for planet construction, `fleet.has_cargo_resources()` for fleet construction.
6. **Consume resources** -- deduct from local stockpile (planet) or cargo (fleet), add to `resources_consumed`.
7. **Check completion** -- if all `resources_consumed >= total_cost`, spawn the item.
8. **Carry-over** -- remaining tick capacity continues to next queue item (mid-tick completion).

Items can complete mid-turn when their full resource cost is consumed. Multiple items can complete in a single turn if the first finishes early.

### Production Rates

Production rates are per-turn (divided by 100 for per-tick). Rates come from `BuildQueueSource`:
- `"planetary_yard"` -- default rate for base colony queue, scaled by PlanetaryYard component's `simple_size_mount` modifier
- Per-facility rates for shipyard queues, scaled by SpaceShipyard component's `simple_size_mount` modifier
- `"fleet_space_yard"` -- rate for fleet construction, multiplied by yard count

**Size mount scaling:** Production rates are multiplied by the `simple_size_mount` modifier value on the yard component. A planetary yard at size 0.2 produces at 20% of the base rate (e.g., 400/resource/turn instead of 2000). Resolution is handled by `modifier_resolver.resolve_size_multiplier()` in `game/strategy/services/modifier_resolver.py`.

### Constants

| Constant | Value | Defined In | Purpose |
|----------|-------|------------|---------|
| `TICKS_PER_TURN` | 100 | `turn_engine.py` (imported by ProductionEngine) | Ticks per game turn |
| `TICK_CAPACITY_EPSILON` | 0.0001 | `production_engine.py` | Minimum tick capacity to continue |
| `COMPLETION_EPSILON` | 0.001 | `production_engine.py` | Float tolerance for completion check |
| `MAX_QUEUE_ITERATIONS` | 10 | `production_engine.py` | Safety limit per tick |

---

## Spawning

**File:** `game/strategy/engine/production_spawner.py`

PROJ-233: Spawning logic is in `ProductionSpawner`, a separate class from `ProductionEngine`. `ProductionEngine._complete_item()` delegates to `ProductionSpawner.spawn_completed_item()`, which dispatches based on item type and build context:

| Item Type | Build Context | Spawner Method | Result |
|-----------|---------------|----------------|--------|
| Complex | Planet base queue | `_create_and_place_facility()` | `PlanetaryFacility` on planet |
| Ship/Satellite | Planet shipyard | `_spawn_ship()` | New `Fleet` at planet |
| Fighter | Planet shipyard | `_spawn_to_staging_yard()` | Planet staging yard |
| Drop Pod | Planet base queue | `_spawn_to_staging_yard()` | Planet staging yard |

**Staging yard transfer:** Players transfer pods from staging yard to ships via the Transfer dialog (T key). Pods are discrete `carried_items`, not bulk cargo.
| Ship/Satellite | Fleet yard | `_spawn_fleet_ship()` | Added to existing fleet |
| Complex | Fleet yard | `_spawn_fleet_complex()` | `PlanetaryFacility` on planet at fleet's hex |

### Complex Spawning (`_create_and_place_facility` / `_spawn_fleet_complex`)

1. Load design_data from `DesignLibrary(save_path, empire_id)`.
2. Create `PlanetaryFacility` with UUID, design_data, `is_operational=True`.
3. Append to `planet.facilities` (fleet variant finds planet at fleet's hex).
4. Log `COMPLEX_BUILT` event.

### Ship Spawning (`_spawn_ship` / `_spawn_fleet_ship`)

1. Load design_data from `DesignLibrary`.
2. Create `ShipInstance` via `ShipInstance.create()`.
3. Planet variant: create new `Fleet` at planet location, add ship, register via `empire.add_fleet()`.
4. Fleet variant: add ship directly to existing fleet.
5. Log `SHIP_BUILT` event.

### Mass Calculation

Mass is calculated by `calculate_design_stats()` (`game/simulation/entities/ship_design_stats.py`), which uses `Ship.from_dict()` + `recalculate_stats()` as the single source of truth for all ship stats including mass. The production spawner delegates to this function.

---

## Design Validation

`DesignValidator` (`game/strategy/services/design_validator.py`) validates designs before build queue insertion. Checks crew housing, life support, and component existence. Invalid designs are blocked from the build queue.

---

## Planetary Complex Components

Six components restricted to `"Planetary Complex"` vehicle type, defined in `data/components.json`:

| Component | Ability |
|-----------|---------|
| `metal_harvester` | `ResourceHarvesterAbility` (metals) |
| `organic_harvester` | `ResourceHarvesterAbility` (organics) |
| `vapor_harvester` | `ResourceHarvesterAbility` (vapors) |
| `radioactive_harvester` | `ResourceHarvesterAbility` (radioactives) |
| `exotic_harvester` | `ResourceHarvesterAbility` (exotics) |
| `space_shipyard` | `SpaceShipyardAbility` |

**Ability classes:** `game/simulation/components/abilities/harvester.py`

---

## UI

### BuildQueueScreen

**File:** `game/ui/screens/build_queue_screen.py`

Full-screen UI with three panels:
- **Items List** (left) -- available designs filtered by category
- **Build Queue** (center) -- VirtualTable displaying order, item name, turns, per-turn spend, and remaining cost columns (PROJ-221)
- **Filter Panel** (right) -- category buttons (Complexes, Ships, Satellites, Fighters, Drop Pods) plus Add/Remove

Accessed from the strategy screen via the "Build Yard" button on owned planets.

---

## Queue Discovery and Rate Resolution

**File:** `game/strategy/data/build_queue_source.py`

`BuildQueueSource` is a dataclass that abstracts away the origin of a queue (planet base, facility, fleet). The UI and command handlers work with `BuildQueueSource` objects rather than distinguishing entity types directly.

### Key Functions

| Function | Purpose |
|----------|---------|
| `collect_build_queues_at_hex()` | All queue sources at a hex for an empire |
| `collect_all_build_queues_for_empire()` | All queue sources across entire empire |
| `get_production_rate_for_queue(entity, queue_id)` | Rate for a specific queue (used by command handler) |
| `estimate_build_turns(total_cost, rate)` | Limiting-resource turn estimate (single source of truth) |
| `get_default_production_rates(yard_type)` | Load rates from `data/production_rates.json` |

**Note:** `estimate_build_turns()` and `get_production_rate_for_queue()` are the authoritative utilities for turn estimation. The command handler delegates to these — do not duplicate this logic elsewhere.

---

## Key Files

| Component | File |
|-----------|------|
| ProductionEngine | `game/strategy/engine/production_engine.py` |
| ProductionSpawner | `game/strategy/engine/production_spawner.py` |
| Production math (shared formula) | `game/strategy/engine/production_math.py` |
| BuildQueueSource & utilities | `game/strategy/data/build_queue_source.py` |
| PlanetaryFacility | `game/strategy/data/planetary_facility.py` |
| Planet (facilities list) | `game/strategy/data/planet.py` |
| Fleet (construction_queue) | `game/strategy/data/fleet.py` |
| Command handlers | `game/strategy/engine/command_handlers.py` |
| BuildQueueScreen | `game/ui/screens/build_queue_screen.py` |
| EmpireBuildQueueWindow | `game/ui/screens/empire_build_queue_window.py` |
| Harvester abilities | `game/simulation/components/abilities/harvester.py` |
| Component definitions | `data/components.json` |
| Production rates | `data/production_rates.json` |
| DesignLibrary | `game/strategy/systems/design_library.py` |
| Design cost calculator | `game/strategy/services/design_cost_calculator.py` |
