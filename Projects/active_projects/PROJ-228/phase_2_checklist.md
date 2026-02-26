# Phase 2: Extract Helpers

> **Goal:** Extract helper functions to reduce CC from 36 to below 20.

## Prerequisites
- [ ] Phase 1 complete (test fortification)
- [ ] Read `design.md` for refactoring strategy
- [ ] Read current function: `game/ui/screens/fleet_report_filters.py:124-222`

## Tasks

### 2.1 Extract `_passes_binary_filter()` Helper
**File:** `game/ui/screens/fleet_report_filters.py`
**Location:** Add before `filter_ships` function (around line 120)

- [ ] Add helper function:
  ```python
  def _passes_binary_filter(has_property: bool, show_has: bool, show_not: bool) -> bool:
      """Check if item passes a binary has/not-has filter.

      Returns True if item should be included, False if excluded.
      """
      if has_property and not show_has:
          return False
      if not has_property and not show_not:
          return False
      return True
  ```
- [ ] Run: `pytest tests/unit/ui/screens/test_fleet_report_filters.py -v`

### 2.2 Extract `_passes_warp_filter()` Helper
**File:** `game/ui/screens/fleet_report_filters.py`

- [ ] Add helper function:
  ```python
  def _passes_warp_filter(ship: 'ShipInstance', filter_state: Dict[str, bool]) -> bool:
      """Check if ship passes warp capability filter."""
      show_warp = filter_state.get('show_warp_capable', True)
      show_not_warp = filter_state.get('show_not_warp_capable', True)
      if show_warp and show_not_warp:
          return True  # Filter not active
      is_warp_capable = ShipStatsCalculator.has_warp_capability(ship)
      return _passes_binary_filter(is_warp_capable, show_warp, show_not_warp)
  ```
- [ ] Update `filter_ships` lines 143-153 to use helper:
  ```python
  if not _passes_warp_filter(ship, filter_state):
      continue
  ```
- [ ] Run: `pytest tests/unit/ui/screens/test_fleet_report_filters.py -v`

### 2.3 Extract `_passes_spaceyard_filter()` Helper
**File:** `game/ui/screens/fleet_report_filters.py`

- [ ] Add helper function (include late import inside):
  ```python
  def _passes_spaceyard_filter(ship: 'ShipInstance', filter_state: Dict[str, bool]) -> bool:
      """Check if ship passes spaceyard filter."""
      show_has = filter_state.get('show_has_spaceyard', True)
      show_not = filter_state.get('show_no_spaceyard', True)
      if show_has and show_not:
          return True
      from game.strategy.data.fleet_capability_calculator import FleetCapabilityCalculator
      has_yard = FleetCapabilityCalculator.ship_has_spaceyard(ship)
      return _passes_binary_filter(has_yard, show_has, show_not)
  ```
- [ ] Update `filter_ships` lines 155-164 to use helper
- [ ] Run: `pytest tests/unit/ui/screens/test_fleet_report_filters.py -v`

### 2.4 Extract `_passes_cargo_filter()` Helper
**File:** `game/ui/screens/fleet_report_filters.py`

- [ ] Add helper function:
  ```python
  def _passes_cargo_filter(ship: 'ShipInstance', filter_state: Dict[str, bool]) -> bool:
      """Check if ship passes cargo filter."""
      show_has = filter_state.get('show_has_cargo', True)
      show_not = filter_state.get('show_no_cargo', True)
      if show_has and show_not:
          return True
      has_cargo = bool(ship.cargo_contents) and sum(ship.cargo_contents.values()) > 0
      return _passes_binary_filter(has_cargo, show_has, show_not)
  ```
- [ ] Update `filter_ships` lines 166-174 to use helper
- [ ] Run: `pytest tests/unit/ui/screens/test_fleet_report_filters.py -v`

### 2.5 Extract `_passes_special_capability_filters()` Helper
**File:** `game/ui/screens/fleet_report_filters.py`

- [ ] Add helper function (eliminates `_skip` flag pattern):
  ```python
  def _passes_special_capability_filters(ship: 'ShipInstance', filter_state: Dict[str, bool]) -> bool:
      """Check if ship passes all special capability filters."""
      from game.strategy.data.fleet_capability_calculator import FleetCapabilityCalculator

      for col_id, ability_name in SPECIAL_CAPABILITY_COLUMNS.items():
          show_has = filter_state.get(f'show_{col_id}', True)
          no_key = col_id.replace('can_', 'no_', 1)
          show_not = filter_state.get(f'show_{no_key}', True)

          if show_has and show_not:
              continue  # Filter not active for this capability

          has_ability = FleetCapabilityCalculator.ship_has_ability(ship, ability_name)
          if not _passes_binary_filter(has_ability, show_has, show_not):
              return False
      return True
  ```
- [ ] Update `filter_ships` lines 176-194 to use helper:
  ```python
  if not _passes_special_capability_filters(ship, filter_state):
      continue
  ```
- [ ] Run: `pytest tests/unit/ui/screens/test_fleet_report_filters.py -v`

### 2.6 Extract `_get_ship_status()` Helper
**File:** `game/ui/screens/fleet_report_filters.py`

- [ ] Add helper function:
  ```python
  def _get_ship_status(ship: 'ShipInstance') -> str:
      """Determine ship's status category for filtering.

      Returns one of: 'destroyed', 'derelict', 'damaged', 'undamaged'
      Priority order: destroyed > derelict > damaged > undamaged
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

### 2.7 Simplify Status Filter Logic
**File:** `game/ui/screens/fleet_report_filters.py`

- [ ] Replace lines 196-220 with simplified logic:
  ```python
  # Status filter (using priority: destroyed > derelict > damaged > undamaged)
  status = _get_ship_status(ship)
  if not filter_state.get(f'show_{status}', True):
      continue
  result.append(ship)
  ```
- [ ] Run: `pytest tests/unit/ui/screens/test_fleet_report_filters.py -v`

### 2.8 Verify Complexity Reduction
- [ ] Run: `python -m radon cc game/ui/screens/fleet_report_filters.py -s`
- [ ] Verify `filter_ships` CC is below 20
- [ ] If CC > 20, identify remaining complexity and extract more helpers

## Completion Criteria
- [ ] 7 helper functions extracted
- [ ] `filter_ships` CC below 20
- [ ] All tests pass
- [ ] Commit: `[PROJ-228] Phase 2: Extract helpers for filter_ships - CC reduced`
