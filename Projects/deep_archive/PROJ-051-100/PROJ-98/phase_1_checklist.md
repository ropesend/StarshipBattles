# Phase 1: Fix Event Handling [Simple]

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-98 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Fix the broken `process_event()` so column toggles and filter toggles respond to clicks. This is the root cause of both issues #1 and #3.

---

## Tasks

### Task 1.1: Write event handling tests [Simple]
**File:** `tests/unit/ui/screens/test_empire_build_queue_window.py`
**Tests:** `pytest tests/unit/ui/screens/test_empire_build_queue_window.py -k "event"`

Add `TestProcessEvent` class that verifies buttons dispatch correctly:

- [x] Create mock pygame_gui event with `type=pygame_gui.UI_BUTTON_PRESSED` and `ui_element` set to a column toggle button. Call `process_event()`, verify column visibility changes.
- [x] Create mock event with `ui_element` set to a filter toggle button. Call `process_event()`, verify filter state changes and `apply_filters()` is called.
- [x] Create mock event with `ui_element` set to `btn_apply_filters`. Call `process_event()`, verify search text is read and `apply_filters()` is called.
- [x] Test that unrecognized button clicks don't crash.

**Setup notes:** The test helper `_make_window()` bypasses `__init__` and doesn't build sidebar widgets. Tests must manually populate `column_toggle_buttons`, `filter_toggle_buttons`, and `btn_apply_filters` with mock UIButtons. Mock `_refresh_list` and `_build_header_labels` or `column_mgr.rebuild_headers` to avoid UI calls.

**Notes:** Added `TestProcessEvent` class with 4 tests using `patch.object(UIWindow, 'process_event')` to bypass parent class attribute requirements.

### Task 1.2: Fix process_event() event dispatch [Simple]
**File:** `game/ui/screens/empire_build_queue_window.py` (lines 421-438)
**Tests:** `pytest tests/unit/ui/screens/test_empire_build_queue_window.py -k "event"`

- [x] Add `import pygame_gui` at top of file (line ~19, alongside existing `from pygame_gui.elements import ...`)
- [x] Change line 426 from `if event.type == pygame.USEREVENT:` to `if event.type == pygame_gui.UI_BUTTON_PRESSED:`
- [x] Remove lines 427-430 (`ui_element = getattr(...)`, `user_type = getattr(...)`, `if ui_element is not None and str(user_type) == ...`)
- [x] Replace with: `ui_element = event.ui_element`
- [x] Keep all existing handler calls unchanged (`_handle_column_toggle_click`, `_handle_filter_toggle_click`, `_handle_apply_filters_click`)

**Notes:** Changed from `pygame.USEREVENT` + `user_type` string check to direct `pygame_gui.UI_BUTTON_PRESSED` event type check.

### Task 1.3: Verify all tests pass [Simple]
**Tests:** `pytest tests/unit/ui/screens/test_empire_build_queue_window.py tests/unit/ui/screens/test_empire_build_queue_filter_manager.py -n 4`

- [x] All existing tests still pass
- [x] New event handling tests pass
- [x] Verify: no regressions in filter or column toggle behavior

**Notes:** Full test suite: 7621 passed (up from 7617 baseline, +4 new event handling tests)

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 2
