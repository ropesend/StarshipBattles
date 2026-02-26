# Phase 2: Extract Helper Functions

**Goal:** Extract predicate helper functions one at a time, running tests after each extraction.

**File:** `game/ui/screens/fleet_report_filters.py`

## Tasks

### 2.1 Extract `_passes_binary_filter()` Helper
- [ ] Add helper function before `filter_ships` (around line 120):
  ```python
  def _passes_binary_filter(has_capability: bool, show_has: bool, show_not_has: bool) -> bool:
      """Return True if ship passes a binary (has/doesn't-have) filter."""
      if show_has and show_not_has:
          return True  # Both enabled = no filtering
      if has_capability:
          return show_has
      return show_not_has
  ```
- [ ] Run tests: `pytest tests/unit/ui/screens/test_fleet_report_filters.py -v`

### 2.2 Extract `_passes_warp_filter()` Helper
- [ ] Add helper function:
  ```python
  def _passes_warp_filter(ship: "ShipInstance", filter_state: Dict[str, bool]) -> bool:
      """Check if ship passes warp capability filter."""
      show_warp = filter_state.get('show_warp_capable', True)
      show_not_warp = filter_state.get('show_not_warp_capable', True)
      if show_warp and show_not_warp:
          return True
      is_warp_capable = ShipStatsCalculator.has_warp_capability(ship)
      return _passes_binary_filter(is_warp_capable, show_warp, show_not_warp)
  ```
- [ ] Replace lines 144-153 in `filter_ships` with:
  ```python
  if not _passes_warp_filter(ship, filter_state):
      continue
  ```
- [ ] Run tests: `pytest tests/unit/ui/screens/test_fleet_report_filters.py -v`

### 2.3 Extract `_passes_spaceyard_filter()` Helper
- [ ] Add helper function (keep lazy import inside):
  ```python
  def _passes_spaceyard_filter(ship: "ShipInstance", filter_state: Dict[str, bool]) -> bool:
      """Check if ship passes spaceyard capability filter."""
      show_has_yard = filter_state.get('show_has_spaceyard', True)
      show_no_yard = filter_state.get('show_no_spaceyard', True)
      if show_has_yard and show_no_yard:
          return True
      from game.strategy.data.fleet_capability_calculator import FleetCapabilityCalculator
      has_yard = FleetCapabilityCalculator.ship_has_spaceyard(ship)
      return _passes_binary_filter(has_yard, show_has_yard, show_no_yard)
  ```
- [ ] Replace lines 155-164 in `filter_ships` with:
  ```python
  if not _passes_spaceyard_filter(ship, filter_state):
      continue
  ```
- [ ] Run tests: `pytest tests/unit/ui/screens/test_fleet_report_filters.py -v`

### 2.4 Extract `_passes_cargo_filter()` Helper
- [ ] Add helper function:
  ```python
  def _passes_cargo_filter(ship: "ShipInstance", filter_state: Dict[str, bool]) -> bool:
      """Check if ship passes cargo filter."""
      show_has_cargo = filter_state.get('show_has_cargo', True)
      show_no_cargo = filter_state.get('show_no_cargo', True)
      if show_has_cargo and show_no_cargo:
          return True
      has_cargo = bool(ship.cargo_contents) and sum(ship.cargo_contents.values()) > 0
      return _passes_binary_filter(has_cargo, show_has_cargo, show_no_cargo)
  ```
- [ ] Replace lines 166-174 in `filter_ships` with:
  ```python
  if not _passes_cargo_filter(ship, filter_state):
      continue
  ```
- [ ] Run tests: `pytest tests/unit/ui/screens/test_fleet_report_filters.py -v`

### 2.5 Extract `_passes_special_capability_filters()` Helper
- [ ] Add helper function (keep lazy import inside):
  ```python
  def _passes_special_capability_filters(ship: "ShipInstance", filter_state: Dict[str, bool]) -> bool:
      """Check if ship passes all special capability filters."""
      for col_id, ability_name in SPECIAL_CAPABILITY_COLUMNS.items():
          show_has = filter_state.get(f'show_{col_id}', True)
          no_key = col_id.replace('can_', 'no_', 1)
          show_not = filter_state.get(f'show_{no_key}', True)
          if show_has and show_not:
              continue
          from game.strategy.data.fleet_capability_calculator import FleetCapabilityCalculator
          has_ability = FleetCapabilityCalculator.ship_has_ability(ship, ability_name)
          if not _passes_binary_filter(has_ability, show_has, show_not):
              return False
      return True
  ```
- [ ] Replace lines 176-194 in `filter_ships` with:
  ```python
  if not _passes_special_capability_filters(ship, filter_state):
      continue
  ```
- [ ] Run tests: `pytest tests/unit/ui/screens/test_fleet_report_filters.py -v`

### 2.6 Extract `_passes_status_filter()` Helper
- [ ] Add helper function (PRESERVE EXACT ORDERING):
  ```python
  def _passes_status_filter(ship: "ShipInstance", filter_state: Dict[str, bool]) -> bool:
      """Check if ship passes status filter. Hierarchy: destroyed > derelict > damaged > undamaged."""
      # Destroyed ships
      if not ship.is_alive:
          return filter_state.get('show_destroyed', True)

      # Derelict ships (checked before damaged since derelict implies damaged)
      if ship.is_derelict:
          return filter_state.get('show_derelict', True)

      # Damaged ships
      if ship.is_damaged():
          return filter_state.get('show_damaged', True)

      # Undamaged (healthy) ships
      return filter_state.get('show_undamaged', True)
  ```
- [ ] Replace lines 196-220 in `filter_ships` with:
  ```python
  if not _passes_status_filter(ship, filter_state):
      continue
  result.append(ship)
  ```
- [ ] Run tests: `pytest tests/unit/ui/screens/test_fleet_report_filters.py -v`

## Completion Criteria
- [ ] 6 helper functions extracted
- [ ] All tests passing after each extraction
- [ ] No behavioral changes
