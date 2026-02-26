# Phase 2: Extract Helpers

**Goal:** Extract 5 helper functions from `filter_ships` to reduce complexity.

**File:** `game/ui/screens/fleet_report_filters.py`

## Tasks

### 2.1 Extract `_passes_warp_filter`
- [ ] Create helper function at line ~124 (before filter_ships):
  ```python
  def _passes_warp_filter(ship: ShipInstance, filter_state: Dict[str, bool]) -> bool:
      """Return True if ship passes warp capability filter."""
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
- [ ] Replace lines 143-153 in filter_ships with:
  ```python
  if not _passes_warp_filter(ship, filter_state):
      continue
  ```
- [ ] Run tests: `pytest tests/unit/ui/screens/test_fleet_report_filters.py -v`

### 2.2 Extract `_passes_spaceyard_filter`
- [ ] Create helper function:
  ```python
  def _passes_spaceyard_filter(ship: ShipInstance, filter_state: Dict[str, bool]) -> bool:
      """Return True if ship passes spaceyard capability filter."""
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
- [ ] Replace lines 155-164 in filter_ships with:
  ```python
  if not _passes_spaceyard_filter(ship, filter_state):
      continue
  ```
- [ ] Run tests: `pytest tests/unit/ui/screens/test_fleet_report_filters.py -v`

### 2.3 Extract `_passes_cargo_filter`
- [ ] Create helper function:
  ```python
  def _passes_cargo_filter(ship: ShipInstance, filter_state: Dict[str, bool]) -> bool:
      """Return True if ship passes cargo filter."""
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
- [ ] Replace lines 166-174 in filter_ships with:
  ```python
  if not _passes_cargo_filter(ship, filter_state):
      continue
  ```
- [ ] Run tests: `pytest tests/unit/ui/screens/test_fleet_report_filters.py -v`

### 2.4 Extract `_passes_capability_filters`
- [ ] Create helper function:
  ```python
  def _passes_capability_filters(ship: ShipInstance, filter_state: Dict[str, bool]) -> bool:
      """Return True if ship passes all special capability filters."""
      from game.strategy.data.fleet_capability_calculator import FleetCapabilityCalculator
      for col_id, ability_name in SPECIAL_CAPABILITY_COLUMNS.items():
          show_has = filter_state.get(f'show_{col_id}', True)
          no_key = col_id.replace('can_', 'no_', 1)
          show_not = filter_state.get(f'show_{no_key}', True)
          if show_has and show_not:
              continue
          has_ability = FleetCapabilityCalculator.ship_has_ability(ship, ability_name)
          if has_ability and not show_has:
              return False
          if not has_ability and not show_not:
              return False
      return True
  ```
- [ ] Replace lines 176-194 in filter_ships with:
  ```python
  if not _passes_capability_filters(ship, filter_state):
      continue
  ```
- [ ] Run tests: `pytest tests/unit/ui/screens/test_fleet_report_filters.py -v`

### 2.5 Extract `_get_ship_status_filter_key`
- [ ] Create helper function:
  ```python
  def _get_ship_status_filter_key(ship: ShipInstance) -> str:
      """Return the filter_state key for the ship's current status."""
      if not ship.is_alive:
          return 'show_destroyed'
      if ship.is_derelict:
          return 'show_derelict'
      if ship.is_damaged():
          return 'show_damaged'
      return 'show_undamaged'
  ```
- [ ] Replace lines 196-220 in filter_ships with:
  ```python
  status_key = _get_ship_status_filter_key(ship)
  if filter_state.get(status_key, True):
      result.append(ship)
  ```
- [ ] Run tests: `pytest tests/unit/ui/screens/test_fleet_report_filters.py -v`

### 2.6 Final filter_ships structure
- [ ] Verify final filter_ships function looks like:
  ```python
  def filter_ships(ships: List[ShipInstance], filter_state: Dict[str, bool]) -> List[ShipInstance]:
      """Filter ships based on status filter state."""
      result = []
      for ship in ships:
          if not _passes_warp_filter(ship, filter_state):
              continue
          if not _passes_spaceyard_filter(ship, filter_state):
              continue
          if not _passes_cargo_filter(ship, filter_state):
              continue
          if not _passes_capability_filters(ship, filter_state):
              continue

          status_key = _get_ship_status_filter_key(ship)
          if filter_state.get(status_key, True):
              result.append(ship)
      return result
  ```
- [ ] Run full test file: `pytest tests/unit/ui/screens/test_fleet_report_filters.py -v`

## Completion Criteria
- [ ] 5 helper functions extracted
- [ ] filter_ships main function simplified
- [ ] All tests passing
- [ ] Ready to proceed to Phase 3
