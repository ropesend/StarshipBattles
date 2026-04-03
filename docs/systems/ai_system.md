# AI System Architecture

This document describes the combat AI system that controls autonomous ship behavior during battles.

---

## Architecture Overview

```
game/ai/
  __init__.py                  # Public API exports
  controller.py                # AIController - per-ship decision loop
  behaviors.py                 # Movement behavior classes (11 total)
  strategy_manager.py          # StrategyManager singleton - loads/resolves strategies
  target_evaluator.py          # TargetEvaluator - scores potential targets
  combat_utils.py              # Shared helpers (distance, HP, PDC arc checks)
  ai_factory.py                # AIControllerFactory - two-phase creation
  protocols.py                 # IGridEntity, IProjectile, IFormationMaster protocols
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
2. **Throttle reset** -- set engine and turn throttle to 1.0 (or formation throttle if leading).
3. **Formation master handling** -- limit turn rate and speed to keep members together.
4. **Formation integrity check** -- drop out if propulsion damaged.
5. **Strategy resolution** -- `StrategyManager.resolve_strategy(ship.ai_strategy)` returns targeting rules and movement policy.
6. **Target acquisition** -- reuse current target if alive, otherwise call `find_target()`.
7. **Secondary targets** -- if ship has multiplex tracking (`max_targets > 1`), find additional targets.
8. **Behavior selection** (see flowchart below).
9. **Behavior execution** -- call `behavior.update(target, context)`.

### Behavior Selection Flowchart

```
Is ship in formation with master?
  YES -> 'formation'
  NO  -> Is HP <= retreat_hp_threshold?
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

## Behavior System

All behaviors extend `AIBehavior(controller)` with `enter()` and `update(target, strategy)`.

### Combat Behaviors (6)

| Behavior | Key | Description |
|----------|-----|-------------|
| **KiteBehavior** | `kite` | Maintain optimal weapon range. Close in if too far, back off if too close. Supports collision avoidance. |
| **AttackRunBehavior** | `attack_run` | Two-phase state machine: APPROACH until within range, then RETREAT for `retreat_duration` seconds. Cycles automatically. |
| **RamBehavior** | `ram` | Navigate straight to target position, no collision avoidance. |
| **FleeBehavior** | `flee` | Move away from target. `fire_while_retreating` controls whether weapons fire. |
| **FormationBehavior** | `formation` | Follow formation master maintaining offset. In-formation: velocity sync + spring-based position correction. Out-of-formation: navigate to predicted master position. |
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

## StrategyManager

Singleton (`SingletonMeta`) that loads and resolves combat strategies from JSON data files.

### Data Files (in `data/`)

| File | Contents |
|------|----------|
| `targeting_policies.json` | Named targeting policies with scoring rules |
| `movement_policies.json` | Named movement policies (behavior, engage_distance, thresholds) |
| `combat_strategies.json` | Named strategies that reference one targeting + one movement policy |

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

Predefined strategies for Combat Lab scenarios that replace manual per-tick commands:

| Strategy ID | Behavior | Purpose |
|-------------|----------|---------|
| `test_stationary_fire` | `stationary_fire` | Stay still, fire at targets. Replaces `comp_trigger_pulled = True` |
| `test_do_nothing` | `do_nothing` | No movement, no firing. For static targets |
| `test_straight_line` | `straight_line` | Full thrust in facing direction. Replaces `thrust_forward()` |
| `test_rotate_right` | `rotate_only` (dir=1) | Clockwise rotation. Replaces `rotate(1)` |
| `test_rotate_left` | `rotate_only` (dir=-1) | Counter-clockwise rotation. Replaces `rotate(-1)` |
| `test_erratic` | `erratic` | Random direction changes. Stress testing |

The AI controller runs these behaviors even without an enemy target (for propulsion tests with no opponents). No-target behaviors: `straight_line`, `rotate_only`, `erratic`, `do_nothing`, `stationary_fire`.

**Thread safety:** Data loading is protected by a lock (double-checked locking). Once loaded, reads are lock-free. `clear()` and `reset()` are test-only and not thread-safe.

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
- **Formation:** `get_formation_members()`, `get_formation_master()`, `leave_formation()`
- **Identity:** `get_team_id()`, `is_alive()`, `get_ai_strategy()`, `get_vehicle_type()`

Formation methods return raw `Ship` objects (not adapters) because formation logic accesses master attributes directly.

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
| `IFormationMaster` | `position`, `angle`, `is_alive`, `is_derelict`, `is_thrusting`, `max_speed`, `engine_throttle`, `current_speed`, `formation`, `current_target` | FormationBehavior |
| `IComponentHealth` | `current_hp`, `max_hp` | Damage evaluation |

TypeGuard functions (`is_grid_entity()`, `is_projectile()`, etc.) use duck-typing (`hasattr`) rather than `isinstance()` for compatibility with test mocks.

---

## Key Files

| Component | File |
|-----------|------|
| AIController | `game/ai/controller.py` |
| All behaviors | `game/ai/behaviors.py` |
| StrategyManager | `game/ai/strategy_manager.py` |
| TargetEvaluator | `game/ai/target_evaluator.py` |
| Combat utilities | `game/ai/combat_utils.py` |
| AIControllerFactory | `game/ai/ai_factory.py` |
| IControllable + Adapter | `game/ai/interfaces/controllable.py` |
| AI protocols | `game/ai/protocols.py` |
| Strategy data | `data/combat_strategies.json`, `data/targeting_policies.json`, `data/movement_policies.json` |
