# Phase 2: Extract Helper Functions

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-246 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Extract filter logic into private helper functions to reduce `filter_ships` complexity

---

## Tasks

### Task 2.1: Extract Generic Binary Filter Helper [Simple]
**File:** `game/ui/screens/fleet_report_filters.py`
**Tests:** `pytest tests/unit/ui/screens/test_fleet_report_filters.py -v`

Add generic helper function before `filter_ships`:

- [ ] Add `_check_binary_filter()` function at line ~123 (before `filter_ships`):
  ```python
  def _check_binary_filter(
      filter_state: Dict[str, bool],
      show_key: str,
      hide_key: str,
      has_property: bool
  ) -> bool:
      """
      Check if a ship passes a binary filter (show/hide pair).

      Returns True if the ship passes the filter, False if it should be excluded.
      When both filter flags are True, the filter is effectively disabled.
      """
      show_has = filter_state.get(show_key, True)
      show_not = filter_state.get(hide_key, True)
      if show_has and show_not:
          return True  # Both enabled, no filtering
      if has_property:
          return show_has
      return show_not
  ```
- [ ] Run tests: `pytest tests/unit/ui/screens/test_fleet_report_filters.py -v`
- [ ] All tests still pass

**Notes:** [Filled during implementation]

---

### Task 2.2: Extract Warp Filter [Simple]
**File:** `game/ui/screens/fleet_report_filters.py`
**Tests:** `pytest tests/unit/ui/screens/test_fleet_report_filters.py::TestFilterShipsWarp -v`

Extract warp capability filter logic:

- [ ] Add `_passes_warp_filter()` function after `_check_binary_filter`:
  ```python
  def _passes_warp_filter(ship: 'ShipInstance', filter_state: Dict[str, bool]) -> bool:
      """Check if ship passes warp capability filter."""
      show_warp = filter_state.get('show_warp_capable', True)
      show_not_warp = filter_state.get('show_not_warp_capable', True)
      if show_warp and show_not_warp:
          return True  # Both enabled, skip expensive check
      is_warp_capable = ShipStatsCalculator.has_warp_capability(ship)
      return _check_binary_filter(filter_state, 'show_warp_capable', 'show_not_warp_capable', is_warp_capable)
  ```
- [ ] Replace lines 144-153 in `filter_ships` with:
  ```python
  if not _passes_warp_filter(ship, filter_state):
      continue
  ```
- [ ] Run tests: `pytest tests/unit/ui/screens/test_fleet_report_filters.py::TestFilterShipsWarp -v`

**Notes:** [Filled during implementation]

---

### Task 2.3: Extract Spaceyard Filter [Simple]
**File:** `game/ui/screens/fleet_report_filters.py`
**Tests:** `pytest tests/unit/ui/screens/test_fleet_report_filters.py::TestFilterShipsSpaceyard -v`

Extract spaceyard filter logic:

- [ ] Add `_passes_spaceyard_filter()` function:
  ```python
  def _passes_spaceyard_filter(ship: 'ShipInstance', filter_state: Dict[str, bool]) -> bool:
      """Check if ship passes spaceyard filter."""
      show_has_yard = filter_state.get('show_has_spaceyard', True)
      show_no_yard = filter_state.get('show_no_spaceyard', True)
      if show_has_yard and show_no_yard:
          return True  # Both enabled, skip expensive check
      # INTENTIONAL LATE IMPORT: Avoid circular import
      from game.strategy.data.fleet_capability_calculator import FleetCapabilityCalculator
      has_yard = FleetCapabilityCalculator.ship_has_spaceyard(ship)
      return _check_binary_filter(filter_state, 'show_has_spaceyard', 'show_no_spaceyard', has_yard)
  ```
- [ ] Replace spaceyard filter block in `filter_ships` with:
  ```python
  if not _passes_spaceyard_filter(ship, filter_state):
      continue
  ```
- [ ] Run tests: `pytest tests/unit/ui/screens/test_fleet_report_filters.py::TestFilterShipsSpaceyard -v`

**Notes:** [Filled during implementation]

---

### Task 2.4: Extract Cargo Filter [Simple]
**File:** `game/ui/screens/fleet_report_filters.py`
**Tests:** `pytest tests/unit/ui/screens/test_fleet_report_filters.py::TestFilterShipsCargo -v`

Extract cargo filter logic:

- [ ] Add `_passes_cargo_filter()` function:
  ```python
  def _passes_cargo_filter(ship: 'ShipInstance', filter_state: Dict[str, bool]) -> bool:
      """Check if ship passes cargo filter."""
      show_has_cargo = filter_state.get('show_has_cargo', True)
      show_no_cargo = filter_state.get('show_no_cargo', True)
      if show_has_cargo and show_no_cargo:
          return True  # Both enabled, skip check
      has_cargo = bool(ship.cargo_contents) and sum(ship.cargo_contents.values()) > 0
      return _check_binary_filter(filter_state, 'show_has_cargo', 'show_no_cargo', has_cargo)
  ```
