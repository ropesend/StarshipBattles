# Phase 2: Delete Dead Type-Specific Methods

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-94 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Remove all remaining type-specific resource methods that PROJ-91 left behind in extracted managers.

---

## Tasks

### Task 2.1: Delete ShipResourceManager type-specific methods [Simple]
**File:** `game/strategy/data/ship_resource_manager.py`
**Tests:** `pytest tests/unit/strategy/test_ship_resource_manager.py -v`

- [ ] Delete lines 40-136 (entire "Fuel Methods" and "Energy Methods" sections):
  - `get_fuel_cost_per_hex()` (lines 42-50)
  - `get_current_fuel()` (lines 52-61)
  - `consume_fuel()` (lines 63-82)
  - `get_warp_fuel_cost()` (lines 84-92)
  - `get_warp_energy_cost()` (lines 96-104)
  - `get_current_energy()` (lines 106-115)
  - `consume_energy()` (lines 117-136)
- [ ] Keep "Generic Resource Methods" section (lines 138+) intact
- [ ] Verify file compiles: `python -c "from game.strategy.data.ship_resource_manager import ShipResourceManager"`

**Notes:**

---

### Task 2.2: Delete test methods for removed ShipResourceManager methods [Simple]
**File:** `tests/unit/strategy/test_ship_resource_manager.py`
**Tests:** `pytest tests/unit/strategy/test_ship_resource_manager.py -v`

- [ ] Delete all test methods that call type-specific methods:
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
- [ ] Keep all generic method tests intact
- [ ] Run: `pytest tests/unit/strategy/test_ship_resource_manager.py -v`

**Notes:**

---

### Task 2.3: Delete FleetResourceAggregator type-specific methods [Simple]
**File:** `game/strategy/data/fleet_resource_aggregator.py`
**Tests:** `pytest tests/unit/strategy/test_fleet_resource_aggregator.py -v`

- [ ] Delete `get_fuel_cost_per_hex()` (lines 32-39)
- [ ] Delete `has_fuel_for_movement()` (lines 41-49)
- [ ] Delete `consume_fleet_fuel()` (lines 51-63)
- [ ] Delete `get_warp_energy_cost()` (lines 149-156)
- [ ] Delete `get_warp_fuel_cost()` (lines 158-165)
- [ ] Delete the "Fuel Consumption Methods" section header comment (lines 30-31)
- [ ] Verify file compiles: `python -c "from game.strategy.data.fleet_resource_aggregator import FleetResourceAggregator"`

**Notes:**

---

### Task 2.4: Delete Fleet facade type-specific methods [Simple]
**File:** `game/strategy/data/fleet.py`
**Tests:** `pytest tests/unit/strategy/fleet/ -v`

- [ ] Delete `get_fuel_cost_per_hex()` (lines 172-174)
- [ ] Delete `has_fuel_for_movement()` (lines 176-178)
- [ ] Delete `consume_fleet_fuel()` (lines 180-182)
- [ ] Delete `get_warp_energy_cost()` (lines 204-206)
- [ ] Delete `get_warp_fuel_cost()` (lines 208-210)
- [ ] Delete the "Fuel Consumption Methods" section header comment (lines 170-171)
- [ ] Verify file compiles: `python -c "from game.strategy.data.fleet import Fleet"`

**Notes:**

---

### Task 2.5: Delete test methods for removed Fleet/Aggregator methods [Simple]
**Files:** `tests/unit/strategy/test_fleet_resource_aggregator.py`, `tests/unit/strategy/fleet/test_warp_resources.py`

- [ ] In `test_fleet_resource_aggregator.py`, delete:
  - `test_get_fuel_cost_per_hex_aggregates_all_ships`
  - `test_get_fuel_cost_per_hex_empty_fleet`
  - `test_has_fuel_for_movement_all_ships_have_fuel`
  - `test_has_fuel_for_movement_one_ship_empty`
  - `test_consume_fleet_fuel_success`
  - `test_consume_fleet_fuel_atomic_on_failure`
  - `test_get_warp_energy_cost_sums`
  - `test_get_warp_fuel_cost_sums`
- [ ] In `test_warp_resources.py`, delete test class `TestFleetFuelConsumption` (or update if it tests generic methods)
- [ ] Run: `pytest tests/unit/strategy/test_fleet_resource_aggregator.py tests/unit/strategy/fleet/test_warp_resources.py -v`

**Notes:**

---

### Task 2.6: Verify no remaining production callers [Simple]
- [ ] Grep: `get_current_fuel|consume_fuel|get_current_energy|consume_energy` in `game/` -- expect 0 matches
- [ ] Grep: `has_fuel_for_movement|consume_fleet_fuel` in `game/` -- expect 0 matches
- [ ] Grep: `get_fuel_cost_per_hex|get_warp_fuel_cost|get_warp_energy_cost` in `game/` -- expect 0 matches (only in deleted code)
- [ ] Run full test suite: `pytest tests/ -n 12`

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
