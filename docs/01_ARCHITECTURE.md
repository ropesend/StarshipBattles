# Starship Battles - Architecture Compact Reference

> **Last verified:** 2026-05-22 — Group B + Group C parallel-batch merge integration. PROJ-468 (Group B): added a New-Game Initialization (GameInitializer) subsection documenting `game/strategy/engine/game_initializer.py`. PROJ-467 (Group B) foundation doc-drift sweep: added the `game/strategy/` prefix to the `galaxy_protocols.py` listing and moved "pathfinding" out of the `data/` listing (it lives in `services/galaxy_pathfinding_service.py`). PROJ-457/459/460 (Group C) consolidated doc update: noted the sibling-module serde extractions — `fleet_serde.py` (PROJ-459) in `game/strategy/data/`, and `battle_state_serde.py` + `battle_controller_spec.py` + the direction-split `replay/` serde modules (`replay_serde_helpers.py` / `replay_capture_serde.py` / `replay_outcome_serde.py`) (PROJ-460) in `game/simulation/`. Earlier (2026-05-18): PROJ-436 Phase 10 doc refresh: `game/strategy/data/` listing now flags the unified `Container` storage substrate (`container.py`, `containable.py`, `bay_inventory.py`'s four-slot widening), the `Empire.resource_pool` pure-aggregation contract, and the `IProductionResourceSource` Protocol seam that replaced the `ProductionEngine.context_type` dispatch. Earlier (2026-05-08): balanced compact replacement derived from `docs/01_ARCHITECTURE.md` and `AgentCoordination/Scratchpad/reports/01_ARCHITECTURE_ALT_compact.md`, with source checks for current exports, protocol modules, turn-engine phases, and recent strategy decomposition paths.

This is the agent-facing architecture reference. It preserves current contracts, paths, invariants, extension rules, and high-value test references while dropping release-note chronology and repeated prose.

## Layer Model

Strict downward dependency flow:

| Layer | Path | Owns | May Depend On |
|---|---|---|---|
| UI | `game/ui/`, `game/app.py` | Pygame screens, panels, widgets, rendering, app loop | AI, Strategy, Research, Simulation, Engine, Services, Assets, Core |
| Assets | `game/assets/` | Asset managers, generated image derivatives, image lookup | Services, Core |
| AI | `game/ai/` | Combat AI, behaviors, targeting, policies | Simulation, Engine, Services, Core |
| Strategy | `game/strategy/` | Galaxy, empires, fleets, turns, economy, generation | Simulation, Engine, Services, Core |
| Research | `game/research/` | Tech tree, research tracker/service | Services, Core |
| Simulation | `game/simulation/` | Combat simulation, ships, components, abilities, battle outcomes | Engine, Services, Core |
| Engine | `game/engine/` | Low-level physics, collision, spatial indexing | Services, Core |
| Services | `game/services/` | Cross-cutting infrastructure used by multiple layers | Core only |
| Core | `game/core/` | Math, config, constants, registry, protocols, validation | Standard library only |

Forbidden imports:

- `game/core/` imports no game layer.
- `game/services/` imports only Core, stdlib, and third-party packages.
- `game/simulation/` does not import Strategy, AI, or UI.
- `game/strategy/` does not import UI.
- `game/engine/` does not import Simulation, Strategy, AI, or UI.
- `game/assets/` does not import UI, Strategy, Simulation, Research, AI, or Engine.

If an import would point upward, introduce a protocol, DTO, facade, adapter, or higher-layer factory injection.

## Service Layer Rules

`game/services/` is for cross-cutting infrastructure only. A service belongs there only if all are true:

- It depends only on `game/core/` plus stdlib/third-party packages.
- It is used by at least two other layers, or has a clear multi-layer roadmap.
- It has a documented protocol and at least one testable implementation.

Current shared service package:

- `game/services/llm/` - `LLMProvider` protocol, `DeepSeekProvider`, `LLMProviderFactory`, background-call helper, and default-provider accessors.

Layer-specific services stay inside the consuming layer, such as `game/ui/services/` or `game/strategy/services/`.

## Composition Root And DI

`game/context.py` sits outside the layer hierarchy and defines `ApplicationContext`.

Current contract:

- `ApplicationContext.create_production()` creates the production service graph.
- `ApplicationContext.create_test(**overrides)` creates isolated test service graphs.
- Context-owned services install matching module-level defaults where applicable.
- Services outside the constructor follow the same `get_default_*` / `set_default_*` accessor pattern and are consulted on demand.
- Prefer constructor injection. Module-level defaults are for composition roots, decorators, convenience functions, and established leaf code.
- Simulation code must not resolve registry providers through globals.

ApplicationContext-managed services:

- `RegistryManager` - `game/core/registry.py`
- `Profiler` - `game/core/profiling.py`
- `ComponentCacheManager` - `game/simulation/components/component_loader.py`
- `PolicyManager` - `game/ai/policy_manager.py`
- `AssetManager` - `game/assets/asset_manager.py`
- `SpriteManager` - `game/ui/renderer/sprites.py`
- `ShipThemeManager` - `game/ui/assets/ship_theme_manager.py`
- `GameSettings` - `game/ui/services/game_settings.py`
- `LLMProvider` - `game/services/llm/provider.py`
- `ImageProvider` - `game/ui/services/image/provider.py`

Additional context-level extension slot:

- `get_default_planet_habitability_service()` / `set_default_planet_habitability_service()` in `game/context.py` let tests and mods swap the `IHabitabilityCalculator` implementation. The default is `PlanetHabitabilityService` in `game/strategy/services/planet_habitability_service.py`.

## Package Map

### `game/core/`

Foundation layer. No game-layer dependencies.

Important modules:

- `math.py`: `Vector2`, `clamp`, `lerp`, `angle_diff`.
- `hex_math.py`: `HexCoord` axial coordinates.
- `spectrum_math.py`: pure spectrum/wavelength math.
- `combat_types.py`: `DamageContext` frozen DTO.
- `config.py`: `DisplayConfig`, `AIConfig`, `PhysicsConfig`, `BattleTuning`.
- `constants.py`: `GameState`, `LayerType`, `AttackType`, `LayerDefaults`, `CombatConstants`.
- `protocols/`: cross-layer Protocol definitions and TypeGuards. Current submodules are `boundary.py`, `combat.py`, `common.py`, `persistence.py`, `registry.py`, `strategy_domain.py`, `strategy_entities.py`, `strategy_mutators.py`, and `ui.py`.
- `registry.py`: `GameRegistries`, `RegistryManager`, `DefaultRegistryProvider`, `TestRegistryProvider`.
- `exceptions.py`: 27 exception classes, including strategy, LLM, and image-service hierarchies.
- `error_codes.py`: `ErrorCode`.
- `event_logging.py`: session-scoped `EventBus` class (constructor-injected; PROJ-390 retired the module-level shim).
- `formula_evaluator.py`: AST-based formula evaluation.
- `validation.py`: `ValidationResult`, `IValidationRule`.
- `paths.py`: file/path constants.
- `resources.py`: `ResourceCatalog`, `ResourceDefinition`.
- `roles.py`: shared `Role` and `RoleRegistry` for gameplay design roles and Combat Lab scenario roles.
- `input_actions.py`: keybinding actions.
- `ship_classes.py`: ship class enumeration/categorization.
- `component_state.py`: per-component runtime state.
- `state_machine.py`: generic `ScreenStateMachine`.
- `return_destination.py`: battle-flow return destination.
- `json_utils.py`: JSON helpers, including atomic save behavior used by replay sidecars.
- `profiling.py`: `Profiler`, `profile_action`.
- `string_utils.py`, `validation_helpers.py`: shared helpers.
- `patterns/layer_iterator.py`: generic layer iteration pattern.

### `game/services/`

- `llm/types.py`: `Role`, `FinishReason`, `Message`, `TokenUsage`, `CompletionResult`.
- `llm/provider.py`: `LLMProvider` runtime-checkable protocol.
- `llm/factory.py`: `LLMProviderFactory.create()` via `LLM_PROVIDER`; `register_provider()`.
- `llm/deepseek.py`: OpenAI-compatible DeepSeek HTTP client with hardened timeouts, SSL, custom user agent, and retry on 5xx except 429.
- `llm/background.py`: `LLMBackgroundCall`, `shutdown_all_calls()`.
- `llm/defaults.py`: default-provider accessors.

### `game/assets/`

- `asset_manager.py`: `AssetManager` and default accessors for external images, generated component derivatives, race/planet/star images, and missing-texture fallback.
- `component_derivatives.py`: startup generation/refresh of component image derivatives from tracked 1024px source images.

### `game/engine/`

- `physics.py`: `PhysicsBody` property container for position, velocity, angle, mass, forward vector.
- `collision.py`: `CollisionSystem` for hit detection, raycasting, ramming, and typed beam-resolution consumption.
- `spatial.py`: `SpatialGrid` hash grid for proximity queries.

### `game/simulation/`

Combat simulation layer.

- `entities/`: `Ship` facade and delegates, component/resource/combat/layer managers, serializers, physics, combat engine, stat calculation/query helpers, projectile/entity types, and `stat_contributors/`.
- `components/`: `Component` facade, `create_component`, modifier/ability/health/resource delegates, component stats, schema/introspection helpers.
- `components/abilities/`: weapons, defense, propulsion, cargo, crew, resources, harvester, colonize, planetary, markers, superweapons.
- `systems/`: `BattleEngine`, end conditions, resource manager, tech presets, tick phase helpers.
- `services/`: `BattleService`, `RegistryLoader`, `ModifierService`, `DesignLoader`, `VehicleDesignService`, `ship_materializer.py`.
- `combat/`: damage, targeting, weapon firing, attack contracts, weapon family registry, fleet auras, boundary regions, formation resolver, modifier stack, telemetry.
- `managers/`: `BattleStateManager`, visual-mode `RetreatManager`.
- `replay/`: replay capture/playback DTOs and serialization. Serialization is split by direction (PROJ-460): `replay_serde_helpers.py` (shared `Vector2` / `ComponentStateSpec` helpers + `REPLAY_SCHEMA_VERSION = "2.0.0"`), `replay_capture_serde.py` (spec-side: boundary, modifier stack, ship/squadron/task-force/team specs, `battle_spec_to_dict`/`from_dict`), `replay_outcome_serde.py` (outcome-side: hit records, weapon summaries, ship stats, `battle_outcome_to_dict`/`from_dict`, `compute_components_registry_hash`). The package `__init__` re-exports the public serde functions. The runtime capture-sink hook is the separate `replay_capture.py`. Headless `replay_player.py` and pure verifier.
- `interfaces/`: simulation-internal protocols for AI controllers, abilities, components, and entities.
- `validation/`: `ShipDesignValidator`.
- Root modules include `BattleState` (save/load serde lives in the sibling `battle_state_serde.py` — PROJ-460), `BattleTuning`, `BattleConfig`, visual-mode `BattleController` (spec-in init lives in the sibling `battle_controller_spec.py` — PROJ-460), `BattleSpec`, `BattleOutcome`, `battle_runner.run_battle`, and `ProjectileManager`.

Replay persistence is strategy-side: `ReplayStore`, `ReplayResolver`, `ReplayShipBuilder`, `ReplayVerificationCoordinator`, and verification sidecars live in `game/strategy/services/`.

### `game/strategy/`

4X strategy layer.

- `data/`: domain entities and delegates, including `Fleet`, `ShipInstance`, `Empire`, `Galaxy`, `GalaxyState`, `Planet`, `StarSystem`, `WarpPoint`, `stars.py`, `spectrum.py`, `planet_serde.py`, `fleet_serde.py`, physics, fleet/ship delegates, hierarchy (`task_force.py`, `squadron.py`, `fleet_hierarchy.py`), role/policy registries, and generation config modules. **Deployable battlefield assets (mines / fighters / satellites) are typed siblings of `Fleet`, NOT Fleets** (PROJ-431 / TD-10): `game/strategy/data/deployed_group.py` defines `DeployedGroup` (abstract) + `MineGroup` + `FighterWing` + `SatelliteConstellation`, and `Empire.deployed_groups: list[DeployedGroup]` carries them alongside `Empire.fleets`. The runtime type IS the model — there is no `Fleet.group_kind` discriminator and no fleet-action guard, because the fleet-action methods don't exist on `DeployedGroup`. See `docs/systems/strategy_layer.md` "Deployed Groups" and `docs/02_PATTERNS.md`. **Storage uses the unified `Container` substrate** (PROJ-436): `container.py` (`Container` + `ContainerPolicy` + `ContainableKind`), `containable.py` (`ItemRef`, `species_mass_per_unit`), and `bay_inventory.py` (`BayInventory` with four typed slots — `bay: list[CarriedVehicle]`, `pods: list[DropPod]`, `resources: dict[str, float]`, `population: dict[str, int]`). One mass-cap + one policy filter governs all three internal slices. `Empire.resource_pool` is a pure aggregation query over `colonies[*].stockpile`; `ProductionEngine` reads through the `IProductionResourceSource` Protocol satisfied by both Planet (stockpile API) and Fleet (cargo API). See `docs/02_PATTERNS.md` Pattern #43 and `docs/systems/resource_system.md`.
- `game/strategy/data/galaxy_protocols.py`: read/read-write protocols for strategy decomposition: `IGalaxySystemGraph`, `IGalaxySpatialQuery`, `IHabitabilityCalculator`, `IStockpileHolder`, `IStagingYardHolder`.
- `engine/`: `TurnEngine`, `TurnEngineConfig`, `GameSession`, config/initializer, command registry/handlers, order handlers, order processor, phase registry, turn snapshots, and sub-engines for movement, conflict, harvesting, production, population, economy, resupply, actions, planet actions, component activation, planet modifier effects, organics, happiness, quality, atmosphere, and water. The order-execution surface accepts both fleet ships and planets via the polymorphic `IIssuerAdapter` abstraction in `game/strategy/engine/issuer_adapter.py` (`FleetShipIssuerAdapter` / `PlanetStagingYardIssuerAdapter`); `ActionExecutionEngine` ticks both `fleet.orders` and `planet.orders` so the five FMS handlers (lay mines / launch / recover fighters and satellites) serve both issuer kinds (see Pattern #40).
- `services/`: fleet speed/navigation, component inspection, design cost/validation, cargo transfer, action time, cargo projection, modifiers, strategic ability scanning, deployment zones, task group suggestions, stabilizer/superweapon registries, system destruction/effects, ability source adapters, replay services, planet query/habitability, galaxy pathfinding, intercept calculation, economy projection, race description LLM helpers, and write services implementing strategy mutator protocols.
- `facade/`: `StrategySessionFacade`.
- `facade/slices/`: internal facade slices behind the public facade.
- `facade/dto/`: read-only DTOs: `FleetInfo`, `SystemInfo`, `PlanetInfo`, `EmpireInfo`, `TaskForceInfo`, `SquadronInfo`, `ShipInfoExtended`, build queue and colony demographic DTOs.
- `interfaces/`: `IBattleResolver`, strategy `BattleResult`, engine interfaces.
- `adapters/`: `SimulationBattleResolver`.
- `combat/`: strategy battle spec compiler and post-battle hook.
- `generation/`: galaxy density, placement, region classification, star/planet/storm generation, image registries, and loaders.
- `events/`: event log/types.
- `formulas/`: colony output and habitability formulas.
- `validation/`: colonization, superweapon, transfer, planet-order validation.
- `systems/`: design/race libraries, cached race registry, race randomizer, `SaveGameService`.
- `config/`: economy config.

Strategy invariants:

- `Galaxy` is a facade over `GalaxyState` plus entity/spatial/generation/pathfinding delegates. Long logic belongs in delegates, not in `Galaxy`, `Planet`, or `Star`.
- Strategy entity mutation should go through write services and mutator protocols when covered by `IFleetMutator`, `IPlanetMutator`, `IEmpireMutator`, or `IShipInstanceMutator`.
- `TurnEngineConfig.create_default(registries, ...)` is the canonical injection entry point for turn-engine dependencies.
- `TurnEngine.__init__` requires `config`; per-engine override kwargs and lazy fallback initialization are not current architecture.
- The silent `_NullBattleResolver` placeholder is gone. Combat without a wired resolver raises at the conflict dispatch site.
- Capability validation is hard, not soft: unmet capability requirements (`RequiresMaintenance` total > `ProvidesMaintenance` total, crew without life support, missing C&C / combat-movement gates, etc.) raise design-time `ValidationException` rather than silently degrading runtime behaviour. See `docs/03_CONVENTIONS.md` "Capability validation is hard, not soft".

### `game/ai/`

- `controller.py`: `AIController.update()` staged as target acquisition, behavior selection, behavior execution.
- `behaviors.py`: 11 behavior classes plus base `AIBehavior`.
- `spatial_behaviors/`: BattleLine, Column, Screen, Escort, PatrolZone, FreeManeuver.
- `group_target_coordinator.py`: focus fire, reserve commitment, flagship succession.
- `policy_manager.py`: targeting/movement policy loading and lookup.
- `target_evaluator.py`: target scoring/prioritization.
- `ai_factory.py`: canonical `AIControllerFactory`.
- `combat_utils.py`, `protocols.py`, `interfaces/`: AI support APIs.

### `game/research/`

- `data/`: `TechNode`, `TechTree`, `ResearchTracker`.
- `systems/`: `ResearchService`.
- No public package exports; treated as sandbox/experimental internally.

### `game/ui/`

- `screens/`: `BattleScreen`, `StrategyScreen`, `DesignWorkshopScreen`, `MenuScene`, `FleetBattleSetupScreen` aliased as `BattleSetupScreen`, `NewGameSetupScreen`, `TestLabScreen`, `GalaxyTestScreen`, `BuildQueueScreen`, setup models, battle results, modal windows, and sub-screen packages (`builder/`, `battle_setup/`, `test_lab/`, `galaxy_test/`, `race_setup/`, `strategy_render/`, `strategy_windows/`).
- `renderer/`: `Camera`, `GameRenderer`, `SpriteManager`.
- `panels/`: battle panels, builder widgets, report panels, galleries, treasury/build queue panels.
- `components/`: reusable UI components including table/filter widgets.
- `widgets/`: panel/dropdown/range/scroll widgets and element registry.
- `services/`: input mapping, ship factory/I/O, component/validation services, game settings, image generation service package.
- `services/image/`: `ImageProvider` protocol, `OpenAIImageProvider`, `NullImageProvider`, factory/defaults, `ImageBackgroundCall`.
- `assets/`: `ShipThemeManager`.
- `orchestration/`: retained package; AI controller creation goes through `AIControllerFactory`.
- `research/`, `interfaces/`, `utils/`, `effects/`, `filters/`, `config.py`, `colors.py`, `fonts.py`: UI support.

## Public Package APIs

Exports are defined by package `__init__.py` and `__all__`.

- `game.core` exports 54 symbols. Includes base exceptions plus LLM exceptions, `ErrorCode`, math utilities, `GameRegistries`, registry providers, constants, event logging helpers, validation/config/path types, selected core protocols/TypeGuards, and `Role`/`RoleRegistry`.
- `game.engine` exports 3 symbols: `PhysicsBody`, `CollisionSystem`, `SpatialGrid`.
- `game.simulation` exports 32 symbols: `Ship`, `ShipSerializer`, `Component`, `create_component`, `BattleEngine`, `BattleLogger`, public end-condition basics, `BattleService`, `BattleServiceResult`, `BattleState`, `ShipDesignValidator`, `BattleSpec` DTOs, and `BattleOutcome` DTOs.
- `game.strategy` exports 15 symbols: `Fleet`, `ShipInstance`, `OrderType`, `Order`, `HexCoord`, `TurnEngine`, `GameSession`, `GameConfig`, `StrategySessionFacade`, four read DTOs, `IBattleResolver`, and `BattleResult`.
- `game.ai` exports 12 symbols: controller, behavior classes, `PolicyManager`, `TargetEvaluator`, and `AIControllerFactory`.
- `game.ui` exports 7 eager module imports: sprites, camera, game renderer, battle screen/UI/panels, builder widgets. `workshop_screen` is intentionally excluded because of Tkinter side effects.
- `game.research` has no public API exports.

## Protocols And Boundary Contracts

Shared cross-layer protocols live in `game/core/protocols/`, a 9-module package re-exported from its `__init__.py`. Protocols use `@runtime_checkable`; runtime narrowing uses TypeGuard functions and duck-typed distinguishing attributes so test doubles do not need full structural conformance.

Cross-layer and common protocols:

- `IRegistryProvider`: `get_components()`, `get_modifiers()`, `get_vehicle_classes()`, `get_resources()`.
- `IPostBattleShip`: strategy/simulation post-battle transfer. Requires `name`, `hp`, `max_hp`, `is_alive`, `is_derelict`, `layers`, optional `resources`.
- `IResourceReader`: read-only resources: `get_value(name)`, `get_max_value(name)`, `get_resource_names()`.
- `IResourceHolder`: resource holder boundary surface.
- `IRaceRegistry`: `get_race(race_id: str) -> Optional[RaceConfig]`; implemented by `CachedRaceRegistry`. Cache invalidation is explicit.
- `ICamera`: camera properties and coordinate conversion/update methods.
- `IScene`: `handle_event(event)`, `update(dt)`, `draw(screen)`, `handle_resize(width, height)`.
- `ISerializable`: persistence boundary protocol.
- `ILocatable`, `INamed`, `IOwnable`: common structural mixins.

Strategy entity protocols:

| Protocol | Distinguishing Surface | TypeGuard |
|---|---|---|
| `IFleet` | ships, orders, location, owner_id, capabilities, resources, battle | `is_fleet` |
| `IPlanet` | planet type, deposits, stockpile, owner, populations, facilities, atmosphere, energy | `is_planet` |
| `IOrderable` | orders and order queue methods | none |
| `IStarSystem` | stars, planets, warp points, global location, storms | `is_star_system` |
| `IStar` | star identity/spatial surface | `is_star` |
| `IEmpire` | id, name, color, colonies, fleets, resource pool | `is_empire` |
| `IStorm` | storm type, abilities, occupied hexes | `is_storm` |
| `ISectorEnvironment` | sector environment surface | `is_sector_environment` |
| `IAbilitySource` | source identity, owner, abilities, sector/system effect checks, activation state | `is_ability_source` |
| `IWarpPoint` | destination id, location | `is_warp_point` |
| `IZoneOccupant` | occupied hexes | `is_zone_occupant` |
| `IShipInstance` | design id, design data, hull class, cargo contents, carried items | `is_ship_instance` |
| `IFacility` | instance id, design id, design data, operational state | `is_facility` |

Strategy mutator protocols:

- `IFleetMutator`, `IPlanetMutator`, `IEmpireMutator`, `IShipInstanceMutator` live in `game/core/protocols/strategy_mutators.py`.
- Production write services live in `game/strategy/services/fleet_write_service.py`, `planet_write_service.py`, `empire_write_service.py`, and `ship_instance_write_service.py`.
- Read protocols answer "what is the state?"; mutator protocols answer "who is allowed to change it?"

Combat protocols:

- `ICombatant`: `team_id`, `is_alive`, `position`; TypeGuard `is_combatant`.
- `IDamageable`: `current_hp`, `max_hp`, `is_derelict`.
- `ICombatShip`: `team_id`, `hp`, `max_hp`, `is_derelict`, `layers`, `resources`, `total_defense_score`; TypeGuard `is_combat_ship`.

Simulation-internal protocols live in `game/simulation/interfaces/` and cover abilities, weapons, resource abilities, warp jump ability, combat/projectile/physics/serializable ships, and components. Each has an `is_*` TypeGuard.

Strategy decomposition protocols outside Core live in `game/strategy/data/galaxy_protocols.py`: `IGalaxySystemGraph`, `IGalaxySpatialQuery`, `IHabitabilityCalculator`, `IStockpileHolder`, and `IStagingYardHolder`.

## Cross-Layer Communication

Use these mechanisms:

- Protocols in `game/core/protocols/`: primary shared boundary contract.
- Strategy-specific read protocols in `game/strategy/data/galaxy_protocols.py` when the contract is not cross-layer.
- Dependency injection: pass `IRegistryProvider`, service protocols, factories, or concrete services from higher layers.
- `IBattleResolver` (`game/strategy/interfaces/battle_resolver.py`): decouples strategy from simulation. Production implementation is `SimulationBattleResolver` in `game/strategy/adapters/simulation_adapter.py`.
- `StrategySessionFacade` (`game/strategy/facade/`): only UI-to-strategy entry point. It returns read-only DTOs to prevent UI mutation of strategy state.
- Intentional late imports only at documented boundary/cycle points.

Allowed late imports:

- `Ship.add_component()` imports `ModifierService`.
- `ShipInstanceBridge.to_ship()` imports `ShipSerializer`.
- `ShipInstance.get_calculated_stats()` imports `calculate_design_stats`.
- `Fleet.trigger_speed_recalculation()` imports `FleetSpeedCalculator`.
- `ReplayPlayer._materialize_ship_state()` imports `ShipInstanceSerializer` from `game/strategy/data/` for replay reconstruction.
- `TurnEngineConfig.create_default()` imports concrete sub-engine and mutator implementations. TurnEngine methods must not import engines locally.

## Data Flow

### JSON To Gameplay

```text
data/*.json
  -> RegistryLoader (game/simulation/services/registry_loader.py)
  -> RegistryManager (game/core/registry.py, managed by ApplicationContext)
  -> GameRegistries(components, modifiers, vehicle_classes, resources, resource_catalog)
  -> IRegistryProvider
  -> Component/create_component, Ship/ShipSerializer, calculate_design_stats, VehicleDesignService
```

Registry DI invariant:

- Production uses `DefaultRegistryProvider`.
- Tests use `TestRegistryProvider`.
- `GameRegistries.__post_init__()` supplies an empty `ResourceCatalog` only when one was omitted; production should pass the real catalog.
- Simulation-layer code does not call global registry accessors.
- `battle_runner.run_battle(..., ship_builder=None, registry_provider=...)` requires `registry_provider` when no ship builder is supplied.
- `BattleController.start_from_spec(...)` mirrors the same DI contract.

### Battle Flow

Unified headless path:

```text
caller (Combat Lab, Battle Setup, Strategy IBattleResolver)
  -> context-specific spec compiler / assembler
  -> BattleSpec frozen DTO
  -> run_battle(spec, ai_factory, ship_builder=None, registry_provider=None, ...)
  -> BattleEngine.start_teams(teams_by_id, seed, end_condition)
  -> tick loop: AI decisions -> weapon firing -> damage calc -> physics -> end checks
  -> extract_outcome(engine, spec)
  -> BattleOutcome
  -> optional spec.post_battle_hook(outcome)
```

The Strategy path uses a typed two-stage seam introduced by PROJ-426
(TD-01). Strategy-only state (`mine_groups`, `owner_to_team_id`,
`combat_fleets`, `engine_ref`) does NOT live on `BattleSpec`; it lives
on a typed `BattleSpecExtensions` sidecar inside a
`StrategyBattleAssembly` returned by
`StrategyBattleAssembler.assemble(...)`. The simulation engine still
receives `assembly.spec`; the pre-tick callback comes from
`assembly.pre_tick_setup.composed_callback()` (a
`PreTickBattleSetupRegistry` populated with the mine + reboard setups).
The legacy `object.__setattr__(spec, "_attr", value)` side-channels on
the frozen `BattleSpec` no longer exist — see Pattern #39 (typed-sidecar
extensions on frozen DTOs) and Pattern #40 (named pre-tick setup
registry) in `docs/02_PATTERNS.md`.

