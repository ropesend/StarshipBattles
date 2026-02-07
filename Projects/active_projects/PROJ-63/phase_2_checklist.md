# Phase 2: Extract BuildQueueDragHandler

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-63 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Extract drag-and-drop state machine into `game/ui/panels/build_queue_drag_handler.py`

---

## Tasks

### Task 2.1: Create BuildQueueDragHandler class [Complex]
**File:** `game/ui/panels/build_queue_drag_handler.py` (NEW)
**Tests:** `pytest tests/integration/ui/test_build_queue_drag_drop.py tests/repro_issues/test_bug_17_drag_preview.py`

- [ ] Create `game/ui/panels/build_queue_drag_handler.py` with class `BuildQueueDragHandler`
- [ ] Constructor: `__init__(self, portrait_loader, design_library, on_add_to_queue, on_refresh_queue, on_refresh_design_report)`
  - `portrait_loader`: `BuildQueuePortraitLoader` instance
  - `design_library`: for scanning designs during drag start
  - `on_add_to_queue(design_id, turns, category, index)`: callback to add item to queue
  - `on_refresh_queue()`: callback to refresh queue display after reorder
  - `on_refresh_design_report(design_id)`: callback to update design report on selection
- [ ] Move drag state from `BuildQueueScreen.__init__` into handler:
  - `self.dragged_item = None` (line 57)
  - `self.drag_preview = None` (line 58)
  - `self.drag_start_pos = None` (line 60)
  - `self.drag_threshold = 10` (line 61)
  - `self._pending_queue_index = None`
  - `self.selected_design = None` (line 54 — shared between drag and selection)
- [ ] Create `handle_mouse_down(self, event, items_scrollable, queue_items, planet, selected_category)` method
  - Extract from `handle_event()` lines 727-763
  - Design button hit-testing + drag start from items list
  - Queue item tracking for potential drag
  - Returns whether event was handled
- [ ] Create `handle_mouse_motion(self, event, planet)` method
  - Extract from `handle_event()` lines 766-794
  - Drag threshold check
  - Queue item pickup on exceeding threshold
- [ ] Create `handle_mouse_up(self, event, build_queue_panel, queue_scrollable, planet)` method
  - Extract from `handle_event()` lines 797-837
  - Click-vs-drag detection for queue selection
  - Drop handling (into queue vs outside)
  - Returns `selected_queue_index` if click-select occurred
- [ ] Create `draw_drag_preview(self, screen)` method
  - Extract from `build_queue_screen.py` `draw()` lines 902-945
  - Renders portrait icon following cursor with shadow and border
  - Includes fallback colored square when no portrait
- [ ] Add property `is_dragging` -> `bool` (returns `self.dragged_item is not None`)
- [ ] Add necessary imports: `pygame`, `log_info` from `game.core.logger`

### Task 2.2: Wire BuildQueueDragHandler into BuildQueueScreen [Medium]
**File:** `game/ui/screens/build_queue_screen.py`
**Tests:** `pytest tests/integration/ui/test_build_queue_drag_drop.py tests/repro_issues/test_bug_17_drag_preview.py`

- [ ] Add import: `from game.ui.panels.build_queue_drag_handler import BuildQueueDragHandler`
- [ ] In `__init__`, create instance after portrait_loader:
  ```python
  self.drag_handler = BuildQueueDragHandler(
      portrait_loader=self.portrait_loader,
      design_library=self.design_library,
      on_add_to_queue=self._add_to_queue,
      on_refresh_queue=self._refresh_queue_display,
      on_refresh_design_report=self._refresh_design_report
  )
  ```
- [ ] Remove drag state from `__init__`: `dragged_item`, `drag_preview`, `drag_start_pos`, `drag_threshold`, `selected_design`
- [ ] In `handle_event()`, replace inline drag-drop code with handler delegation:
  - Replace MOUSEBUTTONDOWN block (lines 727-763) with `self.drag_handler.handle_mouse_down(...)`
  - Replace MOUSEMOTION block (lines 766-794) with `self.drag_handler.handle_mouse_motion(...)`
  - Replace MOUSEBUTTONUP block (lines 797-837) with `self.drag_handler.handle_mouse_up(...)`
- [ ] Update `selected_design` references to use `self.drag_handler.selected_design`:
  - In `handle_event()` btn_add_to_queue check (line 711)
- [ ] In `draw()`, replace drag preview rendering (lines 902-945) with `self.drag_handler.draw_drag_preview(screen)`
- [ ] Delete removed code blocks from `handle_event()` and `draw()`
- [ ] Verify: `self.dragged_item` no longer referenced directly in screen

### Task 2.3: Update tests if needed [Simple]
**Tests:** `pytest tests/integration/ui/test_build_queue_drag_drop.py tests/repro_issues/test_bug_17_drag_preview.py`

- [ ] Check if any tests access `screen.dragged_item` directly — update to `screen.drag_handler.dragged_item`
- [ ] Check if any tests access `screen.selected_design` directly — update to `screen.drag_handler.selected_design`
- [ ] Run drag-drop tests: `pytest tests/integration/ui/test_build_queue_drag_drop.py -v`
- [ ] Run bug 17 tests: `pytest tests/repro_issues/test_bug_17_drag_preview.py -v`

### Task 2.4: Run full suite [Simple]
**Tests:** `pytest tests/ -x -q`

- [ ] Run full test suite: `pytest tests/ -x -q`
- [ ] Verify 6248 tests still pass
- [ ] Verify `build_queue_screen.py` reduced further (should be ~650 lines, down ~195 from Phase 1 end)

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
