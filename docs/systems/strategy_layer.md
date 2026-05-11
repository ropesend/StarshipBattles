# Strategy Layer System

> **Last verified:** 2026-05-11 — issue #9: per-player turn-start state helper

System documentation for the turn-based strategy layer.

## Agent Essentials

- Entry point for UI/engine communication: `game/strategy/facade/strategy_session_facade.py::StrategySessionFacade`.
- Strategy layer may depend on Core, Services, Engine, and Simulation. It must not import UI.
- UI must mutate strategy state only through facade commands or explicit UI-only state knobs called out below.
- Strategy docs use precise spatial terms: a star system is a radius-50 region; a sector is one `HexCoord`.
- Save compatibility shims are not allowed. Old saves and old replay schemas may fail to load.
- Registry-backed design/ability data usually lives outside save files; thread `GameRegistries` or a registry provider instead of assuming ability payloads are inline.

## 1. StrategySessionFacade

**File:** `game/strategy/facade/strategy_session_facade.py`

CQRS-lite boundary between UI and `GameSession`.

| Path | Contract |
|------|----------|
| Write | `handle_command(command) -> ValidationResult`; delegates to `GameSession.handle_command()` and `CommandHandlerRegistry`. |
| Turn advance | `process_turn(*, progress_callback=None)` delegates to `GameSession.process_turn()`. |
| Read | Queries return immutable DTOs from `game/strategy/facade/dto/`, never domain objects. |

DTOs include `FleetInfo`, `FleetSummary`, `StarInfo`, `SystemInfo`, `PlanetInfo`, `EmpireInfo`, `ColonySummary`, `FleetOrderInfo`, `ShipInfo`, `WarpPointInfo`, plus hierarchy DTOs (`TaskForceInfo`, `SquadronInfo`, `ShipInfoExtended`). Each DTO has a `from_<domain_object>()` constructor.

Query groups:

| Group | Methods |
|-------|---------|
| Fleet | `get_fleet`, `get_fleets_at_hex`, path preview/projection, `can_move_to`, pod/cargo state |
| System | `get_all_systems`, `get_all_stars`, `get_system_at_hex`, `get_system_near_hex`, `get_system_containing_fleet`, storm names |
| Planet | `get_planet`, `get_planets_at_hex`, `can_colonize` |
| Empire | `get_all_empires`, `get_empire`, `get_empire_colonies`, `get_empire_fleets` |
| Game state | `get_turn_number`, `get_human_player_ids`, `get_save_path` |
| Events | `get_turn_events`, `get_all_events`, `get_events_by_category` |
| Race/economy | `get_race_registry`, `get_colony_demographic_view(planet_id)` |

Performance/caching contracts:

- `_get_planet_by_id()` uses a lazy planet-index dict.
- `get_all_stars()` caches per turn.
- `FacadeSessionState` owns per-turn shared caches: planet index, fleets-by-hex, all-stars, lazy `IRaceRegistry`.
- Caches invalidate inside `process_turn()` before the new turn's commands run.
- Heavy DTO materialization such as `EconomySlice.get_colony_demographic_view` recomputes per call and is expected to be UI-driven.

Facade slice architecture:

| Slice | File | Responsibility |
|-------|------|----------------|
| `FacadeSessionState` | `_facade_state.py` | Shared caches and lazy race registry |
| `CommandDispatchSlice` | `command_dispatch_slice.py` | `handle_command` and typed `dispatch_*` helpers |
| `FleetSlice` | `fleet_slice.py` | Fleet queries, movement validation, pod state |
| `PlanetSlice` | `planet_slice.py` | Planet queries and colonization validation |
| `SystemSlice` | `system_slice.py` | System/map queries and storm names |
| `EmpireSlice` | `empire_slice.py` | Empire queries and build-queue aggregation |
| `EconomySlice` | `economy_slice.py` | Demographic/economy snapshots |
| `EventSlice` | `event_slice.py` | Event-log queries and basic session state |

Authoring rule: external callers use `StrategySessionFacade`, not slices. Facade properties exposing old private caches exist for legacy tests only.

## 2. Command Dispatch

**Files:** `game/strategy/engine/handlers/` (canonical package; PROJ-383 retired the legacy `command_handlers.py` shim)

Flow:

```text
UI -> StrategySessionFacade.handle_command(cmd)
   -> GameSession.handle_command(cmd)
   -> CommandHandlerRegistry.dispatch(cmd_name, session, cmd)
   -> ICommandHandler.execute(session, cmd) -> ValidationResult
```

`ICommandHandler` protocol:

```python
def execute(self, session: GameSession, command: Command) -> ValidationResult: ...
```

Two registries cooperate:

| Registry | File | Purpose |
|----------|------|---------|
| `CommandRegistry` | `game/strategy/engine/commands/registry.py` | Metadata registry. One `CommandSpec` per Command DTO; single source of truth for runtime handlers, `OrderType` frozensets, action-time ability map, facade helper names, and serializer codecs. |
| `CommandHandlerRegistry` | `game/strategy/engine/handlers/base.py` | Runtime registry of instantiated handlers. `dispatch(command_name, session, cmd)` calls the handler's `execute`. |

Self-registering command metadata:

- Handler classes use `@command_spec(...)`.
- The decorator is metadata-only: it attaches `__command_spec_kwargs__` and returns the class unchanged.
- Registration happens through each handler module's `register(registry)` function.
- `seed_default_commands(registry)` imports modules and calls their `register` functions.
- `reset_command_registry()` clears and reseeds without duplicate decorator-side registration.
- `commands/specs.py` is deleted; do not recreate tuple-literal command spec lists.

Adding a command:

1. Add the Command DTO to `game/strategy/engine/commands/__init__.py`.
2. Add a handler in `game/strategy/engine/handlers/<domain>.py` and decorate it with `@command_spec(...)`.
3. Add the handler to that module's `register(registry)` function; if the module is new, add it to `seed_default_commands`.
4. If a new `OrderType` is needed, update `game/strategy/data/order_types.py` and the relevant movement/action/planet-action frozenset.
5. Add focused tests under `tests/unit/strategy/engine/`.

Do not edit `registry_factory.py`, `action_time_resolver.py`, `command_dispatch_slice.py`, or `strategy_session_facade.py` for normal command additions; those surfaces derive from `CommandRegistry`. The AST guard `tests/unit/strategy/engine/test_no_specs_tuple_literal.py` blocks reintroducing a module-level `COMMAND_SPECS = (...)` tuple anywhere under `game/`.

Ownership and hot-seat rules:

- `Command` DTOs do not carry `empire_id`.
- Authorization uses `session.active_empire.id`.
- `active_empire` defaults to `empires[0]`, rotates via `StrategyGameStateManager.advance_turn`, and replaces the old non-rotating `player_empire`.
- Fleet command handlers resolve the source fleet through `BaseCommandHandler._resolve_player_fleet(session, fleet_id)`.
- Use `_resolve_fleet(empire_id=None)` only for legitimate cross-empire targets, such as an intercept target. Source-fleet authorization must already have happened.
- Planet handlers gate on `planet.owner_id == session.active_empire.id`.

Per-player turn-start UI state (issue #9):

- `StrategyGameStateManager._apply_turn_start_state(empire)` is the single source of truth for what happens when a new player takes control. It is invoked from both branches of `advance_turn`:
  - The else branch (mid-rotation, players 2..N within one full-turn cycle).
  - The true branch (full-turn rollover to player 1, after `_sync_active_empire`).
- The helper performs four ordered actions: clear `screen.selected_fleet` / `selected_object` / `last_selected_system`; centre the camera on `empire.colonies[0]`; auto-select that home colony via `screen.on_ui_selection(home_colony)` — the same code path a manual planet click takes, so `PlanetReportPanel` is populated through `ui.show_detailed_report` and selection-side concerns (e.g. `transfer_dialog.handle_external_selection`, `last_selected_system` derivation) stay consistent; and open the per-player event log scoped to `empire.id` (BUG-123).
- `process_full_turn` does NOT duplicate any of these concerns. It still returns the active empire's `turn_events` so the FEAT-20 dev-loop caller (`run_n_turns`) can aggregate them for a single combined end-of-loop log.
- The helper respects `_suppress_event_log` (FEAT-20) as a defensive guard. `run_n_turns` itself calls `process_full_turn` directly (not `advance_turn`), so the helper does not fire during dev bulk runs.

Base helper surface:

- `_resolve_player_fleet(session, fleet_id)` -> authorized source fleet or `ValidationResult`.
- `_resolve_fleet(session, fleet_id, empire_id=None)` -> optional owner check; cross-empire target path when `empire_id is None`.
- `_resolve_fleet_required(...)` -> fleet or raises.
- `_resolve_planet(...)` / `_resolve_planet_optional(...)`.

Registered command families:

| Family | Commands |
|--------|----------|
| Fleet movement | `IssueMoveCommand`, `IssueInterceptCommand`, `IssueJoinFleetCommand`, `IssueWarpCommand`, `ClearOrdersCommand`, `DeleteOrderCommand`, `ReorderOrderCommand` |
| Fleet actions | `IssueColonizeCommand`, `QueueColonizeMissionCommand`, `IssueTransferCommand`, superweapon commands |
| Construction | `IssueBuildOrderCommand`, `RemoveBuildOrderCommand`, `AddToConstructionQueueCommand`, `RemoveFromConstructionQueueCommand`, `ReorderConstructionQueueCommand` |
| Fleet structure | `SplitFleetCommand` |
| Planet orders | `IssuePlanetOrderCommand`, `ClearPlanetOrdersCommand`, `DeletePlanetOrderCommand`, `SetAtmosphereTargetCommand` |

Shared helper: `add_move_order_if_needed(session, fleet, target_hex, start_hex=None)` chains a MOVE before follow-up actions when required.

## 3. Turn Engine

**File:** `game/strategy/engine/turn_engine.py`

`TurnEngine` is a lightweight orchestrator over specialized sub-engines. Current construction uses `TurnEngineConfig.create_default(...)`; the old `create_default_turn_engine(registries)` factory was deleted.

Canonical construction:

```python
from game.strategy.engine.turn_engine import TurnEngine
from game.strategy.engine.turn_engine_config import TurnEngineConfig

cfg = TurnEngineConfig.create_default(
    registries,
    ai_factory=ai_factory,
    race_registry=race_registry,
    event_bus=event_bus,
)
engine = TurnEngine(
    registries=registries,
    config=cfg,
    ai_factory=ai_factory,
    race_registry=race_registry,
    event_bus=event_bus,
)
```

For tests, override engines with `dataclasses.replace(TurnEngineConfig.create_default(test_registries), movement_engine=mock_movement, ...)` and pass the resulting `config` to `TurnEngine`. `_NullBattleResolver` was deleted; a combat dispatch without a resolver raises `ValueError` at `ConflictResolutionEngine._resolve_combat_at_hex`.

`process_turn(empires, galaxy, save_path, *, progress_callback=None)`:

1. Run 100 tick subturn loop.
2. Run post-loop population growth, quality improvement, atmosphere/water updates.
3. Track and log per-phase timing.

Per-tick order:

| Phase | Engine | Contract |
|-------|--------|----------|
| 0 | `HarvestingEngine` | 1/100th planetary extraction; updates staging capacity. |
| 0b | `ConsumableManagementEngine` | 1/100th per-turn resource consumption. |
| 0c | `ResupplyEngine` | Facility fuel generation. |
| 0c1 | `PlanetEnergyEngine` | Energy generation/consumption and auto-deactivation; facility scans cached per planet. |
| 0d | `ResupplyEngine` | Fleet resupply from facilities. |
| 0e | `ProductionEngine` | Construction from local stockpile/fleet cargo; mid-turn completions. |
| 0f | `EnvironmentalHazardEngine` | Storm damage and fuel drain. |
| 1 | `OrderProcessor` | Instant orders such as `JOIN_FLEET`. |
| 1.5 | `ActionExecutionEngine` | Fleet action orders: colonize, transfer, superweapons. |
| 1.6 | `PlanetActionEngine` | Planet action orders; consecutive planet actions dispatch same tick. |
| 2 | `FleetMovementEngine` | Calculate paths/next moves. |
| 3 | `FleetMovementEngine` | Apply movement simultaneously. |
| 4 | `ConflictResolutionEngine` | Combat dispatch. Triggered per fleet on movement-opportunity ticks and only when the fleet actually left its hex; multiple fleets per empire become one allied team by `owner_id`. |

Post-loop engines:

- `OrganicsConsumptionEngine.process_consumption`
- `HappinessEngine.process_happiness`
- `PopulationEngine.process_population_growth`
- `QualityEngine.process_quality_improvement`
- `AtmosphereEngine.process_atmosphere`
- `WaterEngine` as applicable

Progress callback:

- Signature: `Callable[[int, int], None]`, invoked at the top of each tick with `(current_tick, TICKS_PER_TURN)`.
- Plumbing: `StrategyGameStateManager -> StrategySessionFacade -> GameSession -> TurnEngine -> _process_tick`.
- Used by Strategy UI to repaint the "PROCESSING TURN..." overlay and "Tick N / 100".
- Callback exceptions are intentionally caught/logged and suppressed; engine execution must not depend on UI callback health.
- Callback state is cleared with `try/finally`.
- Mid-turn Esc cancellation is not supported; only inter-turn cancel during multi-turn runs.

Phase descriptor execution:

- `turn_phase_registry.py::DEFAULT_TICK_PHASE_LIST` defines the 15-entry per-tick body.
- `turn_phase_registry.py::DEFAULT_END_OF_TURN_PHASE_LIST` defines the 6-entry once-per-turn body: organics -> happiness -> population growth -> quality -> atmosphere -> water.
- Each phase is a `TickPhase` with a callable target and argument resolver.
- `TurnEngine._run_phases(phases, ctx)` honors hooks, timing buckets, and wraps raw failures as `EnginePhaseError`.
- End-of-turn phases run with `tick=0`, an impossible value during the 1..100 loop and therefore an unambiguous sentinel.

Order handler registry:

| Module | Handler | Order types |
|--------|---------|-------------|
| `order_handlers/base.py` | `IOrderHandler`, `BaseOrderHandler`, `OrderHandlerRegistry`, `OrderExecutionResult` | Infrastructure |
| `join_fleet.py` | `JoinFleetHandler` | `JOIN_FLEET` |
| `colonize.py` | `ColonizeHandler` | `COLONIZE` |
| `transfer.py` | `TransferHandler` | `TRANSFER`, `LOAD_POPULATION`, `UNLOAD_POPULATION` |
| `self_destruct.py` | `SelfDestructHandler` | `SELF_DESTRUCT` |
| `superweapons.py` | `SuperweaponHandlerAdapter` x5 | `IMPLODE_PLANET`, `STELLERATE_STAR`, `OPEN_WARP_POINT`, `CLOSE_WARP_POINT`, `CREATE_DYSON_SPHERE` |
| `registry_factory.py` | `create_default_order_handler_registry(...)` | Registration entry point |

`OrderProcessor` is intentionally a thin facade. Static guards keep it from re-growing legacy helper branches: `tests/unit/strategy/engine/test_order_processor_no_legacy_helpers.py` and `tests/unit/strategy/engine/order_handlers/test_handler_registry_completeness.py`.

## 4. Fleet System

**File:** `game/strategy/data/fleet.py`

Core fleet fields:

- `id`: globally unique via `Galaxy.get_next_fleet_id()`.
- `display_name` / `name`: player-facing name; per-empire numbering is cosmetic.
- `owner_id`, `location: HexCoord`, `ships: list[ShipInstance]`, `orders: list[Order]`, `path`.
- `speed`: minimum speed across combat-capable ships.
- `construction_queue` and `construction_queue_paused`: fleet shipyard queue and pause flag.
- Hierarchy overlay: `task_forces`, `fleet_policy`, `get_unassigned_ships()`.

Fleet hierarchy is `Fleet -> TaskForce -> Squadron -> Ships`. Task forces/squadrons reference ships by `instance_id`; ships may also remain unassigned. Policies inherit from parent levels when unset.

Key hierarchy files:

- `game/strategy/data/fleet_hierarchy.py`: `BattleRole`, `CombatPolicy`, `FleetHierarchyNode`.
- `game/strategy/data/task_force.py`
- `game/strategy/data/squadron.py`
- `game/strategy/facade/dto/fleet_hierarchy_dto.py`: `TaskForceInfo`, `SquadronInfo`, `ShipInfoExtended`.

### Design Roles

Files:

- Data: `data/design_roles.json`
- Registry: `game/strategy/data/design_role_registry.py`
- Shared schema: `game/core/roles.py::Role`, `RoleRegistry`
- Classifier: `game/strategy/data/design_role.py`

Design roles classify vehicle designs for UI grouping and auto-suggestion; they do not directly change combat behavior. The Design Workshop stores `Ship.design_role`, and `ShipInstance.effective_role` returns `role_override` if set, otherwise `design_role`.

There are 27 base roles across ship combat, ship support, universal, planetary complex, and specialized categories. Role fields: `id`, `display_name`, `description`, `vehicle_type_filter`.

Layered loading order: base `data/design_roles.json` -> optional `mods/<mod>/design_roles.json` -> optional `output/design_roles_overlay.json`. Later sources override same `role_id`.

Registry API:

- `get(role_id) -> Role` raises `KeyError` on miss.
- `all() -> list[Role]`, sorted by id.
- `get_roles_for_vehicle_type(vehicle_type) -> list[Role]`, sorted by display name; empty filter matches any vehicle type.
- `add_user_role(role)` allowed because the design-role registry is runtime-mutable.
- `register_invalidation_callback(cb)` is required for any cache derived from roles.
- Reverse lookup by display name: `next((r.id for r in registry.all() if r.display_name == name), None)`.

Auto-classification helpers:

- `classify_design_role(abilities, mass)`
- `classify_from_design_data(design_data, component_registry)`

Base role inventory:

| Category | Role ids |
|----------|----------|
| Ship combat | `line_combatant`, `fleet_escort`, `interceptor`, `assault_ship`, `missile_platform`, `raider` |
| Ship support | `carrier`, `support_ship`, `scout`, `command_ship` |
| Universal | `general_purpose`, `shield_projector`, `sensor_platform`, `stellar_protector` |
| Planetary complex | `resource_harvester`, `production_facility`, `defensive_platform`, `planetary_modifier`, `research_facility` |
| Specialized | `transport`, `superweapon_platform`, `megastructure_builder`, `enrichment_facility`, `resupply_depot`, `construction_accelerator`, `colony_pod`, `assault_pod` |

### Formation, Damage, Policies

- `TaskForce.formation: FormationSpec | None`; `None` means resolve design-role default at battle start through `FormationResolver`.
- `ShipInstance.components: dict[str, ComponentState]` is the only source of truth for per-component HP. Key format: `"{component_id}#{instance_index}"`.
- Strategy combat compilation maps `ShipInstance.components` to `BattleSpec` component specs. Post-battle hook `apply_outcome_to_fleets` writes resulting HP back.
- No automatic repair between strategy battles.
- `GroupPolicyRegistry` reads `data/group_policies.json` and validates targeting, movement, and retreat preset IDs.
- Spatial behavior package: `game/ai/spatial_behaviors/`; factory `create_spatial_behavior(type_str, **kwargs)`, unknown type -> `FreeManeuverBehavior`.
- `DeploymentZoneCalculator` maps `BattleRole` to positions on a 100000x100000 battlefield; team 1 mirrors team 0.
- `GroupTargetCoordinator` is stateless: focus target, aggregate HP ratio, reserve commit, flagship successor.
- `TaskGroupSuggester.suggest_task_groups(ships)` groups by `effective_role`.

Group policy presets:

| Axis | Presets |
|------|---------|
| Targeting | `focus_strongest`, `focus_nearest`, `focus_weakest`, `distributed`, `anti_fighter`, `anti_capital`, `opportunistic` |
| Movement | `advance`, `hold_range`, `hold_position`, `pursue`, `hit_and_run`, `ram`, `evasive` |
| Retreat | `group_25`, `group_50`, `individual_15`, `individual_30`, `flagship_lost`, `ammo_depleted`, `never` |

Deployment zones for team 0:

| Role | X | Y offset |
|------|---|----------|
| `RESERVE` | 10000 | 0 |
| `MAIN_BODY` | 25000 | 0 |
| `SCREEN` | 35000 | 0 |
| `VANGUARD` | 42000 | 0 |
| `FLANKER_LEFT` | 25000 | -15000 |
| `FLANKER_RIGHT` | 25000 | +15000 |

### Fleet Delegates

Fleet delegates expose composition-based services:

| Delegate | Attribute | File | Responsibility |
|----------|-----------|------|----------------|
| `FleetConsumableAggregator` | `fleet.resources` | `fleet_consumable_aggregator.py` | Movement/warp resource costs, atomic consume, cargo capacity/load/unload, endurance. |
| `FleetCapabilityCalculator` | `fleet.capabilities` | `fleet_capability_calculator.py` | Space-yard checks, buildability, warp capability, generic ability lookup. Requires registry DI. |
| `FleetBattleAdapter` | `fleet.battle` | `fleet_battle_adapter.py` | Convert `ShipInstance` objects to simulation `Ship` objects for manual battle setup. Strategy battles now update through post-battle hooks. |
| `FleetPursuerTracker` | `fleet.pursuer_tracker` | `fleet_pursuer_tracker.py` | Tracks fleets pursuing this fleet via `MOVE_TO_FLEET` / `JOIN_FLEET`; rebuilt from orders on load, not serialized. |

Pursuer tracker rules:

- `redirect_pursuers(new_target, *, exclude=frozenset())` returns `(redirected, excluded)`.
- Use `exclude` when absorbing a pursuing fleet to prevent self-target cycles.
- Caller emits `FLEET_JOIN_CANCELLED(reason="self_target_after_redirect")` for excluded pursuers.

Mutual pursuit:

- `FleetNavigationService._is_mutual_pursuit` detects two fleets whose current head orders target each other.
- Mutual pursuers pathfind to the target's current hex instead of using asymmetric intercept prediction.
- `FleetMovementEngine._filter_jump_past_collisions` prevents swap-hex pass-through by dropping the larger fleet's queue entry for that tick; smaller `fleet.id` breaks size ties.
- Broader leapfrog and speed-balanced rendezvous are deferred.

### Ship Stats And Orders

`ShipInstance.get_calculated_stats()` delegates to simulation `calculate_design_stats()` via `Ship.from_dict()` and `recalculate_stats()`. Do not hand-roll stats by iterating design components.

Stats keys include `max_hp`, `mass`, `resource_storage`, `cargo_storage`, `pod_storage_mass`, `strategic_movement`, `warp_max_tonnage`, `warp_resource_costs`, `resource_consumption_per_hex`, `resource_consumption_per_turn`.

Call `ship.invalidate_stats_cache()` after damage, repair, or component activation changes.

Unified order system:

- File: `game/strategy/data/order_types.py`.
- `Order` and `OrderType` are used by both fleet and planet orders.
- Fleet order types: `MOVE`, `MOVE_TO_FLEET`, `WARP`, `COLONIZE`, `TRANSFER`, `LOAD_POPULATION`, superweapons, `JOIN_FLEET`, `BUILD`.
- Planet order types: `ACTIVATE_ABILITY`, `DEACTIVATE_ABILITY`.
- `IOrderable` protocol lives in `game/core/protocols/strategy_entities.py`.
- Planet orders are processed by `PlanetActionEngine`; fleet actions by `ActionExecutionEngine`.

`project_fleet_position(fleet)` in `game/strategy/services/cargo_transfer_service.py` walks queued movement/warp orders and returns the projected final hex. Used by transfer setup and move preview rendering.

### Planet Energy And Activation

Files:

- `game/strategy/engine/planet_energy_engine.py`
- `game/strategy/engine/component_activation_engine.py`
- `game/strategy/engine/planet_action_engine.py`
- `game/ui/screens/planet_abilities_window.py`

Planet energy:

1. Capacity comes from `ResourceStorage`.
2. Generation comes from `StrategicResourceGeneration`.
3. Shield/active abilities drain per tick.
4. Depleted energy auto-deactivates active abilities.
5. Energy clamps to `[0, capacity]`.

Ability lookup on facilities needs a registry provider because design JSON stores component IDs, not full ability payloads.

Per-component activation:

- Source of truth: `facility.component_states[component_key]`.
- `component_key` format: `"LAYER:INDEX:COMP_ID"`.
- `planet.active_abilities` is derived from component states; it is not serialized.
- Validating by `component_key` prevents duplicate activation of one instance while allowing multiple components with the same ability.
- Only `ACTIVE` abilities count for stabilizer protection and combat modifiers. `ACTIVATING` / `DEACTIVATING` provide no protection.

Abilities window:

- One row per activatable component instance, no dedup by ability name.
- Environment editor buttons are owned by the abilities window: atmosphere, gravity, water, radiation.
- Multi-species colonies show a species dropdown in the environment editors; "Species Ideal" uses selected species preferences.

### System Effects And Planet Modification

`game/strategy/services/system_effects_collector.py` splits effects by scope:

- System panel scopes: `system`, `allied_system`, `player_system`, `enemy_system`.
- Sector panel scopes: `sector`, `allied_sector`, `player_sector`, `enemy_sector`.

Supported effect ability set includes stabilizers, resource/build/quality boosters, shield/damage modifiers. Aggregation uses two-phase stacking through `strategic_ability_scanner.py`: intra-group MAX, inter-group MULTIPLY or SUM depending on ability kind.

Planet modification systems:

| System | File | Key model |
|--------|------|-----------|
| Atmosphere | `atmosphere_engine.py` | `planet.atmosphere`, `atmosphere_target`, `surface_pressure`; once per turn, gas mass/pressure conversion, no overshoot. |
| Water | `water_engine.py` | `planet.water_target`, moves `surface_water` toward target, clamped `[0, 1]`. |
| Gravity/Radiation | `planet_modifier_effect_engine.py` | Active modifiers apply/revert `surface_gravity` and `radiation_shielding`; habitability reads these via `FACTOR_REGISTRY` extractors. |

Atmosphere target command flow: editor -> `SetAtmosphereTargetCommand` -> handler validates ownership -> sets/clears `planet.atmosphere_target`. The editor exposes 10 gases (`N2`, `O2`, `CO2`, `H2O`, `CH4`, `H2`, `He`, `Ar`, `NH3`, `SO2`) over 0-150 kPa. "Species Ideal" reads `race_config.preferences["gas.<formula>"].setpoint` in Pa.

Atmosphere processing:

1. For each colony with `atmosphere_target`, sum `modification_rate` from operational `AtmosphereModifier` facilities.
2. Convert between mass and pressure with `Pa_per_kg = gravity / surface_area`.
3. Compute target-current delta per gas, convert to mass, distribute the available rate proportionally, and apply without overshoot.
4. Recompute `surface_pressure` from partial pressures.

Small planets change faster than large planets. An Earth-like planet at the default rate of roughly `7.8e15 kg/turn` changes by about `150 Pa/turn`, so moving to `150 kPa` is a long-running strategic process.

### Strategic-To-Combat Bridge

**File:** `game/strategy/services/combat_modifier_collector.py`

`CombatModifierCollector` collects strategic combat modifiers for fleets entering combat and returns `FleetCombatModifiers(shield_mult, damage_mult, flat_shield_bonus)`.

Important contracts:

- Enemy-scope effects are precomputed into the receiving fleet's modifiers before spec compilation.
- `SimulationBattleResolver.resolve_battle` accepts `fleets` plus a `{team_id: FleetCombatModifiers}` mapping for N-team battles.
- Spec compiler emits real stat keys through `ABILITY_STAT_REGISTRY`: shield capacity multiplier, damage multiplier, flat shield bonus.
- All `find_abilities_in_scope()` calls use `require_active=True`.
- `ConflictResolutionEngine` collects modifiers for every participating fleet and resolves one N-team battle per contested hex.

Battle Setup complex toggles:

- File: `game/ui/screens/battle_setup/spec_compiler.py::_complex_to_entries`.
- Synthetic complex designs emit `ModifierEntry` records for `ShieldProjection`, `ShieldModifier`, `DamageModifier`.
- Routing uses shared `OPPONENT_SCOPES` and `emit_entries_for_ability`.
- Adding a combat-affecting ability should usually be a registry edit in `ABILITY_STAT_REGISTRY`; tests glob `qs_*_complex.json` designs.

Current activatable abilities:

| Ability | Blocks / effect | Default scope | Timing / drain notes |
|---------|-----------------|---------------|----------------------|
| `PlanetaryShield` | Planet bombardment | system | Values come from component data. |
| `GeologicStabilizer` | `IMPLODE_PLANET` | planet/sector/system | Values come from component data. |
| `StellarStabilizer` | `STELLERATE_STAR`, `CREATE_DYSON_SPHERE` | system | 250 ticks activate, 150 deactivate, 250 energy/turn by default. |
| `WarpFieldStabilizer` | `OPEN_WARP_POINT`, `CLOSE_WARP_POINT` | system | 250 ticks activate, 150 deactivate, 150 energy/turn by default. |
| `GravityModifier` | Overrides planet gravity | self | 15 ticks activate, 5 deactivate, 30 energy/turn. |
| `RadiationShield` | Adds radiation shielding | self | 15 ticks activate, 5 deactivate, 20 energy/turn. |
| `ShieldModifier` | Fleet shield multiplier in combat | varies | Typically 15-25 ticks activate, 5-10 deactivate, 30-50 energy/turn. |
| `DamageModifier` | Fleet damage multiplier in combat | varies | Typically 15-25 ticks activate, 5-10 deactivate, 30-50 energy/turn. |
| `ShieldProjection` | Flat shield bonus in combat | varies | Typically 15-25 ticks activate, 5-10 deactivate, 30-50 energy/turn. |

### Activatable Ability Extension Checklist

1. Define ability class in `planetary.py` with energy/activation/deactivation/scope fields.
2. Register in `ABILITY_REGISTRY`.
3. Add to `_ACTIVATABLE_ABILITIES` in `planet_energy_engine.py`.
4. Data-driven abilities window discovery requires `activation_time` in component data; add display override only when CamelCase humanization is wrong.
5. Add display name to `_ACTIVATABLE_DISPLAY_NAMES` in `strategy_detail_fmt.py`.
6. If it blocks superweapons, add a `StabilizerSpec` in `stabilizer_registry.py`.
7. If system/sector scoped, add to `SYSTEM_EFFECT_ABILITIES`.
8. If combat-affecting, extend `combat_modifier_collector.py` with `require_active=True`.
9. Add keyboard/UI wiring as needed.
10. Add component data, QS complex design with `design_role`, tests, and ability/strategy docs.

Adding an environment editor:

1. Add the editor window class, following `gravity_target_editor.py` plus `species_selector_mixin`.
2. Add `(ability_key, label)` to `ENVIRONMENT_EDITORS` in `planet_abilities_controller.py`. This list routes editor windows; it is not a behavior gate for abilities.
3. Add an `_open_*_editor()` method to `strategy_event_router.py`.
4. Wire the editor in `strategy_window_manager.py:_open_planet_editor()`.

Stabilizer pattern:

- `game/strategy/services/stabilizer_registry.py` maps ability names + scopes to blocked `OrderType`s.
- Superweapon handlers call the registry; do not hand-roll scans.
- Thread `component_registry` through every superweapon handler. Without it, the scanner returns nothing, every stabilizer is silently ineffective, and the UI may still show "Active" while the block never fires. Integration test guards this regression.

System destruction pattern:

- Use `game/strategy/services/system_destroyer.py`.
- `collect_system_contents(system, galaxy, empires)` snapshots all planets, stars, and fleets within `SYSTEM_RADIUS_HEXES = 50`.
- `destroy_system(plan, galaxy, empires)` mutates from the snapshot.
- Do not hand-roll system-wide fleet enumeration.

Build queue source DI:

- File: `game/strategy/data/build_queue_source.py`.
- Collectors accept optional `registries`; callers should pass `session.registries`.
- `colony_has_planetary_yard(colony, registries)` requires registries for ability lookup.

Strategy UI widget architecture:

- `StrategyUI` stores `StrategyWidgets` and delegates attribute access via `__getattr__`.
- `StrategyDetailFormatter` uses the same pattern. New widgets added to `StrategyWidgets` become accessible without manual unpacking.

## 5. Event System And Replays

Files:

- `game/strategy/events/event_types.py`
- `game/strategy/events/event_log.py`
- `game/strategy/services/replay_store.py`
- `game/strategy/services/replay_resolver.py`

Events:

- Event categories: `PRODUCTION`, `COLONIES`, `COMBAT`, `SUPERWEAPONS`, `FLEET_OPERATIONS`, `PLANET_OPERATIONS`, `ALL`.
- Event types currently include `SHIP_BUILT`, `COMPLEX_BUILT`, `COLONY_FOUNDED`, `COMBAT_RESOLVED`, `PLANET_DESTROYED`, `STAR_DESTROYED`, `WARP_POINT_OPENED`, `WARP_POINT_CLOSED`, `DYSON_SPHERE_CREATED`, `SHIPS_SELF_DESTRUCTED`, `RESOURCE_SHORTAGE`, `FLEET_JOINED`, `FLEET_JOIN_REDIRECTED`, `FLEET_JOIN_CANCELLED`, `SHIELD_ACTIVATED`, `SHIELD_DEACTIVATED`, and `SHIELD_AUTO_DEACTIVATED`.
- Event fields: `event_type`, `category`, `turn`, `empire_id`, `message`, `details`.
- Event log methods: `append`, `get_events_for_turn(turn, *, empire_id=None)`, `get_events_by_category(category, *, empire_id=None)`, `get_all_events`, `get_events_for_empire(empire_id, *, include_global=True)`, serialization.
- Shield events come from `PlanetActionEngine` and `PlanetEnergyEngine`.

Per-empire scoping:

- `Event.empire_id == -1` is broadcast/global.
- UI filters by `scene.current_empire.id`, not a cached session creator.
- Server authorization uses `session.active_empire.id`; UI scoping uses `scene.current_empire.id`.
- `EventLogWindow` can show the empire name in its title to make scoping visible.

Replay persistence:

| Service | Contract |
|---------|----------|
| `ReplayStore` | Implements simulation `IReplayCaptureSink`; writes one JSON sidecar per battle at `output/saves/<save>/replays/replay_<uuid>.json`; atomic temp-file + replace; ring-buffer cap defaults to 50. |
| `ReplayResolver` | `resolve(replay_id) -> ReplayLookup`; never raises; returns found/missing/corrupt/version_drift/registry_drift states for UI. |

`ReplayStore` active-save coupling:

- `set_save_root(path)` / `clear_save_root()` select the target replay folder.
- `SaveGameService.save_game()` and `.load_game()` notify the store so replays pair with the active save.
- `_PendingCapture` tracks in-flight battles between start/end callbacks.

Resolver outcomes:

| State | UI behavior |
|-------|-------------|
| missing/corrupt/version drift | Disabled button or message; no crash. |
| found + registry drift | Confirmation warning, then launch if player continues. |
| found + no drift | Launch directly. |

Background verification sidecars:

- Each replay may get `replay_<uuid>.verification.json`.
- `ReplayVerificationCoordinator` subscribes through `ReplayStore.add_on_record_persisted_listener`.
- Sidecar statuses: `PASSED`, `FAILED`, `ERROR`, `SKIPPED_DISABLED`, `SKIPPED_QUEUE_FULL`.
- Sidecar deleted with replay delete/eviction.
- `ReplayLookup.verification_status` lets UI show a badge without another resolver call.
- Production wiring starts coordinator in `game/app_bootstrap.py`; shutdown occurs in `RunLoop.run()` before `pygame.quit()`.

Replay UI wiring:

- Combat events store `Event.details["replay_id"]` and optional `replay_unavailable_reason`.
- Event Log uses a `replay_action` column.
- Click flow: table action -> row `replay_id` -> `ReplayResolver.resolve` -> launch, confirm, or explain disabled reason.
- Launch path builds `BattleConfig(replay_mode=True, replay_id=..., captured_telemetry_level=...)` and routes through `Game.start_replay(record)` / `screen_router.start_battle(config=...)`.
- `BattleScreen` shows "REPLAY MODE" while replay is active.
- `shortcut_no_capable` now runs a brief simulator replay; `sole_survivor` and `no_ships` remain shortcut-only with honest unavailable reasons.
- Deferred: scrubbing, playback speed, replay browser, Combat Lab/Battle Setup capture.

## 6. Galaxy Generation

Key files:

- `game/strategy/data/galaxy.py`: `Galaxy` facade.
- `game/strategy/data/galaxy_state.py`: encapsulated `GalaxyState`.
- `game/strategy/data/star_system.py`: `StarSystem`, `WarpPoint`.
- `game/strategy/data/galaxy_protocols.py`: read protocols such as `IGalaxySystemGraph`, `IGalaxySpatialQuery`, `IHabitabilityCalculator`, `IStockpileHolder`, `IStagingYardHolder`.
- `game/strategy/data/galaxy_system_generator.py`, `galaxy_warp_generator.py`.
- `game/strategy/generation/placement_strategies.py`, `region_classifier.py`.
- `game/strategy/data/stars.py`, `data/spectrum.py`, `generation/star_generator.py`, `planet_gen.py`, `classification_config.py`, `resource_generation_config.py`, `star_generation_config.py`, `orbital_generation_config.py`.
- `game/core/spectrum_math.py`: pure spectrum math helpers split from `stars.py`.
- `game/strategy/services/planet_query_service.py`, `planet_habitability_service.py`, `galaxy_pathfinding_service.py`, `intercept_calculator.py`.
- `game/strategy/generation/storm_generator.py`.
- `game/strategy/generation/loaders/astrophysics_loader.py`, `data/astrophysics.json`.

`Galaxy` composition:

- `GalaxyState`: owned mutable state object.
- `GalaxyEntityRegistry`: planet/fleet ID lookup.
- `GalaxySpatialIndex`: hex-to-system spatial queries.
- `GalaxyWarpGenerator`: warp lanes.
- `GalaxySystemGenerator`: star system placement.
- `GalaxyPathfindingService`: pathfinding over system graph and sectors.
- `InterceptCalculator`: fleet intercept calculations.

`Galaxy`, `Planet`, and `Star` are now facade/delegate classes with LOC and method-body guards. Keep new behavior in focused services rather than growing those data classes back into god classes. `Planet` query-style behavior routes through `PlanetQueryService`; habitability multiplier lookup routes through context-injectable `PlanetHabitabilityService`; serde lives in `planet_serde.py`.

`StarSystem` contains `name`, `global_location`, optional `region_id`, `stars`, `planets`, `warp_points`, `storms`.

Pipeline:

1. Place systems through `ISystemPlacementStrategy`.
2. Generate stars.
3. Generate planets: types, atmospheres, resources.
4. Generate warp points.
5. Generate storms.
6. Classify regions.
7. Assign planet images.

Placement:

- `RandomPlacementStrategy`: uniform random within radius, reject if too close.
- `DensityBasedPlacementStrategy`: rejection sampling weighted by density map.
- Both use `SpatialIndex` for average O(1) min-distance checks.

Data-driven generation:

| Area | Config | Notes |
|------|--------|-------|
| Planet resources | `resource_generation` in `astrophysics.json` | Mass scaling, quantity/quality weights, per-type affinities; every planet has some of each resource. |
| Stars | `star_generation` | Type weights, mass generation, multi-star probabilities, companion spacing. |
| Orbitals | `orbital_generation` | Safe offsets, planet count, mass bias, moons, tectonics, magnetic field, surface water. |

Galaxy size contract:

- `GameConfig.system_count` is bounded `1 <= N <= 150`.
- Default is `DEFAULT_SYSTEM_COUNT = 2`; New Game UI imports this constant.
- `N = 1`: shared-system mode. All empires start in the one system on distinct planets; no warp lanes; layout retries up to 10 times (perturbing `galaxy_seed` per attempt) if too few planets, with `Empire.colonies` cleared between attempts. A per-system `next_planet_in_system` counter prevents silent `Planet.owner_id` overwrites; if the planet supply is exhausted, assignment is skipped with a `WARNING` log rather than overwriting another empire's home.
- `N >= 2`: separated mode. Every empire gets a distinct system; `len(players) > system_count` is invalid.
- Home systems are distributed by hand-rolled linspace: `round(i * (N - 1) / (E - 1))`.
- Warp connectivity for `N >= 2` is guaranteed by enumerating all system pairs and building a Kruskal MST; max 150 systems keeps cost trivial.
- New Game slider maps `[0, 1000]` to system count with `1 + 149 * (t / SLIDER_T_MAX) ** 2`; inverse positions the thumb from a default.

## 7. Race Preferences And Habitability

Files:

- `game/strategy/data/environmental_preference.py`
- `game/strategy/data/habitability_factors.py`
- `game/strategy/data/race_config.py`
- `game/strategy/formulas/habitability.py`
- `game/strategy/data/race_point_budget.py`
- `data/homeworld_presets.json`

Race environmental preferences are registry-driven: every habitability axis is one `HabitabilityFactor` in `FACTOR_REGISTRY`; formulas and UI iterate the registry. Legacy ad-hoc `RaceConfig` ideal/tolerance fields are gone — see the field-replacement table below.

Core model:

```python
EnvironmentalPreference(setpoint, tolerance, min_value, max_value, step)
HabitabilityFactor(id, display_name, unit, display_scale, weight,
                   default_setpoint, default_tolerance, min_value, max_value,
                   step, extractor, scorer)
```

Factor set: 17 total.

| Group | Factors | Weight notes |
|-------|---------|--------------|
| Scalar | gravity, temperature, pressure, water, radiation, magnetic, tectonic | Weights 1.0, 1.0, 0.9, 0.8, 0.6, 0.6, 0.4. |
| Gas | O2, N2, CO2, H2O, CH4, H2, He, Ar, NH3, SO2 | Each weight 0.15; gas bucket total 1.5. |

Defaults worth preserving:

- `gas.O2`: setpoint 21000 Pa, tolerance 5000.
- `gas.N2`: setpoint 79000 Pa, tolerance 20000. The non-zero N2 default is load-bearing: without it, an unconfigured Earth-like default race would silently flunk every Earth-like planet (8σ N2 mismatch drags composite score from 1.0 to 0.82).
- Other gases default setpoint 0 (`"don't want this gas"`) and tolerance 10000.
- Total weight is 6.8.

Habitability formula:

- Weighted geometric mean over all factors.
- Score floor `1e-10`.
- Default scorer: Gaussian `exp(-0.5 * ((value - setpoint) / tolerance) ** 2)`, with missing value coerced to `0.0`.
- A weight-1 scalar at zero score strongly tanks habitability; one low-weight gas at zero score only partially tanks it by design.

Adding a new factor:

1. Add to `_SCALAR_FACTORS` or `_GAS_FORMULAS` in `habitability_factors.py`.
2. `calculate_habitability`, `RaceConfig.__post_init__`, race point budget, and `RaceEnvironmentPanel` pick it up automatically.
3. Homeworld presets can omit it and keep the registry default.

Homeworld preset shape (`data/homeworld_presets.json`, 11 presets):

```json
{
  "id": "CONTINENTAL",
  "name": "Continental",
  "description": "Earth-like world with varied terrain and temperate climate",
  "preferences": {
    "gravity":     { "setpoint": 9.81,    "tolerance": 2.94 },
    "temperature": { "setpoint": 293.0,   "tolerance": 50.0 },
    "water":       { "setpoint": 0.6,     "tolerance": 0.2 },
    "gas.O2":      { "setpoint": 21000.0, "tolerance": 5000.0 },
    "gas.N2":      { "setpoint": 79000.0, "tolerance": 20000.0 }
  }
}
```

`apply_preset_to_config(preset, race_config)` overlays only listed factors — partial-override semantics so presets stay stable when new factors land in the registry.

Race point budget:

- Setpoint movement is free.
- Tolerance deviation costs `_exponential_cost(steps) = 2 ** steps - 1`.
- Methods: `calculate_aptitude_cost`, `calculate_preferences_cost`, `calculate_reproduction_cost`, `calculate_total_cost`, `get_remaining_points`, `get_breakdown`.
- Reproduction below default uses linear refund so the 0.5% floor returns exactly -5 points.

Legacy field replacements:

| Old | Replacement |
|-----|-------------|
| `gravity_ideal/tolerance` | `preferences["gravity"].setpoint/tolerance`, divide by 9.81 for g display. |
| `temperature_ideal/tolerance` | `preferences["temperature"].setpoint/tolerance` |
| `water_ideal/tolerance` | `preferences["water"].setpoint/tolerance` |
| `atmosphere_preferences[gas]` | `preferences[f"gas.{formula}"].setpoint` in Pa |
| `radiation_tolerance` | `preferences["radiation"].tolerance` and sometimes setpoint |
| `aptitude_happiness` | `base_happiness` |
| `aptitude_population_growth` | `base_reproduction_rate` |

UI:

- `RaceEnvironmentPanel` renders one reusable `PreferenceRow` per scalar/gas factor.
- Environment editors read selected species preferences for "Species Ideal" / "Auto".

LLM race descriptions:

- Files: `race_caption_loader.py`, `race_description_prompt_builder.py`, `race_description_llm_controller.py`; tools in `Tools/captioning/`.
- Visual captions are pre-baked sidecars; runtime LLM is text-only.
- Missing/malformed captions degrade to a "no visual reference" marker.
- `RaceDescriptionLLMController` is pygame-free, owns background calls for bio/socio, supports cancel, and uses Pattern #28 background service call.

## 8. Colony Demographics Loop

Per-turn demographic pipeline after the 100-tick loop and before quality/environment updates:

```text
OrganicsConsumptionEngine.process_consumption
-> HappinessEngine.process_happiness
-> PopulationEngine.process_population_growth
```

Data model:

- `ColonySpeciesConfig` at `game/strategy/data/colony_species_config.py`.
- Attached to `Planet.species_configs: dict[race_id, ColonySpeciesConfig]`.
- `Planet.get_species_config(race_id)` lazy-creates and stores configs.

Fields:

| Field | Contract |
|-------|----------|
| `food_allocation` | Player scalar, default 1.0, UI slider 0-5 with typed override; scales upkeep and happiness/growth. |
| `last_consumption_ratios` | Transient per-resource `supplied / needed`, cleared and overwritten each turn; not serialized. |
| `last_food_ratio` | Computed min of consumption ratios, fallback 1.0; Liebig's Law minimum. |
| `last_food_surplus` | Computed `food_allocation * min(ratios)`, fallback 1.0; feeds surplus happiness bonus. |

Population consumption:

- `data/economy.json::population_consumption` declares resource -> per-pop-per-turn rate.
- `EconomyConfig` loads it through default accessors; fallback is `{"organics": 0.001}`.
- `primary_resource` is first insertion-order key for UI labels.
- `surplus_food_bonus_per_x` and `surplus_food_bonus_cap` default to 0.20.

Formulas:

- Consumption: for each declared resource, `needed = pop.count * cfg.food_allocation * per_pop_rate`; drain available; write ratio or 1.0 if `needed == 0`.
- Happiness: `raw = race.base_happiness * cfg.last_food_ratio * habitability`, plus surplus bonus when `last_food_surplus > 1`, then clamp to `[0, 3]`.
- Growth: `(race.base_reproduction_rate * last_food_ratio) * P * (1 - P / K_eff) * happiness + decline_term`, where `K_eff = max(1, planet.max_population * habitability)` and starvation decline uses `DECLINE_RATE = 0.02`.

Multi-species resolution:

- `HappinessEngine` and `PopulationEngine` accept optional `race_registry: IRaceRegistry`.
- With registry, each `pop.race_id` uses its own `RaceConfig`.
- Without registry, fallback to `empire.race_config` only when `race_id` matches the empire primary race. When `race_id` does NOT match, the species is gracefully skipped (count and happiness unchanged) — no error, and the empire's primary `RaceConfig` is NOT silently substituted. This closed an earlier dual-return bug where non-primary species silently used the wrong `base_happiness` / `base_reproduction_rate`.
- `GameSession.race_registry` lazily builds `CachedRaceRegistry(RaceLibrary())` and threads it through `TurnEngine`.

UI:

- `FoodAllocationEditor` shows one row per species with slider, typed input, and multi-resource preview.
- Opens from `PlanetAbilitiesWindow` when colony has population.
- Writes directly to `ColonySpeciesConfig`; no command dispatch because this is a UI/player dial, not replayed strategy command semantics.

Changing consumed resources:

1. Edit `data/economy.json::population_consumption`.
2. Ensure each referenced resource exists in `data/resources.json` and can be harvested.
3. Restart or swap cached config via `set_default_economy_config`.
4. Remember min-aggregation: one missing required resource can starve the species.

## 9. Colony Economy Multiplier

**File:** `game/strategy/formulas/colony_output.py`

`planet_habitability_multiplier(planet, race_registry)` scales harvest and production. It is a population-weighted mean across all species on the colony.

Integration:

- `HarvestingEngine._harvest_resource`: multiply after quality and boosters, before `tick_fraction`.
- `ProductionEngine._process_queue_tick_dynamic`: scale production-rate dict up front.
- `TurnEngine.process_turn`: calls `set_current_turn(session.turn_number)` on harvesting/production engines before the tick loop so planet habitability multiplier cache invalidates per turn.

Net habitability effects: carrying capacity, happiness, harvest rate, and production rate.

Projection helpers:

- `projected_growth_rate(planet, pop, race_config, cfg) -> float`: pure per-capita next-turn growth.
- `PlanetEconomyProjector.project(planet) -> dict[resource_id, ResourceProjection]`: pure harvest/upkeep/yard/net projection.
- `StrategySessionFacade.get_colony_demographic_view(planet_id)`: facade DTO combining per-species and per-resource state.

Equivalence tests pin projection math to engine math:

- `tests/integration/strategy/test_growth_rate_equivalence.py`
- `tests/integration/strategy/test_projector_drain_matches_engine.py`

Rule: if projection and engine math drift, update both; do not silence tests.

UI surfaces:

- `PlanetReportPanel` consumes `ColonyDemographicView` for per-species blocks and transposed resource grid.
- Resource grid shape: one column per resource (icon + 3-letter abbrev header), 8 metric rows: `Qty / Qual / Harvest / Upkeep / Yard / Net / Stored / Cap`. Adding a resource to `data/resources.json` adds a column with no UI code change.
- Sign convention: harvest as-is, upkeep + yard rendered as drains via negation, net as-is. Net cells are colour-tinted (healthy/critical/zero).
- Same render path handles owned and unowned planets; unowned planets show intrinsic `Qty / Qual / Stored / Cap` and blank (`-`) flow rows.
- `EmpireTreasuryPanel` renders "Population Upkeep" from `EmpireEconomySnapshot.total_population_upkeep`, hidden when zero.
- Uncolonized-planet habitability list scores resident species through `calculate_habitability`, sorted best-fit first.

## 10. Universal IAbilitySource Framework

Any "thing at a hex/system projects effects" uses `IAbilitySource`.

Pipeline:

```text
entities at hex/system
-> IAbilitySource adapters
-> ability_iterator registered providers
-> system_effects_collector
-> collect_sector_effects / collect_system_effects
-> aggregate_multipliers / aggregate_rates
-> consumers: movement, hazards, spec compiler, system tree panel
```

Key files:

- `game/core/protocols/strategy_entities.py`: `IAbilitySource`, `is_ability_source`.
- `game/strategy/services/ability_sources/`: adapters such as `FacilityAbilitySource`, `StormAbilitySource`, plus intrinsic ability helpers.
- `game/strategy/services/ability_iterator.py`: provider registration and iteration.
- `game/strategy/services/system_effects_collector.py`: collection and helpers.
- `game/strategy/services/strategic_ability_scanner.py`: two-phase aggregation.

Intrinsic ability chance:

- Per-ability `chance` field on registry templates defaults to 1.0.
- Today populated by `data/planet_types.json` for rare planet effects.
- Templates without `chance` consume no extra RNG draws, preserving determinism for unchanged data.

Storm migration:

- Storms declare `abilities: dict[str, Any]` matching components data.
- Five storm types in `data/storms.json` v2.0 cover shield, thrust, strategic speed, environmental damage, fuel drain.
- Overlapping storms multiply per provider; tests pin two ion storms as `0.5 * 0.5 = 0.25`.

Storm coordinate frame:

- `StormAbilitySource.system` is set by the provider.
- `affects_hex(global_hex)` translates local storm coordinates with `system.global_location`.
- Test fixtures MUST use a non-zero `system.global_location`. With a zero origin, local and global coordinates coincide and a storm-coordinate translation bug will silently pass; three known fixtures rely on this rule.

Combat consumption:

- `spec_compiler._entries_from_sector_effects` emits one `ModifierEntry` per ACTIVE provider.
- ShieldModifier, DamageModifier, and ThrustModifier flow through `ABILITY_STAT_REGISTRY`.

Removed legacy:

- `AreaEffectManager`
- `EnvironmentalEffects`
- `StormEffect`
- `Storm.effects`
- `IStorm.effects`
- `_entries_from_environmental_effects`

Old saves with the legacy `effects` shape fail to load by policy.
