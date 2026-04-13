# Starship Battles - Architecture Reference

Primary architecture document for the Starship Battles codebase. All claims verified against source code.

---

## Layer Structure

Six layers with strict downward-only dependency flow:

```
┌──────────────────────────────────────────────────────────────┐
│  UI Layer          game/ui/, game/app.py                     │
│  Pygame screens, panels, widgets, rendering                  │
├──────────────────────────────────────────────────────────────┤
│  AI Layer          game/ai/                                  │
│  Ship combat AI: behaviors, targeting, strategy              │
├──────────────────────────────────────────────────────────────┤
│  Strategy Layer    game/strategy/                             │
│  Galaxy, empires, fleets, turns, economy, generation         │
├──────────────────────────────────────────────────────────────┤
│  Research Layer    game/research/                             │
│  Stochastic tech tree, fuzzy requirements, leaky buckets     │
├──────────────────────────────────────────────────────────────┤
│  Simulation Layer  game/simulation/                           │
│  Combat simulation: ships, components, weapons, battles      │
├──────────────────────────────────────────────────────────────┤
│  Engine Layer      game/engine/                               │
│  Low-level physics, collision detection, spatial indexing     │
├──────────────────────────────────────────────────────────────┤
│  Core Layer        game/core/                                 │
│  Math, config, constants, registry, protocols, validation    │
└──────────────────────────────────────────────────────────────┘
```

### Dependency Rules

| Layer      | Allowed Dependencies                        |
|------------|---------------------------------------------|
| UI         | AI, Strategy, Simulation, Engine, Core      |
| AI         | Simulation, Engine, Core                    |
| Strategy   | Simulation, Core                            |
| Research   | Core only                                   |
| Simulation | Engine, Core                                |
| Engine     | Core                                        |
| Core       | Standard library only                       |

### Forbidden Dependencies

- Core must not import any game layer
- Simulation must not import Strategy, AI, or UI
- Strategy must not import UI
- Engine must not import Simulation, Strategy, AI, or UI

---

## Package Directory Map

### `game/context.py` -- DI Container (outside layer hierarchy)

| Module                | Description |
|-----------------------|-------------|
| `context.py`          | ApplicationContext DI container. `create_production()` and `create_test()`. Manages all 9 services. |

### `game/core/` -- Foundation layer, no game-layer dependencies

| Module                | Description |
|-----------------------|-------------|
| `math.py`             | Vector2, clamp, lerp, angle_diff |
| `hex_math.py`         | HexCoord axial coordinate system for galaxy map |
| `combat_types.py`     | DamageContext frozen dataclass (attacker identity DTO) |
| `config.py`           | DisplayConfig, AIConfig, PhysicsConfig, BattleTuning |
| `constants.py`        | GameState, LayerType, AttackType, LayerDefaults, CombatConstants |
| `protocols.py`        | All cross-layer Protocol definitions (see Protocols section) |
| `registry.py`         | GameRegistries container, RegistryManager (via ApplicationContext), DI providers |
| `exceptions.py`       | GameException hierarchy (10 exception classes) |
| `error_codes.py`      | ErrorCode enum |
| `event_logging.py`    | log_event, set_event_handler, get_event_handler |
| `formula_evaluator.py`| FormulaEvaluator, FormulaContext, AST-based formula evaluation |
| `validation.py`       | ValidationResult, IValidationRule |
| `paths.py`            | Paths constants for file locations |
| `resources.py`        | ResourceCatalog (unified resource definitions), ResourceDefinition |
| `input_actions.py`    | InputAction enum for key bindings |
| `json_utils.py`       | JSON serialization helpers |
| `singleton.py`        | SingletonMeta metaclass (deprecated — no production users, kept for reference) |
| `profiling.py`        | Profiler, profile_action for performance |
| `string_utils.py`     | String utility functions |
| `validation_helpers.py`| Validation helper utilities |
| `patterns/`           | `layer_iterator.py` -- generic layer iteration pattern |

### `game/engine/` -- Low-level physics and spatial systems

| Module          | Description |
|-----------------|-------------|
| `physics.py`    | PhysicsBody base class (position, velocity, angle, mass, forward_vector). Property container -- subclasses implement own physics. |
| `collision.py`  | CollisionSystem (hit detection, raycasting, ramming) |
| `spatial.py`    | SpatialGrid hash grid for efficient proximity queries |

### `game/simulation/` -- Combat simulation engine

