# Phase 3: Enhance Execution Layer

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-55 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Change colonization to remove individual ship instead of entire fleet

---

## Tasks

### Task 3.1: Add Fleet.remove_ship() Method [Simple]
**File:** `game/strategy/data/fleet.py`
**Tests:** Unit test in test_fleet.py

- [ ] Open `game/strategy/data/fleet.py`
- [ ] Find Fleet class (around line 20-100)
- [ ] Add method:
  ```python
  def remove_ship(self, ship):
      """Remove a specific ship from the fleet.

      Args:
          ship: Ship to remove
      """
      if ship in self.ships:
          self.ships.remove(ship)
  ```
- [ ] Verify: Method added, no syntax errors

**Notes:**

---

### Task 3.2: Modify process_colonize() for Individual Ship Removal [Medium]
**File:** `game/strategy/engine/fleet_order_processor.py`
**Tests:** `pytest tests/integration/strategy/test_colonize_logic.py -v`

- [ ] Find `process_colonize(self, fleet, empire, galaxy)` method (around line 100-150)
- [ ] After re-validation block, add code to find colony ship:
  ```python
  # Find ship with matching colony pod
  planet_type_str = target_planet.planet_type.name
  from game.strategy.validation.colonize_validator import ColonizeValidator
  colony_ship = ColonizeValidator.find_ship_with_colony_pod(fleet, planet_type_str)

  if colony_ship is None:
      # Validation should have caught this, but safety check
      fleet.pop_order()
      return ColonizeResult(colonized=False, planet_name="")
  ```
- [ ] Modify fleet consumption code:
  - OLD: `empire.remove_fleet(fleet)` (removes entire fleet)
  - NEW:
    ```python
    # Remove only the colony ship
    fleet.remove_ship(colony_ship)

    # If fleet now empty, remove fleet
    if len(fleet.ships) == 0:
        empire.remove_fleet(fleet)
    ```
- [ ] Verify: Logic flows correctly, handles empty fleet case

**Notes:** Current behavior removes entire fleet - this is the key behavior change

---

### Task 3.3: Update Execution Tests [Medium]
**File:** `tests/integration/strategy/test_colonize_logic.py`
**Tests:** `pytest tests/integration/strategy/test_colonize_logic.py -v`

- [ ] Update existing tests that create fleets:
  - Add colony pod components to ships in test fleets
  - Update assertions from "fleet removed" to "colony ship removed"
- [ ] Add test: `test_colonize_removes_only_colony_ship_not_fleet()`
  - Create fleet with 2 ships: one with colony pod, one without
  - Execute colonization
  - Assert: Colony ship removed from fleet
  - Assert: Other ship still in fleet
  - Assert: Fleet still exists in empire
- [ ] Add test: `test_colonize_removes_fleet_if_last_ship()`
  - Create fleet with 1 ship (has colony pod)
  - Execute colonization
  - Assert: Ship removed
  - Assert: Fleet removed from empire
- [ ] Add test: `test_colonize_with_multiple_pod_types_in_fleet()`
  - Create fleet with 2 ships: Ice Dwarf pod + Continental pod
  - Colonize Ice Dwarf planet
  - Assert: Ice Dwarf pod ship removed
  - Assert: Continental pod ship remains
- [ ] Run tests: `pytest tests/integration/strategy/test_colonize_logic.py -v`
- [ ] Verify: All tests pass

**Notes:** Many existing tests will need colony pod added to ships

---

### Task 3.4: Update Fleet Order Processor Tests [Simple]
**File:** `tests/unit/strategy/test_fleet_order_processor.py`
**Tests:** `pytest tests/unit/strategy/test_fleet_order_processor.py -v`

- [ ] Review tests for `process_colonize()`
- [ ] Update tests to include colony pods on ships
- [ ] Update assertions for new behavior (ship removal vs fleet removal)
- [ ] Run tests: `pytest tests/unit/strategy/test_fleet_order_processor.py -k colonize -v`
- [ ] Verify: All colonize tests pass

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Run `pytest tests/integration/strategy/ -v` - all tests pass
- [ ] Run `pytest tests/unit/strategy/test_fleet_order_processor.py -v` - all tests pass
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 4
