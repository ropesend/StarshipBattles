# 02_PATTERNS Compact Agent Reference

Balanced compact derivative of `docs/02_PATTERNS.md` and
`AgentCoordination/Scratchpad/reports/02_PATTERNS_ALT_compact.md`.
Source doc last verified 2026-05-08. This version removes release-note
archaeology, preserves current contracts and extension recipes, and fixes the
stale pattern count to 35.

## Global Rules

- Prefer dependency injection, protocols, registries, and data-driven dispatch over globals, concrete cross-layer imports, mode switches, and hardcoded class-name lists.
- Simulation code must not call `get_default_registry_provider()`; inject registries or use `Ship._registries` / a passed provider.
- UI talks to strategy through `StrategySessionFacade` DTOs and commands; UI must not mutate strategy domain objects directly.
- New strategy modal windows subclass `StrategyModalWindow`; do not add manual modal slot scanning.
- New UI classes should use Compositional Construction; `bypass_init` is a legacy UIWindow test retrofit only.
- Battle randomness must use injected `random.Random` instances; do not call module-level `random.*` in simulation, engine, or AI.
- Save-file compatibility is not a constraint. Delete replaced systems instead of adding fallback or migration paths.
- Protocol references are under `game/core/protocols/`, not a stale `protocols.py` module path.

## Pattern Map

| # | Pattern | Primary Contract |
|---|---|---|
| 1 | ApplicationContext | `game/context.py::ApplicationContext` owns the app service graph; callers own lifetime. |
| 2 | Protocol + TypeGuard | `game/core/protocols/` defines cross-layer structural contracts plus duck-typed guards. |
| 3 | Registry DI | Services receive `IRegistryProvider`; tests use `TestRegistryProvider`; simulation gets explicit registries. |
| 4 | Registry | Stable keys map to data/classes/callables; avoid switch statements and hardcoded type lists. |
| 5 | Facade / Delegate | Facades expose narrow APIs; delegates own cohesive behavior. |
| 6 | CQRS-lite | Strategy writes use commands; reads use frozen/read-only DTOs. |
| 7 | CommandHandlerRegistry | Command/order dispatch is registry-backed and self-registering. |
| 8 | MVVM | Complex UI screens split state, command boundary, rendering, and events. |
| 9 | Template Method | Validation rules share an execution skeleton with specialized checks. |
| 10 | Event Bus | UI-internal event delivery avoids direct coupling between builder panels. |
| 11 | Surface Caching | `SpriteManager` and asset managers cache loaded/scaled surfaces by stable keys. |
| 12 | Configuration Classes | Named config containers and JSON-backed config loaders replace scattered constants. |
| 13 | Spec Compiler + `run_battle` | All battle callers compile `BattleSpec` and use the unified runner path. |
| 14 | Two-Phase Ability Aggregation | MAX within stack group, then SUM across groups; marker abilities use boolean presence. |
| 15 | Factory | Isolate construction with policy or dependency choices. |
| 16 | ScrollState | Shared scroll bounds/offset helper for UI lists. |
| 17 | Serializable Protocol | Persistence DTOs/classes expose `to_dict` / `from_dict` contracts. |
| 18 | Per-Battle RNG | Seeded `BattleEngine.rng` propagates to combat, collision, damage, and AI. |
| 19 | Error Boundary | Turn processing snapshots, wraps phase errors, rolls back, and re-raises. |
| 20 | Precondition Validation | Sub-engines validate inputs before mutation. |
| 21 | Screen State Machine | App scene transitions use a declarative transition table. |
| 22 | TurnEngineConfig | `TurnEngineConfig.create_default(...)` is the injection point for turn engines. |
| 23 | Tick Phase Registry | Battle tick work is ordered by registered `ITickPhase` priority. |
| 24 | External-Stats Bridge | `ship.external_stats` composes battle-scoped modifiers without mutating source data. |
| 25 | Scope-Driven Team Routing | Ability scope decides recipient team(s), including N-team enemy fan-out. |
| 26 | Ability-Stat Registry | Ability class names map once to external stat entries. |
| 27 | Budget-Aware Randomization | Roll candidates, score with canonical budget API, rebalance toward free baselines. |
| 28 | Background Service Call | Non-daemon worker object with status/result/error/cancel/shutdown contract. |
| 29 | Universal Ability Source | Strategic effects come from `IAbilitySource` adapters and shared collection. |
| 30 | Registrar Close-Callback | Legacy slot cleanup only; modal tracking is superseded by pattern #31. |
| 31 | Strategy Modal Window Base Class | Structural modal register/unregister via `StrategyModalWindow`. |
| 32 | Compositional Construction | New UI classes accept a composition factory/protocol for testable seams. |
| 33 | UI Widget Test Factory | Retrofit legacy pygame_gui widgets with `make_ui_widget` and scoped `bypass_init`. |
| 34 | Weapon Family Registry | Weapon family handlers dispatch attacks; no central branch edits for new families. |
| 35 | Stat Contributor Registry | Per-component stat contributors run through one typed accumulator pipeline. |

## 1. ApplicationContext

Where: `game/context.py`, `game/app.py`, `game/app_bootstrap.py`.

Contract:
- `ApplicationContext.create_production()` builds the production graph once.
- `ApplicationContext.create_test(**overrides)` builds isolated test services.
- Managed services: `RegistryManager`, `Profiler`, `ComponentCacheManager`, `PolicyManager`, `AssetManager`, `SpriteManager`, `ShipThemeManager`, `GameSettings`, `LLMProvider`, `ImageProvider`.
- Context-owned services install matching `get_default_*` / `set_default_*` module defaults where those defaults exist.
- `SingletonMeta`, `game/core/singleton.py`, and `.instance()` service access are retired. Use context, constructor injection, or documented default accessors.
- `game/app_bootstrap.py::bootstrap()` records named `[startup]` phases and saves profiler history early. `pygame.init` and `ctx.create_production` are timed before the profiler exists and backfilled.

Use for composition roots and tests. Do not turn service classes into singletons.

## 2. Protocol + TypeGuard

Where: `game/core/protocols/`, including `boundary.py`, `combat.py`, `common.py`, `persistence.py`, `registry.py`, `strategy_domain.py`, `strategy_entities.py`, `strategy_mutators.py`, `ui.py`.

Contract:
- Define cross-layer interfaces as `@runtime_checkable Protocol`.
- Pair runtime checks with minimal duck-typed `TypeGuard` helpers, not strict `isinstance` checks that require full protocol compliance.
- Use protocols at layer boundaries and for polymorphic entity handling.
- Package `__init__.py` re-exports symbols, so `from game.core.protocols import IFleet` remains valid.

Read/write protocol pair:
- Read protocols answer state questions: `IFleet`, `IPlanet`, `IStarSystem`, `IEmpire`, `IStorm`, `IAbilitySource`, `IWarpPoint`, `IZoneOccupant`, `IShipInstance`, `IFacility`.
- Mutator protocols answer who may change state: `IFleetMutator`, `IPlanetMutator`, `IEmpireMutator`, `IShipInstanceMutator` in `strategy_mutators.py`.
- Engines receive mutators by constructor injection via `GameSession.__init__` and `TurnEngineConfig.create_default()`.
- AST guard: `tests/unit/strategy/data/test_mutator_boundary_ast_guard.py` prevents unauthorized direct mutation of guarded data attributes.

Use mutator protocols when a data class is mutated from more than two outside files. Do not add mutator twins for frozen value objects, single-writer state, or construction-only fields.

## 3. Registry DI

Where: `game/core/registry.py`, `game/core/protocols/registry.py`.

