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

### `game/core/` -- Foundation layer, no game-layer dependencies

| Module                | Description |
|-----------------------|-------------|
| `math.py`             | Vector2, clamp, lerp, angle_diff |
| `hex_math.py`         | HexCoord axial coordinate system for galaxy map |
| `config.py`           | DisplayConfig, AIConfig, PhysicsConfig, BattleConfig |
| `constants.py`        | GameState, LayerType, AttackType, LayerDefaults, CombatConstants, PLANET_RESOURCES |
| `protocols.py`        | All cross-layer Protocol definitions (see Protocols section) |
| `registry.py`         | GameRegistries container, RegistryManager singleton, DI providers |
| `exceptions.py`       | GameException hierarchy (10 exception classes) |
| `error_codes.py`      | ErrorCode enum |
| `event_logging.py`    | log_event, set_event_handler, get_event_handler |
| `validation.py`       | ValidationResult, IValidationRule |
| `paths.py`            | Paths constants for file locations |
| `resources.py`        | Resource data loading from JSON |
| `input_actions.py`    | InputAction enum for key bindings |
| `json_utils.py`       | JSON serialization helpers |
| `singleton.py`        | SingletonMeta metaclass |
| `profiling.py`        | Profiler, profile_action for performance |
| `strategy_metadata.py`| Strategy-layer metadata types |
| `validation_helpers.py`| Validation helper utilities |
| `patterns/`           | `layer_iterator.py` -- generic layer iteration pattern |

### `game/engine/` -- Low-level physics and spatial systems

| Module          | Description |
|-----------------|-------------|
| `physics.py`    | PhysicsBody base class (position, velocity, rotation, drag) |
| `collision.py`  | CollisionSystem (hit detection, raycasting, ramming) |
| `spatial.py`    | SpatialGrid hash grid for efficient proximity queries |

### `game/simulation/` -- Combat simulation engine

| Subpackage       | Description |
|------------------|-------------|
| `entities/`      | Ship (main entity), ShipSerializer, ShipPhysics, ShipCombatEngine, ShipFormation, LayerData, Projectile, AbilityAggregator, ShipLoader, ShipStats, ShipStatQuerier |
| `components/`    | Component class, create_component factory, modifier system, ability manager, stats calculator |
| `components/abilities/` | Ability classes: weapons (beam, seeker, projectile), defense, propulsion, cargo, crew, resources, harvester, colonize, superweapons |
| `systems/`       | BattleEngine (tick loop), BattleEndConditions, ResourceState, ResourceRegistry, TechPresetLoader |
| `services/`      | BattleService (high-level API), RegistryLoader, ModifierService, DesignLoader, VehicleDesignService |
| `combat/`        | DamageCalculator, TargetingSystem, WeaponFiringSystem, BattleModeHandler |
| `managers/`      | BattleStateManager, RetreatManager |
| `interfaces/`    | Simulation-internal protocols: IAIController, IAbility, IWeaponAbility, IComponent, ICombatShip, etc. |
| `validation/`    | ShipDesignValidator |
| (root modules)  | BattleState, BattleConfig/BattleMode, BattleController, FormulaSystem, ProjectileManager |

### `game/strategy/` -- 4X strategy layer

| Subpackage      | Description |
|-----------------|-------------|
| `data/`         | Domain entities (notable modules): Fleet, ShipInstance, Empire, Galaxy, Planet, Stars, Storm, Pathfinding, plus fleet delegates (`fleet_battle_adapter.py`, `fleet_capability_calculator.py`, `fleet_resource_aggregator.py`) |
| `engine/`       | Turn processing: TurnEngine, GameSession, GameConfig, GameInitializer, Commands, CommandHandlers, FleetOrderProcessor, plus sub-engines (movement, conflict, harvesting, production, population, economy, maintenance, resupply, action execution, environmental hazards) |
| `services/`     | ShipStatsCalculator, FleetSpeedCalculator, FleetNavigationService, ComponentInspector, DesignCostCalculator, CargoTransferService, AreaEffectManager, ActionTimeResolver, FleetCargoProjector |
| `facade/`       | StrategySessionFacade (UI-to-engine communication) |
| `facade/dto/`   | Read-only DTOs: FleetInfo, SystemInfo, PlanetInfo, EmpireInfo |
| `interfaces/`   | IBattleResolver, BattleResult (strategy-layer battle DTO) |
| `adapters/`     | SimulationBattleResolver (IBattleResolver implementation) |
| `generation/`   | Galaxy generation: density maps, planet gen, star placement, storm gen |
| `events/`       | EventLog, EventTypes for strategy-layer event tracking |
| `formulas/`     | Habitability formulas |
| `validation/`   | ColonizeValidator, SuperweaponValidator, TransferValidator |
| `systems/`      | DesignLibrary, RaceLibrary, RaceRandomizer, SaveGameService |

