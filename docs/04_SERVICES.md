# Service Layer Architecture

> **Last verified:** 2026-05-08 - Balanced compact rewrite from `docs/04_SERVICES.md` and `AgentCoordination/Scratchpad/reports/04_SERVICES_ALT_compact.md`; reconciled against current service files under `game/services/`, `game/simulation/services/`, `game/strategy/services/`, and `game/ui/screens/builder/`.

Compact reference for service responsibilities, contracts, DI rules, APIs,
invariants, extension points, warnings, and tests. This removes release-note
archaeology and repeated examples, but keeps operational contracts agents need.

## Service Layers

Services are facade-style boundaries over domain operations. They keep UI,
orchestration, and engines from duplicating business logic.

- `game/services/`: cross-cutting infrastructure available to all layers; must depend on Core only.
- `game/simulation/services/`: battle lifecycle, ship materialization, design loading/editing, modifiers, registry reload.
- `game/strategy/services/`: navigation, movement, cargo, economy projections, ability/effect scanning, replay, mutator/write boundaries, superweapon helpers.
- `game/ui/...` services: UI-local helpers that can depend upward as normal UI code. They are not cross-cutting services.

Placement rule for `game/services/`: Core-only dependencies, used by multiple
layers or clearly cross-cutting, documented Protocol plus at least one testable
implementation.

## Directory Map

```text
game/services/llm/
  types.py                         Role, FinishReason, Message, TokenUsage, CompletionResult
  provider.py                      LLMProvider Protocol
  factory.py                       LLMProviderFactory, register_provider()
  deepseek.py                      DeepSeekProvider
  background.py                    LLMBackgroundCall, shutdown_all_calls()
  defaults.py                      get_default_llm_provider(), set_default_llm_provider()

game/simulation/services/
  battle_service.py                Visual-mode BattleEngine service
  design_loader.py                 SimulationDesignLoader
  modifier_service.py              Low-level component modifier rules
  registry_loader.py               reload_registries_from_directory()
  ship_materializer.py             ShipSpec -> Ship materializers
  vehicle_design_service.py        Ship creation/editing service

game/ui/screens/builder/
  modifier_logic.py                Builder ModifierLogicService
  modifier_utils.py                copy_modifiers()
  stat_definitions.py              StatDefinition
  stat_getters.py                  GETTERS registry and formatters
  stat_rows_dynamic.py             Dynamic stats rows
  stats_config.py                  stats_sections loader and SECTION_GENERATORS

game/strategy/services/
  action_time_resolver.py          Order action/activation time lookup
  ability_iterator.py              IAbilitySource provider registry
  ability_sources/                 Facility, storm, fleet, planet, star, warp, archetype adapters
  cargo_transfer_service.py        Transfer dialog/business logic
  combat_modifier_collector.py     Pre-battle strategic combat modifiers
  component_inspector.py           Component/ability inspection utilities
  deployment_zone_calculator.py    BattleRole -> battlefield positions
  design_cost_calculator.py        Registry-backed design cost calculation
  design_validator.py              Strategy design validation
  effect_ability_display.py        Effect display/grouping helpers
  effect_ability_metadata.py       Effect metadata registry
  empire_economy_service.py        UI-safe facade over EmpireEconomyCalculator
  empire_write_service.py          IEmpireMutator implementation
  fleet_cargo_projector.py         Project queued cargo transfers
  fleet_navigation_service.py      Fleet movement and path projection
  fleet_speed_calculator.py        Strategic movement speed
  fleet_write_service.py           IFleetMutator implementation
  galaxy_pathfinding_service.py    Galaxy pathfinding over IGalaxySystemGraph
  intercept_calculator.py          Chase/intercept point calculation
  modifier_resolver.py             size_mount modifier resolution
  planet_economy_projector.py      Per-planet resource flux projection
  planet_habitability_service.py   Injectable cached habitability calculator
  planet_query_service.py          Pure queries over Planet facade data
  planet_write_service.py          IPlanetMutator implementation
  race_description_llm_controller.py / prompt_builder.py
  race_resolver.py                 RaceConfig resolution helper
  replay_resolver.py               Replay id -> saved replay lookup
  replay_ship_builder.py           Replay playback ship builder
  replay_store.py                  Battle replay sidecar persistence
  replay_verification_coordinator.py
  replay_verification_sidecar.py
  ship_instance_write_service.py   IShipInstanceMutator implementation
  stabilizer_registry.py           Stabilizer ability -> blocked superweapon map
  strategic_ability_scanner.py     Scoped ability queries and stacking
  superweapon_registry.py          Declarative strategic superweapon table
  system_destroyer.py              Collect-then-mutate star-system teardown
  system_effects_collector.py      Sector/system effect aggregation
  task_group_suggester.py          Fleet hierarchy auto-suggestion
```

Related data/formula modules:

- `game/strategy/data/environmental_preference.py`
- `game/strategy/data/habitability_factors.py`
- `game/strategy/data/race_config.py`
- `game/strategy/data/race_point_budget.py`
- `game/strategy/data/homeworld_presets.py`
- `game/strategy/data/colony_species_config.py`
- `game/strategy/formulas/habitability.py`
- `game/strategy/formulas/colony_output.py`

Package-export warning: `game/strategy/services/__init__.py` currently exports
only `CargoTransferService`. Import most strategy services from their module
paths. `game/simulation/services/__init__.py` exports the main simulation
services and result DTOs.

## Cross-Cutting LLM Service

Location: `game/services/llm/`

Purpose: provider-neutral chat-completion abstraction. Consumers must depend on
`LLMProvider`, not `DeepSeekProvider`.

Public API from `game.services.llm`:

