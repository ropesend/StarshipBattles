# Combat Simulation System

> **Last verified:** 2026-05-08 -- Balanced compact replacement verified against `docs/systems/combat_simulation.md`, the compact alternate, and current source/test paths. Release-note history is intentionally omitted.

Current reference for the real-time combat simulation layer: battle entry, `BattleSpec`/`BattleOutcome`, ship mechanics, strategy integration, replay capture, and extension rules.

## Core Contract

Combat simulation is spec-driven. Callers compile domain state into a `BattleSpec`; simulation runs it and emits a `BattleOutcome`.

```text
caller (Combat Lab / Battle Setup / Strategy)
  -> context-specific spec compiler
  -> BattleSpec
  -> run_battle(spec, ai_factory, ship_builder, ...)
  -> BattleEngine
  -> BattleOutcome
  -> optional spec.post_battle_hook(outcome)
```

The sanctioned headless entry is `game/simulation/battle_runner.py::run_battle`. It builds a `BattleEngine`, threads `spec.boundary` and `spec.modifier_stack`, starts teams with `engine.start_teams(...)`, drives ticks to completion, attaches telemetry according to `spec.telemetry_level`, extracts the outcome, then invokes the optional post-battle hook.

Visual battles use `game/simulation/battle_controller.py::BattleController.start_from_spec(spec, ai_factory, ship_builder=None, registry_provider=None, config=None, capture_context=None)`. It routes through the same `start_engine_from_spec` helper that `run_battle` uses, then the UI frame loop calls `controller.update()`. At battle end, `controller.get_outcome()` returns the real extracted `BattleOutcome`.

When `ship_builder is None`, both `run_battle` and `BattleController.start_from_spec` require `registry_provider`. Simulation code must not call `get_default_registry_provider()`; non-simulation composition roots may pass `registry_provider=get_default_registry_provider()`.

Do not reintroduce `BattleMode`, `BattleModeHandler`, `create_*_battle` factories, `BattleController.run_headless`, direct production `BattleEngine(...)`/`engine.start*()` entry paths, synthetic fallback outcomes, or scenario `setup(engine)` methods.

## Primary Files

| Area | Current files |
|---|---|
| Spec/outcome DTOs | `game/simulation/battle_spec.py`, `game/simulation/battle_outcome.py` |
| Runner/controller/config | `game/simulation/battle_runner.py`, `game/simulation/battle_controller.py`, `game/simulation/battle_config.py` |
| Low-level visual service | `game/simulation/services/battle_service.py` |
| Engine and end conditions | `game/simulation/systems/battle_engine.py`, `battle_end_conditions.py`, `tick_phase.py` |
| Boundaries/modifiers/formations/telemetry | `game/simulation/combat/boundary.py`, `modifier_stack.py`, `formation.py`, `telemetry.py` |
| Combat mechanics | `game/simulation/combat/damage_calculator.py`, `targeting_system.py`, `weapon_firing_system.py`, `fleet_aura_manager.py`, `combat_events.py` |
| Weapon families | `game/simulation/combat/attack_contract.py`, `weapon_registry.py`, `families/{beam,projectile,seeker,pdc}.py` |
| Ship entity | `game/simulation/entities/ship.py`, `ship_component_manager.py`, `ship_combat_engine.py`, `ship_stats.py`, `ship_stat_querier.py`, `ship_physics.py`, `ship_validator_helper.py` |
| Components/abilities | `game/simulation/components/`, `game/simulation/components/abilities/` |
| Replay | `game/simulation/replay/`, `game/strategy/services/replay_store.py`, `replay_resolver.py`, `replay_verification_coordinator.py` |

## Entry Contexts

| Context | Compiler |
|---|---|
| Combat Lab | `combat_lab/spec_compiler.py::build_test_battle_spec(scenario, registries)` |
| Battle Setup | `game/ui/screens/battle_setup/spec_compiler.py::build_manual_battle_spec(ui_state, registries, ...)` |
| Strategy | `game/strategy/combat/spec_compiler.py::build_strategy_battle_spec(fleets, sector, system, empires, settings, registries, ...)` |

Each compiler owns its source domain and emits the complete `BattleSpec`: teams, formations, entry vectors, boundary, modifier stack, telemetry level, end condition, seed, and optional post-battle hook. Strategy attaches `game/strategy/combat/post_battle_hook.py::apply_outcome_to_fleets`; Combat Lab and Battle Setup usually do not.

`build_strategy_battle_spec(..., max_ticks=N)` is a paired override: it sets both `absolute_max_ticks=N` and `end_condition=TickLimitCondition(max_ticks=N)`. This is required for weaponless truncated strategy encounters because the default `TeamEliminatedCondition` cannot end a battle where neither side can damage the other.

## Visual Mode

