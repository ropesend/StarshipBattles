# Phase 4: Fleet Generic Methods

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-08 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Add generic resource checking and consumption methods

---

## Tasks

### Task 4.1: Add Generic Movement Resource Methods [Medium]
**File:** `game/strategy/data/fleet.py`
**Tests:** `pytest tests/unit/strategy/test_fleet.py`

- [x] Add `get_movement_resource_costs()`, `has_resources_for_movement()`, `consume_movement_resources()`

**Notes:** Lines 225-289 implement all three methods

### Task 4.2: Refactor Warp Resource Methods to Generic [Medium]
**File:** `game/strategy/data/fleet.py`
**Tests:** `pytest tests/unit/strategy/test_fleet.py`

- [x] Update `has_resources_for_warp()` to use generic methods
- [x] Update `consume_warp_resources()` similarly
- [x] Add `get_warp_resource_costs()` method

**Notes:** Lines 293-317 implement generic warp resource methods

### Task 4.3: Keep Backward Compatibility Aliases [Simple]
**File:** `game/strategy/data/fleet.py`
**Tests:** No changes needed

- [x] Verify `has_fuel_for_movement()` wraps `has_resources_for_movement()`
- [x] Verify `consume_fleet_fuel()` wraps `consume_movement_resources()`
- [x] Verify `has_energy_for_warp()` wraps `has_resources_for_warp()`
- [x] Verify `consume_warp_energy()` wraps `consume_warp_resources()`

**Notes:** `has_energy_for_warp()` (line 268) and `consume_warp_energy()` (line 319) wrap generic methods

---

## Phase Completion Checklist
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
