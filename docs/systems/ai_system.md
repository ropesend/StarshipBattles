# AI System Architecture

This document describes the combat AI system that controls autonomous ship behavior during battles.

---

## Architecture Overview

```
game/ai/
  __init__.py                  # Public API exports
  controller.py                # AIController - per-ship decision loop
  behaviors.py                 # Movement behavior classes (11 total)
  spatial_behaviors/            # Spatial positioning system (6 behaviors)
    __init__.py                  # Factory: create_spatial_behavior()
    base.py                      # SpatialBehavior ABC + apply_separation()
    battle_line.py               # Rigid line/wedge/echelon
    column.py                    # Rigid single-file following
    screen.py                    # Loose orbit around anchor
    escort.py                    # Loose close-protection
    patrol_zone.py               # Loose zone coverage
    free_maneuver.py             # No spatial constraints
  group_target_coordinator.py  # Focus fire, reserves, flagship succession
  strategy_manager.py          # StrategyManager (via ApplicationContext) - loads/resolves strategies
  target_evaluator.py          # TargetEvaluator - scores potential targets
  combat_utils.py              # Shared helpers (distance, HP, PDC arc checks)
  ai_factory.py                # AIControllerFactory - two-phase creation
  protocols.py                 # IGridEntity, IProjectile, IComponentHealth protocols
  interfaces/
    __init__.py
    controllable.py            # IControllable ABC + ShipControllableAdapter
```

**Layer Rule:** The AI package depends on `game.core` and `game.simulation` but nothing depends on AI. The simulation layer interacts with AI controllers through the `IAIController` protocol.

---

## AIController

`AIController` is the per-ship decision-maker, called once per tick by BattleEngine.

### Update Cycle (`update()`)

1. **Alive check** -- dead ships do nothing.
2. **Throttle reset** -- set engine and turn throttle to 1.0.
3. **Strategy resolution** -- `StrategyManager.resolve_strategy(ship.ai_strategy)` returns targeting rules and movement policy.
4. **Target acquisition** -- reuse current target if alive, otherwise call `find_target()`.
5. **Secondary targets** -- if ship has multiplex tracking (`max_targets > 1`), find additional targets.
6. **Behavior selection** (see flowchart below).
7. **Behavior execution** -- call `behavior.update(target, context)`.

### Behavior Selection Flowchart

```
Is HP <= retreat_hp_threshold?
  YES -> 'flee'
  NO  -> Use movement policy behavior (default: 'kite')
```

Satellites skip movement entirely after target acquisition.

### Targeting Pipeline

1. Query spatial grid within `TARGET_QUERY_RADIUS` for alive enemy combatants.
2. Optionally include enemy missiles within `MISSILE_QUERY_RADIUS` (if strategy has PDC rules).
3. Pre-compute distance cache and capabilities cache (weapons, PDC) for all candidates.
4. Score each candidate via `TargetEvaluator.evaluate()` using strategy targeting rules.
5. Sort by score descending; highest becomes primary target.
6. For multiplex tracking, repeat excluding primary to fill secondary slots.

---

## Movement Behavior System

All behaviors extend `AIBehavior(controller)` with `enter()` and `update(target, strategy)`.

### Combat Behaviors (5)

| Behavior | Key | Description |
|----------|-----|-------------|
| **KiteBehavior** | `kite` | Maintain optimal weapon range. Close in if too far, back off if too close. Supports collision avoidance. |
| **AttackRunBehavior** | `attack_run` | Two-phase state machine: APPROACH until within range, then RETREAT for `retreat_duration` seconds. Cycles automatically. |
| **RamBehavior** | `ram` | Navigate straight to target position, no collision avoidance. |
| **FleeBehavior** | `flee` | Move away from target. `fire_while_retreating` controls whether weapons fire. |
| **OrbitBehavior** | `orbit` | Circle target at fixed distance using tangent + radial correction vectors. |

### Utility/Test Behaviors (5)

| Behavior | Key | Description |
|----------|-----|-------------|
| **StationaryFireBehavior** | `stationary_fire` | No movement, weapons fire. For testing and satellites. |
| **DoNothingBehavior** | `do_nothing` | No movement, no firing. |
| **StraightLineBehavior** | `straight_line` | Full thrust in initial facing, no rotation. |
| **RotateOnlyBehavior** | `rotate_only` | Continuous rotation, no thrust. |
| **ErraticBehavior** | `erratic` | Random direction changes at random intervals. Stress testing. |

### Strategy Parameters Read by Behaviors

