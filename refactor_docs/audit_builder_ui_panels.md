# Audit: Builder UI Panels

**Status:** Draft
**Date:** 2026-01-02
**Target Files:**
- `ui/builder/detail_panel.py`
- `ui/builder/layer_panel.py`
- `ui/builder/left_panel.py`
- `ui/builder/right_panel.py`

## Findings

### 1. `ui/builder/detail_panel.py`

| Line(s) | Pattern | Problematic Code | Impact | Recommended Fix |
| :--- | :--- | :--- | :--- | :--- |
| **5-7** | **Legacy Imports** | `from components import (Engine, Thruster, Armor, Tank, Generator, CrewQuarters, LifeSupport)` | Imports legacy subclasses that are effectively deprecated. | **Remove imports**. These classes are no longer directly referenced in the code (it uses `comp` generically or `comp.abilities`). |
| **115** | **`type_str`** | `add_line(f"{comp.type_str}", '#C8C8C8')` | Relies on legacy `type_str` property for display. | Use a **Role/Tag based label** or map `type_str` to a cleaner display name if strictly necessary. |
| **132** | **Direct Attribute** | `if hasattr(comp, 'base_accuracy') and comp.base_accuracy > 0:` | Accesses legacy `base_accuracy` attribute directly. | **Migrate to Ability**: Ensure the weapon ability (e.g. `ProjectileWeaponAbility`) exports accuracy in `get_ui_rows()`. |
| **142** | **Direct Attribute** | `if hasattr(comp, 'to_hit_defense'):` | Accesses legacy `to_hit_defense` attribute. | **Migrate to Ability**: Ensure `EvasionAbility` or `DefensiveAbility` exports this in `get_ui_rows()`. |
| **153-198** | **Manual UI Construction** | `for k, v in comp.abilities.items(): ... if k == "CommandAndControl": ...` | Manually constructs UI rows for specific ability keys instead of delegating to the Ability class. | **Refactor**: Ensure `CommandAndControl`, `CrewCapacity`, `LifeSupportCapacity`, `ToHit*` abilities all implement `get_ui_rows()`. Replace this entire block with generic iteration or `comp.get_ui_rows()` aggregation. |
| **172** | **Legacy Strings** | `if k in ["ProjectileWeapon", "BeamWeapon", "Armor"]` | Hardcoded exclusion of legacy keys or ability names. | **Cleanup**: Removing the need for this block by properly implementing `get_ui_rows` in those abilities. |

### 2. `ui/builder/layer_panel.py`

| Line(s) | Pattern | Problematic Code | Impact | Recommended Fix |
| :--- | :--- | :--- | :--- | :--- |
| **15, 39** | **Categorization** | `from ui.builder.grouping_strategies import ..., TypeGroupingStrategy` | Uses Component Type (legacy string) for grouping components in the UI. | **Refactor Strategy**: Update `TypeGroupingStrategy` to group by **Primary Role** (derived from Ability Tags) instead of `type_str`. |

### 3. `ui/builder/left_panel.py`

| Line(s) | Pattern | Problematic Code | Impact | Recommended Fix |
| :--- | :--- | :--- | :--- | :--- |
| **113-114** | **Categorization** | `sorted(list(set(c.type_str for c in builder.available_components)))` | Collects legacy `type_str` logic for the "Filter by Type" dropdown. | **Use Tags**: Collect unique **Primary Roles** or **Categories** from `Ability.tags` or a new `category` field in component data. |
| **228** | **Categorization** | `if c.type_str == self.current_type_filter:` | Filters components by comparing legacy `type_str`. | **Refactor**: Check `c.has_tag(filter)` or check against the Primary Role derived from abilities. |
| **295** | **Categorization** | `filtered.sort(key=lambda c: (c.type_str, c.name))` | Sorts by `type_str`. | **Refactor**: Sort by Primary Role / Category. |

### 4. `ui/builder/right_panel.py`

*No critical legacy patterns found.*
This file relies on `STATS_CONFIG` (data-driven) and `get_logistics_rows` (dynamic), which matches the target architecture. The `VEHICLE_CLASSES` import is standard for ship hull definitions.

## Summary Checklist
- [ ] **detail_panel.py**: Remove legacy component imports.
- [ ] **detail_panel.py**: Refactor manual `comp.abilities` loop -> `get_ui_rows()`.
- [ ] **detail_panel.py**: Migrate `base_accuracy` and `to_hit_defense` display to Abilities.
- [ ] **left_panel.py**: Refactor "Filter by Type" to use Ability Tags/Categories.