- [ ] Replace cargo filter block in `filter_ships` with:
  ```python
  if not _passes_cargo_filter(ship, filter_state):
      continue
  ```
- [ ] Run tests: `pytest tests/unit/ui/screens/test_fleet_report_filters.py::TestFilterShipsCargo -v`

**Notes:** [Filled during implementation]

---

### Task 2.5: Extract Special Capabilities Filter [Medium]
**File:** `game/ui/screens/fleet_report_filters.py`
**Tests:** `pytest tests/unit/ui/screens/test_fleet_report_filters.py::TestSpecialCapabilityFilter -v`

Extract special capabilities filter loop:

- [ ] Add `_passes_special_capability_filters()` function:
  ```python
  def _passes_special_capability_filters(ship: 'ShipInstance', filter_state: Dict[str, bool]) -> bool:
      """Check if ship passes all special capability filters."""
      # INTENTIONAL LATE IMPORT: Avoid circular import
      from game.strategy.data.fleet_capability_calculator import FleetCapabilityCalculator

      for col_id, ability_name in SPECIAL_CAPABILITY_COLUMNS.items():
          show_has = filter_state.get(f'show_{col_id}', True)
          no_key = col_id.replace('can_', 'no_', 1)
          show_not = filter_state.get(f'show_{no_key}', True)

          if show_has and show_not:
              continue  # This filter not active

          has_ability = FleetCapabilityCalculator.ship_has_ability(ship, ability_name)
          if not _check_binary_filter(filter_state, f'show_{col_id}', f'show_{no_key}', has_ability):
              return False
      return True
  ```
- [ ] Replace special capabilities loop in `filter_ships` with:
  ```python
  if not _passes_special_capability_filters(ship, filter_state):
      continue
  ```
- [ ] Run tests: `pytest tests/unit/ui/screens/test_fleet_report_filters.py::TestSpecialCapabilityFilter -v`

**Notes:** [Filled during implementation]

---

### Task 2.6: Extract Status Filter [Medium]
**File:** `game/ui/screens/fleet_report_filters.py`
**Tests:** `pytest tests/unit/ui/screens/test_fleet_report_filters.py::TestFilterShips -v`

Extract status filter logic (most complex part):

- [ ] Add `_get_ship_status()` helper:
  ```python
  def _get_ship_status(ship: 'ShipInstance') -> str:
      """
      Classify ship into a status category.

      Returns one of: 'destroyed', 'derelict', 'damaged', 'undamaged'
      Priority order: Destroyed > Derelict > Damaged > Undamaged
      """
      if not ship.is_alive:
          return 'destroyed'
      if ship.is_derelict:
          return 'derelict'
      if ship.is_damaged():
          return 'damaged'
      return 'undamaged'
  ```
- [ ] Add `_passes_status_filter()` function:
  ```python
  def _passes_status_filter(ship: 'ShipInstance', filter_state: Dict[str, bool]) -> bool:
      """Check if ship passes status filter based on its classification."""
      status = _get_ship_status(ship)
      return filter_state.get(f'show_{status}', True)
  ```
- [ ] Replace status filter cascade in `filter_ships` with:
  ```python
  if not _passes_status_filter(ship, filter_state):
      continue
  result.append(ship)
  ```
- [ ] Run tests: `pytest tests/unit/ui/screens/test_fleet_report_filters.py::TestFilterShips -v`

**Notes:** [Filled during implementation]

---

### Task 2.7: Clean Up Main Function [Simple]
**File:** `game/ui/screens/fleet_report_filters.py`
**Tests:** `pytest tests/unit/ui/screens/test_fleet_report_filters.py -v`

Verify the refactored `filter_ships` is clean:

- [ ] Verify `filter_ships` now looks like:
  ```python
  def filter_ships(ships: List[ShipInstance], filter_state: Dict[str, bool]) -> List[ShipInstance]:
      """Filter ships based on status filter state. [existing docstring]"""
      result = []
      for ship in ships:
          if not _passes_warp_filter(ship, filter_state):
              continue
          if not _passes_spaceyard_filter(ship, filter_state):
              continue
          if not _passes_cargo_filter(ship, filter_state):
              continue
          if not _passes_special_capability_filters(ship, filter_state):
              continue
          if not _passes_status_filter(ship, filter_state):
              continue
          result.append(ship)
      return result
  ```
- [ ] Run all filter tests: `pytest tests/unit/ui/screens/test_fleet_report_filters.py -v`
- [ ] All 19+ tests pass

**Notes:** [Filled during implementation]

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 3