### `game/ai/` -- Combat AI

| Module               | Description |
|----------------------|-------------|
| `controller.py`      | AIController -- main decision loop per ship |
| `behaviors.py`       | 12 behavior classes (Kite, AttackRun, Ram, Flee, Formation, Orbit, StationaryFire, DoNothing, StraightLine, RotateOnly, Erratic + base AIBehavior) |
| `strategy_manager.py`| StrategyManager -- resolves AI strategy names to definitions |
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
| `screens/`       | BattleScreen, StrategyScreen, WorkshopScreen, MenuScene, SetupScreen, NewGameSetupScreen, FormationEditorScreen, TestLabScreen, GalaxyTestScreen, BuildQueueScreen, plus sub-screen packages (`builder/`, `formation/`, `test_lab/`, `galaxy_test/`) |
| `renderer/`      | Camera, GameRenderer, SpriteManager |
| `panels/`        | BattlePanels, BuilderWidgets |
| `components/`    | Reusable UI components including `table/` subpackage |
| `widgets/`       | PanelFactory, ScrollableJsonPanel, UIElementRegistry |
| `services/`      | BattleFactories, InputMapper, ShipFactory, ShipIO, ComponentService, ValidationService |
| `orchestration/` | BattleOrchestrator (coordinates battle UI flow) |
| `research/`      | Research/tech tree UI visualization |
| `interfaces/`    | UI-layer interface definitions |
| `utils/`         | UI utility functions |
| `config.py`      | UIConfig (moved from core in PROJ-113) |
| `colors.py`      | Color constants |
| `fonts.py`       | Font configuration |

---

## Package Public APIs

Exports defined in each package's `__init__.py` via `__all__`.

### `game.core` (43 exports)

- **Exceptions:** GameException, StateException, FrozenStateException, ValidationException, ResourceException, MissingResourceException, PersistenceException, SimulationException, ComponentException, FormulaException
- **Error Codes:** ErrorCode
- **Math:** Vector2, clamp, lerp, angle_diff
- **Registry/DI:** GameRegistries, RegistryManager, DefaultRegistryProvider, TestRegistryProvider, get_default_registry_provider
- **Constants:** GameState, LayerType, AttackType, LayerDefaults, CombatConstants, PLANET_RESOURCES
- **Event Logging:** log_event, set_event_handler, get_event_handler
- **Validation:** ValidationResult, IValidationRule
- **Configuration:** DisplayConfig, AIConfig, PhysicsConfig, BattleConfig
- **Paths:** Paths
- **Protocols:** IRegistryProvider, IFleet, IPlanet, ICombatant, is_fleet, is_planet, is_combatant

### `game.engine` (3 exports)

PhysicsBody, CollisionSystem, SpatialGrid

### `game.simulation` (12 exports)

Ship, ShipSerializer, Component, create_component, BattleEngine, BattleLogger, BattleEndMode, BattleEndCondition, BattleService, BattleServiceResult, BattleState, ShipDesignValidator

### `game.strategy` (15 exports)

Fleet, ShipInstance, OrderType, FleetOrder, HexCoord, TurnEngine, GameSession, GameConfig, StrategySessionFacade, FleetInfo, SystemInfo, PlanetInfo, EmpireInfo, IBattleResolver, BattleResult

### `game.ai` (13 exports)

AIController, AIBehavior, KiteBehavior, AttackRunBehavior, RamBehavior, FleeBehavior, FormationBehavior, OrbitBehavior, StationaryFireBehavior, DoNothingBehavior, StrategyManager, TargetEvaluator, AIControllerFactory

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
| IPlanet       | planet_type, resources, owner_id, populations, facilities, atmosphere | is_planet |
| IStarSystem   | stars, planets, warp_points, global_location, storms | is_star_system |
| IEmpire       | id, name, color, colonies, fleets, resource_pool | is_empire |
| IStorm        | storm_type, effects, occupied_hexes | is_storm |
| IWarpPoint    | destination_id, location | is_warp_point |
| IZoneOccupant | occupied_hexes (FrozenSet) | is_zone_occupant |
| IShipInstance | design_id, design_data, hull_class, cargo_contents | is_ship_instance |
| IFacility     | instance_id, design_id, design_data, is_operational | is_facility |

### Combat Protocols

| Protocol    | Key Properties | TypeGuard |
|-------------|----------------|-----------|
| ICombatant  | team_id, is_alive, position | is_combatant |
| IDamageable | current_hp, max_hp, is_derelict | -- |
| ICombatShip | team_id, hp, max_hp, is_derelict, layers, resources, total_defense_score | is_combat_ship |

