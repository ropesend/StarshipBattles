# Strategy Layer System

System documentation for the turn-based strategy layer.

---

## 1. StrategySessionFacade

**File:** `game/strategy/facade/strategy_session_facade.py`

CQRS-lite pattern: the single point of access for all UI-to-engine communication.
The UI layer never accesses `GameSession` internals directly.

### Write Path (Commands)

All state mutations go through `handle_command(command) -> ValidationResult`.
The facade delegates to `GameSession.handle_command()`, which dispatches
to the `CommandHandlerRegistry`.

`process_turn()` advances the game by one turn (delegates to `GameSession.process_turn()`).

### Read Path (Queries)

All queries return **immutable DTOs**, never domain objects.

DTO types (defined in `game/strategy/facade/dto/` package, with submodules `fleet_dto.py`, `system_dto.py`, `planet_dto.py`, `empire_dto.py`, re-exported via `__init__.py`):
- `FleetInfo` -- fleet state snapshot
- `FleetSummary` -- lightweight fleet overview
- `StarInfo` -- star data with system context (PROJ-231)
- `SystemInfo` -- star system data
- `PlanetInfo` -- planet details
- `EmpireInfo` -- empire state
- `ColonySummary` -- colony overview

Each DTO has a `from_<domain_object>()` class method for conversion.

### Query Categories

| Category | Methods |
|----------|---------|
| Fleet | `get_fleet()`, `get_fleets_at_hex()`, `get_fleet_path_preview()`, `get_fleet_path_projection()` |
| System | `get_all_systems()`, `get_all_stars()`, `get_system_at_hex()`, `get_system_near_hex()`, `get_system_containing_fleet()` |
| Planet | `get_planet()`, `get_planets_at_hex()` |
| Empire | `get_all_empires()`, `get_empire()`, `get_empire_colonies()`, `get_empire_fleets()` |
| Game State | `get_turn_number()`, `get_human_player_ids()`, `get_save_path()` |
| Events | `get_turn_events()`, `get_all_events()`, `get_events_by_category()` |
| Validation | `can_colonize()`, `can_move_to()`, `get_fleet_remaining_pods()` |
| Environment | `get_storm_names_at_hex()` |

---

## 2. Command Dispatch

**File:** `game/strategy/engine/command_handlers.py`

### Architecture

```
UI -> StrategySessionFacade.handle_command(cmd)
       -> GameSession.handle_command(cmd)
           -> CommandHandlerRegistry.dispatch(cmd_name, session, cmd)
               -> ICommandHandler.execute(session, cmd) -> ValidationResult
```

### ICommandHandler Protocol

```python
class ICommandHandler(Protocol):
    def execute(self, session: GameSession, command: Command) -> ValidationResult: ...
```

### BaseCommandHandler

Mixin providing resolution helpers used by all handlers:
- `_resolve_fleet(session, fleet_id, empire_id?)` -- returns `(Fleet, None)` or `(None, ValidationResult)`
- `_resolve_fleet_required(session, fleet_id, empire_id?)` -- returns Fleet or raises ValueError
- `_resolve_planet(session, planet_id)` -- returns `(Planet, None)` or `(None, ValidationResult)`
- `_resolve_planet_optional(session, planet_id, required?)` -- returns Planet or None/raises

### CommandHandlerRegistry

Registry pattern with `register(command_name, handler)` and `dispatch(command_name, session, cmd)`.

Factory: `create_default_registry()` registers all handlers.

### Registered Handlers