Current contracts:

- `run_battle` constructs `BattleEngine` directly; no `BattleController` in headless mode.
- `spec.boundary` and `spec.modifier_stack` are threaded onto the engine.
- Telemetry aggregators attach per `spec.telemetry_level`.
- Strategy post-battle hook writes `ShipOutcome.components` back to `ShipInstance.components` and prunes destroyed/retreated ships.
- Visual mode uses `BattleController` only as a thin per-frame driver around `BattleEngine`.
- Visual construction uses `controller.start_from_spec(spec, ai_factory=..., ship_builder=None, registry_provider=...)`.
- Visual-mode and headless battles both emit `BattleOutcome`.
- Removed systems stay removed: no `BattleMode`, `BattleModeHandler`, `create_*_battle`, or BattleFactories path.

### Replay Flow

Simulation owns capture/playback DTOs and the capture sink protocol; strategy owns persistence and lookup.

```text
run_battle(..., capture_context=...)
  -> IReplayCaptureSink.on_battle_started(...)
  -> BattleOutcome.replay_id
  -> IReplayCaptureSink.on_battle_ended(...)
  -> ReplayStore persists output/saves/<save>/replays/replay_<uuid>.json
  -> ReplayVerificationCoordinator writes replay_<uuid>.verification.json
  -> ReplayResolver.resolve(replay_id) returns ReplayLookup for UI
```

