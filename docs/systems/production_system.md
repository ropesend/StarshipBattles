# Production System

> **Last verified:** 2026-04-27 — FEAT-17: per-yard `construction_queue_paused` flag; gate added at the top of `process_construction_tick`; `BuildQueueSource.is_paused` propagation skips paused yards in Treasury + Planet-detail forecasts.

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

### Per-Yard Pause Flag (FEAT-17)

Each of the three yard types carries an independent `construction_queue_paused: bool` flag on its owning entity:

| Yard | Owner | Flag location |
|------|-------|---------------|
| Planetary yard (base queue) | `Planet` | `Planet.construction_queue_paused` |
| Shipyard facility queue | `PlanetaryFacility` | `PlanetaryFacility.construction_queue_paused` |
| Fleet space-yard queue | `Fleet` | `Fleet.construction_queue_paused` |

`process_construction_tick` checks this flag at each of its three iteration sites and skips ticking that queue when paused — no resource draw, no `resources_consumed` increment, no shortage logging. The queue list itself is unaffected: add/remove/reorder still work via the construction-queue commands. The currently-progressing item retains its `resources_consumed` while paused; unpausing resumes from that saved progress on the next tick.

Toggle is dispatched via `SetBuildQueuePausedCommand` (entity_id + entity_type + paused + optional facility queue_id) routed through the standard command pipeline. The handler resolves the queue *owner* via `BaseCommandHandler._resolve_queue_owner` (sibling to `_resolve_queue`) and flips the flag.

Forecast helpers — `EmpireEconomyCalculator._aggregate_construction_expenses` (Treasury) and `PlanetEconomyProjector._project_yard_drain` (Planet detail "Yard" row) — also skip paused queues so the forecasted drain matches what the engine will actually consume next turn. The skip is at the iteration site; `forecast_queue_turn_spend` itself remains a pure function of (queue, build_rate). Propagation to those helpers happens via `BuildQueueSource.is_paused`, populated by `_collect_planet_sources` / `_collect_fleet_sources` from the owning entity at collection time.

AI controllers do not toggle pause — the flag is player-driven; defaults to `False` everywhere.

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

Full-screen UI with a multi-column refactored layout designed for high-density information and filtering:

- **Left Column (600px width):**
    - **Context Report:** Planet details (population, production rates, complexes) or fleet info (top).
    - **Categories & Roles Filter Panel:** Scrollable vertical lists for category filtering (Ships, Complexes, etc.) and design role filtering (Any, Line Combatant, etc.).
    - **Build Yards Selector:** Scrollable list of available build yards at the current location (Planetary Yard, Shipyards, etc.) to switch between active queues.
- **Available Designs (580px width):**
    - Scrollable list of designs filtered by the selected category and role.
    - Each design row includes a **"+" button** to instantly add it to the active build queue.
- **Build Queue Panel:**
    - `VirtualTable` displaying the active queue.
    - **Leftmost Controls:** Each row includes **"+" / "-"** buttons to adjust quantity and **"Up" / "Down"** arrows for immediate reordering. The original "Actions" column has been removed in favor of these integrated controls.
    - Display columns: Order, Item Name, Turns, Per-turn spend, and Remaining cost.
- **Design Report (Far Right):**
    - Detailed breakdown of stats, abilities, and costs for the selected design.

Accessed from the strategy screen via the "Build Yard" button on owned planets or the keyboard shortcut. All columns support vertical scrollbars via `UIScrollingContainer` when content exceeds visible bounds.

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
| `forecast_queue_turn_spend(queue, build_rate)` (`game/strategy/engine/construction_forecast.py`) | Per-item per-turn resource spend for a queue. The canonical "actual draw" function — mirrors `ProductionEngine._calculate_tick_expenditure × 100`. Consumed by `EmpireEconomyCalculator._aggregate_construction_expenses` (Treasury) and `PlanetEconomyProjector._project_yard_drain` (Planet detail "Yard" row). |

**Note:** `estimate_build_turns()` and `get_production_rate_for_queue()` are the authoritative utilities for turn estimation. The command handler delegates to these — do not duplicate this logic elsewhere. For "what will this queue actually consume next turn?" use `forecast_queue_turn_spend` — both Treasury and Planet detail UI flow through it (BUG-120 fix 2026-04-27 unified Planet detail onto this helper after years of summing yard capacity instead).

