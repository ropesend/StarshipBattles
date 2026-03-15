# Phase 5: Drag Handler Adaptation [Medium]

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-221 5`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Refactor DragHandler to work with VirtualTable row indices instead of UIPanel references

---

## Tasks

### Task 5.1: Analyze DragHandler dependencies on old rendering [Simple]
**File:** `game/ui/panels/build_queue_drag_handler.py`
**Tests:** `pytest tests/integration/ui/test_build_queue_drag_drop.py`

- [ ] Read `build_queue_drag_handler.py` fully — identify all references to:
  - `renderer.queue_items` (list of UIPanel references)
  - Hardcoded 65px row height (line ~277)
  - `queue_scrollable` panel references
  - `queue_index` attribute on UIPanel elements
- [ ] Document each reference point and what it needs to become

**Notes:**

### Task 5.2: Refactor DragHandler to use data-layer indices [Medium]
**File:** `game/ui/panels/build_queue_drag_handler.py`
**Tests:** `pytest tests/integration/ui/test_build_queue_drag_drop.py`

- [ ] Replace `renderer.queue_items` panel list references with VirtualTable queries:
  - `handle_mouse_down()`: Use `virtual_table.find_clicked_row(pos)` to get data index instead of iterating UIPanel list
  - Store clicked data index, not UIPanel reference
- [ ] Replace hardcoded 65px row height:
  - Use `virtual_table._row_height` or pass row_height as constructor parameter
  - Update drop index calculation: `estimated_idx = rel_y // self.row_height`
- [ ] Replace `queue_scrollable` references:
  - Use `virtual_table._list_view_panel` for position calculations
  - Or pass the panel reference to DragHandler at init
- [ ] Remove `queue_index` attribute lookups on UIPanel elements
- [ ] Update constructor to accept VirtualTable reference (or the specific methods/properties needed)
- [ ] Ensure drag preview still works (drawing the dragged item indicator)

**Notes:** The key change is from "find which UIPanel was clicked" to "ask VirtualTable which row index was clicked". The drag-drop logic (reorder, add, remove) stays the same — only the UI position→data index mapping changes.

### Task 5.3: Update DragHandler tests [Medium]
**File:** `tests/integration/ui/test_build_queue_drag_drop.py`, `tests/integration/ui/build_queue_screen/test_drag_handler_multi_queue.py`
**Tests:** `pytest tests/integration/ui/ -k drag`

- [ ] Update test fixtures to provide VirtualTable mock instead of renderer.queue_items
- [ ] Update `test_drag_start_detection` — verify drag starts from VirtualTable row click
- [ ] Update `test_drop_success_and_queue_mutation` — verify drop uses data index
- [ ] Update `test_drag_cancel` — verify cancel works with new system
- [ ] Update `test_queue_reorder_via_drag` — verify reorder still works
- [ ] Run: `pytest tests/integration/ui/ -k drag` — all pass

**Notes:**

### Task 5.4: Update BuildQueueScreen drag integration [Simple]
**File:** `game/ui/screens/build_queue_screen.py`
**Tests:** `pytest tests/unit/ui/screens/test_build_queue_screen.py`

- [ ] Update `_handle_drag_operations()` to pass VirtualTable to DragHandler
- [ ] Ensure MOUSEBUTTONDOWN events reach DragHandler before VirtualTable processes them for selection
- [ ] Verify drag-to-reorder flow: mousedown → drag threshold → visual preview → mouseup → reorder
- [ ] Run: `pytest tests/unit/ui/screens/test_build_queue_screen.py` — all pass

**Notes:** Event priority: DragHandler should get first chance at mouse events. If not dragging, fall through to VirtualTable for selection.

### Task 5.5: Run regression check [Simple]
**Tests:** `pytest tests/ --testmon`

- [ ] Run `pytest tests/ --testmon` — no regressions
- [ ] Run `pytest tests/repro_issues/test_bug_17_drag_preview.py` — passes

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
