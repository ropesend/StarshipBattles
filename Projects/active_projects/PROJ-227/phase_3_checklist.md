# Phase 3: Simplify Main Function

> **Goal:** Refactor `filter_ships` to use the extracted helpers.

## Pre-Phase Checklist
- [ ] Phase 2 complete (all helpers extracted and tests passing)
- [ ] Read current `filter_ships` function (lines 124-222)
- [ ] Run baseline tests: `pytest tests/unit/ui/screens/test_fleet_report_filters.py -v`

## Tasks

### 3.1 Replace Warp Filter Block
**File:** `game/ui/screens/fleet_report_filters.py`
**Location:** Lines 143-153 in `filter_ships`

- [ ] Replace the warp filter block:
  ```python
  # OLD (lines 143-153):
  show_warp = filter_state.get('show_warp_capable', True)
  show_not_warp = filter_state.get('show_not_warp_capable', True)
  if not show_warp or not show_not_warp:
      is_warp_capable = ShipStatsCalculator.has_warp_capability(ship)
      if is_warp_capable and not show_warp:
          continue
      if not is_warp_capable and not show_not_warp:
          continue

  # NEW:
  if not _passes_warp_filter(ship, filter_state):
      continue
  ```

- [ ] Run tests: `pytest tests/unit/ui/screens/test_fleet_report_filters.py::TestFilterShipsWarp -v`

### 3.2 Replace Spaceyard Filter Block
**File:** `game/ui/screens/fleet_report_filters.py`
**Location:** Lines 155-164

- [ ] Replace the spaceyard filter block:
  ```python
  # OLD (lines 155-164):
  show_has_yard = filter_state.get('show_has_spaceyard', True)
  show_no_yard = filter_state.get('show_no_spaceyard', True)
  if not show_has_yard or not show_no_yard:
      from game.strategy.data.fleet_capability_calculator import FleetCapabilityCalculator
      has_yard = FleetCapabilityCalculator.ship_has_spaceyard(ship)
      if has_yard and not show_has_yard:
          continue
      if not has_yard and not show_no_yard:
          continue

  # NEW:
  if not _passes_spaceyard_filter(ship, filter_state):
      continue
  ```

- [ ] Run tests: `pytest tests/unit/ui/screens/test_fleet_report_filters.py::TestFilterShipsSpaceyard -v`

### 3.3 Replace Cargo Filter Block
**File:** `game/ui/screens/fleet_report_filters.py`
**Location:** Lines 166-174

- [ ] Replace the cargo filter block:
  ```python
  # OLD (lines 166-174):
  show_has_cargo = filter_state.get('show_has_cargo', True)
  show_no_cargo = filter_state.get('show_no_cargo', True)
  if not show_has_cargo or not show_no_cargo:
      has_cargo = bool(ship.cargo_contents) and sum(ship.cargo_contents.values()) > 0
      if has_cargo and not show_has_cargo:
          continue
      if not has_cargo and not show_no_cargo:
          continue

  # NEW:
  if not _passes_cargo_filter(ship, filter_state):
      continue
  ```

- [ ] Run tests: `pytest tests/unit/ui/screens/test_fleet_report_filters.py::TestFilterShipsCargo -v`

### 3.4 Replace Special Capabilities Loop
**File:** `game/ui/screens/fleet_report_filters.py`
**Location:** Lines 176-194

- [ ] Replace the special capabilities loop:
  ```python
  # OLD (lines 176-194):
  _skip = False
  for col_id, ability_name in SPECIAL_CAPABILITY_COLUMNS.items():
      show_has = filter_state.get(f'show_{col_id}', True)
      no_key = col_id.replace('can_', 'no_', 1)
      show_not = filter_state.get(f'show_{no_key}', True)
      if not show_has or not show_not:
          from game.strategy.data.fleet_capability_calculator import FleetCapabilityCalculator
          has_ability = FleetCapabilityCalculator.ship_has_ability(ship, ability_name)
          if has_ability and not show_has:
              _skip = True
              break
          if not has_ability and not show_not:
              _skip = True
              break
  if _skip:
      continue

  # NEW:
  if not _passes_capability_filters(ship, filter_state):
      continue
  ```

- [ ] Run tests: `pytest tests/unit/ui/screens/test_fleet_report_filters.py::TestSpecialCapabilityFilter -v`

### 3.5 Replace Status Cascade
**File:** `game/ui/screens/fleet_report_filters.py`
**Location:** Lines 196-220

- [ ] Replace the status cascade:
  ```python
  # OLD (lines 196-220):
  if not ship.is_alive:
      if not filter_state.get('show_destroyed', True):
          continue
      result.append(ship)
      continue

  if ship.is_derelict:
      if not filter_state.get('show_derelict', True):
          continue
      result.append(ship)
      continue

  if ship.is_damaged():
      if not filter_state.get('show_damaged', True):
          continue
      result.append(ship)
      continue

  if not filter_state.get('show_undamaged', True):
      continue
  result.append(ship)

  # NEW:
  status = _get_ship_status(ship)
  if not filter_state.get(f'show_{status}', True):
      continue
  result.append(ship)
  ```

- [ ] Run tests: `pytest tests/unit/ui/screens/test_fleet_report_filters.py::TestFilterShips -v`

### 3.6 Verify Complete Refactored Function
**File:** `game/ui/screens/fleet_report_filters.py`

- [ ] Verify the final `filter_ships` function looks like:
  ```python
  def filter_ships(ships: List[ShipInstance], filter_state: Dict[str, bool]) -> List[ShipInstance]:
      """
      Filter ships based on status filter state.

      Args:
          ships: List of ShipInstance objects
          filter_state: Dict with filter keys (show_damaged, show_warp_capable, etc.)

      Returns:
          Filtered list of ships
      """
      result = []
      for ship in ships:
          # Capability filters
          if not _passes_warp_filter(ship, filter_state):
              continue
          if not _passes_spaceyard_filter(ship, filter_state):
              continue
          if not _passes_cargo_filter(ship, filter_state):
              continue
          if not _passes_capability_filters(ship, filter_state):
              continue

          # Status filter
          status = _get_ship_status(ship)
          if not filter_state.get(f'show_{status}', True):
              continue

          result.append(ship)

      return result
  ```

- [ ] Run all filter tests: `pytest tests/unit/ui/screens/test_fleet_report_filters.py -v`

## Post-Phase Checklist
- [ ] All inline filter code replaced with helper calls
- [ ] All tests passing
- [ ] Run integration tests: `pytest tests/unit/ui/test_fleet_list_view_model.py -v`
- [ ] Run full test suite: `pytest tests/ -n 12`
- [ ] Commit changes: `git add -A && git commit -m "[PROJ-227] Phase 3: Simplify filter_ships using extracted helpers"`

## Verification
```bash
pytest tests/unit/ui/screens/test_fleet_report_filters.py -v
pytest tests/unit/ui/test_fleet_list_view_model.py -v
```

Expected: All tests pass. `filter_ships` is now ~20 lines instead of ~99.