Contract:
- Preferred access is constructor injection of `IRegistryProvider`.
- Leaf factory access may use `get_default_registry_provider()` outside simulation.
- Direct `ctx.registry_manager` use belongs at composition roots.
- `DefaultRegistryProvider` delegates to the module default `RegistryManager`; `TestRegistryProvider` holds isolated dicts.
- `Ship(..., *, registries: GameRegistries)` requires explicit registries and raises on `None`.
- `GameRegistries.__post_init__()` fills an empty `ResourceCatalog` only as a convenience; production should pass the real catalog.
- `ShipStatsCalculator.calculate()` needs a `resource_catalog` or explicit planetary IDs; `calculate_ability_totals()` does not.
- In UI code, use `get_default_registry_provider()` when needed. Do not try to access registries through `scene.facade`; the facade does not expose them.

Facility ability checks:
- Facility designs store component IDs, not inline abilities.
- Resolve abilities through the component registry plus `game.strategy.services.component_inspector.get_component_abilities`.
- Reuse `_facility_has_ability(...)` in `game/strategy/validation/planet_order_validator.py` when applicable.

Unified stat calculation:
- Ship/design stat calculations go through the simulation `Ship` object and `calculate_design_stats()` in `game/simulation/entities/ship_design_stats.py`.
- `ShipInstance.get_calculated_stats()` is the cached strategy wrapper.
- Do not duplicate formulas in UI or strategy, and do not manually iterate components to compute mass/HP.

## 4. Registry Pattern

Where: `game/core/registry.py`, `game/core/resources.py`, ability registries, command registries, weapon/stat contributor registries.

Contract:
- `RegistryManager` holds `components`, `modifiers`, `vehicle_classes`, and `resources` loaded from `data/components.json`, `data/modifiers.json`, `data/vehicleclasses.json`, and `data/resources.json`.
- `GameRegistries` is a frozen DI container and also implements `IRegistryProvider`.
- `ResourceCatalog` / `ResourceDefinition` provide typed, immutable access to planetary materials and operational consumables.
- Lifecycle: load JSON, freeze registry for gameplay, inject provider/container, reset or clear for tests.
- Registries should expose explicit register/reset/lookup behavior and deterministic test reset where mutable.
- Use registries when adding a new type should require one registration, not edits to many dispatch sites.
- Avoid hardcoded lists of ability names, component types, or class names.

## 5. Facade / Delegate

Where: `game/strategy/facade/strategy_session_facade.py`, `game/simulation/entities/ship*.py`, `game/simulation/components/*_manager.py`, strategy data facades for `Galaxy`, `Planet`, and `Star`.

Contract:
- A facade exposes a stable narrow API and hides orchestration.
- A delegate owns one cohesive responsibility and is easier to test directly.
- `StrategySessionFacade` wraps `GameSession`; UI never touches `GameSession` directly.
- Ship delegates component lifecycle to `ShipComponentManager`, combat orchestration to `ShipCombatManager`, and the combat sub-delegate to `ShipCombatEngine`.
- Fleet delegates: `FleetCapabilityCalculator`, `FleetConsumableAggregator`, `FleetBattleAdapter`.
- ShipInstance delegates: `ShipInstanceBridge`, `ShipInstanceSerializer`, `ShipConsumableManager`, `ShipCargoManager`, `ShipDisplayFormatter`.
- Component delegates: `ComponentHealthManager`, `ComponentResourceManager`, `ModifierManager`, `AbilityManager`. `ComponentStatsCalculator` remains a static namespace.

Strategy data facade contract:
- `Galaxy` is a pure facade over `GalaxyState` plus services for entity registry, spatial index, warp generation, system generation, pathfinding, and intercept calculation.
- Read protocols in `game/strategy/data/galaxy_protocols.py`: `IGalaxySystemGraph`, `IGalaxySpatialQuery`, `IHabitabilityCalculator`, `IStockpileHolder`, `IStagingYardHolder`.
- AST guard: `tests/unit/strategy/data/test_no_method_body_over_5_loc.py` keeps `Galaxy` / `Planet` / `Star` methods thin, with lifecycle/serde allowlists.

Use when a class has multiple independent reasons to change. Keep facade methods delegating; put real logic in services/delegates.

## 6. CQRS-lite Strategy Session

Where: `game/strategy/facade/`, DTOs under `game/strategy/facade/dto/`, commands under `game/strategy/engine/commands.py`.

Contract:
- Writes go through command DTOs and command handlers, usually via `facade.handle_command(...)` or generated `dispatch_*` helpers.
- Reads return frozen/read-only DTOs such as `FleetInfo`, `SystemInfo`, `PlanetInfo`, `EmpireInfo`, `TaskForceInfo`, `SquadronInfo`, and `ShipInfoExtended`.
- DTOs include display-safe summaries such as `carried_items_summary`, `pod_storage_capacity`, `pod_storage_used`, and `staging_yard_summary` where needed.
- UI must not hold mutable strategy domain objects as its write surface.

Use for UI-to-strategy communication and any new operation that mutates strategy state.

## 7. CommandHandlerRegistry

> **Last verified:** 2026-05-08

Where:
- Canonical `BaseCommandHandler` + `CommandHandlerRegistry`:
  `game/strategy/engine/handlers/base.py`. The legacy
  `game/strategy/engine/command_handlers.py` re-export shim was removed
  (PROJ-383); all imports must target `handlers/base.py` directly.
- Self-registering command metadata: `game/strategy/engine/commands/registry.py`.
- UI command handlers: `game/strategy/engine/handlers/`.
- Order action handlers: `game/strategy/engine/order_handlers/`.
- Facade command forwarding: `game/strategy/facade/slices/command_dispatch_slice.py`.

Contract:
- Runtime `CommandHandlerRegistry` is `Dict[str, ICommandHandler]` keyed by command class name (e.g. `'IssueColonizeCommand'`); unknown keys return `ValidationResult.error("Unknown command type: ...")`.
- `ICommandHandler` is a `@runtime_checkable` Protocol with one method: `execute(session, command) -> ValidationResult`.
- `BaseCommandHandler` holds shared entity-resolution helpers like `_resolve_fleet(session, fleet_id) -> (fleet, error)`.
- `CommandRegistry` stores one `CommandSpec` per command DTO: handler class, `OrderType`, category, execution model, facade helper name, serializer codec.
- `@command_spec(...)` is metadata-only: it attaches `__command_spec_kwargs__` to the handler class and returns it unchanged. It does NOT call `command_registry.register(...)` at import. Each command module exposes `register(registry)`, and `seed_default_commands(command_registry)` performs registration. Decorator-side registration would break `reset_command_registry()` because Python caches `sys.modules`, so already-imported decorators do not re-fire on a clear+seed cycle.
- `StrategySessionFacade._install_dispatch_forwarders` auto-installs one bound `dispatch_<facade_helper_name>` method per spec so `hasattr(class, name)` and `inspect.getmembers` stay honest. The dispatch slice's `__getattr__` resolves from `command_registry.specs_by_facade_helper()`.
- AST guard: `tests/unit/strategy/engine/test_no_specs_tuple_literal.py` forbids reintroducing a module-level `COMMAND_SPECS = (...)` tuple literal anywhere under `game/`.

Parallel order registry:
- `engine/handlers/`: UI `Command` DTO -> `ValidationResult` and queued `Order` (write side, when player issues a command).
- `engine/order_handlers/`: live `Order` whose action progress hits `action_time` (or instant tick for `JOIN_FLEET`) -> `OrderExecutionResult` and state mutation on Fleet/Planet/Empire.
- `IOrderHandler.execute_action_order(fleet, empire, galaxy, ...)` is the protocol; key is the `OrderType` enum value (e.g. `OrderType.COLONIZE`).
- Factory: `create_default_order_handler_registry(*, event_bus, superweapon_processor=None)`.
- Adding a new order type means add an `IOrderHandler` under `game/strategy/engine/order_handlers/` and register it in `registry_factory.py`.
- Static guards keep `OrderProcessor` LOC under 200, forbid `if order.type == ...` ladders, and require every `OrderType` to have a registered handler.

