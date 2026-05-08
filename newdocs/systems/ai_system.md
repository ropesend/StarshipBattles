# AI System Compact Reference

> **Last verified:** 2026-05-08 - Checked `docs/systems/ai_system.md`, the compact ALT source, current `game/ai/`, policy JSON, and relevant AI boundary tests.

Combat AI controls autonomous ship behavior during battles. It lives in `game/ai/`, may depend on Core, Services, Engine, and Simulation, and is injected into Simulation through protocols. Simulation and Strategy code should not import concrete AI classes at module level; UI/app composition roots provide `AIControllerFactory`.

## Architecture

| Area | Files | Responsibility |
|---|---|---|
| Public API | `game/ai/__init__.py` | Exports controller, core behaviors, `PolicyManager`, `TargetEvaluator`, `AIControllerFactory`. |
| Controller | `game/ai/controller.py` | Per-ship tick loop, policy resolution, targeting, behavior selection/execution. |
| Movement | `game/ai/behaviors.py` | Direct per-ship movement/firing behaviors. |
| Spatial | `game/ai/spatial_behaviors/` | Group-relative desired-position behaviors plus anti-clumping helpers. |
| Coordination | `game/ai/group_target_coordinator.py` | Stateless focus fire, reserve commitment, flagship succession. |
| Policies | `game/ai/policy_manager.py`, `data/*_policies.json` | Lazy-loaded movement, targeting, and group policy presets. |
| Targeting | `game/ai/target_evaluator.py`, `game/ai/combat_utils.py` | Rule scoring, safe entity helpers, distance/capability/PDC checks. |
| Boundaries | `game/ai/ai_factory.py`, `game/ai/interfaces/controllable.py`, `game/ai/protocols.py` | Factory DI, `IControllable` adapter, AI-local TypeGuards. |

Layer contracts:

- `BattleEngine` consumes `IAIController` / `IAIControllerFactory` from `game/simulation/interfaces/ai_controller.py`.
- `AIControllerFactory` lives in `game/ai/` because AI can import Simulation, but Simulation must not import concrete AI classes.
- Strategy adapters accept an injected AI factory and must not import `game.ai` directly. See `tests/unit/strategy/adapters/test_no_ai_import.py`.
- N-team battles treat every non-self `team_id` as hostile. `enemy_team_id` is now a legacy hint for factory construction, not the targeting source of truth.

## AIController Tick Flow

`AIController.update()` runs once per live ship per battle tick:

1. Skip dead ships.
2. Reset engine throttle and turn throttle to `1.0`.
3. Resolve `ship.get_movement_policy()` and `ship.get_targeting_policy()` through `PolicyManager`.
4. Keep the current target if alive; otherwise call `find_target()`.
5. Fill secondary targets when `max_targets > CombatConstants.DEFAULT_MAX_TARGETS`.
6. If there is no target, disable firing and only continue for no-target behaviors.
7. Satellites acquire targets but skip movement behavior execution.
8. Select behavior: flee when HP ratio is at or below positive `retreat_hp_threshold`, otherwise use movement policy `behavior` with default `kite`.
9. Call `behavior.enter()` on behavior changes, then `behavior.update(target, policy_context)`.

No-target behaviors: `straight_line`, `rotate_only`, `erratic`, `do_nothing`, `stationary_fire`.

Target acquisition:

- Query `BattleTuning.TARGET_QUERY_RADIUS` with `SpatialGrid.query_radius_exact()`.
- Enemy ships are alive combatants whose `team_id != self.ship.get_team_id()`.
- Include missiles from `BattleTuning.MISSILE_QUERY_RADIUS` only when a targeting rule uses `pdc_arc` or `missiles_in_pdc_arc`.
- Build a distance cache once per candidate.
- Build a capability cache only for ship-like candidates; projectile candidates are intentionally skipped and guarded in `TargetEvaluator`.
- Sort by score descending and drop `-inf` candidates.

Warnings:

