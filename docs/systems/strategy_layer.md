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

**PROJ-254 Performance:** `_get_planet_by_id()` uses a lazy-built index dict.
`get_all_stars()` caches results per turn. These avoid O(n) scans on every call.

DTO types (defined in `game/strategy/facade/dto/` package, with submodules `fleet_dto.py`, `system_dto.py`, `planet_dto.py`, `empire_dto.py`, re-exported via `__init__.py`):
- `FleetInfo` -- fleet state snapshot (includes `carried_items_summary`, `pod_storage_capacity`, `pod_storage_used`)
- `FleetSummary` -- lightweight fleet overview
- `StarInfo` -- star data with system context (PROJ-231)
- `SystemInfo` -- star system data
- `PlanetInfo` -- planet details (includes `staging_yard_summary`; `shield_active` is now populated from `active_abilities['PlanetaryShield']`)
- `EmpireInfo` -- empire state
- `ColonySummary` -- colony overview
- `FleetOrderInfo` -- order display data (type, target, progress)
- `ShipInfo` -- ship instance summary for fleet display
- `WarpPointInfo` -- warp point data (destination, location)

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
| `IssueColonizeCommand` | `ColonizeCommandHandler` | Direct colonize (deploy pod, claim planet) |
| `QueueColonizeMissionCommand` | `ColonizeMissionCommandHandler` | Chain: MOVE + COLONIZE (population/cargo transferred via explicit TRANSFER orders) |
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
| `IssuePlanetOrderCommand` | `IssuePlanetOrderCommandHandler` | Issue planet action order (shield, stabilizer) |
| `ClearPlanetOrdersCommand` | `ClearPlanetOrdersCommandHandler` | Clear planet orders |
| `DeletePlanetOrderCommand` | `DeletePlanetOrderCommandHandler` | Remove specific planet order |
| `SetAtmosphereTargetCommand` | `SetAtmosphereTargetCommandHandler` | Set atmosphere modification target for planet |
| Superweapon commands (11 total) | `superweapon_command_handlers.py` | Implode planet, stellerate star, warp points, dyson sphere, self-destruct |

### Shared Helpers

- `add_move_order_if_needed(session, fleet, target_hex, start_hex?)` -- chain-aware MOVE queuing

---

## 3. Turn Engine

**File:** `game/strategy/engine/turn_engine.py`

### Overview

TurnEngine is a lightweight orchestrator that delegates to 13 specialized sub-engines.
All sub-engines are dependency-injected: `registries` is a **required** keyword-only parameter (no default), while other engine parameters are optional with lazy defaults.

`process_turn(empires, galaxy, save_path)` runs one full turn:
1. **100-tick subturn loop** -- each tick runs all phases below
2. **Population growth** -- runs once after the loop

### Per-Tick Phase Execution Order

| Phase | Engine | Description |
|-------|--------|-------------|
| 0 | `HarvestingEngine` | Planetary resource extraction to planet.stockpile (1/100th per tick). Also aggregates `StagingYard` capacity per colony into `colony.max_staging_mass`. |
| 0b | `ConsumableManagementEngine` | Per-turn resource consumption (1/100th per tick) |
| 0c | `ResupplyEngine` | Fuel generation at facilities |
| 0c1 | `PlanetEnergyEngine` | Planet energy generation, consumption, auto-deactivation. **PROJ-253:** Caches facility scan results per planet (fingerprint-based invalidation). |
| 0d | `ResupplyEngine` | Fleet resupply from facilities |
| 0e | `ProductionEngine` | Construction from local stockpile/fleet cargo + mid-turn completion |
| 0f | `EnvironmentalHazardEngine` | Storm damage, fuel drain |
| 1 | `OrderProcessor` | Instant orders (JOIN_FLEET) |
| 1.5 | `ActionExecutionEngine` | Action orders (COLONIZE, TRANSFER, superweapons) |
| 1.6 | `PlanetActionEngine` | Planet action orders (shield activation, etc.) — all consecutive planet action orders dispatch instantly on the same tick |
| 2 | `FleetMovementEngine` | Calculate paths/next moves |
| 3 | `FleetMovementEngine` | Apply all movements simultaneously |
| 4 | `ConflictResolutionEngine` | Combat detection and resolution |

