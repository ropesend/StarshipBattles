# PROJ-245: Spatial Grid Incremental Updates

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-245` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-245 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Add position dirty tracking to Ship | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Add incremental operations to SpatialGrid | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Replace full rebuild with incremental updates in BattleEngine | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Handle entity lifecycle (death/spawn) | Not Started | [phase_4_checklist.md](phase_4_checklist.md) |
| 5. Performance verification and cleanup | Not Started | [phase_5_checklist.md](phase_5_checklist.md) |

## Current State
**Last Updated:** 2026-04-05
**Active Phase:** Planning Complete
**Last Action:** Full codebase analysis and protocol-compliant plan written
**Next Action:** Begin Phase 1 -- write dirty flag tests for Ship
**Blockers:** None

## Overview
The battle engine rebuilds the entire spatial grid every tick by clearing all buckets and re-inserting every alive ship and projectile (`battle_engine.py` lines 416-423). This is O(n) work per tick regardless of whether entities moved. For large battles (50+ ships plus hundreds of in-flight projectiles), this creates unnecessary overhead.

This project implements incremental grid updates:
1. Ships track whether their position changed via a dirty flag
2. The grid provides `update()` and `remove()` operations with entity-to-cell tracking
3. The engine only updates entities that actually moved or changed cells
4. Entity lifecycle (death, spawn) triggers targeted grid operations

The grid must remain perfectly accurate since AI targeting (`controller.py`) and projectile collision (`projectile_manager.py`) depend on `query_radius()` results.

## Goals
- Eliminate full grid rebuild every tick -- only update entities that moved
- Add `update()` and `remove()` operations to `SpatialGrid` alongside existing `insert()`
- Track position changes via dirty flags on ships (projectiles always move, no flag needed)
- Handle entity lifecycle: death triggers removal, spawn triggers insertion
- Maintain identical grid query results -- zero behavioral changes to targeting or collision

## Scope
**In:**
- `game/engine/spatial.py` -- add `update()`, `remove()`, entity-to-cell tracking
- `game/simulation/systems/battle_engine.py` -- replace `grid.clear()` + full rebuild with incremental updates
- `game/engine/physics.py` -- add dirty flag support to PhysicsBody (position mutation tracking)
- `game/simulation/entities/ship_physics.py` -- set dirty flag in `update_physics_movement()` (line 73)
- Tests for all new behavior

**Out:**
- Changing the grid cell size (stays at `PhysicsConfig.SPATIAL_GRID_CELL_SIZE = 2000`)
- Changing the `query_radius` algorithm
- Changing AI controller grid usage (`query_radius` API unchanged)
- Changing `ProjectileManager` grid usage (API unchanged)
- Optimizing `query_radius()` itself
- Multi-cell entities (entities occupy one cell based on center position)

## Key Files
| Component | File Path | Lines of Interest |
|-----------|-----------|-------------------|
| SpatialGrid | `game/engine/spatial.py` | L13-47: full class (48 lines total) |
| BattleEngine tick | `game/simulation/systems/battle_engine.py` | L416-423: grid rebuild per tick |
| BattleEngine start | `game/simulation/systems/battle_engine.py` | L221-300: battle initialization |
| BattleEngine projectile spawn | `game/simulation/systems/battle_engine.py` | L446-453: new attacks added to PM |
| PhysicsBody | `game/engine/physics.py` | L56-112: base class with `position` attr |
| ShipPhysicsMixin | `game/simulation/entities/ship_physics.py` | L73: `self.position += self.velocity` |
| Ship entity | `game/simulation/entities/ship.py` | L32-327: Ship class |
| Ship.die() | `game/simulation/entities/ship.py` | L264-269: death handler |
| Projectile entity | `game/simulation/entities/projectile.py` | L108: `self.position += self.velocity` |
| Projectile.update() | `game/simulation/entities/projectile.py` | L84-119: movement + expiry |
| AI controller (grid consumer) | `game/ai/controller.py` | L124, L131, L418: `query_radius` calls |
| ProjectileManager (grid consumer) | `game/simulation/projectile_manager.py` | L53: `query_radius` call |
| PhysicsConfig | `game/core/config.py` | L104: `SPATIAL_GRID_CELL_SIZE = 2000` |
| Existing grid tests | `tests/unit/systems/test_spatial.py` | 186 lines, basic ops |
| Existing grid edge tests | `tests/unit/systems/test_spatial_edge_cases.py` | 332 lines, boundary cases |

## Decisions Log
| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-04-05 | Track entity-to-cell mapping inside SpatialGrid via `_entity_cells: Dict[int, Tuple[int, int]]` | Grid owns the mapping so `update()` can efficiently remove from old cell and insert into new cell without external state. Uses `id(obj)` as key. |
| 2026-04-05 | Projectiles always update (no dirty flag) | Projectiles move every tick (`projectile.py` L108). Dirty flag overhead would exceed the cost of just calling `grid.update(p)`. Only ships benefit from dirty tracking. |
| 2026-04-05 | Keep `clear()` + `insert()` API for backward compat | `start()` method and many tests use full rebuild. New operations are additive -- `clear()` resets `_entity_cells` too. |
| 2026-04-05 | Dirty flag on PhysicsBody, set in ShipPhysicsMixin.update_physics_movement() | Position is mutated in exactly two places for ships: `ship_physics.py` L73 (`self.position += self.velocity`) and `physics.py` L100 (base `update()`, not used by ships). The mixin is the single mutation point for ships in combat. |
| 2026-04-05 | CollisionSystem does NOT use the grid | Confirmed: `game/engine/collision.py` has zero references to `grid`. It does direct distance checks. Only `AIController` and `ProjectileManager` consume grid queries. |
| 2026-04-05 | Fighters spawned mid-battle need grid.insert() | `battle_engine.py` L478-497 spawns fighters via `self.ships.append(new_ship)`. These must be inserted into the grid on creation. |

## Initial Analysis

### Current Grid Rebuild (battle_engine.py L416-423)
```python
# Every tick -- O(S + P):
self.grid.clear()                              # Drop all buckets + create new dict
alive_ships = [s for s in self.ships if s.is_alive]
for s in alive_ships:
    self.grid.insert(s)                        # Re-hash every alive ship