- `avoid_collisions` (bool) -- KiteBehavior collision avoidance toggle
- `engage_distance` (float | `'max_range'` | `'ram'`) -- range multiplier for KiteBehavior
- `fire_while_retreating` (bool) -- FleeBehavior weapon control
- `retreat_hp_threshold` (float) -- HP % that triggers flee
- `attack_run_behavior.approach_distance` (float) -- weapon range multiplier
- `attack_run_behavior.retreat_distance` (float) -- re-approach distance multiplier
- `attack_run_behavior.retreat_duration` (float) -- seconds in retreat phase

---

## Spatial Behavior System

**Package:** `game/ai/spatial_behaviors/`

Spatial behaviors define how ships position relative to an anchor (ship, group centroid, or zone). They replaced the old `ShipFormation` master/follower system.

Each behavior computes a **target position** for a ship. The AI controller navigates the ship there. Behaviors do NOT control ships directly — they only say "you should be here."

### Rigid Behaviors (Hold Relative Positions)

| Behavior | Type String | Parameters | Description |
|----------|-------------|------------|-------------|
| **BattleLineBehavior** | `battle_line` | `spacing`, `shape` (line/wedge/echelon_left/echelon_right) | Ships hold positions in a line perpendicular to the leader's facing. Shape controls the geometry. |
| **ColumnBehavior** | `column` | `follow_distance` | Ships trail behind a leader in single file. |

Rigid behaviors use **tolerance bands** rather than spring correction — a ship drifting within the tolerance is fine, outside it maneuvers back. This looks more natural than spring oscillation.

### Loose Behaviors (Behavioral Zones)

| Behavior | Type String | Parameters | Description |
|----------|-------------|------------|-------------|
| **ScreenBehavior** | `screen` | `radius`, `reactivity` (passive/active/aggressive) | Ships distribute evenly around an anchor at a configured radius. Reactivity controls threat response. |
| **EscortBehavior** | `escort` | `distance` | Ships stay close to an anchor ship, distributing evenly around it. |
| **PatrolZoneBehavior** | `patrol_zone` | `zone_center`, `zone_radius` | Ships distribute within a circular patrol zone at ~70% of zone radius. |
| **FreeManeuverBehavior** | `free_maneuver` | (none) | No spatial constraints — ship moves per its movement policy alone. |

### Anti-Clumping

`apply_separation(positions, min_separation)` in `base.py` enforces minimum distance between ships in the same group. Ships closer than `min_separation` get pushed apart along their connecting vector. Prevents the "blob of ships" problem.

### Factory

`create_spatial_behavior(behavior_type, **kwargs)` creates a behavior by type string. Unknown types default to `FreeManeuverBehavior`.

---

## Group Target Coordinator

**File:** `game/ai/group_target_coordinator.py`

Stateless utility for group-level combat decisions. Used by the fleet hierarchy system to coordinate task force / squadron behavior.

### Focus Fire

`select_focus_target(enemies, priority, reference_position)` selects one target for the group:

| Priority | Logic |
|----------|-------|
| `strongest` | Highest mass enemy |
| `most_damaged` | Lowest HP/maxHP ratio |
| `nearest` | Closest to reference position (group centroid) |
| `largest` | Highest mass (alias for strongest) |

Dead enemies are automatically filtered. Returns `None` if no valid enemies.

### Reserve Commitment

`should_commit_reserve(main_body_ships, threshold)` returns `True` when the main body's aggregate HP ratio drops to or below the threshold (default 50%).

`compute_group_hp_ratio(ships)` calculates total current HP / total max HP for a group of ships.

### Flagship Succession

`find_flagship_successor(ships, has_cnc_check)` finds the next flagship when the current one is destroyed. Selects the **heaviest alive ship** that passes the `has_cnc_check` callback (checking for `CommandAndControl` ability). Returns `None` if no eligible ship exists (leaderless state).

---

## StrategyManager

Service (managed by ApplicationContext) that loads and resolves per-ship combat strategies from JSON data files.

### Data Files (in `data/`)

| File | Contents |
|------|----------|
| `targeting_policies.json` | Named targeting policies with scoring rules |
| `movement_policies.json` | Named movement policies (behavior, engage_distance, thresholds) |
| `combat_strategies.json` | Named strategies that reference one targeting + one movement policy |
| `group_policies.json` | Group-level policy presets for fleet hierarchy nodes (see Strategy Layer doc) |

### Resolution

`resolve_strategy(strategy_id)` returns a fully composed dict:

```python
{
    'definition': { ... },       # Raw strategy entry
    'targeting': { 'rules': [...] },  # Resolved targeting policy
    'movement': { 'behavior': 'kite', 'engage_distance': 'max_range', ... }
}
```

Ships reference a strategy by ID string (e.g., `'standard_ranged'`, `'aggressive'`) via `ship.ai_strategy`. The controller resolves this each tick.

### Test Strategies

