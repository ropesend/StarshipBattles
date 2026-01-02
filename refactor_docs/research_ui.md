# UI Research: Inheritance vs Composition

## Overview
This document details the findings from analyzing the UI codebase for specific dependencies on the legacy Inheritance-based component system. The Move to Composition (Abilities) requires refactoring these areas to check for Ability presence (`comp.has_ability(...)` or `comp.get_ability(...)`) rather than `isinstance(comp, Class)`.

## 1. Hardcoded Type Checks (`isinstance` or `.type`)

### `ui/builder/detail_panel.py`
*   **Line 172**: `if hasattr(comp, 'hp') and isinstance(comp, SeekerWeapon):`
    *   *Usage*: Determining if "Missile HP" should be shown.
    *   *Refactor*: Check for `SeekerWeaponAbility`.
*   **Imports**: Uses `Weapon, BeamWeapon, ProjectileWeapon, SeekerWeapon` etc. directly.

### `ui/builder/weapons_panel.py`
*   **Line 244**: `if isinstance(comp, Weapon):`
    *   *Usage*: Filtering components to find weapons for the report.
    *   *Refactor*: Check `comp.has_ability("WeaponAbility")`.
*   **Lines 246-248**: Explicit filtering for sub-types:
    *   `isinstance(comp, ProjectileWeapon)`
    *   `isinstance(comp, BeamWeapon)`
    *   `isinstance(comp, SeekerWeapon)`
    *   *Refactor*: Check specific abilities: `"ProjectileWeaponAbility"`, `"BeamWeaponAbility"`, `"SeekerWeaponAbility"`.
*   **Line 446**: `if isinstance(weapon, BeamWeapon):`
    *   *Usage*: Tooltip logic. Beams use a Sigmoid probability calculation; others use generic logic.
    *   *Refactor*: Check `has_ability("BeamWeaponAbility")`.

### `battle_ui.py`
*   **Lines 135, 159**: `if isinstance(comp, Weapon) and comp.is_active:`
    *   *Usage*: Debug overlay drawing (Weapon Ranges, Firing Arcs).
    *   *Refactor*: Check `has_ability("WeaponAbility")`.
*   **Line 34**: `if getattr(proj, 'type', '') == 'missile':`
    *   *Usage*: Tracking projectiles in Seeker Panel.
    *   *Note*: This checks the *projectile* entity, not the ship component. May not need immediate refactor if Projectile system isn't changing composition yet, but worth noting.

## 2. Attribute Access (Legacy Attributes)

The following attributes are currently accessed directly on `comp` but will likely move to specific Abilities.

### Core Stats
*   **Mass**: `comp.mass` (Likely stays on Component)
*   **HP**: `comp.max_hp`, `comp.hp` (Likely stays on Component)

### Weapon Stats (`WeaponAbility`)
*   `comp.damage` -> `WeaponAbility.damage`
*   `comp.range` -> `WeaponAbility.range`
*   `comp.reload_time` -> `WeaponAbility.reload_time` (or `cooldown`)
*   `comp.firing_arc` -> `WeaponAbility.firing_arc`
*   `comp.base_accuracy` -> `WeaponAbility.base_accuracy`
*   `comp.accuracy_falloff` -> `WeaponAbility.accuracy_falloff` (Crucial for `weapons_panel.py` calculations)
*   `comp.facing_angle` -> Stuck points? Or `WeaponAbility.mounting_angle`? Currently `comp.facing_angle` is used in drawing.

### Missile Specific (`SeekerWeaponAbility`)
*   `comp.endurance` -> `SeekerWeaponAbility.endurance` (or `VehicleLaunchAbility`?)
*   `comp.projectile_speed` -> `SeekerWeaponAbility.projectile_speed`
*   `comp.turn_rate` -> `SeekerWeaponAbility.turn_rate`
*   `comp.to_hit_defense` -> `SeekerWeaponAbility.to_hit_defense`

### Engine Stats (`CombatPropulsion`, `ManeuveringThruster`)
*   `comp.thrust_force` -> `CombatPropulsion.thrust_force`
*   `comp.turn_speed` -> `ManeuveringThruster.turn_rate` (Note name change potentially)

### Shield Stats (`ShieldProjection`, `ShieldRegeneration`)
*   `comp.shield_capacity` -> `ShieldProjection.capacity`
*   `comp.regen_rate` -> `ShieldRegeneration.rate`

### Resource Generation/Consumption
*   `detail_panel.py` (Line 156-163, 191, 208) already attempts to use `get_ability_val` helper which checks `ability_instances`.
    *   *Win*: `detail_panel.py` is partially ready!
    *   *Fix*: It falls back to raw data if `ability_instances` is missing. We must ensure the Builder creates ability instances or the raw data structure is compatible.

## 3. Visualization Logic

*   **Beams vs Projectiles**: `weapons_panel.py` has distinct drawing methods:
    *   `_draw_beam_weapon_bar`: Draws probability curve (sigmoid) + HitChance labels.
    *   `_draw_projectile_weapon_bar`: Draws damage breakpoints (drop-off).
    *   This logic depends entirely on the distinction between Beam and Projectile/Seeker.
*   **Firing Arcs**: `battle_ui.py` draws arcs. Logic assumes `comp.facing_angle` + `comp.firing_arc`.
*   **Icons**: `weapons_panel.py` uses `comp.sprite_index`.

## 4. Recommendations

1.  **Helper Wrappers**:
    *   Create `Component.get_weapon_specs()` returning a dataclass/dict with standardized keys (`damage`, `range`, `arc`, `is_beam`, etc.) regardless of underlying Ability storage.
    *   Or, update UI to fetch specific ability: `ab = comp.get_ability("WeaponAbility")`.

2.  **Mocking in Tests**:
    *   `unit_tests/test_battle_panels.py` (Line 81) manually defines layers/components as dicts/Mocks.
    *   These mocks must update to include `ability_instances` or the tests will fail when the UI switches to reading abilities.

3.  **Refactoring Order**:
    *   Update `attributes` access to `properties` on Component that proxy to Abilities during transition?
    *   OR Update UI to explicitly look for abilities. (Preferred for cleaner break).
