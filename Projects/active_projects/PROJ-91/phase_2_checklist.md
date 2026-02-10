# Phase 2: Migrate Callers to Generic API

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-91 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Update all production code callers (Fleet, ResupplyEngine) and test mock helpers to use generic resource methods instead of type-specific ones. Remove Fleet's type-specific wrappers.

---

## Tasks

### Task 2.1: Migrate Fleet Fuel-Specific Movement Methods [Medium]
**File:** `game/strategy/data/fleet.py`
**Tests:** `pytest tests/unit/strategy/fleet/ tests/integration/strategy/`

The following Fleet methods call ShipInstance type-specific methods and need to be refactored. Since generic equivalents (`get_movement_resource_costs`, `has_resources_for_movement`, `consume_movement_resources`) already exist, the type-specific versions can be removed and callers redirected.

- [ ] **Remove `get_fuel_cost_per_hex()`** (lines 236-246) — this is a fuel-only duplicate of `get_movement_resource_costs().get('fuel', 0)`. Remove the method entirely.
- [ ] **Remove `has_fuel_for_movement()`** (lines 248-261) — this is a fuel-only duplicate of `has_resources_for_movement()`. Remove the method entirely.
- [ ] **Remove `consume_fleet_fuel()`** (lines 263-290) — this is a fuel-only duplicate of `consume_movement_resources()`. Remove the method entirely.
- [ ] Update `get_capability_summary()` (line 519) — replace `'fuel_cost_per_hex': self.get_fuel_cost_per_hex()` with `'movement_resource_costs': self.get_movement_resource_costs()`
- [ ] Search for callers of the removed Fleet methods and update them
- [ ] Verify: `pytest tests/ --testmon` passes

**Notes:**

### Task 2.2: Migrate Fleet Warp-Specific Methods [Medium]
**File:** `game/strategy/data/fleet.py`
**Tests:** `pytest tests/unit/strategy/fleet/ tests/integration/strategy/`

- [ ] **Remove `get_warp_energy_cost()`** (lines 376-386) — callers should use `get_warp_resource_costs().get('energy', 0)` instead. Remove the method.
- [ ] **Remove `get_warp_fuel_cost()`** (lines 388-398) — callers should use `get_warp_resource_costs().get('fuel', 0)` instead. Remove the method.
- [ ] **Refactor `fuel_endurance()`** (lines 451-470) — change to use generic resource methods:
  ```python
  cost_per_hex = ship.get_all_resource_costs_per_hex().get('fuel', 0)
  current_fuel = ship.get_current_resource('fuel')
  ```
- [ ] **Refactor `warp_jumps_remaining()`** (lines 472-504) — change to use generic resource methods:
  ```python
  warp_costs = ship.get_warp_resource_costs()
  for resource_type, cost in warp_costs.items():
      if cost > 0:
          current = ship.get_current_resource(resource_type)
          jumps = int(current / cost)
          min_jumps = min(min_jumps, jumps)
  ```
- [ ] Update `get_capability_summary()` (lines 520-521) — replace `'warp_energy_cost': self.get_warp_energy_cost()` and `'warp_fuel_cost': self.get_warp_fuel_cost()` with `'warp_resource_costs': self.get_warp_resource_costs()`
- [ ] Verify: `pytest tests/ --testmon` passes

**Notes:**

### Task 2.3: Migrate ResupplyEngine [Medium]
**File:** `game/strategy/engine/resupply_engine.py`
**Tests:** `pytest tests/unit/strategy/engine/test_resupply_engine.py tests/integration/strategy/test_resupply_system.py`

- [ ] Update `_calculate_fuel_distribution()` (lines 211-247):
  - Line 231: `s.get_fuel_cost_per_hex()` → `s.get_all_resource_costs_per_hex().get('fuel', 0)`
  - Line 235: `s.get_current_fuel()` → `s.get_current_resource('fuel')`
  - Line 240: `ship.get_fuel_cost_per_hex()` → `ship.get_all_resource_costs_per_hex().get('fuel', 0)`
  - Line 243: `ship.get_current_fuel()` → `ship.get_current_resource('fuel')`
