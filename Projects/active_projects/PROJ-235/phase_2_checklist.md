# Phase 2: Extract Helper Functions

**Goal:** Extract the repeated filter patterns into helper functions without changing the main function's logic.

**File:** `game/ui/screens/fleet_report_filters.py`

---

## Pre-Flight
- [ ] Run baseline: `pytest tests/unit/ui/screens/test_fleet_report_filters.py -v`
- [ ] Verify all tests pass before starting

---

## Task 2.1: Extract `_get_ship_status` Helper

**Purpose:** Centralize ship status determination (destroyed/derelict/damaged/undamaged).

**Location:** Add after line 16 (after imports, before `calculate_fleet_stats`)

```python
def _get_ship_status(ship: "ShipInstance") -> str:
    """Determine the primary status category for a ship.

    Order matters: destroyed > derelict > damaged > undamaged.
    A derelict ship is also damaged, but should be categorized as derelict.
    """
    if not ship.is_alive:
        return 'destroyed'
    if ship.is_derelict:
        return 'derelict'
    if ship.is_damaged():
        return 'damaged'
    return 'undamaged'
```

- [ ] Add `_get_ship_status` function after imports
- [ ] Run tests: `pytest tests/unit/ui/screens/test_fleet_report_filters.py -v`
- [ ] Verify all tests still pass (function not yet used)

---

## Task 2.2: Extract `_passes_boolean_filter` Helper

**Purpose:** Generic helper for the show_has/show_not filter pattern.

**Location:** Add after `_get_ship_status`

```python
def _passes_boolean_filter(
    has_capability: bool,
    show_has: bool,
    show_not: bool
) -> bool:
    """Check if a ship passes a boolean filter pair.

    Args:
        has_capability: Whether the ship has the capability being filtered
        show_has: Whether to show ships WITH the capability
        show_not: Whether to show ships WITHOUT the capability

    Returns:
        True if ship should be included, False if excluded
    """
    if show_has and show_not:
        return True  # No filtering needed
    if has_capability and not show_has:
        return False
    if not has_capability and not show_not:
        return False
    return True
```

- [ ] Add `_passes_boolean_filter` function
- [ ] Run tests: `pytest tests/unit/ui/screens/test_fleet_report_filters.py -v`
- [ ] Verify all tests still pass (function not yet used)

---

## Task 2.3: Extract `_passes_status_filter` Helper

**Purpose:** Encapsulate the status filter logic with proper ordering.

**Location:** Add after `_passes_boolean_filter`

```python
def _passes_status_filter(ship: "ShipInstance", filter_state: Dict[str, bool]) -> bool:
    """Check if ship passes status filters (destroyed/derelict/damaged/undamaged).

    Status order is critical: destroyed > derelict > damaged > undamaged.
    """
    status = _get_ship_status(ship)
    return filter_state.get(f'show_{status}', True)
```

- [ ] Add `_passes_status_filter` function
- [ ] Run tests: `pytest tests/unit/ui/screens/test_fleet_report_filters.py -v`
- [ ] Verify all tests still pass (function not yet used)

---

## Task 2.4: Extract `_passes_capability_filters` Helper

**Purpose:** Encapsulate all capability filters (warp, spaceyard, cargo, special abilities).

**Location:** Add after `_passes_status_filter`

```python
def _passes_capability_filters(ship: "ShipInstance", filter_state: Dict[str, bool]) -> bool:
    """Check if ship passes all capability-based filters.

    Includes: warp, spaceyard, cargo, and special ability filters.
    """
    # Warp capability filter
    show_warp = filter_state.get('show_warp_capable', True)
    show_not_warp = filter_state.get('show_not_warp_capable', True)
    if not show_warp or not show_not_warp:
        is_warp_capable = ShipStatsCalculator.has_warp_capability(ship)
        if not _passes_boolean_filter(is_warp_capable, show_warp, show_not_warp):
            return False

    # Spaceyard capability filter
    show_has_yard = filter_state.get('show_has_spaceyard', True)
    show_no_yard = filter_state.get('show_no_spaceyard', True)
    if not show_has_yard or not show_no_yard:
        from game.strategy.data.fleet_capability_calculator import FleetCapabilityCalculator
        has_yard = FleetCapabilityCalculator.ship_has_spaceyard(ship)
        if not _passes_boolean_filter(has_yard, show_has_yard, show_no_yard):
            return False

    # Cargo filter
    show_has_cargo = filter_state.get('show_has_cargo', True)
    show_no_cargo = filter_state.get('show_no_cargo', True)
    if not show_has_cargo or not show_no_cargo:
        has_cargo = bool(ship.cargo_contents) and sum(ship.cargo_contents.values()) > 0
        if not _passes_boolean_filter(has_cargo, show_has_cargo, show_no_cargo):
            return False

    # Special capability filters
    for col_id, ability_name in SPECIAL_CAPABILITY_COLUMNS.items():
        show_has = filter_state.get(f'show_{col_id}', True)
        no_key = col_id.replace('can_', 'no_', 1)
        show_not = filter_state.get(f'show_{no_key}', True)
        if not show_has or not show_not:
            from game.strategy.data.fleet_capability_calculator import FleetCapabilityCalculator
            has_ability = FleetCapabilityCalculator.ship_has_ability(ship, ability_name)
            if not _passes_boolean_filter(has_ability, show_has, show_not):
                return False

    return True
```

- [ ] Add `_passes_capability_filters` function
- [ ] Run tests: `pytest tests/unit/ui/screens/test_fleet_report_filters.py -v`
- [ ] Verify all tests still pass (function not yet used)

---

## Verification
- [ ] All 4 helper functions added
- [ ] All tests still pass
- [ ] No changes to `filter_ships` function yet
- [ ] Ready to proceed to Phase 3

---

## Completion Criteria
- Helper functions are defined and importable
- All existing tests pass (helpers not yet integrated)
- Code compiles without errors