- `LLMProvider`: runtime-checkable Protocol; `complete(messages, **opts) -> CompletionResult`.
- `LLMProviderFactory.create(name=None)`: name comes from argument, `LLM_PROVIDER`, or default `"deepseek"`. Unknown provider names raise `LLMConfigError`. Known providers that cannot initialize may return `None`.
- `register_provider(name, cls)`: provider modules register themselves at import time.
- `Role`, `FinishReason`: string enums.
- `Message`, `TokenUsage`, `CompletionResult`: frozen DTOs.
- `LLMBackgroundCall`: worker-thread wrapper; exposes `status`, `result`, `error`, `elapsed_seconds`, `cancel()`, `wait(timeout)`.
- `CallStatus`: `PENDING`, `RUNNING`, `DONE`, `ERROR`, `CANCELLED`. `wait()` is true only for terminal states.
- `shutdown_all_calls(timeout=5.0)`: joins in-flight calls before app shutdown.
- `get_default_llm_provider()` / `set_default_llm_provider(p)`: application default provider slot. UI should gate affordances with `provider is not None`.

Configuration:

- `DEEPSEEK_API_KEY`: required at request time for DeepSeek; read per request, not cached.
- `LLM_PROVIDER`: provider lookup key.
- `game.core.config.LLMConfig`: timeout, retry policy, `MAX_CONCURRENT_CALLS=3`, `DEFAULT_MODEL="deepseek-v4-flash"`, User-Agent.
- Retry policy: retry 5xx with backoff; never retry 429; SSL verification stays enabled.

Error model (codes in `game/core/exceptions.py`): `LLMConfigError` (L001),
`LLMNetworkError` (L002), `LLMResponseError` (L003), `LLMRateLimited` (L004),
`LLMTimeoutError` (L005), `LLMCancelled` (L006), `LLMUnexpectedError` (no code;
wraps any non-LLM exception escaping a provider). All inherit
`LLMException -> GameException`. `DEEPSEEK_API_KEY` is read per request and
must not be cached on the provider instance, in logs, or in exception context.

Reference consumer: `game/strategy/services/race_description_llm_controller.py`.
It owns one `LLMBackgroundCall` per generated field, translates `CallStatus`
to field status, drives Race Setup through `on_change`, and is pygame-free. If
the screen swaps `race_config`, it must call `controller.set_race_config(new_race)`
before accepting results.

Extension recipe: implement `LLMProvider.complete(...) -> CompletionResult`,
raise `LLMException` subclasses for expected provider failures, register via
`register_provider(name, cls)`, and keep credentials out of instance state,
logs, exception contexts, and `repr`.

## Simulation Services

### ShipMaterializer

Location: `game/simulation/services/ship_materializer.py`

Purpose: convert `ShipSpec` to live `Ship` without duplicating caller-specific
builder closures.

Protocol:

```python
@runtime_checkable
class IShipMaterializer(Protocol):
    def materialize(
        self,
        ship_spec: ShipSpec,
        team_id: int,
        registries: GameRegistries,
    ) -> Ship: ...
```

Implementations:

- `InstanceBackedMaterializer`: Strategy, Battle Setup, `game/app.py::start_battle`; requires `ship_spec.instance_ref`.
- `DesignOnlyMaterializer(design_loader)`: Combat Lab; requires `design_loader(design_id: str) -> dict`.

Accessors: `get_default_ship_materializer()` and
`set_default_ship_materializer(materializer)`.

Battle integration:

- `run_battle(spec, ai_factory=..., ship_builder=None, registry_provider=...)` and `BattleController.start_from_spec(...)` use the default materializer when no explicit `ship_builder` is supplied.
- If `ship_builder is None`, caller must pass `registry_provider: IRegistryProvider`.
- `build_context_ship_builder(registry_provider=...)` builds the closure from the default materializer plus explicit registry provider.
- Simulation code must not resolve registry providers by global lookup. Non-Simulation callers may supply `get_default_registry_provider()`.
- `ShipSpec.instance_ref: Optional[Any] = None` lets instance-backed compilers pass `ShipInstance` without Simulation importing Strategy.
- Tests may keep explicit `ship_builder` stubs for isolation.

### BattleService

Location: `game/simulation/services/battle_service.py`

Purpose: visual-mode abstraction around `BattleEngine`. Headless flows use
`game.simulation.battle_runner.run_battle(spec)` directly. Visual-mode
`BattleController` uses this service for per-frame ticking and emits
`BattleOutcome` at battle end, matching the headless DTO contract.

Dependencies: no constructor args. Internally creates `BattleEngine` and
`BattleLogger`. AI factory is injected via `create_battle(..., ai_factory=...)`.

Result DTO:

```python
@dataclass
class BattleServiceResult:
    success: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    engine: BattleEngine | None = None
```

Key API: `create_battle`, `add_ship`, `remove_ship`, `start_battle`,
`adopt_started_engine`, `update`, `run_ticks`, `is_battle_over`,
`get_winner`, `get_battle_state`, `get_all_ships`, `get_alive_ships`,
`get_engine`, `reset`.

### VehicleDesignService

Location: `game/simulation/services/vehicle_design_service.py`

Purpose: high-level ship creation/modification API over layers, components,
class changes, validation, and stat recalculation.

Dependencies: `VehicleDesignService(registries=GameRegistries)`; strict DI,
no fallback.

Result DTO:

```python
@dataclass
class DesignResult:
    success: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    ship: Ship | None = None
    removed_component: Component | None = None
```

Key API: `create_ship`, `add_component`, `add_component_instance`,
`add_component_bulk`, `remove_component`, `move_component`, `change_class`,
`validate_design`, `get_available_components`, `get_layer_info`,
`get_ship_summary`.

Invariant: `move_component` is atomic remove plus re-add and preserves the
component instance. Mass budget is advisory for moves.