| Subpackage       | Description |
|------------------|-------------|
| `entities/`      | Ship (main entity, 10 delegates), ShipComponentManager, ShipCombatManager, ShipLayerManager, ShipResourceManager, ShipSerializer, ShipPhysics, ShipCombatEngine, LayerData, Projectile, AbilityAggregator, ShipLoader, ShipStats, ShipStatQuerier |
| `components/`    | Component class (facade), create_component factory, 4 delegates (ModifierManager, AbilityManager, ComponentHealthManager, ComponentResourceManager), ComponentStatsCalculator (static) |
| `components/abilities/` | Ability classes: weapons (beam, seeker, projectile), defense, propulsion, cargo, crew, resources, harvester, colonize, superweapons |
| `systems/`       | BattleEngine (tick loop), BattleEndConditions, ResourceState, ResourceRegistry, TechPresetLoader |
| `services/`      | BattleService (high-level API), RegistryLoader, ModifierService, DesignLoader, VehicleDesignService |
| `combat/`        | DamageCalculator, TargetingSystem, WeaponFiringSystem, BoundaryRegion (PROJ-269), FormationResolver (PROJ-269), ModifierStack (PROJ-269), TelemetryLevel + aggregators (PROJ-269) |
| `managers/`      | BattleStateManager, RetreatManager |
| `interfaces/`    | Simulation-internal protocols: IAIController, IAbility, IWeaponAbility, IComponent, ICombatShip, etc. |
| `validation/`    | ShipDesignValidator |
| (root modules)  | BattleState, BattleTuning, BattleConfig (visual-mode operational options), BattleController (visual-mode wrapper only), BattleSpec / BattleOutcome (PROJ-269), battle_runner.run_battle (PROJ-269 unified entry), formula_system.py (re-export shim → game.core.formula_evaluator), ProjectileManager |

### `game/strategy/` -- 4X strategy layer

| Subpackage      | Description |
|-----------------|-------------|
| `data/`         | Domain entities (notable modules): Fleet, ShipInstance, Empire, Galaxy, Planet, Stars, Storm, Pathfinding, plus fleet delegates (`fleet_battle_adapter.py`, `fleet_capability_calculator.py`, `fleet_consumable_aggregator.py`), ShipInstance delegates (`ship_instance_bridge.py`, `ship_instance_serializer.py`, `ship_consumable_manager.py`, `ship_cargo_manager.py`, `ship_display_formatter.py`), fleet hierarchy (`fleet_hierarchy.py` [BattleRole, CombatPolicy, FleetHierarchyNode], `task_force.py`, `squadron.py`, `design_role.py` [DesignRole enum, DesignRoleRegistry — loads 28 roles from `data/design_roles.json` with vehicle type filtering], `group_policy_registry.py`), and data-driven configs (`classification_config.py`, `resource_generation_config.py`, `star_generation_config.py`, `orbital_generation_config.py`) |
| `engine/`       | Turn processing: TurnEngine, GameSession, GameConfig, GameInitializer, Commands, CommandHandlers, OrderProcessor, TurnStateSnapshot, plus sub-engines (movement, conflict, harvesting, production + ProductionSpawner, population, economy, resupply, action execution, planet action execution, planet energy, environmental hazards), and shared utilities (`production_math.py`, `construction_forecast.py`). **Error model (PROJ-251):** Sub-engines validate preconditions via `_validate_tick_inputs()`. `_time_phase()` wraps failures in `EnginePhaseError`. `process_turn()` captures pre-turn snapshot and rolls back on failure. |
| `services/`     | FleetSpeedCalculator, FleetNavigationService, ComponentInspector (includes `has_warp_capability`, `get_ability_list`), DesignCostCalculator, DesignValidator, CargoTransferService, AreaEffectManager, ActionTimeResolver, FleetCargoProjector, ModifierResolver, StrategicAbilityScanner, DeploymentZoneCalculator, TaskGroupSuggester |
| `facade/`       | StrategySessionFacade (UI-to-engine communication) |
| `facade/dto/`   | Read-only DTOs: FleetInfo (+ `carried_items_summary`, `pod_storage_capacity`, `pod_storage_used`), SystemInfo, PlanetInfo (+ `staging_yard_summary`), EmpireInfo, TaskForceInfo, SquadronInfo, ShipInfoExtended (fleet hierarchy DTOs) |
| `interfaces/`   | IBattleResolver, BattleResult (strategy-layer battle DTO) |
| `adapters/`     | SimulationBattleResolver (IBattleResolver implementation) |
| `generation/`   | Galaxy generation: density maps, planet gen, star placement, storm gen |
| `events/`       | EventLog, EventTypes for strategy-layer event tracking |
| `formulas/`     | Habitability formulas |
| `validation/`   | ColonizeValidator, SuperweaponValidator, TransferValidator, PlanetOrderValidator |
| `systems/`      | DesignLibrary (design filtering including `design_role`), RaceLibrary, RaceRandomizer, SaveGameService |

