# Phase 4: Controller & Drag Handler - Multi-Queue Support

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-69 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Update BuildQueueController and BuildQueueDragHandler to work with BuildQueueSource and support multi-queue operations.

---

## Tasks

### Task 4.1: Update BuildQueueController for queue sources [Medium]
**File:** `game/ui/panels/build_queue_controller.py`
**Tests:** `pytest tests/unit/ui/ -k "build_queue"`

- [ ] Add `active_queue_source: Optional[BuildQueueSource]` field (initialized from constructor or setter)
- [ ] Add `selected_queue_sources: List[BuildQueueSource]` field (for multi-select)
- [ ] Add `set_active_queue(source: BuildQueueSource)` method - updates active queue source
- [ ] Add `set_selected_queues(sources: List[BuildQueueSource])` method - updates multi-select list
- [ ] Modify `add_to_queue()` (lines 109-159):
  - **Single-select mode** (1 queue selected): add to `active_queue_source.construction_queue` (same as current behavior, just different reference)
  - **Multi-select mode** (multiple queues selected): iterate `selected_queue_sources`, append to each queue's `construction_queue`
  - **Validation per queue:** Check `source.can_build_ships` or `source.can_build_complexes` based on category before adding
  - Skip queues that can't build the selected type (log warning)
- [ ] Update `can_build_type` checks: instead of `self.build_context.can_build_type(cat)`, check `source.can_build_ships`/`source.can_build_complexes`
- [ ] Write test: single-queue add works as before
- [ ] Write test: multi-queue add appends to all selected queues
- [ ] Write test: multi-queue add skips queues that can't build the selected type (e.g., base queue skips ships)
- [ ] Verify: run controller tests

**Notes:** The controller no longer needs a single `build_context` - it works with `BuildQueueSource` instances.

---

### Task 4.2: Update BuildQueueDragHandler for queue context [Medium]
**File:** `game/ui/panels/build_queue_drag_handler.py`
**Tests:** `pytest tests/unit/ui/ -k "drag"`

- [ ] Update `handle_mouse_down()` to work with active_queue_source's `construction_queue` instead of `build_context.construction_queue`
- [ ] Update `handle_mouse_up()` drop logic: insert into `active_queue_source.construction_queue` instead of `build_context.construction_queue`
- [ ] Update `handle_mouse_motion()`: drag reorder uses `active_queue_source.construction_queue`
- [ ] Disable drag-drop operations entirely when in multi-select mode (multiple queues selected):
  - Check if multi-select is active before starting drag
  - Return early from drag operations in multi-select mode
- [ ] Update method signatures to receive `active_queue_source` or its `construction_queue` instead of `build_context`
- [ ] Write test: drag reorder works in single-select mode
- [ ] Write test: drag disabled in multi-select mode

**Notes:** The drag handler should receive queue source info from the screen. In multi-select mode, drag-drop doesn't make sense (which queue would you reorder?).

---

### Task 4.3: Update event handling in BuildQueueScreen [Medium]
**File:** `game/ui/screens/build_queue_screen.py`
**Tests:** Manual test + existing tests

- [ ] Update `handle_event()` (lines 517-597):
  - Add queue selector click event handling:
    - Detect clicks on queue selector rows
    - Regular click → `_on_queue_selected(index)`
    - Ctrl+click → `_on_queue_toggled(index)`
  - Update "Add to Queue" button handler (line 553-555):
    - Pass `active_queue_source` or `selected_queue_sources` to controller
  - Update "Remove Selected" button handler (lines 558-566):
    - Use `self.active_queue_source.construction_queue.pop(idx)` instead of `self.build_context.construction_queue.pop(idx)`
    - Disable remove in multi-select mode
- [ ] Update drag handler calls (lines 570-586):
  - Pass `active_queue_source` instead of `build_context` to drag handler methods
  - Pass `active_queue_source.construction_queue` where `build_context` was used
- [ ] Update `_refresh_queue_display()` call to update queue selector item counts
- [ ] Update `draw()` (lines 633-652): selection highlight uses `active_queue_source.construction_queue`

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Run `pytest tests/ --testmon` - all affected tests pass
- [ ] Manual test: add item in single-select mode works
- [ ] Manual test: add item in multi-select mode adds to all selected
- [ ] Manual test: drag reorder works in single-select, disabled in multi-select
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 5
