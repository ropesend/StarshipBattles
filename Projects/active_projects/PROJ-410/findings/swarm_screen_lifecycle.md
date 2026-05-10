# PROJ-410: Build Queue Widget Cache Invalidation Analysis

## Executive Summary

The `BuildQueueScreen` reused across yards (PROJ-376 Phase 2) creates a persistent widget pool in the `VirtualTable` that **caches row display state** (`_last_text`, `_last_img`, `_last_color`) and is **never cleared between yard switches**. When a second yard's queue has fewer items or different positions, rows from the first yard's data leak into the second display because the pool's cache values don't reflect the new queue.

The screen also **fails to reset selector UI and controller state** before displaying a new yard, causing merged displays, missing yard selector buttons, and phantom row interactions.

---

## Key Findings

### 1. **VirtualTable Row Cache Persists Across Yard Switches**

**File:** `game/ui/components/table/virtual_table.py` (lines 94-307)

The `VirtualTable` maintains a `_row_pool` of pre-built UI widget rows to avoid expensive per-frame widget construction:

- **Line 94:** `self._row_pool: List[Dict[str, Any]] = []` — Pool lifetime spans all yards
- **Lines 177-199:** Pool rebuild checks dimensions but skips rebuild if they match, **without clearing cache**
- **Lines 296-307:** Cache metadata (`_last_text`, `_last_img`, `_last_color`) lives on rows forever

**Impact:** When switching from yard A (10 items) to yard B (5 items), rows 6-10 still hold cached values from A. The `update_visible_rows()` method skips rendering when cache matches, so ghost rows appear.

### 2. **No Pool Cleanup in `open_for_yard()`**

**File:** `game/ui/screens/build_queue_screen.py` (lines 264-344)

`open_for_yard()` does NOT call any cache-flush or pool-reset method:

- **Lines 282-287:** Context-type same → panels reused as-is, including row cache
- **Lines 294-301:** Updates yard state but does NOT clear VirtualTable cache
- **Lines 333-342:** Calls `_refresh_queue_display()` which renders from stale pool

**Missing:** No `self.panels.virtual_table._row_pool.clear()` or similar before refresh.

### 3. **Queue Selector Widget State Partially Persists**

**File:** `game/ui/screens/build_queue_selector.py` (lines 50-87)

The `BuildQueueSelector` stores selected indices and active source. The `refresh()` method (line 89) **does** clear buttons and `_button_index_map`, but the refresh happens AFTER queue_sources is updated, so if yard B has fewer sources than yard A, orphaned button logic may remain.

**Impact:** Clicking phantom buttons for non-existent sources in yard B may crash.

### 4. **Controller Queue Source State NOT Reset**

**File:** `game/ui/panels/build_queue_controller.py` (lines 108-110)

Queue selection state persists across yards:
- `self.active_queue_source` — reference to old yard's source
- `self.selected_queue_sources` — list of old yard's sources

`reset_filters()` only resets category/role, NOT these queue refs. `open_for_yard()` calls `set_active_queue()` but does NOT validate the source is from the NEW yard.

**Impact:** If new yard has fewer sources, controller may dispatch commands for wrong planet/fleet.

### 5. **Drag Handler `selected_design` NOT Reset**

**File:** `game/ui/panels/build_queue_drag_handler.py` (lines 88-100)

`reset_state()` clears drag fields but **misses** `self.selected_design`:

```
def reset_state(self) -> None:
    self.dragged_item = None
    self.drag_preview = None
    self.drag_start_pos = None
    self._pending_queue_index = None
    # MISSING: self.selected_design not cleared!
```

**Impact:** Pressing "Add to Queue" hotkey in yard B adds the design from yard A.

### 6. **Context-Type Same → No Widget Rebuild**

**File:** `game/ui/screens/build_queue_screen.py` (lines 278-287)

Planet→Planet or Fleet→Fleet switches do NOT rebuild panels. The entire widget tree (including row pool and all caches) is reused without reset.

### 7. **VirtualTable Dirty Check Early-Return Masks Cache Issues**

**File:** `game/ui/components/table/virtual_table.py` (lines 318-323)

```
if (current_pct == self._last_scroll_pct and current_count == self._last_row_count):
    return  # Skip entire update if scroll/count unchanged
```

When switching yards with the same scroll position and same queue count (rare but possible), the entire `update_visible_rows()` is skipped, leaving yard A's cell cache visible.

### 8. **No Turn-Boundary Flush Hook**

No hook exists in the UI layer to clear the BuildQueueScreen cache when a player's turn ends and the next player begins. If the screen is still cached, the next player sees the previous player's yard data overlaid on their own.

---

## Persisted State Summary

### Across `open_for_yard()` calls (same context type):

| State | Reset? | Location | Impact |
|-------|--------|----------|--------|
| `_row_pool` | No | VirtualTable:94 | Ghost rows below queue items |
| `_last_text/_last_img/_last_color` on pool rows | No | VirtualTable:296-307 | Wrong display leaks from yard A to yard B |
| `_button_index_map` | Yes | BuildQueueSelector:95 | Refreshed by refresh() |
| `selected_indices` | Partially | BuildQueueSelector:51 | Depends on yard count |
| `active_queue_source` (controller) | No | BuildQueueController:109 | May reference old yard |
| `selected_queue_sources` (controller) | No | BuildQueueController:110 | May reference old yard |
| `selected_category/_role` (controller) | Yes | BuildQueueController:272-273 | Reset by reset_filters() |
| `dragged_item/_pending_queue_index` | Yes | BuildQueueDragHandler:97-100 | Reset by reset_state() |
| **`selected_design`** (drag handler) | **No** | BuildQueueDragHandler:81 | **Old design reused in new yard** |

### Across player turns:

| State | Reset? | Impact |
|-------|--------|--------|
| Entire BuildQueueScreen instance | No | Visible to next player if cached |
| All widget refs in `panels` | No | All widgets carry previous yard state |
| Controller yard/empire context | No | May dispatch commands for wrong player |

---

## Test Coverage Gaps

**File:** `tests/unit/ui/screens/test_build_queue_screen_lifecycle.py`

Covers:
- Shell-only construction
- First `open_for_yard()` call
- Cross-context-type rebuild

**Missing:**
- Same-context-type reuse with cache leaks
- VirtualTable row cache across switches
- Fewer items in yard B than yard A
- Drag handler `selected_design` reset verification
- Turn-boundary scenarios

---

## Root Causes

1. PROJ-376 Phase 2 designed screen reuse but ignored **VirtualTable row widget cache**
2. Pool rebuild optimization skips clearing `_last_text`, `_last_img`, `_last_color`
3. No explicit cache-clear hook in `open_for_yard()`
4. `update_visible_rows()` dirty-check early-return masks stale cache
5. Drag handler `selected_design` field never reset
6. No turn-boundary flush for multi-player scenarios

---

## Files to Investigate

- `game/ui/screens/build_queue_screen.py:264-344` (open_for_yard entry point)
- `game/ui/components/table/virtual_table.py:94-432` (row pool cache)
- `game/ui/panels/build_queue_drag_handler.py:88-100` (reset_state missing selected_design)
- `game/ui/panels/build_queue_controller.py:108-273` (queue source refs not reset)
- `game/ui/screens/build_queue_selector.py:50-133` (selector state)

