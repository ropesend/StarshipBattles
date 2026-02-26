# Phase 2: Extract Filter Helpers

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-242 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Extract helper functions for each filter category while preserving behavior

---

## Tasks

### Task 2.1: Extract Generic Boolean Filter Helper [Simple]
**File:** `game/ui/screens/fleet_report_filters.py`
**Tests:** `pytest tests/unit/ui/screens/test_fleet_report_filters.py -v`

Extract the repeated has/doesn't-have filter pattern:
- [ ] Add function `_passes_boolean_filter(has_capability: bool, show_has: bool, show_not: bool) -> bool`
- [ ] Implementation:
  ```python
  def _passes_boolean_filter(has_capability: bool, show_has: bool, show_not: bool) -> bool:
      """Check if a ship passes a binary (has/lacks) capability filter."""
      if show_has and show_not:
          return True  # No filtering needed
      if has_capability:
          return show_has
      return show_not
  ```
- [ ] Add above the `filter_ships` function (around line 120)
- [ ] Run tests - all should pass (function not yet used)

**Notes:** This helper will be used by warp, spaceyard, cargo, and special ability filters

---

### Task 2.2: Extract Warp Filter [Simple]
**File:** `game/ui/screens/fleet_report_filters.py`
**Tests:** `pytest tests/unit/ui/screens/test_fleet_report_filters.py::TestFilterShipsWarp -v`

Extract warp capability filter to helper function:
- [ ] Add function `_passes_warp_filter(ship, filter_state) -> bool`
- [ ] Implementation:
  ```python
  def _passes_warp_filter(ship, filter_state: Dict[str, bool]) -> bool:
      """Check if ship passes warp capability filter."""
      show_warp = filter_state.get('show_warp_capable', True)
      show_not_warp = filter_state.get('show_not_warp_capable', True)
      if show_warp and show_not_warp:
          return True
      is_warp_capable = ShipStatsCalculator.has_warp_capability(ship)
      return _passes_boolean_filter(is_warp_capable, show_warp, show_not_warp)
  ```
- [ ] Replace inline warp filter (lines 144-153) with call to `_passes_warp_filter`
- [ ] Update main loop: `if not _passes_warp_filter(ship, filter_state): continue`
- [ ] Run warp filter tests - all should pass

**Notes:** First filter extraction - establishes pattern

---

### Task 2.3: Extract Spaceyard Filter [Simple]
**File:** `game/ui/screens/fleet_report_filters.py`
**Tests:** `pytest tests/unit/ui/screens/test_fleet_report_filters.py::TestFilterShipsSpaceyard -v`

Extract spaceyard capability filter:
- [ ] Add function `_passes_spaceyard_filter(ship, filter_state) -> bool`
- [ ] Implementation (keep late import inside function):
  ```python
  def _passes_spaceyard_filter(ship, filter_state: Dict[str, bool]) -> bool:
      """Check if ship passes spaceyard capability filter."""
      show_has_yard = filter_state.get('show_has_spaceyard', True)
      show_no_yard = filter_state.get('show_no_spaceyard', True)
      if show_has_yard and show_no_yard:
          return True
      from game.strategy.data.fleet_capability_calculator import FleetCapabilityCalculator
      has_yard = FleetCapabilityCalculator.ship_has_spaceyard(ship)
      return _passes_boolean_filter(has_yard, show_has_yard, show_no_yard)
  ```
- [ ] Replace inline spaceyard filter (lines 156-164) with call
- [ ] Run spaceyard filter tests - all should pass

**Notes:** Keep late import to avoid circular dependency

---

### Task 2.4: Extract Cargo Filter [Simple]
**File:** `game/ui/screens/fleet_report_filters.py`
**Tests:** `pytest tests/unit/ui/screens/test_fleet_report_filters.py::TestFilterShipsCargo -v`

Extract cargo filter:
- [ ] Add function `_passes_cargo_filter(ship, filter_state) -> bool`
- [ ] Implementation:
  ```python
  def _passes_cargo_filter(ship, filter_state: Dict[str, bool]) -> bool:
      """Check if ship passes cargo filter."""
      show_has_cargo = filter_state.get('show_has_cargo', True)
      show_no_cargo = filter_state.get('show_no_cargo', True)
      if show_has_cargo and show_no_cargo:
          return True
      has_cargo = bool(ship.cargo_contents) and sum(ship.cargo_contents.values()) > 0
      return _passes_boolean_filter(has_cargo, show_has_cargo, show_no_cargo)
  ```
