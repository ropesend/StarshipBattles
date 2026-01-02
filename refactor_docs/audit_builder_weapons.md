# Builder Weapons & Modifier UI Audit

## Executive Summary
This audit reviews the Builder UI components for legacy code patterns related to the Component Ability System refactor. The primary focus is replacing direct attribute access, type string checks, and legacy method calls with Ability-based equivalents.

**Target Files:**
- `ui/builder/weapons_panel.py`
- `ui/builder/modifier_logic.py`
- `ui/builder/modifier_row.py`
- `ui/builder/schematic_view.py`

## Findings

### 1. Direct Component Attribute Access
Legacy code reads stats like `range`, `damage`, `firing_arc`, etc. directly from the component instance, which relies on legacy `__getattr__` or `Weapon` subclass properties.

| File | Line | Code | Type | Fix Approach |
|------|------|------|------|--------------|
| `weapons_panel.py` | 275-278 | `base_acc = getattr(weapon, 'base_accuracy', 2.0)`<br>`falloff = getattr(weapon, 'accuracy_falloff', ...)`<br>`max_range = getattr(weapon, 'range', 0)`<br>`damage = getattr(weapon, 'damage', 0)` | Read/Calc | **MUST FIX**: Retrieve `WeaponAbility` instance and access properties: `ab = comp.get_ability('WeaponAbility'); ab.range`, etc. |
| `weapons_panel.py` | 361 | `weapon_range = getattr(weapon, 'range', 0)` | Read | **MUST FIX**: Use `WeaponAbility` range property. |
| `weapons_panel.py` | 439-443 | `getattr(weapon, 'base_accuracy', 1.0)`<br>`getattr(weapon, 'accuracy_falloff', 0.0)`<br>`getattr(weapon, 'damage', 0)` | Read | **MUST FIX**: Use `WeaponAbility` properties in tooltip calculation. |
| `weapons_panel.py` | 549-550 | `facing = weapon.facing_angle`<br>`arc = weapon.firing_arc` | Read (Visual) | **MUST_FIX**: Facing might remain on component (physical orientation), but Arc is definitely a property of the WeaponAbility (or Turret/Fixed nature). Check `get_ability_value` for arc. |
| `weapons_panel.py` | 654-655 | `getattr(weapon, 'base_accuracy', 1.0)`<br>`getattr(weapon, 'accuracy_falloff', 0.0)` | Read | **MUST FIX**: Update beam bar drawing to use ability stats. |
| `schematic_view.py` | 125-127 | `arc_degrees = getattr(weapon, 'firing_arc', 20)`<br>`weapon_range = getattr(weapon, 'range', 1000)`<br>`facing = getattr(weapon, 'facing_angle', 0)` | Read (Visual) | **MUST FIX**: Update arc visualization to pull from `WeaponAbility` or `BeamWeaponAbility`. |

### 2. Type String Checks (`type_str`)
Logic uses string matching on `component.type_str` instead of checking for capabilities/abilities.

| File | Line | Code | Type | Fix Approach |
|------|------|------|------|--------------|
| `modifier_logic.py` | 23, 27 | `if component.type_str not in mod_def.restrictions...` | Logic | **SHOULD FIX**: If possible, map restrictions to Abilities (e.g., "Requires `WeaponAbility`") rather than "Weapon" type string. However, strict type restrictions might still validly use `major_classification` or tags. |

### 3. Direct Data Dictionary Access
Legacy logic reads `firing_arc` from `component.data`, which bypasses the Ability system's data structure (where stats are nested under `abilities`).

| File | Line | Code | Type | Fix Approach |
|------|------|------|------|--------------|
| `modifier_logic.py` | 123 | `base_arc = component.data.get('firing_arc')` | Logic | **MUST FIX**: Use the Ability System's data source of truth. The code at lines 126-130 already attempts a shim look-up. This should be standardized to always look in the ability dict first or exclusively. |
| `modifier_logic.py` | 161 | `base_arc = component.data.get('firing_arc')` | Logic | **MUST FIX**: Same as above, for `get_local_min_max`. |

### 4. Legacy Method Existence Checks
Checks for `get_damage` method existence, which implies a legacy `Weapon` class structure.

| File | Line | Code | Type | Fix Approach |
|------|------|------|------|--------------|
| `weapons_panel.py` | 475 | `if hasattr(weapon, 'get_damage'):` | Logic | **MUST FIX**: `WeaponAbility` should have a standard `get_damage_at_range(r)` method. Replace with `if ab := weapon.get_ability('WeaponAbility'): dmg = ab.get_damage(range)`. |
| `weapons_panel.py` | 674 | `if hasattr(weapon, 'get_damage'):` | Logic | **MUST FIX**: Same as above (Beam bar). |
| `weapons_panel.py` | 742 | `if hasattr(weapon, 'get_damage'):` | Logic | **MUST FIX**: Same as above (Projectile bar). |

### 5. Firing Arc Visualization
The `draw_direction_indicator` and `schematic_view` rely on `firing_arc`.

- **Issue**: `firing_arc` is now a property that might be modified by `TurretMount` or `FixedMount` logic, which resides in the Ability or Modifier system, not a static attribute on the component.
- **Fix**: Ensure `WeaponAbility` exposes the *modified* effective firing arc (post-modifiers), and the UI reads that.

## Summary of Work Required
1.  **Refactor `WeaponsReportPanel` (`weapons_panel.py`)**:
    - Inject `WeaponAbility` retrieval in `update()` and cache it.
    - Replace all `getattr(weapon, ...)` calls with access to the cached ability instance.
    - Standardize damage calculation using `WeaponAbility.get_damage_at_range()`.
2.  **Refactor `ModifierLogic` (`modifier_logic.py`)**:
    - Update `get_initial_value` and `get_local_min_max` to prioritize reading `firing_arc` from the `WeaponAbility` data dict, removing reliance on root-level `data['firing_arc']`.
3.  **Refactor `SchematicView` (`schematic_view.py`)**:
    - Update `_get_cached_arc` to obtain stats from `comp.get_ability('WeaponAbility')`.

## Migration Note
The `modifier_row.py` file appears clean of legacy component pattern violations, assuming it operates on valid `mod_id`s that are handled correctly by the logic layer.
