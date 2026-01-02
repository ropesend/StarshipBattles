# Audit Report: Data Validation & I/O

## Executive Summary
This audit covers `ship_validator.py`, `ship_io.py`, and the data files in `data/`. The focus was to identify legacy validation rules, type-based logic, and incomplete data migration.

**Status**:
- `ship_validator.py`: **Changes Required** (Relies on legacy `type_str` for layer restrictions).
- `data/modifiers.json`: **Major Updates Required** (Extensive use of `allow_types`/`deny_types`).
- `data/components.json`: **Minor Cleanup Required** (Legacy `PointDefense` boolean flag).
- `data/vehicleclasses.json`: **Clean** (Uses ability-based requirements).
- `ship_io.py`: **Clean**.

---

## Detailed Findings

### 1. Legacy Type-Based Validation Rules
The `LayerRestrictionDefinitionRule` uses `component.type_str` to enforce "block_type" and "allow_type" rules. This should be migrated to check for `tags` or specific `abilities`.

*   **File**: `c:\Dev\Starship Battles\ship_validator.py`
*   **Line**: 113
*   **Code**: `if component.type_str == blocked_type:`
*   **Data Impact**: Validation relies on the string name of the component class (e.g., "Engine", "Weapon"), which encourages keeping legacy subclasses.
*   **Fix Required**: Update rule to support `block_ability` or `block_tag`. Deprecate `block_type`.

*   **File**: `c:\Dev\Starship Battles\ship_validator.py`
*   **Line**: 136
*   **Code**: `if component.type_str == target:`
*   **Fix Required**: Update rule to support `allow_ability` or `allow_tag`.

### 2. Legacy Modifier Restrictions
`modifiers.json` extensively uses `allow_types` and `deny_types` lists, which reference legacy component class names (e.g. "ProjectileWeapon", "SeekerWeapon"). This logic is handled in `ModifierLogic`, but the data itself is legacy.

*   **File**: `c:\Dev\Starship Battles\data\modifiers.json`
*   **Entries**:
    *   `hardened`: `"deny_types": ["Armor"]`
    *   `turret_mount`: `"allow_types": ["Weapon", "ProjectileWeapon", "BeamWeapon", "SeekerWeapon"]`
    *   `range_mount`: `"allow_types": ["ProjectileWeapon", "BeamWeapon"]`
    *   (and 8 other entries)
*   **Data Impact**: Modifiers are tied to legacy class names.
*   **Fix Required**:
    *   Migrate `allow_types` -> `allow_abilities` (e.g. `["WeaponAbility"]`) or `allow_tags` (e.g. `["weapon"]`).
    *   Example: `turret_mount` should allow `["WeaponAbility"]`.

### 3. Legacy PointDefense Flag
The "Point Defence Cannon" component uses a legacy boolean `PointDefense` in its abilities dict. This should likely be a `PointDefenseAbility` or a standardized tag.

*   **File**: `c:\Dev\Starship Battles\data\components.json`
*   **Line**: 481
*   **Code**: `"PointDefense": true`
*   **Data Impact**: Requires special handling in code to detect PDC capability (checking this specific key).
*   **Fix Required**: Convert to `"PointDefenseAbility": {}` or add `"tags": ["pdc"]` (if tag system is fully adopted).

### 4. Legacy Variable Naming in Validator
A variable named `legacy_req` exists in `ClassRequirementsRule`, suggesting a temporary logic bridge.

*   **File**: `c:\Dev\Starship Battles\ship_validator.py`
*   **Line**: 219
*   **Code**: `legacy_req = abs(min(0, ability_totals.get('CrewCapacity', 0)))`
*   **Fix Required**: Rename or refactor to clarify intent (e.g., `crew_deficit`).

## Summary Checklist status

1.  Validation rules using `isinstance` checks: **CLEAN** (None found).
2.  Type-based validation that should use abilities: **FOUND** (`ship_validator.py`).
3.  components.json entries with legacy root-level attributes: **CLEAN** (Root attributes appear structural/factory-related).
4.  vehicleclasses.json requirements referencing legacy component types: **CLEAN** (Uses ability names).
5.  Modifier restrictions using component type instead of ability presence: **FOUND** (`modifiers.json`).
6.  Save/load serialization assuming legacy attribute locations: **CLEAN** (`ship_io.py` is generic).
7.  Any vestiges of Phase 6 migration incomplete: **FOUND** (`PointDefense` flag, `legacy_req` var).
