# Phase 4: Migrate FleetMovementEngine

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-35 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
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

- [ ] Add _nav_service attribute initialization (lazy or in __init__)
- [ ] Replace calculate_next_hex body with delegation
- [ ] Keep all resource consumption in apply_movement (unchanged)
- [ ] Verify no other methods need updating

**Notes:**

---

### Task 4.2: Verify Engine Tests Pass [Simple]
**Tests:** `pytest tests/unit/strategy/test_fleet_movement_engine.py -v`

- [ ] All 26 tests must pass
- [ ] Movement timing preserved (interval = 100 // speed)
- [ ] Resource consumption unchanged

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] All tests pass: `pytest tests/unit/strategy/test_fleet_movement_engine.py -v`
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