`WorkshopViewModel` (`game/ui/screens/workshop_viewmodel.py`) composes this
service with layer resolution and UI state. Its helpers include
`resolve_target_layer`, `quick_add_component`, `move_component`,
`move_component_group`, `resolve_move_target`, and `on_modifier_changed`.

Stats panel extension:

- Config: `data/stats_sections.json`
- Getters: `game/ui/screens/builder/stat_getters.py` `GETTERS`
- Dynamic rows: `game/ui/screens/builder/stat_rows_dynamic.py`
- Config loader/registry: `game/ui/screens/builder/stats_config.py`
- Renderer: `game/ui/panels/design_stats_panel.py`
- Add a stat by adding a getter, registering it, and adding JSON config.
- Add a section by adding a generator, registering it in `SECTION_GENERATORS`, and adding JSON config.

### Modifiers

`ModifierService` in `game/simulation/services/modifier_service.py` owns
low-level modifier rules and requires `modifier_registry: dict[str, Any]`.

`ModifierLogicService` in `game/ui/screens/builder/modifier_logic.py` owns
builder-specific modifier logic: validation, mandatory modifiers, initial
values, component constraints such as turret arc limits, and step-button
snapping. It requires `IRegistryProvider` and creates `ComponentService`
internally.

Key `ModifierLogicService` API: `is_modifier_allowed`,
`get_mandatory_modifiers`, `is_modifier_mandatory`, `get_initial_value`,
`ensure_mandatory_modifiers`, `get_local_min_max`, `calculate_snap_value`.

Warning: the deprecated static `ModifierLogic` wrapper remains for transition.
New code should use `ModifierLogicService` instances.

### SimulationDesignLoader

Location: `game/simulation/services/design_loader.py`

Purpose: load ship designs from JSON or dicts and instantiate `Ship` objects
with stat recalculation.

Dependencies: keyword-only `registries: GameRegistries`; strict DI, raises
`ValidationException` if omitted.

API:

- `load_ship_from_design_data(design_data, center_x, center_y) -> Ship | None`
- `load_ship_from_file(file_path, width=1920, height=1080) -> tuple[Ship | None, str]`

### Registry Reload

Location: `game/simulation/services/registry_loader.py`

Purpose: reload modifiers, components, and vehicle classes from a directory
without Core importing Simulation.

```python
def reload_registries_from_directory(
    registry_manager: RegistryManager,
    data_dir: str | Path,
    *,
    registry_provider: IRegistryProvider,
) -> bool: ...
```

Contract:

- Clears existing registry data, then loads JSON registry files.
- Checks `test_`-prefixed variants first for test data directories.
- Returns `True` if directory exists, `False` if invalid.
- Raises `FrozenStateException` if registry is frozen.
- `registry_provider` is required. Simulation code must not look it up globally.

## Strategy Movement and Fleet Services

### FleetNavigationService

Location: `game/strategy/services/fleet_navigation_service.py`

Purpose: single source of truth for fleet navigation. UI path projection and
turn execution use the same service.

DTOs:

- `NavigationState(location, path, orders, speed, can_warp)`: immutable snapshot; `from_fleet(cls, fleet)`.
- `PathSegment(start, end, turn, is_warp)`: projected UI path segment; `to_dict()`.
- `NavigationStep(next_hex, new_state, order_complete=False)`: result of one navigation step.

Key API: `get_destination`, `compute_path`, `compute_next_step`,
`project_path`, `project_path_as_dicts`, `compute_path_for_warp`,
`calculate_fleet_next_hex`, plus navigation write methods used through
`IFleetMutator` (`set_location`, `set_path`).

Architecture: pure functions operate on `NavigationState`; projection
simulates future movement; execution wraps pure functions and mutates fleet
state only at the bridge.

### FleetSpeedCalculator

Location: `game/strategy/services/fleet_speed_calculator.py`

Purpose: strategic speed in hexes per turn. Fleet speed is the slowest
combat-capable ship.

Constants: `K_STRATEGIC=25`, `MAX_HEXES_PER_TURN=10`,
`MIN_HEXES_PER_TURN=0`, `IMMOBILE_VEHICLE_TYPES={'Planetary Complex',
'Satellite', 'Station'}`, `CARRIER_BASED_TYPES={'Fighter'}`,
`BASE_TICKS_PER_MOVEMENT=100`.

Formula: `floor((strategic_movement * K_STRATEGIC) / mass)`, clamped to
`[0, 10]`.

Key API:

- `calculate_ship_speed(ship_instance) -> int`
- `calculate_fleet_speed(fleet) -> float`
- `update_fleet_speed(fleet) -> None`
- `calculate_fleet_speed_with_strategic_mult(fleet, strategic_mult=1.0) -> float`
- Module function `get_tick_interval(speed) -> int`

Special cases for `calculate_ship_speed`:

- Planetary complexes, satellites, and stations always return 0 (immobile).
- Fighters always return 0 (carrier-based, no independent strategic movement).
- Ships with no `StrategicMovement` ability return 0.

Stale-reference correction: the old environment-object method name
`calculate_fleet_speed_with_environment` is not current. Callers compute sector
effects through `SystemEffectsCollector.aggregate_value_or(...)`, then pass the
numeric multiplier to `calculate_fleet_speed_with_strategic_mult`.

### Pathfinding, Intercept, Deployment, Task Groups

`GalaxyPathfindingService` (`game/strategy/services/galaxy_pathfinding_service.py`)
is pathfinding over `IGalaxySystemGraph`. API: `find_path_deep_space`,
`find_path_interstellar`, `find_hybrid_path`, `find_nearest_system`,
`get_system_at_hex`, `strip_start_hex`.

