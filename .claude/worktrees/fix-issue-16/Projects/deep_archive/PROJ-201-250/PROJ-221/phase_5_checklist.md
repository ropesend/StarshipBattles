# Phase 5: Drag Handler Adaptation [Medium]

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-221 5`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Refactor DragHandler to work with VirtualTable row indices instead of UIPanel references

---

## Tasks

### Task 5.1: Analyze DragHandler dependencies on old rendering [Simple]
**File:** `game/ui/panels/build_queue_drag_handler.py`
**Tests:** `pytest tests/integration/ui/test_build_queue_drag_drop.py`

- [x] Read `build_queue_drag_handler.py` fully — identified all references
- [x] Documented changes: queue_items -> VirtualTable.handle_click(), 65px -> VirtualTable._row_height, queue_scrollable -> VirtualTable._list_view_panel

**Notes:**

### Task 5.2: Refactor DragHandler to use data-layer indices [Medium]
**File:** `game/ui/panels/build_queue_drag_handler.py`
**Tests:** `pytest tests/integration/ui/test_build_queue_drag_drop.py`

- [x] handle_mouse_down(): Uses virtual_table.handle_click(pos) for row detection
- [x] handle_mouse_up(): Uses virtual_table._row_height for drop index, virtual_table._list_view_panel for position
- [x] Removed queue_index attribute lookups on UIPanel elements
- [x] Updated method signatures to accept VirtualTable instead of queue_items/queue_scrollable
- [x] Drag preview still works (unchanged draw_drag_preview method)

**Notes:** The key change is from "find which UIPanel was clicked" to "ask VirtualTable which row index was clicked". The drag-drop logic (reorder, add, remove) stays the same — only the UI position→data index mapping changes.

### Task 5.3: Update DragHandler tests [Medium]
**File:** `tests/integration/ui/test_build_queue_drag_drop.py`, `tests/integration/ui/build_queue_screen/test_drag_handler_multi_queue.py`
**Tests:** `pytest tests/integration/ui/ -k drag`

- [x] Updated integration tests to use VirtualTable row_pool for positions
- [x] test_reorder_queue and test_remove_from_queue updated and passing
- [x] Run: `pytest tests/integration/ui/ -k drag` — all pass

**Notes:**

### Task 5.4: Update BuildQueueScreen drag integration [Simple]
**File:** `game/ui/screens/build_queue_screen.py`
**Tests:** `pytest tests/unit/ui/screens/test_build_queue_screen.py`

- [x] Updated `_handle_drag_operations()` to pass VirtualTable to DragHandler
- [x] DragHandler gets first chance at mouse events, handles selection via VirtualTable.handle_click()
- [x] Run: `pytest tests/unit/ui/screens/test_build_queue_screen.py` — all 39 pass

**Notes:** Event priority: DragHandler should get first chance at mouse events. If not dragging, fall through to VirtualTable for selection.

### Task 5.5: Run regression check [Simple]
**Tests:** `pytest tests/ --testmon`

- [x] Run `pytest tests/` — 13212 passed, 2 skipped
- [x] Run `pytest tests/repro_issues/test_bug_17_drag_preview.py` — 3 passed

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
