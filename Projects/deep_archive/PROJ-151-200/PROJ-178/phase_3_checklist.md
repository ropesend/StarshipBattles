# Phase 3: DesignMetadata Ship Calculation Fix

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-178 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Fix the broken `_calculate_combat_power_from_ship` and `_calculate_resource_cost_from_ship` methods that reference nonexistent `category` attribute, and remove legacy "old layer format" warnings.

---

## Tasks

### Task 3.1: Fix _calculate_combat_power_from_ship [Medium]
**File:** `game/strategy/data/design_metadata.py`
**Tests:** `pytest tests/unit/strategy/test_design_metadata.py`

- [x] Check `data/components.json` for exact `major_classification` and `type_str` values for weapons and armor
- [x] Replace `hasattr(comp, 'category') and comp.category == 'weapon'` (line 207) with `comp.major_classification == 'Weapons'`
- [x] Replace `hasattr(comp, 'category') and comp.category == 'armor'` (line 211) with `comp.major_classification == 'Armor'`
- [x] Replace `getattr(comp, 'damage', 0)` with correct attribute (check Component for weapon damage property)
- [x] Replace `getattr(comp, 'rate_of_fire', 0)` with correct attribute
- [x] Replace `getattr(comp, 'hp', 0)` with `comp.max_hp` (Component line 115)
- [x] Verify method now returns non-zero values for weapon/armor components

**Notes:** Fixed to use `comp.major_classification == 'Weapons'/'Armor'`, access weapon abilities via `comp.get_abilities('WeaponAbility')` for damage/reload_time, and use `comp.max_hp` for armor.

### Task 3.2: Fix _calculate_resource_cost_from_ship [Simple]
**File:** `game/strategy/data/design_metadata.py`
**Tests:** `pytest tests/unit/strategy/test_design_metadata.py`

- [x] Remove `hasattr(comp, 'cost')` guard (line 245) — Component always has `.cost`
- [x] Access `comp.cost` directly
- [x] Verify existing tests pass

**Notes:** Removed guard, added docstring noting Component.cost always exists.

### Task 3.3: Remove "Old layer format" warnings [Simple]
**File:** `game/strategy/data/design_metadata.py`
**Tests:** `pytest tests/unit/strategy/test_design_metadata.py`

- [x] In `_calculate_combat_power` (lines 182-185): Remove `else` branch with warning; treat non-list as empty
- [x] In `_calculate_resource_cost` (lines 227-229): Same treatment
- [x] Verify existing tests pass

**Notes:** Per CLAUDE.md System Migration Policy: old formats are now silently ignored (not warned).

### Task 3.4: Update tests for fixed calculations [Medium]
**File:** `tests/unit/strategy/test_design_metadata.py`
**Tests:** `pytest tests/unit/strategy/test_design_metadata.py`

- [x] Update `TestDesignMetadataCombatPowerFromShip` mock components to use correct attributes (`major_classification` instead of `category`)
- [x] Verify weapon mock produces non-zero combat power
- [x] Verify armor mock produces non-zero combat power
- [x] Add test: components with non-weapon/armor classification contribute 0
- [x] Update resource cost tests for `hasattr` removal if needed

**Notes:** Updated all tests to use `major_classification`, `max_hp`, and mock `WeaponAbility` instances. Added 2 new tests: `test_calculate_combat_power_from_ship_weapon_no_ability` and `test_calculate_combat_power_from_ship_non_weapon_classification`.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] `pytest tests/unit/strategy/test_design_metadata.py` passes (46 passed)
- [x] `_calculate_combat_power_from_ship` returns non-zero for weapon/armor components
- [x] "Old layer format" warnings removed
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