for p in self.projectiles:
    if p.is_alive:
        self.grid.insert(p)                    # Re-hash every alive projectile
```

For a 50v50 battle with 200 in-flight projectiles: 300 insert operations per tick, every tick. Each insert computes `int(pos.x // cell_size)` and appends to a list in a dict.

### SpatialGrid Current API (spatial.py, 48 lines total)
```python
class SpatialGrid:
    def __init__(self, cell_size=2000):
        self.cell_size = cell_size
        self.buckets: Dict[Tuple[int, int], List[Any]] = {}

    def clear(self) -> None               # self.buckets = {}
    def _get_cell(self, pos) -> (int,int)  # int(pos.x // cell_size), int(pos.y // cell_size)
    def insert(self, obj) -> None          # buckets[cell].append(obj)
    def query_radius(self, pos, radius)    # return candidates from overlapping cells
```
No `remove()`, no `update()`, no entity tracking.

### Grid Consumers (must not break)
1. **AIController** (`controller.py`):
   - L124: `grid.query_radius(ship.get_position(), TARGET_QUERY_RADIUS)` -- target acquisition
   - L131: `grid.query_radius(ship.get_position(), MISSILE_QUERY_RADIUS)` -- missile detection
   - L418: `grid.query_radius(ship.get_position(), AVOIDANCE_RADIUS)` -- obstacle avoidance
2. **ProjectileManager** (`projectile_manager.py`):
   - L53: `grid.query_radius(p_pos, query_radius)` -- projectile-to-ship collision detection
3. **combat_context dict** -- passed to `ship.update(context=...)` containing grid reference

### Entity Position Mutation Points
**Ships (only one mutation point in combat):**
- `ship_physics.py` L73: `self.position += self.velocity` -- called from `Ship.update()` L327 via `self.update_physics_movement()`
- `physics.py` L100: `self.position += self.velocity` -- base PhysicsBody.update(), NOT called for ships (see docstring L85-86)
- `physics.py` L70-80: `x.setter` / `y.setter` -- property setters that mutate `position.x` / `position.y`

**Projectiles (always move):**
- `projectile.py` L108: `self.position += self.velocity` -- every tick in `Projectile.update()`

### Entity Lifecycle Events
- **Ship death:** `ship.die()` at L264 sets `is_alive = False`
- **Ship spawn (fighters):** `battle_engine.py` L478-497 appends to `self.ships`
- **Projectile death:** `projectile.py` L93, L112 sets `is_alive = False`
- **Projectile spawn:** `battle_engine.py` L453 via `projectile_manager.add_projectile(attack)`
- **Projectile collision kill:** `projectile_manager.py` L59 via `_apply_hit()` sets `is_alive = False`

### Cell Size Context
- `SPATIAL_GRID_CELL_SIZE = 2000` pixels
- Ship max speed: typically 10-40 px/tick (a fast ship at 37.5 px/tick)
- At 37.5 px/tick, a ship stays in the same 2000px cell for ~53 ticks before crossing a boundary
- Projectile speed: 200 px/tick (railgun at 20000 raw / 100 scale) -- crosses a cell every ~10 ticks
- **Key insight:** Most ships will NOT cross cell boundaries most ticks, making `update()` a no-op most of the time

### Risk Assessment
- **Medium risk:** Grid accuracy is critical -- targeting and collision depend on it
- **Mitigation:** Integration tests comparing incremental vs full-rebuild query results over N-tick battles
- **Fallback:** Keep `clear()` + full rebuild as a method; can revert tick loop easily

### Existing Test Coverage
- `tests/unit/systems/test_spatial.py` -- 186 lines, 12 tests covering insert/clear/query basics
- `tests/unit/systems/test_spatial_edge_cases.py` -- 332 lines, 17 tests covering boundaries, negative coords, radius=0, many objects
- Both use `MockObject` with a `position` attribute
- No tests for remove/update (don't exist yet)

---

## Phases

### Phase 1: Add Position Dirty Tracking to Ship [Simple]
**Objective:** Ships can report whether their position changed since last grid update.

**Key insight:** Position is mutated in `ship_physics.py` L73 (`self.position += self.velocity`). We add a `_grid_dirty` flag set after position mutation in `update_physics_movement()`. New ships start dirty (need initial insert).

#### Task 1.1: Write tests for dirty flag behavior [Simple]
**File:** `tests/unit/simulation/entities/test_ship_dirty_flag.py`
**Test command:** `pytest tests/unit/simulation/entities/test_ship_dirty_flag.py -v`

- [ ] Create test file with ship fixture using test registries
- [ ] Test: new ship has `_grid_dirty = True` (needs initial grid insert) -- checks `ship._grid_dirty` after construction (`ship.py` L~137)
- [ ] Test: calling `update_physics_movement()` with nonzero velocity sets `_grid_dirty = True`
- [ ] Test: calling `clear_grid_dirty()` sets `_grid_dirty = False`
- [ ] Test: ship at rest (zero velocity) after `clear_grid_dirty()` -- calling `update_physics_movement()` still sets dirty (position += zero_vector still executes at L73)
- [ ] Test: `_grid_dirty` survives multiple update cycles (set, clear, set pattern)
- [ ] Run: `pytest tests/unit/simulation/entities/test_ship_dirty_flag.py -v` -- all fail (no implementation yet)

#### Task 1.2: Implement dirty flag on Ship [Simple]
**File:** `game/simulation/entities/ship.py`
**Test command:** `pytest tests/unit/simulation/entities/test_ship_dirty_flag.py -v`

- [ ] Add `self._grid_dirty: bool = True` in `Ship.__init__()` after L136 (`self.is_alive = True`)
- [ ] Add `def clear_grid_dirty(self) -> None:` method that sets `self._grid_dirty = False`
- [ ] Add `@property def grid_dirty(self) -> bool:` read-only property

**File:** `game/simulation/entities/ship_physics.py`
**Test command:** `pytest tests/unit/simulation/entities/test_ship_dirty_flag.py -v`

- [ ] In `update_physics_movement()`, after L73 (`self.position += self.velocity`), add `self._grid_dirty = True`
- [ ] Run: `pytest tests/unit/simulation/entities/test_ship_dirty_flag.py -v` -- all pass
- [ ] Run: `pytest tests/unit/simulation/entities/ -v` -- no regressions
- [ ] Run: `pytest tests/unit/systems/test_spatial.py tests/unit/systems/test_spatial_edge_cases.py -v` -- no regressions

#### Task 1.3: Verify no other position mutation paths for ships in combat [Simple]
**Verification only -- no code changes expected.**

- [ ] Confirm `PhysicsBody.update()` (physics.py L82-101) is NOT called for ships during combat (docstring L85 says so; `Ship.update()` calls `update_physics_movement()` instead at L327)
- [ ] Confirm `PhysicsBody.x.setter` / `y.setter` (physics.py L70-80) are not called during combat tick loop
- [ ] Confirm fighter spawn sets position via constructor (`PhysicsBody.__init__` at L57: `self.position = Vector2(x, y)`) and Ship.__init__ starts with `_grid_dirty = True`
- [ ] Document: the ONLY combat position mutation point is `ship_physics.py` L73

---

### Phase 2: Add Incremental Operations to SpatialGrid [Medium]
**Objective:** SpatialGrid supports `update()` and `remove()` without full rebuild.

**Key insight:** Add `_entity_cells: Dict[int, Tuple[int, int]]` mapping `id(obj)` to current cell. `update()` checks if entity crossed a cell boundary; if not, it's a no-op. With cell size 2000 and max ship speed ~40 px/tick, most updates are no-ops.

#### Task 2.1: Write tests for new grid operations [Medium]
**File:** `tests/unit/systems/test_spatial_incremental.py`
**Test command:** `pytest tests/unit/systems/test_spatial_incremental.py -v`

- [ ] Create MockObject with mutable position (same pattern as existing tests)
- [ ] Test: `insert()` populates `_entity_cells` mapping -- `id(obj) in grid._entity_cells`
- [ ] Test: `insert()` same object twice raises or overwrites cleanly (decide: overwrite)
- [ ] Test: `remove(obj)` removes from bucket AND from `_entity_cells`
- [ ] Test: `remove(obj)` for non-existent entity is a silent no-op
- [ ] Test: `update(obj)` when entity stays in same cell -- no-op, still findable
- [ ] Test: `update(obj)` when entity moves to new cell -- old cell empty, new cell has it
- [ ] Test: `update(obj)` for untracked entity falls through to `insert()`
- [ ] Test: `query_radius()` returns correct results after sequence of insert/update/remove
- [ ] Test: `clear()` resets `_entity_cells` to empty dict
- [ ] Test: incremental ops produce identical results to clear+rebuild for a sequence of moves
- [ ] Run: `pytest tests/unit/systems/test_spatial_incremental.py -v` -- all fail

#### Task 2.2: Add entity-to-cell tracking to insert() and clear() [Simple]
**File:** `game/engine/spatial.py`
**Test command:** `pytest tests/unit/systems/test_spatial_incremental.py -v`

```python
# In __init__ (after L18):
self._entity_cells: Dict[int, Tuple[int, int]] = {}

# In clear() (after L22):
self._entity_cells = {}

# In insert() (after L33):
self._entity_cells[id(obj)] = cell
```

- [ ] Add `_entity_cells: Dict[int, Tuple[int, int]] = {}` in `__init__()` after L18
- [ ] Update `clear()` at L21 to also clear `self._entity_cells = {}`
- [ ] Update `insert()` at L28-33 to record `self._entity_cells[id(obj)] = cell` after appending to bucket
- [ ] Run: `pytest tests/unit/systems/test_spatial.py tests/unit/systems/test_spatial_edge_cases.py -v` -- existing tests still pass
- [ ] Run: relevant new tests from 2.1 that test insert tracking -- pass

#### Task 2.3: Implement remove() [Simple]
**File:** `game/engine/spatial.py`
**Test command:** `pytest tests/unit/systems/test_spatial_incremental.py -v`

```python
def remove(self, obj: Any) -> None:
    """Remove an object from the grid."""
    obj_id = id(obj)
    cell = self._entity_cells.pop(obj_id, None)
    if cell is not None and cell in self.buckets:
        bucket = self.buckets[cell]
        try:
            bucket.remove(obj)
        except ValueError:
            pass  # Already removed (defensive)
        if not bucket:
            del self.buckets[cell]
```

- [ ] Add `remove(obj)` method after `insert()` (after L33)
- [ ] Handles: entity not tracked (no-op), entity tracked but bucket gone (defensive), empty bucket cleanup
- [ ] Run remove-related tests from 2.1 -- pass

#### Task 2.4: Implement update() [Simple]
**File:** `game/engine/spatial.py`
**Test command:** `pytest tests/unit/systems/test_spatial_incremental.py -v`

```python
def update(self, obj: Any) -> None:
    """Update an object's position in the grid. No-op if cell unchanged."""
    new_cell = self._get_cell(obj.position)
    obj_id = id(obj)
    old_cell = self._entity_cells.get(obj_id)

    if old_cell == new_cell:
        return  # Same cell -- no work needed

    if old_cell is not None:
        # Remove from old bucket
        if old_cell in self.buckets:
            bucket = self.buckets[old_cell]
            try:
                bucket.remove(obj)
            except ValueError:
                pass
            if not bucket:
                del self.buckets[old_cell]

    # Insert into new bucket
    if new_cell not in self.buckets:
        self.buckets[new_cell] = []
    self.buckets[new_cell].append(obj)
    self._entity_cells[obj_id] = new_cell
```

- [ ] Add `update(obj)` method after `remove()`
- [ ] Key optimization: if `old_cell == new_cell`, return immediately (most common case for ships)
- [ ] If entity not tracked (`old_cell is None`), acts as `insert()`
- [ ] Run update-related tests from 2.1 -- pass

#### Task 2.5: Run full grid test suite [Simple]
**Test command:** `pytest tests/unit/systems/ -v -k spatial`

- [ ] All new tests pass: `pytest tests/unit/systems/test_spatial_incremental.py -v`
- [ ] All existing tests pass: `pytest tests/unit/systems/test_spatial.py tests/unit/systems/test_spatial_edge_cases.py -v`
- [ ] Equivalence test passes: incremental ops match clear+rebuild for randomized sequences

---

### Phase 3: Replace Full Rebuild with Incremental Updates in BattleEngine [Medium]
**Objective:** BattleEngine tick loop uses incremental grid updates instead of clear+rebuild.

**Key insight:** The grid rebuild happens at the TOP of each tick (L416-423), before AI/ship updates. After switching to incremental, the grid must still be accurate when AI controllers call `query_radius()` at L124/131/418. The order is: grid update -> AI update -> ship update -> attacks -> projectile update. Since ship positions change during ship update (L327), but the grid is read during AI update (which happens before ship update), the grid reflects LAST tick's positions when AI reads it. This is identical to current behavior -- the current code also rebuilds the grid BEFORE ships move.

#### Task 3.1: Write integration tests [Medium]
**File:** `tests/integration/simulation/test_grid_incremental.py`
**Test command:** `pytest tests/integration/simulation/test_grid_incremental.py -v`

- [ ] Test: run 100-tick battle with 2 ships, verify grid contains exactly the alive entities after each tick
- [ ] Test: run battle with ship death, verify dead ship is not in grid queries after death tick
- [ ] Test: run battle with projectiles, verify projectile positions in grid are current
- [ ] Test: compare grid query results between incremental and full-rebuild for a 50-tick 4v4 battle
- [ ] Run: tests fail (implementation not done yet)

#### Task 3.2: Extract grid update into helper method [Simple]
**File:** `game/simulation/systems/battle_engine.py`
**Test command:** `pytest tests/unit/simulation/systems/test_battle_engine_tick.py -v`

- [ ] Extract L416-423 (the grid rebuild block) into `_update_grid(self) -> None` method
- [ ] Call `self._update_grid()` where the inline code was
- [ ] Run existing battle engine tests -- no regressions

#### Task 3.3: Implement incremental _update_grid() [Medium]
**File:** `game/simulation/systems/battle_engine.py`
**Test command:** `pytest tests/integration/simulation/test_grid_incremental.py -v`

Replace the extracted `_update_grid()` with:
```python
def _update_grid(self) -> None:
    """Update spatial grid incrementally. Only moves entities that changed cells."""
    # Remove dead ships
    for s in self.ships:
        if not s.is_alive:
            self.grid.remove(s)

    # Update alive ships (only those with dirty positions)
    for s in self.ships:
        if s.is_alive and s.grid_dirty:
            self.grid.update(s)
            s.clear_grid_dirty()

    # Update alive projectiles (always move)
    for p in self.projectiles:
        if p.is_alive:
            self.grid.update(p)
        else:
            self.grid.remove(p)
```

- [ ] Replace `_update_grid()` body with incremental logic
- [ ] Note: dead entities are removed first, then alive entities updated
- [ ] Note: `grid.update()` handles untracked entities (new projectiles) via insert fallthrough
- [ ] Run: `pytest tests/integration/simulation/test_grid_incremental.py -v` -- pass
- [ ] Run: `pytest tests/unit/simulation/systems/test_battle_engine_tick.py -v` -- pass

#### Task 3.4: Update start() for initial grid population [Simple]
**File:** `game/simulation/systems/battle_engine.py`
**Test command:** `pytest tests/unit/simulation/systems/test_battle_engine_tick.py -v`

- [ ] After L300 (end of `start()` method), add initial grid population:
```python
# Initial grid population
self.grid.clear()
for s in self.ships:
    self.grid.insert(s)
    s.clear_grid_dirty()
```
- [ ] This ensures grid is populated before first tick and all ships start clean
- [ ] Run: `pytest tests/unit/simulation/systems/ -v` -- pass

#### Task 3.5: Run comprehensive test suites [Simple]
- [ ] `pytest tests/unit/ -n 12` -- all unit tests pass
- [ ] `pytest tests/integration/ -n 12` -- all integration tests pass
- [ ] `python -m simulation_tests.run_tests --fast` -- all simulation tests pass

---

### Phase 4: Handle Entity Lifecycle (Death/Spawn) [Simple]
**Objective:** Dead entities are removed from grid; spawned entities (fighters, projectiles) are inserted promptly.

**Key insight:** The incremental `_update_grid()` from Phase 3 already removes dead entities and handles new projectiles via `grid.update()` fallthrough. This phase handles the remaining case: mid-battle fighter spawns (L478-497) and ensures the projectile manager's dead-projectile cleanup is consistent.

#### Task 4.1: Write lifecycle tests [Simple]
**File:** `tests/integration/simulation/test_grid_lifecycle.py`
**Test command:** `pytest tests/integration/simulation/test_grid_lifecycle.py -v`

- [ ] Test: ship dies mid-battle -- not returned by `query_radius()` on next tick
- [ ] Test: projectile expires (endurance or range) -- not in grid on next tick
- [ ] Test: newly spawned fighter is in grid on next tick after spawn
- [ ] Test: newly fired projectile is in grid on next tick after firing
- [ ] Test: grid entity count matches alive entity count after N ticks
- [ ] Run: tests fail initially

#### Task 4.2: Ensure fighter spawn inserts into grid [Simple]
**File:** `game/simulation/systems/battle_engine.py`
**Test command:** `pytest tests/integration/simulation/test_grid_lifecycle.py -v`

- [ ] After L497 (`self.ships.append(new_ship)` in fighter launch block), add `self.grid.insert(new_ship)` and `new_ship.clear_grid_dirty()`
- [ ] This ensures the fighter is immediately queryable
- [ ] Run: fighter spawn test passes

#### Task 4.3: Verify projectile lifecycle [Simple]
**Verification -- no code changes expected.**

- [ ] Confirm: `projectile_manager.add_projectile()` does NOT insert into grid (L24: just appends to list)
- [ ] Confirm: new projectiles get inserted on next `_update_grid()` call via `grid.update(p)` which falls through to `insert()` for untracked entities
- [ ] Confirm: dead projectiles are removed via `grid.remove(p)` in `_update_grid()`
- [ ] This means new projectiles have a 1-tick delay before appearing in grid -- same as current behavior (they're inserted at start of NEXT tick in the current code too)

#### Task 4.4: Final lifecycle validation [Simple]
- [ ] Run: `pytest tests/integration/simulation/test_grid_lifecycle.py -v` -- all pass
- [ ] Run: `pytest tests/unit/simulation/systems/test_battle_engine_tick.py -v` -- no regressions

---

### Phase 5: Performance Verification and Cleanup [Simple]
**Objective:** Verify correctness across full test suite, clean up any dead code, optionally benchmark.

#### Task 5.1: Full regression testing [Simple]
- [ ] `python scripts/test_sharded.py` -- all tests pass
- [ ] `python -m simulation_tests.run_tests --fast` -- all simulation tests pass
- [ ] `python -m simulation_tests.run_tests` -- all simulation tests including HT pass

#### Task 5.2: Code cleanup [Simple]
- [ ] Verify: `grid.clear()` is only called in `start()` and test setup, never in tick loop
- [ ] Verify: no dead entities remain in grid after any tick (add assertion in debug mode if desired)
- [ ] Verify: all grid consumers (`AIController`, `ProjectileManager`) work identically -- API unchanged
- [ ] Remove any temporary debug code

#### Task 5.3: Documentation updates [Simple]
- [ ] Update `docs/systems/combat_simulation.md` if it documents grid rebuild behavior
- [ ] Update `docs/01_ARCHITECTURE.md` if SpatialGrid API is described there
- [ ] Add `update()` and `remove()` to any API documentation for SpatialGrid

#### Task 5.4: Optional performance benchmark [Simple]
- [ ] Create a simple timing script: run a 1000-tick 20v20 battle, measure average tick time
- [ ] Compare before (full rebuild) vs after (incremental) -- expect modest improvement
- [ ] Log results in decisions.md -- not a hard requirement, just informational

---

## Verification Checklist

### Project Start (REQUIRED)
- [ ] Read `docs/` foundation docs (01_ARCHITECTURE, 02_PATTERNS, 03_CONVENTIONS)
- [ ] Read `docs/systems/combat_simulation.md`
- [ ] Run full test suite -- establish baseline: `python scripts/test_sharded.py`
- [ ] Confirm baseline passes

### After Each Phase
- [ ] Run targeted tests for affected files
- [ ] Verify grid query results are identical to full-rebuild approach
- [ ] No changes to AI targeting behavior
- [ ] No changes to collision detection behavior

### Final Verification
- [ ] `python scripts/test_sharded.py` -- all tests pass
- [ ] `python -m simulation_tests.run_tests --fast` -- all simulation tests pass
- [ ] Grid `clear()` only called in `start()`, not in tick loop
- [ ] No dead entities remain in grid after any tick
- [ ] All grid consumers (AIController, ProjectileManager) work identically
- [ ] Update `docs/` if spatial grid API is documented

---

## Performance Notes

### Expected Improvement
- **Ships:** Most ships hold position or move slowly within a 2000px cell. At max speed ~37.5 px/tick, a ship stays in the same cell for ~53 ticks. In a 50v50 battle, `grid.update()` is a no-op (same-cell check) for most ships most ticks.
- **Projectiles:** Always move at 200+ px/tick, cross cells every ~10 ticks. `grid.update()` still saves the `clear()` + full rebuild cost and avoids re-inserting ships.
- **Cell boundary optimization:** `update()` checks `old_cell == new_cell` first. This is O(1) dict lookup + tuple comparison, much cheaper than hash + append + dict allocation of fresh insert.
- **Memory:** `_entity_cells` dict adds ~64 bytes per entity (id -> tuple). For 300 entities: ~19KB. Negligible.

### Worst Case
If all entities move every tick AND cross cell boundaries every tick, incremental update has slightly MORE overhead than clear+rebuild (due to entity tracking dict lookups and remove-from-list operations). This is unlikely in practice with 2000px cells. The expected common case (ships stationary, projectiles within cells) gives a net win.

### Why Not Track Position in Grid Directly?
The grid stores `obj` references and accesses `obj.position` for cell calculation. An alternative design would cache `(x, y)` inside the grid to detect movement. We chose the dirty-flag approach because:
1. Ships already have a single position mutation point (`ship_physics.py` L73)
2. Dirty flag is cheaper than comparing floats every tick
3. It's explicit about intent (ship moved vs grid checking)

---

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log
