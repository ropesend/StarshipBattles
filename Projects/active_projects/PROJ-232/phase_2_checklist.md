# Phase 2: Extract Helper Functions

**Objective:** Extract filter predicates into separate private functions to reduce complexity.

**File:** `game/ui/screens/fleet_report_filters.py`

---

## Tasks

### 2.1 Move Late Import to Function Top
- [ ] Move `from game.strategy.data.fleet_capability_calculator import FleetCapabilityCalculator` to the top of `filter_ships` function (line ~125)
- [ ] Remove duplicate imports from inside conditionals (lines 159, 185)
- [ ] Run: `pytest tests/unit/ui/screens/test_fleet_report_filters.py -v`

### 2.2 Extract `_get_ship_status_category()` Helper
- [ ] Add new function before `filter_ships` (around line 124):
  ```python
  def _get_ship_status_category(ship: 'ShipInstance') -> str:
      """Determine the status category of a ship.

      Returns one of: 'destroyed', 'derelict', 'damaged', 'undamaged'

      IMPORTANT: Order matters - derelict implies damaged, so check derelict first.
      """
      if not ship.is_alive:
          return 'destroyed'
      if ship.is_derelict:
          return 'derelict'
      if ship.is_damaged():
          return 'damaged'
      return 'undamaged'
  ```
- [ ] Run: `pytest tests/unit/ui/screens/test_fleet_report_filters.py -v`

### 2.3 Extract `_passes_status_filter()` Helper
- [ ] Add new function after `_get_ship_status_category`:
  ```python
  def _passes_status_filter(ship: 'ShipInstance', filter_state: Dict[str, bool]) -> bool:
      """Check if ship passes the status filter."""
      category = _get_ship_status_category(ship)
      return filter_state.get(f'show_{category}', True)
  ```
- [ ] Run: `pytest tests/unit/ui/screens/test_fleet_report_filters.py -v`

### 2.4 Extract `_passes_binary_capability_filter()` Helper
- [ ] Add new function:
  ```python
  def _passes_binary_capability_filter(
      has_capability: bool,
      show_has: bool,
      show_not: bool
  ) -> bool:
      """Generic binary filter check.

      Args:
          has_capability: Whether the ship has the capability
          show_has: Filter state for showing ships WITH capability
          show_not: Filter state for showing ships WITHOUT capability

      Returns:
          True if ship passes filter, False if it should be excluded
      """
      if show_has and show_not:
          return True  # No filtering needed
      if has_capability:
          return show_has
      return show_not
  ```
- [ ] Run: `pytest tests/unit/ui/screens/test_fleet_report_filters.py -v`

### 2.5 Extract `_passes_warp_filter()` Helper
- [ ] Add new function:
  ```python
  def _passes_warp_filter(ship: 'ShipInstance', filter_state: Dict[str, bool]) -> bool:
      """Check if ship passes the warp capability filter."""
      show_warp = filter_state.get('show_warp_capable', True)
      show_not_warp = filter_state.get('show_not_warp_capable', True)

      if show_warp and show_not_warp:
          return True

      is_warp_capable = ShipStatsCalculator.has_warp_capability(ship)
      return _passes_binary_capability_filter(is_warp_capable, show_warp, show_not_warp)
  ```
- [ ] Run: `pytest tests/unit/ui/screens/test_fleet_report_filters.py::TestFilterShipsWarp -v`

### 2.6 Extract `_passes_spaceyard_filter()` Helper
- [ ] Add new function:
  ```python
  def _passes_spaceyard_filter(
      ship: 'ShipInstance',
      filter_state: Dict[str, bool],
      capability_calculator
  ) -> bool:
      """Check if ship passes the spaceyard capability filter."""
      show_has = filter_state.get('show_has_spaceyard', True)
      show_not = filter_state.get('show_no_spaceyard', True)

      if show_has and show_not:
          return True

      has_yard = capability_calculator.ship_has_spaceyard(ship)
      return _passes_binary_capability_filter(has_yard, show_has, show_not)
  ```
- [ ] Run: `pytest tests/unit/ui/screens/test_fleet_report_filters.py::TestFilterShipsSpaceyard -v`

### 2.7 Extract `_passes_cargo_filter()` Helper
- [ ] Add new function:
  ```python
  def _passes_cargo_filter(ship: 'ShipInstance', filter_state: Dict[str, bool]) -> bool:
      """Check if ship passes the cargo filter."""
      show_has = filter_state.get('show_has_cargo', True)
      show_not = filter_state.get('show_no_cargo', True)

      if show_has and show_not:
          return True

      has_cargo = bool(ship.cargo_contents) and sum(ship.cargo_contents.values()) > 0
      return _passes_binary_capability_filter(has_cargo, show_has, show_not)
  ```
- [ ] Run: `pytest tests/unit/ui/screens/test_fleet_report_filters.py::TestFilterShipsCargo -v`

### 2.8 Extract `_passes_special_capabilities_filter()` Helper
- [ ] Add new function:
  ```python
  def _passes_special_capabilities_filter(
      ship: 'ShipInstance',
      filter_state: Dict[str, bool],
      capability_calculator
  ) -> bool:
      """Check if ship passes all special capability filters."""
      for col_id, ability_name in SPECIAL_CAPABILITY_COLUMNS.items():
          show_has = filter_state.get(f'show_{col_id}', True)
          no_key = col_id.replace('can_', 'no_', 1)
          show_not = filter_state.get(f'show_{no_key}', True)

          if show_has and show_not:
              continue  # No filtering for this capability

          has_ability = capability_calculator.ship_has_ability(ship, ability_name)
          if not _passes_binary_capability_filter(has_ability, show_has, show_not):
              return False
      return True
  ```
- [ ] Run: `pytest tests/unit/ui/screens/test_fleet_report_filters.py::TestSpecialCapabilityFilter -v`

### 2.9 Run Full Test Suite
- [ ] Run: `pytest tests/unit/ui/screens/test_fleet_report_filters.py -v`
- [ ] Verify all tests pass
- [ ] All helper functions are defined but not yet used by `filter_ships`

---

## Completion Criteria

- [ ] All 7 helper functions extracted
- [ ] All tests still pass (helpers not yet integrated)
- [ ] No behavioral changes yet
