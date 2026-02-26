# Phase 2: Extract Helpers

> **Goal:** Extract filter logic into focused helper functions to reduce complexity.

## Pre-Phase Checklist
- [ ] Phase 1 complete (all tests passing)
- [ ] Read target file: `game/ui/screens/fleet_report_filters.py`
- [ ] Baseline test run: `pytest tests/unit/ui/screens/test_fleet_report_filters.py -v`

## Tasks

### 2.1 Extract `_passes_binary_filter` Helper
**File:** `game/ui/screens/fleet_report_filters.py`
**Location:** Add before `filter_ships` function (around line 120)

- [ ] Add helper function:
  ```python
  def _passes_binary_filter(
      filter_state: Dict[str, bool],
      show_key: str,
      show_not_key: str,
      has_capability: bool
  ) -> bool:
      """Check if a ship passes a binary (has/doesn't have) capability filter.

      Returns True if the ship should be included based on the filter settings.
      Both filters default to True (show all) if keys are missing.
      """
      show_has = filter_state.get(show_key, True)
      show_not = filter_state.get(show_not_key, True)

      # Both enabled = show all
      if show_has and show_not:
          return True

      # Check based on capability
      if has_capability:
          return show_has
      return show_not
  ```
- [ ] Run tests: `pytest tests/unit/ui/screens/test_fleet_report_filters.py -v`

### 2.2 Extract `_passes_warp_filter` Helper
**File:** `game/ui/screens/fleet_report_filters.py`
**Location:** Add after `_passes_binary_filter`

- [ ] Add helper function:
  ```python
  def _passes_warp_filter(ship: 'ShipInstance', filter_state: Dict[str, bool]) -> bool:
      """Check if ship passes warp capability filter."""
      show_warp = filter_state.get('show_warp_capable', True)
      show_not_warp = filter_state.get('show_not_warp_capable', True)

      # Skip expensive check if both filters enabled
      if show_warp and show_not_warp:
          return True

      is_warp_capable = ShipStatsCalculator.has_warp_capability(ship)
      return _passes_binary_filter(filter_state, 'show_warp_capable', 'show_not_warp_capable', is_warp_capable)
  ```
- [ ] Run tests: `pytest tests/unit/ui/screens/test_fleet_report_filters.py::TestFilterShipsWarp -v`

### 2.3 Extract `_passes_spaceyard_filter` Helper
**File:** `game/ui/screens/fleet_report_filters.py`
**Location:** Add after `_passes_warp_filter`

- [ ] Add helper function:
  ```python
  def _passes_spaceyard_filter(ship: 'ShipInstance', filter_state: Dict[str, bool]) -> bool:
      """Check if ship passes spaceyard capability filter."""
      show_has = filter_state.get('show_has_spaceyard', True)
      show_not = filter_state.get('show_no_spaceyard', True)

      # Skip expensive check if both filters enabled
      if show_has and show_not:
          return True

      # INTENTIONAL LATE IMPORT: Avoid circular import with strategy data
      from game.strategy.data.fleet_capability_calculator import FleetCapabilityCalculator
      has_yard = FleetCapabilityCalculator.ship_has_spaceyard(ship)
      return _passes_binary_filter(filter_state, 'show_has_spaceyard', 'show_no_spaceyard', has_yard)
  ```
- [ ] Run tests: `pytest tests/unit/ui/screens/test_fleet_report_filters.py::TestFilterShipsSpaceyard -v`

### 2.4 Extract `_passes_cargo_filter` Helper
**File:** `game/ui/screens/fleet_report_filters.py`
**Location:** Add after `_passes_spaceyard_filter`

- [ ] Add helper function:
  ```python
  def _passes_cargo_filter(ship: 'ShipInstance', filter_state: Dict[str, bool]) -> bool:
      """Check if ship passes cargo filter."""
      show_has = filter_state.get('show_has_cargo', True)
      show_not = filter_state.get('show_no_cargo', True)

      # Skip check if both filters enabled
      if show_has and show_not:
          return True

      has_cargo = bool(ship.cargo_contents) and sum(ship.cargo_contents.values()) > 0
      return _passes_binary_filter(filter_state, 'show_has_cargo', 'show_no_cargo', has_cargo)
  ```
- [ ] Run tests: `pytest tests/unit/ui/screens/test_fleet_report_filters.py::TestFilterShipsCargo -v`

### 2.5 Extract `_passes_special_capability_filters` Helper
**File:** `game/ui/screens/fleet_report_filters.py`
**Location:** Add after `_passes_cargo_filter`

- [ ] Add helper function:
  ```python
  def _passes_special_capability_filters(ship: 'ShipInstance', filter_state: Dict[str, bool]) -> bool:
      """Check if ship passes all special capability filters (destroy planet, open warp, etc.)."""
      for col_id, ability_name in SPECIAL_CAPABILITY_COLUMNS.items():
          # Derive filter keys from column id
          show_has = filter_state.get(f'show_{col_id}', True)
          no_key = col_id.replace('can_', 'no_', 1)
          show_not = filter_state.get(f'show_{no_key}', True)

          # Skip check if both filters enabled
          if show_has and show_not:
              continue

          # INTENTIONAL LATE IMPORT: Avoid circular import with strategy data
          from game.strategy.data.fleet_capability_calculator import FleetCapabilityCalculator
          has_ability = FleetCapabilityCalculator.ship_has_ability(ship, ability_name)

          if has_ability and not show_has:
              return False
          if not has_ability and not show_not:
              return False

      return True
  ```
- [ ] Run tests: `pytest tests/unit/ui/screens/test_fleet_report_filters.py::TestSpecialCapabilityFilter -v`

### 2.6 Extract `_classify_ship_status` Helper
**File:** `game/ui/screens/fleet_report_filters.py`
**Location:** Add after `_passes_special_capability_filters`

- [ ] Add helper function:
  ```python
  def _classify_ship_status(ship: 'ShipInstance') -> str:
      """Classify ship into status category.

      Returns one of: 'destroyed', 'derelict', 'damaged', 'undamaged'.
      Order is important - a derelict ship is also damaged but should return 'derelict'.
      """
      if not ship.is_alive:
          return 'destroyed'
      if ship.is_derelict:
          return 'derelict'
      if ship.is_damaged():
          return 'damaged'
      return 'undamaged'
  ```
- [ ] Run tests: `pytest tests/unit/ui/screens/test_fleet_report_filters.py::TestFilterShips -v`

### 2.7 Extract `_passes_status_filter` Helper
**File:** `game/ui/screens/fleet_report_filters.py`
**Location:** Add after `_classify_ship_status`

- [ ] Add helper function:
  ```python
  def _passes_status_filter(ship: 'ShipInstance', filter_state: Dict[str, bool]) -> bool:
      """Check if ship passes status filter based on its classified status."""
      status = _classify_ship_status(ship)
      return filter_state.get(f'show_{status}', True)
  ```
- [ ] Run tests: `pytest tests/unit/ui/screens/test_fleet_report_filters.py::TestFilterShips -v`

## Post-Phase Checklist
- [ ] All 7 helper functions added
- [ ] All tests still pass: `pytest tests/unit/ui/screens/test_fleet_report_filters.py -v`
- [ ] Full test suite passes: `pytest tests/ -n 12`
- [ ] Commit: `git commit -m "[PROJ-247] Phase 2: Extract helper predicates for filter_ships"`
