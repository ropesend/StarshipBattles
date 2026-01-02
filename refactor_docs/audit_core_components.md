# Core Components Legacy Code Audit

This report details legacy code patterns found in `components.py`, `abilities.py`, `resources.py`, `component_modifiers.py`, and `formula_system.py`.

## Summary
The audit revealed significant legacy code retention in `components.py`, primarily consisting of backward-compatibility logic ("shims") for the migration to the new Ability System. The entire `Weapon` class hierarchy and legacy `Engine`, `Thruster`, `Shield` subclasses are still present and functioning as wrappers or duplicators of ability logic.

## Detailed Findings

### 1. components.py

#### Legacy Subclass & Type Patterns
| Line | Code Snippet | Issue | Recommendation |
|------|--------------|-------|----------------|
| 3    | `from enum import Enum, auto` | `ComponentStatus` enum might be legacy if statuses are now strictly data-driven or handled differently, but likely okay to keep for now. | **Keep** as generic state. |
| 69   | `self.type_str = data['type']` | Relies on legacy string types ("Engine", "Weapon") instead of capability detection (`has_ability`). | **Refactor**: Replace usages with `if self.has_ability("CombatPropulsion"):`. |
| 153  | `def has_pdc_ability(self) -> bool:` | Contains explicit legacy fallback: `if self.abilities.get('PointDefense', False):`. | **Refactor**: Remove legacy check, enforce tag-based `pdc` detection. |
| 182  | `def _instantiate_abilities(self):` | Contains massive "Legacy Shim (Auto-Correction)" section (lines 198-296). | **Remove**: Entire shim section should be deleted once data migration is verified (Phase 6 verified). |
| 527  | `if hasattr(self, 'thrust_force'):` | Direct attribute access for legacy `Engine` prop. | **Remove**: Should rely on `CombatPropulsion` ability values. |
| 529  | `if hasattr(self, 'turn_speed'):` | Direct attribute access for legacy `Thruster` prop. | **Remove**: Should rely on `ManeuveringThruster` ability values. |
| 649  | `class Bridge(Component):` | Legacy subclass. | **Remove**: Convert to generic `Component` with `CommandAndControl` ability. |
| 655  | `class Weapon(Component):` | Legacy subclass duplicating `WeaponAbility` logic (`fire`, `can_fire`, `get_damage`). | **Remove**: Logic must strictly live in `WeaponAbility`. |
| 731  | `class ProjectileWeapon(Weapon):` | Legacy subclass. | **Remove**: Use `Component` + `ProjectileWeaponAbility`. |
| 750  | `class Engine(Component):` | Legacy subclass defining `thrust_force`. | **Remove**: Use `Component` + `CombatPropulsion`. |
| 763  | `class Thruster(Component):` | Legacy subclass defining `turn_speed`. | **Remove**: Use `Component` + `ManeuveringThruster`. |
| 799  | `class BeamWeapon(Weapon):` | Legacy subclass. | **Remove**: Use `Component` + `BeamWeaponAbility`. |
| 862  | `class SeekerWeapon(Weapon):` | Legacy subclass. | **Remove**: Use `Component` + `SeekerWeaponAbility`. |
| 943  | `class Shield(Component):` | Legacy subclass defining `shield_capacity`. | **Remove**: Use `Component` + `ShieldProjection`. |
| 1021 | `COMPONENT_TYPE_MAP = {...}` | Hardcoded mapping of string types to legacy subclasses. | **Remove**: All components should be instantiated as `Component` (or a factory that attaches abilities). |

#### Legacy Shims & Attribute Access
| Line | Code Snippet | Issue | Recommendation |
|------|--------------|-------|----------------|
| 114  | `if key in ['mass', 'hp', 'damage', 'range', 'cost']:` | Formula parsing forcing legacy attributes onto component instance. | **Refactor**: Only `mass`, `hp`, `cost` should remain on Component. `damage` and `range` belong to abilities. |
| 241  | `val = get_shim_value('thrust_force')` | Shim code reading legacy data. | **Remove**. |
| 263  | `if not has_weapon and is_positive(dmg):` | Auto-detection of weapons from legacy `damage` attribute. | **Remove**. |
| 359  | `if self.type_str in mod_def.restrictions['deny_types']:` | Modifier restriction checking legacy `type_str`. | **Refactor**: Modifiers should check for *Capabilities* (Abilities) or Tags, not legacy class strings. |
| 519  | `raw_damage = get_weapon_data_for_stats('damage', 0)` | `recalculate_stats` pulling weapon data to set component attribute. | **Remove**: `Component` should not have `self.damage` or `self.range`. |

### 2. abilities.py

#### Legacy/Transitional Factories
| Line | Code Snippet | Issue | Recommendation |
|------|--------------|-------|----------------|
| 322  | `"FuelStorage": lambda c, d: ...` | Shortcut factories for specific resource types. | **Keep**: These are useful shorthands for data definitions, even if "legacy-inspired". |

### 3. resources.py
*No critical legacy patterns found.* usage is consistent with new system.

### 4. component_modifiers.py

#### Semantic Coupling
| Line | Code Snippet | Issue | Recommendation |
|------|--------------|-------|----------------|
| 165  | `def seeker_stealth(val, stats):` | Specific modifier logic tied to specific component type logic. | **Keep**: These are functional. |

#### Potential Legacy Reference
| Line | Code Snippet | Issue | Recommendation |
|------|--------------|-------|----------------|
| 42   | `# Original: mass_mult *= cost_mult_increase...` | Comment referencing original legacy code behavior. | **Update/Remove Comment**: Once verified. |

### 5. formula_system.py
*No legacy patterns found.*

## Global Recommendations
1.  **Phase out `Component` subclasses**: The `COMPONENT_TYPE_MAP` should eventually point `Component` for all types, or specialized classes that *only* handle visualization/callbacks, not game logic.
2.  **Strict Ability Usage**: Remove all `hasattr(self, 'thrust_force')` style checks. If a component doesn't have the `CombatPropulsion` ability, it doesn't thrust.
3.  **Data Cleanup**: Ensure all JSON data files are fully migrated (Phase 6) so that the `_instantiate_abilities` shims can be safely deleted.
