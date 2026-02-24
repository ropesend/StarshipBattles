# Phase 3: DesignMetadata Ship Calculation Fix

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-178 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Fix the broken `_calculate_combat_power_from_ship` and `_calculate_resource_cost_from_ship` methods that reference nonexistent `category` attribute, and remove legacy "old layer format" warnings.

---

## Tasks

### Task 3.1: Fix _calculate_combat_power_from_ship [Medium]
**File:** `game/strategy/data/design_metadata.py`
**Tests:** `pytest tests/unit/strategy/test_design_metadata.py`

- [ ] Check `data/components.json` for exact `major_classification` and `type_str` values for weapons and armor
- [ ] Replace `hasattr(comp, 'category') and comp.category == 'weapon'` (line 207) with `comp.major_classification == 'Weapons'`
- [ ] Replace `hasattr(comp, 'category') and comp.category == 'armor'` (line 211) with `comp.major_classification == 'Armor'`
- [ ] Replace `getattr(comp, 'damage', 0)` with correct attribute (check Component for weapon damage property)
- [ ] Replace `getattr(comp, 'rate_of_fire', 0)` with correct attribute
- [ ] Replace `getattr(comp, 'hp', 0)` with `comp.max_hp` (Component line 115)
- [ ] Verify method now returns non-zero values for weapon/armor components

**Notes:** This is a BUG FIX. Component has `type_str` and `major_classification`, NOT `category`. Current code always returns 0.0.

### Task 3.2: Fix _calculate_resource_cost_from_ship [Simple]
**File:** `game/strategy/data/design_metadata.py`
**Tests:** `pytest tests/unit/strategy/test_design_metadata.py`

- [ ] Remove `hasattr(comp, 'cost')` guard (line 245) — Component always has `.cost`
- [ ] Access `comp.cost` directly
- [ ] Verify existing tests pass

**Notes:**

### Task 3.3: Remove "Old layer format" warnings [Simple]
**File:** `game/strategy/data/design_metadata.py`
**Tests:** `pytest tests/unit/strategy/test_design_metadata.py`

- [ ] In `_calculate_combat_power` (lines 182-185): Remove `else` branch with warning; treat non-list as empty
- [ ] In `_calculate_resource_cost` (lines 227-229): Same treatment
- [ ] Verify existing tests pass

**Notes:** Per CLAUDE.md System Migration Policy: old formats should be eradicated, not handled gracefully.

### Task 3.4: Update tests for fixed calculations [Medium]
**File:** `tests/unit/strategy/test_design_metadata.py`
**Tests:** `pytest tests/unit/strategy/test_design_metadata.py`

- [ ] Update `TestDesignMetadataCombatPowerFromShip` mock components to use correct attributes (`major_classification` instead of `category`)
- [ ] Verify weapon mock produces non-zero combat power
- [ ] Verify armor mock produces non-zero combat power
- [ ] Add test: components with non-weapon/armor classification contribute 0
- [ ] Update resource cost tests for `hasattr` removal if needed

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `pytest tests/unit/strategy/test_design_metadata.py` passes
- [ ] `_calculate_combat_power_from_ship` returns non-zero for weapon/armor components
- [ ] "Old layer format" warnings removed
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
