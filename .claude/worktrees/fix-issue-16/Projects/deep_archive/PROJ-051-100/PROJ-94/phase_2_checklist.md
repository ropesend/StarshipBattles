# Phase 2: Delete Dead Type-Specific Methods

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-94 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Remove all remaining type-specific resource methods that PROJ-91 left behind in extracted managers.

---

## Tasks

### Task 2.1: Delete ShipResourceManager type-specific methods [Simple]
**File:** `game/strategy/data/ship_resource_manager.py`
**Tests:** `pytest tests/unit/strategy/test_ship_resource_manager.py -v`

- [x] Delete lines 40-136 (entire "Fuel Methods" and "Energy Methods" sections):
  - `get_fuel_cost_per_hex()` (lines 42-50)
  - `get_current_fuel()` (lines 52-61)
  - `consume_fuel()` (lines 63-82)
  - `get_warp_fuel_cost()` (lines 84-92)
  - `get_warp_energy_cost()` (lines 96-104)
  - `get_current_energy()` (lines 106-115)
  - `consume_energy()` (lines 117-136)
- [x] Keep "Generic Resource Methods" section (lines 138+) intact
- [x] Verify file compiles: `python -c "from game.strategy.data.ship_resource_manager import ShipResourceManager"`

**Notes:** Deleted 97 lines (lines 40-136)

---

### Task 2.2: Delete test methods for removed ShipResourceManager methods [Simple]
**File:** `tests/unit/strategy/test_ship_resource_manager.py`
**Tests:** `pytest tests/unit/strategy/test_ship_resource_manager.py -v`

- [x] Delete all test methods that call type-specific methods:
  - `test_get_current_fuel_full`
  - `test_get_current_fuel_partial`
  - `test_consume_fuel_success`
  - `test_consume_fuel_insufficient`
  - `test_consume_fuel_from_full`
  - `test_get_fuel_cost_per_hex`
  - `test_get_warp_fuel_cost`
  - `test_get_current_energy_full`
  - `test_get_current_energy_partial`
  - `test_consume_energy_success`
  - `test_consume_energy_insufficient`
  - `test_get_warp_energy_cost`
- [x] Keep all generic method tests intact
- [x] Run: `pytest tests/unit/strategy/test_ship_resource_manager.py -v`

**Notes:** Deleted 12 test methods

---

### Task 2.3: Delete FleetResourceAggregator type-specific methods [Simple]
**File:** `game/strategy/data/fleet_resource_aggregator.py`
**Tests:** `pytest tests/unit/strategy/test_fleet_resource_aggregator.py -v`

- [x] Delete `get_fuel_cost_per_hex()` (lines 32-39)
- [x] Delete `has_fuel_for_movement()` (lines 41-49)
- [x] Delete `consume_fleet_fuel()` (lines 51-63)
- [x] Delete `get_warp_energy_cost()` (lines 149-156)
- [x] Delete `get_warp_fuel_cost()` (lines 158-165)
- [x] Delete the "Fuel Consumption Methods" section header comment (lines 30-31)
- [x] Verify file compiles: `python -c "from game.strategy.data.fleet_resource_aggregator import FleetResourceAggregator"`

**Notes:** Deleted 5 methods (50 lines)

---

### Task 2.4: Delete Fleet facade type-specific methods [Simple]
**File:** `game/strategy/data/fleet.py`
**Tests:** `pytest tests/unit/strategy/fleet/ -v`

- [x] Delete `get_fuel_cost_per_hex()` (lines 172-174)
- [x] Delete `has_fuel_for_movement()` (lines 176-178)
- [x] Delete `consume_fleet_fuel()` (lines 180-182)
- [x] Delete `get_warp_energy_cost()` (lines 204-206)
- [x] Delete `get_warp_fuel_cost()` (lines 208-210)
- [x] Delete the "Fuel Consumption Methods" section header comment (lines 170-171)
- [x] Verify file compiles: `python -c "from game.strategy.data.fleet import Fleet"`

**Notes:** Deleted 5 facade methods (20 lines)

---

### Task 2.5: Delete test methods for removed Fleet/Aggregator methods [Simple]
**Files:** `tests/unit/strategy/test_fleet_resource_aggregator.py`, `tests/unit/strategy/fleet/test_warp_resources.py`

- [x] In `test_fleet_resource_aggregator.py`, delete:
  - `test_get_fuel_cost_per_hex_aggregates_all_ships`
  - `test_get_fuel_cost_per_hex_empty_fleet`
  - `test_has_fuel_for_movement_all_ships_have_fuel`
  - `test_has_fuel_for_movement_one_ship_empty`
  - `test_consume_fleet_fuel_success`
  - `test_consume_fleet_fuel_atomic_on_failure`
  - `test_get_warp_energy_cost_sums`
  - `test_get_warp_fuel_cost_sums`
- [x] In `test_warp_resources.py`, delete test class `TestFleetFuelConsumption` (or update if it tests generic methods)
- [x] Run: `pytest tests/unit/strategy/test_fleet_resource_aggregator.py tests/unit/strategy/fleet/test_warp_resources.py -v`

**Notes:** Deleted 8 tests + 1 test class (TestFleetFuelConsumption with 1 test) = 9 deleted tests

---

### Task 2.6: Verify no remaining production callers [Simple]
- [x] Grep: `get_current_fuel|consume_fuel|get_current_energy|consume_energy` in `game/` -- expect 0 matches
- [x] Grep: `has_fuel_for_movement|consume_fleet_fuel` in `game/` -- expect 0 matches
- [x] Grep: `get_fuel_cost_per_hex|get_warp_fuel_cost|get_warp_energy_cost` in `game/` -- expect 0 matches (only in deleted code)
- [x] Run full test suite: `pytest tests/ -n 12`

**Notes:** All greps return 0 matches. Full suite: 7595 passed (21 tests deleted)

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