`BattleConfig` is only an operational-options bag for `BattleController`: `seed`, `end_condition`, `absolute_max_ticks`, `return_destination`, `show_results`, `headless`, `start_paused`, `enable_logging`, `allow_retreat`, `allow_reinforcements`, `replay_mode`, `replay_id`, and `captured_telemetry_level`.

Battle identity and variance live on `BattleSpec`, not `BattleConfig`. Removed config-style fields must stay removed: `mode`, `team_modifiers`, `global_modifiers`, `environmental_effects`, `source_fleets`, `per_tick_callback`, `test_scenario`, and `map_bounds`.

`ReturnDestination` is canonical at `game/core/return_destination.py`, with values `BATTLE_SETUP`, `TEST_LAB`, and `STRATEGY`. `game/simulation/battle_config.py` imports it for the dataclass default, but new code should import from `game.core.return_destination` directly.

`BattleScreen` enters through `start_battle(controller)`, consumes a running controller, and shows results from `controller.get_outcome()`. Tests that need a minimal visual battle should use `tests/fixtures/battle.py::make_minimal_spec` plus `BattleController.start_from_spec`.

`BattleService` remains a low-level wrapper around `BattleEngine` for visual controller integration. Its direct `create_battle`/`add_ship`/`start_battle` path is legacy 2-team shaped; the current spec-in path is `BattleController.start_from_spec -> start_engine_from_spec -> BattleService.adopt_started_engine`. Do not use `BattleService` as a new high-level battle entry.

## Spec And Outcome

`BattleSpec` contains frozen DTOs: `TeamSpec`, `TaskForceSpec`, `SquadronSpec`, `ShipSpec`, `ComponentStateSpec`, `EntryVector`, `CombatPolicies`, and `PostBattleHook`.

`BattleOutcome` contains `TeamOutcome`, `ShipOutcome`, `ShipStatus`, `EndReason`, `HitRecord`, `WeaponSummary`, `ShipStats`, and `ModifierApplication`.

Important invariants:

- Every live battle emits a real `BattleOutcome`.
- `BattleOutcome` does not carry a `winner` field. Engine/service winner queries use `BattleEngine.get_winner()`/`BattleService.get_winner()` (`team_id` or `-1` draw). Strategy maps `BattleOutcome` into `BattleResult.winner`, but strategy treats it as informational.
- `BattleOutcome.replay_id` is `str | None`; empty strings from `NullCaptureSink` are coerced to `None` during extraction.
- `BattleOutcome.teams[i].team_id` mirrors `BattleSpec.teams[i].team_id`.
- Each `ShipSpec.instance_id` should have one matching `ShipOutcome`.
- `ShipOutcome.components` is the authoritative per-component end state.

Component identity is `(component_id, instance_index)`, so duplicate components on one ship stay independent across specs, outcomes, strategy persistence, and replay.

`ComponentStateSpec` fields are `component_id`, `instance_index`, `current_hp`, `max_hp`, `status`, and `is_active`. `status` is a `ComponentStatus.name` string: `ACTIVE`, `DAMAGED`, `NO_CREW`, `NO_POWER`, `NO_FUEL`, or `NO_AMMO`. There is no component `DESTROYED` enum value; destruction is `current_hp == 0` plus inactive.

## Tick Loop

`BattleEngine` owns ships, AI controllers, projectiles, spatial grid, collision system, combat event bus, aura manager, and deterministic RNG.

Startup:

- Assign team IDs and initialize the team roster.
- Create AI controllers through injected `IAIControllerFactory`, unless pre-supplied.
- Initialize `SpatialGrid`, `ProjectileManager`, and `CollisionSystem`.
- Run `_initialize_ship()` for event bus wiring, component update, stat recalculation, and derelict check.
- Initialize `FleetAuraManager` with all ships and `spec.modifier_stack`.
- Seed per-battle RNG.

Per tick:

1. Rebuild the spatial grid with alive ships and active projectiles.
2. Update AI, ships, components, resources, physics, and fleet auras.
3. Collect attacks emitted by ships.
4. Process attacks by typed weapon family or launch request.
5. Resolve ramming collisions.
6. Update projectiles for movement, hit detection, and expiration.
7. Sample telemetry, enforce boundaries, and evaluate end conditions.

`add_ship_mid_battle()` is the only sanctioned path for reinforcements and fighter launch. It assigns an existing team ID, initializes the ship, creates/registers AI, and updates aura membership. Creating a brand-new team mid-battle is not supported.

## Boundary, Retreat, And End Conditions

`BattleSpec.boundary` is a `BoundaryRegion`; `None` means `UnboundedRegion()`. Shapes are `RectBoundary`, `CircleBoundary`, and `UnboundedRegion`, centered on `(0, 0)`.

`BoundaryEnforcementPhase` runs in the tick-phase registry. If an alive ship exits:

| `ExitPolicy` | Effect |
|---|---|
| `DESTROY` | Kill via remaining HP damage; outcome status `DESTROYED` |
| `RETREAT` | Remove from `engine.ships`, append to `engine.retreated_ships`; outcome status `RETREATED` |
| `BOUNCE` | Clamp to `closest_inside_point` and reflect velocity |
| `NONE` | No-op |

`game/simulation/managers/retreat_manager.py::RetreatManager` is visual-mode only. Its public API is `request_retreat`, `cancel_retreat`, `update`, `is_retreating`, `get_retreat_state`, and `set_on_ship_escaped`. Edge retreat navigates to the boundary; warp retreat charges over `WARP_CHARGE_TICKS` and may be interruptible. Headless strategy battles use boundary exit policy, not `RetreatManager`.

End conditions implement `IEndCondition` and serialize through `to_dict()` plus `end_condition_from_dict()`: `TeamEliminatedCondition`, `TickLimitCondition`, `TeamIncapacitatedCondition`, `NeverCondition`, `EscapeCondition`, `ShipDestroyedCondition`, `AnyCondition`, and `AllCondition`. `BattleEngine.absolute_max_ticks` is an independent safety ceiling.

For N teams, `TeamEliminatedCondition` fires when at most one team has alive ships; with `check_derelict=True`, derelict ships count as eliminated. `TeamIncapacitatedCondition` fires when at most one team can still fight or move.

## Formations And Teams

`FormationResolver` resolves starting positions from `TaskForceSpec.formation`, team `EntryVector(origin, facing)`, and ship order.

Supported shapes: `LINE_ABREAST`, `LINE_ASTERN`, `WEDGE`, `ECHELON_LEFT`, `ECHELON_RIGHT`, `SCREEN`, `CARRIER_PROTECTED`, and `CUSTOM`.

World-space conversion: local position -> rotate by `facing` degrees counter-clockwise -> translate by `origin` -> clamp to boundary. Each ship angle equals entry-vector facing.

Default formation is chosen from dominant `design_role`: carriers use `CARRIER_PROTECTED`, strike roles use `WEDGE`, defenders use `LINE_ABREAST`, scouts use `LINE_ASTERN`, and mixed/unknown/ties use `LINE_ABREAST`.

All three entry contexts support 2 to 8 teams. The engine itself has no hard team cap, but the UI/spec compilers and `resolve_team_entry_vectors` cap teams at 8. N-team entry vectors preserve the west/east placement for 2 teams and use an inward-facing ring for 3 or more.

AI treats every non-self team as hostile. There are no alliances or enemy-team preferences inside the battle engine.

## Strategy Combat

Strategy conflict resolution makes one `IBattleResolver.resolve_battle(...)` call per contested sector, regardless of how many empires are present. Allied fleets are grouped by `owner_id` into one team by the strategy spec compiler.

```python
IBattleResolver.resolve_battle(
    fleets,
    modifiers=None,
    seed=None,
    registries=None,
    environmental_effects=None,
    empires=None,
) -> BattleResult
```

`BattleResult` carries `winner`, `tick_count`, `team_survivors: dict[int, list[IPostBattleShip]]`, `replay_id`, and `replay_unavailable_reason`. Include empty survivor lists for wiped teams.

Strategy does not decide a winner. The compiler-attached `apply_outcome_to_fleets` hook is authoritative: it writes component HP/status back to `ShipInstance.components`, mutates `Fleet.ships` for `SURVIVED`, `DERELICT`, `DESTROYED`, and `RETREATED`, and prunes empty fleets via `EmpireWriteService.prune_empty_fleets`. `_resolve_combat_at_hex` observes post-hook fleet counts and reports destroyed fleet IDs; it does not remove fleets itself.

The `empires={team_id: Empire}` mapping must thread through resolver -> spec compiler -> post-battle hook so empty fleets can be pruned. Test mock resolvers should accept `empires` even when they ignore it.

Surviving opposing fleets remain co-located and can re-engage later. Combat triggering is per-fleet movement opportunity: combat fires on ticks where a fleet has a movement opportunity and fails to leave the contested sector. This avoids per-subtick repeated battles while allowing stalemates to continue.

`COMBAT_RESOLVED` event details use:

- `participating_fleet_ids`
- `surviving_fleet_ids`
- `destroyed_fleet_ids`
- `empire_id` as the lowest participating empire ID for filtering only
- `replay_id`
- `replay_unavailable_reason`

Do not add back `winner_fleet_id` or `loser_fleet_id`.

Shortcut behavior:

- `sole_survivor`: one team has combat-capable ships and another starts with no ships; no replay, reason `"sole_survivor"`.
- `no_ships`: all fleets empty; no replay, reason `"no_ships"`.
- `truncated_no_capable`: teams have ships but no team can fight; run simulator with `_BRIEF_RUN_TICK_BUDGET` (`_DEFAULT_ABSOLUTE_MAX_TICKS // 10`, currently 2000) and `TickLimitCondition`, producing a real short replay.