- [ ] Verify: `pytest tests/ --testmon` passes

**Notes:**

### Task 2.4: Update Test Mock Helper in test_resupply_engine.py [Medium]
**File:** `tests/unit/strategy/engine/test_resupply_engine.py`
**Tests:** `pytest tests/unit/strategy/engine/test_resupply_engine.py`

- [ ] Update `_make_mock_ship()` helper (lines 305-330):
  - Replace `ship.get_current_fuel.return_value` with `ship.get_current_resource.side_effect` that returns fuel for `'fuel'` arg
  - Replace `ship.get_fuel_cost_per_hex.return_value` with `ship.get_all_resource_costs_per_hex.return_value = {'fuel': fuel_cost_per_hex}`
  - Update internal fuel state tracking to use `get_current_resource` calls
- [ ] Run all tests in file: `pytest tests/unit/strategy/engine/test_resupply_engine.py -v`
- [ ] Verify: all 9 TestFleetResupply tests pass

**Notes:**

### Task 2.5: Update Test Mock Helper in test_resupply_system.py [Medium]
**File:** `tests/integration/strategy/test_resupply_system.py`
**Tests:** `pytest tests/integration/strategy/test_resupply_system.py`

- [ ] Update `_make_mock_ship()` helper (lines 113-141):
  - Replace `ship.get_current_fuel.side_effect` with `ship.get_current_resource.side_effect`
  - Replace `ship.get_fuel_cost_per_hex.return_value` with `ship.get_all_resource_costs_per_hex.return_value`
- [ ] Update assertions at lines 288, 290, 332, 334:
  - `ship_a.get_current_fuel()` → `ship_a.get_current_resource('fuel')`
  - `ship_b.get_current_fuel()` → `ship_b.get_current_resource('fuel')`
- [ ] Run all tests in file: `pytest tests/integration/strategy/test_resupply_system.py -v`

**Notes:**

### Task 2.6: Update Test Mock Helper in test_resupply.py [Medium]
**File:** `tests/integration/strategy/turn_engine/test_resupply.py`
**Tests:** `pytest tests/integration/strategy/turn_engine/test_resupply.py`

- [ ] Update `_make_mock_ship()` helper (lines 99-128):
  - Replace `ship.get_current_fuel.side_effect` with `ship.get_current_resource.side_effect`
  - Replace `ship.get_fuel_cost_per_hex.return_value` with `ship.get_all_resource_costs_per_hex.return_value`
- [ ] Run all tests in file: `pytest tests/integration/strategy/turn_engine/test_resupply.py -v`

**Notes:**

### Task 2.7: Update Fleet Test Mocks [Medium]
**File:** `tests/unit/strategy/fleet/test_warp_resources.py`
**Tests:** `pytest tests/unit/strategy/fleet/test_warp_resources.py`

- [ ] Remove `TestBackwardCompatibility` class (tests `consume_fleet_fuel` wrapper which is being removed)
- [ ] Search for any mocks of removed Fleet methods (`get_fuel_cost_per_hex`, `get_warp_energy_cost`, `get_warp_fuel_cost`, `consume_fleet_fuel`, `has_fuel_for_movement`) in other test files and update them
- [ ] Verify: `pytest tests/unit/strategy/fleet/ -v` passes

**Notes:**

### Task 2.8: Search for Any Remaining Callers [Simple]
**Tests:** `pytest tests/ --testmon`

- [ ] Grep for all removed method names to ensure no callers remain:
  ```
  get_current_fuel, consume_fuel, get_current_energy, consume_energy,
  get_fuel_cost_per_hex, get_warp_fuel_cost, get_warp_energy_cost,
  has_fuel_for_movement, consume_fleet_fuel
  ```
- [ ] Fix any remaining call sites found
- [ ] Verify: `pytest tests/ --testmon` passes

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Run full test suite: `pytest tests/ -n 12` — all 7353+ tests pass
- [ ] Grep confirms no remaining calls to type-specific methods
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 3
