# Phase 2: Extract Filter Helpers

**Goal:** Extract helper functions to reduce complexity while preserving behavior.

**File:** `game/ui/screens/fleet_report_filters.py`

## Tasks

### 2.1 Extract Binary Filter Helper
- [ ] Add `_passes_binary_filter` function (after imports, before `calculate_fleet_stats`)
  ```python
  def _passes_binary_filter(
      filter_state: Dict[str, bool],
      positive_key: str,
      negative_key: str,
      has_property: bool
  ) -> bool:
      """
      Check if a ship passes a binary filter (has/doesn't have property).

      Returns True if the ship should be included.
      """
      show_positive = filter_state.get(positive_key, True)
      show_negative = filter_state.get(negative_key, True)

      if show_positive and show_negative:
          return True  # Both shown, always passes

      if has_property:
          return show_positive
      return show_negative
  ```
- [ ] Run tests to verify no regressions

### 2.2 Extract Status Category Helper
- [ ] Add `_get_status_category` function
  ```python
  def _get_status_category(ship: 'ShipInstance') -> str:
      """
      Get the ship's status category for filtering.

      Order matters: destroyed > derelict > damaged > undamaged
      """
      if not ship.is_alive:
          return 'destroyed'
      if ship.is_derelict:
          return 'derelict'
      if ship.is_damaged():
          return 'damaged'
      return 'undamaged'
  ```
- [ ] Run tests to verify no regressions

### 2.3 Extract Warp Filter Helper
- [ ] Add `_passes_warp_filter` function
  ```python
  def _passes_warp_filter(ship: 'ShipInstance', filter_state: Dict[str, bool]) -> bool:
      """Check if ship passes warp capability filter."""
      show_warp = filter_state.get('show_warp_capable', True)
      show_not_warp = filter_state.get('show_not_warp_capable', True)

      if show_warp and show_not_warp:
          return True

      is_warp_capable = ShipStatsCalculator.has_warp_capability(ship)
      return _passes_binary_filter(filter_state, 'show_warp_capable', 'show_not_warp_capable', is_warp_capable)
  ```
- [ ] Run tests to verify no regressions

### 2.4 Extract Spaceyard Filter Helper
- [ ] Add `_passes_spaceyard_filter` function
  ```python
  def _passes_spaceyard_filter(ship: 'ShipInstance', filter_state: Dict[str, bool]) -> bool:
      """Check if ship passes spaceyard capability filter."""
      show_has_yard = filter_state.get('show_has_spaceyard', True)
      show_no_yard = filter_state.get('show_no_spaceyard', True)

      if show_has_yard and show_no_yard:
          return True

      # Late import to avoid circular dependency
      from game.strategy.data.fleet_capability_calculator import FleetCapabilityCalculator
      has_yard = FleetCapabilityCalculator.ship_has_spaceyard(ship)
      return _passes_binary_filter(filter_state, 'show_has_spaceyard', 'show_no_spaceyard', has_yard)
  ```
- [ ] Run tests to verify no regressions

### 2.5 Extract Cargo Filter Helper
- [ ] Add `_passes_cargo_filter` function
  ```python
  def _passes_cargo_filter(ship: 'ShipInstance', filter_state: Dict[str, bool]) -> bool:
      """Check if ship passes cargo filter."""
      show_has_cargo = filter_state.get('show_has_cargo', True)
      show_no_cargo = filter_state.get('show_no_cargo', True)

      if show_has_cargo and show_no_cargo:
          return True

      has_cargo = bool(ship.cargo_contents) and sum(ship.cargo_contents.values()) > 0
      return _passes_binary_filter(filter_state, 'show_has_cargo', 'show_no_cargo', has_cargo)
  ```
- [ ] Run tests to verify no regressions

### 2.6 Extract Special Capability Filter Helper
- [ ] Add `_passes_special_capability_filters` function
  ```python
  def _passes_special_capability_filters(ship: 'ShipInstance', filter_state: Dict[str, bool]) -> bool:
      """Check if ship passes all special capability filters."""
      for col_id, ability_name in SPECIAL_CAPABILITY_COLUMNS.items():
          show_has = filter_state.get(f'show_{col_id}', True)
          no_key = col_id.replace('can_', 'no_', 1)
          show_not = filter_state.get(f'show_{no_key}', True)

          if show_has and show_not:
              continue

          # Late import to avoid circular dependency
          from game.strategy.data.fleet_capability_calculator import FleetCapabilityCalculator
          has_ability = FleetCapabilityCalculator.ship_has_ability(ship, ability_name)
          if not _passes_binary_filter(filter_state, f'show_{col_id}', f'show_{no_key}', has_ability):
              return False
      return True
  ```
- [ ] Run tests to verify no regressions

### 2.7 Extract Status Filter Helper
- [ ] Add `_passes_status_filter` function
  ```python
  def _passes_status_filter(ship: 'ShipInstance', filter_state: Dict[str, bool]) -> bool:
      """
      Check if ship passes status filter.

      CRITICAL: Order matters - destroyed > derelict > damaged > undamaged
      """
      category = _get_status_category(ship)
      filter_key = f'show_{category}'
      return filter_state.get(filter_key, True)
  ```
- [ ] Run tests to verify no regressions

### 2.8 Verification
- [ ] Run targeted tests: `pytest tests/unit/ui/screens/test_fleet_report_filters.py -v`
- [ ] All tests pass
- [ ] Run full test suite: `pytest tests/ -n 12`

## Completion Criteria
- All 7 helper functions added
- All tests still pass
- Ready for Phase 3