- PDC detection is tag-based. Use `Component.has_pdc_ability()`; do not check for a non-existent `PDCAbility` class string.
- Candidate lists can contain ships and missiles. Any targeting rule that touches components must guard with `is_combat_ship()`.
- Target evaluation catches `AttributeError` / `TypeError`, logs context, and skips the broken candidate so combat continues.

## Movement Behaviors

All direct movement behaviors extend `AIBehavior(controller)` and implement `enter()` plus `update(target, strategy)`.

| Key | Behavior | Notes |
|---|---|---|
| `kite` | `KiteBehavior` | Smooth range-keeping: radial correction plus tangent orbiting; supports collision avoidance and `throttle_limit`. |
| `attack_run` | `AttackRunBehavior` | Approach/retreat state machine with hysteresis and `PhysicsConfig.TICK_RATE` timer decrement. |
| `ram` | `RamBehavior` | Navigate straight to target position; no collision avoidance. |
| `flee` | `FleeBehavior` | Move away from target; `fire_while_retreating` controls weapon trigger. |
| `orbit` | `OrbitBehavior` | Circle target at `orbit_distance` using tangent plus radial correction. |
| `stationary_fire` | `StationaryFireBehavior` | No movement; weapon trigger stays enabled when a target exists. |
| `do_nothing` | `DoNothingBehavior` | No movement and explicitly disables firing. |
| `straight_line` | `StraightLineBehavior` | Full thrust in current facing, no rotation. |
| `rotate_only` | `RotateOnlyBehavior` | Rotate by `rotation_direction`, no thrust. |
| `erratic` | `ErraticBehavior` | Seeded random turn changes with optional `leash_radius`. |

Movement policy fields currently read by code:

| Field | Used by |
|---|---|
| `behavior` | Controller behavior lookup; defaults to `kite`. |
| `retreat_hp_threshold` | Controller flee override; ignored when threshold is `0` or below. |
| `engage_distance` | Kite range multiplier: numeric, `max_range`, `optimal_range`, `medium_range`, `short_range`, `point_blank`, or `ram`. |
| `avoid_collisions` | `KiteBehavior.check_avoidance()` toggle. |
| `throttle_limit` | `KiteBehavior` throttle cap. |
| `fire_while_retreating` | `FleeBehavior` weapon trigger. |
| `attack_run_behavior.approach_distance` | Weapon-range multiplier for attack-run approach. |
| `attack_run_behavior.retreat_distance` | Weapon-range multiplier before re-approach. |
| `attack_run_behavior.retreat_duration` | Seconds spent in retreat phase. |
| `rotation_direction` | `RotateOnlyBehavior`; `1` clockwise, `-1` counter-clockwise. |
| `turn_interval_min`, `turn_interval_max`, `leash_radius` | `ErraticBehavior`. |
| `orbit_distance` | `OrbitBehavior`. |

Stale-reference correction: `AttackRunBehavior` reads the nested key `attack_run_behavior`, while the current `data/movement_policies.json` `strafe_run` entry stores those knobs under `params`. Until data or code is reconciled with tests, `strafe_run` uses attack-run defaults for approach, retreat, and duration.

## Spatial Behaviors

Spatial behaviors compute desired positions for group members. They do not call thrust, rotate, or fire APIs directly; the controller navigates ships toward the returned position.

| Type | File | Parameters | Contract |
|---|---|---|---|
| `battle_line` | `spatial_behaviors/battle_line.py` | `spacing`, `shape` | Rigid line, wedge, or echelon relative to leader facing. |
| `column` | `spatial_behaviors/column.py` | `follow_distance` | Rigid single-file following behind a leader. |
| `screen` | `spatial_behaviors/screen.py` | `radius`, `reactivity` | Loose distribution around an anchor. |
| `escort` | `spatial_behaviors/escort.py` | `distance` | Close protection around an anchor ship. |
| `patrol_zone` | `spatial_behaviors/patrol_zone.py` | `zone_center`, `zone_radius` | Distribution inside a circular patrol zone. |
| `free_maneuver` | `spatial_behaviors/free_maneuver.py` | none | No spatial constraint; ship follows its movement policy. |