### `game/ai/` -- Combat AI

| Module               | Description |
|----------------------|-------------|
| `controller.py`      | AIController -- main decision loop per ship. `update()` decomposed into `_acquire_targets()`, `_select_behavior()`, `_execute_behavior()` stages. |
| `behaviors.py`       | 11 behavior classes (Kite, AttackRun, Ram, Flee, Orbit, StationaryFire, DoNothing, StraightLine, RotateOnly, Erratic + base AIBehavior) |
| `spatial_behaviors/`  | Spatial positioning system: BattleLine, Column, Screen, Escort, PatrolZone, FreeManeuver. Replaces old ShipFormation. |
| `group_target_coordinator.py` | GroupTargetCoordinator -- focus fire, reserve commitment, flagship succession |
| `policy_manager.py`  | PolicyManager -- loads and provides lookup for targeting and movement policies |
| `target_evaluator.py`| TargetEvaluator -- scores and prioritizes targets |
| `ai_factory.py`      | AIControllerFactory -- creates controllers (moved from simulation layer) |
| `combat_utils.py`    | Shared AI combat utility functions |
| `protocols.py`       | AI-specific protocol definitions |
| `interfaces/`        | AI interface definitions |

### `game/research/` -- Tech tree system

| Subpackage     | Description |
|----------------|-------------|
| `data/`        | TechNode, TechTree data structures, ResearchTracker |
| `systems/`     | ResearchService (fuzzy requirements, leaky bucket mechanics) |

### `game/ui/` -- Pygame rendering and screens

| Subpackage       | Description |
|------------------|-------------|
| `screens/`       | BattleScreen, StrategyScreen, WorkshopScreen, MenuScene, FleetBattleSetupScreen (aliased as BattleSetupScreen), NewGameSetupScreen, TestLabScreen, GalaxyTestScreen, BuildQueueScreen, BattleSetupState/BattleSetupSide (setup data model), plus sub-screen packages (`builder/`, `test_lab/`, `galaxy_test/`) |
| `renderer/`      | Camera, GameRenderer, SpriteManager |
| `panels/`        | BattlePanels, BuilderWidgets |
| `components/`    | Reusable UI components including `table/` subpackage |
| `widgets/`       | PanelFactory, ScrollableJsonPanel, UIElementRegistry |
| `services/`      | BattleFactories, InputMapper, ShipFactory, ShipIO, ComponentService, ValidationService |
| `orchestration/` | (Package retained for future UI orchestration; `BattleOrchestrator` removed — `AIControllerFactory` is the canonical AI creation path) |
| `research/`      | Research/tech tree UI visualization |
| `interfaces/`    | UI-layer interface definitions |
| `utils/`         | UI utility functions |
| `config.py`      | UIConfig (moved from core in PROJ-113) |
| `colors.py`      | Color constants |
| `fonts.py`       | Font configuration |

---

## Package Public APIs

Exports defined in each package's `__init__.py` via `__all__`.

### `game.core` (42 exports)

- **Exceptions:** GameException, StateException, FrozenStateException, ValidationException, ResourceException, MissingResourceException, PersistenceException, SimulationException, ComponentException, FormulaException
- **Error Codes:** ErrorCode
- **Math:** Vector2, clamp, lerp, angle_diff
- **Registry/DI:** GameRegistries, RegistryManager, DefaultRegistryProvider, TestRegistryProvider, get_default_registry_provider
- **Constants:** GameState, LayerType, AttackType, LayerDefaults, CombatConstants
- **Resources:** ResourceCatalog, ResourceDefinition
- **Event Logging:** log_event, set_event_handler, get_event_handler
- **Validation:** ValidationResult, IValidationRule
- **Configuration:** DisplayConfig, AIConfig, PhysicsConfig, BattleTuning
- **Paths:** Paths
- **Protocols:** IRegistryProvider, IFleet, IPlanet, ICombatant, is_fleet, is_planet, is_combatant