**FEAT-17:** `BuildQueueSource.is_paused` is populated by `_collect_planet_sources` / `_collect_fleet_sources` from the owner's `construction_queue_paused`. Read this on the source rather than reaching back through `owner_entity` — the source is the consumer-facing contract.

---

## Habitability Multiplier (PROJ-285)

A colony's harvest AND production rates scale with how livable the planet is for its resident species. Hostile worlds produce slowly; ideal worlds produce at full rate.

> **PROJ-290 UI hooks:** the Empire Treasury shows aggregated populace upkeep as a dedicated "Population Upkeep" expense row (hidden on fresh game); the planet detail panel shows a 0-100 habitability score per resident species when the selected planet is uncolonized. Both surfaces share PROJ-286's `EconomyConfig.population_consumption` + PROJ-288's `PlanetEconomyProjector` as their source data. See [strategy_layer.md § Treasury & Planet Detail UI Integration (PROJ-290)](strategy_layer.md#treasury--planet-detail-ui-integration-proj-290).

### Formula

```
effective_rate = base_rate * booster_mult * habitability_mult
```

`habitability_mult` comes from `planet_habitability_multiplier(planet, race_registry)` in `game/strategy/formulas/colony_output.py` — a **population-weighted mean** of `score_planet_for_race(planet, race_config)` across every species on the colony:

```
mult = Σ (pop.count * score_planet_for_race(planet, race_for(pop))) / Σ pop.count
```

Larger species count proportionally more. If a colony is 70% Species-A (habitability 1.0) and 30% Species-B (habitability 0.2), the multiplier is `0.7 * 1.0 + 0.3 * 0.2 = 0.76`.

### Edge cases

| Situation | Multiplier |
|-----------|-----------|
| Uncolonized planet (no populations) | 1.0 (no penalty; automated extractors run at full rate) |
| Every species has `count == 0` | 1.0 (functionally uncolonized) |
| Every species' `race_id` missing from registry | 1.0 (save-drift defence; preserves the empire's economy rather than silently collapsing it) |
| Species with `count == 0` | Excluded from BOTH numerator and denominator |
| Species whose `race_id` isn't in registry | Excluded from BOTH numerator and denominator (NOT scored as 0) |
| Fleet-based production queues | 1.0 (no planet context — fleet yards operate in space) |

### Per-turn caching

Populations only change at turn boundaries (population growth runs after the 100-tick loop). Computing the multiplier once per colony per turn — not once per tick per resource per colony — saves O(species × resources × ticks) CPU. The cache lives on `Planet`:

- `Planet._cached_habitability_multiplier: Optional[float]` (default `None`)
- `Planet._cached_multiplier_turn: int` (default `-1`)
- `Planet.get_cached_habitability_multiplier(race_registry, turn) -> float`

Both fields are `init=False`, `repr=False`, `compare=False`, and NOT emitted by `to_dict`. Post-load planets start with a cold cache and recompute on their first read.

`TurnEngine.process_turn` calls `set_current_turn(session.turn_number)` on both `HarvestingEngine` and `ProductionEngine` at turn start, invalidating the per-turn key for every colony simultaneously.

### Stacking with boosters

Habitability multiplies **alongside** existing `BuildRateBooster` and `ResourceHarvestBooster` aggregation (`aggregate_multipliers` in `game/strategy/services/strategic_ability_scanner.py`). The three factors multiply:

```
final = base_rate * booster_mult(stacked) * habitability_mult
```

No change to the booster aggregation logic itself.

### Backward compatibility

Both engines default `race_registry=None` — legacy callers (and 850+ lines of MagicMock-based pre-PROJ-285 tests) take this path and get multiplier=1.0, preserving the pre-PROJ-285 formula byte-for-byte. Habitability only applies when the engine is explicitly constructed with a race registry and the colony exposes `get_cached_habitability_multiplier`.

### Related files

- `game/strategy/formulas/colony_output.py` — `planet_habitability_multiplier` helper
- `game/strategy/data/planet.py` — per-turn cache + accessor method
- `game/strategy/engine/harvesting_engine.py` — harvest hook via `_get_habitability_mult`
- `game/strategy/engine/production_engine.py` — production hook: scales `production_rate` dict before tick-capacity math
- `game/strategy/engine/turn_engine.py` — calls `set_current_turn(session.turn_number)` at turn start
- `game/strategy/formulas/habitability.py` — underlying `score_planet_for_race` (PROJ-283, registry-driven via `FACTOR_REGISTRY`)

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