| Command | Handler | Purpose |
|---------|---------|---------|
| `IssueMoveCommand` | `MoveCommandHandler` | Queue MOVE order with pathfinding |
| `IssueColonizeCommand` | `ColonizeCommandHandler` | Direct colonize with auto-load population |
| `QueueColonizeMissionCommand` | `ColonizeMissionCommandHandler` | Chain: LOAD_POPULATION + MOVE + COLONIZE |
| `IssueInterceptCommand` | `InterceptCommandHandler` | MOVE_TO_FLEET order |
| `IssueJoinFleetCommand` | `JoinCommandHandler` | MOVE_TO_FLEET + JOIN_FLEET |
| `IssueTransferCommand` | `TransferCommandHandler` | Cargo transfer with auto-MOVE |
| `IssueWarpCommand` | `WarpCommandHandler` | Warp transit with auto-MOVE to warp point |
| `ClearFleetOrdersCommand` | `ClearOrdersCommandHandler` | Clear all orders and path |
| `IssueBuildOrderCommand` | `BuildOrderCommandHandler` | INSERT BUILD order at front |
| `RemoveBuildOrderCommand` | `RemoveBuildOrderCommandHandler` | Remove BUILD orders |
| `SplitFleetCommand` | `SplitFleetCommandHandler` | Split ships into new fleet |
| `DeleteFleetOrderCommand` | `DeleteFleetOrderCommandHandler` | Remove specific order by index |
| `ReorderFleetOrderCommand` | `ReorderFleetOrderCommandHandler` | Swap order positions |
| `AddToConstructionQueueCommand` | `AddToConstructionQueueCommandHandler` | Add item to build queue |
| `RemoveFromConstructionQueueCommand` | `RemoveFromConstructionQueueCommandHandler` | Remove queue item |
| `ReorderConstructionQueueCommand` | `ReorderConstructionQueueCommandHandler` | Move queue item |
| Superweapon commands (11 total) | `superweapon_command_handlers.py` | Implode planet, stellerate star, warp points, dyson sphere, self-destruct |

### Shared Helpers

- `add_move_order_if_needed(session, fleet, target_hex, start_hex?)` -- chain-aware MOVE queuing
- `create_auto_load_population_order()` -- LOAD_POPULATION order factory (no params; colony resolved at execution time)

---

## 3. Turn Engine

**File:** `game/strategy/engine/turn_engine.py`

### Overview

TurnEngine is a lightweight orchestrator that delegates to 11 specialized sub-engines.
All sub-engines are dependency-injected: `registries` is a **required** keyword-only parameter (no default), while other engine parameters are optional with lazy defaults.

`process_turn(empires, galaxy, save_path)` runs one full turn:
1. **100-tick subturn loop** -- each tick runs all phases below
2. **Population growth** -- runs once after the loop

### Per-Tick Phase Execution Order

| Phase | Engine | Description |
|-------|--------|-------------|
| 0 | `HarvestingEngine` | Planetary resource extraction to planet.stockpile (1/100th per tick) |
| 0b | `ConsumableManagementEngine` | Per-turn resource consumption (1/100th per tick) |
| 0c | `ResupplyEngine` | Fuel generation at facilities |
| 0c1 | `PlanetEnergyEngine` | Planet energy generation, consumption, auto-deactivation |
| 0d | `ResupplyEngine` | Fleet resupply from facilities |
| 0e | `ProductionEngine` | Construction from local stockpile/fleet cargo + mid-turn completion |
| 0f | `EnvironmentalHazardEngine` | Storm damage, fuel drain |
| 1 | `OrderProcessor` | Instant orders (JOIN_FLEET) |
| 1.5 | `ActionExecutionEngine` | Action orders (COLONIZE, TRANSFER, superweapons) |
| 1.6 | `PlanetActionEngine` | Planet action orders (shield activation, etc.) |
| 2 | `FleetMovementEngine` | Calculate paths/next moves |
| 3 | `FleetMovementEngine` | Apply all movements simultaneously |
| 4 | `ConflictResolutionEngine` | Combat detection and resolution |

After the 100-tick loop:
- `PopulationEngine.process_population_growth(empires)`

### Sub-Engine Interfaces

All sub-engines implement interfaces from `game/strategy/interfaces/engines.py`:

| Interface | Default Implementation |
|-----------|----------------------|
| `IMovementEngine` | `FleetMovementEngine` |
| `IProductionEngine` | `ProductionEngine` |
| `IOrderProcessor` | `OrderProcessor` |
| `IConflictEngine` | `ConflictResolutionEngine` |
| `IConsumableEngine` | `ConsumableManagementEngine` |
| `IPopulationEngine` | `PopulationEngine` |
| `IResupplyEngine` | `ResupplyEngine` |
| `IHarvestingEngine` | `HarvestingEngine` |
| `IActionExecutionEngine` | `ActionExecutionEngine` |
| `IEnvironmentalHazardEngine` | `EnvironmentalHazardEngine` |

### Dependency Injection

```python
# Production code
engine = TurnEngine(registries=registries)

# Test code -- inject mocks for fast, isolated tests
engine = TurnEngine(
    registries=test_registries,
    movement_engine=mock_movement,
    production_engine=mock_production,
    conflict_engine=mock_conflict,
)
```

Factory function: `create_default_turn_engine(registries)` for standard initialization.

### Performance Tracking

TurnEngine accumulates per-phase timing and logs a summary after each turn
at WARNING level for profiling.

---

## 4. Fleet System

**File:** `game/strategy/data/fleet.py`

### Fleet Class

Core state:
- `id`, `owner_id`, `location: HexCoord`
- `ships: List[ShipInstance]` -- full state tracking
- `orders: List[FleetOrder]`, `path: List[HexCoord]`
- `speed: float` -- minimum of all combat-capable ships' speeds
- `construction_queue: List[Dict]` -- for fleets with space yards

### Fleet Delegates

Fleet uses composition with 3 delegates:

#### FleetConsumableAggregator (`fleet.resources`)

**File:** `game/strategy/data/fleet_consumable_aggregator.py`

Handles fleet-wide resource calculations across all combat-capable ships:

- `get_movement_resource_costs()` -- total cost per hex of movement
- `has_resources_for_movement()` -- verify all ships can afford 1 hex
- `consume_movement_resources(hexes)` -- atomic consume (all-or-nothing)
- `get_warp_resource_costs()` / `has_resources_for_warp()` / `consume_warp_resources()`
- `fuel_endurance()` -- minimum hexes before any ship runs dry (-1 = unlimited)
- `warp_jumps_remaining()` -- minimum jumps available (0 = can't warp)
- Cargo: `get_fleet_cargo_capacity()`, `load_cargo_to_fleet()`, `unload_cargo_from_fleet()`

Internal helpers:
- `_accumulate_ship_costs(cost_getter)` -- loop-over-ships accumulation
- `_verify_and_consume_resources(cost_getter, consume, multiplier)` -- atomic verify+consume

#### FleetCapabilityCalculator (`fleet.capabilities`)

**File:** `game/strategy/data/fleet_capability_calculator.py`

Queries about what the fleet can do:

- `has_space_shipyard` / `space_shipyard_count` -- checks for SpaceShipyard ability
- `can_build_type(vehicle_type, galaxy?)` -- ship/fighter/satellite/complex buildability
- `can_use_warp()` -- ALL combat-capable ships must have WarpJump with sufficient tonnage
- `get_warp_limiting_ship()` -- first ship without warp capability
- `has_ability(ability_name)` / `ships_with_ability(ability_name)` -- generic ability checks
- `list_abilities()` -- all unique ability names across fleet

Uses `component_inspector` service for ship-level ability lookups.
Requires component registry via DI (constructor or ship's `_registries`).

#### FleetBattleAdapter (`fleet.battle`)

**File:** `game/strategy/data/fleet_battle_adapter.py`

Bridges strategy Fleet with simulation Ship for combat:

- `to_battle_ships(team_id, formation_positions?, registries?)` -- converts
  `ShipInstance` list to simulation `Ship` objects with formation positions
  (default: Team 0 at x=20000, Team 1 at x=80000, 2000px vertical spacing)
- `update_from_battle_results(surviving_ships)` -- updates fleet from
  `IPostBattleShip` protocol; ships not in survivors are removed (destroyed)

### Order System (PROJ-238: Unified)

Order types defined in `game/strategy/data/order_types.py`:
- Movement: `MOVE`, `MOVE_TO_FLEET`, `WARP` (fleet-only)
- Actions: `COLONIZE`, `TRANSFER`, `LOAD_POPULATION`, superweapons (fleet)
- Planet actions: `ACTIVATE_SHIELD`, `DEACTIVATE_SHIELD` (planet)
- Fleet: `JOIN_FLEET`, `BUILD`

Both Fleet and Planet implement the `IOrderable` protocol (`game/core/protocols.py`),
providing a unified interface: `orders` list, `get_current_order()`, `add_order()`,
`pop_order()`, `clear_orders()`.

The unified `Order` class (renamed from `FleetOrder` in PROJ-238) and `OrderType`
enum are used by both entity types. Import from `game.strategy.data.order_types`.

**Planet orders** are processed by `PlanetActionEngine` (every tick, no speed concept).
**Fleet orders** are processed by `ActionExecutionEngine` (speed-based tick interval).

### Planet Energy System (PROJ-237/238)

**File:** `game/strategy/engine/planet_energy_engine.py`

Each planet tracks an energy pool fed by `StrategicResourceGeneration` abilities
and bounded by `ResourceStorage` abilities (both scanned from facility components
via registry lookup). Active planetary shields consume energy per turn.

**Turn processing (100 ticks per turn):**
1. Recalculate capacity from `ResourceStorage` abilities (per resource type)
2. Recalculate generation from `StrategicResourceGeneration` abilities
3. Generate: `energy += generation_rate / 100`
4. Consume: if shield active, `energy -= drain_rate / 100`
5. Auto-deactivate shield if energy depleted
6. Clamp energy to `[0, capacity]`

**Critical:** Uses `get_default_registry_provider()` for ability lookup on facility
components. See Pattern 3 in `02_PATTERNS.md` for the registry lookup requirement.

---

## 5. Event System

**Files:**
- `game/strategy/events/event_types.py` -- enums
- `game/strategy/events/event_log.py` -- Event dataclass + EventLog collection

### EventType Enum

```
SHIP_BUILT, COMPLEX_BUILT, COLONY_FOUNDED, COMBAT_RESOLVED,
PLANET_DESTROYED, STAR_DESTROYED, WARP_POINT_OPENED, WARP_POINT_CLOSED,
DYSON_SPHERE_CREATED, SHIPS_SELF_DESTRUCTED
```

### EventCategory Enum

```
PRODUCTION, COLONIES, COMBAT, SUPERWEAPONS, FLEET_OPERATIONS, ALL
```

### Event Dataclass

```python
@dataclass
class Event:
    event_type: str       # EventType value
    category: str         # EventCategory value
    turn: int             # Turn number when event occurred
    empire_id: int        # Empire that owns/triggered the event
    message: str          # Human-readable description
    details: Dict[str, Any]  # Structured data specific to event type
```

Serializable via `to_dict()` / `from_dict()`.

### EventLog Collection

- `append(event)` -- add event
- `get_events_for_turn(turn)` -- filter by turn number
- `get_events_by_category(category)` -- filter by category (ALL returns everything)
- `get_all_events()` -- return all events
- Serializable via `to_dict()` / `from_dict()`

Events are created by sub-engines during turn processing and surfaced to the UI
via `StrategySessionFacade.get_turn_events()` (returns dicts, not domain objects).

---

## 6. Galaxy Generation

**Files:**
- `game/strategy/data/galaxy.py` -- `Galaxy`, `StarSystem`, `WarpPoint`
- `game/strategy/data/galaxy_system_generator.py` -- `GalaxySystemGenerator`
- `game/strategy/data/galaxy_warp_generator.py` -- `GalaxyWarpGenerator`
- `game/strategy/generation/placement_strategies.py` -- placement algorithms
- `game/strategy/generation/region_classifier.py` -- arm/cluster classification
- `game/strategy/data/stars.py` -- `StarGenerator`, `Star`, `StarType`, `Spectrum`
- `game/strategy/data/planet_gen.py` -- `PlanetGenerator`
- `game/strategy/generation/storm_generator.py` -- `StormGenerator`
- `game/strategy/data/classification_config.py` -- `ClassificationConfig` (planet classification thresholds)
- `game/strategy/data/resource_generation_config.py` -- `ResourceGenerationConfig` (data-driven resource parameters)
- `game/strategy/data/star_generation_config.py` -- `StarGenerationConfig` (star type weights, mass distribution, companion spacing)
- `game/strategy/data/orbital_generation_config.py` -- `OrbitalGenerationConfig` (orbital placement, moon system, surface flags)
- `game/strategy/generation/loaders/astrophysics_loader.py` -- `AstrophysicsLoader` (loads `data/astrophysics.json`)
- `data/astrophysics.json` -- central data file for all generation parameters

### Galaxy Structure

`Galaxy` uses composition with extracted subsystems:
- `GalaxyEntityRegistry` -- planet/fleet ID lookups
- `GalaxySpatialIndex` -- hex-to-system spatial queries
- `GalaxyWarpGenerator` -- warp point creation
- `GalaxySystemGenerator` -- star system placement

`StarSystem` contains:
- `name`, `global_location: HexCoord`, `region_id: Optional[int]`
- `stars: List[Star]`, `planets: List[Planet]`, `warp_points: List[WarpPoint]`
- `storms: List[Storm]`

### Placement Strategies

**Protocol:** `ISystemPlacementStrategy`
- `sample_location(radius, existing_systems, min_dist, rng, max_attempts, spatial_index)`

**Implementations:**

| Strategy | Algorithm |
|----------|-----------|
| `RandomPlacementStrategy` | Uniform random within hex radius, reject if too close |
| `DensityBasedPlacementStrategy` | Rejection sampling weighted by `DensityMap`; higher density = higher acceptance probability |

Both use `SpatialIndex` for O(1) average-case minimum distance checks.

### Density System

Density maps (`game/strategy/generation/density/density_map.py`) define probability
distributions for system placement. The `DensityBasedPlacementStrategy` evaluates
`density_map.evaluate(q, r)` and accepts candidates probabilistically.

### Region Classifier

**File:** `game/strategy/generation/region_classifier.py`

Classifies star systems into named regions based on layout configuration.

`RegionInfo` dataclass: `region_id`, `region_type` (arm/cluster/core/bar/ring), `name`.

`RegionClassifier(layout_config, galaxy_radius)`:
- `classify(coord) -> int` -- assigns region ID to a hex coordinate
- `regions` -- list of all `RegionInfo`
- `get_region_neighbors()` -- adjacency map for connectivity

Layout detection:
- **Spiral:** Classifies by nearest arm using log-spiral math; core region if within sigma threshold
- **Cluster:** Classifies by nearest cluster center (sigma-weighted distance)
- **Ring/Bar:** Simple region assignment

### Generation Pipeline

1. **System placement** -- `GalaxySystemGenerator` uses `ISystemPlacementStrategy` to place N systems
2. **Star generation** -- `StarGenerator` creates stars per system
3. **Planet generation** -- `PlanetGenerator` creates planets with types, atmospheres, resources
4. **Warp point generation** -- `GalaxyWarpGenerator` connects systems via warp points
5. **Storm generation** -- `StormGenerator` places environmental hazards
6. **Region classification** -- `RegionClassifier` assigns region IDs to systems
7. **Planet images** -- `PlanetImageRegistry` assigns visual assets

### Planet Resource Generation

**Files:**
- `game/strategy/data/planet_gen.py` -- `PlanetGenerator._generate_resources(mass, planet_type)`
- `game/strategy/data/resource_generation_config.py` -- `ResourceGenerationConfig`, `get_resource_generation_config()`
- `data/astrophysics.json` -- `resource_generation` section

Resource generation is fully data-driven via `astrophysics.json`. All parameters are loaded through `ResourceGenerationConfig` (follows the `ClassificationConfig` pattern with `@lru_cache` singleton and hardcoded defaults as fallback).

**Parameters (in `astrophysics.json` → `resource_generation`):**
- `mass_scaling` -- log10(kg) bounds for normalizing planet mass to a 0-1 size_factor
- `quantity` -- `earth_mass_baseline` (default 10M), determinism/randomness weights, minimum floor
- `quality` -- max quality (0-100), determinism/randomness weights, minimum floor
- `planet_type_affinities` -- per-planet-type resource multiplier matrix (e.g., MAGMA: Radioactives×2.5, Organics×0.2)

**Resource generation formula:**
1. Compute `size_factor` from log10(mass) normalized to `[min_log_mass, max_log_mass]`
2. Calibrate so Earth-mass yields `earth_mass_baseline` quantity per resource
3. For each resource: `quantity = (size_factor * determinism + random * randomness) * calibration * affinity`
4. Quality inversely correlates: `quality = (1 - size_factor) * determinism + random * randomness`
5. Both have minimum floors to prevent zero values

**Affinity design:** Moderate specialization (1.5-2.5× favored, 0.3-0.8× reduced). Every planet has some of each resource. Thematic mapping:
- Gas giants (JOVIAN, ICE_GIANT) → high Vapors, low Metals
- Volcanic (MAGMA, CHTHONIAN) → high Metals + Radioactives, low Organics
- Ocean/temperate (PELAGIC, CONTINENTAL) → high Organics
- Cold/exotic (CRYOPLANET, ICE_DWARF) → high Vapors + Exotics

### Star Generation Config

**Files:**
- `game/strategy/data/stars.py` -- `StarGenerator._determine_type_and_radius()`, `_generate_mass()`, `_generate_random_stars()`
- `game/strategy/data/star_generation_config.py` -- `StarGenerationConfig`, `get_star_generation_config()`
- `data/astrophysics.json` -- `star_generation` section

Star generation parameters are data-driven via `astrophysics.json`. Follows the same `@lru_cache` singleton + hardcoded defaults pattern as `ClassificationConfig`.

**Parameters (in `astrophysics.json` → `star_generation`):**
- `type_weights` -- probability weights for star type selection (8 types, sum to ~1.0)
- `mass_generation` -- log-normal distribution parameters (sigma, min/max mass, max attempts)
- `system_probabilities` -- multi-star system count thresholds, age generation range
- `companion_spacing` -- companion star hex placement (ring multiplier, jitter, collision limit)

Stefan-Boltzmann types (RED_GIANT, BROWN_DWARF, WHITE_DWARF) share a common luminosity formula and are parameterized in `DEFAULT_STEFAN_BOLTZMANN_TYPES` with per-type mass adjustment, radius, temperature range, and fixed color.

### Orbital Generation Config

**Files:**
- `game/strategy/data/planet_gen.py` -- `PlanetGenerator._generate_orbital_slots()`, `_calculate_moon_chance()`, `_generate_surface_flags()`
- `game/strategy/data/orbital_generation_config.py` -- `OrbitalGenerationConfig`, `get_orbital_generation_config()`
- `data/astrophysics.json` -- `orbital_generation` section

Orbital generation parameters are data-driven via `astrophysics.json`. Follows the same pattern as `ClassificationConfig` and `StarGenerationConfig`.

**Parameters (in `astrophysics.json` → `orbital_generation`):**
- `orbital` -- safe start offset, max orbital distance, planet count range, triangular distribution mode, hot Jupiter forcing parameters
- `mass_generation` -- log-normal mu/sigma per bias type (small, large, default), max iterations
- `moon_system` -- mass threshold log-interpolation (Jupiter/Earth/Ceres breakpoints and chances), moon mass ratio bounds, max moons per body
- `surface` -- tectonic activity and magnetic field ranges per body mass class, water temperature thresholds