## 8. MVVM

Where: `game/ui/screens/workshop_*`, `game/ui/screens/build_queue_*`, `game/ui/screens/test_lab/`, `game/ui/screens/battle_setup/`.

Contract:
- ViewModel owns state, derived view data, and events without Pygame dependencies.
- Controller owns facade queries and command emission.
- Renderer/UI builder owns pygame_gui element construction and updates.
- Event router dispatches UI events to the right controller/render path.
- Screen classes compose collaborators and should stay thin.

Build Queue collaborators (canonical multi-collaborator example):
- `BuildQueueController` (`game/ui/panels/build_queue_controller.py`) — business logic.
- `BuildQueueRenderer` (`game/ui/screens/build_queue_renderer.py`) — view management.
- `BuildQueuePanelFactory` (`game/ui/screens/build_queue_panel_factory.py`) — construction.
- `BuildQueueDragHandler` (`game/ui/panels/build_queue_drag_handler.py`) — drag input.

Workshop contracts:
- `WorkshopViewModel` delegates ship operations to `VehicleDesignService`, not `ShipBuilderService`.
- Ship mutations must go through the ViewModel (`remove_component`, `quick_add_component`, movement methods), never directly on the `Ship` object.
- `quick_add_component` layer resolution: use selected layer if valid; if invalid, find nearest valid layer and prefer inner on ties; if no selection, use innermost valid layer; HULL is never a quick-add target.
- Component movement uses remove + re-add of the same instance, preserving modifiers and state.
- `on_modifier_changed()` syncs multi-selection, recalculates ship stats, and emits events.
- Stats panel visibility is data-driven via `data/stats_sections.json` and `stats_config.py::resolve_section_visibility()`.

Use for complex screens. Put new mutation logic in controllers, derived state in view-models, and widget construction in renderers/builders.

## 9. Template Method Validation

Where: `game/simulation/validation/base.py` and validation modules.

Contract:
- Shared validation skeleton handles setup, result aggregation, and error shape.
- `ValidationRule.validate(...)` checks `_should_validate(...)` before calling `_do_validate(...)`.
- `DesignValidationRule` always runs; `AdditionValidationRule` runs for component/layer additions.
- Validation should return structured `ValidationResult` or raise specific exceptions according to the calling contract.

Use when multiple validators share setup, aggregation, and reporting behavior.

## 10. Event Bus

Where: `game/ui/screens/builder/event_bus.py`, `game/ui/screens/builder_utils.py::BuilderEvents`, `game/core/event_logging.py`.

Workshop event bus contract:
- Simple pub/sub with string event constants.
- `subscribe(event_type, callback)` validates the callback is callable.
- `emit(event_type, data=None)` passes exactly one `data` argument.
- `emit()` makes a defensive copy of handlers and isolates callback errors by logging.
- Use `BuilderEvents` constants such as `SHIP_UPDATED`, `SELECTION_CHANGED`, `REGISTRY_RELOADED`, `TEMPLATE_MODIFIERS_CHANGED`, `DRAG_STATE_CHANGED`, `HULL_LAYER_VISIBILITY_CHANGED`; do not use raw strings.
- Scoped to Workshop UI; not a general-purpose game event system.

Strategy/core event logging:
- `game/core/event_logging.py::EventBus` is separate structured event logging for simulation/strategy events.
- Each `GameSession` creates its own event bus to avoid process-global mutable state.
- Constructor injection is the only supported pattern: every event-emitting engine, handler, or data class takes an `event_bus: EventBus` parameter (or, for projectiles, an `event_logger=` callable that closes over a session-scoped bus). PROJ-390 retired the module-level `log_event()` / `set_event_handler()` / `get_event_handler()` compatibility shim — there is no fallback path.

## 11. Surface Caching

> **Last verified:** 2026-05-11 — PROJ-410: cross-context invalidation pattern added (`VirtualTable.invalidate_widget_caches`).

Where: `game/ui/renderer/sprites.py::SpriteManager`, `game/assets/asset_manager.py`, `game/assets/component_derivatives.py`, `game/ui/panels/race_flag_gallery.py`, `game/ui/panels/race_portrait_gallery.py`, `game/ui/panels/race_theme_gallery.py`, `game/ui/components/table/virtual_table.py`.

Contract:
- Cache loaded/scaled pygame surfaces by stable asset key and dimensions.
- `SpriteManager` loads 64px component sprites from `Paths.COMPONENTS_64_DIR` and parses `{resolution}Portrait_Comp_{number}.png` filenames; `tile_size = 36`.
- Use fallback/missing textures through asset managers rather than ad hoc loads.
- Component derivative images are generated/refreshed by asset tooling from the tracked 1024px source set.
- Individual UI panels may keep local `Dict[str, Surface]` caches with `invalidate_cache()` methods for rotated text and scaled surfaces.
- Cross-instance thumbnail caches use a module-level singleton + `_clear_thumbnail_caches()` reset hook (mirrors `ShipThemeManager.clear()`). Used by `RaceFlagGallery`, `RacePortraitGallery`, `RaceThemeGallery` so re-opening Setup Species reuses decoded thumbnails instead of re-scanning + re-decoding 28 × 2048-px portraits and 18 ship-theme thumbs every time.
- Do not cache color fills or line drawing; they are fast and position-dependent.

### Cross-context invalidation (PROJ-410)

