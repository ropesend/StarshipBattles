# Phase 2: Extract Filter Predicates

**Goal:** Create helper functions for each filter category.
**File:** `game/ui/screens/fleet_report_filters.py`

## Pre-Phase Verification
- [ ] Phase 1 complete (all new tests passing)
- [ ] Run baseline: `pytest tests/unit/ui/screens/test_fleet_report_filters.py -v`

## Tasks

### T2.1: Add `_passes_binary_filter()` Helper
**Location:** After imports, before `calculate_fleet_stats` (around line 18)

```python
def _passes_binary_filter(has_capability: bool, show_has: bool, show_not: bool) -> bool:
    """
    Universal binary filter check.

    Returns True if ship passes a has/lacks filter pair.
    When both show_has and show_not are True, filter is disabled (always passes).
    """
    if show_has and show_not:
        return True
    return (has_capability and show_has) or (not has_capability and show_not)
```

- [ ] Add function
- [ ] Run tests to verify no regressions

### T2.2: Add `_classify_ship_status()` Helper
**Location:** After `_passes_binary_filter`

```python
def _classify_ship_status(ship: 'ShipInstance') -> str:
    """
    Classify ship into exactly one status category.

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

- [ ] Add function
- [ ] Run tests to verify no regressions

### T2.3: Add `_passes_warp_filter()` Helper
**Location:** After `_classify_ship_status`

```python
def _passes_warp_filter(ship: 'ShipInstance', filter_state: Dict[str, bool]) -> bool:
    """Check if ship passes warp capability filter."""
    show_warp = filter_state.get('show_warp_capable', True)
    show_not_warp = filter_state.get('show_not_warp_capable', True)
    if show_warp and show_not_warp:
        return True
    is_warp_capable = ShipStatsCalculator.has_warp_capability(ship)
    return _passes_binary_filter(is_warp_capable, show_warp, show_not_warp)
```

- [ ] Add function
- [ ] Run tests to verify no regressions

### T2.4: Add `_passes_spaceyard_filter()` Helper
**Location:** After `_passes_warp_filter`

```python
def _passes_spaceyard_filter(ship: 'ShipInstance', filter_state: Dict[str, bool]) -> bool:
    """Check if ship passes spaceyard capability filter."""
    show_has_yard = filter_state.get('show_has_spaceyard', True)
    show_no_yard = filter_state.get('show_no_spaceyard', True)
    if show_has_yard and show_no_yard:
        return True
    # Late import to avoid circular dependency
    from game.strategy.data.fleet_capability_calculator import FleetCapabilityCalculator
    has_yard = FleetCapabilityCalculator.ship_has_spaceyard(ship)
    return _passes_binary_filter(has_yard, show_has_yard, show_no_yard)
```

- [ ] Add function (preserve late import)
- [ ] Run tests to verify no regressions

### T2.5: Add `_passes_cargo_filter()` Helper
**Location:** After `_passes_spaceyard_filter`

```python
def _passes_cargo_filter(ship: 'ShipInstance', filter_state: Dict[str, bool]) -> bool:
    """Check if ship passes cargo filter."""
    show_has_cargo = filter_state.get('show_has_cargo', True)
    show_no_cargo = filter_state.get('show_no_cargo', True)
    if show_has_cargo and show_no_cargo:
        return True
    has_cargo = bool(ship.cargo_contents) and sum(ship.cargo_contents.values()) > 0
    return _passes_binary_filter(has_cargo, show_has_cargo, show_no_cargo)
```

- [ ] Add function
- [ ] Run tests to verify no regressions

### T2.6: Add `_passes_special_filters()` Helper
**Location:** After `_passes_cargo_filter`

```python
def _passes_special_filters(ship: 'ShipInstance', filter_state: Dict[str, bool]) -> bool:
    """Check if ship passes all special capability filters."""
    for col_id, ability_name in SPECIAL_CAPABILITY_COLUMNS.items():
        show_has = filter_state.get(f'show_{col_id}', True)
        no_key = col_id.replace('can_', 'no_', 1)
        show_not = filter_state.get(f'show_{no_key}', True)
        if show_has and show_not:
            continue  # Filter disabled for this ability
        # Late import to avoid circular dependency
        from game.strategy.data.fleet_capability_calculator import FleetCapabilityCalculator
        has_ability = FleetCapabilityCalculator.ship_has_ability(ship, ability_name)
        if not _passes_binary_filter(has_ability, show_has, show_not):
            return False
    return True
```

- [ ] Add function (preserve late import)
- [ ] Run tests to verify no regressions

### T2.7: Add `_passes_status_filter()` Helper
**Location:** After `_passes_special_filters`

```python
def _passes_status_filter(ship: 'ShipInstance', filter_state: Dict[str, bool]) -> bool:
    """Check if ship passes status filter based on its classified status."""
    status = _classify_ship_status(ship)
    return filter_state.get(f'show_{status}', True)
```

- [ ] Add function
- [ ] Run tests to verify no regressions

## Post-Phase Verification
- [ ] All 7 helper functions added
- [ ] Run full filter tests: `pytest tests/unit/ui/screens/test_fleet_report_filters.py -v`
- [ ] All tests pass (including Phase 1 tests)
- [ ] Update phase status in plan.md

## Test Commands
```bash
# Run after each helper addition
pytest tests/unit/ui/screens/test_fleet_report_filters.py -v

# Quick smoke test
pytest tests/unit/ui/screens/test_fleet_report_filters.py::TestFilterShips -v
```