After the 100-tick loop:
- `PopulationEngine.process_population_growth(empires)`
- `QualityEngine.process_quality_improvement(empires)` — planetary quality improvement
- `AtmosphereEngine.process_atmosphere(empires)` — atmosphere modification toward targets

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
| `IPlanetEnergyEngine` | `PlanetEnergyEngine` |
| `IPlanetActionEngine` | `PlanetActionEngine` |
| `IComponentActivationEngine` | `ComponentActivationEngine` |

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
- `ships: List[ShipInstance]` -- canonical flat list of all ships
- `orders: List[FleetOrder]`, `path: List[HexCoord]`
- `speed: float` -- minimum of all combat-capable ships' speeds
- `construction_queue: List[Dict]` -- for fleets with space yards

Fleet hierarchy (organizational overlay for combat behavior):
- `task_forces: List[TaskForce]` -- task forces containing squadrons
- `fleet_policy: CombatPolicy` -- fleet-level combat policy defaults
- `get_unassigned_ships()` -- ships not in any task force

The hierarchy is a **3-level tree**: Fleet → TaskForce → Squadron → Ships.
Task forces and squadrons reference ships from `fleet.ships` by `instance_id`.
Ships can exist at any level (lone ships in a task force, or unassigned at
fleet level). Each level can set independent policies for targeting, movement,
and retreat. Unset policies inherit from the parent level.

See `game/strategy/data/fleet_hierarchy.py` (BattleRole, CombatPolicy,
FleetHierarchyNode), `game/strategy/data/task_force.py`, and
`game/strategy/data/squadron.py`.

### Design Roles

**Data file:** `data/design_roles.json`
**Registry:** `game/strategy/data/design_role.py` — `DesignRoleRegistry`
**Enum (legacy):** `game/strategy/data/design_role.py` — `DesignRole`

Design roles are classification labels assigned to vehicle designs. They
drive auto-suggestion for fleet organization and UI grouping but have no
direct combat behavior effect. The player assigns a role in the Design
Workshop via a dropdown.

**28 roles** defined in `data/design_roles.json`, each with:
- `id` �� string identifier (e.g., `"line_combatant"`)
- `name` — display name (e.g., `"Line Combatant"`)
- `description` — tooltip text
- `allowed_vehicle_types` — which vehicle types can use this role (e.g., `["Ship", "Satellite"]`)

Role categories:
- **Ship combat** (6): line_combatant, fleet_escort, interceptor, assault_ship, missile_platform, raider
- **Ship support** (4): carrier, support_ship, scout, command_ship
- **Universal** (4): general_purpose, shield_projector, sensor_platform, stellar_protector
- **Planetary complex** (5): resource_harvester, production_facility, defensive_platform, planetary_modifier, research_facility
- **Specialized** (7): transport, superweapon_platform, megastructure_builder, enrichment_facility, resupply_depot, construction_accelerator, colony_pod, assault_pod

**DesignRoleRegistry** (loaded from JSON):
- `get_roles_for_vehicle_type(type)` — roles allowed for a vehicle type (for dropdown filtering)
- `get_role_name(role_id)` — display name from ID
- `get_role_id_by_name(display_name)` — ID from display name
- `get_all_role_ids()` — all role IDs
- Module-level accessor: `get_default_design_role_registry()`

**Auto-classification** (legacy, still available):
- `classify_design_role(abilities, mass)` — classify from ability set + mass
- `classify_from_design_data(design_data, component_registry)` — classify from full design

**Ship field:** `Ship.design_role: str` — stored in design JSON, defaults to `"general_purpose"`

**ShipInstance fields:**
- `design_role: Optional[str]` — from design data
- `role_override: Optional[str]` — player override per instance
- `effective_role` property — returns override if set, else design_role

**DesignMetadata field:** `design_role: str` — extracted during `from_design_file()`,
used by `DesignSelectorWindow` role filter dropdown.

**UI integration:**
- **Design Workshop** right panel: "Role:" dropdown after "AI:" dropdown, filtered by current vehicle type. Updates when vehicle type changes.
- **Design Selector** (load dialog): "Design Role:" filter dropdown in sidebar. Defaults to "All Roles", filters design list when a specific role is selected.

All 25 QS starter designs have `design_role` assigned.

### Group Combat Policies

**Data file:** `data/group_policies.json`
**Registry:** `game/strategy/data/group_policy_registry.py`

Group policies define combat behavior for fleet hierarchy nodes. Three
independent axes, each with preset IDs:

**Targeting** (7 presets): `focus_strongest`, `focus_nearest`, `focus_weakest`,
`distributed`, `anti_fighter`, `anti_capital`, `opportunistic`.
Focus modes coordinate group fire on one target; distributed lets ships
pick independently.