`InterceptCalculator` (`game/strategy/services/intercept_calculator.py`) holds a
`GalaxyPathfindingService` and calculates an intercept hex for a fleet or
`NavigationState` chaser. `project_fleet_path(fleet, galaxy, max_turns=10)` is a
top-level helper delegating to `FleetNavigationService`.

`DeploymentZoneCalculator` maps `BattleRole` to mirrored team deployment
positions on the 100000x100000 battlefield. API: `get_zone_center` and
`compute_positions`.

`suggest_task_groups(ships)` in `task_group_suggester.py` groups ships by
`effective_role` into TaskForces/Squadrons with default combat policies. It is
one-shot: the player can accept, modify, or discard the suggestion.

## Strategy Design, Cargo, and Action Services

### Ship Design Stats

Location: `game/simulation/entities/ship_design_stats.py`

Purpose: single source of truth for design stats. Uses `Ship.from_dict()` plus
`recalculate_stats()` so calculations go through simulation `ShipStatsCalculator`.

Contract:

- `calculate_design_stats(design_data, registries, components=None, component_toggles=None) -> dict`
- Requires `GameRegistries`.
- Full `ShipStatsCalculator.calculate()` requires `resource_catalog`; missing catalog raises at calculation time when needed.
- No `expected_stats` fallback. If `Ship.from_dict()` fails, the error propagates.

Return keys include `max_hp`, `mass`, `resource_storage`, `cargo_storage`,
`pod_storage_mass`, `resource_consumption_per_hex`,
`resource_consumption_per_turn`, `warp_resource_costs`,
`strategic_movement`, `warp_max_tonnage`.

Toggles and damage:

- Toggled-off components are excluded before `Ship` creation.
- Per-instance damage uses `components: dict[str, ComponentState]` keyed by `component_state_key(component_id, instance_index)`.
- Damage is applied before `recalculate_stats()`, preserving threshold deactivation and crew reallocation behavior.

Callers include `ShipInstance.get_calculated_stats()`,
`ProductionSpawner._spawn_to_staging_yard()`,
`Tools/validate_designs/validate_designs.py`, and `Tools/fix_designs/fix_designs.py`.

### ActionTimeResolver

Location: `game/strategy/services/action_time_resolver.py`

Purpose: resolve action/activation/deactivation ticks for fleet and planet
orders from component abilities.

Contract:

- `ORDER_TO_ABILITY_MAP` is derived from the self-registering command registry, not a hardcoded table.
- `MOVEMENT_ORDER_TYPES = frozenset({OrderType.MOVE, OrderType.MOVE_TO_FLEET})` complete with 0 action ticks.
- `ACTIVATE_ABILITY` and `DEACTIVATE_ABILITY` read `ability_name` from `order.target` and use `activation_time` / `deactivation_time`.
- Fleet orders search ship components; planet action orders search target facility components.
- Default fallback for unmapped/missing ability time is 1 tick.

API: `ActionTimeResolver.resolve_action_time(entity, order, component_registry=None) -> int`.

### Cargo, Costs, and Component Inspection

`CargoTransferService` (`game/strategy/services/cargo_transfer_service.py`) is
shared transfer business logic. API: `resolve_colonies`, `get_unload_items`,
`get_load_items`, `get_inventory_items`, `build_transfer_command`. Module
function `project_fleet_position(fleet) -> HexCoord` walks queued MOVE/WARP
orders.

`FleetCargoProjector.get_projected_cargo(fleet, cargo_type) -> int` projects
future fleet cargo by applying queued transfer orders.

`DesignCostCalculator.calculate_total_cost(design_data, registries) -> dict[str, float]`
centralizes resource cost calculation. It resolves component costs through
registry-backed ship loading, handles formula/modifier effects, and applies
vehicle class `cost_multiplier`.

`ComponentInspector` (`game/strategy/services/component_inspector.py`) provides
module-level inspection utilities. Key API: `get_component_abilities`,
`extract_abilities_from_component`, `iterate_design_components`,
`iter_facility_ability_entries`, `ship_has_ability`, `find_ship_with_ability`,
`count_ability`, `list_ship_abilities`, `get_ability_list`,
`has_warp_capability`.

Critical registry invariant: facility and ship `design_data` often stores only
component IDs. Ability checks must resolve through the component registry. Do
not inspect only inline `comp.get("abilities", {})`; that silently misses
registry-defined abilities.

`get_ability_list` is the canonical normalizer for scalar, dict, and list
ability forms. `has_warp_capability` uses `get_calculated_stats()` so it
respects mass, storage, resource cost, and damage state.

## Ability, Effect, and Superweapon Services

### StrategicAbilityScanner

Location: `game/strategy/services/strategic_ability_scanner.py`

Purpose: scoped strategic ability queries for stabilizers, harvest boosters,
build-rate boosters, combat modifiers, and similar effects.

API:

- `find_abilities_at_planet(ability_key, planet, registries=None, require_active=False) -> list[dict]`
- `find_abilities_in_scope(ability_key, target_planet, galaxy, empire, scope, registries=None, require_active=False) -> list[dict]`
- `aggregate_multipliers(entries) -> float`: intra-group MAX, inter-group MULTIPLY, default 1.0.
- `aggregate_rates(entries) -> float`: intra-group MAX, inter-group SUM, default 0.0.

Scopes resolve to which planets are scanned:

| Scope | Planets scanned |
|---|---|
| `planet` / `self` | Target planet only. |
| `sector` | All empire-owned planets at the target's global hex via `galaxy.get_planet_global_hex` + `galaxy.get_planets_at_global_hex`. |
| `system` | All empire-owned planets in the target's star system via `galaxy.get_system_of_planet`. |
| `empire` | All empire colonies. |

