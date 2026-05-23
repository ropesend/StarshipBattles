# 02_PATTERNS Compact Agent Reference

> **Last verified:** 2026-05-20 — PROJ-467 foundation doc-drift sweep: fixed Pattern #6's `commands.py` → `commands/` package path and reworded Pattern #4's "data/classes/callables" to "data, classes, or callables" (value kinds, not a directory). Earlier (2026-05-18): PROJ-436 Phase 10 doc refresh: added Pattern #43 (Unified Container Substrate); updated Pattern #38 (CarriedVehicle Substrate) and Pattern #41 (Polymorphic Order Issuer) to reflect the Phase 9 deletion of `_CarriedItemsProxy` + `ShipInstance.carried_items` (typed `BayInventory.bay` slot is the canonical write surface). Earlier: source doc last verified 2026-05-17.

Balanced compact derivative of `docs/02_PATTERNS.md` and
`AgentCoordination/Scratchpad/reports/02_PATTERNS_ALT_compact.md`.
This version removes release-note archaeology, preserves current
contracts and extension recipes, and the current pattern count is 43.
Patterns #37, #38, #41 came from the PROJ-FMS series + Round 4 QA:
group-kind discriminator, CarriedVehicle substrate, polymorphic
`IIssuerAdapter`. Patterns #39 (typed-sidecar extensions on frozen
DTOs) and #40 (named pre-tick setup registry) came from PROJ-426
(TD-01) and replace the prior `_compose_setup_callbacks` +
`object.__setattr__(spec, ...)` side-channel pattern. Pattern #43
(unified Container substrate) came from PROJ-436 alongside the
deletion of `VALID_CARGO_TYPES` (Phase 7),
`ProductionEngine.context_type` storage dispatch (Phase 8), and the
`_CarriedItemsProxy` test shim (Phase 9).

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
| 4 | Registry | Stable keys map to data, classes, or callables; avoid switch statements and hardcoded type lists. |
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
| 36 | Re-Export Shim | Thin module shim preserves a legacy import path during decomposition; tied to a tracked migration project. |
| 37 | Typed `DeployedGroup` Family (sibling of `Fleet`) | `Empire.deployed_groups: list[DeployedGroup]` (`MineGroup` / `FighterWing` / `SatelliteConstellation`) holds deployable battlefield assets as concrete typed dataclasses, NOT `Fleet`s. The fleet-action surface (Move / Warp / Build / Join) is structurally unreachable because the methods don't exist on `DeployedGroup`. Replaces the retired `Fleet.group_kind` string discriminator + `_reject_if_non_fleet_group` guard (PROJ-431 / TD-10). |
| 38 | CarriedVehicle Substrate | `VehicleBayAbility` (`capacity_mass`, `allowed_types`) plus the `CarriedVehicle` payload and shared `carried_vehicle_to_ship_instance` helper carry design-backed vehicles through bay storage, strategic launch / recovery, and end-of-battle reboard. |
| 39 | Typed-Sidecar Extensions on Frozen DTOs | A frozen cross-layer DTO (e.g. `BattleSpec`) is paired with a typed extensions dataclass (`BattleSpecExtensions`) inside a wrapper (`StrategyBattleAssembly`) constructed by a single orchestrator. Replaces the `object.__setattr__(frozen_dto, "_attr", ...)` side-channel anti-pattern eliminated by PROJ-426 (TD-01). |
| 40 | Named Pre-Tick Setup Registry | `PreTickBattleSetupRegistry` chains battle-setup closures (`mine_setup`, `reboard_setup`, etc.) by string name in registration order. `composed_callback()` returns the single `run_battle(..., pre_tick_loop_callback=...)` callable or `None` when empty. Independent subsystems register their own setup without coupling to others or fighting for the single hook slot. |
| 41 | Polymorphic Order Issuer (`IIssuerAdapter`) | Order handlers accept an `IIssuerAdapter` protocol (`FleetShipIssuerAdapter` / `PlanetStagingYardIssuerAdapter`) instead of a concrete `(Fleet, ShipInstance)` pair, so a single handler family serves both fleet-ship and planet-facility issuers; `ActionExecutionEngine` ticks both `fleet.orders` and `planet.orders`. |
| 42 | Bootstrap-State Single Assignment Path | One frozen-dataclass payload (`SessionBootstrapState`) backs both fresh construction and rehydration; one private `_apply_bootstrap_state(state)` method is the only place that mutates `self` from state. Canonical example: `GameSession`. Eliminates the PROJ-396 CRIT-002 service-wiring drift surface. |
| 43 | Unified Container Substrate | `Container(capacity_mass, policy, resources, items, population)` is one mass-priced storage abstraction with three internal slices and one `ContainerPolicy` filter. Used directly by `BayInventory` (typed four-slot widening: `bay`, `pods`, `resources`, `population`); production-engine read/consume goes through the narrower `IProductionResourceSource` Protocol satisfied by both `Planet` and `Fleet` via polymorphic delegators. Replaced the three pre-PROJ-436 storage abilities (`ResourceStorage`, `CargoStorage`, `VehicleBay`) and eight legacy entity-level storage fields. |

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
- Canonical lazy-default DI seams on engine processors (test-substitution targets): `SuperweaponOrderProcessor.__init__(event_bus=, empire_mutator=, nav_service=, validator=)` — each kwarg defaults to `None` and lazy-instantiates the canonical service in a `_get_*` helper. Tests inject stubs via the constructor rather than patching the underlying class methods (PROJ-493).

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

### Read-path policy (PROJ-472)

The `StrategySessionFacade` enforces the **write** path (commands route through
`facade.handle_command(...)` / `facade.commands.<verb>(...)`, guarded by
`tests/static_guards/test_facade_bypass_guard.py`). The **read** path is governed
by **option (b): a documented UI-safe read surface enforced by a static guard +
an exact allowlist + convention** — NOT a blanket "all UI reads become facade
DTOs" rule. The blanket rule does not fit: many `game/ui` imports of
`game.strategy` are pre-session config/value/enum reads, render-hot reads, or
editor surfaces that a DTO rule would churn without boundary value.

Convention:

- **Use the facade** for session-owned, mutation-adjacent, or
  cross-screen-cached reads (build queues, fleet/colony state, registries,
  turn number, path projections). The facade already exposes grouped read
  namespaces and frozen DTOs for these (`empires.build_queues`,
  `fleets.get`/`path_projection`, `FleetInfo`, `BuildQueueSourceDTO`, …).
