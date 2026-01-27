# Phase 2: Create FleetNavigationService

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-35 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Build the unified service with core navigation logic

---

## Tasks

### Task 2.1: Create NavigationState Dataclass [Simple]
**File:** `game/strategy/services/fleet_navigation_service.py` (NEW)
**Tests:** `pytest tests/unit/strategy/test_fleet_navigation_service.py -v`

```python
@dataclass(frozen=True)
class NavigationState:
    """Immutable snapshot for all navigation calculations."""
    location: HexCoord
    path: tuple[HexCoord, ...]  # Immutable tuple
    orders: tuple[FleetOrder, ...]
    speed: float
    can_warp: bool  # Pre-computed from fleet

    @classmethod
    def from_fleet(cls, fleet: Fleet) -> 'NavigationState':
        return cls(
            location=fleet.location,
            path=tuple(fleet.path),
            orders=tuple(fleet.orders),
            speed=fleet.speed,
            can_warp=fleet.can_use_warp() if hasattr(fleet, 'can_use_warp') else True
        )
```

- [ ] Create new file `game/strategy/services/fleet_navigation_service.py`
- [ ] Create dataclass with frozen=True
- [ ] Add from_fleet() factory method
- [ ] Include can_warp field to eliminate fake fleet hack

**Notes:**

---

### Task 2.2: Create PathSegment and NavigationStep [Simple]
**File:** `game/strategy/services/fleet_navigation_service.py`

```python
@dataclass(frozen=True)
class PathSegment:
    start: HexCoord
    end: HexCoord
    turn: int
    is_warp: bool

    def to_dict(self) -> dict:
        return {'start': self.start, 'end': self.end, 'turn': self.turn,
                'is_warp': self.is_warp, 'hex': self.end}

@dataclass(frozen=True)
class NavigationStep:
    next_hex: Optional[HexCoord]
    new_state: NavigationState
    order_complete: bool = False
```

- [ ] Move PathSegment from fleet_movement.py
- [ ] Create NavigationStep for step results

**Notes:**

---

### Task 2.3: Implement Core Navigation Methods [Medium]
**File:** `game/strategy/services/fleet_navigation_service.py`

- [ ] Implement `get_destination(state, order, galaxy) -> Optional[HexCoord]`
  - Handle MOVE: return order.target
  - Handle MOVE_TO_FLEET: call calculate_intercept_point with NavigationState
  - Handle others: return None
- [ ] Implement `compute_path(state, destination, galaxy) -> list[HexCoord]`
  - Wrap find_hybrid_path
  - Remove start hex if equals current location
- [ ] Implement `compute_next_step(state, galaxy) -> NavigationStep`
  - Pure function, no mutation
  - Handle path recalculation when destination changes
  - Handle order completion
- [ ] Implement `_needs_path_recalculation(state, destination) -> bool`
  - Check if path[-1] != destination

**Notes:**

---

### Task 2.4: Implement Projection Methods [Medium]
**File:** `game/strategy/services/fleet_navigation_service.py`

- [ ] Implement `project_path(fleet, galaxy, max_turns) -> list[PathSegment]`
  - Port from FleetMovementSimulator.project_path()
  - Use NavigationState internally
  - Preserve max_iterations safety limit
- [ ] Implement `project_path_as_dicts(fleet, galaxy, max_turns) -> list[dict]`
  - Wrapper that converts PathSegments to dicts

**Notes:**

---

### Task 2.5: Implement Execution Wrapper [Medium]
**File:** `game/strategy/services/fleet_navigation_service.py`

```python
def calculate_fleet_next_hex(self, fleet: Fleet, galaxy) -> Optional[HexCoord]:
    """
    Calculate next hex for fleet, applying state changes to mutable Fleet.
    Used by FleetMovementEngine for turn execution.
    """
    state = NavigationState.from_fleet(fleet)
    step = self.compute_next_step(state, galaxy)

    if step.next_hex is None:
        if step.order_complete:
            fleet.pop_order()
        return None

    # Apply state changes to mutable fleet
    fleet.path = list(step.new_state.path)
    if step.order_complete:
        fleet.pop_order()

    return step.next_hex
```

- [ ] Implement calculate_fleet_next_hex() with mutation bridge
- [ ] Handle order completion correctly
- [ ] Handle path updates correctly

**Notes:**

---

### Task 2.6: Create Unit Tests [Medium]
**File:** `tests/unit/strategy/test_fleet_navigation_service.py` (NEW)
**Tests:** `pytest tests/unit/strategy/test_fleet_navigation_service.py -v`

- [ ] Test NavigationState.from_fleet() creates correct snapshot
- [ ] Test get_destination() for MOVE orders
- [ ] Test get_destination() for MOVE_TO_FLEET orders
- [ ] Test compute_path() path normalization (removes start hex)
- [ ] Test compute_next_step() is pure (doesn't mutate input)
- [ ] Test project_path() produces correct segments

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] All tests pass: `pytest tests/unit/strategy/test_fleet_navigation_service.py -v`
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
