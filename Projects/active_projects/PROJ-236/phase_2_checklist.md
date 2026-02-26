# Phase 2: Extract Status Helpers

**Goal:** Extract the status cascade logic into helper functions to reduce CC by ~8 points.

**File to modify:** `game/ui/screens/fleet_report_filters.py`

## Pre-Phase Checks
- [ ] Phase 1 complete (all safety tests pass)
- [ ] Run tests: `pytest tests/unit/ui/screens/test_fleet_report_filters.py -v`

## Tasks

### 2.1 Add `_get_ship_status` Helper
- [ ] Add function above `filter_ships` (around line 122):
```python
def _get_ship_status(ship: 'ShipInstance') -> str:
    """
    Classify ship into one of four mutually exclusive status categories.

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
- [ ] Run tests to verify no regressions

### 2.2 Add `_passes_status_filter` Helper
- [ ] Add function after `_get_ship_status`:
```python
def _passes_status_filter(ship: 'ShipInstance', filter_state: Dict[str, bool]) -> bool:
    """Check if ship passes the status filter based on its status category."""
    status = _get_ship_status(ship)
    filter_key = f'show_{status}'
    return filter_state.get(filter_key, True)
```
- [ ] Run tests to verify no regressions

### 2.3 Refactor Status Cascade in `filter_ships`
- [ ] Replace lines 196-220 (the status cascade) with:
```python
        # Status filter (destroyed/derelict/damaged/undamaged)
        if not _passes_status_filter(ship, filter_state):
            continue
        result.append(ship)
```
- [ ] Run tests: `pytest tests/unit/ui/screens/test_fleet_report_filters.py -v`
- [ ] All tests pass

### 2.4 Verify CC Reduction
- [ ] Run complexity check: `python -m radon cc game/ui/screens/fleet_report_filters.py -s -a`
- [ ] Note current CC for `filter_ships` (should be ~28, down from 36)

## Post-Phase Verification
- [ ] All tests pass
- [ ] CC reduced (document in this file)
- [ ] Update plan.md: Phase 2 status = Complete

**CC After Phase 2:** ___ (fill in)
