# Phase 3: Fix Intercept Calculation

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-35 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
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

- [ ] Add import for NavigationState and Union
- [ ] Update function signature to accept Union[Fleet, NavigationState]
- [ ] Add isinstance check at function start
- [ ] Extract location, speed, can_warp from either type
- [ ] Update all references to chaser.location → chaser_location, etc.
- [ ] Update find_hybrid_path call to pass can_warp correctly
- [ ] Run pathfinding tests to verify unchanged behavior

**Notes:**

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

- [ ] Update import to use FleetNavigationService
- [ ] Update function call to use service
- [ ] Run pathfinding tests to verify unchanged behavior

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] All tests pass: `pytest tests/unit/strategy/test_pathfinding.py -v`
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