### Simulation-Internal Protocols (`game/simulation/interfaces/`)

Ability: IAbility, IWeaponAbility, IBeamWeaponAbility, ISeekerWeaponAbility, IProjectileWeaponAbility, IResourceConsumptionAbility, IResourceStorageAbility, IResourceGenerationAbility, IWarpJumpAbility. Entity: ICombatShip, IProjectile, IPhysicsShip, IFormationHost, ISerializableShip. Component: IComponent. Each has a corresponding `is_*` TypeGuard function.

---

## Cross-Layer Communication

### 1. Protocols (Primary Mechanism)

Layers communicate through Protocol definitions in `game/core/protocols.py`. Upper layers depend on protocol interfaces, not concrete classes. Example: Strategy layer uses `IPostBattleShip` to read post-battle ship state without importing `game.simulation.entities.ship.Ship`.

### 2. Dependency Injection

**Registry DI:** Services accept `IRegistryProvider` instead of accessing the global `RegistryManager` singleton directly. Production uses `DefaultRegistryProvider`; tests use `TestRegistryProvider`.

**AI Factory DI:** `BattleService.create_battle()` accepts an optional `IAIControllerFactory` injected from higher layers (UI/strategy), because AI depends on Simulation (not vice versa).

### 3. Interface Contracts

**IBattleResolver** (`game/strategy/interfaces/battle_resolver.py`): Abstract base class that decouples strategy from simulation. `SimulationBattleResolver` (`game/strategy/adapters/`) is the production implementation.

### 4. Facade Pattern

**StrategySessionFacade** (`game/strategy/facade/`): Single entry point for UI-to-strategy communication. Returns read-only DTOs (FleetInfo, SystemInfo, PlanetInfo, EmpireInfo) to prevent UI from mutating strategy state.

### 5. Late Imports

Intentional late imports exist at specific cross-layer boundaries:
- `Ship.add_component()` imports ModifierService (real import cycle)
- `ShipInstance.from_ship()`/`to_ship()` imports ShipSerializer (cross-layer boundary)
- `ShipInstance.get_calculated_stats()` imports ShipStatsCalculator (lazy init)
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
RegistryManager (game/core/registry.py)
  singleton holding GameRegistries(components, modifiers, vehicle_classes, resources)
       │
       ▼
IRegistryProvider (injected into services)
       │
       ├──► Component / create_component()  (game/simulation/components/)
       ├──► Ship / ShipSerializer           (game/simulation/entities/)
       ├──► ShipStatsCalculator             (game/strategy/services/)
       └──► VehicleDesignService            (game/simulation/services/)
```

### Battle Flow

```
UI (BattleScreen) or Strategy (IBattleResolver)
       │
       ▼
BattleService.create_battle(ai_factory=...)
       │  returns BattleServiceResult(engine=BattleEngine)
       ▼
BattleEngine.tick()  (game/simulation/systems/battle_engine.py)
       │  runs: AI decisions → weapon firing → damage calc → physics → end checks
       │
       ▼
BattleState (game/simulation/battle_state.py)
       │  holds: ships[], tick_count, results
       ▼
Post-battle: Ship instances satisfy IPostBattleShip protocol
       │
       ▼
Strategy layer reads survivors via IPostBattleShip
  ShipInstance.update_from_ship(survivor)
  Fleet.update_from_battle_results(survivors)
```

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
       │  Phase 0:   HarvestingEngine (1/100th per tick)
       │  Phase 0a:  MaintenanceEngine (1/100th per tick, immediate scuttle)
       │  Phase 0b:  ResourceManagementEngine (per-turn consumption)
       │  Phase 0c:  ResupplyEngine (fuel generation at facilities)
       │  Phase 0d:  ResupplyEngine (fleet resupply from facilities)
       │  Phase 0e:  ProductionEngine (construction + mid-turn completion)
       │  Phase 0f:  EnvironmentalHazardEngine (storm damage, fuel drain)
       │  Phase 1:   FleetOrderProcessor (instant orders)
       │  Phase 1.5: ActionExecutionEngine (COLONIZE, TRANSFER, superweapons)
       │  Phase 2:   FleetMovementEngine (calculate moves)
       │  Phase 3:   FleetMovementEngine (apply moves)
       │  Phase 4:   ConflictResolutionEngine (triggers IBattleResolver)
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

`game/app.py` -- Pygame application loop. Initializes registries, creates scenes (implementing `IScene` protocol), and runs the main event/update/draw loop. Scene transitions are managed by the app, not by scenes themselves. Key screens: MenuScene, BattleScreen, StrategyScreen, WorkshopScreen (DesignWorkshopScreen), BattleSetupScreen, FormationEditorScreen, TestLabScreen, NewGameSetupScreen, KeybindingsScene.