Diagnostic INFO logs include branch decisions (`shortcut_sole_survivor`, `shortcut_no_ships`, `truncated_no_capable`, `simulator`), simulator ticks/winner/survivor counts, and conflict-resolution entry/exit summaries. Operators can grep `battle.log` for those branch names.

## Modifier Stack And External Stats

All battle-scoped modifiers enter simulation through `BattleSpec.modifier_stack`; old `BattleConfig.team_modifiers`/`global_modifiers` style fields are gone.

`FleetAuraManager` combines ship-provided non-SELF abilities and external `ModifierStack` entries into `ship.external_stats: dict[str, float]`. Stacking is two-phase:

- Within the same `stack_group`, take MAX.
- Across different groups, SUM.

Provider auras and external entries use different top-level buckets. They do not cross-compose even if their `stack_group` strings match.

All compilers must map abilities to stat keys through `game/simulation/combat/ability_stat_registry.py`, especially `ABILITY_STAT_REGISTRY`, `emit_entries_for_ability`, `OPPONENT_SCOPES`, and `KNOWN_EXTERNAL_STAT_KEYS`. Unknown external stat keys warn once per `(stat_key, source)` via `FleetAuraManager._log_unknown_stat_key_once`.

Known strategic mappings:

- Storm shield interference -> `shield_capacity_mult`
- Team `shield_mult` -> `shield_capacity_mult`
- Team `damage_mult` -> `damage_mult`
- Flat shield bonus -> `shield_bonus_add`
- Battle Setup complex abilities (`ShieldModifier`, `DamageModifier`, `ShieldProjection`) -> stat-key entries routed by scope

For N teams, `emit_entries_for_ability(..., num_teams=N)` fans `enemy_*` entries out to every non-owner team.

External modifier sources are static for the duration of a battle. They cannot be destroyed or deactivated mid-fight because they are compiled entries, not ship entities. Destructible external modifiers must become real in-battle entities.

## Shield Formula

`ShipStatsCalculator._apply_aggregated_stats` computes:

```text
max_shields = sum_i(base_capacity_i * capacity_mult_i * shield_capacity_mult)
              + shield_bonus_add * shield_capacity_mult
```

`shield_capacity_mult` scales both real shield components and flat shield bonuses. `shield_bonus_add` is read from `ship.external_stats["shield_bonus_add"]`. External team auras do not currently populate per-component `capacity_mult`; do not double-multiply flat bonuses by `capacity_mult`.

## Telemetry

`BattleSpec.telemetry_level` is `TelemetryLevel.MINIMAL`, `NORMAL`, or `DETAILED`.

| Level | Aggregators | Outcome fields |
|---|---|---|
| `MINIMAL` | none | end reason, duration ticks, seed, per-ship status/components/pose |
| `NORMAL` | `WeaponSummaryAggregator`, `ShipStatsAggregator` | minimal + weapon summaries and ship stats |
| `DETAILED` | normal + `HitLogRecorder` | normal + `ShipOutcome.hits_taken` |

`_attach_telemetry(engine, spec)` raises `engine.combat_events.detail_level` so the event bus emits enough events for attached aggregators. `ShipStatsAggregator.sample_tick(engine)` runs once per tick for peak speed and alive/derelict tick counts.

Defaults: Strategy `NORMAL`; Battle Setup `NORMAL`; Combat Lab `DETAILED` unless scenario metadata overrides.

At `DETAILED`, `HitRecord.modifiers_applied` includes global and attacker-team modifier entries active at the time of the hit. At lower levels it is an empty tuple.

## Ship Architecture

`Ship` extends `PhysicsBody` and `ShipPhysicsMixin`. It requires explicit `registries: GameRegistries` and auto-equips the default hull component from vehicle-class data.

Key state:

- `layers: dict[LayerType, LayerData]` with `HULL`, `CORE`, `INNER`, `OUTER`, and `ARMOR`
- `resources: ResourceRegistry`
- `is_alive`, `is_derelict`
- Targeting: `current_target`, `secondary_targets`, `max_targets`
- Defense: `emissive_armor`, `shield_regenerating_armor`, `current_shields`, `max_shields`
- Offense/defense scores: `baseline_to_hit_offense`, `total_defense_score`
- Metadata: `movement_policy`, `targeting_policy`, `design_role`

Per-ship update sequence:

1. Resource regeneration.
2. Component consumption/cooldowns.
3. Arcade physics.
4. Shield/repair cooldowns through `ShipCombatEngine`.
5. Weapon firing through `ShipCombatEngine`.

Delegates:

```text
Ship
  -> combat_engine: ShipCombatEngine
       -> TargetingSystem
       -> DamageCalculator
       -> WeaponFiringSystem
  -> stats_calculator: ShipStatsCalculator
  -> stat_querier: ShipStatQuerier
  -> validator_helper: ShipValidatorHelper
  -> component_manager: ShipComponentManager
  -> resources: ResourceRegistry
```