Replay invariants:

- `ReplayStore` writes one JSON sidecar per battle under the active save folder.
- Replay writes use atomic JSON save behavior.
- Ring-buffer eviction writes the new replay first, then prunes oldest sidecars.
- Verification sidecars are deleted with their replay record and cannot outlive it.
- `ReplayResolver.resolve()` does not raise for missing, corrupt, version-drifted, or registry-drifted records; it returns a `ReplayLookup` state.
- Verification statuses include `PASSED`, `FAILED`, `ERROR`, `SKIPPED_DISABLED`, and `SKIPPED_QUEUE_FULL`.
- Production bootstrap wires the replay store, capture sink, resolver, and verification coordinator; run-loop shutdown joins coordinators before `pygame.quit()`.

### Strategy Turn Flow

```text
UI StrategyScreen
  -> StrategySessionFacade
  -> GameSession
  -> TurnEngine.process_turn()
  -> updated Galaxy/Empire/Fleet state
  -> read-only DTOs returned through StrategySessionFacade
```

### GameSession Lifecycle (PROJ-423)

`GameSession` is a thin shell. Composition lives in three internal collaborators under `game/strategy/engine/session/`:

- `SessionRuntimeServices` (`runtime_services.py`): frozen dataclass holding `registries`, `event_log`, `event_bus`, four mutators, `turn_engine`, `command_registry`. `race_registry` is intentionally outside this bag and remains lazy on `GameSession`.
- `SessionBootstrap` (`bootstrap.py`): canonical wiring. `_build_services(...)` is the single construction site shared by `__init__` and `from_dict`. `new_game_state(config, ai_factory=...)` adds `GameInitializer.initialize` with `SessionInitializationError` null-object substitution.
- `SessionPersistenceAdapter` (`persistence_adapter.py`): `serialize(session)` returns the save dict byte-for-byte; `rehydrate_state(data, ai_factory=..., turn_number_provider=..., race_registry_provider=...)` returns a `SessionBootstrapState`. The four post-deserialize wiring steps (galaxy back-refs, fleet registration, order-target resolve, pursuer-tracker rebuild) run via `restore_graph_wiring(galaxy, empires)` in `game/strategy/engine/session/graph_restoration.py` — PROJ-438 Phase 1 collapsed the previously-duplicated inline loops in `SessionPersistenceAdapter.rehydrate_state()` and `TurnStateSnapshot.restore()` into this shared collaborator. Per-empire `DesignCatalog` repopulation is save-load-only by intentional design.