`apply_separation(positions, min_separation)` in `spatial_behaviors/base.py` returns adjusted copies and does not mutate inputs. `create_spatial_behavior(behavior_type, **kwargs)` dispatches through the package registry; unknown type strings log a warning and return `FreeManeuverBehavior`.

## Policies

`PolicyManager` is managed by `ApplicationContext` and also has module-level `get_default_policy_manager()` lazy access. Loading uses double-checked locking; reads are lock-free after load. Missing policy IDs return safe defaults:

- Targeting default: nearest target with weight `100`.
- Movement default: `kite`, `engage_distance=max_range`, `retreat_hp_threshold=0.1`, `avoid_collisions=True`.

Policy files:

| File | Current IDs |
|---|---|
| `data/targeting_policies.json` | `standard`, `sniper`, `brawler`, `anti_fighter`, `self_defense`. |
| `data/movement_policies.json` | `kite_max`, `kite_medium`, `brawl_close`, `strafe_run`, `ramming_speed`, `kite_optimal`, `hold_position`, `flee_panic`, plus `test_*` policies. |
| `data/group_policies.json` | 21 group presets split across targeting, movement, and retreat axes. |

Combat Lab / test movement policies:

| Policy ID | Behavior |
|---|---|
| `test_stationary` | `stationary_fire` |
| `test_do_nothing` | `do_nothing` |
| `test_straight_line` | `straight_line` |
| `test_rotate_right` | `rotate_only`, direction `1` |
| `test_rotate_left` | `rotate_only`, direction `-1` |
| `test_erratic` | `erratic` |
| `test_erratic_leashed` | `erratic` with `leash_radius=1000` |

Group policy status:

- `game.strategy.data.group_policy_registry.GroupPolicyRegistry` loads and validates `data/group_policies.json` using `Paths.GROUP_POLICIES_FILE`.
- `game.strategy.data.fleet_hierarchy.CombatPolicy` has independent `targeting`, `movement`, and `retreat` axes with parent inheritance.
- `game.strategy.data.fleet_battle_adapter.FleetBattleAdapter.to_battle_ships()` still maps group movement keys to per-ship movement policies and per-ship `_targeting_policy` overrides.
- The current unified `BattleSpec` compilers (`game/strategy/combat/spec_compiler.py`, `game/ui/screens/battle_setup/spec_compiler.py`) emit empty `CombatPolicies()` placeholders and do not apply those group-policy axes to materialized ships. Verify the call path before relying on hierarchy policy overrides in `run_battle()`.

## Target Evaluation

`TargetEvaluator.evaluate(ship, candidate, rules, ...)` returns a numeric score; higher is better. A failed required rule returns `-inf`.

| Rule family | Types | Notes |
|---|---|---|
| Distance | `nearest`, `farthest`, `distance` | Uses cache when supplied, otherwise safe distance helper. |
| Mass/size | `mass`, `largest`, `smallest`, `strongest`, `weakest` | Uses candidate `mass`. |
| Speed | `fastest`, `slowest` | Uses `candidate.velocity.length()`. |
| Damage | `most_damaged`, `least_damaged` | Uses HP percentage helper. |
| Capability | `has_weapons`, `least_armor` | Guards projectile candidates before component/layer queries. |
| PDC | `pdc_arc`, `missiles_in_pdc_arc` | Applies to missile projectiles; uses `is_in_pdc_arc()`. |

Extension guidance:

- Add scoring behavior as data-driven rule handling or shared helper predicates, not scenario-specific branches in `AIController`.
- Keep caches optional and backward-compatible; evaluator paths must work without caches.
- Never hardcode ability or component class-name lists when tags, registries, protocols, or component methods exist.

## Group Coordination

`GroupTargetCoordinator` is stateless.