- [ ] Replace inline cargo filter (lines 167-174) with call
- [ ] Run cargo filter tests - all should pass

**Notes:** Preserve exact cargo detection logic (zero values = no cargo)

---

### Task 2.5: Extract Special Ability Filters [Medium]
**File:** `game/ui/screens/fleet_report_filters.py`
**Tests:** `pytest tests/unit/ui/screens/test_fleet_report_filters.py::TestSpecialCapabilityFilter -v`

Extract special ability filter loop:
- [ ] Add function `_passes_special_ability_filters(ship, filter_state) -> bool`
- [ ] Implementation (keep late import):
  ```python
  def _passes_special_ability_filters(ship, filter_state: Dict[str, bool]) -> bool:
      """Check if ship passes all special ability filters."""
      for col_id, ability_name in SPECIAL_CAPABILITY_COLUMNS.items():
          show_has = filter_state.get(f'show_{col_id}', True)
          no_key = col_id.replace('can_', 'no_', 1)
          show_not = filter_state.get(f'show_{no_key}', True)
          if show_has and show_not:
              continue  # No filtering for this ability
          from game.strategy.data.fleet_capability_calculator import FleetCapabilityCalculator
          has_ability = FleetCapabilityCalculator.ship_has_ability(ship, ability_name)
          if not _passes_boolean_filter(has_ability, show_has, show_not):
              return False
      return True
  ```
- [ ] Replace inline loop (lines 176-194) with call
- [ ] Run special ability tests - all should pass

**Notes:** Converts flag+break pattern to early return pattern

---

### Task 2.6: Extract Status Classification [Simple]
**File:** `game/ui/screens/fleet_report_filters.py`
**Tests:** `pytest tests/unit/ui/screens/test_fleet_report_filters.py::TestFilterShips -v`

Extract ship status classification:
- [ ] Add constant at module level:
  ```python
  _STATUS_FILTER_KEYS = {
      'destroyed': 'show_destroyed',
      'derelict': 'show_derelict',
      'damaged': 'show_damaged',
      'undamaged': 'show_undamaged',
  }
  ```
- [ ] Add function `_get_ship_status(ship) -> str`
- [ ] Implementation:
  ```python
  def _get_ship_status(ship) -> str:
      """Classify ship into one of four mutually exclusive status categories."""
      if not ship.is_alive:
          return 'destroyed'
      if ship.is_derelict:
          return 'derelict'
      if ship.is_damaged():
          return 'damaged'
      return 'undamaged'
  ```
- [ ] Run status filter tests - all should pass (function not yet used)

**Notes:** Preparation for Task 2.7

---

### Task 2.7: Extract Status Filter [Medium]
**File:** `game/ui/screens/fleet_report_filters.py`
**Tests:** `pytest tests/unit/ui/screens/test_fleet_report_filters.py::TestFilterShips -v`

Extract status filter using lookup pattern:
- [ ] Add function `_passes_status_filter(ship, filter_state) -> bool`
- [ ] Implementation:
  ```python
  def _passes_status_filter(ship, filter_state: Dict[str, bool]) -> bool:
      """Check if ship passes status filter based on its classification."""
      status = _get_ship_status(ship)
      filter_key = _STATUS_FILTER_KEYS[status]
      return filter_state.get(filter_key, True)
  ```
- [ ] Replace inline status cascade (lines 196-220) with:
  ```python
  if not _passes_status_filter(ship, filter_state):
      continue
  result.append(ship)
  ```
- [ ] Run all filter tests - all should pass

**Notes:** This is the most significant change - eliminates fragile cascade pattern

---

### Task 2.8: Run Full Test Suite [Simple]
**Tests:** `pytest tests/ -n 12`

Verify no regressions after helper extractions:
- [ ] Run full test suite
- [ ] All tests pass
- [ ] No behavior changes

**Notes:** Sanity check before Phase 3

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] 7 helper functions extracted
- [ ] All tests still pass
- [ ] Main function still works (just with helper calls)
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 3
