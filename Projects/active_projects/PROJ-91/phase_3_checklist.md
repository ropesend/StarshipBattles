# Phase 3: Remove Type-Specific Methods & Clean Up

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-91 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Delete the 7 type-specific methods from ShipInstance, delete deprecated tests, and do final verification.

---

## Tasks

### Task 3.1: Delete Type-Specific Methods from ShipInstance [Simple]
**File:** `game/strategy/data/ship_instance.py`
**Tests:** `pytest tests/ -n 12`

Remove these methods entirely:
- [ ] Delete `get_fuel_cost_per_hex()` (lines 246-254)
- [ ] Delete `get_current_fuel()` (lines 256-265)
- [ ] Delete `consume_fuel()` (lines 267-286)
- [ ] Delete `get_warp_energy_cost()` (lines 288-296)
- [ ] Delete `get_warp_fuel_cost()` (lines 298-306)
- [ ] Delete `get_current_energy()` (lines 308-317)
- [ ] Delete `consume_energy()` (lines 319-338)
- [ ] Verify: `pytest tests/ --testmon` passes (all callers already migrated in Phase 2)

**Notes:** Line numbers may shift after Phase 1/2 edits. Delete methods by name, not by line number.

### Task 3.2: Delete Deprecated Tests [Simple]
**File:** `tests/unit/strategy/ship_instance/test_convenience_methods.py`
**Tests:** `pytest tests/unit/strategy/ship_instance/`

- [ ] Delete `test_get_current_fuel` test method
- [ ] Delete `test_consume_fuel` test method
- [ ] Delete `test_get_current_energy` test method
- [ ] Delete `test_consume_energy` test method
- [ ] If the `TestResourceConvenienceMethods` class is now empty, delete the entire class
- [ ] Verify the remaining tests (`TestResourceMethodInteractions`) still pass
- [ ] Verify: `pytest tests/unit/strategy/ship_instance/test_convenience_methods.py -v`

**Notes:**

### Task 3.3: Final Grep Verification [Simple]
**Tests:** Full suite

- [ ] Grep entire codebase for all removed method names — confirm zero matches outside comments/docs:
  - `get_current_fuel` (should find 0 in .py files)
  - `consume_fuel` (should find 0)
  - `get_current_energy` (should find 0)
  - `consume_energy` (should find 0)
  - `get_fuel_cost_per_hex` (should find 0 — removed from both ShipInstance and Fleet)
  - `get_warp_fuel_cost` (should find 0 — removed from both ShipInstance and Fleet)
  - `get_warp_energy_cost` (should find 0 — removed from both ShipInstance and Fleet)
  - `has_fuel_for_movement` (should find 0 — removed from Fleet)
  - `consume_fleet_fuel` (should find 0 — removed from Fleet)
- [ ] Grep for `hasattr(ship, 'resources')` — should find 0
- [ ] Grep for `['fuel', 'energy', 'ammo']` in bridge methods — should find 0
- [ ] Fix any remaining references found

**Notes:**

### Task 3.4: Final Full Test Suite [Simple]
**Tests:** `pytest tests/ -n 12`

- [ ] Run full test suite: `pytest tests/ -n 12`
- [ ] All 7353+ tests pass (minus deleted tests, plus any new tests added)
- [ ] No new warnings introduced

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Full test suite passes
- [ ] Final grep verification clean
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to `Complete`
- [ ] Update plan.md Verification checklist