- **A documented UI-safe surface is allowed** for immutable-ish
  config/value/enum/protocol types and static-data loaders/queries that exist
  before (or independent of) a live `GameSession`. The UI-safe types are:
  `GameConfig` (and the `game_config` scalars/`PlayerConfig`), `RaceConfig`
  (and its label tuples), `EnvironmentalPreference`, `HabitabilityFactor` (and
  the `habitability_factors` iterators), `ContainableKind`, `ActivationPhase`,
  `ComponentActivationState` (a detached `@dataclass` of a phase enum + scalar
  tick counters — no live session ref), the pre-session race-setup helpers
  `RacePointBudget` (the cost authority shared with UI save validation) and the
  `homeworld_presets` loaders/applicators (`load_homeworld_presets`,
  `apply_preset_to_config`, `get_preset_for_planet_type`,
  `get_preset_id_from_name`), the pure enums `OrderType`, `PlanetType`,
  `BattleRole`, and `FieldStatus`, the detached `CombatPolicy` scalar dataclass,
  the cached static-config getter `get_default_economy_config` (NOT the mutating
  setter), and the static ability/superweapon metadata `StrategicKind`,
  `abilities_with_kind_tag`, `SUPERWEAPONS`. Membership is a property of the
  **symbol**, not the file — so a tooling screen may import a UI-safe enum while
  its live/generation imports stay transitional. The guard enforces this
  surface as symbol-level `(module, member)` data in `_UISAFE_SYMBOLS`
  (`tests/static_guards/test_facade_read_path_imports_guard.py`), kept in lockstep
  with the canonical token block below by a doc<->guard parity test. The
  canonical token block — one `module.member` per line — is the **machine-checked
  source of truth**; neither it nor `_UISAFE_SYMBOLS` may drift from the other:

  <!-- PROJ-474 UISAFE canonical token list: parsed by
       tests/static_guards/test_facade_read_path_imports_guard.py
       (test_uisafe_symbols_match_pattern5_token_list). One module.member per
       line. Keep in sync with _UISAFE_SYMBOLS — the parity test fails on drift. -->
  <!-- PROJ-474 UISAFE canonical token list -->
  ```
  game.strategy.engine.game_config.DEFAULT_SYSTEM_COUNT
  game.strategy.engine.game_config.GameConfig
  game.strategy.engine.game_config.PlayerConfig
  game.strategy.engine.game_config.THEME_DEFAULTS
  game.strategy.engine.game_config.MAX_SYSTEM_COUNT
  game.strategy.engine.game_config.MIN_SYSTEM_COUNT
  game.strategy.engine.game_config.VALID_GALAXY_TYPES
  game.strategy.data.environmental_preference.EnvironmentalPreference
  game.strategy.data.habitability_factors.iter_gas_factors
  game.strategy.data.habitability_factors.iter_scalar_factors
  game.strategy.data.homeworld_presets.apply_preset_to_config
  game.strategy.data.homeworld_presets.get_preset_for_planet_type
  game.strategy.data.homeworld_presets.get_preset_id_from_name
  game.strategy.data.homeworld_presets.load_homeworld_presets
  game.strategy.data.race_config.RaceConfig
  game.strategy.data.race_config.GOVERNMENT_ORGANIZATIONS
  game.strategy.data.race_config.GOVERNMENT_TYPES
  game.strategy.data.race_config.LEADER_TITLES
  game.strategy.data.race_config.PHYSICAL_TYPES
  game.strategy.data.race_config.SOCIETY_TYPES
  game.strategy.data.race_point_budget.RacePointBudget
  game.strategy.data.containable.ContainableKind
  game.strategy.data.component_activation_state.ActivationPhase
  game.strategy.data.component_activation_state.ComponentActivationState
  game.strategy.data.order_types.OrderType
  game.strategy.data.planet.PlanetType
  game.strategy.data.fleet_hierarchy.BattleRole
  game.strategy.data.fleet_hierarchy.CombatPolicy
  game.strategy.config.economy_config.get_default_economy_config
  game.strategy.services.race_description_llm_controller.FieldStatus
  game.strategy.services.ability_metadata.StrategicKind
  game.strategy.services.ability_metadata.abilities_with_kind_tag
  game.strategy.services.superweapon_registry.SUPERWEAPONS
  ```
- **A tooling-exemption category covers detached editor/sandbox/authoring
  imports.** Some tooling, editor, and sandbox screens import `game.strategy.*`
  symbols that are neither facade-routed live reads nor pure UI-safe symbols:
  they are detached pre-session editors that construct/mutate real domain
  objects before any session exists (`battle_setup` holds real
  `Fleet`/`ShipInstance`/`TaskForce`/`Squadron`), standalone sandbox harnesses
  that build their OWN world for inspection (`galaxy_test` constructs its own
  `Galaxy`/`StarSystem` via generation), pre-session authoring services
  (`race_setup`'s `RaceLibrary`/`RaceRandomizer`/`RaceCaptionLoader`/
  `RaceDescriptionLLMController`), and design-editor metadata/catalog loaders
  (`get_default_design_role_registry`, browse-time `DesignCatalog`). None reads
  a live `GameSession`, so facade migration is the wrong tool; but they are
  **not** immutable pure symbols either (`RaceLibrary` orchestrates the
  filesystem, `get_default_design_role_registry` lazy-loads a mutable
  base/mod/user overlay, `RaceDescriptionLLMController` is a live state machine,
  the battle-setup models are mutable real domain objects), so promoting them to
  the UI-safe surface would silently widen the always-safe policy. They earn a
  first-class, machine-checkable **`_TOOLING_EXEMPTIONS`** entry instead: an
  exact `(file, module, member)` triple plus a `category_tag` and a one-line
  reason (in `tests/static_guards/test_facade_read_path_imports_guard.py`). This
  is **exact-triple scoped, NOT a folder/subpackage waiver** — the tooling dirs
  mix promotable pure symbols with these genuine tooling imports, so the guard
  stays active everywhere and a net-new live import in a tooling dir is still
  flagged (a positive-control test pins this). The boundary: live-session /
  service readers stay facade-routed (PROJ-475/477); pure value/enum/static
  symbols are UI-safe (PROJ-474, the token list above); these detached tooling
  imports are tooling-exempt. The four category tags are the machine-checked
  source of truth (a doc<->guard parity test fails on drift):

  <!-- PROJ-476 tooling-exemption canonical tag list: parsed by
       tests/static_guards/test_facade_read_path_imports_guard.py
       (test_tooling_exemption_tags_match_pattern5). One tag per line. Keep in
       sync with the tags used in _TOOLING_EXEMPTIONS — the parity test fails on drift. -->
  <!-- PROJ-476 tooling-exemption canonical tag list -->
  ```
  prebattle-editor
  sandbox-harness
  race-authoring
  design-editor
  ```
