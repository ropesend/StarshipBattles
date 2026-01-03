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

## Verification Plan
1. Run `unit_tests/test_ship_stats.py` after refactoring it to ensuring no regression.
2. Run `unit_tests/test_ui_*.py` and manually verify Builder UI after detail/weapon panel refactors.
3. Full suite pass: `python -m pytest unit_tests/`