Public API is unchanged: `GameSession(config=..., ai_factory=...)`, `GameSession.from_dict(data, ai_factory=...)`, `GameSession.to_dict()`. Both `__init__` and `from_dict` route through the canonical `_apply_bootstrap_state(state)` method, which is the single internal assignment path. The save schema is unchanged.

### New-Game Initialization (GameInitializer)

The new-game branch of `SessionBootstrap.new_game_state(...)` delegates galaxy
and empire creation to `game/strategy/engine/game_initializer.py`
(`GameInitializer`), extracted from `GameSession` (PROJ-87 Phase 6) so
initialization logic stays isolated from session management. Its single public
entry point is the static `GameInitializer.initialize(config, *,
planet_mutator=None, empire_mutator=None) -> tuple[Galaxy, list[Empire]]`.

The flow:

1. Build empires from `GameConfig` (`_create_empires`; deterministic, consumes
   no RNG).
2. Generate the galaxy and place homeworlds, retrying on a planet shortage. At
   `N=1` with multiple empires (FEAT-27) the lone star system must hold at least
   one homestead planet per empire; some blueprints can roll too few, so a
   shortage raises an internal `_PlanetShortageError` and the loop re-rolls a
   deterministically-perturbed `galaxy_seed` (via `dataclasses.replace`) up to
   `_PLANET_SHORTAGE_RETRY_ATTEMPTS` (10) times before raising a
   `ValidationException`. Galaxy generation uses placement strategies from
   `game/strategy/generation/` (`RandomPlacementStrategy`,
   `DensityBasedPlacementStrategy`).