| Method | Contract |
|---|---|
| `select_focus_target(enemies, priority, reference_position=None)` | Filters dead enemies; `strongest`/`largest` choose highest mass, `most_damaged` chooses lowest HP ratio, `nearest` chooses closest to reference or `(0, 0)`. Unknown priority falls back to first alive enemy. |
| `compute_group_hp_ratio(ships)` | Aggregate bounded current HP divided by aggregate max HP; returns `0.0` when no positive max HP exists. |
| `should_commit_reserve(main_body_ships, threshold=0.50)` | True when aggregate HP ratio is at or below threshold. |
| `find_flagship_successor(ships, has_cnc_check)` | Heaviest alive ship passing `has_cnc_check`; returns `None` for leaderless state. |

## Integration Boundaries

`ShipControllableAdapter` implements `IControllable` over a Simulation `Ship`. The adapter surface includes position, velocity, rotation, radius, movement controls, target state, component queries, policy IDs, vehicle type, and all-components access. Do not bypass it from controller or behavior code unless deliberately extending the adapter contract.

`AIControllerFactory` current concrete contract:

1. Construct with no dependencies.
2. Call `set_grid(engine.grid)`.
3. Call `set_rng(engine.rng)`.
4. Call `create_for_ship(ship, enemy_team_id)` or `create_for_ships(...)`.

`BattleEngine.__init__()` sets grid and a pre-seed RNG on the injected factory. `BattleEngine.start_teams()` replaces that with the per-battle seeded `random.Random(seed)` before creating controllers. `create_for_ship()` raises `StateException` when grid or RNG is missing. `ErraticBehavior` requires an explicit `rng` kwarg and must not consume module-level `random`.

AI-local protocols in `game/ai/protocols.py`:

| Protocol | Surface |
|---|---|
| `IGridEntity` | `position`, `is_alive`, `team_id`, `radius` |
| `IProjectile` | `IGridEntity` plus projectile `type` |
| `IComponentHealth` | `current_hp`, `max_hp` |

TypeGuards use duck typing via `_has_attrs()` so tests can use mocks without full runtime protocol compliance.

## Extension Recipes

Add a direct movement behavior:

1. Implement an `AIBehavior` subclass in `game/ai/behaviors.py`.
2. Register the behavior key in `AIController.__init__`.
3. Add or update a movement policy in `data/movement_policies.json`.
4. Add unit coverage under `tests/unit/ai/`, usually `test_behavior_units.py` or `test_advanced_behaviors.py`.

Add a spatial behavior:

1. Add a module under `game/ai/spatial_behaviors/`.
2. Subclass `SpatialBehavior` and implement `compute_target_position()`.
3. Export it and register its type string in `spatial_behaviors/__init__.py`.
4. Cover target positions and anti-clumping interactions under `tests/unit/ai/spatial_behaviors/`.

Add a targeting rule:

1. Add the evaluator branch in `game/ai/target_evaluator.py`.
2. Keep projectile and mock safety by using protocols/TypeGuards.
3. Add policy JSON only if the rule is meant to be available to content.
4. Cover required-rule failure, cache/no-cache behavior, and projectile candidates.

Change AI factory integration:

1. Update `AIControllerFactory` and the `IAIControllerFactory` protocol together.
2. Preserve `set_grid()` and `set_rng()` setup from `BattleEngine`.
3. Run factory and determinism tests before touching battle runner flows.

## Tests And Commands

Targeted commands:

```bash
pytest tests/unit/ai
pytest tests/unit/ai/spatial_behaviors
pytest tests/unit/ai/test_policy_manager.py
pytest tests/unit/ai/test_target_evaluator_rules.py tests/unit/ai/target_evaluator/test_projectile_candidate_guards.py
pytest tests/unit/ai/test_capability_cache_pdc.py
pytest tests/unit/ai/test_ai_n_team_targeting.py
pytest tests/unit/ai/test_erratic_behavior_seeded.py
pytest tests/unit/simulation/factories/test_ai_factory.py
pytest tests/unit/strategy/adapters/test_no_ai_import.py
```

Full-suite command:

```bash
python Tools/test_sharded/test_sharded.py
```

Use `python -m combat_lab.run_tests` when AI changes affect Combat Lab scenarios or scenario policies.
