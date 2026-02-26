# Phase 2: Extract Helpers

**Goal:** Extract helper functions from `filter_ships` to reduce cyclomatic complexity.

**Target:** Reduce `filter_ships` CC from 36 to ≤15.

---

## Pre-Conditions
- [ ] Phase 1 complete (all tests passing)
- [ ] Read `game/ui/screens/fleet_report_filters.py` lines 124-222

---

## Critical Invariants (DO NOT BREAK)

1. **Status filter order:** destroyed → derelict → damaged → undamaged
2. **Default behavior:** Missing filter keys default to `True` (show all)
3. **Short-circuit optimization:** Don't call expensive checks when both show flags are True
4. **Late imports:** Keep `FleetCapabilityCalculator` imports inside helpers
5. **Special capability keys:** `can_X` → `no_X` transformation

---

## Tasks

### 2.1 Extract `_passes_status_filter()`
**File:** `game/ui/screens/fleet_report_filters.py`
**Lines to extract:** 196-220 (status filter cascade)

```python
def _passes_status_filter(ship: 'ShipInstance', filter_state: Dict[str, bool]) -> bool:
    """Check if ship passes the status filter (destroyed/derelict/damaged/undamaged)."""
    if not ship.is_alive:
        return filter_state.get('show_destroyed', True)
    if ship.is_derelict:
        return filter_state.get('show_derelict', True)
    if ship.is_damaged():
        return filter_state.get('show_damaged', True)
    return filter_state.get('show_undamaged', True)
```

- [ ] Add helper function before `filter_ships`
- [ ] Update `filter_ships` to call helper
- [ ] Run tests: `pytest tests/unit/ui/screens/test_fleet_report_filters.py -v`
- [ ] All tests pass

### 2.2 Extract `_passes_warp_filter()`
**File:** `game/ui/screens/fleet_report_filters.py`
**Lines to extract:** 144-153 (warp capability filter)

```python
def _passes_warp_filter(ship: 'ShipInstance', filter_state: Dict[str, bool]) -> bool:
    """Check if ship passes the warp capability filter."""
    show_warp = filter_state.get('show_warp_capable', True)
    show_not_warp = filter_state.get('show_not_warp_capable', True)

    if show_warp and show_not_warp:
        return True  # Short-circuit: no filtering needed

    is_warp_capable = ShipStatsCalculator.has_warp_capability(ship)
    if is_warp_capable:
        return show_warp
    return show_not_warp
```

- [ ] Add helper function
- [ ] Update `filter_ships` to call helper
- [ ] Run tests
- [ ] All tests pass

### 2.3 Extract `_passes_spaceyard_filter()`
**File:** `game/ui/screens/fleet_report_filters.py`
**Lines to extract:** 155-164 (spaceyard filter)

```python
def _passes_spaceyard_filter(ship: 'ShipInstance', filter_state: Dict[str, bool]) -> bool:
    """Check if ship passes the spaceyard capability filter."""
    show_has_yard = filter_state.get('show_has_spaceyard', True)
    show_no_yard = filter_state.get('show_no_spaceyard', True)

    if show_has_yard and show_no_yard:
        return True  # Short-circuit

    # Late import to avoid circular dependency
    from game.strategy.data.fleet_capability_calculator import FleetCapabilityCalculator
    has_yard = FleetCapabilityCalculator.ship_has_spaceyard(ship)
    if has_yard:
        return show_has_yard
    return show_no_yard
```

- [ ] Add helper function (keep late import!)
- [ ] Update `filter_ships` to call helper
- [ ] Run tests
- [ ] All tests pass

### 2.4 Extract `_passes_cargo_filter()`
**File:** `game/ui/screens/fleet_report_filters.py`
**Lines to extract:** 166-174 (cargo filter)

```python
def _passes_cargo_filter(ship: 'ShipInstance', filter_state: Dict[str, bool]) -> bool:
    """Check if ship passes the cargo filter."""
    show_has_cargo = filter_state.get('show_has_cargo', True)
    show_no_cargo = filter_state.get('show_no_cargo', True)

    if show_has_cargo and show_no_cargo:
        return True  # Short-circuit

    has_cargo = bool(ship.cargo_contents) and sum(ship.cargo_contents.values()) > 0
    if has_cargo:
        return show_has_cargo
    return show_no_cargo
```

- [ ] Add helper function
- [ ] Update `filter_ships` to call helper
- [ ] Run tests
- [ ] All tests pass

### 2.5 Extract `_passes_special_capability_filters()`
**File:** `game/ui/screens/fleet_report_filters.py`
**Lines to extract:** 176-194 (special capabilities loop)

```python
def _passes_special_capability_filters(ship: 'ShipInstance', filter_state: Dict[str, bool]) -> bool:
    """Check if ship passes all special capability filters."""
    for col_id, ability_name in SPECIAL_CAPABILITY_COLUMNS.items():
        show_has = filter_state.get(f'show_{col_id}', True)
        no_key = col_id.replace('can_', 'no_', 1)
        show_not = filter_state.get(f'show_{no_key}', True)

        if show_has and show_not:
            continue  # Short-circuit for this capability

        # Late import to avoid circular dependency
        from game.strategy.data.fleet_capability_calculator import FleetCapabilityCalculator
        has_ability = FleetCapabilityCalculator.ship_has_ability(ship, ability_name)

        if has_ability and not show_has:
            return False
        if not has_ability and not show_not:
            return False

    return True
```

- [ ] Add helper function (keep late import inside loop!)
- [ ] Update `filter_ships` to call helper
- [ ] Run tests
- [ ] All tests pass

### 2.6 Simplify main `filter_ships` function
**File:** `game/ui/screens/fleet_report_filters.py`

After all extractions, the main function should look like:

```python
def filter_ships(ships: List[ShipInstance], filter_state: Dict[str, bool]) -> List[ShipInstance]:
    """Filter ships based on status filter state."""
    result = []
    for ship in ships:
        if not _passes_warp_filter(ship, filter_state):
            continue
        if not _passes_spaceyard_filter(ship, filter_state):
            continue
        if not _passes_cargo_filter(ship, filter_state):
            continue
        if not _passes_special_capability_filters(ship, filter_state):
            continue
        if not _passes_status_filter(ship, filter_state):
            continue
        result.append(ship)
    return result
```

- [ ] Verify main function is simplified
- [ ] Run full test file
- [ ] All tests pass

---

## Post-Conditions
- [ ] 5 helper functions extracted
- [ ] `filter_ships` main function is ~15 lines
- [ ] All tests pass
- [ ] No behavioral changes (same inputs → same outputs)

---

## Verification Command
```bash
pytest tests/unit/ui/screens/test_fleet_report_filters.py -v
```

## Next Phase
After all tasks complete, proceed to [phase_3_checklist.md](phase_3_checklist.md).
