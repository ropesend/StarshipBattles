# Combat Simulation System

System documentation for the real-time combat simulation layer.

---

## 0. Unified Entry (PROJ-269 + PROJ-270 — complete)

> **Status:** Implementation complete as of PROJ-270. Every battle (Combat
> Lab, Battle Setup, Strategy combat) compiles a `BattleSpec` via its
> context-specific compiler and either:
> - calls `run_battle(spec) -> BattleOutcome` directly (headless paths), or
> - hands the spec to `BattleController` which drives a per-frame tick
>   loop for visual mode and calls `extract_outcome(engine, spec)` at
>   battle end to emit a `BattleOutcome`.
>
> Every live battle produces a `BattleOutcome`. The legacy `BattleMode`
> enum + `BattleModeHandler` hierarchy + the four `create_*_battle`
> factories are deleted (PROJ-269). The `engine_ref["engine"] = engine`
> closure trick Combat Lab used to capture the engine is also deleted
> (PROJ-270 Phase 2). Validators consume `(BattleOutcome, CombatLabTelemetry)`.
>
> Acceptance locked by `tests/unit/simulation/test_unified_entry_guard.py`:
> no direct `engine.start*()` / `BattleEngine(...)` bypasses; no
> `scenario.setup(engine)` methods; no "Legacy-compatible" markers;
> `BattleController.run_headless` deleted; `get_outcome()` / `set_spec()`
> present on `BattleController`. See §1 for the full flow.

`run_battle(spec: BattleSpec) -> BattleOutcome` at
[`game/simulation/battle_runner.py`](../../game/simulation/battle_runner.py)
is the target single entry point. Every battle — Combat Lab, Battle Setup,
Strategy combat — builds a `BattleSpec` via a context-specific compiler and
hands it here.

**DTOs** (introduced in Phase 1):

| File | Contains |
|------|----------|
| `game/simulation/battle_spec.py` | `BattleSpec`, `TeamSpec`, `TaskForceSpec`, `SquadronSpec`, `ShipSpec`, `ComponentStateSpec`, `EntryVector`, `AIPolicy`, `CombatPolicies`, `PostBattleHook` |
| `game/simulation/battle_outcome.py` | `BattleOutcome`, `TeamOutcome`, `TaskForceOutcome`, `ShipOutcome`, `ShipStatus`, `EndReason`, `HitRecord`, `WeaponSummary`, `ShipStats`, `ModifierApplication` |
| `game/simulation/combat/boundary.py` | `BoundaryRegion` protocol, `RectBoundary`, `CircleBoundary`, `UnboundedRegion`, `ExitPolicy` |
| `game/simulation/combat/modifier_stack.py` | `ModifierStack`, `ModifierEntry` — source-tagged modifier bundle |
| `game/simulation/combat/formation.py` | `FormationShape`, `FormationSpec` (resolver lands in Phase 4) |
| `game/simulation/combat/telemetry.py` | `TelemetryLevel` (MINIMAL / NORMAL / DETAILED; subscribers land in Phase 5) |

**Spec compilers** (one per context):

| File | Function |
|------|----------|
| `combat_lab/spec_compiler.py` | `build_test_battle_spec(scenario, registries)` |
| `game/ui/screens/battle_setup/spec_compiler.py` | `build_manual_battle_spec(ui_state, registries, ...)` |
| `game/strategy/combat/spec_compiler.py` | `build_strategy_battle_spec(fleets, sector, system, empires, settings, registries)` |

**Engine entry:**

```python
from game.simulation.battle_runner import run_battle

spec = build_test_battle_spec(scenario, registries)
outcome = run_battle(
    spec,
    ai_factory=AIControllerFactory(),
    ship_builder=my_ship_builder,     # Phase-1 transitional; Phase 2 folds in
    per_tick_callback=on_tick,        # optional — rendering / observation
)
```

All four Phase-1 hooks are wired into the engine:
- `boundary` — fully enforced as of Phase 3 (per-tick + `ExitPolicy`
  dispatch via `BoundaryEnforcementPhase`)
- `formation` — fully resolved at compile time as of Phase 4
- `telemetry_level` — fully wired as of Phase 5 (see below)
- `modifier_stack` — wired as of Phase 5.5. `run_battle` threads
  `spec.modifier_stack` onto `BattleEngine.modifier_stack`; at
  `start_teams`, `FleetAuraManager.initialize(ships, modifier_stack=...)`
  translates each `ModifierEntry` into an `ExternalModifier` using
  `entry.effect.stat_key` as the ability name (`ToHitAttackModifier`,
  `ToHitDefenseModifier`, ...). Entries whose `stat_key == "placeholder"`
  are silently skipped — compilers emit those as record-of-presence
  markers for toggles whose real effect mapping hasn't been authored
  yet. When a compiler wires a real `stat_key`, the aura manager
  applies it without further engine changes. `HitLogRecorder` also
  consumes the stack at DETAILED telemetry to populate
  `HitRecord.modifiers_applied` with the active modifiers (globals +
  attacker-team entries, placeholders filtered).

