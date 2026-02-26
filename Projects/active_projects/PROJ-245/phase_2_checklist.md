# Phase 2: Extract Filter Helpers

> Extract each filter section into a named predicate function. Each extraction is done one at a time with test verification.

**File:** `game/ui/screens/fleet_report_filters.py`

## Tasks

### 2.1 Extract `_passes_warp_filter()`
- [ ] Add function `_passes_warp_filter(ship: ShipInstance, filter_state: Dict[str, bool]) -> bool` above `filter_ships`
- [ ] Move lines 143-153 (warp filter logic) into the new function
- [ ] Return `True` if ship passes, `False` if excluded
- [ ] Preserve both-True optimization: `if show_warp and show_not_warp: return True`
- [ ] Run: `pytest tests/unit/ui/screens/test_fleet_report_filters.py::TestFilterShipsWarp -v`

### 2.2 Extract `_passes_spaceyard_filter()`
- [ ] Add function `_passes_spaceyard_filter(ship: ShipInstance, filter_state: Dict[str, bool]) -> bool`
- [ ] Move lines 155-164 (spaceyard filter logic) into the new function
- [ ] Keep late import of `FleetCapabilityCalculator` INSIDE the function
- [ ] Run: `pytest tests/unit/ui/screens/test_fleet_report_filters.py::TestFilterShipsSpaceyard -v`

### 2.3 Extract `_passes_cargo_filter()`
- [ ] Add function `_passes_cargo_filter(ship: ShipInstance, filter_state: Dict[str, bool]) -> bool`
- [ ] Move lines 166-174 (cargo filter logic) into the new function
- [ ] Preserve exact cargo check: `bool(ship.cargo_contents) and sum(ship.cargo_contents.values()) > 0`
- [ ] Run: `pytest tests/unit/ui/screens/test_fleet_report_filters.py::TestFilterShipsCargo -v`

### 2.4 Extract `_passes_special_capability_filter()`
- [ ] Add function `_passes_special_capability_filter(ship: ShipInstance, filter_state: Dict[str, bool]) -> bool`
- [ ] Move lines 176-194 (special capabilities loop) into the new function
- [ ] Preserve early-exit on first exclusion (the `_skip` pattern becomes `return False`)
- [ ] Keep late import of `FleetCapabilityCalculator` INSIDE the function
- [ ] Preserve filter key derivation: `no_key = col_id.replace('can_', 'no_', 1)`
- [ ] Run: `pytest tests/unit/ui/screens/test_fleet_report_filters.py::TestSpecialCapabilityFilter -v`

### 2.5 Extract `_passes_status_filter()`
- [ ] Add function `_passes_status_filter(ship: ShipInstance, filter_state: Dict[str, bool]) -> bool`
- [ ] Move lines 196-220 (status chain) into the new function
- [ ] CRITICAL: Preserve status priority order: destroyed > derelict > damaged > undamaged
- [ ] Return `True` if ship's status filter is enabled, `False` otherwise
- [ ] Run: `pytest tests/unit/ui/screens/test_fleet_report_filters.py::TestFilterShips -v`

### 2.6 Verify All Extractions
- [ ] Run: `pytest tests/unit/ui/screens/test_fleet_report_filters.py -v`
- [ ] All 21+ tests pass
- [ ] Run: `pytest tests/ --testmon`

## Verification
```bash
pytest tests/unit/ui/screens/test_fleet_report_filters.py -v
pytest tests/ -n 12 --tb=short
```

## Exit Criteria
- [ ] All 5 helper functions extracted
- [ ] All tests passing
- [ ] Helper functions have docstrings
- [ ] Late imports preserved in spaceyard and special capability helpers