`ShipComponentManager` owns component list structure, per-layer storage, all-component cache, and weapon-only cache. Use its accessors instead of reaching into layer dicts:

- `add_component(component, layer_type)`
- `add_components_bulk(component, layer_type, count)`
- `remove_component(layer_type, index)`
- `get_all_components()`
- `get_weapon_components_cached()`
- `get_components_by_layer(layer_type)`
- `get_components_by_ability(ability_name, operational_only=True)`
- `iter_components()`
- `find_component_with_index(predicate)`
- `has_components()`
- `clear_non_hull_components()`

List ownership is distinct from behavior managers: `ModifierManager`, `AbilityManager`, `ComponentHealthManager`, and `ComponentResourceManager`.

Cache invalidation: `_components_cache_dirty` and `_weapon_cache_dirty` flags are set on every mutation; readers rebuild the cache lazily. Always use `get_all_components()` / `get_weapon_components_cached()` rather than reaching into the underlying layer dicts — only those accessors honour the dirty flag.

## Damage Pipeline

`game/simulation/combat/damage_calculator.py::DamageCalculator.apply_damage()` stages:

1. `_absorb_shields()` uses `ship.current_shields`; early return if absorbed.
2. `_reduce_emissive_armor()` applies flat overflow reduction; early return if absorbed.
3. `_absorb_regenerating_armor()` absorbs overflow and recharges shields by absorbed amount, capped at `max_shields`; early return if absorbed.
4. `_distribute_hull_damage()` distributes remaining damage by component layers, outermost first: `ARMOR -> OUTER -> INNER -> CORE -> HULL`.
5. `_finalize_damage()` recalculates stats, updates derelict status, and emits events.

Zero or negative damage returns immediately and must not heal or mutate state.

Within a layer, component selection is weighted random by current HP. Components with more HP are more likely to be hit; each selected component absorbs `min(component.current_hp, remaining_damage)`.

After hull damage, finalization runs `ship.recalculate_stats()`, `ship.update_derelict_status()`, and emits `SHIP_DERELICT` if the flag changed. New code paths that mutate component state (HP changes, activation/deactivation, resource flips) must call `recalculate_stats()` before relying on stat reads — derived stats are cached and become stale otherwise.

`CombatEventBus` emits `SHIELD_HIT`, `ARMOR_ABSORBED`, `COMPONENT_HIT`, `COMPONENT_DESTROYED`, `SHIP_DESTROYED`, and `SHIP_DERELICT`; events carry `DamageContext` attacker identity.

Damage pipeline scenario coverage lives in `combat_lab/scenarios/damage_pipeline_scenarios.py`, including PIPELINE-001 through PIPELINE-005 and PIPELINE-007 for shield-regenerating armor recharge-cap overflow.

## Operational Status And Resources

Only active and operational components contribute stats during `recalculate_stats()`. A component is non-operational when constant-trigger `ResourceConsumption` cannot be satisfied, or when it requires command and control but no active `CommandAndControl` provider exists.

Resource storage components always contribute capacity regardless of operational status.

`RequiresCommandAndControl` is per-component, not ship-wide. A lost bridge disables C&C-dependent weapons, engines, shields, sensors, ECM, generators, hangars, and repair bays; passive armor, storage, crew quarters, life support, and strategy-only components continue.

`is_derelict` is functional: true when the ship has no operational weapons and no operational engines. It can result from C&C loss, resource depletion, crew shortage, or component destruction. Battle startup runs an initial component update so derelict status is correct before tick 1.

When `max_shields` decreases, `current_shields` is capped to the new max.

Resource aggregation is data-driven through `ShipStatsCalculator._aggregate_resource_abilities()`. It discovers resource types from `ResourceStorage`, `ResourceGeneration`, and `ResourceConsumption`; do not hardcode fuel/energy/ammo assumptions in simulation.

Strategy-relevant attributes populated by `ShipStatsCalculator` and read through `calculate_design_stats()`:

- `cargo_storage`
- `pod_storage_mass`
- `warp_resource_costs`

Do not recompute these independently in strategy.

## Targeting, Weapons, And Cooldowns

`TargetingSystem`:

- `select_target(ship, candidates)` filters dead/friendly ships and picks the closest enemy.
- `find_valid_target(ship, primary, secondaries, comp, weapon_ab)` checks range, arc, PDC missile/fighter rules, and seeker range.
- `calculate_firing_solution(ship, comp, target)` uses direct aim for beams and `solve_lead(pos, vel, t_pos, t_vel, p_speed)` (quadratic intercept; returns `t > 0`) for projectile/seeker intercepts.

PDC weapons can only target missiles and fighters (fighters detected via `vehicle_type == 'Fighter'`). Tag-driven detection only — never branch on a `PDCAbility` class string; use `Component.has_pdc_ability()`.

