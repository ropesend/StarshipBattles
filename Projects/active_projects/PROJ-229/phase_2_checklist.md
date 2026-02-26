# Phase 2: Extract Helpers

**Goal:** Extract predicate helper functions from `filter_ships` without changing behavior.

**File:** `game/ui/screens/fleet_report_filters.py`

---

## Pre-Phase
- [ ] Verify all tests pass: `pytest tests/unit/ui/screens/test_fleet_report_filters.py -v`
- [ ] Read current `filter_ships` implementation (lines 124-222)

## Tasks

### 2.1 Extract Boolean Filter Helper
**Location:** Add above `filter_ships` function (around line 120)

- [ ] Add `_passes_boolean_filter` function:
  ```python
  def _passes_boolean_filter(has_attribute: bool, show_has: bool, show_not: bool) -> bool:
      """
      Generic boolean pair filter logic.

      Returns True if the item should be included based on:
      - has_attribute: Whether the item has the attribute being filtered
      - show_has: Filter state for showing items WITH the attribute
      - show_not: Filter state for showing items WITHOUT the attribute
      """
      if show_has and show_not:
          return True  # No filtering needed
      if has_attribute and not show_has:
          return False
      if not has_attribute and not show_not:
          return False
      return True
  ```

- [ ] Run tests: `pytest tests/unit/ui/screens/test_fleet_report_filters.py -v`

### 2.2 Extract Status Helper
**Location:** Add after `_passes_boolean_filter`

- [ ] Add `_get_ship_status` function:
  ```python
  def _get_ship_status(ship: 'ShipInstance') -> str:
      """
      Determine ship's status category.

      Returns one of: 'destroyed', 'derelict', 'damaged', 'undamaged'

      IMPORTANT: Status is mutually exclusive - hierarchy is:
      destroyed > derelict > damaged > undamaged
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

### 2.3 Extract Warp Filter Helper
**Location:** Add after `_get_ship_status`

- [ ] Add `_passes_warp_filter` function:
  ```python
  def _passes_warp_filter(ship: 'ShipInstance', filter_state: Dict[str, bool]) -> bool:
      """Check if ship passes warp capability filters."""
      show_warp = filter_state.get('show_warp_capable', True)
      show_not_warp = filter_state.get('show_not_warp_capable', True)

      if show_warp and show_not_warp:
          return True

      is_warp_capable = ShipStatsCalculator.has_warp_capability(ship)
      return _passes_boolean_filter(is_warp_capable, show_warp, show_not_warp)
  ```

- [ ] Run tests: `pytest tests/unit/ui/screens/test_fleet_report_filters.py -v`

### 2.4 Extract Spaceyard Filter Helper
**Location:** Add after `_passes_warp_filter`

- [ ] Add `_passes_spaceyard_filter` function:
  ```python
  def _passes_spaceyard_filter(ship: 'ShipInstance', filter_state: Dict[str, bool]) -> bool:
      """Check if ship passes spaceyard capability filters."""
      show_has_yard = filter_state.get('show_has_spaceyard', True)
      show_no_yard = filter_state.get('show_no_spaceyard', True)

      if show_has_yard and show_no_yard:
          return True

      # INTENTIONAL LATE IMPORT: Avoid circular import
      from game.strategy.data.fleet_capability_calculator import FleetCapabilityCalculator
      has_yard = FleetCapabilityCalculator.ship_has_spaceyard(ship)
      return _passes_boolean_filter(has_yard, show_has_yard, show_no_yard)
  ```

- [ ] Run tests: `pytest tests/unit/ui/screens/test_fleet_report_filters.py -v`

### 2.5 Extract Cargo Filter Helper
**Location:** Add after `_passes_spaceyard_filter`

- [ ] Add `_passes_cargo_filter` function:
  ```python
  def _passes_cargo_filter(ship: 'ShipInstance', filter_state: Dict[str, bool]) -> bool:
      """Check if ship passes cargo presence filters."""
      show_has_cargo = filter_state.get('show_has_cargo', True)
      show_no_cargo = filter_state.get('show_no_cargo', True)

      if show_has_cargo and show_no_cargo:
          return True

      has_cargo = bool(ship.cargo_contents) and sum(ship.cargo_contents.values()) > 0
      return _passes_boolean_filter(has_cargo, show_has_cargo, show_no_cargo)
  ```

- [ ] Run tests: `pytest tests/unit/ui/screens/test_fleet_report_filters.py -v`

### 2.6 Extract Special Ability Filter Helper
**Location:** Add after `_passes_cargo_filter`

- [ ] Add `_passes_special_ability_filters` function:
  ```python
  def _passes_special_ability_filters(ship: 'ShipInstance', filter_state: Dict[str, bool]) -> bool:
      """Check if ship passes all special ability filters."""
      for col_id, ability_name in SPECIAL_CAPABILITY_COLUMNS.items():
          # Derive filter keys: 'can_destroy_planet' -> show_can_destroy_planet / show_no_destroy_planet
          show_has = filter_state.get(f'show_{col_id}', True)
          no_key = col_id.replace('can_', 'no_', 1)
          show_not = filter_state.get(f'show_{no_key}', True)

          if show_has and show_not:
              continue

          # INTENTIONAL LATE IMPORT: Avoid circular import
          from game.strategy.data.fleet_capability_calculator import FleetCapabilityCalculator
          has_ability = FleetCapabilityCalculator.ship_has_ability(ship, ability_name)

          if not _passes_boolean_filter(has_ability, show_has, show_not):
              return False

      return True
  ```

- [ ] Run tests: `pytest tests/unit/ui/screens/test_fleet_report_filters.py -v`

### 2.7 Extract Status Filter Helper
**Location:** Add after `_passes_special_ability_filters`

- [ ] Add `_passes_status_filter` function:
  ```python
  def _passes_status_filter(ship: 'ShipInstance', filter_state: Dict[str, bool]) -> bool:
      """Check if ship passes status filters based on its determined status."""
      status = _get_ship_status(ship)
      return filter_state.get(f'show_{status}', True)
  ```

- [ ] Run tests: `pytest tests/unit/ui/screens/test_fleet_report_filters.py -v`

## Post-Phase
- [ ] All 7 helper functions added
- [ ] All tests still pass
- [ ] No behavioral changes introduced
- [ ] Update plan.md Current State
- [ ] Commit: `[PROJ-229] Phase 2: Extract helper functions for filter_ships - Automated`

## Test Commands
```bash
# Quick check after each helper
pytest tests/unit/ui/screens/test_fleet_report_filters.py -v

# Full suite check
pytest tests/ -n 12
```