### Telemetry (Phase 5)

`BattleSpec.telemetry_level` is an `IntEnum` at
[game/simulation/combat/telemetry.py](../../game/simulation/combat/telemetry.py)
with three values: `MINIMAL` (1), `NORMAL` (2), `DETAILED` (3).
`run_battle` attaches opt-in aggregators based on the level:

| Level | Attached aggregators | `BattleOutcome` fields populated |
|-------|----------------------|---------------------------------|
| `MINIMAL` | (none) | only `end_reason` / `duration_ticks` / `seed` + per-ship `status` / `components` / pose |
| `NORMAL` | `WeaponSummaryAggregator`, `ShipStatsAggregator` | above + `ShipOutcome.weapons` (per-weapon shots/hits) + `ShipOutcome.stats` (damage / speed / ticks) |
| `DETAILED` | above + `HitLogRecorder` | above + `ShipOutcome.hits_taken` (one `HitRecord` per damage event) |

**How it works:** `_attach_telemetry(engine, spec)` raises
`engine.combat_events.detail_level` to match the telemetry level so
the `CombatEventBus` actually emits the events the aggregators subscribe
to. MINIMAL runs at whatever the bus default is (no new subscribers).
NORMAL / DETAILED raise the bus level so all damage events reach
the aggregators.

**Per-tick sampling:** `ShipStatsAggregator.sample_tick(engine)` is
called each tick from the tick loop to update peak_speed / ticks_alive
/ ticks_derelict. Not event-driven because the engine doesn't emit
"tick complete" events today.

**Defaults per context (set by each compiler):**
- Strategy: `NORMAL`
- Battle Setup: `NORMAL`
- Combat Lab: `DETAILED` (individual scenarios may override via
  `TestMetadata.telemetry_level = "MINIMAL" | "NORMAL" | "DETAILED"`)

**Overhead (as of 2026-04-12 reference measurement):** On a 500-tick
1v1 smoke battle (ships at 1000px, minimal event traffic):
MINIMAL ≈ NORMAL ≈ DETAILED ≈ 28-30ms. See
`tests/performance/test_telemetry_overhead.py` for the regression gate
and `Projects/active_projects/PROJ-269/decisions.md` for updated
baselines.

**`HitRecord.modifiers_applied`** is an empty tuple in the MVP — real
modifier-trace provenance requires wiring the ModifierStack through
the damage pipeline, deferred to a follow-up.

### Boundary Region (Phase 3)

`BattleEngine.boundary: BoundaryRegion` is enforced every tick by
`BoundaryEnforcementPhase` at priority 250 (after ship movement,
before attacks). For each alive ship, the engine calls
`boundary.contains(ship.position)`; if False, it dispatches to
`_apply_exit_policy(ship, boundary.exit_policy)` with one of:

| ExitPolicy | Effect |
|------------|--------|
| `DESTROY` | Ship is killed via `combat_engine.take_damage(remaining_hp)`; `ShipStatus.DESTROYED` in outcome |
| `RETREAT` | Ship removed from `engine.ships` and appended to `engine.retreated_ships`; `ShipStatus.RETREATED` in outcome |
| `BOUNCE` | Ship position clamped to `boundary.closest_inside_point`; velocity reflected (Rect: flip X/Y, Circle: radial reflect) |
| `NONE` | No-op — ship may exit freely (unbounded Combat Lab scenarios) |

Boundary shapes: `RectBoundary(width, height)`, `CircleBoundary(radius)`,
`UnboundedRegion()` — all centered on `(0, 0)`.
`BattleSpec.boundary=None` is equivalent to `UnboundedRegion()`.

Retreat is a special case of boundary exit with the `RETREAT` policy
— no separate retreat mechanic.

### Formation System (Phase 4)

Ship positions at battle start are computed by `FormationResolver`
([game/simulation/combat/formation.py](../../game/simulation/combat/formation.py))
from three inputs:

1. `FormationSpec(shape, spacing, custom_positions=())` carried on
   `TaskForceSpec.formation`
2. The team's `EntryVector(origin, facing)` — where the formation
   anchors in world space
3. The fleet's ship list (order = position assignment)

Supported `FormationShape` values (8 total):

| Shape | Local-frame pattern (facing = +x) |
|-------|-----------------------------------|
| `LINE_ABREAST` | Perpendicular to facing; symmetric around y=0 |
| `LINE_ASTERN` | Single file along +x: (0,0), (s,0), (2s,0)... |
| `WEDGE` | Leader at (0,0); each row k behind at (-k·s, ±k·s) |
| `ECHELON_LEFT` | Diagonal up-left: (-i·s, +i·s) |
| `ECHELON_RIGHT` | Diagonal down-left: (-i·s, -i·s) |
| `SCREEN` | Main line x=0 + screen column x=+s |
| `CARRIER_PROTECTED` | ~n/3 carriers at origin; rest on ring of radius=s |
| `CUSTOM` | `custom_positions` tuple used verbatim |

