# Production System

This document describes the unified construction/production system: build queues, tick-based resource consumption, turn estimation, and item spawning. The same `ProductionEngine` algorithm handles all build contexts — planet base queues (complexes), planet shipyard facility queues (ships), and fleet space yard queues (ships and complexes).

---

## Overview

Players design items in the Workshop (ships, complexes, satellites, fighters), queue them for construction via the Build Queue UI, and `ProductionEngine` consumes resources per tick (100 ticks/turn) until completion. The system is context-agnostic: one algorithm processes all queue types with parameterized production rates and context-specific spawning.

### Build Contexts

| Context | Queue Source | Can Build | Production Rate |
|---------|-------------|-----------|-----------------|
| Planet base queue | `planet.construction_queue` | Complexes only | `planetary_yard` (2000/resource/turn) |
| Planet shipyard facility | `facility.construction_queue` | Ships + complexes | Per-facility rate (default 3000, with bonus) |
| Fleet space yard | `fleet.construction_queue` | Ships + complexes | `fleet_space_yard` × yard count |

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
    "turns_remaining": 2.5         # Pre-calculated at queue-add time, updated each tick
}
```

`turns_remaining` is pre-calculated when the item is added to the queue using
`estimate_build_turns()` from `build_queue_source.py`, which applies the same
limiting-resource formula as `ProductionEngine`. This ensures the UI shows a
correct estimate immediately, before the first production tick recalculates it.

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

| Constant | Value | Defined In | Purpose |
|----------|-------|------------|---------|
| `TICKS_PER_TURN` | 100 | `turn_engine.py` (imported by ProductionEngine) | Ticks per game turn |
| `TICK_CAPACITY_EPSILON` | 0.0001 | `production_engine.py` | Minimum tick capacity to continue |
| `COMPLETION_EPSILON` | 0.001 | `production_engine.py` | Float tolerance for completion check |
| `MAX_QUEUE_ITERATIONS` | 10 | `production_engine.py` | Safety limit per tick |

---

## Spawning

`_complete_item()` dispatches to the appropriate spawner based on item type and build context:

| Item Type | Build Context | Spawner | Result |
|-----------|---------------|---------|--------|
| Complex | Planet base queue | `_spawn_complex()` | `PlanetaryFacility` on planet |
| Ship/Fighter/Satellite | Planet shipyard | `_spawn_ship()` | New `Fleet` at planet |
| Ship/Fighter/Satellite | Fleet yard | `_spawn_fleet_ship()` | Added to existing fleet |
| Complex | Fleet yard | `_spawn_fleet_complex()` | `PlanetaryFacility` on planet at fleet's hex |

### Complex Spawning (`_spawn_complex` / `_spawn_fleet_complex`)

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

---

## Planetary Complex Components

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
- **Build Queue** (center) -- VirtualTable displaying order, item name, turns, per-turn spend, and remaining cost columns (PROJ-221)
- **Filter Panel** (right) -- category buttons (Complexes, Ships, Satellites, Fighters) plus Add/Remove

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