`require_active=True` filters to components whose `ComponentActivationState.phase`
is `ACTIVE`. Stabilizer and combat-modifier checks use this; harvest and build
boosters use the default `False` because they are always-on.

Registry parameter is critical: facility `design_data` typically stores bare
component IDs (`{"id": "stellar_stabilizer"}`) and ability data is looked up via
the component registry. Callers that omit `registries` silently get nothing back,
even from active stabilizers. The scanner's `_extract_ability` delegates to
`component_inspector.extract_abilities_from_component`, which accepts either a
`GameRegistries` or a plain components dict. Component iteration uses
`iter_keyed_components` from `game.core.patterns.layer_iterator`.

### IAbilitySource and SystemEffectsCollector

Locations:

- Protocol: `IAbilitySource` in `game/core/protocols/strategy_entities.py`
- Iterator: `game/strategy/services/ability_iterator.py`
- Adapters: `game/strategy/services/ability_sources/`
- Collector: `game/strategy/services/system_effects_collector.py`
- Metadata/display helpers: `effect_ability_metadata.py`, `effect_ability_display.py`

Purpose: unified pipeline for "things at a hex/system project effects." Current
providers include facilities, storms, fleets, planets, stars, warp points, and
system archetypes.

`IAbilitySource` exposes `source_kind`, `source_label`, `source_id`, `owner_id`,
`get_abilities()`, `affects_hex(h)`, `affects_system(s)`,
`get_activation_state(name)`.

Iterator API:

- `register_source_provider_at_hex(provider)`
- `register_source_provider_in_system(provider)`
- `unregister_source_provider(provider)`
- `iter_ability_sources_at_hex(system, hex_coord, registries=None, include_system_sources=...)`
- `iter_ability_sources_in_system(system, registries=None)`
- `set_fleet_lookups(at_hex=None, in_system=None)` for fleet provider lookup injection.

Collector API:

- `collect_sector_effects(system, hex_coord, empire_id, registries=None) -> list[dict]`
- `collect_system_effects(system, empire_id, registries=None) -> list[dict]`
- `find_sector_effect(effects, ability_name, **filters)`
- `aggregate_value_or(effects, ability_name, default, **filters)`

Effect dict shape:

```python
{
    "ability_name": str,
    "display_name": str,
    "group_key": str,
    "status": str,
    "resource_type": str | None,
    "damage_type": str | None,
    "kind": "multiplier" | "rate",
    "aggregate_value": float,
    "providers": [{
        "source_kind": str,
        "source_label": str,
        "source_id": str,
        "owner_id": int | None,
        "status": str,
        "is_active": bool,
        "value": float,
        "ability_data": dict,
    }],
}
```

Aggregation rules: `aggregate_multipliers` is intra-group MAX, inter-group
MULTIPLY, default 1.0; `aggregate_rates` is intra-group MAX, inter-group SUM,
default 0.0. Multiplier-only and rate-only entries must not appear in the same
group; mixed-kind groups are skipped with a warning. Ownerless sources may not
declare ownership-aware scopes (`enemy_sector`, `allied_sector`, etc.); offending
entries are skipped and logged. A component must not declare both combat scopes
(self/fleet/team) and strategic scopes on the same ability instance.

Intrinsic ability helpers (stars, warp points, archetypes, planets):

- `roll_intrinsic_abilities(template, rng)` in `ability_sources/intrinsic_roll.py` converts `{"min": x, "max": y}` ranges to scalar rolls. Optional per-ability `chance` (default 1.0) gates the ability; on `chance < 1.0` the helper draws `rng.random()` and skips on failure. The `chance` key is stripped from the output. Templates without `chance` consume zero extra RNG draws to keep determinism byte-identical.
- `format_intrinsic_source_label(entity_name, type_name)` in `ability_sources/labels.py` is the canonical label format.

Stale-reference correction: the legacy `AreaEffectManager` / `EnvironmentalEffects`
service wording is obsolete. Current effect display and environment behavior
flow through `ability_iterator`, `SystemEffectsCollector`, and
`effect_ability_metadata`. Storms now declare `abilities: Dict[str, Any]`
matching the `components.json` shape; overlapping storms multiply per-provider
(no shared `stack_group`) so two ion storms apply 0.5x · 0.5x = 0.25x shields.
An adapter package AST guard forbids `get_default_registry_provider()` calls
inside `ability_sources/`.

Extension recipe for a new strategic effect:

1. Ensure an `IAbilitySource` can expose the ability.
2. Register a provider with `ability_iterator` if the source type is new.
3. Add one metadata entry in `effect_ability_metadata.py` for display, value field, kind, grouping, and owner-aware scopes.
4. Let `SystemEffectsCollector` aggregate. Avoid central collector edits unless the aggregation contract itself changes.

### Stabilizers, Superweapons, System Destruction

`StabilizerRegistry` (`stabilizer_registry.py`) maps stabilizer abilities to
blocked superweapon orders. `STABILIZERS` is a tuple of
`StabilizerSpec(ability_name, scopes, blocks)`. Add or extend a stabilizer by
editing one tuple entry.

`SuperweaponRegistry` (`superweapon_registry.py`) maps strategic superweapon
orders to declarative `SuperweaponSpec` rows. `SELF_DESTRUCT` is intentionally
out of this registry. `STELLERATE_STAR` has `ability_name=None` because it
dispatches through `SystemDestroyer`.

`SystemDestroyer` (`system_destroyer.py`) centralizes collect-then-mutate
star-system teardown. Fleet inclusion is by hex distance within
`SYSTEM_RADIUS_HEXES = 50` of `system.global_location`, matching star-system
radius semantics. Collect first, then mutate, so unregistering planets cannot
change which fleets are found.