World-space pipeline for each ship: local_pos → rotate by `facing` (°, CCW) → translate by `origin` → optional clamp to `boundary.closest_inside_point`. Every ship's `angle = entry_vector.facing`.

Default formation when `TaskForce.formation is None` comes from
`resolve_default_for_task_force(ships)` — dominant `design_role` bucket:

| Dominant archetype | Default shape |
|---------------------|--------------|
| Carrier (`carrier`) | CARRIER_PROTECTED |
| Strike (`interceptor`/`assault_ship`/`raider`/`missile_platform`) | WEDGE |
| Defender (`line_combatant`/`fleet_escort`/`defensive_platform`/`shield_projector`) | LINE_ABREAST |
| Scout (`scout`/`command_ship`/`sensor_platform`) | LINE_ASTERN |
| Mixed / unknown roles | LINE_ABREAST (fallback) |

Ties → LINE_ABREAST. Compilers consult `_pick_formation_for_fleet`
(first explicit `TaskForce.formation` wins, else default).

### N-Team Support (Phase 3)

The engine supports any number of teams. Internal APIs:

| Method | Returns |
|--------|---------|
| `engine.teams: Dict[int, List[Ship]]` | Ships grouped by team_id (property, always in sync) |
| `engine.get_ships_by_team(team_id)` | All ships with that team_id |
| `engine.get_enemies_of(ship)` | All ships whose `team_id != ship.team_id` (no alliances) |
| `engine.start_teams(teams: Dict[int, List[Ship]], ...)` | N-team version of `start()` |

`engine.start(team0, team1, ...)` remains a backward-compat 2-team
wrapper.

`TeamEliminatedCondition` fires when **≤1 team retains alive ships**
(correct for any N). Equivalent to the old "any team has 0 alive"
semantic for 2-team battles. `TeamIncapacitatedCondition` analogous.

AI targeting: `AIController._find_enemies_in_radius` filters on
`obj.team_id != self.ship.get_team_id()` — every non-self team is
equally hostile. No target preference between teams.

`engine.get_winner()` returns the sole surviving team_id when exactly
one team is alive; -1 otherwise.

### Component HP Persistence (Phase 2)

Per-component HP persists across strategy battles via the
`ShipSpec.components → BattleOutcome.components → ShipInstance.components`
round-trip. A ship that enters battle with one component at 40% HP is
reported at ≤40% HP in the outcome, and the `PostBattleHook` writes
that back to the `ShipInstance` so the NEXT battle's compiled spec
carries the same damage.

Flow:
1. `ShipInstance.components: Dict[str, ComponentState]`
   ([game/strategy/data/component_state.py](../../game/strategy/data/component_state.py))
   keyed by `"{component_id}#{instance_index}"` — disambiguates
   identical components (e.g. three seeker missiles).
2. `build_strategy_battle_spec(...)` translates each `ComponentState`
   into a `ComponentStateSpec` on `ShipSpec.components`.
3. `run_battle(spec, ...)` applies per-component HP after the ship
   builder runs (`_apply_spec_components_to_ship`), then runs the
   battle.
4. `extract_outcome(engine, spec)` reads each Ship's per-component
   final HP into `ShipOutcome.components` via `_extract_component_states`.
5. `post_battle_hook(outcome)` (the strategy compiler attaches
   `apply_outcome_to_fleets` by default) writes per-component HP back
   into `ShipInstance.components` for survivors, removes destroyed /
   retreated ships from their fleets, and prunes empty fleets from
   their empire.

Ships are never "repaired" between battles — component HP only
decreases over a ship's lifetime unless an explicit repair mechanic
adjusts it. Repair is a separate future project.

Legacy `ShipInstance.component_damage: Dict[str, int]` (single-instance
granularity) coexists with `components` during the PROJ-269 transition
so 40+ existing call sites continue to work. Consolidation is a
follow-up.

---

## 1. Battle Orchestration (post-PROJ-269 unified flow)

### `run_battle(spec) -> BattleOutcome` is the only sanctioned entry

The battle simulator is a **pure engine**: callers compile their own
domain inputs into a `BattleSpec` via a per-context compiler and hand it
to `run_battle`. The engine knows nothing about test scenarios, fleet
hierarchies, or UI screens — it just runs the sim and emits a
`BattleOutcome`.

**Architecture layers:**
```
Caller (Battle Setup / Combat Lab / Strategy)
  → context-specific spec compiler
    → BattleSpec (frozen DTO)
      → run_battle(spec, ai_factory, ship_builder, ...)
        → BattleEngine (constructed inline; no controller wrapper)
          → BattleOutcome
            → spec.post_battle_hook(outcome)  # optional side effects
```

**Unified entry**:

```python
from game.simulation.battle_runner import run_battle

spec = build_strategy_battle_spec(fleets, sector=..., empires=..., registries=...)
outcome = run_battle(
    spec,
    ai_factory=AIControllerFactory(),
    ship_builder=lambda ship_spec: ship_instance.to_ship(...),
    per_tick_callback=None,           # optional
    pre_tick_loop_callback=None,      # optional
)
```

