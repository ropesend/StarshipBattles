# Research: AI & Combat Logic Refactoring

**Date:** 2026-01-02
**Subject:** Transition to Composition-Based Component System

## Executive Summary
The current AI and Combat systems are heavily coupled to concrete `Component` subclasses (e.g., `Weapon`, `Engine`, `Thruster`). The transition to a generic `Component` with a list of `Ability` objects will require significant refactoring in `ship.py`, `ship_stats.py`, `ship_combat.py`, and `ai.py`.

## 1. Capability Detection
The AI currently detects capabilities primarily through `isinstance()` checks and specific attribute lookups.

### Findings
- **Weapons**:
  - `ship_combat.py`: `fire_weapons()` iterates components and strictly checks `isinstance(comp, Weapon)`. It also casts to `SeekerWeapon` and `BeamWeapon` for specific behavior.
  - `ai.py`: `_stat_is_in_pdc_arc()` checks `isinstance(comp, Weapon)` and `comp.abilities.get('PointDefense')`.
  - `ai.py`: `TargetEvaluator` rule `'has_weapons'` checks `hasattr(c, 'damage')` (property check) which is slightly more generic but still brittle.

- **Movement (Engines/Thrusters)**:
  - `ship_stats.py`: `calculate()` explicitly calls `isinstance(comp, Engine)` for thrust and `isinstance(comp, Thruster)` for turn speed.
  - `ai.py`: `_check_formation_integrity()` imports `Engine` and `Thruster` to check if propulsion is damaged.

- **Defenses (Shields/Armor)**:
  - `ship_stats.py`: Iterates searching for `Shield`, `ShieldRegenerator`, and `Armor` classes to calculate `max_shields`, `regen`, and `hp_pool`.

### Implications
- **Refactoring Needed**: Replace `isinstance(comp, X)` with `comp.get_ability(AbilityType)`.
- **New Pattern**: 
  - `if comp.has_ability('CombatPropulsion'): ...`
  - `weapons = ship.get_components_with_ability('Weapon')`

## 2. Range Calculation
Range determination relies on iterating the component list and accessing properties specific to the `Weapon` class.

### Findings
- **`ship.max_weapon_range` (`ship.py`)**:
  - Iterates all components.
  - Checks `isinstance(comp, Weapon)`.
  - **Special Case**: Checks `isinstance(comp, SeekerWeapon)` to calculate range as `speed * endurance`.
  - Standard weapons use `comp.range`.

- **Combat Logic**:
  - `ship_combat.py`: `fire_weapons()` re-implements range checks using `comp.range` or the `SeekerWeapon` formula.

### Implications
- **Refactoring Needed**: 
  - The `WeaponAbility` should encapsulate the range calculation (including the Seeker logic).
  - `ship.max_weapon_range` should aggregate `ability.effective_range` from all Weapon abilities.

## 3. Special Abilities
Logic for special behaviors (Kiting, Ramming, Hangar) is scattered between `ai_behaviors.py` and `ship_combat.py`.

### Findings
- **Kiting (`KiteBehavior` in `ai_behaviors.py`)**:
  - Relies entirely on `ship.max_weapon_range`. If the range calculation is fixed to use abilities, `KiteBehavior` should work without modification, as it works on the ship-level property.

- **Ramming (`RamBehavior`)**:
  - Does not check for "RammingProw" or mass. It simply navigates to `dist=0`.
  - **Note**: `TargetEvaluator` has rules for `mass`, indicating preference for heavy targets, but not heavy *self*.

- **Point Defense (PDC)**:
  - `ship_combat.py`: `_find_pdc_target` assumes the component has `comp.range`.
  - `ai.py`: Explicitly checks `comp.abilities.get('PointDefense')`. This is already partially using the ability system (dict lookup), which is good.

- **Hangars**:
  - `ship_combat.py`: Explicit `isinstance(comp, Hangar)` check to trigger launches.
  - `ship_stats.py`: Explicit `isinstance` check to calculate `fighter_capacity`.

## 4. Resource System
The `ship_combat.py` file has a mixed implementation of the new Resource System.

### Findings
- **Shield Regen**:
  - Correctly checks `self.resources.get_resource('energy')`.
  - **Issue**: It duplicates logic found in `ship_stats.py` regarding costs.

- **Firing Costs**:
  - `comp.consume_activation()` is called in `fire_weapons`. This assumes the component (or its ability) handles the deduction.

## Recommendations
1.  **Iterate Abilities, Not Components**: Change `ship_stats.py` to iterate `comp.ability_instances` instead of `if isinstance(comp, Type)`.
2.  **Encapsulate Weapon Logic**: Move `range` and `fire()` logic into `ProjectileWeaponAbility` and `BeamWeaponAbility`. `ship_combat.py` should call `active_weapon_ability.fire()`.
3.  **Unified Range Property**: `ship.max_weapon_range` must query abilities.
4.  **Tag-Based/Ability-Based AI**: `AIController` should query `ship.has_capability('point_defense')` rather than inspecting component logic.
