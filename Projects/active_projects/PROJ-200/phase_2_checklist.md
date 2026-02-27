# Phase 2: Extract Helpers

> **ONE EXTRACTION AT A TIME:** Extract each helper, run tests, commit before moving to next.

## Prerequisites
- [x] Phase 1 complete (all tests passing)
- [x] Read current `filter_ships` implementation (lines 124-222)

## Tasks

### 2.1 Extract `_should_exclude_by_warp`
**File:** `game/ui/screens/fleet_report_filters.py`

- [x] Create function `_should_exclude_by_warp(ship: ShipInstance, filter_state: Dict[str, bool]) -> bool`
- [x] Move lines 143-153 logic into the new function
- [x] Return `True` if ship should be excluded, `False` otherwise
- [x] Replace original code with `if _should_exclude_by_warp(ship, filter_state): continue`
- [x] Run: `pytest tests/unit/ui/screens/test_fleet_report_filters.py::TestFilterShipsWarp -v`
- [x] Verify all warp tests pass (3 passed)

### 2.2 Extract `_should_exclude_by_spaceyard`
**File:** `game/ui/screens/fleet_report_filters.py`

- [x] Create function `_should_exclude_by_spaceyard(ship: ShipInstance, filter_state: Dict[str, bool]) -> bool`
- [x] Move lines 155-164 logic into the new function
- [x] **CRITICAL:** Keep late import `from game.strategy.data.fleet_capability_calculator import FleetCapabilityCalculator` INSIDE the function
- [x] Return `True` if ship should be excluded, `False` otherwise
- [x] Replace original code with `if _should_exclude_by_spaceyard(ship, filter_state): continue`
- [x] Run: `pytest tests/unit/ui/screens/test_fleet_report_filters.py::TestFilterShipsSpaceyard -v`
- [x] Verify all spaceyard tests pass (3 passed)

### 2.3 Extract `_should_exclude_by_cargo`
**File:** `game/ui/screens/fleet_report_filters.py`

- [x] Create function `_should_exclude_by_cargo(ship: ShipInstance, filter_state: Dict[str, bool]) -> bool`
- [x] Move lines 166-174 logic into the new function
- [x] Return `True` if ship should be excluded, `False` otherwise
- [x] Replace original code with `if _should_exclude_by_cargo(ship, filter_state): continue`
- [x] Run: `pytest tests/unit/ui/screens/test_fleet_report_filters.py::TestFilterShipsCargo -v`
- [x] Verify all cargo tests pass (5 passed)

### 2.4 Extract `_should_exclude_by_special_capabilities`
**File:** `game/ui/screens/fleet_report_filters.py`

- [x] Create function `_should_exclude_by_special_capabilities(ship: ShipInstance, filter_state: Dict[str, bool]) -> bool`
- [x] Move lines 176-194 logic into the new function
- [x] **CRITICAL:** Keep late import INSIDE the function
- [x] **CRITICAL:** Preserve the loop + early return pattern (replaces `_skip` flag + `break`)
- [x] Return `True` if ship should be excluded, `False` otherwise
- [x] Replace original code with `if _should_exclude_by_special_capabilities(ship, filter_state): continue`
- [x] Run: `pytest tests/unit/ui/screens/test_fleet_report_filters.py::TestSpecialCapabilityFilter -v`
- [x] Verify all special capability tests pass (7 passed)

### 2.5 Extract `_should_exclude_by_status`
**File:** `game/ui/screens/fleet_report_filters.py`

- [x] Create function `_should_exclude_by_status(ship: ShipInstance, filter_state: Dict[str, bool]) -> bool`
- [x] Move lines 196-220 logic into the new function
- [x] **CRITICAL:** Preserve exact order: destroyed -> derelict -> damaged -> undamaged
- [x] Add comment documenting the order requirement
- [x] Return `True` if ship should be excluded, `False` otherwise
- [x] Replace original code with `if _should_exclude_by_status(ship, filter_state): continue`
- [x] After all exclusion checks, add `result.append(ship)` (remove individual appends from status checks)
- [x] Run: `pytest tests/unit/ui/screens/test_fleet_report_filters.py::TestFilterShips -v`
- [x] Verify all status filter tests pass (5 passed)

### 2.6 Clean Up Main Function
**File:** `game/ui/screens/fleet_report_filters.py`

- [x] Verify `filter_ships` now looks like:
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
- [x] Run full filter tests: `pytest tests/unit/ui/screens/test_fleet_report_filters.py -v`
- [x] All tests pass (59 passed)

## Verification
- [x] All extractions complete
- [x] All tests passing (12734 passed, 1 skipped)
- [x] Code follows the target structure from design.md
- [x] CC measured: filter_ships reduced from 36 to 7

## Completion Criteria
- All checkboxes above are checked
- No test failures
- Ready to proceed to Phase 3