`run_battle` instantiates `BattleEngine` directly, threads
`spec.boundary` and `spec.modifier_stack` onto it, calls
`engine.start_teams(...)`, drives the tick loop, attaches telemetry
aggregators per `spec.telemetry_level`, extracts a `BattleOutcome` via
`extract_outcome(engine, spec)`, and finally invokes
`spec.post_battle_hook(outcome)` if one is attached.

### Spec compilers

| Context | Compiler | File |
|---------|----------|------|
| Combat Lab | `build_test_battle_spec(scenario, registries)` | [`combat_lab/spec_compiler.py`](../../combat_lab/spec_compiler.py) |
| Battle Setup | `build_manual_battle_spec(ui_state, registries, ...)` | [`game/ui/screens/battle_setup/spec_compiler.py`](../../game/ui/screens/battle_setup/spec_compiler.py) |
| Strategy combat | `build_strategy_battle_spec(fleets, ...)` | [`game/strategy/combat/spec_compiler.py`](../../game/strategy/combat/spec_compiler.py) |

Each compiler:
1. Walks its own domain inputs (TestScenario / BattleSetupState / Fleets).
2. Emits a `BattleSpec` with the right boundary, formations, modifier stack, telemetry level, and end condition.
3. Optionally attaches a `PostBattleHook` (strategy attaches `apply_outcome_to_fleets`; Combat Lab and Battle Setup pass None).

### Visual mode (post-PROJ-269 transitional)

`run_battle` is a blocking-headless call — it runs the tick loop to
completion. Visual battles (Battle Setup → Battle Screen, Combat Lab UI
visual run) still use a `BattleController` wrapper for per-frame
ticking. That wrapper is a thin lifecycle holder (configure → add_ships
→ start → tick-from-game-loop) and no longer dispatches on mode. The
remaining `BattleController` will be deleted when Task 6.9's UI
visual-mode migration lands a non-blocking `run_battle` driver.

**`BattleConfig`** (post-PROJ-269 reshape) is a thin operational-options
bag for the visual-mode controller — `seed`, `end_condition`,
`absolute_max_ticks`, `headless`, `start_paused`, `enable_logging`,
`allow_retreat`, `allow_reinforcements`, `return_destination`,
`show_results`, `test_scenario`, `map_bounds`. The `BattleMode` enum
+ `BattleModeHandler` strategy hierarchy + `BattleConfig.mode` field +
`team_modifiers` / `global_modifiers` / `environmental_effects` /
`source_fleets` / `per_tick_callback` fields are all GONE — variance
moved onto `BattleSpec`.

**`ReturnDestination`** (in `battle_config.py`) is retained for the
post-battle UI flow:
- `BATTLE_SETUP` — return to battle setup screen
- `TEST_LAB` — return to Combat Lab
- `STRATEGY` — return to strategy map

### BattleService (Low-Level Abstraction)

**File:** `game/simulation/services/battle_service.py`

Provides a clean interface between UI screens and BattleEngine.
All operations return `BattleServiceResult` (success/errors/warnings/engine ref).

Lifecycle:
1. `create_battle(seed, enable_logging, ai_factory)` -- creates BattleEngine
2. `add_ship(ship, team_id)` -- registers ships to teams (0 or 1)
3. `start_battle(end_condition, absolute_max_ticks)` -- initializes engine, creates AI controllers
4. `update()` or `run_ticks(count)` -- advances simulation
5. `is_battle_over()` / `get_winner()` -- query outcome
6. `reset()` -- cleanup

### BattleEngine (Tick Loop)

**File:** `game/simulation/systems/battle_engine.py`

BattleEngine owns the simulation state: ships, AI controllers, projectiles, spatial grid.

**`start()` initialization:**
- Assigns team IDs (0 and 1)
- Creates AI controllers via injected `IAIControllerFactory` (or accepts pre-created list)
- Initializes `SpatialGrid`, `ProjectileManager`, `CollisionSystem`
- Per-ship initialization via `_initialize_ship()`: event bus wiring, component update, stat recalculation, derelict check
- Initializes `FleetAuraManager` with all ships
- Seeds RNG for deterministic replays

