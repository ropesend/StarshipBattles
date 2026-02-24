# Phase 5: TestLabScreen MVVM Extraction

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-172 5`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
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

- [ ] Read `screen.py` fully, catalog all mutable state attributes
- [ ] Identify state for ViewModel:
  - [ ] `test_list_scroll_offset`, `test_list_max_scroll` — scroll state
  - [ ] `update_expected_button_visible`, `update_expected_button_rect` — button visibility
  - [ ] `json_popup`, `confirmation_dialog` — dialog visibility flags
  - [ ] `ship_panels`, `component_panels`, `results_panel`, `test_details_panel` — panel refs
  - [ ] `battle_state_viewer` visibility state
  - [ ] `batch_running` state (or delegate to executor)
- [ ] Create `game/ui/screens/test_lab/viewmodel.py`:
  - [ ] `TestLabViewModel` class
  - [ ] `TestLabEvents` class with: `SCROLL_CHANGED`, `PANELS_UPDATED`, `DIALOG_OPENED`, `DIALOG_CLOSED`, `BATCH_STATE_CHANGED`
  - [ ] Constructor: `__init__(self, event_bus, controller, panel_manager, executor)`
  - [ ] Coordinate with existing TestLabUIController for business logic
  - [ ] Methods: `scroll(delta)`, `update_panels(test_id)`, `show_json_popup(data)`, `show_confirmation(...)`, `start_batch()`, `continue_batch()`
  - [ ] Properties: `scroll_offset`, `max_scroll`, `is_dialog_open`, `current_panels`
  - [ ] NO Pygame imports
- [ ] Write tests:
  - [ ] Test scroll state management (offset clamping, max scroll)
  - [ ] Test dialog open/close state transitions
  - [ ] Test panel update delegation to PanelManager
  - [ ] Test event emission
- [ ] Run new tests: `pytest tests/unit/test_lab/test_viewmodel.py -v`

**Notes:**

---

### Task 5.2: Extract TestLabRenderer [Complex]
**File:** `game/ui/screens/test_lab/screen.py` (read)
**New File:** `game/ui/screens/test_lab/renderer.py`
**Tests:** `pytest tests/unit/test_lab/`

- [ ] Identify all `_draw_*` methods (19 methods, ~650 lines):
  - [ ] `_draw_header()`, `_draw_header_seed_controls()`
  - [ ] `_draw_category_sidebar()`, `_draw_tag_filters()`
  - [ ] `_draw_test_list()`, `_draw_test_list_scrollbar()`
  - [ ] `_draw_metadata_panel()`, `_draw_section()`, `_draw_section_wrapped()`, `_draw_bullet_list()`, `_draw_wrapped_text()`
  - [ ] `_draw_validation_section()`, `_draw_validation_flag()`, `_is_condition_verified()`
  - [ ] Any other `_draw_*` methods
- [ ] Create `game/ui/screens/test_lab/renderer.py`:
  - [ ] `TestLabRenderer` class
  - [ ] Constructor takes layout constants (widths, heights, fonts)
  - [ ] Main method: `draw(surface, viewmodel, controller)` — reads state from ViewModel and controller
  - [ ] Move ALL `_draw_*` methods into renderer
  - [ ] Renderer reads state from ViewModel properties — does NOT mutate anything
  - [ ] Move rendering-related constants (colors, layout values) to renderer
- [ ] Update screen.py `draw()` to delegate:
  ```python
  def draw(self, surface):
      self.renderer.draw(surface, self.viewmodel, self.controller)
  ```
- [ ] Run tests: `pytest tests/unit/test_lab/ -v`

**Notes:**

---

### Task 5.3: Extract TestLabInputHandler [Complex]
**File:** `game/ui/screens/test_lab/screen.py` (read)
**New File:** `game/ui/screens/test_lab/screen_input_handler.py`
**Tests:** `pytest tests/unit/test_lab/`

- [ ] Identify all input handling methods (~12 methods, ~280 lines):
  - [ ] `_handle_click()` — main click dispatcher
  - [ ] `_check_category_clicks()` — category sidebar clicks
  - [ ] `_check_tag_filter_clicks()` — tag filter clicks
  - [ ] `_check_test_item_click()` — test list item clicks
  - [ ] `_check_action_button_clicks()` — action button clicks
  - [ ] `_check_seed_mode_clicks()` — seed control clicks
  - [ ] `_handle_scroll_and_mouse()` — scroll + mouse events
  - [ ] `_update_hover_state()` — hover tracking
  - [ ] `_handle_dialog_events()` — dialog event routing
  - [ ] `_handle_panel_events()` — panel event routing
- [ ] Create `game/ui/screens/test_lab/screen_input_handler.py`:
  - [ ] `TestLabInputHandler` class
  - [ ] Constructor takes viewmodel, controller, renderer (for layout rects)
  - [ ] Methods: `handle_event(event)`, `handle_click(pos)`, `handle_scroll(delta)`, `update_hover(pos)`
  - [ ] Input handler calls ViewModel methods to mutate state (not screen methods)
  - [ ] Input handler does NOT import screen.py (one-way dependency)
- [ ] Update screen.py `handle_input()` to delegate:
  ```python
  def handle_input(self, events):
      for event in events:
          self.ui_manager.process_events(event)
          self.input_handler.handle_event(event)
  ```
- [ ] Run tests: `pytest tests/unit/test_lab/ -v`

**Notes:**

---

### Task 5.4: Refactor TestLabScreen to coordinator [Complex]
**File:** `game/ui/screens/test_lab/screen.py`
**Tests:** `pytest tests/unit/test_lab/`

- [ ] Refactor screen to use ViewModel + Renderer + InputHandler:
  - [ ] In `__init__`: create EventBus, ViewModel, Renderer, InputHandler
  - [ ] Subscribe to ViewModel events for UI refresh
  - [ ] Remove all `_draw_*` methods (now in Renderer)
  - [ ] Remove all click/hover/scroll handlers (now in InputHandler)
  - [ ] Remove scroll state (now in ViewModel)
  - [ ] Remove dialog state (now in ViewModel)
  - [ ] Keep: lifecycle (`update`, `handle_resize`), UI manager, scene callbacks
  - [ ] Keep: delegation to existing services (executor, data_extractor, etc.)
- [ ] Screen methods should be thin:
  - [ ] `draw()` — delegates to renderer
  - [ ] `handle_input()` — delegates to input handler
  - [ ] `update()` — delegates to ViewModel/executor
- [ ] Verify screen public API unchanged (IScene protocol: draw, update, handle_input, handle_resize)
- [ ] Run all test lab tests: `pytest tests/unit/test_lab/ -v`
- [ ] Fix any test failures from moved methods
- [ ] Verify: TestLabScreen < 500 lines

**Notes:**

---

### Task 5.5: Phase 5 verification [Simple]
**Tests:** `pytest tests/ -n 12`

- [ ] Run full test suite: `pytest tests/ -n 12`
- [ ] Verify: 12,023+ tests pass, 0 failures
- [ ] Verify line counts:
  - [ ] `test_lab/screen.py` < 500 lines
  - [ ] `test_lab/viewmodel.py` exists, no Pygame imports
  - [ ] `test_lab/renderer.py` exists
  - [ ] `test_lab/screen_input_handler.py` exists
- [ ] Verify: ViewModel independently testable
- [ ] Verify: Renderer does NOT mutate ViewModel state
- [ ] Verify: InputHandler does NOT import screen.py

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to "Project Complete"
