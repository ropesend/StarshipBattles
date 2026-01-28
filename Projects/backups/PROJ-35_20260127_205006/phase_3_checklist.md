# Phase 3: Fix Intercept Calculation

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-35 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Update calculate_intercept_point to accept NavigationState

---

## Tasks

### Task 3.1: Update calculate_intercept_point Signature [Medium]
**File:** `game/strategy/data/pathfinding.py`
**Lines:** 229-370
**Tests:** `pytest tests/unit/strategy/test_pathfinding.py -v`

Change from:
```python
def calculate_intercept_point(chaser_fleet, target_fleet, galaxy):
```

To:
```python
def calculate_intercept_point(
    chaser: Union[Fleet, NavigationState],
    target_fleet: Fleet,
    galaxy
) -> Optional[HexCoord]:
    # Support both Fleet and NavigationState for backward compatibility
    if isinstance(chaser, NavigationState):
        chaser_location = chaser.location
        chaser_speed = chaser.speed
        chaser_id = -1  # Projection context
        chaser_can_warp = chaser.can_warp
    else:
        chaser_location = chaser.location
        chaser_speed = chaser.speed
        chaser_id = chaser.id
        chaser_can_warp = chaser.can_use_warp() if hasattr(chaser, 'can_use_warp') else True
```

- [x] Add import for NavigationState and Union
- [x] Update function signature to accept Union[Fleet, NavigationState]
- [x] Add isinstance check at function start
- [x] Extract location, speed, can_warp from either type
- [x] Update all references to chaser.location → chaser_location, etc.
- [x] Update find_hybrid_path call to pass can_warp correctly
- [x] Run pathfinding tests to verify unchanged behavior

**Notes:** Implemented using ChaserProxy class to pass to find_hybrid_path (which needs a fleet-like object with id and can_use_warp()). Added 4 new tests for NavigationState support. Updated FleetNavigationService.get_destination() to pass NavigationState directly instead of fake fleet-like object.

---

### Task 3.2: Update project_fleet_path [Simple]
**File:** `game/strategy/data/pathfinding.py`
**Lines:** 209-227
**Tests:** `pytest tests/unit/strategy/test_pathfinding.py -v`

Change from:
```python
from game.strategy.engine.fleet_movement import FleetMovementSimulator
simulator = FleetMovementSimulator()
return simulator.project_path_as_dicts(fleet, galaxy, max_turns)
```

To:
```python
from game.strategy.services.fleet_navigation_service import FleetNavigationService
service = FleetNavigationService()
return service.project_path_as_dicts(fleet, galaxy, max_turns)
```

- [x] Update import to use FleetNavigationService
- [x] Update function call to use service
- [x] Run pathfinding tests to verify unchanged behavior

**Notes:** Updated project_fleet_path to use FleetNavigationService instead of FleetMovementSimulator. Also fixed fleet_like object in compute_path() to include `id` field and proper `self` parameter in lambda.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] All tests pass: `pytest tests/unit/strategy/test_pathfinding.py -v`
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