`WeaponFiringSystem.fire_weapons(ship, context)` iterates components:

1. Hangar launch for `VehicleLaunch` when a target exists.
2. Weapon fire when component can afford activation, weapon cooldown passes, and targeting validates.

Weapon dispatch uses the registry:

- `game/simulation/combat/attack_contract.py`: `WeaponFamily` (`BEAM`, `PROJECTILE`, `SEEKER`, `PDC`), `AttackRequest`, `BeamResolution`, `ProjectileResolution`, `NoAttack`, `WeaponHandler`, `FAMILY_METADATA`
- `game/simulation/combat/weapon_registry.py`: `WEAPON_REGISTRY`, `detect_family(component)`
- `game/simulation/combat/families/{beam,projectile,seeker,pdc}.py`: one handler per family, registered on import

PDC is detected before BEAM because PDC is a Beam-role weapon tagged `pdc`. `WeaponRegistry.dispatch` raises `UnregisteredWeaponFamilyError` when a handler is missing; do not swallow it.

Add a new weapon family by adding one family module, one `FAMILY_METADATA` entry if needed, and one import in `families/__init__.py`. Do not edit `weapon_firing_system`, `targeting_system`, `collision`, or `projectile_manager` for normal family extension.

Per-tick maintenance in `ShipCombatEngine`:

- Shield regen: `shield_regen_rate / 100` per tick, costing `shield_regen_cost / 100` energy.
- Repair: `repair_rate / 100` per tick, repairing the component with lowest HP ratio.

Speed and motion units:

- Ship `max_speed = (thrust * 25) / mass` in px/tick.
- `turn_speed = (raw * 25000) / mass^1.5` in degrees per 100 ticks; `rotate()` divides by 100 each tick.
- Projectile runtime speed = `projectile_speed / PROJECTILE_SPEED_SCALE` (constant `PROJECTILE_SPEED_SCALE = 100`) in px/tick. A `projectile_speed=20000` field becomes 200 px/tick.

## Ability System

`game/simulation/components/abilities/base.py::Ability` exposes:

- `layer`: `COMBAT`, `STRATEGIC`, or `BOTH`
- `scope`: `SELF`, `SECTOR`, `ALLIED_SECTOR`, `SYSTEM`, `ALLIED_SYSTEM`, or `PLANET`
- `stack_group`
- `tags`, such as `pdc` or `main_weapon`
- `get_primary_value()`, `get_effective_stat(stat_key)`, `recalculate()`, `update()`

`SimpleMultiplierAbility` is the common base for abilities with one numeric value modified by one stat multiplier.

Ability aggregation (`game/simulation/entities/ability_aggregator.py::calculate_ability_totals`) is two-phase:

- Within a `stack_group`, take max; components without a group each get a unique group.
- Across groups, sum numeric abilities; marker abilities are boolean OR.

Ability modules live under `game/simulation/components/abilities/`: `weapons.py`, `defense.py`, `propulsion.py`, `resources.py`, `crew.py`, `markers.py`, `cargo.py`, `superweapons.py`, `harvester.py`, `colonize.py`, and `planetary.py`. Use `docs/systems/ability_reference.md` for exact keys, parameters, data formats, and stat bindings.

## Protocols

Simulation-internal protocols live in `game/simulation/interfaces/`.

Entity protocols:

- `ICombatShip`: name, team, position, velocity, HP, shields, layers, combat engine
- `IProjectile`: owner, team, position, damage, type, target, turn rate
- `IPhysicsShip`: thrust/turn/mass/movement attributes
- `ISerializableShip`: strategic persistence fields

`IComponent` includes id, name, active flag, HP, status, ability instances, modifiers, stats, and ability stats; methods include `get_abilities`, `get_ability`, `has_ability`, `has_pdc_ability`, and `can_afford_activation`.

Ability protocols include `IAbility`, `IWeaponAbility`, `IBeamWeaponAbility`, `ISeekerWeaponAbility`, `IProjectileWeaponAbility`, `IResourceConsumptionAbility`, `IResourceStorageAbility`, `IResourceGenerationAbility`, and `IWarpJumpAbility`.

TypeGuards use duck typing for MagicMock compatibility.

## UI Visibility

Battle-scoped modifiers appear in:

- `game/ui/screens/battle_results_screen.py::_draw_ship_card`: per-ship `"Shields: current/max"` from `ShipOutcome.current_shields` and `.max_shields`.
- `game/ui/screens/battle_screen.py::get_active_modifier_labels`: live HUD labels from `FleetAuraManager.get_active_bonuses(team_id)`, formatted as `T{N} {stat_key}={value:.2f} ({source})`.

`BattleResultsScreen` consumes `BattleOutcome` through `game/ui/screens/battle_results_data.py::extract_battle_results(outcome, return_destination)`. It does not read from a live engine.

