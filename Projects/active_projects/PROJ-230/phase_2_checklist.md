# Phase 2: Extract Filter Helpers

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-230 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Extract 5 filter predicate helper functions from filter_ships

---

## Tasks

### Task 2.1: Extract `_passes_warp_filter` [Simple]
**File:** `game/ui/screens/fleet_report_filters.py`
**Tests:** `pytest tests/unit/ui/screens/test_fleet_report_filters.py::TestFilterShipsWarp -v`

Extract lines 144-153 into a helper function.

- [ ] Add helper function above `filter_ships`:
  ```python
  def _passes_warp_filter(ship: ShipInstance, filter_state: Dict[str, bool]) -> bool:
      """Check if ship passes warp capability filter."""
      show_warp = filter_state.get('show_warp_capable', True)
      show_not_warp = filter_state.get('show_not_warp_capable', True)

      if show_warp and show_not_warp:
          return True

      is_warp_capable = ShipStatsCalculator.has_warp_capability(ship)
      if is_warp_capable and not show_warp:
          return False
      if not is_warp_capable and not show_not_warp:
          return False
      return True
  ```
- [ ] Run warp tests: verify passing
- [ ] Do NOT modify `filter_ships` yet - just add the helper

**Notes:** Helper function CC should be ~4

---

### Task 2.2: Extract `_passes_spaceyard_filter` [Simple]
**File:** `game/ui/screens/fleet_report_filters.py`
**Tests:** `pytest tests/unit/ui/screens/test_fleet_report_filters.py::TestFilterShipsSpaceyard -v`

Extract lines 156-164 into a helper function.

- [ ] Add helper function (preserve late import inside function):
  ```python
  def _passes_spaceyard_filter(ship: ShipInstance, filter_state: Dict[str, bool]) -> bool:
      """Check if ship passes spaceyard capability filter."""
      show_has_yard = filter_state.get('show_has_spaceyard', True)
      show_no_yard = filter_state.get('show_no_spaceyard', True)

      if show_has_yard and show_no_yard:
          return True

      from game.strategy.data.fleet_capability_calculator import FleetCapabilityCalculator
      has_yard = FleetCapabilityCalculator.ship_has_spaceyard(ship)
      if has_yard and not show_has_yard:
          return False
      if not has_yard and not show_no_yard:
          return False
      return True
  ```
- [ ] Run spaceyard tests: verify passing
- [ ] Do NOT modify `filter_ships` yet

**Notes:** Keep late import inside function to avoid circular imports

---

### Task 2.3: Extract `_passes_cargo_filter` [Simple]
**File:** `game/ui/screens/fleet_report_filters.py`
**Tests:** `pytest tests/unit/ui/screens/test_fleet_report_filters.py::TestFilterShipsCargo -v`

Extract lines 167-174 into a helper function.

- [ ] Add helper function:
  ```python
  def _passes_cargo_filter(ship: ShipInstance, filter_state: Dict[str, bool]) -> bool:
      """Check if ship passes cargo presence filter."""
      show_has_cargo = filter_state.get('show_has_cargo', True)
      show_no_cargo = filter_state.get('show_no_cargo', True)

      if show_has_cargo and show_no_cargo:
          return True

      has_cargo = bool(ship.cargo_contents) and sum(ship.cargo_contents.values()) > 0
      if has_cargo and not show_has_cargo:
          return False
      if not has_cargo and not show_no_cargo:
          return False
      return True
  ```
- [ ] Run cargo tests: verify passing
- [ ] Do NOT modify `filter_ships` yet

**Notes:** Preserve the cargo boolean logic exactly

---

### Task 2.4: Extract `_passes_special_ability_filters` [Medium]
**File:** `game/ui/screens/fleet_report_filters.py`
**Tests:** `pytest tests/unit/ui/screens/test_fleet_report_filters.py::TestSpecialCapabilityFilter -v`

Extract lines 177-194 into a helper function.

- [ ] Add helper function (preserve late import inside function):
  ```python
  def _passes_special_ability_filters(ship: ShipInstance, filter_state: Dict[str, bool]) -> bool:
      """Check if ship passes all special ability filters."""
      for col_id, ability_name in SPECIAL_CAPABILITY_COLUMNS.items():
          show_has = filter_state.get(f'show_{col_id}', True)
          no_key = col_id.replace('can_', 'no_', 1)
          show_not = filter_state.get(f'show_{no_key}', True)

          if show_has and show_not:
              continue

          from game.strategy.data.fleet_capability_calculator import FleetCapabilityCalculator
          has_ability = FleetCapabilityCalculator.ship_has_ability(ship, ability_name)
          if has_ability and not show_has:
              return False
          if not has_ability and not show_not:
              return False
      return True
  ```
- [ ] Run special capability tests: verify passing
- [ ] Do NOT modify `filter_ships` yet

**Notes:** This helper will have higher CC due to loop, but isolates the complexity

---

### Task 2.5: Extract `_passes_status_filter` [Critical]
**File:** `game/ui/screens/fleet_report_filters.py`
**Tests:** `pytest tests/unit/ui/screens/test_fleet_report_filters.py::TestFilterShips -v`

Extract lines 196-220 into a helper function. **This is the critical one with mutual exclusivity.**

- [ ] Add helper function:
  ```python
  def _passes_status_filter(ship: ShipInstance, filter_state: Dict[str, bool]) -> bool:
      """
      Check if ship passes status filter.

      Status categories are mutually exclusive in this order:
      destroyed > derelict > damaged > undamaged
      """
      # Determine ship's status category (mutually exclusive, checked in priority order)
      if not ship.is_alive:
          status_key = 'show_destroyed'
      elif ship.is_derelict:
          status_key = 'show_derelict'
      elif ship.is_damaged():
          status_key = 'show_damaged'
      else:
          status_key = 'show_undamaged'

      return filter_state.get(status_key, True)
  ```
- [ ] Run status tests: verify passing (including hierarchy tests from Phase 1)
- [ ] Do NOT modify `filter_ships` yet

**Notes:** The mutual exclusivity is now explicit in the if/elif chain

---

### Task 2.6: Run Full Test Suite [Simple]
**Tests:** `pytest tests/ -n 12`

- [ ] Run full test suite with all 5 helpers added
- [ ] Verify: Same test count as Phase 1, 0 failures
- [ ] Commit with message: `[PROJ-230] Phase 2: Add filter helper functions`

**Notes:** Helpers are added but not yet used - all tests should still pass

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All 5 helper functions added
- [ ] All task checkboxes above are checked
- [ ] Full test suite passes
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 3
