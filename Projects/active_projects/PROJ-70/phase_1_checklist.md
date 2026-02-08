# Phase 1: Write Tests (TDD)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-70 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Write unit tests for the enhanced `format_fleet_info()` function before implementing it. Tests should fail initially.

---

## Tasks

### Task 1.1: Add Mock Helper Function [Simple]
**File:** `tests/unit/ui/screens/test_fleet_detail_fmt.py`
**Tests:** `pytest tests/unit/ui/screens/test_fleet_detail_fmt.py`

- [x] Add `_make_mock_ship(design_id, design_name, mass, cargo=None)` helper that creates a MagicMock with:
  - `ship.design_id = design_id`
  - `ship.design_data = {'name': design_name}`
  - `ship.get_calculated_stats.return_value = {'mass': mass}`
  - `ship.cargo_contents = cargo or {}`
- [x] Add `_make_mock_fleet(fleet_id=1, owner_id=0, ships=None, orders=None, speed=5.0, fuel_endurance=20)` helper that creates a MagicMock with:
  - `fleet.id = fleet_id`, `fleet.owner_id = owner_id`
  - `fleet.ships = ships or []`
  - `fleet.orders = orders or []`
  - `fleet.speed = speed`
  - `fleet.fuel_endurance.return_value = fuel_endurance`
  - `fleet.location = MagicMock(__str__=lambda self: "(0, 0)")`
  - `fleet.construction_queue = []`

**Notes:** Both helpers created. Existing TRANSFER tests refactored to use `_make_mock_fleet`.

### Task 1.2: Write Travel Range Tests [Simple]
**File:** `tests/unit/ui/screens/test_fleet_detail_fmt.py`
**Tests:** `pytest tests/unit/ui/screens/test_fleet_detail_fmt.py`

- [x] `test_format_fleet_info_travel_range` - fleet.speed=5.0, fuel_endurance()=20 → assert "5 hex/turn" and "20 hex fuel" in output
- [x] `test_format_fleet_info_unlimited_fuel` - fuel_endurance()=-1 → assert "unlimited fuel" in output
- [x] `test_format_fleet_info_zero_speed` - speed=0.0 → assert "0 hex/turn" in output (empty fleet case)

**Notes:** All 3 tests fail as expected (TDD).

### Task 1.3: Write Ship Grouping Tests [Simple]
**File:** `tests/unit/ui/screens/test_fleet_detail_fmt.py`
**Tests:** `pytest tests/unit/ui/screens/test_fleet_detail_fmt.py`

- [x] `test_format_fleet_info_ship_grouping` - 2 ships with design_id="Destroyer" + 1 with design_id="Scout" → assert "Destroyer x 2" and "Scout" and "Ships (3):" in output
- [x] `test_format_fleet_info_sorted_by_mass` - Destroyer (mass=5000) + Scout (mass=1000) → assert "Destroyer" appears before "Scout" in output
- [x] `test_format_fleet_info_single_ship_no_multiplier` - 1 ship → assert name appears without "x 1"
- [x] `test_format_fleet_info_empty_fleet` - no ships → assert "Ships: None" in output, no crash

**Notes:** All 4 tests fail as expected (TDD).

### Task 1.4: Write Cargo Summary Tests [Simple]
**File:** `tests/unit/ui/screens/test_fleet_detail_fmt.py`
**Tests:** `pytest tests/unit/ui/screens/test_fleet_detail_fmt.py`

- [x] `test_format_fleet_info_cargo_summary` - ships with passengers=50 and passengers=30+minerals=10 → assert "Passengers: 80" and "Minerals: 10" in output
- [x] `test_format_fleet_info_no_cargo` - all ships have empty cargo_contents → assert "Cargo:" does NOT appear

**Notes:** `test_cargo_summary` fails (TDD). `test_no_cargo` passes because current function doesn't emit "Cargo:" at all.

### Task 1.5: Write Order Formatting Tests [Simple]
**File:** `tests/unit/ui/screens/test_fleet_detail_fmt.py`
**Tests:** `pytest tests/unit/ui/screens/test_fleet_detail_fmt.py`

- [x] `test_format_fleet_info_move_order` - MOVE order with target hex → assert "MOVE" and target in output
- [x] `test_format_fleet_info_build_order` - BUILD order + fleet.construction_queue with 2 items → assert "BUILDING (2 items)" in output
- [x] `test_format_fleet_info_no_orders` - empty orders list → assert "(No Orders)" in output
- [x] Verify existing TRANSFER tests still pass (don't break them)

**Notes:** `test_move_order` and `test_no_orders` pass (current behavior). `test_build_order` fails (BUILD not handled yet). TRANSFER tests pass.

### Task 1.6: Verify Tests Fail Appropriately [Simple]
**Tests:** `pytest tests/unit/ui/screens/test_fleet_detail_fmt.py`

- [x] Run all new tests - new tests should fail because `format_fleet_info()` doesn't yet have the new sections
- [x] Existing 2 TRANSFER tests should still pass (they test current behavior)

**Notes:** 9 new tests fail, 5 tests pass (2 existing TRANSFER + 3 that match current behavior). TDD setup complete.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
