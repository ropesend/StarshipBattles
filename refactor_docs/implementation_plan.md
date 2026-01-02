# Component Ability System Refactor Plan

## Goal
Transition the Starship Battles codebase from an inheritance-based component hierarchy (v1.x) to a pure composition-based system (v2.0).
The `Component` class will become a generic container that derives its behavior (Stats, Physics, Combat, UI) exclusively from a collection of `Ability` objects.

## Status: Planning & Research Complete
Assessment: **High Difficulty / High Risk**
Strategy: **Incremental Refactor**. We will implement the foundation (Abilities) and generic Component logic first, maintaining a "Legacy Shim" to keep the game playable while we migrate subsystems (Stats, Combat, UI) one by one.

## User Review Required
> [!IMPORTANT]
> **Data Migration Strategy**: We will use a **Script-Based Batch Conversion** (`scripts/migrate_legacy_components.py`) rather than runtime conversion. This ensures `components.json` serves as the single source of truth and simplifies validation logic.

> [!WARNING]
> **Breaking Changes**:
> *   `Weapon`, `Engine`, `Bridge` subclasses will be deprecated. Logic relying on `isinstance(c, Engine)` will be replaced by `c.has_ability("CombatPropulsion")`.
> *   Formula-based values (e.g. `damage`) will move inside Ability definitions.

## Test Management & Handoff Strategy
To manage the complexity across multiple agents/sessions, we will maintain a **Test Ledger** in `refactor_handoff.md`.
*   **Tracking**: Every unit test file will be tracked as Active, Ignored, or Deleted.
*   **Re-integration**: "Ignored" tests will have a `Target Phase` for reinstatement.
*   **Handoff**: Each session must update `refactor_handoff.md` with instructions for the next agent, ensuring context is preserved.

## Detailed Implementation Phases

### Phase 1: Foundation (Abilities Module)
Establish the vocabulary of the new system.

#### 1.1 New Module: `abilities.py`
Create `abilities.py` to avoid circular imports in `components.py` or `resources.py`.
*   **Base Class**: `Ability(component, data)`
    *   Methods: `update()`, `get_ui_rows()`, `on_activation()`
*   **Gameplay Abilities**:
    *   `CombatPropulsion` (Thrust)
    *   `ManeuveringThruster` (Turn Speed)
    *   `Structure` (Mass, HP - *Optional/TBD if staying on Component*)
    *   `CommandAndControl` (Bridge logic)
    *   `CrewHabitation` (Crew Cap, Life Support)
    *   `HangarBay` (Vehicle storage/launch)
*   **Weapon Abilities** (Hierarchy):
    *   `WeaponAbility` (Base: cooldowns, reload, range, damage)
    *   `ProjectileWeaponAbility` (Spawns Projectiles)
    *   `BeamWeaponAbility` (Hitscan logic)
    *   `SeekerWeaponAbility` (Spawns Seeker/Missiles)
*   **Resource Abilities** (Migrated from `resources.py`):
    *   `ResourceStorage`, `ResourceConsumption`, `ResourceGeneration`
    *   `VehicleLaunchAbility` (Hangar logic: capacity, launch rate, fighter class)

#### 1.2 Ability Factory
*   Implement `create_ability(name, component, data)` to instantiate classes from `ABILITY_REGISTRY`.
*   Support primitive shorthand (e.g., `"CombatPropulsion": 150` -> `{"value": 150}`).

### Phase 2: Core Refactor (Components)
Make `Component` the single source of truth.

#### 2.1 Generic Component Analysis
Refactor `Component.__init__`:
1.  **Physical Properties**: `id`, `mass`, `hp`/`max_hp`, `cost`, `sprite_index` remain top-level (Physical Object properties).
2.  **Functional Properties**: All other logic (`thrust_force`, `damage`) delegated to Abilities.
3.  **Strict Loading**: Iterate `data['abilities']` and instantiate via Factory.

#### 2.2 Legacy Shim (Backward Compatibility)
*   **Temporary Logic**: In `Component.__init__`, if legacy top-level keys exist (e.g., `thrust_force`), automatically instantiate the corresponding Ability (`CombatPropulsion`) in-memory.
*   **Goal**: Allows existing `components.json` to work immediately while we prepare the migration script.

#### 2.3 Update Loop
*   `Component.update()` iterates `self.ability_instances` and calls `ability.update()`.
*   `Component.is_operational` is derived from checking all `ResourceConsumption` abilities.

### Phase 3: Stats & Physics Integration
Decouple `ShipStatsCalculator` from Component types.

#### 3.1 Ship Stats Refactor (`ship_stats.py`)
*   **Aggregation Loop**: Replace hardcoded `isinstance` checks.
    *   Old: `if isinstance(c, Engine): total_thrust += c.thrust_force`
    *   New: `for ab in c.get_abilities('CombatPropulsion'): total_thrust += ab.value`
*   **Mappings**:
    *   `Engine` -> `CombatPropulsion`
    *   `Thruster` -> `ManeuveringThruster`
    *   `Shield` -> `ShieldProjection`

