# PROJ-410: VirtualTable & DataSource Cache Invalidation Analysis

## Executive Summary

Two recent perf optimizations compose poorly on yard switches with identical geometry:
1. **PROJ-373 phase 3** (`aca743a25`): `VirtualTable._rebuild_row_pool()` skips rebuild when panel dims unchanged
2. **PROJ-376 phase 2** (`a93330bb9`): `BuildQueueScreen.open_for_yard()` reuses a single screen instance

When geometry is identical during yard switch, the row pool is reused with stale widget state (`_last_text`, `_last_img`, `_last_color`), and button handlers retain closures bound to the previous yard context, causing ghost rows and cross-yard action dispatch.

---

## VirtualTable State & Caching

**File:** `game/ui/components/table/virtual_table.py`

### Instance Attributes (Caching)

Key cached attributes:
- `_last_scroll_pct` (line 97): Dirty-track scroll position
- `_last_row_count` (line 98): Dirty-track data row count  
- `_last_pool_dims` (line 103): Cache pool rebuild fingerprint
- `_row_pool[*]["_last_color"]` (line 306): Cached row bg color
- `_row_pool[*]["widgets"][*]["_last_text"]` (line 297): Cached label text
- `_row_pool[*]["widgets"][*]["_last_img"]` (line 242): Cached image surface

### Early-Return Optimization (PROJ-373 Phase 3)

**Lines 184-185**: Early-return skips all widget state reset
```
if self._row_pool and not self._pool_dims_changed():
    return
```

**Critical issue**: `_pool_dims_changed()` (line 175) compares only geometry (height, width, row_height, visible-column fingerprint) against current state. **No data-identity check**: ignores queue length, data source ID, yard, or build context.

**Consequence**: When yard switches with identical geometry, the pool is reused as-is with stale widget caches.

### Widget State Retention on Pool Reuse

When `_rebuild_row_pool()` is skipped (line 184-185):
1. **Row background panels** (`row["bg"]`) are reused
2. **Widget dictionaries** retain all state:
   - `_last_text` (line 297) from previous yard
   - `_last_img` (line 242) from previous yard  
   - `_last_color` (line 306) from previous yard
3. **Button references** in `actions_dict` (line 264) are same objects; no handler re-binding

### Hidden-Row Reset (Incomplete)

**Lines 424-431**: Only clears caches for rows BEYOND new data count
```
else:
    row["bg"].hide()
    row["_last_color"] = None
    for widget in row["widgets"]:
        if widget["type"] == "label":
            widget["_last_text"] = None
        else:
            widget["_last_img"] = None
```

**Critical gap**: Rows reused for new data (indices 0 to N-1) keep stale caches. `update_visible_rows()` line 420 skips updates when `text == widget.get("_last_text")`, so display never refreshes.

### update_visible_rows() Dirty Check

**Lines 318-323**: Entire update skipped if unchanged
```
if (current_pct == self._last_scroll_pct and
    current_count == self._last_row_count):
    return
```

**Issue**: Only checks scroll position and row count, not data identity. No way to detect yard switch with same queue length.

### Text Update Condition

**Line 420**: 
```
if text != widget.get("_last_text"):
    widget["_last_text"] = text
    widget["el"].set_text(text)
```

If `_last_text` was "Cruiser" from yard A and yard B item 0 is also "Cruiser", condition is false and label not updated.

---

## BuildQueueQueueDataSource State

**File:** `game/ui/screens/build_queue_queue_data_source.py`

### Instance Attributes

- `_queue` (line 88): Active queue items
- `_build_rate` (line 89): Per-turn production rate
- `_per_turn_cache` (line 90): Pre-computed spend distribution
- `_columns` (line 86): Column definitions

### set_queue() Method (Lines 92-104)

```
def set_queue(self, queue: List[Dict], build_rate: Dict[str, float]) -> None:
    self._queue = queue
    self._build_rate = build_rate
    self._per_turn_cache = calculate_queue_turn_spend(queue, build_rate)
```

**Critical finding**: No hash, version counter, or generation marker. Data identity is purely list length.

**No cache invalidation methods** exist on this class. `set_queue()` is the only public mutation.

---

## BuildQueueDataSource (Empire) State  

**File:** `game/ui/screens/empire_build_queue_data_source.py`

Read-only wrapper delegating to ViewModel. No mutable state. No reset/invalidate methods.

---

## Call Chain: refresh_queue_display

**File:** `game/ui/screens/build_queue_renderer.py` lines 140-164

Problem sequence:
1. `set_queue()` updates but carries no yard/generation metadata
2. `force_update()` resets scroll/count dirty flags only (does NOT invalidate widget caches)
3. `update_visible_rows()` skips if scroll pct & row count match (lines 319-323)  
4. Pool rebuild skipped if geometry unchanged (line 184-185)
5. **Result**: Stale `_last_text`, `_last_img`, `_last_color` on reused rows

---

## Button Handler Binding

**File:** `game/ui/components/table/virtual_table.py`

### Button Creation (Lines 244-265)

UIButton instances created during `_rebuild_row_pool()`. When pool is reused, button objects are reused.

### Yard Switch (`build_queue_screen.py` lines 317-324)

Controller state updated:
```
self.controller.build_context = yard
self.controller.set_active_queue(source)
```

But if pool is reused, **UIButton instances are the same objects**. If pygame_gui cached handler bindings, old closures remain.

### check_action_button_press() (lines 503-531)

Maps button object to row index via `row.get("row_index", -1)`. Same button reused across yards can dispatch to wrong row index (destructive).

---

## Test Coverage Gaps

**Unit Tests** (`tests/unit/ui/components/table/test_virtual_table.py`):
- 8 tests in TestRowPoolReuseGuard verify pool reuse when dims match
- **Gap**: No test for yard/data-source switch with identical geometry + same queue length

**Unit Tests** (`tests/unit/ui/screens/test_build_queue_queue_data_source.py`):
- TestSetQueue verifies updates on queue switch
- **Gap**: No test for stale cache retention

**Integration Tests** (`tests/integration/ui/build_queue_screen/`):
- **Gap**: No test for ghost rows on identical-geometry yard switch

---

## Missing Invalidation Hooks

No methods exist to:
1. Mark data source as "changed" (no generation counter, hash, or version)
2. Invalidate row-pool widget caches on data switch
3. Force pool rebuild regardless of geometry
4. Re-bind button handlers when pool is reused
5. Clear dirty-tracking flags for widget pool itself

---

## Key Findings Summary

1. **Lines 184-185** (`virtual_table.py`): Early-return skips all widget state reset
2. **Lines 148-175** (`virtual_table.py`): Dimension comparison ignores data identity
3. **Lines 297, 242, 306** (`virtual_table.py`): Widget caches never reset on pool reuse
4. **Lines 424-431** (`virtual_table.py`): Hidden-row reset incomplete; visible rows keep stale caches
5. **Lines 92-104** (`build_queue_queue_data_source.py`): `set_queue()` carries no version/hash
6. **Lines 140-164** (`build_queue_renderer.py`): `force_update()` does not invalidate widget pool
7. **Lines 503-531** (`virtual_table.py`): Button objects reused; closures capture stale context
