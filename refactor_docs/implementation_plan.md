# Starship Battles Refactor Implementation Plan

## Phase 1-6: Complete ✅
(See previous revisions for details)

## Phase 7: Legacy Removal ✅
**Status:** Complete and Verified.

## Phase 8: Final Cleanup & Hardening (New)
**Goal:** Address findings from the 100% Code Coverage Audit to ensure zero legacy patterns remain.

### 1. Core Infrastructure Hardening
- **File:** `components.py`
    - [ ] Remove `base_damage`, `base_range` initialization in `__init__`.
- **File:** `abilities.py`
    - [ ] Implement `recalculate()` in `BeamWeaponAbility` (Sync `accuracy_add` -> `base_accuracy`).
    - [ ] Update `WeaponAbility.recalculate()` to sync `facing_angle` from `stats['properties']`.
- **File:** `unit_tests/test_components.py`
    - [ ] Remove legacy alias usage (`Tank`, `Weapon`) and `isinstance` checks.

### 2. Physics & Stats Cleanup
- **File:** `unit_tests/test_ship_stats.py`
    - [ ] **Critical:** Replace all `self.Engine(...)`, `self.Thruster(...)` instantiations with `Component(...)`.
- **File:** `ship_stats.py`
    - [ ] Refactor `_priority_sort_key` to use `has_ability('CombatPropulsion')` instead of `type_str == "Engine"`.
    - [ ] Remove unused imports (`Shield`, `Hangar`, etc.).
- **File:** `ship.py`
    - [ ] Remove unused legacy imports.

### 3. Combat Logic Strictness
- **File:** `ship_combat.py`
    - [ ] Remove legacy fallback `getattr(comp, 'range', 0)` in `_find_pdc_target`. Any missing ability should be a hard error or return 0 safely without fallback.

### 4. UI Modernization (Deep Refactor)
- **File:** `ui/builder/detail_panel.py`
    - [ ] Refactor `show_component` to remove manual `if/elif` ability chain.
    - [ ] Use `comp.get_ui_rows()` exclusively for display.
- **File:** `ui/builder/weapons_panel.py`
    - [ ] Refactor `_calculate_threshold_ranges`, `_draw_beam_weapon_bar` to use `weapon.get_ability('WeaponAbility')`.
    - [ ] Remove direct access to `weapon.damage`, `weapon.range`.

### 5. Data & Validation
- **File:** `ship_validator.py`
    - [ ] Update `LayerRestrictionDefinitionRule` to support Ability-based validation (`allow_ability`/`deny_ability`).



## Phase 10: Final Polish (Deep Dive Audit Findings)
**Goal:** Address specific legacy artifacts and minor logic gaps identified in the "Deep Dive" audit to achieve a 100% pure v2.0 codebase.

### 1. Core Infrastructure & Logic (`ship.py`, `components.py`)
- **Refactor `ship.py`**:
    - [ ] **Sensor/ECM Logic:** Refactor `get_total_sensor_score` and `get_total_ecm_score` to use `comp.get_abilities()` aggregation instead of direct `comp.abilities` dictionary checks.
    - [ ] **Legacy Dict:** Remove `SHIP_CLASSES` dictionary and update usages to `VEHICLE_CLASSES`.
    - [ ] **Dead Code:** Remove legacy fallback comments and dead `pass` blocks.
- **Refactor `components.py`**:
    - [ ] **PDC Fallback:** Remove `self.abilities.get('PointDefense')` check in `has_pdc_ability`.
    - [ ] **Aliases:** Remove `Weapon = Component`, `Engine = Component` etc. aliases.
    - [ ] **Map Update:** Update `COMPONENT_TYPE_MAP` to use `Component` directly.

### 2. Ability Logic Hardening (`abilities.py`)
- **Implement `recalculate()`**:
    - [ ] `VehicleLaunchAbility`: Apply `capacity_mult` from component stats to `capacity`.
    - [ ] `ToHitAttackModifier`: Implement standard recalculate structure.
    - [ ] `ToHitDefenseModifier`: Implement standard recalculate structure.
    - [ ] `EmissiveArmor`: Implement standard recalculate structure.

### 3. UI Cleanup (`builder_gui.py`)
- **Import Cleanup**:
    - [ ] Remove unused imports of legacy classes (`BeamWeapon`, `Engine`, `Shield`, etc.) from `components`.

### 4. Optional / Architectural Polish
- **Armor Ability**:
    - [ ] Register a dummy `Armor` ability class in `abilities.py` so `has_ability('Armor')` works, allowing removal of `comp.abilities.get('Armor')` checks in `ship_stats.py`.


