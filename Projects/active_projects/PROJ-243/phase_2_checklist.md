# Phase 2: Extract Binary Filter Helper

**Objective:** Create `_passes_binary_filter()` helper function and apply it to warp, spaceyard, cargo, and special capability filters.

**Expected CC Reduction:** From 36 to ~20

---

## Prerequisites
- [ ] Phase 1 complete (all edge case tests passing)
- [ ] Run baseline tests: `pytest tests/unit/ui/screens/test_fleet_report_filters.py -v`

---

## Tasks

### 2.1 Create Binary Filter Helper

**File:** `game/ui/screens/fleet_report_filters.py`
**Location:** Add BEFORE `filter_ships` function (around line 124)

- [ ] **Add `_passes_binary_filter()` function**
  ```python
  def _passes_binary_filter(
      ship: ShipInstance,
      filter_state: Dict[str, bool],
      has_key: str,
      not_key: str,
      capability_check: Callable[[ShipInstance], bool]
  ) -> bool:
      """Check if ship passes a binary has/has-not capability filter.

      Args:
          ship: The ship to check
          filter_state: Dictionary of filter flags
          has_key: Key for "show ships WITH capability" (e.g., 'show_warp_capable')
          not_key: Key for "show ships WITHOUT capability" (e.g., 'show_not_warp_capable')
          capability_check: Function that returns True if ship has the capability

      Returns:
          True if ship passes this filter, False if it should be excluded
      """
      show_has = filter_state.get(has_key, True)
      show_not = filter_state.get(not_key, True)

      if show_has and show_not:
          return True  # No filtering active

      has_capability = capability_check(ship)
      return show_has if has_capability else show_not
  ```
- [ ] Add `Callable` to typing imports at top of file
- [ ] Run tests: `pytest tests/unit/ui/screens/test_fleet_report_filters.py -v`

### 2.2 Refactor Warp Capability Filter

**Lines:** 143-153 in `filter_ships`

- [ ] **Replace warp filter block with helper call**
  - Replace lines 143-153 with:
  ```python
  # Warp capability filter
  if not _passes_binary_filter(
      ship, filter_state,
      'show_warp_capable', 'show_not_warp_capable',
      ShipStatsCalculator.has_warp_capability
  ):
      continue
  ```
- [ ] Run tests: `pytest tests/unit/ui/screens/test_fleet_report_filters.py::TestFilterShipsWarp -v`

### 2.3 Refactor Spaceyard Capability Filter

**Lines:** 155-164 in `filter_ships`

- [ ] **Replace spaceyard filter block with helper call**
  - Move the late import to inside a lambda or keep inline
  - Replace with:
  ```python
  # Spaceyard capability filter
  from game.strategy.data.fleet_capability_calculator import FleetCapabilityCalculator
  if not _passes_binary_filter(
      ship, filter_state,
      'show_has_spaceyard', 'show_no_spaceyard',
      FleetCapabilityCalculator.ship_has_spaceyard
  ):
      continue
  ```
- [ ] Run tests: `pytest tests/unit/ui/screens/test_fleet_report_filters.py::TestFilterShipsSpaceyard -v`

### 2.4 Refactor Cargo Filter

**Lines:** 166-174 in `filter_ships`

- [ ] **Replace cargo filter block with helper call**
  ```python
  # Cargo filter
  def _has_cargo(s: ShipInstance) -> bool:
      return bool(s.cargo_contents) and sum(s.cargo_contents.values()) > 0

  if not _passes_binary_filter(
      ship, filter_state,
      'show_has_cargo', 'show_no_cargo',
      _has_cargo
  ):
      continue
  ```
  - Note: The `_has_cargo` helper can be defined inside the loop or extracted as a module-level function
- [ ] Run tests: `pytest tests/unit/ui/screens/test_fleet_report_filters.py::TestFilterShipsCargo -v`

### 2.5 Refactor Special Capability Filters Loop

**Lines:** 176-194 in `filter_ships`

- [ ] **Replace special capability loop with helper calls**
  ```python
  # Special capability filters
  from game.strategy.data.fleet_capability_calculator import FleetCapabilityCalculator
  _skip = False
  for col_id, ability_name in SPECIAL_CAPABILITY_COLUMNS.items():
      has_key = f'show_{col_id}'
      not_key = f'show_{col_id.replace("can_", "no_", 1)}'

      def check_ability(s: ShipInstance, name: str = ability_name) -> bool:
          return FleetCapabilityCalculator.ship_has_ability(s, name)

      if not _passes_binary_filter(ship, filter_state, has_key, not_key, check_ability):
          _skip = True
          break
  if _skip:
      continue
  ```
- [ ] Run tests: `pytest tests/unit/ui/screens/test_fleet_report_filters.py::TestSpecialCapabilityFilter -v`

---

## Verification

- [ ] Run full filter tests: `pytest tests/unit/ui/screens/test_fleet_report_filters.py -v`
- [ ] Run view model tests: `pytest tests/unit/ui/test_fleet_list_view_model.py -v`
- [ ] Run `pytest tests/ --testmon` for broader regression check
- [ ] Verify no behavioral changes (same test results as before)

---

## Completion Criteria

- [ ] `_passes_binary_filter()` helper created
- [ ] All 4 capability filter blocks refactored to use helper
- [ ] All tests passing
- [ ] Code is cleaner and more readable