- **Do NOT allowlist live session/domain traversal helpers** just because they
  are "read-only". The counterexamples — explicitly NON-allowlisted — are
  `BuildQueueSource`, `collect_build_queues_at_hex` /
  `collect_all_build_queues_for_empire`, `FleetCapabilityCalculator`,
  `GameSession`, strategy mutators, and `turn_engine`-shaped helpers. They return
  mutable owner references / live queue lists, which is exactly what the facade
  exists to hide.

Two static guards enforce this over `game/ui/**/*.py` (both ignore
`if TYPE_CHECKING:` imports):

- `tests/static_guards/test_facade_read_path_imports_guard.py` — runtime-import
  guard. Always allows `game.strategy.facade.*` and
  `game.strategy.engine.commands` (the write path). Fails on any other runtime
  `game.strategy.*` import not on an **exact** `(file, module, member)`
  allowlist (no subpackage wildcards — the codebase is too mixed for
  `game.strategy.data.*` to be blanket-safe).
- `tests/static_guards/test_facade_read_path_session_guard.py` — session-read
  guard. Matches `<expr>.session.<attr>`, `<expr>._session.<attr>`, and the full
  `<expr>.facade_state.session.<attr>` chain. Allowlisted by
  **file + attribute-path + reason**, not by bare attribute name.

**Honest scope note (transitional surfaces, not yet closed):** Phase 1 tightens
the read path (blocks net-new bypasses) but does NOT seal it. `StrategyScreen`
keeps documented transitional pass-through properties — `galaxy`, `empires`,
`systems`, `active_empire`, `enemy_empire`, `human_player_ids`
(`game/ui/screens/strategy_screen.py`) — and `FacadeSessionState` still publicly
holds `session`. These remain **allowlisted-with-reason** as transitional read
surfaces; deprecating them (plus the ~75-file `game/ui` tail) is follow-on work
(PROJ-474 value/config allowlist consolidation, PROJ-475 remaining live readers +
pass-through deprecation, PROJ-476 tooling/editor screens — the latter now
codified as the `_TOOLING_EXEMPTIONS` category above rather than parked in
`TAIL`). Do not read the guards as evidence the read path is fully closed.

## 6. CQRS-lite Strategy Session

Where: `game/strategy/facade/`, DTOs under `game/strategy/facade/dto/`, commands under the `game/strategy/engine/commands/` package.

Contract:
- Writes go through command DTOs and command handlers, usually via `facade.handle_command(...)` or the grouped `facade.commands.<verb>(...)` namespace (TD-08; prefix-stripped command helpers, registry-driven).
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
- Post-TD-08: `StrategySessionFacade` no longer installs top-level `dispatch_*` methods. The `FacadeCommands` grouped namespace (`facade.commands`) accepts `(helper_name, command_class)` pairs from `command_registry.specs_by_facade_helper()` at facade construction; each verb is the legacy helper name with the `dispatch_` prefix stripped. The dispatch slice's `__getattr__` still resolves the helper closure per call.
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

Where: `game/ui/screens/builder/event_bus.py::WorkshopEventBus`, `game/ui/screens/builder_utils.py::BuilderEvents`, `game/core/event_logging.py::EventBus`.

There are **two distinct event-bus classes** with deliberately separate domains; the name divergence is intentional (PROJ-382 naming hygiene), not drift:
- `WorkshopEventBus` (`game/ui/screens/builder/event_bus.py`) — Workshop / build-queue **UI** pub/sub.
- `EventBus` (`game/core/event_logging.py`) — session-scoped structured **simulation/strategy** event logging.

They do not share an `EventBusProtocol`; their payload contracts differ (one-arg `data` callback vs structured logging records) and they serve non-overlapping scopes, so a shared protocol is not planned. Renaming the UI bus to `WorkshopEventBus` (PROJ-382 Phase 2) removed the import ambiguity that the shared `EventBus` name created.

`WorkshopEventBus` contract:
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

