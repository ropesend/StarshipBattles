# Phase 1 Checklist: Add Position Dirty Tracking to Ship
**Status:** Not Started

## Task 1.1: Write tests for dirty flag behavior [Simple]
**File:** `tests/unit/simulation/entities/test_ship_dirty_flag.py`
**Tests:** `pytest tests/unit/simulation/entities/test_ship_dirty_flag.py -v`
- [ ] Create test file with ship fixture using test registries
- [ ] Test: new ship has `_grid_dirty = True` (needs initial grid insert) -- checks `ship._grid_dirty` after construction (`ship.py` L~137)
- [ ] Test: calling `update_physics_movement()` with nonzero velocity sets `_grid_dirty = True`
- [ ] Test: calling `clear_grid_dirty()` sets `_grid_dirty = False`
- [ ] Test: ship at rest (zero velocity) after `clear_grid_dirty()` -- calling `update_physics_movement()` still sets dirty (position += zero_vector still executes at L73)
- [ ] Test: `_grid_dirty` survives multiple update cycles (set, clear, set pattern)
- [ ] Run: `pytest tests/unit/simulation/entities/test_ship_dirty_flag.py -v` -- all fail (no implementation yet)
**Notes:**

## Task 1.2: Implement dirty flag on Ship [Simple]
**File:** `game/simulation/entities/ship.py`
**Tests:** `pytest tests/unit/simulation/entities/test_ship_dirty_flag.py -v`
- [ ] Add `self._grid_dirty: bool = True` in `Ship.__init__()` after L136 (`self.is_alive = True`)
- [ ] Add `def clear_grid_dirty(self) -> None:` method that sets `self._grid_dirty = False`
- [ ] Add `@property def grid_dirty(self) -> bool:` read-only property

**File:** `game/simulation/entities/ship_physics.py`
**Tests:** `pytest tests/unit/simulation/entities/test_ship_dirty_flag.py -v`
- [ ] In `update_physics_movement()`, after L73 (`self.position += self.velocity`), add `self._grid_dirty = True`
- [ ] Run: `pytest tests/unit/simulation/entities/test_ship_dirty_flag.py -v` -- all pass
- [ ] Run: `pytest tests/unit/simulation/entities/ -v` -- no regressions
- [ ] Run: `pytest tests/unit/systems/test_spatial.py tests/unit/systems/test_spatial_edge_cases.py -v` -- no regressions
**Notes:**

## Task 1.3: Verify no other position mutation paths for ships in combat [Simple]
**Verification only -- no code changes expected.**
- [ ] Confirm `PhysicsBody.update()` (physics.py L82-101) is NOT called for ships during combat (docstring L85 says so; `Ship.update()` calls `update_physics_movement()` instead at L327)
- [ ] Confirm `PhysicsBody.x.setter` / `y.setter` (physics.py L70-80) are not called during combat tick loop
- [ ] Confirm fighter spawn sets position via constructor (`PhysicsBody.__init__` at L57: `self.position = Vector2(x, y)`) and Ship.__init__ starts with `_grid_dirty = True`
- [ ] Document: the ONLY combat position mutation point is `ship_physics.py` L73
**Notes:**
