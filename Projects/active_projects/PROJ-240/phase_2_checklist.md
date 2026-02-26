# Phase 2: Extract Helper Functions

> **Goal:** Extract repeated binary filter pattern and status filter logic into helper functions.

## Pre-Conditions
- [ ] Phase 1 complete (edge case tests added)
- [ ] All tests passing

## Tasks

### 2.1 Extract `_passes_binary_filter` Helper
**File:** `game/ui/screens/fleet_report_filters.py`
**Location:** Add before `filter_ships` function (around line 120)

- [ ] Add helper function:
  ```python
  def _passes_binary_filter(has_capability: bool, show_has: bool, show_not: bool) -> bool:
      """
      Check if ship passes a binary capability filter.

      Args:
          has_capability: Whether the ship has the capability
          show_has: Filter setting for ships WITH the capability
          show_not: Filter setting for ships WITHOUT the capability

      Returns:
          True if ship should be included, False if filtered out
      """
      if show_has and show_not:
          return True  # No filtering needed
      if has_capability:
          return show_has
      return show_not
  ```

- [ ] Run tests: `pytest tests/unit/ui/screens/test_fleet_report_filters.py -v`

### 2.2 Extract `_passes_warp_filter` Helper
**File:** `game/ui/screens/fleet_report_filters.py`

- [ ] Add helper function:
  ```python
  def _passes_warp_filter(ship: 'ShipInstance', filter_state: Dict[str, bool]) -> bool:
      """Check if ship passes the warp capability filter."""
      show_warp = filter_state.get('show_warp_capable', True)
      show_not_warp = filter_state.get('show_not_warp_capable', True)
      if show_warp and show_not_warp:
          return True
      is_warp_capable = ShipStatsCalculator.has_warp_capability(ship)
      return _passes_binary_filter(is_warp_capable, show_warp, show_not_warp)
  ```

- [ ] Run tests: `pytest tests/unit/ui/screens/test_fleet_report_filters.py::TestFilterShipsWarp -v`

### 2.3 Extract `_passes_spaceyard_filter` Helper
**File:** `game/ui/screens/fleet_report_filters.py`

- [ ] Add helper function:
  ```python
  def _passes_spaceyard_filter(ship: 'ShipInstance', filter_state: Dict[str, bool]) -> bool:
      """Check if ship passes the spaceyard capability filter."""
      show_has_yard = filter_state.get('show_has_spaceyard', True)
      show_no_yard = filter_state.get('show_no_spaceyard', True)
      if show_has_yard and show_no_yard:
          return True
      # LATE IMPORT: Avoid circular import
      from game.strategy.data.fleet_capability_calculator import FleetCapabilityCalculator
      has_yard = FleetCapabilityCalculator.ship_has_spaceyard(ship)
      return _passes_binary_filter(has_yard, show_has_yard, show_no_yard)
  ```

- [ ] Run tests: `pytest tests/unit/ui/screens/test_fleet_report_filters.py::TestFilterShipsSpaceyard -v`

### 2.4 Extract `_passes_cargo_filter` Helper
**File:** `game/ui/screens/fleet_report_filters.py`

- [ ] Add helper function:
  ```python
  def _passes_cargo_filter(ship: 'ShipInstance', filter_state: Dict[str, bool]) -> bool:
      """Check if ship passes the cargo filter."""
      show_has_cargo = filter_state.get('show_has_cargo', True)
      show_no_cargo = filter_state.get('show_no_cargo', True)
      if show_has_cargo and show_no_cargo:
          return True
      has_cargo = bool(ship.cargo_contents) and sum(ship.cargo_contents.values()) > 0
      return _passes_binary_filter(has_cargo, show_has_cargo, show_no_cargo)
  ```

- [ ] Run tests: `pytest tests/unit/ui/screens/test_fleet_report_filters.py::TestFilterShipsCargo -v`

### 2.5 Extract `_passes_special_capability_filters` Helper
**File:** `game/ui/screens/fleet_report_filters.py`

- [ ] Add helper function:
  ```python
  def _passes_special_capability_filters(ship: 'ShipInstance', filter_state: Dict[str, bool]) -> bool:
      """Check if ship passes all special capability filters."""
      for col_id, ability_name in SPECIAL_CAPABILITY_COLUMNS.items():
          show_has = filter_state.get(f'show_{col_id}', True)
          no_key = col_id.replace('can_', 'no_', 1)
          show_not = filter_state.get(f'show_{no_key}', True)
          if show_has and show_not:
              continue
          # LATE IMPORT: Avoid circular import
          from game.strategy.data.fleet_capability_calculator import FleetCapabilityCalculator
          has_ability = FleetCapabilityCalculator.ship_has_ability(ship, ability_name)
          if not _passes_binary_filter(has_ability, show_has, show_not):
              return False
      return True
  ```

- [ ] Run tests: `pytest tests/unit/ui/screens/test_fleet_report_filters.py::TestSpecialCapabilityFilter -v`

### 2.6 Extract `_get_ship_status` Helper
**File:** `game/ui/screens/fleet_report_filters.py`

- [ ] Add helper function:
  ```python
  def _get_ship_status(ship: 'ShipInstance') -> str:
      """
      Classify ship into mutually exclusive status category.

      Returns one of: 'destroyed', 'derelict', 'damaged', 'undamaged'
      """
      if not ship.is_alive:
          return 'destroyed'
      if ship.is_derelict:
          return 'derelict'
      if ship.is_damaged():
          return 'damaged'
      return 'undamaged'
  ```

- [ ] Run tests: `pytest tests/unit/ui/screens/test_fleet_report_filters.py -v`

### 2.7 Extract `_passes_status_filter` Helper
**File:** `game/ui/screens/fleet_report_filters.py`

- [ ] Add helper function:
  ```python
  def _passes_status_filter(ship: 'ShipInstance', filter_state: Dict[str, bool]) -> bool:
      """Check if ship passes the status filter based on its status category."""
      status = _get_ship_status(ship)
      filter_key = f'show_{status}'
      return filter_state.get(filter_key, True)
  ```

- [ ] Run tests: `pytest tests/unit/ui/screens/test_fleet_report_filters.py::TestFilterShips -v`

## Verification
```bash
pytest tests/unit/ui/screens/test_fleet_report_filters.py -v
```

## Exit Criteria
- [ ] 7 helper functions added
- [ ] All tests pass
- [ ] Commit: `[PROJ-240] Phase 2: Extract filter helper functions`
