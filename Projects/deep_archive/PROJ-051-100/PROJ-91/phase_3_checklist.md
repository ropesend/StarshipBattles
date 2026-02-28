# Phase 3: Remove Type-Specific Methods & Clean Up

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-91 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Delete the 7 type-specific methods from ShipInstance, delete deprecated tests, and do final verification.

---

## Tasks

### Task 3.1: Delete Type-Specific Methods from ShipInstance [Simple]
**File:** `game/strategy/data/ship_instance.py`
**Tests:** `pytest tests/ -n 12`

Remove these methods entirely:
- [x] Delete `get_fuel_cost_per_hex()` (lines 246-254)
- [x] Delete `get_current_fuel()` (lines 256-265)
- [x] Delete `consume_fuel()` (lines 267-286)
- [x] Delete `get_warp_energy_cost()` (lines 288-296)
- [x] Delete `get_warp_fuel_cost()` (lines 298-306)
- [x] Delete `get_current_energy()` (lines 308-317)
- [x] Delete `consume_energy()` (lines 319-338)
- [x] Verify: `pytest tests/ --testmon` passes (all callers already migrated in Phase 2)

**Notes:** Line numbers may shift after Phase 1/2 edits. Delete methods by name, not by line number.

### Task 3.2: Delete Deprecated Tests [Simple]
**File:** `tests/unit/strategy/ship_instance/test_convenience_methods.py`
**Tests:** `pytest tests/unit/strategy/ship_instance/`

- [x] Delete `test_get_current_fuel` test method
- [x] Delete `test_consume_fuel` test method
- [x] Delete `test_get_current_energy` test method
- [x] Delete `test_consume_energy` test method
- [x] If the `TestResourceConvenienceMethods` class is now empty, delete the entire class
- [x] Verify the remaining tests (`TestResourceMethodInteractions`) still pass
- [x] Verify: `pytest tests/unit/strategy/ship_instance/test_convenience_methods.py -v`

**Notes:**

### Task 3.3: Final Grep Verification [Simple]
**Tests:** Full suite

- [x] Grep entire codebase for all removed method names — confirm zero matches outside comments/docs:
  - `get_current_fuel` (found only in ShipResourceManager internals + tests for manager)
  - `consume_fuel` (found only in ShipResourceManager internals + tests for manager)
  - `get_current_energy` (found only in ShipResourceManager internals + tests for manager)
  - `consume_energy` (found only in ShipResourceManager internals + tests for manager)
  - `get_fuel_cost_per_hex` (found only in ShipResourceManager/FleetResourceAggregator internals)
  - `get_warp_fuel_cost` (found only in FleetResourceAggregator internals)
  - `get_warp_energy_cost` (found only in FleetResourceAggregator internals)
  - `has_fuel_for_movement` (found only in FleetResourceAggregator internals)
  - `consume_fleet_fuel` (found only in FleetResourceAggregator internals)
- [x] Grep for `hasattr(ship, 'resources')` — should find 0 ✓
- [x] Grep for `['fuel', 'energy', 'ammo']` in bridge methods — only in UI display code (out of scope)
- [x] Fix any remaining references found (cleaned up test mock helper)

**Notes:**

### Task 3.4: Final Full Test Suite [Simple]
**Tests:** `pytest tests/ -n 12`

- [x] Run full test suite: `pytest tests/ -n 12`
- [x] All 7557 tests pass (7561 - 4 deleted tests = 7557)
- [x] No new warnings introduced

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Full test suite passes
- [x] Final grep verification clean
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to `Complete`
- [x] Update plan.md Verification checklist