### `game.engine` (3 exports)

PhysicsBody, CollisionSystem, SpatialGrid

### `game.simulation` (34 exports)

Existing: Ship, ShipSerializer, Component, create_component, BattleEngine, BattleLogger, IEndCondition, TeamEliminatedCondition, TickLimitCondition, end_condition_from_dict, BattleService, BattleServiceResult, BattleState, ShipDesignValidator.

PROJ-269 BattleSpec DTOs: AIPolicy, BattleSpec, CombatPolicies, ComponentStateSpec, EntryVector, PostBattleHook, ShipSpec, SquadronSpec, TaskForceSpec, TeamSpec.

PROJ-269 BattleOutcome DTOs: BattleOutcome, EndReason, HitRecord, ModifierApplication, ShipOutcome, ShipStats, ShipStatus, TaskForceOutcome, TeamOutcome, WeaponSummary.

PROJ-269 entry: `game.simulation.battle_runner.run_battle(spec, ai_factory, ship_builder, ...) -> BattleOutcome`.

### `game.strategy` (16 exports)

Fleet, ShipInstance, OrderType, Order, HexCoord, TurnEngine, GameSession, GameConfig, StrategySessionFacade, FleetInfo, SystemInfo, PlanetInfo, EmpireInfo, IBattleResolver, BattleResult

### `game.ai` (12 exports)

AIController, AIBehavior, KiteBehavior, AttackRunBehavior, RamBehavior, FleeBehavior, OrbitBehavior, StationaryFireBehavior, DoNothingBehavior, PolicyManager, TargetEvaluator, AIControllerFactory

### `game.ui` (7 module exports)

Eagerly imports submodules to prevent pytest-xdist race conditions: sprites, camera, game_renderer, battle_screen, battle_ui, battle_panels, builder_widgets. WorkshopScreen is excluded due to Tkinter side effects.

### `game.research`

No public API exports (sandbox/experimental system). Contains TechNode, TechTree, ResearchService internally.

---

## Key Protocols

All defined in `game/core/protocols.py`. Uses `@runtime_checkable` Protocol classes with TypeGuard functions for duck typing.

### Cross-Layer Boundary Protocols

**IPostBattleShip** -- Strategy-Simulation boundary for post-battle state transfer:
- `name: str` -- ship name for identification
- `hp: int` -- current hull points
- `max_hp: int` -- maximum hull points
- `is_alive: bool` -- operational status
- `is_derelict: bool` -- destroyed but present on battlefield
- `layers: Dict[LayerType, Any]` -- ship layers containing components
- `resources: Optional[IResourceReader]` -- resource registry or None

**IResourceReader** -- Read-only resource access:
- `get_value(name) -> float`
- `get_max_value(name) -> float`
- `get_resource_names() -> List[str]`

**IRegistryProvider** -- Dependency injection for registry access:
- `get_components() -> Dict`
- `get_modifiers() -> Dict`
- `get_vehicle_classes() -> Dict`
- `get_resources() -> Dict`

**ICamera** -- Camera abstraction for research layer visualization:
- `width`, `height`, `zoom`, `position`
- `world_to_screen()`, `screen_to_world()`, `update()`, `update_input()`

**IScene** -- Game scene protocol (menu, battle, workshop, etc.):
- `handle_event(event)`, `update(dt)`, `draw(screen)`, `handle_resize(width, height)`

### Strategy Entity Protocols

| Protocol      | Distinguishing Properties | TypeGuard |
|---------------|---------------------------|-----------|
| IFleet        | ships, orders, location, owner_id, capabilities, resources, battle | is_fleet |
| IPlanet       | planet_type, deposits, stockpile, max_stockpile, owner_id, populations, facilities, atmosphere, energy, energy_capacity | is_planet |
| IOrderable    | orders, get_current_order(), add_order(), pop_order(), clear_orders() | — |
| IStarSystem   | stars, planets, warp_points, global_location, storms | is_star_system |
| IEmpire       | id, name, color, colonies, fleets, resource_pool (read-only aggregate) | is_empire |
| IStorm        | storm_type, effects, occupied_hexes | is_storm |
| IWarpPoint    | destination_id, location | is_warp_point |
| IZoneOccupant | occupied_hexes (FrozenSet) | is_zone_occupant |
| IShipInstance | design_id, design_data, hull_class, cargo_contents, carried_items | is_ship_instance |
| IFacility     | instance_id, design_id, design_data, is_operational | is_facility |

