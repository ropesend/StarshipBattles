# Phase 4: Migrate FleetMovementEngine

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-35 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Update Engine to delegate navigation to the new service

---

## Tasks

### Task 4.1: Update calculate_next_hex [Simple]
**File:** `game/strategy/engine/fleet_movement_engine.py`
**Lines:** 49-113
**Tests:** `pytest tests/unit/strategy/test_fleet_movement_engine.py -v`

Replace implementation with:
```python
def calculate_next_hex(self, fleet: Fleet, galaxy) -> Optional[HexCoord]:
    """Calculate next hex - delegates to FleetNavigationService."""
    from game.strategy.services.fleet_navigation_service import FleetNavigationService

    if not hasattr(self, '_nav_service'):
        self._nav_service = FleetNavigationService()

    return self._nav_service.calculate_fleet_next_hex(fleet, galaxy)
```

- [x] Add _nav_service attribute initialization (lazy or in __init__)
- [x] Replace calculate_next_hex body with delegation
- [x] Keep all resource consumption in apply_movement (unchanged)
- [x] Verify no other methods need updating

**Notes:** Implemented with lazy initialization using `self._nav_service = None` in `__init__`. Cleaned up unused imports (`OrderType`, `find_hybrid_path`, `calculate_intercept_point`). Also updated test patches to reference correct module paths (`game.strategy.services.fleet_navigation_service.find_hybrid_path` instead of `game.strategy.engine.fleet_movement_engine.find_hybrid_path`).

---

### Task 4.2: Verify Engine Tests Pass [Simple]
**Tests:** `pytest tests/unit/strategy/test_fleet_movement_engine.py -v`

- [x] All 29 tests pass (29 not 26 - includes 3 new tests added during implementation)
- [x] Movement timing preserved (interval = 100 // speed)
- [x] Resource consumption unchanged

**Notes:** Updated tests to: (1) Set `fleet.orders = [order]` since NavigationService uses orders list directly, (2) Patch at correct module paths (`game.strategy.services.fleet_navigation_service` instead of `game.strategy.engine.fleet_movement_engine`). Fixed critical bugs: (1) Non-movement orders (COLONIZE, JOIN_FLEET) now preserved instead of being popped, (2) Removed double order-pop bug in `apply_movement()` since `calculate_next_hex` already pops completed orders.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] All tests pass: `pytest tests/unit/strategy/test_fleet_movement_engine.py -v`
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
