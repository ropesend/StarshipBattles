# Phase 3: Extract Capability Helpers

**Goal:** Extract capability filter logic into helper functions to reduce CC to below 20.

**File to modify:** `game/ui/screens/fleet_report_filters.py`

## Pre-Phase Checks
- [ ] Phase 2 complete
- [ ] Run tests: `pytest tests/unit/ui/screens/test_fleet_report_filters.py -v`

## Tasks

### 3.1 Add `_passes_binary_filter` Helper
- [ ] Add generic helper function (at top of helpers section):
```python
def _passes_binary_filter(has_capability: bool, show_has: bool, show_not: bool) -> bool:
    """
    Check if an item passes a binary filter (has/doesn't have capability).

    Args:
        has_capability: Whether the item has the capability
        show_has: Whether to show items WITH the capability
        show_not: Whether to show items WITHOUT the capability

    Returns:
        True if item passes the filter, False if excluded
    """
    if has_capability and not show_has:
        return False
    if not has_capability and not show_not:
        return False
    return True
```
- [ ] Run tests to verify no regressions

### 3.2 Add `_passes_capability_filters` Helper
- [ ] Add helper that handles warp, spaceyard, and cargo filters:
```python
def _passes_capability_filters(ship: 'ShipInstance', filter_state: Dict[str, bool]) -> bool:
    """Check if ship passes warp, spaceyard, and cargo filters."""
    # Warp capability filter
    show_warp = filter_state.get('show_warp_capable', True)
    show_not_warp = filter_state.get('show_not_warp_capable', True)
    if not show_warp or not show_not_warp:
        is_warp_capable = ShipStatsCalculator.has_warp_capability(ship)
        if not _passes_binary_filter(is_warp_capable, show_warp, show_not_warp):
            return False

    # Spaceyard capability filter
    show_has_yard = filter_state.get('show_has_spaceyard', True)
    show_no_yard = filter_state.get('show_no_spaceyard', True)
    if not show_has_yard or not show_no_yard:
        from game.strategy.data.fleet_capability_calculator import FleetCapabilityCalculator
        has_yard = FleetCapabilityCalculator.ship_has_spaceyard(ship)
        if not _passes_binary_filter(has_yard, show_has_yard, show_no_yard):
            return False

    # Cargo filter
    show_has_cargo = filter_state.get('show_has_cargo', True)
    show_no_cargo = filter_state.get('show_no_cargo', True)
    if not show_has_cargo or not show_no_cargo:
        has_cargo = bool(ship.cargo_contents) and sum(ship.cargo_contents.values()) > 0
        if not _passes_binary_filter(has_cargo, show_has_cargo, show_no_cargo):
            return False

    return True
```
- [ ] Run tests to verify no regressions

### 3.3 Add `_passes_special_capability_filters` Helper
- [ ] Add helper that handles the SPECIAL_CAPABILITY_COLUMNS loop:
```python
def _passes_special_capability_filters(ship: 'ShipInstance', filter_state: Dict[str, bool]) -> bool:
    """Check if ship passes all special capability filters (destroy planet, etc.)."""
    from game.strategy.data.fleet_capability_calculator import FleetCapabilityCalculator

    for col_id, ability_name in SPECIAL_CAPABILITY_COLUMNS.items():
        show_has = filter_state.get(f'show_{col_id}', True)
        no_key = col_id.replace('can_', 'no_', 1)
        show_not = filter_state.get(f'show_{no_key}', True)

        if not show_has or not show_not:
            has_ability = FleetCapabilityCalculator.ship_has_ability(ship, ability_name)
            if not _passes_binary_filter(has_ability, show_has, show_not):
                return False

    return True
```
- [ ] Run tests to verify no regressions

### 3.4 Refactor `filter_ships` to Use Helpers
- [ ] Replace entire function body with:
```python
def filter_ships(ships: List[ShipInstance], filter_state: Dict[str, bool]) -> List[ShipInstance]:
    """
    Filter ships based on status filter state.

    Args:
        ships: List of ShipInstance objects
        filter_state: Dict with boolean filter keys (see docstring for full list)

    Returns:
        Filtered list of ships
    """
    return [
        ship for ship in ships
        if _passes_capability_filters(ship, filter_state)
        and _passes_special_capability_filters(ship, filter_state)
        and _passes_status_filter(ship, filter_state)
    ]
```
- [ ] Run tests: `pytest tests/unit/ui/screens/test_fleet_report_filters.py -v`
- [ ] All tests pass

### 3.5 Verify Final CC
- [ ] Run complexity check: `python -m radon cc game/ui/screens/fleet_report_filters.py -s -a`
- [ ] `filter_ships` CC is now below 20
- [ ] Document individual helper CCs

## Post-Phase Verification
- [ ] All tests pass
- [ ] `filter_ships` CC < 20
- [ ] Update plan.md: Phase 3 status = Complete

**CC After Phase 3:**
- `filter_ships`: ___ (target: < 20)
- `_passes_capability_filters`: ___
- `_passes_special_capability_filters`: ___
- `_passes_status_filter`: ___
- `_get_ship_status`: ___
- `_passes_binary_filter`: ___
