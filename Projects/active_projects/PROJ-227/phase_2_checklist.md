# Phase 2: Extract Helpers

> **Goal:** Extract repeated patterns into focused helper functions.

## Pre-Phase Checklist
- [ ] Phase 1 complete (all edge case tests passing)
- [ ] Read `game/ui/screens/fleet_report_filters.py` lines 124-222
- [ ] Run baseline tests: `pytest tests/unit/ui/screens/test_fleet_report_filters.py -v`

## Tasks

### 2.1 Extract `_passes_binary_filter` Helper
**File:** `game/ui/screens/fleet_report_filters.py`
**Location:** Add before `filter_ships` function (around line 120)

- [ ] Add the `_passes_binary_filter` function:
  ```python
  def _passes_binary_filter(
      filter_state: Dict[str, bool],
      positive_key: str,
      negative_key: str,
      has_attribute: bool
  ) -> bool:
      """Check if item passes a binary (has/lacks) filter.

      Returns True if the item should be included based on the positive/negative
      filter toggles. Preserves short-circuit optimization: if both toggles are
      enabled, returns True without checking the attribute value.
      """
      show_with = filter_state.get(positive_key, True)
      show_without = filter_state.get(negative_key, True)

      # Both enabled = pass all (short-circuit optimization)
      if show_with and show_without:
          return True

      # Check attribute against enabled filters
      if has_attribute:
          return show_with
      return show_without
  ```

- [ ] Run tests: `pytest tests/unit/ui/screens/test_fleet_report_filters.py -v`

### 2.2 Extract `_get_ship_status` Helper
**File:** `game/ui/screens/fleet_report_filters.py`
**Location:** Add after `_passes_binary_filter`

- [ ] Add the `_get_ship_status` function:
  ```python
  def _get_ship_status(ship: "ShipInstance") -> str:
      """Get the mutually exclusive status of a ship.

      Returns one of: 'destroyed', 'derelict', 'damaged', 'undamaged'.
      Priority order ensures mutual exclusivity (a destroyed ship is not
      also counted as derelict or damaged).
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

### 2.3 Extract `_passes_warp_filter` Helper
**File:** `game/ui/screens/fleet_report_filters.py`
**Location:** Add after `_get_ship_status`

- [ ] Add the `_passes_warp_filter` function:
  ```python
  def _passes_warp_filter(ship: "ShipInstance", filter_state: Dict[str, bool]) -> bool:
      """Check if ship passes the warp capability filter."""
      show_warp = filter_state.get('show_warp_capable', True)
      show_not_warp = filter_state.get('show_not_warp_capable', True)

      # Short-circuit: both enabled means no filtering needed
      if show_warp and show_not_warp:
          return True

      is_warp_capable = ShipStatsCalculator.has_warp_capability(ship)
      return _passes_binary_filter(
          filter_state, 'show_warp_capable', 'show_not_warp_capable', is_warp_capable
      )
  ```

- [ ] Run tests: `pytest tests/unit/ui/screens/test_fleet_report_filters.py -v`

### 2.4 Extract `_passes_spaceyard_filter` Helper
**File:** `game/ui/screens/fleet_report_filters.py`
**Location:** Add after `_passes_warp_filter`

- [ ] Add the `_passes_spaceyard_filter` function:
  ```python
  def _passes_spaceyard_filter(ship: "ShipInstance", filter_state: Dict[str, bool]) -> bool:
      """Check if ship passes the spaceyard capability filter."""
      show_has_yard = filter_state.get('show_has_spaceyard', True)
      show_no_yard = filter_state.get('show_no_spaceyard', True)

      if show_has_yard and show_no_yard:
          return True

      # Late import to avoid circular dependency
      from game.strategy.data.fleet_capability_calculator import FleetCapabilityCalculator
      has_yard = FleetCapabilityCalculator.ship_has_spaceyard(ship)
      return _passes_binary_filter(
          filter_state, 'show_has_spaceyard', 'show_no_spaceyard', has_yard
      )
  ```

- [ ] Run tests: `pytest tests/unit/ui/screens/test_fleet_report_filters.py -v`

### 2.5 Extract `_passes_cargo_filter` Helper
**File:** `game/ui/screens/fleet_report_filters.py`
**Location:** Add after `_passes_spaceyard_filter`

- [ ] Add the `_passes_cargo_filter` function:
  ```python
  def _passes_cargo_filter(ship: "ShipInstance", filter_state: Dict[str, bool]) -> bool:
      """Check if ship passes the cargo presence filter."""
      show_has_cargo = filter_state.get('show_has_cargo', True)
      show_no_cargo = filter_state.get('show_no_cargo', True)

      if show_has_cargo and show_no_cargo:
          return True

      has_cargo = bool(ship.cargo_contents) and sum(ship.cargo_contents.values()) > 0
      return _passes_binary_filter(
          filter_state, 'show_has_cargo', 'show_no_cargo', has_cargo
      )
  ```

- [ ] Run tests: `pytest tests/unit/ui/screens/test_fleet_report_filters.py -v`

### 2.6 Extract `_passes_capability_filters` Helper
**File:** `game/ui/screens/fleet_report_filters.py`
**Location:** Add after `_passes_cargo_filter`

- [ ] Add the `_passes_capability_filters` function:
  ```python
  def _passes_capability_filters(ship: "ShipInstance", filter_state: Dict[str, bool]) -> bool:
      """Check if ship passes all special capability filters.

      Iterates through SPECIAL_CAPABILITY_COLUMNS and checks each ability filter.
      Returns False immediately if any filter rejects the ship.
      """
      from game.strategy.data.fleet_capability_calculator import FleetCapabilityCalculator

      for col_id, ability_name in SPECIAL_CAPABILITY_COLUMNS.items():
          show_has = filter_state.get(f'show_{col_id}', True)
          no_key = col_id.replace('can_', 'no_', 1)
          show_not = filter_state.get(f'show_{no_key}', True)

          if show_has and show_not:
              continue

          has_ability = FleetCapabilityCalculator.ship_has_ability(ship, ability_name)
          if not _passes_binary_filter(filter_state, f'show_{col_id}', f'show_{no_key}', has_ability):
              return False

      return True
  ```

- [ ] Run tests: `pytest tests/unit/ui/screens/test_fleet_report_filters.py -v`

## Post-Phase Checklist
- [ ] All 6 helper functions added
- [ ] All existing tests still passing
- [ ] Run full test suite: `pytest tests/ -n 12`
- [ ] Commit changes: `git add -A && git commit -m "[PROJ-227] Phase 2: Extract helper functions for filter_ships"`

## Verification
```bash
pytest tests/unit/ui/screens/test_fleet_report_filters.py -v
pytest tests/unit/ui/test_fleet_list_view_model.py -v
```

Expected: All tests pass. Helper functions are defined but not yet used by `filter_ships`.