#### 3.2 Physics Update (`ship_physics.py`)
*   **Constraint**: `ship_physics.py` currently re-iterates components to sum operational thrust, duplicating logic from `ship_stats.py`.
*   **Refactor**:
    *   Remove `isinstance(comp, Engine)` checks.
    *   Implement helper `Ship.get_total_ability_value(ability_name, operational_only=True)`.
    *   Update `update_physics_movement` to use this helper for `CombatPropulsion` and `ManeuveringThruster`.

### Phase 4: Combat System Migration
Move firing logic to Abilities.

#### 4.1 Weapon Logic Refactor
*   **Range Calculation**: Refactor `Ship.max_weapon_range` in `ship.py` to iterate abilities instead of `isinstance(Weapon)`.
*   **Cooldowns**: Move `cooldown_timer` from Component to `WeaponAbility`.
*   **Update**: `Ability.update()` handles cooldown decrement.
*   **Firing**:
    *   `ShipCombatMixin.fire_weapons`: Iterate components with `WeaponAbility`.
    *   Call `ability.check_firing_solution(context)` (Range/Arc).
    *   Call `ability.fire(target)`.

#### 4.2 Seeker Logic
*   `SeekerWeaponAbility` serves as a Factory.
*   `fire()` spawns a `Projectile` entity into the simulation. The Ability does *not* track the missile state after launch.

#### 4.3 Fighter Launch Logic
*   **Refactor `fire_weapons`**: Explicitly check for `VehicleLaunchAbility`.
*   **Logic**: Call `ability.try_launch()`. If successful, generate `AttackType.LAUNCH` event.
*   **Data**: `ability.fighter_class` replaces hardcoded strings.

#### 4.4 Point Defense Targeting
*   **Refactor `_find_pdc_target`**:
    *   Remove legacy `ability.get('PointDefense')` boolean check.
    *   Use `ability.tags` (e.g. `{'pdc'}`) to identify PDC weapons.
    *   Preserve logic: Standard weapons ignore missiles; PDCs target missiles (and fighters) preferentially.

#### 4.5 AI Controller Updates
*   **Refactor `ai.py`**:
    *   Line 369: Replace `isinstance(comp, Weapon)` with `comp.has_ability('WeaponAbility')`.
    *   Update PDC detection to use `ability.tags` instead of `abilities.get('PointDefense', False)`.

### Phase 5: UI & Capabilities
Data-driven UI rendering.

#### 5.1 Capabilities Rendering
*   Implement `Ability.get_ui_rows() -> List[UIRow]`.
*   Refactor `Component.get_ui_rows()` to aggregate rows from all ability instances.

#### 5.2 UI Implementation
*   **Ship Builder**:
    *   Target: `ui/builder/detail_panel.py` class `ComponentDetailPanel`.
    *   Refactor `show_component(self, comp)`: Remove generic `if comp.type_str` and `if hasattr` checks.
    *   Replace with `lines = comp.get_ui_rows()`.
*   **Battle HUD**:
    *   Target: `battle_panels.py` class `ShipStatsPanel`.
    *   Refactor `draw_ship_details`: Use `comp.get_ui_rows()` for expanded views.
    *   Refactor `battle_ui.py`:
        *   `draw_debug_overlay`: Check `comp.has_ability('WeaponAbility')` instead of `isinstance`.
        *   `draw_arcs`: Use `WeaponAbility` attributes (`firing_arc`, `facing_angle`).
    *   Refactor `ui/builder/weapons_panel.py`:
        *   Replace `isinstance(BeamWeapon)` checks with `comp.has_ability('BeamWeaponAbility')`.
        *   Update tooltip and visualization logic to read from Ability attributes.
*   **Caching**: Implement `Ship.cached_summary` to avoid re-calculating stats every frame in the Builder.

### Phase 6: Data Migration
Make `components.json` strict.

#### 6.1 Assignment Script
*   Create `scripts/migrate_legacy_components.py`.
*   Iterate all components. Move top-level keys (`thrust_force`, `turn_speed`, `damage`) into `abilities`.
*   Validate against new schema.
*   Save clean `components.json`.

#### 6.2 Validation Rules
*   Update `ship_validator.py` with `ComponentAbilityConstraintRule`.
*   Enforce: "If you have `CombatPropulsion`, you are an Engine" (or vice-versa for Major Classification).

## Verification Plan

### Automated Testing
*   **Unit Tests**:
    *   `unit_tests/test_abilities.py`: Test individual ability logic.
    *   `unit_tests/test_component_composition.py`: Verify generic component simply containers mechanics correctly.
    *   `unit_tests/test_migration.py`: Test migration script on dummy data.
*   **Regression**:
    *   Ensure `test_ship_stats.py` passes with new aggregator.

### Manual Testing
*   **Ship Builder**: Verify stats appear correctly for engines/weapons.
*   **Combat**: Verify standard weapons fire and infinite-ammo weapons work.
