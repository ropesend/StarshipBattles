# Phase 5: TestLabScreen MVVM Extraction

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-172 5`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Extract TestLabScreen (1,906 lines, 74 methods) into MVVM architecture. This is the largest and most complex file. It already has 6 extracted helper modules but still manages rendering, input, and UI state directly. This phase creates a ViewModel for UI state, extracts a Renderer for all 19 `_draw_*` methods, and an InputHandler for all click/hover/scroll methods.

**Already Extracted (DO NOT RE-EXTRACT):**
- `test_lab/data_extractor.py` — TestLabDataExtractor
- `test_lab/validation_manager.py` — TestLabValidationManager
- `test_lab/panel_manager.py` — TestLabPanelManager
- `test_lab/test_executor.py` — TestLabExecutor
- `test_lab/dialogs.py` — JSONPopup, ConfirmationDialog
- `test_lab/json_viewer.py` — ScrollableJSONViewer
- `test_lab/test_run_card.py` — TestRunCard

---

## Tasks

### Task 5.1: Create TestLabViewModel [Medium]
**File:** `game/ui/screens/test_lab/screen.py` (read)
**New File:** `game/ui/screens/test_lab/viewmodel.py`
**Tests:** Write new tests in `tests/unit/test_lab/test_viewmodel.py`

- [x] Read `screen.py` fully, catalog all mutable state attributes
- [x] Identify state for ViewModel:
  - [x] `test_list_scroll_offset`, `test_list_max_scroll` — scroll state
  - [x] `update_expected_button_visible`, `update_expected_button_rect` — button visibility
  - [x] `json_popup`, `confirmation_dialog` — dialog visibility flags
  - [x] `ship_panels`, `component_panels`, `results_panel`, `test_details_panel` — panel refs
  - [x] `battle_state_viewer` visibility state
  - [x] `batch_running` state (or delegate to executor)
- [x] Create `game/ui/screens/test_lab/viewmodel.py`:
  - [x] `TestLabViewModel` class
  - [x] `TestLabEvents` class with: `SCROLL_CHANGED`, `PANELS_UPDATED`, `DIALOG_OPENED`, `DIALOG_CLOSED`, `TEST_SELECTED`
  - [x] Constructor: `__init__(self, event_bus)`
  - [x] Coordinate with existing TestLabUIController for business logic
  - [x] Methods: `scroll(delta)`, `open/close_json_popup()`, `open/close_confirmation_dialog()`, etc.
  - [x] Properties: `scroll_offset`, `max_scroll`, `is_dialog_open`, panel references
  - [x] NO Pygame imports
- [x] Write tests:
  - [x] Test scroll state management (offset clamping, max scroll)
  - [x] Test dialog open/close state transitions
  - [x] Test panel update delegation
  - [x] Test event emission
- [x] Run new tests: `pytest tests/unit/test_lab/test_viewmodel.py -v` — 24 passed

**Notes:** ViewModel manages UI state (scroll, dialogs, panel refs) separately from business state (which stays in controller.ui_state)

---

### Task 5.2: Extract TestLabRenderer [Complex]
**File:** `game/ui/screens/test_lab/screen.py` (read)
**New File:** `game/ui/screens/test_lab/renderer.py`
**Tests:** `pytest tests/unit/test_lab/`

- [x] Identify all `_draw_*` methods (19 methods, ~650 lines):
  - [x] `_draw_header()`, `_draw_header_seed_controls()`
  - [x] `_draw_category_sidebar()`, `_draw_tag_filters()`
  - [x] `_draw_test_list()`, `_draw_test_list_scrollbar()`
  - [x] `_draw_metadata_panel()`, `_draw_section()`, `_draw_section_wrapped()`, `_draw_bullet_list()`, `_draw_wrapped_text()`
  - [x] `_draw_validation_section()`, `_draw_validation_flag()`, `_is_condition_verified()`
  - [x] `_draw_output_log()`
- [x] Create `game/ui/screens/test_lab/renderer.py`:
  - [x] `TestLabRenderer` class (1038 lines)
  - [x] Constructor initializes fonts and layout constants
  - [x] Main method: `draw(surface, viewmodel, controller, registry, categories, filtered_scenarios, executor, ui_manager)`
  - [x] Move ALL `_draw_*` methods into renderer
  - [x] Renderer reads state from ViewModel properties — stores button rects back to ViewModel
  - [x] Move rendering-related constants (colors, layout values) to renderer
- [x] Update screen.py `draw()` to delegate to renderer
- [x] Run tests: all passing

**Notes:** Renderer is 1038 lines but is pure rendering logic - no state mutation except storing rects in ViewModel for input handler

---

### Task 5.3: Extract TestLabInputHandler [Complex]
**File:** `game/ui/screens/test_lab/screen.py` (read)
**New File:** `game/ui/screens/test_lab/screen_input_handler.py`
**Tests:** `pytest tests/unit/test_lab/`

- [x] Identify all input handling methods (~12 methods, ~280 lines):
  - [x] `_handle_click()` — main click dispatcher
  - [x] `_check_category_clicks()` — category sidebar clicks
  - [x] `_check_tag_filter_clicks()` — tag filter clicks
  - [x] `_check_test_item_click()` — test list item clicks
  - [x] `_check_action_button_clicks()` — action button clicks
  - [x] `_check_seed_mode_clicks()` — seed control clicks
  - [x] `_handle_scroll_and_mouse()` — scroll + mouse events
  - [x] `_update_hover_state()` — hover tracking
  - [x] `_handle_dialog_events()` — dialog event routing
  - [x] `_handle_panel_events()` — panel event routing
- [x] Create `game/ui/screens/test_lab/screen_input_handler.py`:
  - [x] `TestLabInputHandler` class (388 lines)
  - [x] Constructor takes viewmodel, controller, registry, callbacks dict
  - [x] Methods: `handle_event()`, `_handle_click()`, `_handle_scroll_and_mouse()`, `_update_hover_state()`
  - [x] Input handler calls ViewModel methods for UI state, controller for business state
  - [x] Input handler does NOT import screen.py (uses callbacks instead)
- [x] Update screen.py `handle_input()` to delegate to input handler
- [x] Run tests: all passing

**Notes:** InputHandler uses callback dict pattern to avoid circular dependency with screen

---

### Task 5.4: Refactor TestLabScreen to coordinator [Complex]
**File:** `game/ui/screens/test_lab/screen.py`
**Tests:** `pytest tests/unit/test_lab/`

- [x] Refactor screen to use ViewModel + Renderer + InputHandler:
  - [x] In `__init__`: create EventBus, ViewModel, Renderer, InputHandler
  - [x] Remove all `_draw_*` methods (now in Renderer)
  - [x] Remove all click/hover/scroll handlers (now in InputHandler)
  - [x] Remove scroll state (now in ViewModel)
  - [x] Remove dialog state (now in ViewModel)
  - [x] Keep: lifecycle (`update`, `handle_resize`), UI manager, scene callbacks
  - [x] Keep: delegation to existing services (executor, data_extractor, etc.)
- [x] Screen methods should be thin:
  - [x] `draw()` — delegates to renderer
  - [x] `handle_input()` — delegates to input handler
  - [x] `update()` — delegates to panel updates
- [x] Verify screen public API unchanged (IScene protocol: draw, update, handle_input, handle_resize)
- [x] Run all test lab tests: `pytest tests/unit/test_lab/ -v`
- [x] Fix test fixtures for moved json_popup property
- [x] Verify: TestLabScreen 679 lines (from 1906, 64% reduction)

**Notes:** Screen is 679 lines, exceeds 500 target due to backward compatibility property delegates (~100+ lines). Acceptable given MVVM separation achieved.

---

### Task 5.5: Phase 5 verification [Simple]
**Tests:** `pytest tests/ -n 12`

- [x] Run full test suite: `pytest tests/ -n 12`
- [x] Verify: 12,312 passed, 1 skipped, 0 failures
- [x] Verify line counts:
  - [x] `test_lab/screen.py` = 679 lines (from 1906, 64% reduction)
  - [x] `test_lab/viewmodel.py` = 375 lines, no Pygame imports
  - [x] `test_lab/renderer.py` = 1038 lines
  - [x] `test_lab/screen_input_handler.py` = 388 lines
- [x] Verify: ViewModel independently testable (24 unit tests)
- [x] Verify: Renderer stores rects to ViewModel but no state mutation
- [x] Verify: InputHandler does NOT import screen.py (uses callbacks)

**Notes:** Total MVVM decomposition: 2480 lines across 4 files. Clean separation of concerns achieved.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to "Project Complete"
