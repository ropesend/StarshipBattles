# Phase 2: Extract Helpers

> **ONE EXTRACTION AT A TIME:** Extract each helper, run tests, commit before moving to next.

## Prerequisites
- [ ] Phase 1 complete (all tests passing)
- [ ] Read current `filter_ships` implementation (lines 124-222)

## Tasks

### 2.1 Extract `_should_exclude_by_warp`
**File:** `game/ui/screens/fleet_report_filters.py`

- [ ] Create function `_should_exclude_by_warp(ship: ShipInstance, filter_state: Dict[str, bool]) -> bool`
- [ ] Move lines 143-153 logic into the new function
- [ ] Return `True` if ship should be excluded, `False` otherwise
- [ ] Replace original code with `if _should_exclude_by_warp(ship, filter_state): continue`
- [ ] Run: `pytest tests/unit/ui/screens/test_fleet_report_filters.py::TestFilterShipsWarp -v`
- [ ] Verify all warp tests pass

### 2.2 Extract `_should_exclude_by_spaceyard`
**File:** `game/ui/screens/fleet_report_filters.py`

- [ ] Create function `_should_exclude_by_spaceyard(ship: ShipInstance, filter_state: Dict[str, bool]) -> bool`
- [ ] Move lines 155-164 logic into the new function
- [ ] **CRITICAL:** Keep late import `from game.strategy.data.fleet_capability_calculator import FleetCapabilityCalculator` INSIDE the function
- [ ] Return `True` if ship should be excluded, `False` otherwise
- [ ] Replace original code with `if _should_exclude_by_spaceyard(ship, filter_state): continue`
- [ ] Run: `pytest tests/unit/ui/screens/test_fleet_report_filters.py::TestFilterShipsSpaceyard -v`
- [ ] Verify all spaceyard tests pass

### 2.3 Extract `_should_exclude_by_cargo`
**File:** `game/ui/screens/fleet_report_filters.py`

- [ ] Create function `_should_exclude_by_cargo(ship: ShipInstance, filter_state: Dict[str, bool]) -> bool`
- [ ] Move lines 166-174 logic into the new function
- [ ] Return `True` if ship should be excluded, `False` otherwise
- [ ] Replace original code with `if _should_exclude_by_cargo(ship, filter_state): continue`
- [ ] Run: `pytest tests/unit/ui/screens/test_fleet_report_filters.py::TestFilterShipsCargo -v`
- [ ] Verify all cargo tests pass

### 2.4 Extract `_should_exclude_by_special_capabilities`
**File:** `game/ui/screens/fleet_report_filters.py`

- [ ] Create function `_should_exclude_by_special_capabilities(ship: ShipInstance, filter_state: Dict[str, bool]) -> bool`
- [ ] Move lines 176-194 logic into the new function
- [ ] **CRITICAL:** Keep late import INSIDE the function
- [ ] **CRITICAL:** Preserve the loop + early return pattern (replaces `_skip` flag + `break`)
- [ ] Return `True` if ship should be excluded, `False` otherwise
- [ ] Replace original code with `if _should_exclude_by_special_capabilities(ship, filter_state): continue`
- [ ] Run: `pytest tests/unit/ui/screens/test_fleet_report_filters.py::TestSpecialCapabilityFilter -v`
- [ ] Verify all special capability tests pass

### 2.5 Extract `_should_exclude_by_status`
**File:** `game/ui/screens/fleet_report_filters.py`

- [ ] Create function `_should_exclude_by_status(ship: ShipInstance, filter_state: Dict[str, bool]) -> bool`
- [ ] Move lines 196-220 logic into the new function
- [ ] **CRITICAL:** Preserve exact order: destroyed → derelict → damaged → undamaged
- [ ] Add comment documenting the order requirement
- [ ] Return `True` if ship should be excluded, `False` otherwise
- [ ] Replace original code with `if _should_exclude_by_status(ship, filter_state): continue`
- [ ] After all exclusion checks, add `result.append(ship)` (remove individual appends from status checks)
- [ ] Run: `pytest tests/unit/ui/screens/test_fleet_report_filters.py::TestFilterShips -v`
- [ ] Verify all status filter tests pass

### 2.6 Clean Up Main Function
**File:** `game/ui/screens/fleet_report_filters.py`

- [ ] Verify `filter_ships` now looks like:
  ```python
  def filter_ships(ships: List[ShipInstance], filter_state: Dict[str, bool]) -> List[ShipInstance]:
      result = []
      for ship in ships:
          if _should_exclude_by_warp(ship, filter_state):
              continue
          if _should_exclude_by_spaceyard(ship, filter_state):
              continue
          if _should_exclude_by_cargo(ship, filter_state):
              continue
          if _should_exclude_by_special_capabilities(ship, filter_state):
              continue
          if _should_exclude_by_status(ship, filter_state):
              continue
          result.append(ship)
      return result
  ```
- [ ] Run full filter tests: `pytest tests/unit/ui/screens/test_fleet_report_filters.py -v`
- [ ] All tests pass

## Verification
- [ ] All extractions complete
- [ ] All tests passing
- [ ] Code follows the target structure from design.md

## Completion Criteria
- All checkboxes above are checked
- No test failures
- Ready to proceed to Phase 3