**Movement** (7 presets): `advance`, `hold_range`, `hold_position`, `pursue`,
`hit_and_run`, `ram`, `evasive`. Each maps to a per-ship movement policy
from `movement_policies.json`.

**Retreat** (7 presets): `group_25`, `group_50`, `individual_15`, `individual_30`,
`flagship_lost`, `ammo_depleted`, `never`. Group mode triggers when
aggregate HP drops; individual mode uses per-ship thresholds.

`GroupPolicyRegistry.validate_policy(combat_policy)` returns error messages
for invalid preset IDs.

### Spatial Behaviors

**Package:** `game/ai/spatial_behaviors/`

Spatial behaviors define how ships position relative to an anchor (ship,
group centroid, or zone). Each behavior computes a target position; the
AI controller navigates the ship there.

| Behavior | Type | Description |
|----------|------|-------------|
| `FreeManeuverBehavior` | Loose | No spatial constraints |
| `BattleLineBehavior` | Rigid | Line/wedge/echelon perpendicular to leader facing |
| `ColumnBehavior` | Rigid | Single file behind leader |
| `ScreenBehavior` | Loose | Orbit around anchor point at radius |
| `EscortBehavior` | Loose | Stay near anchor ship |
| `PatrolZoneBehavior` | Loose | Cover a circular zone |

Factory: `create_spatial_behavior(type_str, **kwargs)` creates behavior by
type string. Unknown types default to `FreeManeuverBehavior`.

### Deployment Zones

**File:** `game/strategy/services/deployment_zone_calculator.py`

Maps `BattleRole` to positions on the 100000x100000 battlefield.
Team 0 deploys on the left, Team 1 mirrors on the right.

| Role | Team 0 X | Y Offset | Purpose |
|------|----------|----------|---------|
| RESERVE | 10000 | 0 | Held back |
| MAIN_BODY | 25000 | 0 | Primary battle line |
| SCREEN | 35000 | 0 | Between vanguard and main |
| VANGUARD | 42000 | 0 | Forward deployment |
| FLANKER_LEFT | 25000 | -15000 | Wide left envelopment |
| FLANKER_RIGHT | 25000 | +15000 | Wide right envelopment |

- `DeploymentZoneCalculator.get_zone_center(role, team_id)` — zone center as Vector2
- `DeploymentZoneCalculator.compute_positions(count, role, team_id)` — ship positions as (x,y) tuples

### Group Coordination

**File:** `game/ai/group_target_coordinator.py`

Stateless utility for group-level combat decisions:

- `select_focus_target(enemies, priority, reference_position)` — pick one target for focus fire
  - Priorities: `strongest` (mass), `most_damaged` (HP ratio), `nearest` (distance), `largest`
- `compute_group_hp_ratio(ships)` — aggregate HP/maxHP for a group
- `should_commit_reserve(main_body_ships, threshold)` — True when main body HP <= threshold
- `find_flagship_successor(ships, has_cnc_check)` — heaviest alive ship with C&C

### Auto-Suggestion

**File:** `game/strategy/services/task_group_suggester.py`

`suggest_task_groups(ships)` examines `effective_role` on each ship and groups them:

| Role | Suggested Group | Battle Role |
|------|----------------|-------------|
| line_combatant, assault_ship, command_ship | Battle Line | MAIN_BODY |
| fleet_escort, interceptor | Escort Screen | SCREEN |
| raider, scout | Vanguard | VANGUARD |
| carrier, support_ship | Support Group | RESERVE |

Each group gets default targeting and movement policies matching its role.

### Fleet Hierarchy DTOs

**File:** `game/strategy/facade/dto/fleet_hierarchy_dto.py`

Immutable DTOs for UI display of the fleet hierarchy:

- `TaskForceInfo` — name, battle_role, policies, squadrons tuple, ship counts
- `SquadronInfo` — name, battle_role, policies, spatial_behavior, ship count
- `ShipInfoExtended` — extends ShipInfo with `effective_role`

Factory methods: `TaskForceInfo.from_task_force()`, `SquadronInfo.from_squadron()`,
`ShipInfoExtended.from_ship_instance()`.

### Fleet Delegates

Fleet uses composition with 4 delegates:

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