`CombatModifierCollector` (`combat_modifier_collector.py`) collects
strategic combat modifiers before battle: shield multiplier, damage
multiplier, and flat shield projection. It scans owner and opponent facilities
by scope through `StrategicAbilityScanner`, requires active components, and
aggregates with the same two-phase stacking rules.

## Habitability, Demographics, and Economy

### Race Habitability and Point-Buy

Locations:

- `game/strategy/data/environmental_preference.py`: `EnvironmentalPreference(setpoint, tolerance, min_value, max_value, step)`.
- `game/strategy/data/habitability_factors.py`: `HabitabilityFactor`, `FACTOR_REGISTRY`, `get_factor(id)`, `iter_scalar_factors()`, `iter_gas_factors()`.
- `game/strategy/data/race_config.py`: `RaceConfig.preferences`, `base_reproduction_rate=0.03`, `base_happiness=0.5`.
- `game/strategy/data/race_point_budget.py`: `RacePointBudget`.
- `game/strategy/data/homeworld_presets.py`: `apply_preset_to_config(preset, race_config)`.
- `game/strategy/formulas/habitability.py`: `calculate_habitability(planet, race_config) -> float`, `score_planet_for_race(...)`.

Extension invariant: add a habitability axis by registering one
`HabitabilityFactor` in `FACTOR_REGISTRY`. That axis then participates in
habitability, race point budget, Race Setup UI, homeworld presets, and
population logic. Do not add parallel hardcoded factor lists.

Point-buy API: `calculate_aptitude_cost`, `calculate_preferences_cost`,
`calculate_reproduction_cost`, `calculate_total_cost`, `get_remaining_points`,
`is_within_budget`, `get_aptitude_breakdown`, `get_breakdown`. Tolerance-deviation
cost is `_exponential_cost(steps) = 2**steps - 1`. `calculate_reproduction_cost`
uses linear-in-rate math (not integer steps) so the 0.5% floor returns -5
exactly. `RaceConfig.preferences` is registry-keyed and is backfilled from
`FACTOR_REGISTRY` defaults via `__post_init__`. `RaceConfig.base_reproduction_rate
= 0.03`, `RaceConfig.base_happiness = 0.5`. The default 100-point budget covers
all three cost categories combined.

### Colony Demographics Loop

Locations and contracts:

- `ColonySpeciesConfig(food_allocation=1.0, last_consumption_ratios={})`; `last_food_ratio` is a read-only computed `@property` returning `min(last_consumption_ratios.values())`, defaulting to 1.0 for empty dict (Liebig's Law). `to_dict` emits only `food_allocation`; `from_dict` always resets `last_consumption_ratios` to `{}`. `__post_init__` validates `food_allocation >= 0`. Tests that pre-set `last_food_ratio=X` migrate to `last_consumption_ratios={"organics": X}`.
- `Planet.get_species_config(race_id)`: lazy-create-and-store species config.
- `EconomyConfig(population_consumption: dict[str, float])`, `primary_resource`, `load_economy_config(path=None)`, `get_default_economy_config()`, `set_default_economy_config()`.
- `data/economy.json`: current population consumption data.
- `OrganicsConsumptionEngine.process_consumption(empires) -> None`.
- `HappinessEngine.process_happiness(empires, galaxy) -> None`.
- `PopulationEngine`: growth and decline.
- `FoodAllocationEditor`: player-facing allocation editor.

Turn order: 100-tick loop, then consumption, happiness, population growth,
quality, atmosphere, water.

Transient invariant: `ColonySpeciesConfig.last_consumption_ratios` is transient.
`OrganicsConsumptionEngine` must clear and rewrite it every turn, including 1.0
edge-case values for zero population or zero allocation. Saving it would make
post-load demographic state stale.

Happiness formula: `pop.happiness = clamp(raw, 0, 3)` where
`raw = race.base_happiness * cfg.last_food_ratio * habitability` plus a
surplus-food additive bonus `min(economy.surplus_food_bonus_cap,
economy.surplus_food_bonus_per_x * (surplus - 1.0))` when `surplus > 1.0`,
applied before clamp. `HappinessEngine` accepts optional `economy_config` and
`race_registry` kwargs; both fall back to default lookups when None.

Population formula: `growth = (base_reproduction_rate * last_food_ratio) * P *
(1 - P/K_eff) * happiness + decline_term`, where
`K_eff = max(1.0, max_population * habitability)` and
`decline_term = -DECLINE_RATE * P * (1 - last_food_ratio)` when
`last_food_ratio < 1.0` else 0. `DECLINE_RATE = 0.02` is a module constant.

UI invariant: `FoodAllocationEditor` is population-driven, not
facility-ability-gated. It mutates `ColonySpeciesConfig.food_allocation`
directly; this is a player dial, not a replayable order command.

### Colony Economy Multiplier

Locations:

- `game/strategy/formulas/colony_output.py`: `planet_habitability_multiplier(planet, race_registry) -> float`.
- `game/strategy/services/planet_habitability_service.py`: injectable cached calculator.
- `game/strategy/data/planet.py`: transient cache fields and facade method.
- `HarvestingEngine` and `ProductionEngine`: habitability multiplier in harvest/production paths.
- `TurnEngine`: sets current turn on harvesting and production engines.

Contracts:

- Multiplier is population-weighted mean of `score_planet_for_race(planet, race_for(pop))` across resident species.
- Uncolonized, zero-population, or all-missing-race cases return 1.0.
- Missing race IDs are excluded from BOTH numerator and denominator (not scored as 0) — save-drift defence.
- Computed once per colony per turn; cache warms on first read and invalidates at turn boundary. Cache fields `_cached_habitability_multiplier` and `_cached_multiplier_turn` are `init=False, compare=False` and are NOT emitted by `to_dict`; post-load planets re-warm on first read.
- Effective rate is multiplicative: `base_rate * booster_mult * habitability_mult`. Stacks alongside `ResourceHarvestBooster` and `BuildRateBooster` aggregation from `StrategicAbilityScanner`.
- `HarvestingEngine` and `ProductionEngine` accept optional `race_registry=None`; when None, the habitability hook short-circuits to 1.0 for legacy single-race compatibility.
- `TurnEngine.process_turn` calls `set_current_turn(session.turn_number)` on both engines before the 100-tick loop, guarded with `getattr` so mock engines do not break.
- Fleet production queues use 1.0 because they have no planet context.

### Race Registry

Protocol: `IRaceRegistry` in `game/core/protocols/strategy_domain.py`.

Implementation: `CachedRaceRegistry` in `game/strategy/systems/race_library.py`.
It wraps `RaceLibrary`, caches hits and misses, has no TTL or locks, and exposes
`invalidate(race_id=None)`.

Facade: `StrategySessionFacade.get_race_registry() -> IRaceRegistry`
lazy-constructs and memoizes one session registry.

Invalidation invariant: registry does not watch files. Race editor save should
call `invalidate(race_id)` when a session registry exists. External race file
edits require restart.

Companion API: `Empire.resident_species() -> set[str]` in
`game/strategy/data/empire.py` returns race IDs with count >= 1 on any colony
and excludes extinct species. A species with count=0 on colony A but count>=1 on
colony B is included. Not cached; recomputing is cheap relative to invalidation
complexity.

### Planet and Empire Economy Services

`PlanetQueryService` (`planet_query_service.py`) holds pure queries delegated by
the `Planet` facade: `active_abilities`, `is_ability_active`,
`occupied_hexes`, `can_build_type`. These never mutate the planet.

`PlanetHabitabilityService` (`planet_habitability_service.py`) implements the
default injectable habitability calculator. Its cache lives on the planet's
transient fields, not on the service.

`PlanetEconomyProjector` (`planet_economy_projector.py`) is the read-only
per-planet resource flux projector for UI/facade DTOs. The historical home of
`compute_planet_production` was `game/ui/panels/planet_report_panel.py`; the
current home is here. There is no backward-compat re-export.

Constructor: `PlanetEconomyProjector(*, registries, economy_config, race_registry)`;
all three are required.

API: `project(planet) -> dict[str, ResourceProjection]`.

Sub-projections:

- Harvest: delegates to `compute_planet_production(planet, registries)`, then applies habitability.
- Upkeep: mirrors consumption engine demand; not habitability-scaled.
- Yard drain: uses `_collect_planet_sources` plus `forecast_queue_turn_spend`; applies habitability to `build_rate` before the forecast walk.

`ResourceProjection` invariant: `net == harvest - upkeep - yard`.

Growth helper: `projected_growth_rate(planet, pop, race_config, cfg) -> float`
in `game/strategy/formulas/colony_output.py`. It mirrors
`PopulationEngine._grow_species` without mutation; positive means growth,
negative means decline. Equivalence test:
`tests/integration/strategy/test_growth_rate_equivalence.py`.

Facade accessor:
`StrategySessionFacade.get_colony_demographic_view(planet_id) -> ColonyDemographicView | None`.
UI should import facade/service data, not engine internals or copied production math.

`EmpireEconomyService` (`empire_economy_service.py`) is the UI-safe facade over
`EmpireEconomyCalculator`. Constructor mirrors the calculator (`registries`
required, `economy_config` and `race_registry` optional). API:
`get_snapshot(empire) -> EmpireEconomySnapshot`. `__all__` intentionally
excludes `EmpireEconomyCalculator`.

## Replay Services

Strategy-side replay persistence lives in `game/strategy/services/`; replay
capture/playback DTOs live under `game/simulation/replay/`.

`ReplayStore` (`replay_store.py`) persists battle replay sidecars below the
active save root. Key API: `set_save_root`, `clear_save_root`, `replay_dir`,
`on_battle_started`, `on_battle_ended`, `persist`, `list`, `load`,
`load_or_error`, `delete`, plus post-persist listeners.

`ReplayResolver` maps a replay ID to a persisted replay lookup. Use
`ReplayResolver.from_registries(...)` when building it from configured
registries.

`ReplayVerificationCoordinator` subscribes to `ReplayStore` post-persist
notifications, runs a single-worker FIFO background verifier, writes
verification sidecars, and exposes `start`, `shutdown`, and `wait_for_idle`.
Use `shutdown_all_coordinators(timeout=5.0)` at application shutdown.

`replay_verification_sidecar.py` owns
`REPLAY_VERIFICATION_SCHEMA_VERSION = "1.0.0"`, `VerificationStatus`,
`VerificationSource`, `VerificationSidecar`, `sidecar_path_for_replay`,
`write_verification_sidecar`, and `read_verification_sidecar`.

`replay_ship_builder.py` builds a replay playback ship builder from the replay
record, registries, and materialization context.

Tests and commands:

- Full suite: `python Tools/test_sharded/test_sharded.py`
- Replay-related focused tests live under `tests/unit/strategy/services/` and `tests/unit/simulation/replay/` where present.
- Combat Lab replay flows also use `python -m combat_lab.run_tests`.

## Mutator and Write Services

Write services implement the read/write Protocol Pair pattern. Engines receive
mutator protocols through `TurnEngineConfig.create_default(...)`; production
constructs the concrete services in `GameSession.__init__`. Data classes expose
read state; services own cross-class or external writes.

- `FleetWriteService`: `IFleetMutator` for orders, ships, hierarchy, construction queue, display name, policy. Navigation writes delegate to `FleetNavigationService`; without it, `set_location` / `set_path` raise `NotImplementedError`.
- `PlanetWriteService`: `IPlanetMutator` for populations, facilities, stockpile, staging yard, construction queue, orders, owner/atmosphere/energy/gravity/water/radiation fields. `set_owner_id` does not update `Empire.colonies`; callers must route empire membership through `IEmpireMutator`.
- `EmpireWriteService`: `IEmpireMutator` for colonies, fleets, storage, built designs, and post-battle empty-fleet pruning.
- `ShipInstanceWriteService`: `IShipInstanceMutator` for alive/derelict/HP, component replacement plus cache invalidation, cargo/consumables, carried items, toggles, activation states, XP, kills.

Do not bypass mutators from engines or other external writers unless the data
class is the documented owner of that mutation.

## Design Principles and Invariants

### Dependency Injection

Services needing registries use constructor injection with no fallback:

```python
VehicleDesignService(registries=game_registries)
ModifierLogicService(registry_provider=game_registries)
SimulationDesignLoader(registries=game_registries)
PlanetEconomyProjector(
    registries=game_registries,
    economy_config=economy_config,
    race_registry=race_registry,
)
```

Passing `None` should raise `TypeError` or `ValidationException`.

Stateless services require no constructor args: `BattleService()`,
`FleetNavigationService()`.

Static/module-level logic includes `FleetSpeedCalculator`,
`ActionTimeResolver`, `DesignCostCalculator`, `CargoTransferService`,
`FleetCargoProjector`, `ComponentInspector` functions, and
`calculate_design_stats()`.

### Result Objects

Expected validation failures should return result objects rather than raising:

```python
@dataclass
class ServiceResult:
    success: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
```

Unexpected corrupt state, invalid DI, frozen registry mutation, provider/network
failures, and serialization failures should use the project exception model.

### Layer Rules

- UI may import services.
- Services may import domain objects within allowed layer direction.
- Domain objects should not import UI.
- Simulation code must not use global registry lookup.
- UI should not directly manipulate domain objects for complex workflows; route through services, facade DTOs, commands, or mutators.
- `game/services/` must depend on Core only.

### Stale References to Avoid

- Do not reference `game/strategy/services/area_effect_manager.py`; the current path is ability sources plus `SystemEffectsCollector`.
- Do not use `calculate_fleet_speed_with_environment`; use `calculate_fleet_speed_with_strategic_mult`.
- Do not hardcode `ORDER_TO_ABILITY_MAP`; it is derived from the self-registering command registry.
- Do not treat `BuildQueueController` / `BuildQueueRenderer` as strategy services; they are UI classes under `game/ui/`.
- Do not import `IRaceRegistry` from old protocol paths; current path is `game/core/protocols/strategy_domain.py`.
- Do not add save-file migration or compatibility shims for old save/replay formats unless a project explicitly changes the no-migration policy.

## Testing

Primary service test locations:

- `tests/unit/services/`
- `tests/unit/strategy/services/`
- `tests/unit/simulation/services/`
- `tests/integration/strategy/` for engine/facade equivalence flows

Common commands:

```bash
pytest tests/unit/strategy/services/
pytest tests/unit/simulation/services/
pytest tests/integration/strategy/test_growth_rate_equivalence.py
python Tools/test_sharded/test_sharded.py
python -m combat_lab.run_tests
```

Testing pattern:

- Use strict DI fixtures such as `fresh_registries`, `minimal_registries`, or `mock_registries`.
- Assert result object `success`, `errors`, `warnings`, and returned domain fields.
- For pure services, test pure function behavior separately from mutation bridge behavior.
- For background services, assert terminal statuses and call shutdown helpers.

## Extension Checklist

Adding a cross-cutting service:

1. Confirm it depends only on Core and is useful to multiple layers.
2. Define a Protocol and at least one testable implementation.
3. Add factory/default accessors only if lifecycle requires application-wide defaults.
4. Wire through `ApplicationContext` only when it belongs in the production service graph.
5. Add focused tests before implementation.

Adding a strategy ability source:

1. Implement or wrap an `IAbilitySource`.
2. Register a provider with `ability_iterator`.
3. Ensure `affects_hex`, `affects_system`, and activation state are correct.
4. Add metadata if the ability should appear in sector/system effect rows.
5. Let `SystemEffectsCollector` aggregate.

Adding a stabilizer:

1. Add one `StabilizerSpec` to `STABILIZERS`.
2. Include ability name, spatial scopes, and blocked order types.
3. Ensure the ability is discoverable through component registry lookup.
4. Add or update tests for active/inactive behavior.

Adding a strategic superweapon:

1. Add one `SuperweaponSpec` to `SUPERWEAPONS` unless the weapon is a structural outlier like `SELF_DESTRUCT`.
2. Wire the dispatcher effect closure.
3. Add stabilizer coverage when applicable.
4. Preserve collect-then-mutate behavior for destructive system effects.

Adding a habitability axis:

1. Add a `HabitabilityFactor` to `FACTOR_REGISTRY`.
2. Verify race setup, point budget, homeworld presets, habitability formula, and population behavior.
3. Do not add parallel hardcoded factor lists.

Adding a stat panel value:

1. Add a getter in `stat_getters.py`.
2. Register it in `GETTERS`.
3. Add the stat entry to `data/stats_sections.json`.
4. For dynamic rows, add and register a generator in `stat_rows_dynamic.py` / `stats_config.py`.

Adding a replay persistence behavior:

1. Add or update replay DTO serialization tests first.
2. Keep persistence behind `ReplayStore` and lookup behind `ReplayResolver`.
3. If verification behavior changes, update `ReplayVerificationCoordinator` and sidecar schema deliberately.
4. Keep replay shutdown deterministic with `shutdown_all_coordinators()`.