Visual hit effects are in `game/ui/effects/hit_effects.py`; `BattleScreen` subscribes to combat events and renders timer-based shield, armor, component, and ship-destroyed effects.

## Replay ID Plumbing

Strategy battle capture stores `output/saves/<save>/replays/replay_<uuid>.json` and records the UUID on `engine.replay_id`.

```text
engine.replay_id
-> BattleOutcome.replay_id
-> BattleResult.replay_id / replay_unavailable_reason
-> COMBAT_RESOLVED event details
-> EventLogDataSource replay cells
-> EventLogWindow replay click
-> ReplayResolver.resolve(...)
-> Game.start_replay(record)
-> BattleController.start_from_spec(..., replay_mode=True, ship_builder=...)
```

`NullCaptureSink.on_battle_started()` returns `""`; `extract_outcome` coerces this to `None`. Do not propagate empty replay IDs.

`replay_id` remains `None` for `sole_survivor`, `no_ships`, paths with `capture_context=None`, Combat Lab/Battle Setup runs without capture context, and legacy event rows.

## Replay Capture, Playback, Verification

Replay is not a separate engine. Playback re-runs `run_battle(spec)` with a frozen seed and reconstructed ship state.

Files in `game/simulation/replay/`:

- `replay_serialization.py`: free `to_dict`/`from_dict` pairs for simulation DTOs; `REPLAY_SCHEMA_VERSION = "2.0.0"`.
- `replay_spec.py`: `ReplaySpec`, `ReplayShipSpec`; JSON-safe mirror of `BattleSpec`.
- `replay_outcome.py`: `ReplayOutcome`.
- `replay_record.py`: `ReplayRecord` with spec, outcome, id, timestamp, sector, turn, empires, and component registry hash.
- `replay_capture.py`: `IReplayCaptureSink`, `NullCaptureSink`, `ReplayCaptureContext`, default sink accessors.
- `replay_player.py`: `build_replay_ship_builder(record)`, `replay_record_to_spec(record)`, `run_replay_headless(record, ai_factory, ship_builder)`.

Capture lifecycle:

1. `start_engine_from_spec` gets the default capture sink.
2. Sink `on_battle_started(replay_spec, context=ctx)` returns `replay_id`.
3. Engine stores `engine.replay_id`.
4. Battle runs.
5. `extract_outcome` reads/coerces `engine.replay_id`, calls `sink.on_battle_ended(replay_id, outcome)`, and sets `BattleOutcome.replay_id`.

`ReplayCaptureContext` is caller-built. Strategy supplies sector, turn, empires, ship-instance lookup, and component registry hash. Simulation must not know strategy-shaped metadata.

Playback lifecycle:

1. UI resolves `replay_id` through strategy `ReplayResolver`, which gates on schema version and registry hash.
2. `replay_record_to_spec(record)` rebuilds `BattleSpec`.
3. `build_replay_ship_builder(record)` reconstructs ships from snapshots via `ShipInstanceSerializer.from_dict()` and `ShipInstance.to_ship(...)`.
4. Headless playback calls `run_replay_headless(..., capture_context=None)`.
5. Visual playback calls `BattleController.start_from_spec(..., replay_mode=True, ship_builder=...)`; `BattleScreen` shows replay mode, hides order buttons, and skips post-battle results.

Schema `2.0.0` is current. Old replay schemas surface as `version_drift`, not migrations.

Determinism: simulation, engine, and AI hot paths must use seeded RNG. AST guards forbid unseeded `random.*` and `time.time()` in those layers. New random behavior must accept injected `Random` or seed.

Background verification:

- `game/strategy/services/replay_verification_coordinator.py` subscribes to `ReplayStore.add_on_record_persisted_listener`.
- It runs a single-worker FIFO queue, materializes ship builders through `game/strategy/services/replay_ship_builder.py`, calls `run_replay_headless(record, capture_context=None)`, runs the pure verifier, and writes sidecars.
- Sidecars are `replay_<id>.verification.json` beside the replay record. Status values: `PASSED`, `FAILED`, `ERROR`, `SKIPPED_DISABLED`, and `SKIPPED_QUEUE_FULL`.
- Settings live in `output/settings/replay_settings.json`: `verification_enabled` default `True`, `verification_queue_cap` default `16`.
- No recursion: verifier playback passes `capture_context=None`, so verification never captures another replay.
- Combat Lab fallback uses `DesignOnlyMaterializer(load_combat_lab_design)` wired at bootstrap; missing fallback for snapshotless records writes an ERROR sidecar.
- `RunLoop.run()` shutdown order is LLM calls, replay coordinators, then `pygame.quit()`.
- `game/simulation/replay/replay_verifier.py` imports only stdlib and `game.simulation.*`; strategy ship-builder reconstruction lives outside simulation.

## Extension Rules