When a cached widget pool is reused for *different content* (e.g. yard switch in `BuildQueueScreen`, where the pool widgets stay alive across yards/players to preserve PROJ-373 phase 3's `~1.5s` row-pool reuse perf win), expose a public `invalidate_widget_caches() -> None` method that:

- Nulls per-row/per-widget caches (`_last_text`, `_last_img`, `_last_color`).
- Sets a private `_data_identity_dirty: bool` flag.
- Does NOT call `.kill()` on any pool widget — `kill()` defeats the perf-lock that `TestRowPoolReuseGuard` enforces.

The flag is **ephemeral**: cleared at the end of the next `update_visible_rows()` re-render so subsequent frames keep the early-return optimization. Without this, every frame after invalidation re-renders all visible rows (~10–20% FPS drop).

Pair the invalidation method with a content-mutation hook in the renderer (`BuildQueueRenderer.refresh_queue_display()` calls it before `update_visible_rows()`) and a screen-lifecycle hook (`BuildQueueScreen.on_active_player_changed()` calls it on player change). The renderer hook handles per-mutation refreshes; the lifecycle hook handles cross-context boundaries (yard/player swap, save/load).

Canonical example: `VirtualTable.invalidate_widget_caches()` in `game/ui/components/table/virtual_table.py`.

Use for repeated image loads, component sprites, race/planet/star images, and generated derivatives.

## 12. Configuration Classes

> **Last verified:** 2026-05-08

Where: `game/core/config.py`, `game/strategy/data/*_config.py`, `game/ui/screens/builder_utils.py`, `game/strategy/config/economy_config.py`.

Contracts:
- Core config classes (`DisplayConfig`, `AIConfig`, `PhysicsConfig`, `BattleConfig`) are plain classes with class-level attributes. Do not add `@dataclass` decorators.
- UI layout config can use frozen dataclasses with singleton instances, e.g. panel width objects.
- Strategy data-driven configs load `data/astrophysics.json` through cached getters and `DEFAULT_*` dict fallbacks.
- JSON-backed config modules: `classification_config.py`, `resource_generation_config.py`, `star_generation_config.py`, `orbital_generation_config.py`.
- Config getters use `@lru_cache(maxsize=1)` and late-import `AstrophysicsLoader`; tests must call `get_*_config.cache_clear()` in setup/teardown when overriding data.
- Fallback catches expected load/shape failures (`ImportError`, file/OS errors, key/type/value errors) and returns defaults.

Three valid singleton-access flavors coexist:

1. **`@lru_cache(maxsize=1)` getters** — used by the JSON-backed configs above. Tests call `.cache_clear()` to swap.
2. **`DEFAULT_*` dict fallback** — module-level dict consulted when JSON load fails (e.g. `DEFAULT_CLASSIFICATION_CONFIG`).
3. **Module-accessor pair (`get_default_*` / `set_default_*`)** — a `_default = None` module variable plus paired accessors, currently used by `game/strategy/config/economy_config.py:136-149`. Justification (quoted from the file): "Chose this over `@lru_cache` (as used by `ClassificationConfig`) because CLAUDE.md's module-accessor form gives tests a clean swap API without poking `.cache_clear()`." PROJ-382 Phase 4 (audit U6) elevates this to a documented variant despite being below the usual 3-site bar — the in-code justification is explicit and the variant is intentional rather than accidental.

Use named config instead of inline magic numbers. Use JSON-backed config for gameplay tuning that designers/data should control.

## 13. Spec Compiler + `run_battle`

Where:
- Runner: `game/simulation/battle_runner.py::run_battle`.
- DTOs: `game/simulation/battle_spec.py`, `game/simulation/battle_outcome.py`.
- Compilers: `combat_lab/spec_compiler.py::build_test_battle_spec`, `game/ui/screens/battle_setup/spec_compiler.py::build_manual_battle_spec`, `game/strategy/combat/spec_compiler.py::build_strategy_battle_spec`.

Contract:
- Caller-specific compilers emit frozen `BattleSpec` DTOs.
- `run_battle(spec, ai_factory, ship_builder=None, registry_provider=None, ...) -> BattleOutcome` is the headless unified entry.
- Visual mode calls `BattleController.start_from_spec(...)`, which uses the same engine-start path as `run_battle`.
- If `ship_builder is None`, callers must pass `registry_provider`.
- Simulation layer must not resolve registry provider through globals.
- Every battle path emits `BattleOutcome`; visual mode obtains it through `controller.get_outcome()`.
- Variance lives on spec fields (`boundary`, `end_condition`, `modifier_stack`, `telemetry_level`, `post_battle_hook`) rather than a mode switch.
- Deleted stale system: do not revive `BattleModeHandler`, concrete mode handlers, `get_handler_for_mode(BattleMode)`, or duplicated engine materialization blocks.

Extension recipe:
- New battle context: create `build_*_battle_spec()` in the caller layer, then call `run_battle` or `BattleController.start_from_spec`.
- New cross-context variance: add a `BattleSpec` field and consume it from the engine.
- Context-specific post-battle side effect: attach `spec.post_battle_hook`.

## 14. Two-Phase Ability Aggregation

Where: `game/simulation/entities/ability_aggregator.py`, `ShipStatsCalculator`, component ability managers.

Contract:
- Phase 1 collects ability contributions across the ship.
- Numeric abilities aggregate as MAX within the same named `stack_group`, then SUM across different groups.
- Marker abilities (`CommandAndControl`, `Armor`, `RequiresCommandAndControl`, etc.) use boolean `True` semantics.
- Stack groups are defined in component JSON via `stack_group`.
- `FleetAuraManager._recalculate()` delegates to `_aggregate_ability_groups()`; new aggregation code should use the shared function.
- Phase 2 consumes totals to calculate final ship stats, preventing order-dependent behavior when one component affects another.

Use when an ability needs whole-ship context before final stat application.

## 15. Factory

Where: `game/ai/ai_factory.py`, `game/ui/services/ship_factory.py`, `game/ui/widgets/panel_factory.py`, LLM/image provider factories, registry factory modules.

Contract:
- Factory owns construction choices, default dependencies, and policy-based selection.
- Callers ask for the object they need instead of knowing all concrete collaborators.
- Factories pair well with tests when construction depends on registries, environment variables, display state, providers, or mode-specific policy.

Use where construction is conditional, dependency-heavy, or shared by production/tests.

## 16. ScrollState

Where: `game/ui/widgets/scroll_state.py`, tests in `tests/unit/ui/widgets/test_scroll_state.py`.

Contract:
- One helper owns scroll offset, bounds, viewport/content size, wheel delta, clamp behavior, and scroll ratio.
- Works for pixel-based scrolling and line-based scrolling.
- UI widgets read/write scroll state instead of reimplementing `scroll_offset` / `max_scroll` math.
- Do not use for camera zoom handling or pygame_gui scrollbar-driven scrolling.

Use for scrollable lists/panels.

## 17. Serializable Protocol

Where: `game/core/protocols/persistence.py`, tests in `tests/unit/core/test_serializable_protocol.py`.

Contract:
- `ISerializable` is a `@runtime_checkable` protocol for `to_dict()` / `from_dict()` and type checking.
- There is no mixin/base class; each implementor owns domain-specific serialization logic.
- Implementors include simulation state DTOs and `ShipInstance` via `game/strategy/data/ship_instance_serializer.py`.
- Corrupt persistence data should raise `PersistenceException` or a specific exception, not be swallowed.
- Save migrations are not required; old saves are disposable.

Use for save/load DTOs, replay DTOs, and domain persistence boundaries.

## 18. Per-Battle RNG

Where: `game/simulation/systems/battle_engine.py`, `game/engine/collision.py`, `game/simulation/combat/damage_calculator.py`, `game/ai/ai_factory.py`, `game/ai/controller.py`, `game/ai/behaviors.py`, `game/strategy/engine/conflict_resolution_engine.py`.

Contract:
- `BattleEngine.start_teams(..., seed=N, ...)` initializes `self.rng = random.Random(seed)`.
- The same RNG is injected into `CollisionSystem`, `DamageCalculator`, `AIControllerFactory`, `AIController`, and random AI behaviors such as `ErraticBehavior`.
- AI behaviors that need randomness take `rng` as a required keyword-only constructor argument and consume it via `self._rng`. `AIController._rng` forwards from `AIControllerFactory._rng`, ultimately `BattleEngine.rng`.
- Strategy conflict resolution owns its own `self._rng = random.Random()` (unseeded; separate from battle replay determinism) for empire pairing in multi-empire conflicts.
- Do not call `random.seed()` or module-level `random.*` from simulation, engine, or AI.
- Guard test: `tests/unit/quality/test_no_unseeded_random.py` forbids `random.<X>(...)` under `game/simulation/`, `game/engine/`, or `game/ai/` except `random.Random(...)`.
- A `# noqa: replay-determinism` allowlist marker exists for genuinely justified exceptions; none are expected.
- Determinism integration: `tests/integration/fleet_combat/test_battle_determinism.py::TestBattleStateHashRegression` asserts SHA-256 of canonical per-ship final state is equal across 5 repeated runs of the same seeded battle.

Use injected RNG for every combat random decision.

## 19. Error Boundary

Where: `game/strategy/engine/turn_engine.py`, `game/strategy/engine/turn_state_snapshot.py`.

Contract:
- `TurnStateSnapshot.capture()` serializes all empires + galaxy via `to_dict()` before processing a turn.
- `_time_phase()` wraps sub-engine failures as `EnginePhaseError`.
- `process_turn()` catches `EnginePhaseError`, restores the snapshot, writes a crash diagnostic file, and re-raises.
- `GameSession.process_turn()` catches `EnginePhaseError` for UI notification.

Use snapshot/rollback around multi-step strategy mutations that must be atomic. The snapshot/rollback shape is preferred to full transactional semantics when the state graph is complex.

## 20. Precondition Validation

Where: sub-engines under `game/strategy/engine/`.

Contract:
- Each mutating tick entry validates inputs up front through `_validate_tick_inputs(empires)` at the entry point of any method that mutates state.
- Checks for null references, missing attributes, and impossible values before any mutation.
- Raise `ValidationException` with `context={"empire_id": ..., "fleet_id": ...}` identifying the broken entity, not a cryptic `AttributeError`.
- Validate before any state mutation so pattern #19 can roll back cleanly with a useful error.

Use for engine phases, action execution, production, movement, hazards, and any new mutating sub-engine.

Skeleton:

```python
def _validate_tick_inputs(self, empires):
    from game.core.exceptions import ValidationException
    for empire in empires:
        for fleet in empire.fleets:
            if fleet.location is None:
                raise ValidationException(
                    f"Empire {empire.id}: fleet '{fleet.id}' has None location",
                    context={"empire_id": empire.id, "fleet_id": fleet.id},
                )
```

## 21. Screen State Machine

Where: `game/core/state_machine.py`, transition table in `game/app.py`.

Contract:
- `ScreenStateMachine` validates transitions against a declarative table.
- Supports guards, enter/exit callbacks, and stack-based return via `push_and_transition()` / `pop_and_return()`.
- `_switch_scene()` in `app.py` delegates transition validity to the state machine before changing the active scene.

Use for formal app/screen states and return-to-previous flows.

## 22. TurnEngineConfig

Where: `game/strategy/engine/turn_engine_config.py`, helper `tests/fixtures/turn_engine.py::build_test_turn_engine(...)`.

Contract:
- Frozen dataclass bundles 18 sub-engine dependencies: 15 tick-loop engines plus 3 end-of-turn terraforming engines.
- `TurnEngineConfig.create_default(registries, *, ai_factory=None, race_registry=None, event_bus=None)` is the canonical construction path and eagerly constructs default engines in one place.
- `TurnEngine.__init__` requires `config=...`; per-engine override kwargs are gone.
- Tests override specific engines via `dataclasses.replace(cfg, foo_engine=mock)`.
- Phase descriptor lists (`tick_phases`, `end_of_turn_phases`) remain separate constructor kwargs because they are descriptor tuples, not engine dependencies.
- Explicit `tick_phases=` / `end_of_turn_phases=` constructor kwargs win over registry defaults.
- Do not import engine classes inside `TurnEngine` methods. The lone allow-listed location for function-local engine imports is `TurnEngineConfig.create_default()`.
- Guard test: `test_no_lazy_fallback_init.py::test_no_function_local_engine_imports_in_TurnEngine_methods`.

Use for all turn-engine dependency construction and test substitution.

## 23. Tick Phase Registry

> **Last verified:** 2026-05-08

Where: `game/simulation/systems/tick_phase.py`.

Contract:
- `ITickPhase` has `name`, `priority`, and `execute(engine)`.
- `TickPhaseRegistry` executes phases ordered by ascending priority.
- Defaults (six phases — every name carries the `Phase` suffix):
  `RebuildGridPhase(100)`, `AIAndShipUpdatePhase(200)`,
  `BoundaryEnforcementPhase(250)`, `AttackProcessingPhase(300)`,
  `RammingPhase(400)`, `ProjectileUpdatePhase(500)`.
- `BattleEngine.update()` delegates to the registry.

Add simulation tick behavior by registering a phase at a deliberate priority.

## 24. External-Stats Bridge

Where: `game/simulation/entities/ship.py`, `game/simulation/combat/fleet_aura_manager.py`, `game/simulation/components/abilities/base.py`, `game/simulation/entities/ship_stats.py`.

Contract:
- Spec compiler `ModifierStack` entries aggregate through `FleetAuraManager._recalculate` into `ship.external_stats: dict[str, float]`.
- Ability-level consumers call `Ability.get_effective_stat(stat_key)`: `_mult` keys multiply local and external values; `_add` keys sum.
- Ship-level virtual stats such as `shield_bonus_add` are read in `_apply_aggregated_stats`.
- `external_stats` is battle-scoped and never serialized.
- Only `FleetAuraManager._apply_bonuses` populates it.
- Do not mutate `component.stats` from outside `Component._calculate_modifier_stats`.

Known limitation:
- Stack groups aggregate within a source only. Provider auras bucket by ability class name, while external `ModifierStack` entries bucket by stat key, so a provider `ShieldModifier` and an external `shield_capacity_mult` with the same stack group do not cross-compose via MAX.

Use for battle-scoped modifiers that should not mutate component stats or save data.

## 25. Scope-Driven Team Routing

Where: `game/simulation/combat/ability_stat_registry.py`, `game/ui/screens/battle_setup/spec_compiler.py`, `game/strategy/services/combat_modifier_collector.py`.

Contract:
- Ability `AbilityScope` decides recipient side.
- `fleet` / `allied_*` / `player_*` / `system` / `sector` route to the owner team.
- `enemy_sector` / `enemy_system` route to all non-owner teams.
- Suppressor vs booster is just multiplying by less than 1 vs more than 1; the scope is the routing mechanism, not a separate ability kind.
- `OPPONENT_SCOPES` is the single source of truth; compilers must not keep local duplicate scope sets.
- `emit_entries_for_ability(..., owner_team, num_teams, ...)` returns `(team_id, ModifierEntry)` pairs and handles N-team fan-out.
- For `num_teams == 2`, enemy fan-out is one opponent; for larger N, it emits one entry for every non-owner team.
- Strategy compiler may receive precomputed enemy effects from `CombatModifierCollector`; battle setup compiler delegates routing directly.

Use for any ability whose effects compile into `ModifierStack` entries. Extending `OPPONENT_SCOPES` requires tests proving routing across N-team fan-out.

## 26. Ability-Stat Registry

Where: `game/simulation/combat/ability_stat_registry.py`.

Contract:
- `ABILITY_STAT_REGISTRY` maps ability class name to `AbilityStatMapping(stat_key, operation, value_field)`.
- Current mappings include `ShieldProjection -> shield_bonus_add/add/value`, `ShieldModifier -> shield_capacity_mult/multiply/multiplier`, `DamageModifier -> damage_mult/multiply/multiplier`.
- `emit_entries_for_ability(ability_name, ability_data, *, scope, owner_team, num_teams, source, source_modifier_id, source_modifier_name, stack_group=None)` performs value extraction, team routing, N-team fan-out, and entry creation.
- Unknown abilities and zero values emit nothing.
- `KNOWN_EXTERNAL_STAT_KEYS` lists downstream-consumed stat keys; `FleetAuraManager` warns once per `(stat_key, source)` for unconsumed emitted keys.
- Consumers: `game/ui/screens/battle_setup/spec_compiler.py::_complex_to_entries`, `game/strategy/combat/spec_compiler.py::_emit_entries_team_scoped`.
- Guard tests in `tests/unit/simulation/combat/test_ability_stat_registry.py` iterate `data/designs/qs_*_complex.json` for placeholder keys and coverage.

To add a combat-affecting ability: add one registry entry, add the consumed stat key to `KNOWN_EXTERNAL_STAT_KEYS`, and rely on glob tests for quickstart complex coverage.

## 27. Budget-Aware Randomization

Where: `game/strategy/systems/race_randomizer.py`, `game/strategy/data/race_point_budget.py::RacePointBudget`.

Contract:
- Randomizers roll candidate aptitude/environment values.
- Cost is computed only through `RacePointBudget`, the same authority used by UI save validation.
- If over budget, move the most expensive value one step toward its free baseline until valid.
- Aptitude baseline is 50; environment preference baseline is the factor default tolerance. Setpoints are free and are not rebalanced.
- Tolerance-deviation cost is `_exponential_cost(steps) = 2**steps - 1`; aptitudes use the same exponential shape from the 50 baseline. Reproduction-rate cost is exponential above the 3% default and a linear refund (2 points per 1% step) below default down to a 0.5% floor (returns -5 exactly).
- `randomize_all` splits a 100-point budget between aptitude and environment slices using a per-run random fraction in `[0.3, 0.7]`.
- Environment generation may seed from a random `homeworld_presets.json` preset before per-factor jitter so randomized races are biologically coherent.
- Methods accept optional `random.Random` for deterministic tests; module-level `random` remains the production default for this strategy/UI randomizer.

Use when randomized output must satisfy a global budget. Skip for simple per-axis bounds.

## 28. Background Service Call

Where: `game/services/llm/background.py`, `game/strategy/services/race_description_llm_controller.py`, image background equivalents under `game/ui/services/image/`.

Contract:
- Background call object owns a non-daemon worker thread.
- Tracks status, result, error, and elapsed time.
- Cancellation sets an event checked between provider retries; in-flight HTTP completes in the background and is discarded logically.
- Shared state is guarded by an instance lock.
- Module-level counter enforces `LLMConfig.MAX_CONCURRENT_CALLS` (default 3); exceeding it raises `LLMConfigError`.
- `shutdown_all_calls(timeout=5.0)` joins workers before `pygame.quit()`.
- Worker exceptions are captured and surfaced through object state, not thrown only on the worker thread.
- Non-LLM exceptions escaping a provider are wrapped in `LLMUnexpectedError`; `CallStatus.ERROR` may carry it.
- Status reads are lock-protected so concurrent reads never observe torn state.

Reference consumer:
- `RaceDescriptionLLMController` owns two `LLMBackgroundCall` instances, translates `CallStatus` into a domain `FieldStatus`, exposes elapsed seconds for 30s/90s UI messaging, and is polled by the screen each frame.

Use for external provider calls that must not block UI but must complete or shut down cleanly. Do not use for fast in-memory/file operations, skip the concurrency limit, or daemon-thread workers.

## 29. Universal Ability Source

Where:
- Protocol: `game/core/protocols/strategy_entities.py::IAbilitySource`.
- Adapters: `game/strategy/services/ability_sources/`.
- Iterator: `game/strategy/services/ability_iterator.py`.
- Collector: `game/strategy/services/system_effects_collector.py`.
- Aggregation: `game/strategy/services/strategic_ability_scanner.py`.

Contract:
- Ability sources expose `source_kind`, `source_label`, `source_id`, `owner_id`, `get_abilities()`, `affects_hex()`, `affects_system()`, and activation state.
- Adapters include facility, storm, planet intrinsic, star, warp point, system, and fleet sources.
- Providers register via `register_source_provider_at_hex` / `register_source_provider_in_system`.
- Collector filters by owner and scope, groups compatible effects, then aggregates multipliers or rates.
- Multipliers aggregate intra-provider MAX and inter-provider MULTIPLY; rates aggregate intra-provider MAX and inter-provider SUM.
- Fleet providers are wired at session start through `set_fleet_lookups`.
- Validations reject mixed effect kinds in one group, ownerless ownership-aware scopes, and combat+strategic scopes on one ability instance.
- Adapter package must not call `get_default_registry_provider()`; static guard enforces layering.
- Overlapping storms multiply per provider; hostile star systems are deliberately uncapped and surfaced through hazard hints.

Use by adding an `IAbilitySource` adapter and provider for any new strategic entity that projects effects to a hex or system.

## 30. Registrar Close-Callback

Status: legacy slot cleanup pattern only. Modal tracking is superseded by pattern #31.

Where: `game/ui/screens/strategy_windows/`, `game/ui/screens/planet_abilities_window.py`, `game/ui/screens/planet_list_window.py`, `game/ui/screens/strategy_event_router.py`.

Contract:
- Legacy window registrars may still own convenience slots on `StrategyWindowManager`.
- Open path stores the window ref and passes an `on_close_callback`.
- Window `kill()` invokes callback before `super().kill()`.
- Callback clears the slot to avoid stale references.
- The `_handle_window_close` event-driven cleanup branch also clears several legacy slots on `UI_WINDOW_CLOSE`.
- New modal blocking behavior must not use this as the tracking mechanism.

Use only when maintaining existing slot cleanup. New strategy modal windows use `StrategyModalWindow`.

## 31. Strategy Modal Window Base Class

> **Last verified:** 2026-05-11 — issue #12: is_blocking flag for native hover suppression added; pygame-gui's `UIWindow.is_blocking=True` now suppresses background hover state in addition to clicks.

Where: `game/ui/screens/strategy_modal_window.py`, `game/ui/screens/strategy_window_manager.py`, tests in `tests/unit/ui/screens/test_strategy_modal_window.py` and `tests/integration/ui/test_editor_click_blocking.py`.

Contract:
- `StrategyModalWindow(UIWindow)` registers itself with `StrategyWindowManager.register_modal(self)` during construction when a manager is supplied.
- Constructor requires keyword-only `window_manager`; callers outside strategy screen may pass `window_manager=None`.
- `kill()` unregisters before calling `super().kill()`.
- `unregister_modal` is idempotent, so double `kill()` is safe.
- `StrategyEventRouter.has_modal_open()` and blocking-element checks iterate `window_manager.iter_live_modals()`.
- `iter_live_modals()` filters dead refs with `.alive()` and reaps orphan refs.
- `has_modal_open()` also checks retained pre-modal concerns such as `menu_panel` and `build_queue_screen`.
- Legacy slot fields remain as caller-convenience pointers; they no longer provide modal tracking.
- **Full modality (issue #12):** while any subclass instance is live, the strategy event router blocks ALL background clicks (hex grid AND top-bar buttons) regardless of click position relative to the window's rect. Specifically, `_is_blocking_ui_element_at` returns True whenever `iter_live_modals()` yields any window, and `_handle_button_pressed` early-returns whenever `has_modal_open()` is True. Do not re-introduce a rect-only path or a per-window opt-out flag; the rect-pass-through behavior was the source of bug class #12.
- **Native hover suppression (issue #12 scope-expansion):** the base class also sets `self.is_blocking = True` after `super().__init__()`. pygame-gui's `UIWindow.check_hover()` returns True unconditionally when `is_blocking`, propagating `hover_handled=True` to `UIManager._handle_hovering`. That suppresses hover dispatch on every lower-layer element — top-bar buttons, detail-panel context buttons, tree items — without any per-button retrofit. Hover is poll-based inside `UIManager.update`, not event-driven, so this is the only mechanism that addresses the hover leak; gating MOUSEMOTION at the strategy router has no effect. The MOUSEBUTTONDOWN consumption that `is_blocking` also enables runs in parallel with the manual click-block above; both defenses coexist.

Use for every new strategy-screen modal that should block input. Do not add manual slots, `has_modal_open()` clauses, custom modal `kill()` cleanup, or slot-based modal tracking.

## 32. Compositional Construction

Where: `game/ui/screens/strategy_screen_composition.py`, `game/ui/screens/strategy_screen.py`, `tests/fixtures/strategy_screen_composition.py`, `tests/unit/ui/screens/test_strategy_screen_composition.py`.

Contract:
- Define a `FooComposition` protocol/dataclass grouping collaborators.
- Production constructor accepts an optional composition factory and otherwise uses `DefaultFooCompositionFactory`.
- Factory exposes one `make_<thing>(self_ref)` method per stable collaborator slot.
- Tests pass a `Mock<Class>Composition` / null composition without bypassing `__init__`.
- Adding/renaming a slot is one edit in the protocol, default factory, and mock fixture, not repeated per test.
- Constructor stays cheap enough to wire collaborators before heavy widget creation.
- `MockStrategyScreenComposition.populate(screen)` exists for the remaining bypass-init path; direct construction can pass the mock composition as a kwarg.

Use for classes that construct three or more stable, heavy collaborators in `__init__`. Prefer this over `bypass_init` for new UI classes.

Skeleton:

```python
class StrategyScreenComposition(Protocol):
    def make_renderer(self, screen) -> StrategyRenderer: ...
    def make_camera_navigator(self, screen) -> CameraNavigator: ...
    # ... one per stable sub-object slot

class StrategyScreenCompositionFactory:
    def make_renderer(self, screen) -> StrategyRenderer:
        return StrategyRenderer(screen)
    # ...

class StrategyScreen:
    def __init__(self, ..., *, composition: StrategyScreenComposition | None = None):
        comp = composition or StrategyScreenCompositionFactory()
        self._renderer = comp.make_renderer(self)
        self._camera_nav = comp.make_camera_navigator(self)
```

## 33. UI Widget Test Factory

Where: `tests/fixtures/ui_widget_factory.py`, `tests/fixtures/test_ui_widget_factory.py`, per-class UI builder fixtures under `tests/fixtures/`.

Contract:
- `make_ui_widget(cls, extra_modules=(), **kwargs)` constructs a real instance while patching `pygame_gui.elements.UI*` classes with mocks.
- The factory patches the canonical `pygame_gui.elements` namespace and module-bound imports along the class MRO.
- It introspects `__init__` defaults for common kwargs such as panel, manager/ui_manager, container, and rect; caller kwargs override.
- For UIWindow subclasses, element-class patches are insufficient because `super().__init__()` resolves through the MRO. Use `bypass_init(cls)`.
- `bypass_init(cls)` is a context manager; never set `Cls.bypass_init = True` bare in tests.

Two-stage UIWindow shape:
- Stage 1 above bypass guard: pure-Python state, delegate factory wiring, builder seam setup. No pygame_gui widgets, no `self.get_container()`, no asset I/O.
- Guard: `if getattr(type(self), "bypass_init", False): return`. Use `type(self)` so inherited guards honor subclass flags.
- Stage 2 below guard: `super().__init__(...)` and heavy widget tree via UI builder.
- Use `Null{Foo}UiBuilder` when UI is irrelevant; use `Mock{Foo}UiBuilder` when asserting UI calls.

Use for legacy pygame_gui widget/unit tests. Use integration UI tests for real multi-widget event flow. Production never sets `bypass_init`.

Skeleton (two-stage `UIWindow` `__init__`):

```python
def __init__(self, ..., *, ui_builder=None, delegate_factory=None):
    # Stage 1 — pure-Python state + delegate factory wiring + UI-builder seam.
    # No pygame_gui widgets, no self.get_container(), no asset I/O.
    self._race_config = ...
    delegates = (delegate_factory or DefaultRaceSetupDelegateFactory()).build(self)
    self._controller = delegates.controller

    # Bypass guard — type(self) so subclass flags win.
    if getattr(type(self), "bypass_init", False):
        return

    # Stage 2 — heavy widget tree.
    super().__init__(...)
    builder = ui_builder or DefaultRaceSetupUiBuilder()
    builder.build(self)
```

Test invocation:

```python
from tests.fixtures.ui_widget_factory import bypass_init, make_ui_widget

with bypass_init(FleetReportWindow):
    window = make_ui_widget(FleetReportWindow, fleet=mock_fleet, ...)
```

Never set `Cls.bypass_init = True` bare in a test body — a crash mid-test leaks the flag to every subsequent test.

## 34. Weapon Family Registry

Where:
- Contract types: `game/simulation/combat/attack_contract.py`.
- Registry: `game/simulation/combat/weapon_registry.py`.
- Handlers: `game/simulation/combat/families/{beam,projectile,seeker,pdc}.py`.
- Consumers: `weapon_firing_system.py`, `targeting_system.py`, `game/engine/collision.py`.
- Acceptance test: `tests/unit/simulation/combat/test_weapon_registry.py::TestExtensibilityAcceptance`.

Contract:
- Each `WeaponFamily` registers one `WeaponHandler`.
- Importing `game.simulation.combat.families` triggers built-in registration.
- Firing flow: `detect_family(comp)` -> `AttackRequest` -> `WEAPON_REGISTRY.dispatch(request)` -> typed resolution.
- `BeamResolution` carries `source`, `component`, `target`, `damage`, `range`, `origin`, `direction`, `hit`, plus `type=AttackType.BEAM`.
- `ProjectileResolution` wraps a `Projectile`; `NoAttack` represents no fire.
- `FAMILY_METADATA` owns targeting policy flags such as missile targeting and PDC context.
- Engine collision consumes typed resolution attributes, not simulation dict keys.

To add a new family: add enum member, handler module implementing `WeaponHandler.fire`, metadata if needed, and import in `families/__init__.py`. Do not edit central firing/targeting/collision/projectile dispatch unless the shared contract itself changes.

## 35. Stat Contributor Registry

Where: `game/simulation/entities/stat_contributors/`.

Contract:
- `STAT_CONTRIBUTOR_REGISTRY` is the single Phase-3 stat aggregation pipeline.
- `ShipStatsCalculator._phase_stats_aggregation` iterates `STAT_CONTRIBUTOR_REGISTRY.iter_for(comp)` once per operational component.
- Built-ins are registered entries seeded after domain modules load with explicit `phase_order`: movement=10, defense=20, hangar=40, command=50.
- Modder entries default to `phase_order=99`, after non-replaced built-ins.
- `StatAccumulator` is a typed `slots=True` dataclass with 10 scalar fields and 4 named map fields; misspelled scalar/map fields raise.
- Dynamic resource keys (`max_<resource>`, `gen_<resource>`) live inside `acc.resource_storage` / `acc.resource_generation`.
- Conflict policies: `REPLACE_WARN`, `REPLACE_SILENT`, `APPEND`, `ERROR`.
- `REPLACE_*` entries suppress the underlying default while active; unregistering restores the default.
- `register_stat_contributor(...)` returns a `RegistrationHandle`; unregister by handle.
- Defaults cannot be unregistered by handle; `reset_stat_contributor_registry()` clears and re-seeds.
- `CREW_PRIORITY_REGISTRY` is separate and maps ability names to crew allocation priority.
- This registry is distinct from `combat.ability_stat_registry.ABILITY_STAT_REGISTRY`; the latter emits battle modifier entries, this one aggregates component stats.
- Acceptance tests: `tests/unit/simulation/entities/stat_contributors/test_registry_pipeline.py` and `tests/unit/simulation/entities/test_stat_contributor_extension.py`.

To add a recalculation-time stat ability: define a contributor taking `(ship, comp, accumulator)`, register it for the ability name with an explicit conflict policy, capture the handle, and reset/unregister in tests.

Boundary:
- Phase-5 helpers such as `weapons.aggregate_targeting_scores`, `defense.apply_armor_and_repair_scores`, and `defense.init_armor_pool` remain imperative after the Phase-4 physics boundary. Folding them into the registry requires a future design.

## 36. Re-Export Shim

> **Last verified:** 2026-05-08 (PROJ-396 MAJ-006: Pattern #5 facade-bypass prohibition added)

Where (4 confirmed sites at PROJ-382 verification, 2026-05-07):
- `game/ui/screens/race_setup_screen.py` (~31 LOC) — re-exports
  `RaceSetupScreen`, `RaceRandomizer`, `RaceBrowserDialog` from
  `game/ui/screens/race_setup/`.
- `game/ui/screens/test_lab/test_run_details.py` (~12 LOC) — re-exports
  `TestRunDetailsPanel` from `game/ui/screens/test_lab/details/`.
- `game/simulation/components/component.py:395-405` — re-exports
  loader symbols from `game/simulation/components/component_loader.py`.
- (Removed PROJ-383) `game/strategy/engine/command_handlers.py` —
  the transitional re-export shim is deleted; all callers import
  from `game/strategy/engine/handlers/base.py` directly.

Problem the pattern solves:
- A module is decomposed into a sub-package (or sibling module) but
  many existing imports still target the original path. Editing every
  importer in one PR enlarges the change footprint and complicates
  review/rollback. A thin re-export shim preserves the legacy import
  path while the canonical implementation moves.

Structure:
- The shim file is small (≤ ~30 LOC) and contains only `from <new
  path> import <name>` lines plus an `__all__` listing of the
  re-exported names.
- A header docstring identifies the canonical module and the project
  / migration that introduced the shim.
- Tests that exercise behavior import from the canonical module.

When to use:
- Decomposing a god-module into a sub-package mid-refactor.
- Renaming a module while letting downstream call sites migrate
  incrementally (e.g. across multiple PROJs).
- Promoting an internal symbol to a new canonical home without a
  hard, repository-wide rename pass in a single change.

When NOT to use:
- For "compatibility" with old save files or external API consumers
  outside the repo — Rule 3 (Root Cause Fixes) prohibits compat shims
  for either. Re-export shims are an internal-migration aid only.
- To paper over genuinely unmigrated state. The shim is a temporary
  scaffold tied to a tracked decomposition project; it does not
  legitimize a permanent two-path import surface.
- When the canonical home is uncertain. Decide before introducing the
  shim; otherwise the shim becomes a permanent fixture.
- To create a public import surface that bypasses a Facade
  (Pattern #5). PROJ-382 Phase 1 specifically eradicated facade-bypass
  paths from `BuildQueueScreen` and `EmpireBuildQueueWindow`; a
  re-export shim that exposes internal delegate symbols the Facade
  is supposed to hide reopens the same hole under a new name.
  Facade-bypass sites must route through the Facade — never through a
  re-export shim, a renamed kwarg (e.g. `portrait_session=`), or any
  other indirection that re-exposes the underlying session/object.

Retirement:
- Each shim should reference the project responsible for migrating
  its callers (e.g. PROJ-302 for race_setup; PROJ-383 retired the
  former command_handlers shim).
- When the legacy import path has zero remaining call sites under
  `game/`, delete the shim file in the same PR that removes the last
  caller. Audit guard: a periodic grep for shim contents is the
  current detection mechanism; a future audit may add a static check.

## Critical Naming Reminders

- Ship inherits `(PhysicsBody, ShipPhysicsMixin)` — there is no `ShipCombatMixin`.
- Config classes in `game/core/config.py` are plain classes, not dataclasses.
- Use `BattleScreen` / `StrategyScreen`, not `BattleScene` / `StrategyScene`.
- Use `VehicleDesignService`, not `ShipBuilderService`.
- `PolicyManager` lives at `game/ai/policy_manager.py`.
- Workshop `EventBus` lives at `game/ui/screens/builder/event_bus.py`; it is distinct from `game/core/event_logging.py::EventBus` used by simulation/strategy logging.
- Galaxy/Planet/Star read protocols (`IGalaxySystemGraph`, `IGalaxySpatialQuery`, `IHabitabilityCalculator`, `IStockpileHolder`, `IStagingYardHolder`) live at `game/strategy/data/galaxy_protocols.py`, beside the data classes; the cross-layer protocol package is `game/core/protocols/`.
- Mutator protocols (`IFleetMutator`, `IPlanetMutator`, `IEmpireMutator`, `IShipInstanceMutator`) live at `game/core/protocols/strategy_mutators.py`.

## Quick File/API Reminders

- `ApplicationContext`: `game/context.py`.
- Registry provider: `game/core/registry.py::DefaultRegistryProvider`, `TestRegistryProvider`, `get_default_registry_provider`.
- Protocols: `game/core/protocols/`.
- Strategy facade: `game/strategy/facade/strategy_session_facade.py`.
- Battle runner: `game/simulation/battle_runner.py::run_battle`.
- Battle spec/outcome DTOs: `game/simulation/battle_spec.py`, `game/simulation/battle_outcome.py`.
- Ability stat registry: `game/simulation/combat/ability_stat_registry.py`.
- Weapon registry: `game/simulation/combat/weapon_registry.py`.
- Stat contributor registry: `game/simulation/entities/stat_contributors/registry.py`.
- Universal ability source adapters: `game/strategy/services/ability_sources/`.
- Strategy modal base: `game/ui/screens/strategy_modal_window.py`.
- UI widget factory: `tests/fixtures/ui_widget_factory.py`.
- Turn config: `game/strategy/engine/turn_engine_config.py`.
- Tick phases: `game/simulation/systems/tick_phase.py`.

## Extension Checklist

- New battle launch: compile `BattleSpec`; call `run_battle` or `BattleController.start_from_spec`; pass `registry_provider` when no ship builder is supplied.
- New strategic effect source: implement `IAbilitySource`, register source provider, add owner/scope validation tests.
- New combat modifier ability: register in `ABILITY_STAT_REGISTRY`, update `KNOWN_EXTERNAL_STAT_KEYS`, add tests through quickstart complex coverage.
- New weapon family: add handler and metadata, register via family module import, keep central systems unchanged.
- New recalculation stat contributor: use `register_stat_contributor`, typed `StatAccumulator`, explicit conflict policy, and handle cleanup.
- New turn sub-engine: add dependency to `TurnEngineConfig.create_default`, add/adjust phase descriptor, validate preconditions before mutation.
- New strategy modal: subclass `StrategyModalWindow` and require keyword-only `window_manager`.
- New complex UI class: use Compositional Construction; for legacy UIWindow tests only, use scoped `bypass_init`.
- New registry consumer in simulation: inject provider/registries; never call global registry lookup.
- New random behavior in combat/AI/engine: accept and use injected `random.Random`; add determinism coverage if behavior affects outcomes.

## Guard And Test Anchors

- Registry/global lookup guard: simulation must not call `get_default_registry_provider()`.
- Mutation boundary guard: `tests/unit/strategy/data/test_mutator_boundary_ast_guard.py`.
- Facade thinness guard: `tests/unit/strategy/data/test_no_method_body_over_5_loc.py`.
- Command tuple regression: `tests/unit/strategy/engine/test_no_specs_tuple_literal.py`.
- RNG guard: `tests/unit/quality/test_no_unseeded_random.py`.
- Battle determinism: `tests/integration/fleet_combat/test_battle_determinism.py`.
- Scroll utility: `tests/unit/ui/widgets/test_scroll_state.py`.
- Serializable protocol: `tests/unit/core/test_serializable_protocol.py`.
- Modal base contracts: `tests/unit/ui/screens/test_strategy_modal_window.py`, `tests/integration/ui/test_editor_click_blocking.py`.
- Weapon family extensibility: `tests/unit/simulation/combat/test_weapon_registry.py::TestExtensibilityAcceptance`.
- Stat contributor registry: `tests/unit/simulation/entities/stat_contributors/test_registry_pipeline.py`, `tests/unit/simulation/entities/test_stat_contributor_extension.py`.