**`add_ship_mid_battle()` (reinforcements and fighter launch):**
- Sets team ID, appends to ships list
- Creates AI controller (via factory or pre-created)
- Runs the same per-ship initialization as `start()` via `_initialize_ship()`
- Registers with `FleetAuraManager` via `register_ship()` (scans new ship's abilities, recalculates bonuses)
- Fighter launch (`LAUNCH` attack type in `update()`) delegates to `add_ship_mid_battle()`

**`update()` tick sequence (per tick):**

The `update()` method is a concise coordinator that delegates to focused helpers:

| Phase | Helper Method | Description |
|-------|---------------|-------------|
| 1 | `_rebuild_grid()` | Clear and rebuild spatial grid with alive ships + active projectiles |
| 2 | `_update_ai_and_ships()` | Update AI controllers, ship physics/weapons/abilities, fleet auras |
| 3 | `_collect_new_attacks()` | Gather and clear attacks emitted by ships this tick |
| 4 | `_process_attacks()` | Dispatch by type: PROJECTILE/MISSILE via `_process_projectile_attack()`; BEAM via CollisionSystem; LAUNCH via `_process_launch_attack()` (spawns fighter Ship) |
| 5 | (inline) | Process ramming collisions (kamikaze ships) |
| 6 | (inline) | Update projectiles (movement, hit detection, expiration) |

**Fleet Aura System** (`game/simulation/combat/fleet_aura_manager.py`):

`FleetAuraManager` on `BattleEngine` manages abilities with non-SELF scope (fleet, system, empire).
Initialized at battle start, recalculated every tick. Bonuses removed immediately when provider
ship is destroyed. Stacking follows two-phase aggregation (same group = MAX, different groups = SUM).

Per-team and global battle conditions can be injected via `BattleConfig.team_modifiers` and
`BattleConfig.global_modifiers` for external bonuses (sensor arrays, nebula effects, etc.).

**End conditions** (composable via `IEndCondition` protocol):

Leaf conditions:
- `TeamEliminatedCondition` -- ends when all ships on one team are dead (default)
- `TickLimitCondition` -- ends after max_ticks reached
- `TeamIncapacitatedCondition` -- ends when a team cannot fight or move
- `NeverCondition` -- never ends automatically
- `EscapeCondition` -- ends when ships escape beyond radius from arena center
- `ShipDestroyedCondition` -- ends when a named ship is destroyed

Composite conditions:
- `AnyCondition([...])` -- OR: first child met triggers end
- `AllCondition([...])` -- AND: all children must be met

All conditions are serializable via `to_dict()` / `end_condition_from_dict()`.
Safety ceiling (`absolute_max_ticks`) is enforced by `BattleEngine` independently.

**Winner determination:** `get_winner()` returns 0, 1, or -1 (draw).

**Combat Event System** (`game/simulation/combat/combat_events.py`):

`CombatEventBus` on `BattleEngine` emits events during damage resolution:
- `SHIELD_HIT` -- shield absorbed damage
- `ARMOR_ABSORBED` -- emissive armor or SRA absorbed damage
- `COMPONENT_HIT` -- hull component took damage
- `COMPONENT_DESTROYED` -- component HP reached 0
- `SHIP_DESTROYED` -- ship was killed
- `SHIP_DERELICT` -- ship became derelict

Each event carries a `DamageContext` with attacker identity (ship, weapon, damage type).
Event detail levels (`MINIMAL`, `NORMAL`, `DETAILED`) control granularity for performance.

**Visual Hit Effects** (`game/ui/effects/hit_effects.py`):

`BattleScreen` subscribes to combat events and creates timer-based visual effects:
- Shield hit: cyan concentric circles (0.2s)
- Armor/component hit: orange expanding circle + radiating lines (0.15s)
- Component destroyed: larger orange burst (0.25s)
- Ship destroyed: white flash + expanding ring (0.4s)

**Battle Results Screen** (`game/ui/screens/battle_results_screen.py`):

Full-screen IScene showing post-battle statistics. Data extracted via
`extract_battle_results()` in `battle_results_data.py`. Two-column layout
with per-ship HP bars, weapon accuracy tables, and team summaries.

---

## 2. Battle Modes — REMOVED in PROJ-269 Phase 6

The `BattleModeHandler` Strategy pattern (4 concrete handlers
dispatched via `get_handler_for_mode(BattleMode)`) was deleted in
PROJ-269 Phase 6. Variance now lives on `BattleSpec` fields:

| Old mode trait | New `BattleSpec` field / mechanism |
|----------------|-----------------------------------|
| `can_retreat` | `BoundaryRegion(exit_policy=RETREAT)` |
| `can_reinforce` | `BattleConfig.allow_reinforcements` (visual mode only) |
| `should_clone_ships` | Caller supplies pre-cloned ships in their `ship_builder` |
| `is_headless_default` | `run_battle(spec, headless=...)` kwarg |
| `apply_results` | `BattleSpec.post_battle_hook` (e.g. `apply_outcome_to_fleets`) |

See [`Projects/active_projects/PROJ-269/decisions.md`](../../Projects/active_projects/PROJ-269/decisions.md)
for the full rationale.

---

## 3. Ship Entity Architecture

**Files:**
- `game/simulation/entities/ship.py` -- `Ship(PhysicsBody, ShipPhysicsMixin)`
- `game/simulation/entities/ship_combat_engine.py` -- `ShipCombatEngine`
- `game/simulation/entities/ship_stats.py` -- `ShipStatsCalculator`
- `game/simulation/entities/ship_stat_querier.py` -- `ShipStatQuerier`
- `game/simulation/entities/ship_physics.py` -- `ShipPhysicsMixin`
- `game/simulation/entities/ship_validator_helper.py` -- `ShipValidatorHelper`

### Ship Class

Ship extends `PhysicsBody` (position, velocity, angle) and `ShipPhysicsMixin` (arcade physics).

**Key state:**
- `layers: Dict[LayerType, LayerData]` -- HULL, CORE, INNER, OUTER, ARMOR
- `resources: ResourceRegistry` -- fuel, ammo, energy pools
- `is_alive`, `is_derelict` -- survival state (derelict = no operational weapons AND no engines)
- `current_target`, `secondary_targets`, `max_targets` -- targeting
- Defense stats: `emissive_armor`, `shield_regenerating_armor`, `current_shields`, `max_shields`
- Offense: `baseline_to_hit_offense`, `total_defense_score`
- Metadata: `movement_policy` + `targeting_policy` (per-ship AI behavior), `design_role` (classification label from `data/design_roles.json`)

**Initialization:** Requires `registries: GameRegistries` (strict DI, PROJ-50).
Auto-equips default hull component from vehicle class definition.

**`update()` per-tick sequence:**
1. Update resources (regeneration)
2. Update components (consumption, cooldowns)
3. Physics movement (arcade: acceleration toward target speed)
4. Combat cooldowns (shields, repair) via `combat_engine`
5. Weapon firing (if trigger pulled) via `combat_engine`

### Delegation Chain

```
Ship
  ├── combat_engine: ShipCombatEngine (lazy)
  │     ├── _targeting_system: TargetingSystem (shared/stateless)
  │     ├── _damage_calculator: DamageCalculator (shared/stateless)
  │     └── _weapon_firing_system: WeaponFiringSystem (shared/stateless)
  ├── stats_calculator: ShipStatsCalculator (lazy)
  ├── stat_querier: ShipStatQuerier (lazy)
  ├── validator_helper: ShipValidatorHelper (lazy)
  └── resources: ResourceRegistry
```

All subsystems are lazy-initialized. `ShipCombatEngine` subsystems (TargetingSystem,
DamageCalculator, WeaponFiringSystem) are class-level shared instances since they are stateless.

### Component Caching (PROJ-49)

- `_components_cache` -- dirty-flag cache of all components across layers
- `_weapons_cache` -- per-tick cache for AI targeting hot path
- Invalidated on add/remove/recalculate

---

## 4. Damage Pipeline

**File:** `game/simulation/combat/damage_calculator.py` -- `DamageCalculator`

Damage flows through 5 stages, each extracted as a focused method:

```
Incoming Damage
    │
    ▼
[1] _absorb_shields() ──────── Absorbs from shield pool (ship.current_shields)
    │                          Early return if fully absorbed
    ▼
[2] _reduce_emissive_armor() ─ Flat reduction on overflow (ship.emissive_armor)
    │                          Early return if fully absorbed
    ▼
[3] _absorb_regenerating_armor() ─ Absorbs overflow, recharges shields
    │                          by absorbed amount (capped at max_shields)
    │                          Early return if fully absorbed
    ▼
[4] _distribute_hull_damage() ─ Distributes to components sorted by radius_pct
    │                          (outermost first: ARMOR → OUTER → INNER → CORE → HULL)
    ▼
[5] _finalize_damage() ─────── Recalculate stats, check derelict status, emit events
```

The `apply_damage()` coordinator calls these stages in sequence with early returns
preserving the original behavior: if shields or armor fully absorb the hit,
hull layers are never touched and stats are not recalculated.

### Hull Layer Damage Distribution

Within each layer, components are selected by **weighted random** based on
current HP. Damage absorbed = min(component.current_hp, remaining_damage).
Components with more HP are more likely to be hit.

**Note:** `apply_damage()` returns immediately for zero or negative damage
values to prevent invalid state changes (e.g., negative damage healing shields).

After damage reaches hull layers, `_finalize_damage()` runs:
- `ship.recalculate_stats()` -- updates derived stats (skips non-operational components)
- `ship.update_derelict_status()` -- functional check: ship is derelict when it has no operational weapons AND no operational engines
- Emits `SHIP_DERELICT` event if derelict status changed

### Pipeline Validation

The damage pipeline is validated by integration tests in
`combat_lab/scenarios/damage_pipeline_scenarios.py`:
- PIPELINE-001 through PIPELINE-005: Pairwise and full pipeline combinations
- PIPELINE-007: SRA recharge cap overflow (excess recharge above max_shields is wasted)

Individual defense stages are also tested in isolation by their respective
ability test categories (SHIELD-PROJ-*, EMISSIVE-*, SRA-*).

### Component Operational Status and Stats

During `recalculate_stats()`, only **active AND operational** components contribute
stats. A component becomes non-operational when:
- Its constant-trigger `ResourceConsumption` cannot be satisfied (e.g., shield without energy)
- It has `RequiresCommandAndControl` but the ship has no active `CommandAndControl` provider (e.g., bridge destroyed)

Resource storage components always contribute their capacity regardless of
operational status.

### RequiresCommandAndControl (Per-Component)

Individual components declare `RequiresCommandAndControl: true` to indicate they
need a bridge or command center to function. Each tick, `RequiresCommandAndControl.update()`
checks if the ship has an active `CommandAndControl` provider. If not, the component
becomes non-operational — its stats don't contribute (no thrust, no shields, no weapon firing).

This is enforced per-component, not ship-wide. A ship that loses its bridge will have
all C&C-dependent components (weapons, engines, shields, sensors, ECM, generators)
go non-operational while passive components (armor, storage, crew quarters) continue.

**Production components with RequiresCommandAndControl (24 total):**
All weapons, shields, engines, thrusters, sensors, ECM, generators, hangars, and repair bays.
Armor, storage tanks, crew quarters, life support, and strategy-only components are exempt.

### Derelict Status

`is_derelict` is a **functional flag** (not tied to a specific component):
- `True` when the ship has **no operational weapons AND no operational engines**
- Used by UI for status display, by battle engine for victory counting, by AI for behavior decisions
- Can result from C&C loss, resource depletion, crew shortage, or component destruction

`battle_engine.start()` runs an initial component update cycle so that RequiresCommandAndControl
checks take effect before the first tick. This ensures ships without bridges start
the battle with correct operational status.

When `max_shields` decreases (e.g., shield component loses power), `current_shields`
is capped to the new max — preventing orphaned shield HP from lingering after
deactivation.

### Generic Resource Support

Resource aggregation is fully data-driven. `ShipStatsCalculator._aggregate_resource_abilities()`
discovers resource types dynamically from component `ResourceStorage`, `ResourceGeneration`,
and `ResourceConsumption` abilities. Any resource defined in `data/resources.json` works —
including planetary resources like metals, organics, vapors, radioactives, and exotics.
No hardcoded fuel/energy/ammo assumptions in the combat simulation layer.

### Strategy-Relevant Attributes on Ship

`ShipStatsCalculator` also populates these attributes used by the strategy layer
(via `calculate_design_stats()` in `game/simulation/entities/ship_design_stats.py`):

| Attribute | Type | Source | Description |
|-----------|------|--------|-------------|
| `cargo_storage` | `Dict[str, float]` | `CargoStorage` abilities | Cargo capacity by type (passengers, generic) |
| `pod_storage_mass` | `float` | `PodStorage` abilities (raw dict) | Drop pod mass capacity |
| `warp_resource_costs` | `Dict[str, float]` | `ResourceConsumption` with `trigger='warp_jump'` | Full warp cost breakdown per resource |

These are aggregated in `_aggregate_cargo_and_pod_abilities()` and
`_aggregate_resource_abilities()` (warp costs), and applied in `_apply_aggregated_stats()`.
The strategy layer reads them through `calculate_design_stats()` — do NOT compute
these independently.

---

## 5. Targeting and Firing

### TargetingSystem

**File:** `game/simulation/combat/targeting_system.py`

- `select_target(ship, candidates)` -- filters dead/friendly, returns closest enemy
- `find_valid_target(ship, primary, secondaries, comp, weapon_ab)` -- validates
  per-weapon constraints (range, arc, PDC vs missile/fighter, seeker range).
  PDC weapons can only target missiles and fighters (detected via `vehicle_type == 'Fighter'`)
- `calculate_firing_solution(ship, comp, target)` -- beam: direct aim; projectile/seeker:
  lead calculation via `solve_lead()` (quadratic intercept formula)
- `solve_lead(pos, vel, t_pos, t_vel, p_speed)` -- returns intercept time t > 0

### WeaponFiringSystem

**File:** `game/simulation/combat/weapon_firing_system.py`

`fire_weapons(ship, context)` iterates all components:

1. **Hangar launch:** Components with `VehicleLaunch` ability auto-launch when target exists
2. **Weapon fire:** Components with `WeaponAbility` that pass:
   - `can_afford_activation()` -- resource check
   - `weapon_ab.can_fire()` -- cooldown check
   - `find_valid_target()` -- valid target in arc/range

Attack creation by type:
- **Beam** (`BeamWeaponAbility`): Instant hit dict with damage, range, direction
- **Seeker** (`SeekerWeaponAbility`): Guided `Projectile` with turn_rate, endurance, HP
- **Standard projectile** (`ProjectileWeaponAbility`): Ballistic `Projectile` with velocity

### ShipCombatEngine Cooldowns

Per-tick maintenance:
- **Shield regen:** `shield_regen_rate / 100` per tick, costs `shield_regen_cost / 100` energy
- **Repair:** `repair_rate / 100` per tick, repairs most-damaged component (by hp_ratio)

---

## 6. Ability System

**File:** `game/simulation/components/abilities/base.py` -- `Ability` base class
**Aggregation:** `game/simulation/entities/ability_aggregator.py`

### Ability Base Class

All abilities extend `Ability` with:
- `layer: AbilityLayer` -- COMBAT, STRATEGIC, or BOTH
- `scope: AbilityScope` -- SELF, SECTOR, ALLIED_SECTOR, SYSTEM, ALLIED_SYSTEM, PLANET
- `stack_group: Optional[str]` -- grouping key for aggregation
- `tags: Set[str]` -- categorization (e.g., 'pdc', 'main_weapon')

Key methods:
- `get_primary_value() -> float` -- polymorphic value for aggregation
- `get_effective_stat(stat_key)` -- checks ability-specific stats then component stats
- `recalculate()` -- called when modifiers change
- `update() -> bool` -- per-tick processing

`SimpleMultiplierAbility` -- common base for abilities with one numeric value
modified by one stat multiplier (7+ subclasses use this).

### Two-Phase Aggregation

**File:** `game/simulation/entities/ability_aggregator.py`

`calculate_ability_totals(components, layer?, scope_filter?)`:

**Phase 1 -- Intra-group (MAX / Redundancy):**
Within each `stack_group`, take the MAX value. Components without a stack_group
are each treated as their own group (unique key = component instance).

**Phase 2 -- Inter-group (SUM):**
Across different groups:
- **Numeric abilities:** SUM all group contributions (all abilities use SUM)
- **Marker abilities** (`CommandAndControl`, `Armor`, etc.): Boolean OR (any True = True)

Example: Two sensors in stack_group "basic_sensor" with values 1.2 and 1.5
contribute MAX(1.2, 1.5) = 1.5. A third sensor in stack_group "advanced_sensor"
with value 1.3 is in a different group. Inter-group SUM gives total = 1.5 + 1.3 = 2.8.

### Ability Categories

Defined across files in `game/simulation/components/abilities/`:

| File | Abilities |
|------|-----------|
| `weapons.py` | WeaponAbility, BeamWeaponAbility, ProjectileWeaponAbility, SeekerWeaponAbility |
| `defense.py` | ShieldProjection, ShieldRegeneration, EmissiveArmor, ToHitAttackModifier, ToHitDefenseModifier |
| `propulsion.py` | CombatPropulsion, ManeuveringThruster, WarpJump, StrategicMovement |
| `resources.py` | ResourceConsumption, ResourceStorage, ResourceGeneration |
| `crew.py` | CrewCapacity, CrewRequired, LifeSupportCapacity |
| `markers.py` | CommandAndControl, RequiresCommandAndControl, RequiresCombatMovement, StructuralIntegrity, VehicleLaunchAbility |
| `cargo.py` | CargoStorage |
| `superweapons.py` | DestroyPlanet, DestroyStar, OpenWarpPoint, CloseWarpPoint, CreateDysonSphere, SelfDestruct, SuperweaponMarker |
| `harvester.py` | ResourceHarvesterAbility, LocalStorageAbility, SpaceShipyardAbility |
| `colonize.py` | ColonizePlanet |
| `planetary.py` | PlanetaryShieldAbility, PlanetaryEnergyGeneratorAbility, PlanetaryEnergyStorageAbility |

> For complete details on every ability (registry keys, required parameters, data formats, stat bindings), see [ability_reference.md](ability_reference.md).

---

## 7. Key Protocols

**Files:** `game/simulation/interfaces/`

### Entity Protocols (`entity_protocols.py`)

| Protocol | Purpose | Key Properties |
|----------|---------|----------------|
| `ICombatShip` | Ships in combat | name, team_id, position, velocity, hp, shields, layers, combat_engine |
| `IProjectile` | Projectiles (missiles, bullets) | owner, team_id, position, damage, type, target, turn_rate |
| `IPhysicsShip` | Ships with movement | is_thrusting, engine_throttle, mass, turn_speed, turn_throttle, acceleration_rate |
| `ISerializableShip` | Strategic persistence | total_strategic_movement, warp_max_tonnage, ship_class, warp_energy_cost, vehicle_type, theme_id |

TypeGuard functions: `is_combat_ship()`, `is_projectile()`, `is_physics_ship()`, etc.
Use duck typing (`hasattr` checks) for MagicMock compatibility.

### Component Protocol (`component_protocols.py`)

`IComponent` -- id, name, is_active, current_hp, ability_instances, modifiers, stats,
ability_stats. Methods: `get_abilities()`, `get_ability()`, `has_ability()`,
`has_pdc_ability()`, `can_afford_activation()`.

### Ability Protocols (`ability_protocols.py`)

| Protocol | Extends | Key Properties |
|----------|---------|----------------|
| `IAbility` | -- | stack_group, tags |
| `IWeaponAbility` | IAbility | damage, range, reload_time, firing_arc |
| `IBeamWeaponAbility` | IWeaponAbility | base_accuracy, accuracy_falloff |
| `ISeekerWeaponAbility` | IWeaponAbility | projectile_speed, endurance, turn_rate, projectile_hp, projectile_damage |
| `IProjectileWeaponAbility` | IWeaponAbility | projectile_speed |
| `IResourceConsumptionAbility` | IAbility | trigger, resource_type, amount |
| `IResourceStorageAbility` | IAbility | resource_type, max_amount |
| `IResourceGenerationAbility` | IAbility | resource_type, rate |
| `IWarpJumpAbility` | IAbility | max_tonnage, energy_cost |

TypeGuard functions: `is_weapon()`, `is_beam_weapon()`, `is_seeker_weapon()`, etc.

All protocols are `@runtime_checkable` and designed for 1:1 mapping to
C# interfaces / Rust traits.