- Add battle entry behavior by extending or creating a context-specific spec compiler, not by bypassing `run_battle`.
- Add battle-scoped effects by emitting `ModifierEntry` through `ABILITY_STAT_REGISTRY` / `emit_entries_for_ability`; keep `stack_group` explicit.
- Add ship-provided aura behavior through abilities and `FleetAuraManager`; provider auras are recalculated and removed when the provider ship is destroyed.
- Add new weapon families through `game/simulation/combat/families/`, `WeaponFamily`, `FAMILY_METADATA`, and registry import only.
- Add abilities under `game/simulation/components/abilities/`; document exact ability keys and data in the owned docs tree when source docs are allowed to change.
- Preserve seeded determinism for all replayable combat behavior.
- Preserve the strategy post-battle hook as the only authoritative fleet mutation path.
- Preserve component identity by `(component_id, instance_index)`.
- Do not add compatibility shims or migrations for old save/replay formats; old data may surface as unavailable/version drift.

## Tests And Commands

Focused tests to check when editing combat:

- `tests/unit/simulation/test_battle_runner.py`
- `tests/unit/simulation/test_battle_runner_di.py`
- `tests/unit/simulation/test_battle_runner_telemetry.py`
- `tests/unit/simulation/test_battle_runner_component_hp.py`
- `tests/unit/simulation/battle_controller/test_start_from_spec.py`
- `tests/unit/simulation/battle_controller/test_outcome_emission.py`
- `tests/unit/simulation/battle_controller/test_execution.py`
- `tests/unit/simulation/test_battle_config.py`
- `tests/unit/simulation/services/test_battle_service.py`
- `tests/unit/simulation/systems/test_battle_engine_n_teams.py`
- `tests/integration/simulation/test_three_team_battle.py`
- `tests/integration/simulation/test_four_team_battle.py`
- `tests/unit/simulation/systems/test_exit_policy.py`
- `tests/integration/simulation/test_boundary_retreat.py`
- `tests/unit/simulation/managers/test_retreat_manager.py`
- `tests/unit/simulation/combat/test_weapon_registry.py::TestExtensibilityAcceptance`
- `tests/unit/simulation/combat/test_ability_stat_registry.py`
- `tests/unit/simulation/combat/test_fleet_aura_manager_modifier_stack.py`
- `tests/unit/simulation/combat/test_fleet_aura_unknown_stat_key_warning.py`
- `tests/unit/simulation/entities/test_ship_component_manager.py`
- `tests/unit/simulation/entities/test_ship_shield_bonus_add.py`
- `tests/performance/test_contested_hex_round_budget.py`
- `tests/performance/test_telemetry_overhead.py`
- `tests/integration/strategy/test_replay_capture_e2e.py`
- `tests/integration/ui/test_event_log_replay_e2e.py`
- `tests/integration/ui/test_replay_visual_launch_e2e.py`
- `tests/integration/replay/test_capture_pipeline.py`
- `tests/integration/replay/test_replay_playback.py`
- `tests/integration/replay/test_replay_resolver.py`
- `tests/integration/replay/test_replay_store.py`
- `tests/unit/simulation/replay/test_serialization.py`
- `tests/unit/simulation/replay/test_replay_player.py`
- `tests/unit/simulation/replay/test_replay_verifier.py`
- `tests/unit/simulation/replay/test_replay_verifier_imports.py`
- `tests/unit/strategy/services/test_replay_store_eviction.py`
- `tests/unit/strategy/services/test_replay_verification_sidecar.py`
- `tests/unit/strategy/services/test_replay_verification_coordinator.py`
- `tests/integration/replay/test_verification_queue_integration.py`
- `tests/integration/replay/test_headless_visual_equivalence.py`
- `tests/integration/replay/test_verification_uses_production_materializer.py`
- `tests/integration/replay/test_combat_lab_verification.py`
- `tests/unit/test_run_loop_shutdown_ordering.py`

Stale reference corrections in this replacement:

- `tests/unit/simulation/test_unified_entry_guard.py` is not present in the current tree; unified-entry coverage is split across battle runner, controller, and DI tests listed above.
- `tests/unit/simulation/replay/test_replay_serialization.py` is now `tests/unit/simulation/replay/test_serialization.py`.
- Strategy replay resolver/store coverage is under `tests/integration/replay/` and `tests/unit/strategy/services/`, not `tests/unit/strategy/test_replay_resolver.py` or `tests/unit/strategy/test_replay_store.py`.
- `BattleOutcome.winner` is not a current field; use `BattleEngine.get_winner()` or strategy `BattleResult.winner` as appropriate.
- `ReturnDestination` is canonical in `game/core/return_destination.py`.
- Component status has no `DESTROYED` enum member.

Commands:

```bash
pytest tests/path/to/test.py -k test_name
pytest tests/ --testmon
python -m combat_lab.run_tests
python Tools/test_sharded/test_sharded.py
```