### Combat Protocols

| Protocol    | Key Properties | TypeGuard |
|-------------|----------------|-----------|
| ICombatant  | team_id, is_alive, position | is_combatant |
| IDamageable | current_hp, max_hp, is_derelict | -- |
| ICombatShip | team_id, hp, max_hp, is_derelict, layers, resources, total_defense_score | is_combat_ship |

### Simulation-Internal Protocols (`game/simulation/interfaces/`)

Ability: IAbility, IWeaponAbility, IBeamWeaponAbility, ISeekerWeaponAbility, IProjectileWeaponAbility, IResourceConsumptionAbility, IResourceStorageAbility, IResourceGenerationAbility, IWarpJumpAbility. Entity: ICombatShip, IProjectile, IPhysicsShip, ISerializableShip. Component: IComponent. Each has a corresponding `is_*` TypeGuard function.

---

## Cross-Layer Communication

### 1. Protocols (Primary Mechanism)

Layers communicate through Protocol definitions in `game/core/protocols.py`. Upper layers depend on protocol interfaces, not concrete classes. Example: Strategy layer uses `IPostBattleShip` to read post-battle ship state without importing `game.simulation.entities.ship.Ship`.

### 2. Dependency Injection

**Registry DI:** Services accept `IRegistryProvider` instead of accessing `RegistryManager` directly. Production uses `DefaultRegistryProvider`; tests use `TestRegistryProvider`. All services are managed by `ApplicationContext` (`game/context.py`).

**AI Factory DI:** `BattleService.create_battle()` accepts an optional `IAIControllerFactory` injected from higher layers (UI/strategy), because AI depends on Simulation (not vice versa).

### 3. Interface Contracts

**IBattleResolver** (`game/strategy/interfaces/battle_resolver.py`): Abstract base class that decouples strategy from simulation. `SimulationBattleResolver` (`game/strategy/adapters/`) is the production implementation.

### 4. Facade Pattern

**StrategySessionFacade** (`game/strategy/facade/`): Single entry point for UI-to-strategy communication. Returns read-only DTOs (FleetInfo, SystemInfo, PlanetInfo, EmpireInfo) to prevent UI from mutating strategy state.

### 5. Late Imports

Intentional late imports exist at specific cross-layer boundaries:
- `Ship.add_component()` imports ModifierService (real import cycle)
- `ShipInstanceBridge.to_ship()` imports ShipSerializer (cross-layer boundary)
- `ShipInstance.get_calculated_stats()` imports `calculate_design_stats` (lazy init)
- `Fleet.trigger_speed_recalculation()` imports FleetSpeedCalculator (edge operation)

---

## Data Flow

### JSON to Gameplay

```
data/*.json  (project root)
       │
       ▼
RegistryLoader (game/simulation/services/registry_loader.py)
  loads: components.json, modifiers.json, vehicleclasses.json, resources.json
       │
       ▼
RegistryManager (game/core/registry.py, managed by ApplicationContext)
  holds GameRegistries(components, modifiers, vehicle_classes, resources, resource_catalog)
       │
       ▼
IRegistryProvider (injected into services)
       │
       ├──► Component / create_component()  (game/simulation/components/)
       ├──► Ship / ShipSerializer           (game/simulation/entities/)
       ├──► calculate_design_stats          (game/simulation/entities/ship_design_stats.py)
       └──► VehicleDesignService            (game/simulation/services/)
```

### Battle Flow (post-PROJ-269 unified path)

```
caller (Combat Lab / Battle Setup / Strategy IBattleResolver)
       │
       ▼
context-specific spec compiler (build_*_battle_spec)
       │  emits a BattleSpec frozen DTO
       ▼
run_battle(spec, ai_factory, ship_builder, ...)   (game/simulation/battle_runner.py)
       │  - constructs BattleEngine directly (no BattleController)
       │  - threads spec.boundary + spec.modifier_stack onto the engine
       │  - calls engine.start_teams(teams_by_id, seed, end_condition)
       │  - drives the tick loop until is_battle_over()
       │  - attaches telemetry aggregators per spec.telemetry_level
       ▼
BattleEngine.tick()  (game/simulation/systems/battle_engine.py)
       │  runs: AI decisions → weapon firing → damage calc → physics → end checks
       ▼
extract_outcome(engine, spec) → BattleOutcome
       │  per-team / per-ship / per-component results
       ▼
spec.post_battle_hook(outcome)  (optional)
       │  Strategy attaches `apply_outcome_to_fleets` — writes
       │  ShipOutcome.components back into ShipInstance.components
       │  and prunes destroyed/retreated ships from fleets.
```

