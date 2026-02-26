# Phase 2: Extract Helper Functions

**Goal:** Create helper predicate functions for each filter category without changing the main function yet.

**Target file:** `game/ui/screens/fleet_report_filters.py`

---

## Tasks

### 2.1 Move FleetCapabilityCalculator import
- [ ] Add import at module level with TYPE_CHECKING guard
- [ ] Keep runtime import inside functions that need it (circular dependency)
- [ ] Verify tests still pass

```python
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from game.strategy.data.fleet_capability_calculator import FleetCapabilityCalculator
```

### 2.2 Create `_passes_binary_filter()` helper
- [ ] Add function after imports, before `calculate_fleet_stats`
- [ ] Implement generic binary filter logic
- [ ] Expected CC: 3

```python
def _passes_binary_filter(
    filter_state: Dict[str, bool],
    has_key: str,
    not_key: str,
    has_capability: bool
) -> bool:
    """
    Check if a ship passes a binary capability filter.

    Returns True if the ship should be included, False to exclude.
    Both-true optimization: if both filters enabled, always return True.
    """
    show_has = filter_state.get(has_key, True)
    show_not = filter_state.get(not_key, True)

    # Both enabled = no filtering needed
    if show_has and show_not:
        return True

    # Check based on capability
    if has_capability:
        return show_has
    return show_not
```

### 2.3 Create `_passes_warp_filter()` helper
- [ ] Add function using `_passes_binary_filter`
- [ ] Call `ShipStatsCalculator.has_warp_capability()` only when needed
- [ ] Expected CC: 2

```python
def _passes_warp_filter(ship: 'ShipInstance', filter_state: Dict[str, bool]) -> bool:
    """Check if ship passes warp capability filter."""
    show_warp = filter_state.get('show_warp_capable', True)
    show_not_warp = filter_state.get('show_not_warp_capable', True)

    # Both enabled = no check needed
    if show_warp and show_not_warp:
        return True

    is_warp_capable = ShipStatsCalculator.has_warp_capability(ship)
    return _passes_binary_filter(filter_state, 'show_warp_capable', 'show_not_warp_capable', is_warp_capable)
```

### 2.4 Create `_passes_spaceyard_filter()` helper
- [ ] Add function using `_passes_binary_filter`
- [ ] Include late import of `FleetCapabilityCalculator`
- [ ] Expected CC: 2

```python
def _passes_spaceyard_filter(ship: 'ShipInstance', filter_state: Dict[str, bool]) -> bool:
    """Check if ship passes spaceyard capability filter."""
    show_has = filter_state.get('show_has_spaceyard', True)
    show_not = filter_state.get('show_no_spaceyard', True)

    if show_has and show_not:
        return True

    from game.strategy.data.fleet_capability_calculator import FleetCapabilityCalculator
    has_spaceyard = FleetCapabilityCalculator.ship_has_spaceyard(ship)
    return _passes_binary_filter(filter_state, 'show_has_spaceyard', 'show_no_spaceyard', has_spaceyard)
```

### 2.5 Create `_passes_cargo_filter()` helper
- [ ] Add function with cargo detection logic
- [ ] Preserve `sum(cargo_contents.values()) > 0` check
- [ ] Expected CC: 3

```python
def _passes_cargo_filter(ship: 'ShipInstance', filter_state: Dict[str, bool]) -> bool:
    """Check if ship passes cargo presence filter."""
    show_has = filter_state.get('show_has_cargo', True)
    show_not = filter_state.get('show_no_cargo', True)

    if show_has and show_not:
        return True

    has_cargo = bool(ship.cargo_contents) and sum(ship.cargo_contents.values()) > 0
    return _passes_binary_filter(filter_state, 'show_has_cargo', 'show_no_cargo', has_cargo)
```

### 2.6 Create `_passes_special_capability_filters()` helper
- [ ] Add function iterating over `SPECIAL_CAPABILITY_COLUMNS`
- [ ] Preserve `can_X → no_X` key transformation
- [ ] Return False on first failing filter (early exit)
- [ ] Expected CC: 4

```python
def _passes_special_capability_filters(ship: 'ShipInstance', filter_state: Dict[str, bool]) -> bool:
    """Check if ship passes all special capability filters."""
    for col_id, ability_name in SPECIAL_CAPABILITY_COLUMNS.items():
        show_has = filter_state.get(f'show_{col_id}', True)
        no_key = col_id.replace('can_', 'no_', 1)
        show_not = filter_state.get(f'show_{no_key}', True)

        if show_has and show_not:
            continue

        from game.strategy.data.fleet_capability_calculator import FleetCapabilityCalculator
        has_ability = FleetCapabilityCalculator.ship_has_ability(ship, ability_name)

        if not _passes_binary_filter(filter_state, f'show_{col_id}', f'show_{no_key}', has_ability):
            return False

    return True
```

### 2.7 Create `_passes_status_filter()` helper
- [ ] Add function with status hierarchy logic
- [ ] Preserve order: Destroyed → Derelict → Damaged → Undamaged
- [ ] Expected CC: 5

```python
def _passes_status_filter(ship: 'ShipInstance', filter_state: Dict[str, bool]) -> bool:
    """
    Check if ship passes status filter.

    Status categories are mutually exclusive. Order matters:
    Destroyed -> Derelict -> Damaged -> Undamaged
    """
    if not ship.is_alive:
        return filter_state.get('show_destroyed', True)

    if ship.is_derelict:
        return filter_state.get('show_derelict', True)

    if ship.is_damaged():
        return filter_state.get('show_damaged', True)

    # Undamaged (healthy)
    return filter_state.get('show_undamaged', True)
```

### 2.8 Run tests after each helper
- [ ] Run `pytest tests/unit/ui/screens/test_fleet_report_filters.py -v` after each addition
- [ ] Verify all tests still pass (helpers not yet used by main function)

---

## Completion Criteria
- [ ] All 6 helper functions created
- [ ] All existing tests still pass
- [ ] No changes to `filter_ships` main function yet
- [ ] Commit: `[PROJ-234] Phase 2: Extract filter helper functions`