Predefined strategies for Combat Lab scenarios:

| Strategy ID | Behavior | Purpose |
|-------------|----------|---------|
| `test_stationary_fire` | `stationary_fire` | Stay still, fire at targets |
| `test_do_nothing` | `do_nothing` | No movement, no firing |
| `test_straight_line` | `straight_line` | Full thrust in facing direction |
| `test_rotate_right` | `rotate_only` (dir=1) | Clockwise rotation |
| `test_rotate_left` | `rotate_only` (dir=-1) | Counter-clockwise rotation |
| `test_erratic` | `erratic` | Random direction changes |

No-target behaviors (execute without an enemy target): `straight_line`, `rotate_only`, `erratic`, `do_nothing`, `stationary_fire`.

**Thread safety:** Data loading is protected by a lock (double-checked locking). Once loaded, reads are lock-free.

---

## TargetEvaluator

Static class that scores a candidate target against a list of targeting rules.

### Rule Types

| Category | Rule Types | Scoring Logic |
|----------|-----------|---------------|
| **Distance** | `nearest`, `farthest`, `distance` | Score proportional to distance (negated for nearest) |
| **Mass/Size** | `mass`, `largest`, `smallest`, `strongest`, `weakest` | Score proportional to candidate mass |
| **Speed** | `fastest`, `slowest` | Score proportional to velocity magnitude |
| **Damage** | `most_damaged`, `least_damaged` | Score based on HP percentage |
| **Capability** | `has_weapons`, `least_armor` | Component-based checks |
| **PDC** | `pdc_arc`, `missiles_in_pdc_arc` | Checks if missile target is within PDC firing arc and range |

Each rule has `weight` (or `factor`), and optionally `required: true`. If a required rule fails, the candidate scores `-inf` and is excluded.

### Performance Optimizations

- **Distance cache:** Distances pre-calculated once per candidate, shared across rules.
- **Capabilities cache:** Component lookups (weapons, PDC) done once per candidate, not per rule.

---

## ShipControllableAdapter

`IControllable` is the abstract interface that decouples AI from `Ship` internals. `ShipControllableAdapter` wraps a `Ship` and delegates all calls.

The interface covers:
- **Position/movement reads:** `get_position()`, `get_rotation()`, `get_max_speed()`, etc.
- **Movement controls:** `set_throttle()`, `rotate()`, `thrust_forward()`, `adjust_position()`
- **Combat:** `get_weapon_range()`, `set_trigger_pulled()`, target management
- **Identity:** `get_team_id()`, `is_alive()`, `get_ai_strategy()`, `get_vehicle_type()`

---

## AIControllerFactory

Two-phase initialization pattern:

```
Phase 1: factory = AIControllerFactory()        # No dependencies
Phase 2: factory.set_grid(engine.grid)          # Grid available after BattleEngine init
         controller = factory.create_for_ship(ship, enemy_team_id=1)
```

The factory:
1. Wraps each `Ship` in a `ShipControllableAdapter`.
2. Creates an `AIController(adapter, grid, enemy_team_id)`.
3. Returns it typed as `IAIController` (simulation-layer protocol).

Raises `StateException` if `set_grid()` was not called before creating controllers.

---

## Protocols (`game/ai/protocols.py`)

Runtime-checkable protocols for type-safe duck typing:

| Protocol | Required Attributes | Used By |
|----------|-------------------|---------|
| `IGridEntity` | `position`, `is_alive`, `team_id`, `radius` | Spatial queries, collision |
| `IProjectile` | extends IGridEntity + `type` | PDC targeting (missile detection) |
| `IComponentHealth` | `current_hp`, `max_hp` | Damage evaluation |

TypeGuard functions (`is_grid_entity()`, `is_projectile()`, etc.) use duck-typing (`hasattr`) rather than `isinstance()` for compatibility with test mocks.

---

## Key Files

| Component | File |
|-----------|------|
| AIController | `game/ai/controller.py` |
| Movement behaviors | `game/ai/behaviors.py` |
| Spatial behaviors | `game/ai/spatial_behaviors/` (package) |
| Group coordinator | `game/ai/group_target_coordinator.py` |
| StrategyManager | `game/ai/strategy_manager.py` |
| TargetEvaluator | `game/ai/target_evaluator.py` |
| Combat utilities | `game/ai/combat_utils.py` |
| AIControllerFactory | `game/ai/ai_factory.py` |
| IControllable + Adapter | `game/ai/interfaces/controllable.py` |
| AI protocols | `game/ai/protocols.py` |
| Per-ship strategy data | `data/combat_strategies.json`, `data/targeting_policies.json`, `data/movement_policies.json` |
| Group policy data | `data/group_policies.json` |