Uses `component_inspector` service for ship-level ability lookups (including
`has_warp_capability()` and `get_ability_list()`).
Requires component registry via DI (constructor or ship's `_registries`).

#### FleetBattleAdapter (`fleet.battle`)

**File:** `game/strategy/data/fleet_battle_adapter.py`

Bridges strategy Fleet with simulation Ship for combat:

- `to_battle_ships(team_id, formation_positions?, registries?)` -- converts
  `ShipInstance` list to simulation `Ship` objects with deployment positions
  (default: Team 0 at x=20000, Team 1 at x=80000, 2000px vertical spacing;
  use `DeploymentZoneCalculator` for hierarchy-aware positioning)
- `update_from_battle_results(surviving_ships)` -- updates fleet from
  `IPostBattleShip` protocol; ships not in survivors are removed (destroyed)

#### FleetPursuerTracker (`fleet.pursuer_tracker`)

**File:** `game/strategy/data/fleet_pursuer_tracker.py`

Tracks fleets pursuing this fleet via `MOVE_TO_FLEET`/`JOIN_FLEET` orders (PROJ-222):

- `pursuers` -- read-only `FrozenSet` of all pursuing fleets
- `pursuer_count` -- number of active pursuers
- `add_pursuer(fleet)` / `remove_pursuer(fleet)` -- register/unregister
- `redirect_pursuers(new_target)` -- on merge, redirect all pursuers to new fleet
- `notify_target_destroyed()` -- on destruction, cancel all pursuit orders

Not serialized — rebuilt from order targets on load.

### ShipInstance Stat Calculation

**File:** `game/strategy/data/ship_instance.py`

`ShipInstance.get_calculated_stats()` returns a cached stats dict computed by
`calculate_design_stats()` from `game/simulation/entities/ship_design_stats.py`.
This delegates to `Ship.from_dict()` + `recalculate_stats()` — the simulation
layer is the single source of truth for all stats.

**Stats dict keys:** `max_hp`, `mass`, `resource_storage`, `cargo_storage`,
`pod_storage_mass`, `strategic_movement`, `warp_max_tonnage`, `warp_resource_costs`,
`resource_consumption_per_hex`, `resource_consumption_per_turn`.

**Cache invalidation:** Call `ship.invalidate_stats_cache()` after damage, repair,
or component toggle changes. The next `get_calculated_stats()` call recomputes.

**Component toggles:** Toggled-off components are excluded from the design before
Ship creation, so their stats don't contribute. Component damage is applied to
the Ship's components before recalculation.

**Anti-pattern:** Do NOT compute stats by iterating design components manually —
use `get_calculated_stats()` or `calculate_design_stats()`. See Pattern 3 in
`02_PATTERNS.md` ("Unified Stat Calculation") for details.

### Order System (PROJ-238: Unified)

Order types defined in `game/strategy/data/order_types.py`:
- Movement: `MOVE`, `MOVE_TO_FLEET`, `WARP` (fleet-only)
- Actions: `COLONIZE`, `TRANSFER`, `LOAD_POPULATION`, superweapons (fleet)
- Planet actions: `ACTIVATE_ABILITY`, `DEACTIVATE_ABILITY` (planet; generic ability toggles)
- Fleet: `JOIN_FLEET`, `BUILD`

Both Fleet and Planet implement the `IOrderable` protocol (`game/core/protocols.py`),
providing a unified interface: `orders` list, `get_current_order()`, `add_order()`,
`pop_order()`, `clear_orders()`.

The unified `Order` class (renamed from `FleetOrder` in PROJ-238) and `OrderType`
enum are used by both entity types. Import from `game.strategy.data.order_types`.

**Planet orders** are processed by `PlanetActionEngine` (every tick, no speed concept).
**Fleet orders** are processed by `ActionExecutionEngine` (speed-based tick interval).

### Fleet Position Projection

**File:** `game/strategy/services/cargo_transfer_service.py`

`project_fleet_position(fleet)` walks the fleet's order queue and returns the
hex where the fleet will be after all queued MOVE/WARP orders execute. Returns
`fleet.location` if no movement orders are queued.

Used by:
- `CargoTransferService.resolve_colonies()` — fallback when no colonies at primary hex
  or fleet location; checks projected destination
- `TransferDialog._populate_initial_data()` — finds colonies at projected position
  for transfer orders queued after MOVE orders
- `StrategyRenderer._draw_move_preview()` — draws preview line from projected position
  (handles MOVE→WARP chains, not just the last MOVE target)

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

### Per-Component Activation Architecture

**Source of truth:** `facility.component_states[component_key]` (ComponentActivationState)

Each activatable component on a facility has an independent activation state tracked
by a composite key in format `"LAYER:INDEX:COMP_ID"` (e.g., `"OUTER:0:geologic_stabilizer_sector"`).

**`planet.active_abilities`** is a **derived property** (not a stored field). It scans
all `facility.component_states` for entries with `phase == "active"` and returns a
summary dict `{ability_name: True}`. This means:
- Multiple components with the same ability can be active simultaneously
- No stale state — the property always reflects current component_states
- Not serialized — derived on access from facility.component_states (which IS serialized)

**Component-key flow:**
1. UI identifies `component_key` from `iter_keyed_components(facility.design_data)`
2. `IssuePlanetOrderCommand` carries `component_key` to the handler
3. Handler stores `component_key` in `order.target` dict
4. `PlanetActionEngine._resolve_component_key()` uses it directly (no search needed)
5. `ComponentActivationEngine` ticks the state at `facility.component_states[component_key]`
6. `PlanetEnergyEngine` sums drain rates from all draining component_states entries

**Validator checks at component granularity** when `component_key` is provided —
prevents activating the same component twice, but allows different components with
the same ability name to be activated independently.

**Stabilizer protection requires ACTIVE phase:** `SuperweaponOrderProcessor._is_stabilized()`
passes `require_active=True` to `find_abilities_in_scope()`, which checks
`facility.get_activation_state(comp_key).is_functionally_active` for each component.
A stabilizer that is installed but not activated provides **no protection**. Only the
`ACTIVE` phase counts — `ACTIVATING` and `DEACTIVATING` do not protect.

**UI abilities panel** (`game/ui/screens/planet_abilities_window.py`) shows one row per
activatable component instance (no dedup by ability name). When multiple instances of
the same ability exist, they get numbered labels (e.g., "Geologic Stabilizer (Facility #1)").

The abilities panel also provides **environment editor buttons** at the top for setting
planet modification targets. Buttons are shown conditionally based on facility presence:
- **Atmosphere** — shown when planet has `AtmosphereModifier` facility
- **Gravity** — shown when planet has `GravityModifier` facility
- **Water** — shown when planet has `WaterModifier` facility
- **Radiation** — shown when planet has `RadiationShield` facility

Each button opens the corresponding target editor window. The editors open via a callback
from `strategy_window_manager.py` which delegates to the event router's `_open_*_editor()`
methods. The standalone atmosphere button was removed from the strategy detail panel —
all environment editors are now accessed exclusively through the abilities window.

**Species selector for multi-species planets:** All 4 editors include a dropdown
(from `game/ui/screens/species_selector_mixin.py`) when the planet has multiple species
populations. The dropdown lists species sorted by population count; "Species Ideal"
uses the selected species' preferences from `RaceConfig`. Single-species planets show
no dropdown.

### System Effects Display

**File:** `game/strategy/services/system_effects_collector.py`

`collect_system_effects(system, empire_id, registries)` scans all empire-owned
colonies in a star system for system-scope abilities and returns structured effect
data for UI display.

**Supported ability types:** GeologicStabilizer, StellarStabilizer, WarpFieldStabilizer,
ResourceHarvestBooster, BuildRateBooster, QualityImprovement, ShieldModifier, DamageModifier.

**Scope filter:** The collector accepts abilities with scopes in `_SYSTEM_RELEVANT_SCOPES`:
`system`, `allied_system`, `player_system`, `enemy_system`, `sector`, `allied_sector`,
`player_sector`, `enemy_sector`. Scopes `self`, `fleet`, and `planet` are excluded.

**Two categories:**
- **Activatable** (have activation_time): status from ComponentActivationState
  (Active/Inactive/Activating N/Deactivating N)
- **Passive** (no activation_time): always "Active" when facility is operational

**Aggregation:** Values use two-phase stacking (intra-group MAX, inter-group MULTIPLY)
via `aggregate_multipliers()` from `strategic_ability_scanner.py`.

**UI integration:** `SystemTreePanel._add_system_effects()` renders a collapsible
"System Effects (N)" group after Warp Points and before Planets in the system tree.
Each effect type is a group header with aggregate status and value. Expanding shows
individual provider facilities with their planet location, individual value, and status.

### Atmosphere Modification Pipeline

**Files:**
- `game/strategy/engine/atmosphere_engine.py` -- per-turn atmosphere processing
- `game/strategy/engine/commands.py` -- `SetAtmosphereTargetCommand`
- `game/strategy/engine/planet_command_handlers.py` -- `SetAtmosphereTargetCommandHandler`
- `game/ui/screens/atmosphere_target_editor.py` -- gas slider UI
- `game/strategy/data/planet.py` -- `atmosphere`, `atmosphere_target`, `surface_pressure` fields

Atmosphere modification is a once-per-turn system that gradually changes a planet's
gas composition toward a player-set target. It runs after the 100-tick loop, alongside
population growth and quality improvement.

**Data model:**
- `planet.atmosphere: Dict[str, float]` -- gas formula (e.g., "O2") to partial pressure (Pa)
- `planet.atmosphere_target: Dict[str, float]` -- target partial pressures per gas
- `planet.surface_pressure: float` -- total atmospheric pressure (sum of all partial pressures)

**Command flow:**
1. Player opens Atmosphere Target Editor from planet detail (button shown only if planet has operational `AtmosphereModifier` facility)
2. Editor provides sliders for 10 gases (N2, O2, CO2, H2O, CH4, H2, He, Ar, NH3, SO2), range 0-150 kPa
3. Presets: "Species Ideal" (from race atmosphere preferences), "Match Current", "Clear Target"
4. "Apply" dispatches `SetAtmosphereTargetCommand(planet_id, atmosphere_target)` via facade
5. Handler validates ownership, sets `planet.atmosphere_target` (empty dict clears target)

**Per-turn processing algorithm** (`AtmosphereEngine.process_atmosphere()`):
1. For each empire's colony, check if `atmosphere_target` is set
2. Sum `modification_rate` (kg/turn) from all operational facilities with `AtmosphereModifier`
3. Convert between mass and pressure using planet physics: `Pa_per_kg = gravity / surface_area`
4. Calculate delta (target - current) for each gas, convert to mass
5. Distribute available modification rate proportionally across gases by mass delta
6. Apply changes without overshooting target values
7. Update `surface_pressure` as sum of all partial pressures

**Physics notes:**
- Small planets change atmosphere faster than large planets (less mass per Pa)
- Earth-like planet at default rate (7.8e15 kg/turn): ~150 Pa/turn, ~1000 turns to reach 150 kPa
- Multiple facilities stack additively

**Related:** `AtmosphereModifier` ability in [ability_reference.md](ability_reference.md#atmospheremodifier), race atmosphere preferences in `game/strategy/data/race_config.py` (`GAS_NAME_TO_FORMULA`, `GAS_FORMULA_TO_NAME`).

### Water Modification Pipeline

**File:** `game/strategy/engine/water_engine.py`

Same pattern as AtmosphereEngine but simpler — a single float (`surface_water`) instead of a gas dict. Runs once per turn after the 100-tick loop.

- Target: `planet.water_target` (0.0-1.0, None = no modification)
- Rate: sum of `modification_rate` from operational `WaterModifier` facilities
- Change: moves `surface_water` toward target, clamped to [0.0, 1.0], no overshoot
- Permanent: changes persist even if facility removed

### Planet Modifier Effect Engine

**File:** `game/strategy/engine/planet_modifier_effect_engine.py`

Handles instant-apply/revert for activatable planet modifiers (GravityModifier, RadiationShield). Runs once per tick as Phase 1.8 after ComponentActivationEngine:

- **GravityModifier:** When ACTIVE + `gravity_target` set, stores original in `gravity_original` and overrides `surface_gravity`. Reverts when INACTIVE or facility destroyed.
- **RadiationShield:** When ACTIVE + `radiation_shielding_target` set, applies to `radiation_shielding`. Reverts to 0.0 when INACTIVE or facility destroyed.
- **Habitability:** `score_planet_for_race()` uses `magnetic_field + radiation_shielding` for the radiation factor. Gravity and water read directly from the (possibly modified) planet fields.

### Strategic-to-Combat Bridge

**File:** `game/strategy/services/combat_modifier_collector.py`

Collects strategic combat modifiers (ShieldModifier, DamageModifier, scoped ShieldProjection) for fleets entering combat. Returns `FleetCombatModifiers(shield_mult, damage_mult, flat_shield_bonus)`.

Applied in `SimulationBattleResolver.resolve_battle()` after environmental effects:
1. Flat shield bonus added to `max_shields` and `current_shields`
2. Shield multiplier applied via `_apply_shield_interference()`
3. Damage multiplier set on `ship.damage_output_mult`

All `find_abilities_in_scope()` calls use `require_active=True` — only abilities in the
ACTIVE activation phase contribute to combat modifiers. Inactive or activating abilities
have no effect. This means planetary complex ShieldModifier/DamageModifier/ShieldProjection
must be manually activated before they affect combat.

Wired from `ConflictResolutionEngine._resolve_combat_simulated()` which collects modifiers for both fleets and passes them to the resolver.

### Activatable Abilities & Stabilizer Pattern

**Files:**
- `game/strategy/engine/component_activation_engine.py` -- tick-based activation state machine
- `game/strategy/engine/planet_energy_engine.py` -- energy drain for active abilities
- `game/strategy/services/strategic_ability_scanner.py` -- scope-based ability discovery
- `game/strategy/engine/superweapon_order_processor.py` -- stabilizer protection checks
- `game/ui/screens/planet_abilities_window.py` -- activation toggle UI

Some strategic abilities require manual activation, consume energy while active, and
take multiple ticks to transition between states. These share a common architecture.

**Activation state machine** (`ComponentActivationEngine`):

```
INACTIVE --[activate order]--> ACTIVATING --[N ticks]--> ACTIVE
ACTIVE   --[deactivate order]--> DEACTIVATING --[N ticks]--> INACTIVE
```

- State tracked per component instance in `facility.component_states[component_key]`
- `component_key` format: `"LAYER:INDEX:COMP_ID"` (e.g., `"CORE:0:stellar_stabilizer"`)
- Each tick, `ComponentActivationEngine` increments `progress_ticks` for ACTIVATING/DEACTIVATING components
- Transition to ACTIVE/INACTIVE when `progress_ticks >= required_ticks`
- ACTIVATING and DEACTIVATING phases provide **no protection** -- only ACTIVE counts

**Energy system integration:**
- `PlanetEnergyEngine` sums `energy_drain_rate / 100` per tick from all ACTIVE draining components
- If energy depletes, active abilities auto-deactivate
- Energy generation comes from `StrategicResourceGeneration` abilities, storage from `ResourceStorage`

**Current activatable abilities:**

| Ability | Blocks | Default Scope | Activation | Deactivation | Energy Drain |
|---------|--------|---------------|------------|--------------|--------------|
| `PlanetaryShield` | Planet bombardment | system | varies | varies | varies |
| `GeologicStabilizer` | IMPLODE_PLANET | planet/sector/system | varies | varies | varies |
| `StellarStabilizer` | STELLERATE_STAR, CREATE_DYSON_SPHERE | system | 250 ticks | 150 ticks | 250/turn |
| `WarpFieldStabilizer` | OPEN_WARP_POINT, CLOSE_WARP_POINT | system | 250 ticks | 150 ticks | 150/turn |
| `GravityModifier` | — (modifies planet gravity) | self | 15 ticks | 5 ticks | 30/turn |
| `RadiationShield` | — (adds radiation shielding) | self | 15 ticks | 5 ticks | 20/turn |
| `ShieldModifier` | — (modifies fleet shields in combat) | varies | 15-25 ticks | 5-10 ticks | 30-50/turn |
| `DamageModifier` | — (modifies fleet damage in combat) | varies | 15-25 ticks | 5-10 ticks | 30-50/turn |
| `ShieldProjection` | — (adds flat shields in combat) | varies | 15-25 ticks | 5-10 ticks | 30-50/turn |

The list of activatable ability keys is maintained in `planet_energy_engine.py:_ACTIVATABLE_ABILITIES`.

**Stabilizer protection pattern:**

All three stabilizers (Geologic, Stellar, WarpField) use a unified check in
`SuperweaponOrderProcessor._is_stabilized(ability_name, scopes, reference_entity, galaxy, empires)`:

1. Superweapon order targets a location (planet/system)
2. Processor calls the appropriate `_is_system_*_stabilized()` wrapper
3. Wrapper finds a reference planet at the target location
4. `_is_stabilized()` delegates to `find_abilities_in_scope()` from `strategic_ability_scanner.py`
5. Scanner checks all empire colonies in scope for ACTIVE instances of the ability
6. If any active instance found, superweapon order is cancelled with a protection message

**Scope resolution** (`strategic_ability_scanner.py`):
- `find_abilities_in_scope()` accepts `require_active=True` to filter to ACTIVE phase only
- SYSTEM scope: all empire-owned planets in the star system
- SECTOR scope: all planets in the same hex
- Returns ability data dicts with scope metadata for aggregation

**Adding a new activatable ability:**
1. Define ability class in `planetary.py` with `energy_drain_rate`, `activation_time`, `deactivation_time`, `scope` parameters
2. Register in `ABILITY_REGISTRY` (`abilities/__init__.py`)
3. Add to `_ACTIVATABLE_ABILITIES` list in `planet_energy_engine.py`
4. Add display name to `TOGGLEABLE_ABILITIES` dict in `planet_abilities_window.py`
5. Add display name to `_ACTIVATABLE_DISPLAY_NAMES` in `strategy_detail_fmt.py`
6. If it blocks superweapons: add check method in `superweapon_order_processor.py` using `_is_stabilized()`
7. Add to `SYSTEM_EFFECT_ABILITIES` in `system_effects_collector.py` if system/sector scope — the collector accepts scopes in `_SYSTEM_RELEVANT_SCOPES` (system*, sector*, planet)
8. If it affects combat: add to `combat_modifier_collector.py` with `require_active=True`
9. Add keyboard toggle binding in `strategy_fleet_command_router.py`
10. Create component in `components.json` with `energy_drain_rate`, `activation_time`, `deactivation_time` in the ability data — these are required for the abilities window to show the ability
11. Create QS complex design in `data/designs/` with `design_role` field
12. Write tests in `tests/unit/simulation/components/abilities/` and `tests/unit/strategy/engine/`
13. Update `docs/systems/ability_reference.md` and `docs/systems/strategy_layer.md` activatable abilities table

### Build Queue Source DI

**File:** `game/strategy/data/build_queue_source.py`

Functions that collect build queue sources accept an optional `registries` parameter
(GameRegistries) threaded via DI from callers. This replaces the former pattern of
calling `get_default_registry_provider()` internally with an adapter shim.

```python
collect_build_queues_at_hex(hex_coord, galaxy, empire, registries=None)
collect_all_build_queues_for_empire(empire, registries=None)
_collect_planet_sources(planet, sources, galaxy, empire, registries=None)
```

Callers pass `session.registries`:
- `BuildQueueScreen` passes `self.session.registries`
- `EmpireBuildQueueWindow` passes `session.registries`
- `StrategyDetailFormatter` passes `self.scene.session.registries`

`colony_has_planetary_yard(colony, registries)` requires `GameRegistries` for
registry-based ability lookup (design JSONs don't store abilities inline).

### Strategy UI Widget Architecture

**File:** `game/ui/screens/strategy_ui.py`

`StrategyUI` stores the `StrategyWidgets` dataclass directly and delegates attribute
access via `__getattr__`. This eliminates manual button unpacking — new buttons added
to `StrategyWidgets` are automatically accessible on `StrategyUI` without code changes.

```python
self._widgets = widgets  # StrategyWidgets dataclass from create_strategy_panels()

def __getattr__(self, name):
    widgets = self.__dict__.get('_widgets')
    if widgets is not None and hasattr(widgets, name):
        return getattr(widgets, name)
    raise AttributeError(...)
```

`StrategyDetailFormatter` uses the same pattern — accepts `StrategyWidgets` directly
and delegates lookups via `__getattr__` instead of a manually-curated widget dict.

---

## 5. Event System

**Files:**
- `game/strategy/events/event_types.py` -- enums
- `game/strategy/events/event_log.py` -- Event dataclass + EventLog collection

### EventType Enum

```
SHIP_BUILT, COMPLEX_BUILT, COLONY_FOUNDED, COMBAT_RESOLVED,
PLANET_DESTROYED, STAR_DESTROYED, WARP_POINT_OPENED, WARP_POINT_CLOSED,
DYSON_SPHERE_CREATED, SHIPS_SELF_DESTRUCTED, RESOURCE_SHORTAGE,
FLEET_JOINED, FLEET_JOIN_REDIRECTED, FLEET_JOIN_CANCELLED,
SHIELD_ACTIVATED, SHIELD_DEACTIVATED, SHIELD_AUTO_DEACTIVATED
```

### EventCategory Enum

```
PRODUCTION, COLONIES, COMBAT, SUPERWEAPONS, FLEET_OPERATIONS, PLANET_OPERATIONS, ALL
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

**Shield events** (SHIELD_ACTIVATED, SHIELD_DEACTIVATED, SHIELD_AUTO_DEACTIVATED) are
generated by `PlanetActionEngine` (activation/deactivation) and `PlanetEnergyEngine`
(auto-deactivation on energy depletion). Both engines accept an `event_bus` parameter
wired by `TurnEngine`'s lazy init.

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
