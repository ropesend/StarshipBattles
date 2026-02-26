# Phase 2: Extract Helpers

**Goal:** Extract helper functions to reduce complexity and eliminate duplication.

**File:** `game/ui/screens/fleet_report_filters.py`

## Prerequisites
- [ ] Phase 1 complete (edge case tests added)
- [ ] All tests passing

## Tasks

### 2.1 Extract `_passes_binary_filter()` helper
- [ ] Add helper function before `filter_ships` (around line 120):
  ```python
  def _passes_binary_filter(has_capability: bool, show_has: bool, show_not_has: bool) -> bool:
      """Return True if ship passes a binary (has/doesn't have) capability filter."""
      if has_capability:
          return show_has
      return show_not_has
  ```
- [ ] Run: `pytest tests/unit/ui/screens/test_fleet_report_filters.py -v`

### 2.2 Extract `_get_ship_status()` helper
- [ ] Add helper function:
  ```python
  def _get_ship_status(ship: ShipInstance) -> str:
      """Return status category for filtering: 'destroyed', 'derelict', 'damaged', or 'undamaged'."""
      if not ship.is_alive:
          return 'destroyed'
      if ship.is_derelict:
          return 'derelict'
      if ship.is_damaged():
          return 'damaged'
      return 'undamaged'
  ```
- [ ] Run: `pytest tests/unit/ui/screens/test_fleet_report_filters.py -v`

### 2.3 Extract `_passes_status_filter()` helper
- [ ] Add helper function:
  ```python
  def _passes_status_filter(ship: ShipInstance, filter_state: Dict[str, bool]) -> bool:
      """Return True if ship passes the status filter."""
      status = _get_ship_status(ship)
      return filter_state.get(f'show_{status}', True)
  ```
- [ ] Run: `pytest tests/unit/ui/screens/test_fleet_report_filters.py -v`

### 2.4 Extract `_passes_capability_filters()` helper
- [ ] Add helper function that consolidates all capability checks:
  ```python
  def _passes_capability_filters(ship: ShipInstance, filter_state: Dict[str, bool]) -> bool:
      """Return True if ship passes all capability filters (warp, spaceyard, cargo, special)."""
      # Late import to avoid circular dependency
      from game.strategy.data.fleet_capability_calculator import FleetCapabilityCalculator

      # Warp capability
      show_warp = filter_state.get('show_warp_capable', True)
      show_not_warp = filter_state.get('show_not_warp_capable', True)
      if not (show_warp and show_not_warp):
          is_warp = ShipStatsCalculator.has_warp_capability(ship)
          if not _passes_binary_filter(is_warp, show_warp, show_not_warp):
              return False

      # Spaceyard capability
      show_yard = filter_state.get('show_has_spaceyard', True)
      show_no_yard = filter_state.get('show_no_spaceyard', True)
      if not (show_yard and show_no_yard):
          has_yard = FleetCapabilityCalculator.ship_has_spaceyard(ship)
          if not _passes_binary_filter(has_yard, show_yard, show_no_yard):
              return False

      # Cargo filter
      show_cargo = filter_state.get('show_has_cargo', True)
      show_no_cargo = filter_state.get('show_no_cargo', True)
      if not (show_cargo and show_no_cargo):
          has_cargo = bool(ship.cargo_contents) and sum(ship.cargo_contents.values()) > 0
          if not _passes_binary_filter(has_cargo, show_cargo, show_no_cargo):
              return False

      # Special capabilities
      for col_id, ability_name in SPECIAL_CAPABILITY_COLUMNS.items():
          show_has = filter_state.get(f'show_{col_id}', True)
          no_key = col_id.replace('can_', 'no_', 1)
          show_not = filter_state.get(f'show_{no_key}', True)
          if not (show_has and show_not):
              has_ability = FleetCapabilityCalculator.ship_has_ability(ship, ability_name)
              if not _passes_binary_filter(has_ability, show_has, show_not):
                  return False

      return True
  ```
- [ ] Run: `pytest tests/unit/ui/screens/test_fleet_report_filters.py -v`

### 2.5 Verify all tests still pass
- [ ] Run full test suite: `pytest tests/unit/ui/screens/test_fleet_report_filters.py -v`
- [ ] Run broader tests: `pytest tests/unit/ui/ -v --tb=short`

## Completion Criteria
- [ ] 4 helper functions added
- [ ] All tests pass
- [ ] No behavioral changes (helpers not yet used by main function)
- [ ] Helpers have docstrings and type hints

## Test Commands
```bash
# Quick check after each helper
pytest tests/unit/ui/screens/test_fleet_report_filters.py -v

# Full UI test suite
pytest tests/unit/ui/ -v --tb=short
```
