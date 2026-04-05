# Phase 4 Checklist: Handle Entity Lifecycle (Death/Spawn)
**Status:** Not Started

## Task 4.1: Write lifecycle tests [Simple]
**File:** `tests/integration/simulation/test_grid_lifecycle.py`
**Tests:** `pytest tests/integration/simulation/test_grid_lifecycle.py -v`
- [ ] Test: ship dies mid-battle -- not returned by `query_radius()` on next tick
- [ ] Test: projectile expires (endurance or range) -- not in grid on next tick
- [ ] Test: newly spawned fighter is in grid on next tick after spawn
- [ ] Test: newly fired projectile is in grid on next tick after firing
- [ ] Test: grid entity count matches alive entity count after N ticks
- [ ] Run: tests fail initially
**Notes:**

## Task 4.2: Ensure fighter spawn inserts into grid [Simple]
**File:** `game/simulation/systems/battle_engine.py`
**Tests:** `pytest tests/integration/simulation/test_grid_lifecycle.py -v`
- [ ] After L497 (`self.ships.append(new_ship)` in fighter launch block), add `self.grid.insert(new_ship)` and `new_ship.clear_grid_dirty()`
- [ ] This ensures the fighter is immediately queryable
- [ ] Run: fighter spawn test passes
**Notes:**

## Task 4.3: Verify projectile lifecycle [Simple]
**Verification -- no code changes expected.**
- [ ] Confirm: `projectile_manager.add_projectile()` does NOT insert into grid (L24: just appends to list)
- [ ] Confirm: new projectiles get inserted on next `_update_grid()` call via `grid.update(p)` which falls through to `insert()` for untracked entities
- [ ] Confirm: dead projectiles are removed via `grid.remove(p)` in `_update_grid()`
- [ ] This means new projectiles have a 1-tick delay before appearing in grid -- same as current behavior (they're inserted at start of NEXT tick in the current code too)
**Notes:**

## Task 4.4: Final lifecycle validation [Simple]
- [ ] Run: `pytest tests/integration/simulation/test_grid_lifecycle.py -v` -- all pass
- [ ] Run: `pytest tests/unit/simulation/systems/test_battle_engine_tick.py -v` -- no regressions
**Notes:**
