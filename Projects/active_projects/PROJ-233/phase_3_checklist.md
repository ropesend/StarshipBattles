# Phase 3: Simplify Main Function

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-233 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Refactor `filter_ships` to use extracted helpers, reducing its CC.

**Prerequisites:** Phase 2 must be complete (helpers extracted).

---

## Tasks

### Task 3.1: Refactor `filter_ships` [Medium]
**File:** `game/ui/screens/fleet_report_filters.py`
**Tests:** `pytest tests/unit/ui/screens/test_fleet_report_filters.py -v`

Replace the entire body of `filter_ships` (lines 141-222) with:

```python
def filter_ships(ships: List[ShipInstance], filter_state: Dict[str, bool]) -> List[ShipInstance]:
    """
    Filter ships based on status filter state.

    Args:
        ships: List of ShipInstance objects
        filter_state: Dict with keys:
            - show_damaged: Include damaged ships
            - show_undamaged: Include undamaged ships
            - show_derelict: Include derelict ships
            - show_destroyed: Include destroyed ships
            - show_warp_capable: Include warp-capable ships
            - show_not_warp_capable: Include ships without warp capability
            - show_has_spaceyard: Include ships with spaceyard
            - show_no_spaceyard: Include ships without spaceyard
            - show_has_cargo: Include ships with cargo
            - show_no_cargo: Include ships without cargo
            - show_can_X / show_no_X: Special capability filters

    Returns:
        Filtered list of ships
    """
    return [
        ship for ship in ships
        if _passes_capability_filters(ship, filter_state)
        and _passes_status_filter(ship, filter_state)
    ]
```

- [ ] Replace `filter_ships` body with list comprehension
- [ ] Preserve docstring (update if needed)
- [ ] Run tests: `pytest tests/unit/ui/screens/test_fleet_report_filters.py -v`
- [ ] Verify all tests still pass

**Notes:**

---

### Task 3.2: Verify CC Reduction [Simple]
**Tests:** `radon cc game/ui/screens/fleet_report_filters.py -s -a`

- [ ] Run `radon cc game/ui/screens/fleet_report_filters.py -s -a`
- [ ] Verify `filter_ships` CC is now < 5
- [ ] Verify all helpers are below threshold (< 20 each)
- [ ] Document actual CC values in notes below

**Expected results:**
- `filter_ships`: CC 2-3
- `_passes_binary_filter`: CC 3
- `_passes_capability_filters`: CC 8-10
- `_passes_status_filter`: CC 5

**Notes:** (Record actual CC values here)

---

### Task 3.3: Run Integration Tests [Simple]
**Tests:** `pytest tests/unit/ui/ -v --tb=short`

- [ ] Run broader UI test suite: `pytest tests/unit/ui/ -v --tb=short`
- [ ] Verify `FleetListViewModel` tests still pass
- [ ] No regressions in related components

**Notes:**

---

## Verification Commands

```bash
# Full filter test suite
pytest tests/unit/ui/screens/test_fleet_report_filters.py -v

# Broader UI tests
pytest tests/unit/ui/ -v --tb=short

# Check complexity
radon cc game/ui/screens/fleet_report_filters.py -s -a

# Verify no other test regressions
pytest tests/ -n 12 --tb=line -q
```

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `filter_ships` refactored to use helpers
- [ ] CC verified below 20 for all functions
- [ ] All tests passing
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 4
