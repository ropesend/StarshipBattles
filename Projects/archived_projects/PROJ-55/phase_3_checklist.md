# Phase 3: Enhance Execution Layer

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-55 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Change colonization to remove individual ship instead of entire fleet

---

## Tasks

### Task 3.1: Add Fleet.remove_ship() Method [Simple]
**File:** `game/strategy/data/fleet.py`
**Tests:** Unit test in test_fleet.py

- [x] Open `game/strategy/data/fleet.py`
- [x] Find Fleet class (around line 20-100)
- [x] Add method: **ALREADY EXISTS** at line 74
- [x] Verify: Method added, no syntax errors

**Notes:** Method already existed in the codebase with same signature and behavior. No changes needed.

---

### Task 3.2: Modify process_colonize() for Individual Ship Removal [Medium]
**File:** `game/strategy/engine/fleet_order_processor.py`
**Tests:** `pytest tests/integration/strategy/test_colonize_logic.py -v`

- [x] Find `process_colonize(self, fleet, empire, galaxy)` method (around line 152)
- [x] Add optional `component_registry` parameter for backward compatibility
- [x] After re-validation block, add code to find colony ship using `ColonizeValidator.find_ship_with_colony_pod()`
- [x] Modify fleet consumption code:
  - When registry is provided: Remove only colony ship, remove fleet only if empty
  - When registry is None: Legacy behavior (remove entire fleet)
- [x] Verify: Logic flows correctly, handles empty fleet case

**Notes:** Implementation uses optional `component_registry` parameter. When None, old behavior is preserved for backward compatibility. When provided, uses `ColonizeValidator.find_ship_with_colony_pod()` to find and remove only the colony ship.

---

### Task 3.3: Update Execution Tests [Medium]
**File:** `tests/integration/strategy/test_colonize_logic.py`
**Tests:** `pytest tests/integration/strategy/test_colonize_logic.py -v`

- [x] Added MockShip class with design_data and get_calculated_stats()
- [x] Added mock_component_registry fixture with colony pod definitions
- [x] Added galaxy_with_typed_planets fixture for ICE_DWARF/CONTINENTAL
- [x] Add test: `test_colonize_removes_only_colony_ship_not_fleet()` - PASSING
- [x] Add test: `test_colonize_removes_fleet_if_last_ship()` - PASSING
- [x] Add test: `test_colonize_with_multiple_pod_types_removes_correct_ship()` - PASSING
- [x] Add test: `test_colonize_backward_compatible_without_registry()` - PASSING
- [x] Run tests: `pytest tests/integration/strategy/test_colonize_logic.py -v` - 9 passed
- [x] Verify: All tests pass

**Notes:** Added TestColonizePodShipRemoval class with 4 new integration tests. All existing tests continue to pass (backward compatible).

---

### Task 3.4: Update Fleet Order Processor Tests [Simple]
**File:** `tests/unit/strategy/test_fleet_order_processor.py`
**Tests:** `pytest tests/unit/strategy/test_fleet_order_processor.py -v`

- [x] Added TestColonizeShipRemoval class with 4 new unit tests
- [x] Added fixtures: mock_ship_with_pod, mock_ship_combat, mock_component_registry, mock_planet_ice_dwarf
- [x] Test: `test_process_colonize_with_registry_removes_ship` - PASSING
- [x] Test: `test_process_colonize_with_registry_removes_fleet_when_empty` - PASSING
- [x] Test: `test_process_colonize_with_registry_keeps_fleet_when_ships_remain` - PASSING
- [x] Test: `test_process_colonize_without_registry_removes_fleet` - PASSING
- [x] Run tests: `pytest tests/unit/strategy/test_fleet_order_processor.py -v` - 30 passed
- [x] Verify: All colonize tests pass

**Notes:** Added 4 new unit tests for the new colony ship removal behavior.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Run `pytest tests/integration/strategy/ -v` - all tests pass (1306 passed)
- [x] Run `pytest tests/unit/strategy/test_fleet_order_processor.py -v` - all tests pass (30 passed)
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 4
