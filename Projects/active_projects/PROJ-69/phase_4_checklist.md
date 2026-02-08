# Phase 4: Controller & Drag Handler - Multi-Queue Support

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-69 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Update BuildQueueController and BuildQueueDragHandler to work with BuildQueueSource and support multi-queue operations.

---

## Tasks

### Task 4.1: Update BuildQueueController for queue sources [Medium]
**File:** `game/ui/panels/build_queue_controller.py`
**Tests:** `pytest tests/integration/ui/build_queue_screen/test_controller_multi_queue.py`

- [x] Add `active_queue_source: Optional[BuildQueueSource]` field (initialized from constructor or setter)
- [x] Add `selected_queue_sources: List[BuildQueueSource]` field (for multi-select)
- [x] Add `set_active_queue(source: BuildQueueSource)` method - updates active queue source
- [x] Add `set_selected_queues(sources: List[BuildQueueSource])` method - updates multi-select list
- [x] Modify `add_to_queue()`:
  - **Single-select mode** (1 queue selected): add to `active_queue_source.construction_queue`
  - **Multi-select mode** (multiple queues selected): iterate `selected_queue_sources`, append to each queue's `construction_queue`
  - **Validation per queue:** Check `source.can_build_ships` or `source.can_build_complexes` based on category before adding
  - Skip queues that can't build the selected type (log warning)
- [x] Refactored into `_add_to_single_queue()`, `_add_to_multiple_queues()`, `_add_to_fallback()` methods
- [x] Added `_source_can_build_category()` for category-to-capability mapping
- [x] Write test: single-queue add works as before (3 tests)
- [x] Write test: multi-queue add appends to all selected queues
- [x] Write test: multi-queue add skips queues that can't build the selected type
- [x] Write test: fallback to build_context when no queue source set
- [x] Verify: 10 controller tests pass

**Notes:** Controller retains build_context as fallback for legacy (non-hex) mode. `_SHIP_CATEGORIES` and `_COMPLEX_CATEGORIES` module-level sets for category mapping.

---

### Task 4.2: Update BuildQueueDragHandler for queue context [Medium]
**File:** `game/ui/panels/build_queue_drag_handler.py`
**Tests:** `pytest tests/integration/ui/build_queue_screen/test_drag_handler_multi_queue.py`

- [x] Update `handle_mouse_down()` - accepts `construction_queue` list + `multi_select_active` flag
- [x] Update `handle_mouse_up()` - accepts `construction_queue` list + `multi_select_active` flag
- [x] Update `handle_mouse_motion()` - accepts `construction_queue` list + `multi_select_active` flag
- [x] Disable drag-drop operations entirely when `multi_select_active=True`:
  - `handle_mouse_down` returns False immediately
  - `handle_mouse_motion` returns False immediately
  - `handle_mouse_up` clears stale state and returns None
- [x] Removed `build_context` parameter from all methods - now takes `construction_queue` list directly
- [x] Write test: drag disabled in multi-select mode (3 tests)
- [x] Write test: drag picks up from queue source's construction_queue
- [x] Write test: drop calls on_add_to_queue correctly
- [x] Verify: 6 drag handler tests pass

**Notes:** Removed Union type imports for BuildContext/Planet/Fleet since handler now receives raw list.

---

### Task 4.3: Update event handling in BuildQueueScreen [Medium]
**File:** `game/ui/screens/build_queue_screen.py`
**Tests:** All existing build queue tests + new tests

- [x] Updated drag handler calls to pass `active_queue.construction_queue` and `multi_select_active` flag
- [x] Updated `_on_queue_selected()` to sync controller via `controller.set_active_queue()`
- [x] Updated `_on_queue_toggled()` to sync controller via `controller.set_active_queue()` or `controller.set_selected_queues()`
- [x] Updated "Remove Selected" button handler to disable in multi-select mode
- [x] Constructor syncs controller only in hex-based multi-queue mode (legacy mode uses fallback)
- [x] Computed `multi_select` and `active_queue` at top of drag handler section for clarity
- [x] Verified: 49 build queue tests pass (10 controller + 6 drag + 33 existing)

**Notes:** Legacy (non-hex) mode preserves dynamic `build_context.can_build_type()` by not setting active_queue_source on controller.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Run `pytest tests/ -n 12` - 6561 passed, 1 pre-existing failure
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 5
