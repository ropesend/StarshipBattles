# Phase 2: Extract Helpers

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-233 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Extract helper functions to reduce complexity of `filter_ships`.

**Prerequisites:** Phase 1 must be complete (test fortification).

---

## Tasks

### Task 2.1: Extract `_passes_binary_filter` [Simple]
**File:** `game/ui/screens/fleet_report_filters.py`
**Tests:** `pytest tests/unit/ui/screens/test_fleet_report_filters.py -v`

Add helper function before `filter_ships` (around line 124):

```python
def _passes_binary_filter(
    filter_state: Dict[str, bool],
    show_key: str,
    hide_key: str,
    has_property: bool
) -> bool:
    """
    Check if a ship passes a binary (has/doesn't have) filter.

    Returns True if the ship should be included based on this filter.
    """
    show_has = filter_state.get(show_key, True)
    show_not = filter_state.get(hide_key, True)

    # If both filters are on, no filtering needed
    if show_has and show_not:
        return True

    # Otherwise, check based on property
    if has_property:
        return show_has
    return show_not
```

- [ ] Add `_passes_binary_filter` function
- [ ] Add docstring explaining purpose
- [ ] Run tests: `pytest tests/unit/ui/screens/test_fleet_report_filters.py -v`
- [ ] Verify all tests still pass

**Notes:**

---

### Task 2.2: Extract `_passes_status_filter` [Medium]
**File:** `game/ui/screens/fleet_report_filters.py`
**Tests:** `pytest tests/unit/ui/screens/test_fleet_report_filters.py -v`

Add helper function that handles status priority chain:

```python
def _passes_status_filter(ship: 'ShipInstance', filter_state: Dict[str, bool]) -> bool:
    """
    Check if ship passes status filters (destroyed > derelict > damaged > undamaged).

    Status categories are mutually exclusive - a ship can only be one status.
    """
    if not ship.is_alive:
        return filter_state.get('show_destroyed', True)
    if ship.is_derelict:
        return filter_state.get('show_derelict', True)
    if ship.is_damaged():
        return filter_state.get('show_damaged', True)
    return filter_state.get('show_undamaged', True)
```

- [ ] Add `_passes_status_filter` function
- [ ] Add docstring explaining mutual exclusivity
- [ ] Run tests: `pytest tests/unit/ui/screens/test_fleet_report_filters.py -v`
- [ ] Verify all tests still pass

**Notes:**

---

### Task 2.3: Extract `_passes_capability_filters` [Complex]
**File:** `game/ui/screens/fleet_report_filters.py`
**Tests:** `pytest tests/unit/ui/screens/test_fleet_report_filters.py -v`

Add helper function that handles all capability filters:

```python
def _passes_capability_filters(ship: 'ShipInstance', filter_state: Dict[str, bool]) -> bool:
    """
    Check if ship passes all capability filters (warp, spaceyard, cargo, special abilities).

    Late imports are used to avoid circular dependencies.
    """
    # Warp capability filter
    show_warp = filter_state.get('show_warp_capable', True)
    show_not_warp = filter_state.get('show_not_warp_capable', True)
    if not show_warp or not show_not_warp:
        is_warp_capable = ShipStatsCalculator.has_warp_capability(ship)
        if not _passes_binary_filter(filter_state, 'show_warp_capable',
                                      'show_not_warp_capable', is_warp_capable):
            return False

    # Spaceyard capability filter
    show_has_yard = filter_state.get('show_has_spaceyard', True)
    show_no_yard = filter_state.get('show_no_spaceyard', True)
    if not show_has_yard or not show_no_yard:
        from game.strategy.data.fleet_capability_calculator import FleetCapabilityCalculator
        has_yard = FleetCapabilityCalculator.ship_has_spaceyard(ship)
        if not _passes_binary_filter(filter_state, 'show_has_spaceyard',
                                      'show_no_spaceyard', has_yard):
            return False

    # Cargo filter
    show_has_cargo = filter_state.get('show_has_cargo', True)
    show_no_cargo = filter_state.get('show_no_cargo', True)
    if not show_has_cargo or not show_no_cargo:
        has_cargo = bool(ship.cargo_contents) and sum(ship.cargo_contents.values()) > 0
        if not _passes_binary_filter(filter_state, 'show_has_cargo',
                                      'show_no_cargo', has_cargo):
            return False

    # Special capability filters
    for col_id, ability_name in SPECIAL_CAPABILITY_COLUMNS.items():
        show_has = filter_state.get(f'show_{col_id}', True)
        no_key = col_id.replace('can_', 'no_', 1)
        show_not = filter_state.get(f'show_{no_key}', True)
        if not show_has or not show_not:
            from game.strategy.data.fleet_capability_calculator import FleetCapabilityCalculator
            has_ability = FleetCapabilityCalculator.ship_has_ability(ship, ability_name)
            if not _passes_binary_filter(filter_state, f'show_{col_id}',
                                          f'show_{no_key}', has_ability):
                return False

    return True
```

- [ ] Add `_passes_capability_filters` function
- [ ] Keep late imports inside function (not at module level)
- [ ] Add docstring explaining late imports
- [ ] Run tests: `pytest tests/unit/ui/screens/test_fleet_report_filters.py -v`
- [ ] Verify all tests still pass

**Notes:**

---

## Verification Commands

```bash
# Run all filter tests after each extraction
pytest tests/unit/ui/screens/test_fleet_report_filters.py -v

# Verify no regressions in broader UI tests
pytest tests/unit/ui/screens/ -v --tb=short

# Check CC of new functions (should be low individually)
radon cc game/ui/screens/fleet_report_filters.py -s -a
```

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] All 3 helper functions added
- [ ] All tests passing
- [ ] Each helper function has docstring
- [ ] Late imports preserved in `_passes_capability_filters`
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 3
