# Phase 2 Checklist: Add Incremental Operations to SpatialGrid
**Status:** Not Started

## Task 2.1: Write tests for new grid operations [Medium]
**File:** `tests/unit/systems/test_spatial_incremental.py`
**Tests:** `pytest tests/unit/systems/test_spatial_incremental.py -v`
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
**Notes:**

## Task 2.2: Add entity-to-cell tracking to insert() and clear() [Simple]
**File:** `game/engine/spatial.py`
**Tests:** `pytest tests/unit/systems/test_spatial_incremental.py -v`
- [ ] Add `_entity_cells: Dict[int, Tuple[int, int]] = {}` in `__init__()` after L18
- [ ] Update `clear()` at L21 to also clear `self._entity_cells = {}`
- [ ] Update `insert()` at L28-33 to record `self._entity_cells[id(obj)] = cell` after appending to bucket
- [ ] Run: `pytest tests/unit/systems/test_spatial.py tests/unit/systems/test_spatial_edge_cases.py -v` -- existing tests still pass
- [ ] Run: relevant new tests from 2.1 that test insert tracking -- pass
**Notes:**
```python
# In __init__ (after L18):
self._entity_cells: Dict[int, Tuple[int, int]] = {}

# In clear() (after L22):
self._entity_cells = {}

# In insert() (after L33):
self._entity_cells[id(obj)] = cell
```

## Task 2.3: Implement remove() [Simple]
**File:** `game/engine/spatial.py`
**Tests:** `pytest tests/unit/systems/test_spatial_incremental.py -v`
- [ ] Add `remove(obj)` method after `insert()` (after L33)
- [ ] Handles: entity not tracked (no-op), entity tracked but bucket gone (defensive), empty bucket cleanup
- [ ] Run remove-related tests from 2.1 -- pass
**Notes:**
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

## Task 2.4: Implement update() [Simple]
**File:** `game/engine/spatial.py`
**Tests:** `pytest tests/unit/systems/test_spatial_incremental.py -v`
- [ ] Add `update(obj)` method after `remove()`
- [ ] Key optimization: if `old_cell == new_cell`, return immediately (most common case for ships)
- [ ] If entity not tracked (`old_cell is None`), acts as `insert()`
- [ ] Run update-related tests from 2.1 -- pass
**Notes:**
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

## Task 2.5: Run full grid test suite [Simple]
**Tests:** `pytest tests/unit/systems/ -v -k spatial`
- [ ] All new tests pass: `pytest tests/unit/systems/test_spatial_incremental.py -v`
- [ ] All existing tests pass: `pytest tests/unit/systems/test_spatial.py tests/unit/systems/test_spatial_edge_cases.py -v`
- [ ] Equivalence test passes: incremental ops match clear+rebuild for randomized sequences
**Notes:**