**Visual mode (Combat Lab UI, Battle Setup screen):** uses
`BattleController` as a thin per-frame tick-loop driver around
`BattleEngine`. Construction goes through the spec compiler +
`materialize_spec_ships(spec, ship_builder)` + `controller.add_ships`
+ `controller.start()`. PROJ-269 Phase 6 deleted the `BattleMode` /
`BattleModeHandler` / `create_*_battle` factory machinery; the
controller is now config-flag-driven only.

**PROJ-270 Phase 4:** `BattleController` now also accepts the compiled
spec via `controller.set_spec(spec)` and — once `is_battle_over()`
first returns True — calls `extract_outcome(engine, spec)` to produce a
`BattleOutcome` via `controller.get_outcome()`. Visual-mode battles
therefore honour the same "every battle emits a `BattleOutcome`"
contract that headless callers already satisfied.

### Strategy Turn Flow

```
UI (StrategyScreen)
       │
       ▼
StrategySessionFacade (game/strategy/facade/)
       │  UI-to-engine communication
       ▼
GameSession (game/strategy/engine/game_session.py)
       │  manages game state, delegates to TurnEngine
       ▼
TurnEngine.process_turn() (game/strategy/engine/turn_engine.py)
       │  runs 100 sub-ticks, each executing phases in order:
       │  Phase 0:    HarvestingEngine (1/100th per tick, deposits to planet.stockpile)
       │  Phase 0b:   ConsumableManagementEngine (per-turn consumption)
       │  Phase 0c:   ResupplyEngine (fuel generation at facilities)
       │  Phase 0c1:  PlanetEnergyEngine (energy generation/consumption)
       │  Phase 0d:   ResupplyEngine (fleet resupply from facilities)
       │  Phase 0e:   ProductionEngine (construction from local stockpile/fleet cargo)
       │  Phase 0f:   EnvironmentalHazardEngine (storm damage, fuel drain)
       │  Phase 1:    OrderProcessor (instant orders)
       │  Phase 1.5:  ActionExecutionEngine (COLONIZE, TRANSFER, superweapons)
       │  Phase 1.6:  PlanetActionEngine (shield activation, etc.)
       │  Phase 2:    FleetMovementEngine (calculate moves)
       │  Phase 3:    FleetMovementEngine (apply moves)
       │  Phase 4:    ConflictResolutionEngine (triggers IBattleResolver)
       │  After tick loop: PopulationEngine
       ▼
Updated Galaxy/Empire/Fleet state
       │
       ▼
StrategySessionFacade returns DTOs to UI
```

---

## Configuration Reference

### DisplayConfig (`game/core/config.py`)

| Constant        | Value     | Usage |
|-----------------|-----------|-------|
| DEFAULT_WIDTH   | 3840      | 4K resolution (game window) |
| DEFAULT_HEIGHT  | 2160      | 4K resolution (game window) |
| WINDOWED_WIDTH  | 2560      | Windowed mode |
| WINDOWED_HEIGHT | 1600      | Windowed mode |
| TEST_WIDTH      | 1440      | Test/headless resolution |
| TEST_HEIGHT     | 900       | Test/headless resolution |

### PhysicsConfig (`game/core/config.py`)

TICK_RATE=0.01s, DEFAULT_LINEAR_DRAG=0.5, DEFAULT_ANGULAR_DRAG=0.5, SPATIAL_GRID_CELL_SIZE=2000.

---

## Entry Point

`game/app.py` -- Pygame application loop. Initializes registries, creates scenes (implementing `IScene` protocol), and runs the main event/update/draw loop. Scene transitions are managed by the app, not by scenes themselves. Key screens: MenuScene, BattleScreen, StrategyScreen, WorkshopScreen (DesignWorkshopScreen), FleetBattleSetupScreen (fleet-based battle setup with multi-fleet support, task force/squadron hierarchy, and complex effects — aliased as BattleSetupScreen), TestLabScreen, NewGameSetupScreen, KeybindingsScene.