3. Set galaxy back-references on each empire (PROJ-219, for auto fleet
   registration) and wire fleet-at-hex / fleets-in-system lookups into the
   unified ability iterator (`_wire_fleet_lookups`, PROJ-305) so fleet
   sector-effects surface.

`planet_mutator` (`IPlanetMutator`) and `empire_mutator` (`IEmpireMutator`) are
the PROJ-370 mutation seams: when supplied (the production path via
`GameSession`) homeworld population seeding and attempt-restart colony resets
route through the mutators; when `None` (direct test calls) the initializer
lazy-constructs an `EmpireWriteService` and falls back to direct list
operations. Loading a saved game does **not** call `GameInitializer` — that
path runs through `SessionPersistenceAdapter.rehydrate_state` instead.

`TurnEngineConfig` contract:

- `TurnEngineConfig` is a frozen dataclass bundling 22 fields: 18 engines plus 4 strategy mutator protocols.
- `TurnEngineConfig.create_default(registries, ...)` eagerly constructs all default engines and mutators.
- Tests override dependencies with `dataclasses.replace(cfg, movement_engine=mock)`.
- `TurnEngine.__init__` accepts `registries`, required `config`, optional documentation/override hooks, and optional `tick_phases` / `end_of_turn_phases`.

Per-tick descriptor list in `game/strategy/engine/turn_phase_registry.py`:

| Order | Phase Key | Engine |
|---|---|---|
| 0 | `harvesting` | `HarvestingEngine` |
| 0b | `resources` | `ConsumableManagementEngine` |
| 0c | `fuel_gen` | `ResupplyEngine.process_fuel_generation` |
| 0c1 | `planet_energy` | `PlanetEnergyEngine` |
| 0d | `resupply` | `ResupplyEngine.process_fleet_resupply` |
| 0e | `production` | `ProductionEngine` |
| 0f | `environmental` | `EnvironmentalHazardEngine` |
| 1 | `instant_orders` | `OrderProcessor` |
| 1.5 | `actions` | `ActionExecutionEngine` |
| 1.6 | `planet_actions` | `PlanetActionEngine` |
| 1.7 | `activation_timers` | `ComponentActivationEngine` |
| 1.8 | `planet_modifier_effects` | `PlanetModifierEffectEngine` |
| 2 | `movement_calc` | `FleetMovementEngine.collect_movements` |
| 3 | `movement_apply` | `FleetMovementEngine.apply_movements` |
| 4 | `combat` | `ConflictResolutionEngine` |

End-of-turn descriptor list:

```text
organics_consumption -> happiness -> population_growth -> quality_improvement -> atmosphere -> water_modification
```

Turn execution invariants:

- `DEFAULT_TICK_PHASE_LIST` has 15 entries and runs for ticks 1..100.
- `DEFAULT_END_OF_TURN_PHASE_LIST` has 6 entries and runs once with `TickContext.tick = 0`.
- `_run_phases()` routes each phase through `_time_phase()` so raw failures become `EnginePhaseError`.
- `process_turn()` captures a pre-turn snapshot and rolls back on failure.
- Sub-engines validate preconditions via `_validate_tick_inputs()` where applicable.
- `progress_callback(current_tick, TICKS_PER_TURN)` is optional and UI-safe; callback failures are logged and do not break turn execution.

## Configuration

`DisplayConfig` in `game/core/config.py`:

- `DEFAULT_WIDTH = 3840`, `DEFAULT_HEIGHT = 2160`.
- `WINDOWED_WIDTH = 2560`, `WINDOWED_HEIGHT = 1600`.
- `TEST_WIDTH = 1440`, `TEST_HEIGHT = 900`.

`PhysicsConfig` in `game/core/config.py`:

- `TICK_RATE = 0.01`.
- `DEFAULT_LINEAR_DRAG = 0.5`.
- `DEFAULT_ANGULAR_DRAG = 0.5`.
- `SPATIAL_GRID_CELL_SIZE = 2000`.

