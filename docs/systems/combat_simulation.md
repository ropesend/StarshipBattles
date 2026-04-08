# Combat Simulation System

System documentation for the real-time combat simulation layer.

---

## 1. Battle Orchestration

### Unified Entry/Exit Flow

The battle simulator is a **pure engine**: it receives ships in any state, runs the
simulation, and reports ALL results. It does NOT know about test scenarios, fleet
updates, or pass/fail validation — callers analyze the output.

**Architecture layers:**
```
Caller (Battle Setup / Combat Lab / Strategy Layer)
  → BattleController (orchestrator)
    → BattleService (abstraction)
      → BattleEngine (core tick loop)
```

**Unified entry** — all modes use ONE path:
```python
controller = BattleController(ai_factory=AIControllerFactory())
controller.configure(BattleConfig(
    end_condition=...,                           # Composable IEndCondition
    return_destination=ReturnDestination.TEST_LAB, # Where to go after battle
    show_results=True,                           # Show results screen?
    start_paused=True,                           # Start paused?
))
controller.add_ships(team1_ships, team_id=0)
controller.add_ships(team2_ships, team_id=1)
controller.start()
battle_screen.start_battle(controller)  # ONE entry point
```

**Convenience factory** — `create_started_battle_controller()` (`game/ui/services/battle_factories.py`)
centralizes the configure→add_ships→start sequence. `BattleScreen.start()`, `create_manual_battle()`,
and `create_hypothetical_battle()` all delegate to it.

**Unified exit** — all modes use ONE path:
- Battle ends → `BattleScreen._on_battle_ended()` 
- If `show_results=True`: extracts results → `BattleResultsScreen` → user clicks Return
- If `show_results=False`: returns directly to destination
- `app.py._return_to(destination)` routes to the correct scene

**`ReturnDestination`** enum (`game/simulation/battle_config.py`):
- `BATTLE_SETUP` — return to battle setup screen
- `TEST_LAB` — return to Combat Lab
- `STRATEGY` — return to strategy map

### BattleConfig (`game/simulation/battle_config.py`)

Data-only configuration. The `BattleMode` enum is a label for logging, not a behavior switch.
All behavior differences are expressed through config fields.

Key fields: `mode`, `seed`, `end_condition`, `return_destination`, `show_results`,
`headless`, `start_paused`, `allow_retreat`, `allow_reinforcements`, `per_tick_callback`.

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

## 2. Battle Modes

**File:** `game/simulation/combat/battle_mode_handler.py`

Strategy pattern with `BattleModeHandler` ABC and 4 concrete implementations.
Factory function: `get_handler_for_mode(BattleMode) -> BattleModeHandler`.

### BattleModeHandler ABC

Abstract methods:
- `configure(controller, config)` -- mode-specific setup
- `can_retreat()` -- whether ships can flee
- `can_reinforce()` -- whether mid-battle additions allowed
- `should_clone_ships()` -- whether ships need deep-cloning for isolation
- `is_headless_default()` -- visual vs headless default
- `apply_results(controller, results)` -- post-battle fleet effects

### Concrete Modes

| Mode | Headless | Retreat | Reinforce | Clone | Fleet Effects |
|------|----------|---------|-----------|-------|---------------|
| `ManualBattleModeHandler` | No | No | No | No | None |
| `TestBattleModeHandler` | Yes | No | No | No | None |
| `StrategyBattleModeHandler` | Yes | Yes | Yes | No | Via ConflictResolutionEngine |
| `HypotheticalBattleModeHandler` | Yes | No | No | Yes | None (isolated) |

Strategy mode stores `source_fleets` from config. Fleet updates are handled by
the strategy layer's `ConflictResolutionEngine`, not by apply_results().

---

## 3. Ship Entity Architecture

**Files:**
- `game/simulation/entities/ship.py` -- `Ship(PhysicsBody, ShipPhysicsMixin)`
- `game/simulation/entities/ship_combat_engine.py` -- `ShipCombatEngine`
- `game/simulation/entities/ship_stats.py` -- `ShipStatsCalculator`
- `game/simulation/entities/ship_stat_querier.py` -- `ShipStatQuerier`
- `game/simulation/entities/ship_physics.py` -- `ShipPhysicsMixin`
- `game/simulation/entities/ship_formation.py` -- `ShipFormation`
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
  ├── formation: ShipFormation
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
- Used by UI for status display, by battle engine for victory counting, by AI for formation control
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
| `IFormationHost` | Formation leaders | formation |
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
