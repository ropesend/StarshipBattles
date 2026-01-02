# Combat System Audit - Legacy Code Patterns

**Focus Area**: `ship_combat.py`, `battle_engine.py`, `battle.py`, `collision_system.py`, `projectiles.py`, `projectile_manager.py`

> **Status**: Review Complete
> **Date**: 2026-01-02

---

## 1. `ship_combat.py`

### Legacy Component Attribute Access (MUST FIX)
Direct access to component attributes (`damage`, `range`, `firing_arc`, etc.) assumes either legacy data storage or rely on `__getattr__` shims acting as proxies to `WeaponAbility`. These should be updated to query the ability instance directly or use a unified helper.

| Line | Code Snippet | Issue | Recommendation |
|------|--------------|-------|----------------|
| 116 | `max_range = comp.range` | Legacy `range` attribute | `comp.get_ability('WeaponAbility').range` |
| 119 | `comp.projectile_speed * comp.endurance` | Legacy `projectile_speed`, `endurance` | Use ability values |
| 131 | `comp.firing_arc` | Legacy `firing_arc` | Use ability values |
| 161 | `comp.damage` | Legacy `damage` | Use ability values |
| 162 | `comp.range` | Legacy `range` | Use ability values |
| 183 | `comp.projectile_speed` | Legacy `projectile_speed` | Use ability values |
| 190 | `comp.damage` | Legacy `damage` | Use ability values |
| 191 | `range_val=comp.projectile_speed * ...` | Legacy attributes | Use ability values |
| 194 | `turn_rate=comp.turn_rate` | Legacy `turn_rate` | Use ability values |
| 212 | `damage=comp.damage` | Legacy `damage` | Use ability values |
| 213 | `range_val=comp.range` | Legacy `range` | Use ability values |
| 236 | `if dist > comp.range: continue` | Legacy `range` in `_find_pdc_target` | Use ability values |
| 254 | `comp.projectile_speed` | Legacy `projectile_speed` in firing solution | Use ability values |

### Legacy Weapon Firing Logic (SHOULD FIX)
Direct method calls on components bypass the explicit ability-driven logic, relying on the component class to hopefully delegate correctly.

| Line | Code Snippet | Issue | Recommendation |
|------|--------------|-------|----------------|
| 141 | `if valid_target and ... comp.fire(target):` | `comp.fire()` is a legacy entry point | `ability = comp.get_ability('WeaponAbility'); ability.fire(target)` |

### Imports (ACCEPTABLE)
| Line | Code Snippet | Issue | Recommendation |
|------|--------------|-------|----------------|
| 4 | `from components import ... BeamWeapon...` | Importing legacy subclasses | Low priority, used for type hints or specific checks elsewhere? Verify if needed. |

---

## 2. `collision_system.py`

### Legacy Method Calls (MUST FIX)
The collision system calls methods on `beam_comp` (`calculate_hit_chance`, `get_damage`) which likely exist on the legacy `Weapon` class or are shims. These methods should be on `BeamWeaponAbility` or accessed via it.

| Line | Code Snippet | Issue | Recommendation |
|------|--------------|-------|----------------|
| 67 | `beam_comp.calculate_hit_chance(...)` | Method likely belongs to ability logic | `ability.calculate_hit_chance(...)` |
| 71 | `damage = beam_comp.get_damage(hit_dist)` | Method likely belongs to ability logic | `ability.get_damage(hit_dist)` |

---

## 3. `projectile_manager.py`

### Legacy Method Calls (MUST FIX)
Projectiles store a reference to `source_weapon` (the Component). The manager accesses methods/attributes on this component directly.

| Line | Code Snippet | Issue | Recommendation |
|------|--------------|-------|----------------|
| 100 | `hasattr(p.source_weapon, 'get_damage')` | Checking component for method | Check `p.source_weapon_ability` instead? |
| 101 | `p.source_weapon.get_damage(hit_dist)` | Calling legacy method on component | Use ability method |
| 127 | `p.source_weapon.shots_hit += 1` | Updating component stats directly | `ability.record_hit()` |

---

## 4. `projectiles.py`

### Component Reference (SHOULD FIX)
| Line | Code Snippet | Issue | Recommendation |
|------|--------------|-------|----------------|
| 38 | `self.source_weapon = source_weapon` | Stores `Component` | Store `AbilityInstance` check if `source_weapon` is ability or component |

---

## Summary of Actions
1.  **Refactor `ship_combat.py`**: Update all attribute accesses to use `comp.get_ability('WeaponAbility').<attr>`. Refactor `comp.fire()` to use ability directly.
2.  **Refactor `collision_system.py`**: Update beam logic to expect an Ability instance or access the ability from the component.
3.  **Refactor `projectile_manager.py`**: Retrieve projectile damage from the stored Ability instance (or pass damage formula to projectile at creation to satisfy "Ability Data-Driven" requirement).
4.  **Update `Projectiles`**: Ensure they carry enough context (or the specific ability instance) to calculate dynamic damage (falloff) without relying on legacy Component methods.
