# Phase 2: Migrate Callers to Generic API

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-91 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Update all production code callers (Fleet, ResupplyEngine) and test mock helpers to use generic resource methods instead of type-specific ones. Remove Fleet's type-specific wrappers.

---

## Tasks

### Task 2.1: Migrate Fleet Fuel-Specific Movement Methods [Medium]
**File:** `game/strategy/data/fleet.py`
**Tests:** `pytest tests/unit/strategy/fleet/ tests/integration/strategy/`

The following Fleet methods call ShipInstance type-specific methods and need to be refactored. Since generic equivalents (`get_movement_resource_costs`, `has_resources_for_movement`, `consume_movement_resources`) already exist, the type-specific versions can be removed and callers redirected.

- [x] **Refactor `get_fuel_cost_per_hex()`** — now delegates to `get_movement_resource_costs().get('fuel', 0.0)`
- [x] **Refactor `has_fuel_for_movement()`** — now delegates to `has_resources_for_movement()`
- [x] **Refactor `consume_fleet_fuel()`** — now delegates to `consume_movement_resources(hexes)`
- [x] Update `get_capability_summary()` — now returns `'movement_resource_costs'` and `'warp_resource_costs'` instead of type-specific costs
- [x] Search for callers of the removed Fleet methods and update them
- [x] Verify: `pytest tests/ --testmon` passes

**Notes:** Refactored FleetResourceAggregator to delegate type-specific methods to generic methods instead of removing them outright. This keeps Fleet API stable while using generic ShipInstance methods internally.

### Task 2.2: Migrate Fleet Warp-Specific Methods [Medium]
**File:** `game/strategy/data/fleet.py`
**Tests:** `pytest tests/unit/strategy/fleet/ tests/integration/strategy/`

- [x] **Refactor `get_warp_energy_cost()`** — now delegates to `get_warp_resource_costs().get('energy', 0.0)`
- [x] **Refactor `get_warp_fuel_cost()`** — now delegates to `get_warp_resource_costs().get('fuel', 0.0)`
- [x] **Refactor `fuel_endurance()`** — now uses `ship.get_all_resource_costs_per_hex().get('fuel', 0.0)` and `ship.get_current_resource('fuel')`
- [x] **Refactor `warp_jumps_remaining()`** — now uses generic `ship.get_warp_resource_costs()` and `ship.get_current_resource(resource_type)` loop
- [x] Update `get_capability_summary()` — now returns `'movement_resource_costs'` and `'warp_resource_costs'`
- [x] Verify: `pytest tests/ --testmon` passes

**Notes:** All methods in FleetResourceAggregator now use ShipInstance's generic resource methods instead of type-specific ones.

### Task 2.3: Migrate ResupplyEngine [Medium]
**File:** `game/strategy/engine/resupply_engine.py`
**Tests:** `pytest tests/unit/strategy/engine/test_resupply_engine.py tests/integration/strategy/test_resupply_system.py`

- [x] Update `_calculate_fuel_distribution()`:
  - `s.get_fuel_cost_per_hex()` → `s.get_all_resource_costs_per_hex().get('fuel', 0)`
  - `s.get_current_fuel()` → `s.get_current_resource('fuel')`
  - `ship.get_fuel_cost_per_hex()` → `ship.get_all_resource_costs_per_hex().get('fuel', 0)`
  - `ship.get_current_fuel()` → `ship.get_current_resource('fuel')`
- [x] Verify: `pytest tests/ --testmon` passes

**Notes:** ResupplyEngine._calculate_fuel_distribution() now uses generic resource API.

### Task 2.4: Update Test Mock Helper in test_resupply_engine.py [Medium]
**File:** `tests/unit/strategy/engine/test_resupply_engine.py`
**Tests:** `pytest tests/unit/strategy/engine/test_resupply_engine.py`

- [x] Update `_make_mock_ship()` helper:
  - Replaced `ship.get_current_fuel.return_value` with `ship.get_current_resource.side_effect`
  - Replaced `ship.get_fuel_cost_per_hex.return_value` with `ship.get_all_resource_costs_per_hex.return_value`
- [x] Run all tests in file: `pytest tests/unit/strategy/engine/test_resupply_engine.py -v`
- [x] Verify: all 6 TestFleetResupply tests pass

**Notes:**

### Task 2.5: Update Test Mock Helper in test_resupply_system.py [Medium]
**File:** `tests/integration/strategy/test_resupply_system.py`
**Tests:** `pytest tests/integration/strategy/test_resupply_system.py`

- [x] Update `_make_mock_ship()` helper:
  - Replaced `ship.get_current_fuel.side_effect` with `ship.get_current_resource.side_effect`
  - Replaced `ship.get_fuel_cost_per_hex.return_value` with `ship.get_all_resource_costs_per_hex.return_value`
- [x] Update assertions:
  - `ship_a.get_current_fuel()` → `ship_a.get_current_resource('fuel')`
  - `ship_b.get_current_fuel()` → `ship_b.get_current_resource('fuel')`
- [x] Run all tests in file: `pytest tests/integration/strategy/test_resupply_system.py -v`

**Notes:**

### Task 2.6: Update Test Mock Helper in test_resupply.py [Medium]
**File:** `tests/integration/strategy/turn_engine/test_resupply.py`
**Tests:** `pytest tests/integration/strategy/turn_engine/test_resupply.py`

- [x] Update `_make_mock_ship()` helper:
  - Replaced `ship.get_current_fuel.side_effect` with `ship.get_current_resource.side_effect`
  - Replaced `ship.get_fuel_cost_per_hex.return_value` with `ship.get_all_resource_costs_per_hex.return_value`
- [x] Run all tests in file: `pytest tests/integration/strategy/turn_engine/test_resupply.py -v`

**Notes:**

### Task 2.7: Update Fleet Test Mocks [Medium]
**File:** `tests/unit/strategy/fleet/test_warp_resources.py`
**Tests:** `pytest tests/unit/strategy/fleet/test_warp_resources.py`

- [x] Renamed `TestBackwardCompatibility` to `TestFleetFuelConsumption` - tests now verify consume_fleet_fuel delegates to generic methods
- [x] Updated mocks to use generic methods (`get_all_resource_costs_per_hex`, `consume_resource`)
- [x] Verify: `pytest tests/unit/strategy/fleet/ -v` passes

**Notes:**

### Task 2.8: Search for Any Remaining Callers [Simple]
**Tests:** `pytest tests/ --testmon`

- [x] Grep confirmed no production callers of type-specific methods remain in game/ folder (only method definitions in ship_instance.py and Fleet delegation wrappers)
- [x] Verify: `pytest tests/ -n 12` passes — 7561 tests pass

**Notes:** Type-specific methods remain defined on ShipInstance and Fleet but are no longer called by production code. They will be removed in Phase 3.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Run full test suite: `pytest tests/ -n 12` — 7561 tests pass
- [x] Grep confirms no remaining calls to type-specific methods in production code
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 3
