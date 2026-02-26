# Phase 3: Refactor Main Function

**Goal:** Replace the complex `filter_ships` implementation with calls to helper functions.

**File:** `game/ui/screens/fleet_report_filters.py`

---

## Pre-Flight
- [ ] Run baseline: `pytest tests/unit/ui/screens/test_fleet_report_filters.py -v`
- [ ] Verify all tests pass before starting
- [ ] Verify helpers from Phase 2 are in place

---

## Task 3.1: Replace `filter_ships` Implementation

**Purpose:** Simplify the main function to use extracted helpers.

**Location:** Lines 124-222, replace entire function body

**New implementation:**
```python
def filter_ships(ships: List[ShipInstance], filter_state: Dict[str, bool]) -> List[ShipInstance]:
    """
    Filter ships based on status filter state.

    Args:
        ships: List of ShipInstance objects
        filter_state: Dict with filter keys (all default to True if missing):
            - show_damaged: Include damaged ships
            - show_undamaged: Include undamaged ships
            - show_derelict: Include derelict ships
            - show_destroyed: Include destroyed ships
            - show_warp_capable: Include warp-capable ships
            - show_not_warp_capable: Include ships without warp capability
            - show_has_spaceyard: Include ships with spaceyards
            - show_no_spaceyard: Include ships without spaceyards
            - show_has_cargo: Include ships with cargo
            - show_no_cargo: Include ships without cargo
            - show_can_<ability>: Include ships with special ability
            - show_no_<ability>: Include ships without special ability

    Returns:
        Filtered list of ships
    """
    result = []
    for ship in ships:
        # Check capability filters (warp, spaceyard, cargo, special abilities)
        if not _passes_capability_filters(ship, filter_state):
            continue

        # Check status filter (destroyed/derelict/damaged/undamaged)
        if not _passes_status_filter(ship, filter_state):
            continue

        result.append(ship)

    return result
```

- [ ] Replace `filter_ships` function body with new implementation
- [ ] Preserve the docstring (update if needed for clarity)
- [ ] Run tests: `pytest tests/unit/ui/screens/test_fleet_report_filters.py -v`
- [ ] ALL TESTS MUST PASS - if any fail, investigate immediately

---

## Task 3.2: Verify Behavior Preservation

**Purpose:** Ensure refactoring didn't change any behavior.

- [ ] Run full test suite: `pytest tests/ --testmon`
- [ ] Run view model tests: `pytest tests/unit/ui/test_fleet_list_view_model.py -v`
- [ ] Verify all 46+ related tests pass

---

## Task 3.3: Measure New Complexity

**Purpose:** Verify CC reduction meets target.

- [ ] Run complexity check: `python -m radon cc game/ui/screens/fleet_report_filters.py -s -a`
- [ ] Record new CC for `filter_ships` (target: <10)
- [ ] Record CC for each helper function
- [ ] Verify no individual function exceeds CC=20

**Expected results:**
| Function | Expected CC |
|----------|-------------|
| `filter_ships` | 3-5 |
| `_passes_capability_filters` | 8-12 |
| `_passes_boolean_filter` | 3-4 |
| `_passes_status_filter` | 1-2 |
| `_get_ship_status` | 4 |

---

## Verification
- [ ] All tests pass
- [ ] `filter_ships` CC < 10
- [ ] No function exceeds CC=20
- [ ] Ready to proceed to Phase 4

---

## Completion Criteria
- `filter_ships` refactored to use helpers
- All 46+ related tests pass
- CC significantly reduced
- No behavioral changes