## Entry Point

`game/app.py` is the Pygame application loop. It initializes registries, creates scenes implementing `IScene`, handles transitions, and runs update/draw/event processing. Scenes do not own app-level transitions.

Key scenes/screens:

- `MenuScene`
- `BattleScreen`
- `StrategyScreen`
- `WorkshopScreen` / `DesignWorkshopScreen`
- `FleetBattleSetupScreen`, aliased as `BattleSetupScreen`
- `TestLabScreen`
- `NewGameSetupScreen`
- `KeybindingsScene`

## Extension Guidance

- Add shared infrastructure to `game/services/` only when it satisfies the service-layer rules; otherwise place it in the owning layer.
- Add shared cross-layer contracts to `game/core/protocols/`, with TypeGuards when runtime narrowing is needed.
- Add strategy-local read contracts to `game/strategy/data/galaxy_protocols.py` when they do not need to cross layer boundaries.
- Add covered strategy mutations through write services and mutator protocols, not ad hoc direct attribute mutation.
- Keep UI mutation of strategy state behind `StrategySessionFacade`; expose read-only DTOs.
- Use `IBattleResolver` for strategy-to-simulation battle resolution.
- Use `BattleSpec` plus `run_battle` for headless combat and `BattleController.start_from_spec` for visual combat.
- Pass registries or providers explicitly into simulation code; do not introduce global registry lookups there.
- Extend turn processing by editing descriptor lists in `turn_phase_registry.py`, then update descriptor order tests.
- Override turn-engine dependencies in tests by building `TurnEngineConfig.create_default(...)` and applying `dataclasses.replace`.
- Add strategy commands through the command registry/handler packages (`game/strategy/engine/commands/`, `handlers/`, `order_handlers/`), not tuple literals or hardcoded dispatch lists.
- Use `set_default_planet_habitability_service(...)` to replace habitability calculation; do not monkey-patch formulas or `Planet`.
- Use replay store listener APIs for replay-related subscribers; listener failures must not make replay persistence fail.
- Use late imports only for known, documented cycles or cross-layer reconstruction boundaries.

## Warnings And Stale Reference Corrections

- `game/core/protocols.py` is stale terminology. The current path is the `game/core/protocols/` package, including `strategy_mutators.py`.
- Core public exports are currently 54, not 53. Simulation exports 32, not 34. Strategy exports 15, not 16.
- `exceptions.py` exports 27 exception classes, including LLM and image-service hierarchies. `game.core.__all__` exports the LLM exception subset, not every exception class.
- `TurnEngineConfig` is required and bundles 22 fields. Do not use deleted per-engine kwargs, lazy fallback initialization, or `create_default_turn_engine`.
- The current turn phase model is 15 per-tick descriptors plus 6 end-of-turn descriptors. Older references that stop after planet actions or population growth are incomplete.
- `StarGenerator` lives at `game/strategy/generation/star_generator.py`; `Spectrum` lives at `game/strategy/data/spectrum.py`; pure spectrum math lives at `game/core/spectrum_math.py`.
- `StarSystem` and `WarpPoint` live at `game/strategy/data/star_system.py` and are re-exported from `galaxy.py` for existing imports.
- `AreaEffectManager` is replaced by `SystemEffectsCollector`, `AbilityIterator`, and the `game/strategy/services/ability_sources/` adapter package.
- `BattleController` is visual-mode only; headless callers go through `game.simulation.battle_runner.run_battle`.
- Removed battle setup systems remain removed: no `BattleFactories`, `BattleMode`, `BattleModeHandler`, or `create_*_battle` path.
- `workshop_screen` is intentionally not eagerly imported by `game.ui` because of Tkinter side effects.

## Verification Commands

Primary commands:

```bash
python Tools/test_sharded/test_sharded.py
pytest tests/ --testmon
python -m combat_lab.run_tests
```

Focused architecture guard tests:

```bash
pytest tests/unit/simulation/test_battle_runner_di.py tests/unit/simulation/battle_controller/test_start_from_spec.py
pytest tests/unit/strategy/turn_engine/test_default_tick_phase_list.py tests/unit/strategy/turn_engine/test_default_end_of_turn_phase_list.py tests/unit/strategy/turn_engine/test_tick_phase_descriptors.py tests/unit/strategy/turn_engine/test_no_lazy_fallback_init.py
pytest tests/unit/strategy/data/test_mutator_boundary_ast_guard.py tests/unit/strategy/data/test_galaxy_planet_star_loc_ceilings.py tests/unit/strategy/data/test_no_method_body_over_5_loc.py tests/unit/strategy/data/test_galaxy_state_encapsulation.py
pytest tests/integration/replay/test_capture_pipeline.py tests/integration/replay/test_verification_queue_integration.py
```