> **Last verified:** 2026-05-12 — issue #17 follow-up: `invalidate_widget_caches()` now also hides each `row["bg"]`, and `BuildQueueScreen.show()` re-runs `force_update() + update_visible_rows()` after `panels.background.show()` so the per-row visibility invariant survives pygame_gui's recursive un-hide. PROJ-411 Phase 1 extension: per-turn UI caches on `FacadeSessionState` for data-gathering panels (planet/star/design/economy snapshots), cleared by `FacadeSessionState.invalidate_all()` from `StrategySessionFacade.process_turn`. PROJ-411 Phase 2 added: window-reuse for strategy modals (`hide()` instead of `kill()`; instance preserved across opens). PROJ-411 Phase 3 added: `StarshipUIAppearanceTheme` subclass with tuple-keyed `_combined_ids_cache` working around pygame_gui 0.6.14's pathological `build_all_combined_ids` cache key.

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
- **Clears the widget content too** — `UILabel.set_text("")` on labels, `UIImage.set_image(blank_surface)` on images (issue #17). Cache-attr nulling alone is insufficient: pygame_gui's `UIPanel.show(show_contents=True)` calls `panel_container.show(True)`, and `UIContainer.show(True)` iterates every child and calls `.show()` on it unconditionally — regardless of each child's prior individual `visible` state. So any stale text/image left on a pool row that `update_visible_rows()` individually hid will re-appear on the next `panel.show()`.
- **Hides each row's background panel** — `row["bg"].hide()` (issue #17 follow-up). Content-clearing addresses stale text/portrait BUT leaves the row-pool widgets (action buttons `+ – ^ v`, the blank portrait `UIImage`, labels) visible. With an empty active queue (`row_count == 0`) every pool row goes through the `else` (hide) branch in `update_visible_rows()` — but the subsequent `BuildQueueScreen.show()` → `panels.background.show()` un-hides every descendant again via the same recursive contract. `UIPanel.hide(hide_contents=True)` recursively hides every child of the row background, so one `row["bg"].hide()` per row suffices.
- Sets a private `_data_identity_dirty: bool` flag.
- Does NOT call `.kill()` on any pool widget — `kill()` defeats the perf-lock that `TestRowPoolReuseGuard` enforces.

The flag is **ephemeral**: cleared at the end of the next `update_visible_rows()` re-render so subsequent frames keep the early-return optimization. Without this, every frame after invalidation re-renders all visible rows (~10–20% FPS drop).

Pair the invalidation method with a content-mutation hook in the renderer (`BuildQueueRenderer.refresh_queue_display()` calls it before `update_visible_rows()`) and a screen-lifecycle hook (`BuildQueueScreen.on_active_player_changed()` calls it on player change). The renderer hook handles per-mutation refreshes; the lifecycle hook handles cross-context boundaries (yard/player swap, save/load).

**Screen-level show() override (issue #17 follow-up):** any screen that calls `panel.show()` on a container above the row pool must re-assert per-row visibility AFTER the show, because pygame_gui's recursive `UIContainer.show(True)` un-hides descendants regardless of their prior individual visibility. The canonical pattern is:

```python
def show(self) -> None:
    if self.panels is not None:
        self.panels.background.show()
        self.panels.virtual_table.force_update()
        self.panels.virtual_table.update_visible_rows()
        self.manager.update(0)
```

`force_update()` resets `_last_scroll_pct`/`_last_row_count` so `update_visible_rows()` cannot early-return on the unchanged tuple. PROJ-373 perf-lock and PROJ-410 ephemeral dirty flag are both preserved — `force_update()` only mutates dirty-tracking scalars and `update_visible_rows()` uses hide/show/set_text/set_image, not `.kill()`. Canonical example: `BuildQueueScreen.show()` in `game/ui/screens/build_queue_screen.py`.

Canonical example: `VirtualTable.invalidate_widget_caches()` in `game/ui/components/table/virtual_table.py`.

Use for repeated image loads, component sprites, race/planet/star images, and generated derivatives.

### Per-turn UI caches on `FacadeSessionState` (PROJ-411 Phase 1)

For panels whose data is stable within a single turn (Galactic Planet Registry, Galactic Star Registry, Empire Overview, Build Queue), thread a `facade_state: FacadeSessionState | None` kwarg through the data-gathering function. Cache shape lives on the slice at `game/strategy/facade/slices/_facade_state.py`:

- `designs_by_empire: Dict[int, List[DesignMetadata]]`
- `planets_for_empire_cache: Dict[int, list]`
- `stars_cache_new: Optional[list]`
- `empire_economy_snapshot: Dict[int, Any]`

`FacadeSessionState.invalidate_all()` clears every PROJ-411 slot and is called from `StrategySessionFacade.process_turn` post-turn-advance. Functions check the cache first and fall back to a fresh gather when the slot is empty or `facade_state` is `None` (the latter is the test stub / non-strategy path — uncached behavior preserved).

### Window reuse for strategy modals (PROJ-411 Phase 2, extended by issue #28)

Galactic Planet Registry, Galactic Star Registry, Empire Overview, Event Log, Empire Build Queue, Fleet Report subclass `StrategyModalWindow` and override `on_close_window_button_pressed` + `request_close` to call `self.hide()` instead of `self.kill()`. `StrategyModalWindow.hide()` consolidates: `is_blocking=False`, unregister from window manager, remove from pygame_gui's `UIWindowStack`. `show()` mirrors. Registrars branch on `existing.alive()`: hit calls `existing.open_for_X(...)` rebinding context; miss constructs fresh. Re-open cost drops from 3–5 s to <500 ms.

Issue #28 extended this from same-empire reuse to **cross-empire reuse**. Empire Build Queue (`open_for_empire(empire, galaxy)`) and Empire Overview (`open_for_empire(empire)`) rebuild per-empire data in place when the empire differs: Empire Build Queue calls `viewmodel.update_sources(new_sources)`; Empire Overview re-fetches the economy snapshot, calls `EmpireTreasuryPanel.refresh(snapshot)`, invalidates the lazily-built Population tab, and rebinds `self.empire`. Fleet Report uses `open_for_fleet(fleet, empire=)` which is a thin rebind + `refresh_list()` since its content is fleet-keyed, not empire-keyed.

### Per-player UI view-state (issue #28)

Per-player view-state (column visibility, sort selection, expanded tab indices, scroll positions) is partitioned by `empire.id` via `PerPlayerUiState` in `game/ui/screens/per_player_ui_state.py`, owned by `StrategyGameStateManager`. Windows opt in by exposing three class-level / instance attributes:

- `SNAPSHOT_SLOT: str` — registry key. Current slots: `"planet_list"`, `"star_list"`, `"empire_build_queue"`, `"empire_panel"`, `"fleet_report"`, `"event_log"`.
- `capture_view_state() -> dict` — produces a serialisable snapshot.
- `apply_view_state(state: dict | None) -> None` — restores; `state is None` means "no saved state, use defaults".

`StrategyWindowManager.iter_snapshot_windows()` is the registry — it walks the slot attributes (`planet_list_window`, `star_list_window`, etc.) and filters to non-`None`, alive instances exposing `SNAPSHOT_SLOT`.

The capture/restore hooks in `StrategyGameStateManager`:

- **Capture** runs at the head of `advance_turn` via `_capture_outgoing_player_state` BEFORE `_next_live_player_index` mutates `current_player_index` (otherwise capture writes to the incoming player's slot).
- **Restore** runs at the TOP of `_apply_turn_start_state` via `_restore_incoming_player_state` BEFORE issue #25's defeat short-circuit (so a defeated empire's defeat modal and last-turn event log surface against the player's own saved view).

Lifecycle: session-scoped, not serialised — symmetric with #25's `_defeated_player_ids`. Defeated empires' snapshots remain in the container indefinitely (cheap, safe if a save reload revives them). Anti-reversion: single source of truth — do NOT reintroduce per-window `_filter_snapshots_by_empire` dicts.

### pygame_gui theme-id cache key (PROJ-411 Phase 3)

`game/ui/pygame_gui_patch.py::StarshipUIAppearanceTheme` overrides `build_all_combined_ids` to use a private tuple-keyed `_combined_ids_cache`, working around pygame_gui 0.6.14's pathological chained-`str.join` cache key (~10 KB per call). Source-fingerprint guard `UPSTREAM_HAS_KNOWN_BUG` flips False when upstream fixes the bug — cue to delete the patch. `StarshipUIManager.create_new_theme` returns the subclass; 8 production `UIManager` construction sites use the subclass. `pygame_gui==0.6.14` pinned in `requirements.txt` while patch is live.

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
- Consumers: `game/ui/screens/battle_setup/spec_compiler.py::_complex_to_entries`, `game/strategy/combat/strategy_modifier_stack_builder.py::StrategyModifierStackBuilder._emit_team_scoped`.
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

> **Adoption note (DOC-032, 2026-05-20):** the single current production consumer of this pattern is `StrategyScreen` (`game/ui/screens/strategy_screen.py` via `StrategyScreenComposition`). The "three or more collaborators" guidance above is the *threshold for adopting* the pattern, not a claim of multiple adopters. Promote additional UI classes to this pattern as they cross the threshold.

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

Where (remaining confirmed sites; PROJ-416 deleted `race_setup_screen.py` and PROJ-417 deleted `test_run_details.py`, 2026-05-13):
- (Removed PROJ-417) `game/ui/screens/test_lab/test_run_details.py` —
  the ~12-LOC re-export shim is deleted; callers import
  `TestRunDetailsPanel` from `game/ui/screens/test_lab/details/` directly.
- `game/simulation/components/component.py:392-405` — re-exports
  loader symbols from `game/simulation/components/component_loader.py`
  (the `# Re-exports from component_loader.py` block header is at line
  392; the `from ... import (...)` statement spans 395-405).
- (Removed PROJ-416) `game/ui/screens/race_setup_screen.py` —
  the transitional re-export shim is deleted; all callers import
  from `game/ui/screens/race_setup/screen.py` directly.
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

## 37. Typed `DeployedGroup` Family (sibling of `Fleet`)

Where: `game/strategy/data/deployed_group.py` (`DeployedGroup`
abstract base + `MineGroup` / `FighterWing` /
`SatelliteConstellation`); `game/strategy/data/empire.py`
(`Empire.deployed_groups`, `add_deployed_group`,
`remove_deployed_group`, `deployed_groups_of`); the five FMS order
handlers under `game/strategy/engine/order_handlers/`
(`lay_mines.py`, `launch_fighters.py`, `launch_satellites.py`,
`recover_fighters.py`, `recover_satellites.py`); combat seam at
`game/strategy/combat/spec_compiler.py` /
`game/strategy/combat/team_spec_builder.py`; minefield seam at
`game/strategy/engine/minefield_resolver.py`.

Replaces the retired (PROJ-431 / TD-10) "Group-Kind Fleet
Discriminator" pattern in which `Fleet.group_kind` ∈
`{"fleet", "mine_group", "fighter_group", "satellite_group"}` plus
`BaseCommandHandler._reject_if_non_fleet_group` constrained
non-`fleet` Fleet kinds from movement / build / warp / intercept /
join commands. `Fleet.group_kind`, the guard, and the synthetic
mine-carrier `ShipInstance` are all DELETED.

Contract:
- Concrete subclasses register their `type` discriminator string via
  `@_register_type("<name>")` and implement `_from_dict_payload(data)`
  for polymorphic round-trip via `DeployedGroup.from_dict`.
- The base class deliberately exposes a NARROW surface: identity
  (`id`, `owner_id`, `location: HexCoord`, `display_name`) only.
  Fleet-action methods (Move / Warp / Build / Join) are NOT present.
  The runtime type IS the model; there is no string discriminator
  and no validation guard — deployed groups never reach fleet-action
  handlers because they are not `Fleet`s.
- `Empire.fleets` and `Empire.deployed_groups` are disjoint
  collections. Combat membership: the spec compiler walks both
  `empire.fleets` and `empire.deployed_groups_of(FighterWing |
  SatelliteConstellation)` for the at-hex participant set;
  `MineGroup`s are routed into the typed `mine_groups` sidecar on
  `StrategyBattleAssembly.extensions`.
- Strategic launch / lay actions mint a fresh group every time — no
  same-hex auto-merge for new launches (PROJ-FMS-B audit Fix 4;
  mirrored by PROJ-FMS-C / PROJ-FMS-D). End-of-battle fighter /
  satellite overflow DOES merge into a pre-existing same-type group
  at the sector when present.
- ID namespace conventions: `MineGroup` 100000+, `FighterWing`
  200000+, `SatelliteConstellation` 300000+.

`_ShipBearingDeployedGroup` is an internal (non-registered) base
for groups whose `ships` are real `ShipInstance` entries
(`FighterWing`, `SatelliteConstellation`). It supplies
`remove_ship` so the PROJ-269 post-battle hook prunes destroyed
ships via the same `IFleetMutator` plumbing used for real Fleets.

Use for: any new "empire-owned, hex-located deployable" entity that
conceptually is NOT a Fleet (no orders, no strategic move, no
shipyard). Add a new subclass under `deployed_group.py`, register
its `type`, and let the combat / DTO / serialisation paths pick it
up via `empire.deployed_groups_of(<NewType>)`.

Boundary: real fleets (have orders, can move, can build) remain
`Fleet`s on `empire.fleets`. Do not bolt a deployable concept onto
`Fleet` — extend the `DeployedGroup` family instead.

## 38. CarriedVehicle Substrate

Where: `game/strategy/data/ship_instance.py::ShipInstance.bay_inventory`
(typed `BayInventory.bay: list[CarriedVehicle]` slot — PROJ-436
Phase 9 deleted the legacy `_CarriedItemsProxy` shim and the
`carried_items` property);
`game/simulation/components/abilities/vehicle_bay.py::VehicleBayAbility`;
`game/strategy/data/carried_vehicle_deploy.py::carried_vehicle_to_ship_instance`;
`game/strategy/data/ship_cargo_manager.py`; order handlers under
`game/strategy/engine/order_handlers/` for launch / recovery.

Contract:
- `VehicleBayAbility` data shape: `{"capacity_mass": <int>,
  "allowed_types": ["mine", "fighter", "satellite"]}`. `allowed_types`
  is the typed-bay filter — `fighter_bay` carries `["fighter"]`,
  `satellite_bay` carries `["satellite"]`, `mine_bay` carries
  `["mine"]`, and universal `vehicle_bay` carries all three. Capacity
  scales via the `simple_size_mount` modifier and the
  `bay_capacity_mult` stat key (Round 4 Obs C).
- `CarriedVehicle` (a typed payload in `bay_inventory.bay`) holds
  `design_id`, `design_data`, `current_hp`, optional
  `component_states`, and `vehicle_type`. Mass is the capacity gate;
  `ShipCargoManager.can_accept_vehicle` queries `allowed_types`.
- Deploy: `carried_vehicle_to_ship_instance(cv, fleet_id, ...)` is the
  single shared helper that mints a deployed `ShipInstance` from a
  `CarriedVehicle`, preserving HP and per-component damage. Used by
  both strategic launch order handlers and tactical
  `BattleEngine.launch_*_in_battle`.
- Reboard: `fighter_reboard.apply_reboard` and the satellite reboard
  hook convert deployed `ShipInstance`s back into `CarriedVehicle`s
  appended to the recovering carrier's `bay_inventory.bay` (HP +
  component_states preserved).

Use for: any future design-backed cargo (drones, drop pods, boarding
craft). Reuse `VehicleBayAbility` with a new `vehicle_type` plus an
`allowed_types` entry on the bay rather than inventing a parallel
storage concept.

Boundary: drop pods and other non-design-backed cargo live in
`bay_inventory.pods` as typed `DropPod` entries. The
`bay_inventory.resources` / `bay_inventory.population` slots **exist**
(PROJ-436 Phase 2 widening) but production fleet-cargo today still
routes through the Phase 3 `ShipCargoManager` / `_cargo_contents`
substrate exposed via `Fleet.get_cargo_resource` /
`consume_cargo_resource`; migration into the typed BayInventory
slots is intentionally deferred (no production caller needs it
today). The four-slot `BayInventory` is the canonical
**typed** surface for `bay` and `pods`; `VehicleBay` capacity gates
only the `bay` slot's `CarriedVehicle` items.

## 39. Typed-Sidecar Extensions on Frozen DTOs

Where: `game/strategy/combat/battle_assembly.py::BattleSpecExtensions`,
`StrategyBattleAssembly`, `StrategyBattleAssembler`;
`game/simulation/battle_spec.py::BattleSpec` (frozen target).

Contract:
- A frozen simulation-layer DTO (e.g. `BattleSpec`) is a layer-spanning
  contract — strategy code MUST NOT mutate it. Strategy-only state that
  the simulation later needs is bundled in a typed `Extensions`
  dataclass wrapped alongside the spec by a typed
  `StrategyBattleAssembly`.
- Mutation requirements that must survive the frozen contract (e.g.
  a one-slot list filled by a pre-tick callback so a post-battle hook
  can read it) live as a mutable container field inside the otherwise
  frozen extensions dataclass. The frozen dataclass holds the reference;
  the container is appended to, never replaced.
- The orchestrator (`StrategyBattleAssembler.assemble`) is the only path
  that constructs both halves so spec and extensions cannot drift.
- Replaces the deprecated `object.__setattr__(frozen_dto, "_attr", value)`
  side-channel anti-pattern eliminated by PROJ-426 (TD-01).

Use for: any future cross-layer DTO where one side owns immutability
and the other needs to attach context, lifecycle state, or
extension-point data.

Boundary: fields that genuinely belong on the simulation contract
(read by `run_battle` / engine subsystems via their public surface)
go on the frozen DTO itself. Strategy-only data that the simulation
never reads goes on the extensions dataclass.

## 40. Named Pre-Tick Setup Registry

Where: `game/strategy/combat/pre_tick_setup_registry.py::PreTickBattleSetupRegistry`;
`game/strategy/combat/pre_tick_setup/{mine,reboard}_setup.py`;
`game/strategy/combat/battle_assembly.py::StrategyBattleAssembler`;
`game/simulation/battle_runner.py::run_battle`
(`pre_tick_loop_callback` parameter).

Contract:
- `run_battle` accepts a single `pre_tick_loop_callback(engine,
  battle_spec)` invoked once after engine construction and before the
  tick loop starts.
- Independent subsystems (mine resolvers, fighter reboard tracker,
  etc.) each export a `build_*_setup(...)` factory under
  `game/strategy/combat/pre_tick_setup/` that returns its own closure.
- `PreTickBattleSetupRegistry.register(name, setup)` adds a setup
  callback under a string name (duplicate names raise);
  `composed_callback()` returns a single ordered callback (registration
  order) or `None` when the registry is empty.
- `StrategyBattleAssembler` populates the registry once per assembly;
  the adapter passes `assembly.pre_tick_setup.composed_callback()`
  straight to `run_battle`.

Use for: any new battle-setup wiring that needs to install state on
the live `BattleEngine` before the tick loop. Register a named setup
with the assembler rather than racing for the single `pre_tick_loop_callback`
slot or adding a parallel kwarg to `run_battle`.

Boundary: things that need to run per-tick belong in the tick-phase
registry (Pattern #23). Things that need to run at end-of-battle
belong on the strategy post-battle hook
(`PostBattleHookBuilder.build`), not on this setup registry.

## 41. Polymorphic Order Issuer (`IIssuerAdapter`)

Where: `game/strategy/engine/issuer_adapter.py::IIssuerAdapter`,
`FleetShipIssuerAdapter`, `PlanetStagingYardIssuerAdapter`; the five
FMS order handlers under `game/strategy/engine/order_handlers/`
(`lay_mines.py`, `launch_fighters.py`, `launch_satellites.py`,
`recover_fighters.py`, `recover_satellites.py`);
`game/strategy/engine/action_execution_engine.py`.

Contract:
- `IIssuerAdapter` is a `@runtime_checkable` Protocol exposing the
  minimum slice of fleet/planet that the FMS order handlers need:
  `location`, `owner_id`, `display_label`, `pop_carried(...)`,
  `count_carried(...)`, `append_carried(...)`, `append_recovered(...)`.
- Two production implementations: `FleetShipIssuerAdapter` wraps a
  `(Fleet, ShipInstance)` pair and operates on
  `ship.bay_inventory.bay` (typed `CarriedVehicle` entries — the
  Phase 9 deletion of the legacy `carried_items` shim made the typed
  slot the canonical write surface); `PlanetStagingYardIssuerAdapter`
  wraps a `Planet` and operates on `planet.staging_yard`
  (capacity-checked via `Planet.add_to_staging_yard`).
- Order handlers expose `execute_for_issuer(*, issuer, order_owner,
  empire, galaxy=None, registries=None) -> OrderExecutionResult` (the
  PROJ-438 Phase 6 unified 5-kwarg signature; recovery handlers accept
  and ignore the trailing `galaxy` / `registries`) and treat the
  `IIssuerAdapter` as the only mutation surface — no direct
  `fleet.ships[i].bay_inventory.bay` access.
- `ActionExecutionEngine` ticks both `fleet.orders` and `planet.orders`
  in Round 4; each iteration constructs the matching adapter and
  dispatches to the same handler.
- All five FMS `Issue*Command` DTOs carry an optional `planet_id`
  alongside the existing `fleet_id`; exactly one must be set.

Recipe (when adding a new issuer kind, e.g. orbital platform):

1. Define a new `IIssuerAdapter` implementation that exposes the
   minimum surface (location / owner_id / carried-vehicle pop+append).
2. Widen the `Issue*Command` DTOs in scope with an optional
   identifier for the new issuer kind.
3. Update the FMS command handlers' validation to recognise the new
   identifier and confirm the issuer holds the required capability
   ability.
4. Update `ActionExecutionEngine` to tick the new issuer's order list
   and construct the new adapter.
5. The five FMS order handlers should require no change — they
   already operate on `IIssuerAdapter`.

Use for: any new "thing that can issue strategic action orders"
(orbital platform, space station, megastructure, etc.) that should
reuse the existing FMS order pipeline rather than spawn a parallel
handler family.

Boundary: this pattern is for sharing handler logic across issuer
kinds. It is NOT for adding new order types — those still get their
own command + handler + order handler trio (Pattern #7).

## 42. Bootstrap-State Single Assignment Path

Where: `game/strategy/engine/session/runtime_services.py`, `game/strategy/engine/session/bootstrap.py`, `game/strategy/engine/session/persistence_adapter.py`, `game/strategy/engine/game_session.py`.

Use this pattern when a class has two construction entry paths (e.g. fresh construction + rehydration from a save) that must produce structurally identical instances. The historical failure mode is service-wiring drift: the two paths re-implement composition by hand, a new dependency lands on one path, and the other quietly diverges. PROJ-396 CRIT-002 is the canonical case in this codebase — the prior `GameSession` had a hand-mirrored mutator-service / turn-engine / event-bus block in both `__init__` and `from_dict`.

Contract:

- Define a single frozen-dataclass payload (e.g. `SessionBootstrapState`) that captures everything either path needs to apply onto `self`.
- Define a single internal assignment method (e.g. `_apply_bootstrap_state(state)`) that is the **only** place that mutates `self` from a state value. Do NOT use `self.__dict__.update(...)` or `cls.__new__(cls)` re-construction.
- Define a single canonical wiring function (e.g. `SessionBootstrap._build_services(...)`) shared by both paths.
- Both entry paths build a state and call the assignment method. Public API stays the same; tests should not see the indirection.
- Cover with an anti-drift regression test that compares service classes across both construction paths (e.g. `test_init_and_from_dict_use_identical_service_classes`).

Skeleton:

```python
@dataclass(frozen=True)
class SessionRuntimeServices:
    registries: GameRegistries
    event_log: EventLog
    # ... other wired services

@dataclass(frozen=True)
class SessionBootstrapState:
    config: GameConfig
    services: SessionRuntimeServices
    # ... other owned state

class SessionBootstrap:
    @staticmethod
    def _build_services(*, registries, event_log=None, ...): ...

    @staticmethod
    def new_game_state(config, *, ai_factory=None) -> SessionBootstrapState: ...

class GameSession:
    def __init__(self, config=None, ai_factory=None, *, _state=None):
        self._race_registry = None
        if _state is not None:
            self._apply_bootstrap_state(_state)
            return
        state = SessionBootstrap.new_game_state(config or GameConfig(), ai_factory=ai_factory)
        self._apply_bootstrap_state(state)

    @classmethod
    def from_dict(cls, data, ai_factory=None):
        session = cls.__new__(cls)
        session._race_registry = None
        state = SessionPersistenceAdapter.rehydrate_state(data, ai_factory=ai_factory, ...)
        session._apply_bootstrap_state(state)
        return session

    def _apply_bootstrap_state(self, state):
        # Single state-mutation site.
        self._services = state.services
        # ... other owned fields
```

Boundary: this pattern is for *structural* drift, not behavioral cleanup. If the two construction paths have intentionally different semantics (e.g. `human_player_ids` fallback differing between fresh and load paths), keep that asymmetry inside the state-builder for each path. The single-assignment method only copies from the state; it does not enforce equality across paths.

## 43. Unified Container Substrate

Where: `game/strategy/data/container.py::Container` (PROJ-436 Phase 0
substrate), `game/strategy/data/containable.py`,
`game/strategy/data/bay_inventory.py::BayInventory` (Phase 2 widened to
the four-slot Container projection), `game/strategy/engine/production_engine.py::IProductionResourceSource`
(Phase 8 polymorphic-protocol seam).

Use this pattern when a storage surface needs to hold heterogeneous
mass-priced content (resources, items, population) under one
capacity cap with one policy filter. PROJ-436 unified eight separate
storage fields and three ability variants (`ResourceStorage`,
`CargoStorage`, `VehicleBay`) into one `Container` abstraction; the
typed `BayInventory` shipped four parallel slots
(`bay: list[CarriedVehicle]`, `pods: list[DropPod]`,
`resources: dict[str, float]`, `population: dict[str, int]`) sharing
one mass cap.

Contract:

- `Container(capacity_mass, policy, resources, items, population)`
  carries three internal slices. Mass is the universal capacity gate
  — resource mass-per-unit resolves through
  `ResourceCatalog.get_mass_per_unit()`; item mass comes from the
  `ItemRef`; population mass comes from `species_mass_per_unit()`.
- `ContainerPolicy(allowed_kinds, allowed_type_ids=None)` filters by
  `ContainableKind` (RESOURCE / ITEM / POPULATION) plus an optional
  type-id allowlist. Policy is data, not code — a `metals_silo` with
  `allowed_type_ids=["metals"]` and a generic cargo hold with
  `allowed_type_ids=None` use the same engine path.
- `Container.accepts(containable)` is the policy seam for
  container-backed write paths and the unified projection surface
  (`BayInventory.container_view()` is a snapshot for callers that
  want unified accounting). **Transfer-kind validation does NOT go
  through `Container.accepts()` today** — `TransferValidator._is_known_cargo_type`
  routes through `ResourceCatalog.has()` plus three categorical
  sentinels (`passengers`, `drop_pod`, `vehicle`) directly; a future
  pass could wire the validator through `Container.accepts()` if a
  per-container policy check is needed, but that is not the current
  contract.
- For the production-engine read/consume path, the
  `IProductionResourceSource` Protocol (Phase 8) is the narrower
  polymorphic seam — `Planet` (over its stockpile API) and `Fleet`
  (over its cargo API) both satisfy
  `production_has_resources` / `production_get_resource` /
  `production_consume_resource`. The engine reads through these
  three methods without dispatching on entity type.
- Test-only: `set_resource_catalog(catalog)` on `container.py` injects
  a deterministic catalog for unit tests (PROJ-258
  `get_default_*` / `set_default_*` accessor convention).

Use for: any new storage surface that holds mixed mass-priced
content (drones-on-a-shipyard, planet-side civilian housing, etc.).
Reuse `Container` with a tailored `ContainerPolicy` rather than
inventing a parallel typed-list field per category. For
production-engine integration, satisfy `IProductionResourceSource`
via thin polymorphic delegators (do not extend the Protocol with
entity-specific methods).

Boundary: launch / recovery / life support / production stay
**separate** abilities — `Container` is storage only. Today's
**live** write substrates remain typed: `CarriedVehicle` items live
in `BayInventory.bay` (a `list[CarriedVehicle]` — see Pattern #38);
`DropPod` items live in `BayInventory.pods` (a `list[DropPod]`);
`Planet.stockpile` is a `dict[str, float]` over the `IStockpileHolder`
protocol; fleet cargo aggregates per-ship `_cargo_contents`
substrate through `Fleet.get_cargo_resource` /
`consume_cargo_resource` (the `BayInventory.resources` slot exists
from Phase 2 widening but production cargo has not been migrated
into it). `Container` and `Container.accepts()` are the unified
projection / policy seam over those typed substrates, not a
wholesale replacement of them — `BayInventory.container_view()`
returns a snapshot, not a mutable view. Deployed groups (`FighterWing`,
`SatelliteConstellation`, `MineGroup` on `empire.deployed_groups`)
are not in any container — Container handles only pre-deployment /
post-recovery storage. See Pattern #37 for the typed `DeployedGroup`
family.

> **Last verified:** 2026-05-18 — PROJ-436 Phase 10 doc refresh +
> Phase 11 consult disposition.
> Container substrate landed in Phase 0; `BayInventory` widened to
> four slots in Phase 2; `TransferValidator.VALID_CARGO_TYPES`
> deleted in Phase 7 — replaced by `ResourceCatalog.has()` + three
> categorical sentinels (`Container.accepts()` is the analogous
> seam for container-backed write paths but is NOT called by the
> current transfer validator);
> `ProductionEngine.context_type` storage-dispatch deleted in
> Phase 8 via the `IProductionResourceSource` Protocol;
> `_CarriedItemsProxy` deleted in Phase 9.

## 44. HabitabilityFactor Registry

Where: `game/strategy/data/habitability_factors.py`. Consumers across `game/strategy/data/`, `game/strategy/formulas/`, and `game/ui/widgets/` (≈24 references). `AGENTS.md` names this the single source of truth for habitability axes.

Contract:
- Each habitability axis (gravity, temperature, water, pressure, tectonic, magnetic, radiation, plus 10 atmospheric gases) is one frozen `HabitabilityFactor` dataclass instance: id, display_name, unit, display_scale, weight, default setpoint/tolerance, slider min/max/step, an `extractor(Planet) -> float | None`, a `scorer(value, EnvironmentalPreference) -> float`, and PROJ-293 display fields (`display_unit`, `display_precision`).
- `FACTOR_REGISTRY: Dict[str, HabitabilityFactor]` assembles 7 scalar factors + 10 gas factors keyed by canonical id (`"gravity"`, …, `"gas.O2"`, …). Gas ids are prefixed `gas.`.
- Lookup/iteration API: `get_factor(id)` (raises `KeyError` on unknown id), `iter_scalar_factors()` (non-`gas.` factors), `iter_gas_factors()` (`gas.`-prefixed factors).
- The habitability formula and the race-setup UI both iterate the registry, so adding a new axis is a single data-edit (append a `HabitabilityFactor`); no formula or UI code changes.

When to use: any per-axis habitability data or behavior. Never hardcode an axis list — iterate the registry.

## 45. AbilityMetadataRegistry

Where: `game/strategy/services/ability_metadata.py` (consolidated 11 scattered classification sources per PROJ-429).

Contract:
- Two classification facets as `Enum`s: `RoleTag` (`WEAPON`, `SEEKER`, `BEAM_PROJECTILE`, `SENSOR`, `SUPPORT`, `CARRIER`, `COMMAND`) and `StrategicKind` (`COMBAT_MODIFIER`, `COMBAT_FLAT_BONUS`, `STABILIZER`, `SUPERWEAPON`, `ENVIRONMENTAL`, `RESOURCE_BOOSTER`, `BUILD_RATE_BOOSTER`, `PLANETARY_SHIELD`, `ENERGY_DRAINING`).
- `EffectFacet` / `EnergyFacet` describe an ability's multiplier/rate effect and energy-drain behavior; `AbilityMetadata` bundles `effect`, `role_tags: frozenset[RoleTag]`, `energy`, and `kind_tags: frozenset[StrategicKind]` keyed by ability name (string).
- Query API: `get_ability_metadata(name) -> AbilityMetadata | None`, `ability_has_role_tag(name, tag)`, `ability_has_kind_tag(name, tag)`, `abilities_with_role_tag(tag) -> frozenset[str]`, `abilities_with_kind_tag(tag) -> frozenset[str]`, plus `ability_action_time_field(name)` and `ability_drains_energy(name)`.
- **Cycle-safety invariant:** this module must NOT import from `game.simulation.components.abilities` (strategy depends on simulation, and the ability classes import back). Ability names are bare strings here; no ability-class instantiation. Pinned by `test_ability_metadata_module_does_not_import_simulation_abilities`.

When to use: any strategy-layer classification of abilities by role or strategic kind. Never re-introduce hardcoded role/kind frozensets at call sites — query this registry.

## 46. RoleRegistry (layered-loading registry)

Where: machinery in `game/core/roles.py`; the strategy accessor in `game/strategy/data/design_role_registry.py`. A variant of Pattern #4 (Registry) specialized for layered file loading + invalidation. Documented here as its own entry because the layered-load + runtime-add gating + invalidation recipe is non-obvious.

Contract:
- `Role` is a frozen spec; `RoleRegistry(*, allow_runtime_add: bool)` loads roles in layers via `load_from_file(path, source_tag)` / `load_from_file_optional(...)` — base → mods → user overlay — later layers overriding earlier ones by id.
- `allow_runtime_add` gates `add_user_role(role)`: when `False`, runtime mutation raises `RoleRegistryReadOnlyError`. `register_invalidation_callback(cb)` lets dependents (cached vehicle-type lookups, formation defaults) rebuild when roles change.
- Two instances: `design_role_registry` (`allow_runtime_add=True`, mutable — subsystems may add user roles) and `combat_lab_role_registry` (`allow_runtime_add=False`, read-only scenario-wiring labels).
- Accessor convention (the `get_default_*` / `set_default_*` / `reset_default_*` triple): `get_default_design_role_registry()` returns the cached layered-loaded registry; `set_default_design_role_registry(r)` overrides it (tests/DI); `reset_default_design_role_registry()` clears the cache so the next `get_default_*` rebuilds.

When to use: any registry whose contents come from layered JSON (base + mods + user overlay) and whose consumers cache derived views that must invalidate on change.

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
