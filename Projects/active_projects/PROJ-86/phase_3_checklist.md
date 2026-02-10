# Phase 3: TestLabScreen Panel Manager [Simple]

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-86 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Extract panel/widget creation methods from TestLabScreen into a new `panel_manager.py` module. This removes ~209 lines of widget factory logic.

**File:** `game/ui/screens/test_lab/screen.py`
**New File:** `game/ui/screens/test_lab/panel_manager.py`
**Tests:** `pytest tests/unit/ui/test_lab_scene/ tests/unit/test_lab/ -x`

---

## Tasks

### Task 3.1: Create panel_manager.py [Simple]
**File:** `game/ui/screens/test_lab/panel_manager.py` (new)

- [ ] Create new file `game/ui/screens/test_lab/panel_manager.py`
- [ ] Create `class TestLabPanelManager` with constructor accepting:
  - `data_extractor` - TestLabDataExtractor instance (for `_load_component_data` callback in ComponentPanel)
  - `test_history` - TestHistory instance (for ResultsPanel)
  - `layout` - dict or object with layout constants (header_height, category_width, test_list_width, metadata_width)
- [ ] Move `_create_ship_panels` logic (lines 615-704) into `PanelManager.create_ship_panels(self, test_id, screen)` method
  - Returns tuple: `(ship_panels, component_panels, tabbed_ship_panel)`
- [ ] Move `_create_results_panel` logic (lines 706-759) into `PanelManager.create_results_panel(self, test_id, ship_panels, tabbed_ship_panel, callbacks)` method
  - `callbacks` dict with keys: `on_view_battle_states`, `on_use_seed`, `on_copy_results`
  - Returns tuple: `(results_panel, test_details_panel)`
- [ ] Move `_create_ui` logic (lines 761-784) into `PanelManager.create_ui_buttons(self, ui_manager, on_back_callback)` method
  - Returns tuple: `(btn_back, button_callbacks_dict)`
- [ ] Ensure imports: `pygame`, `pygame_gui`, `.ship_panels`, `.results_panel`, `.test_run_details`
- [ ] Add docstrings to module and class

**Notes:** These methods reference layout constants like `self.header_height`, `self.category_width`, `self.test_list_width`, `self.metadata_width`, and the module-level `HEIGHT`. Pass layout as a dict or use the existing `DisplayConfig`.

---

### Task 3.2: Update screen.py to delegate to panel_manager [Simple]
**File:** `game/ui/screens/test_lab/screen.py`

- [ ] Add import: `from .panel_manager import TestLabPanelManager`
- [ ] In `TestLabScreen.__init__`, create layout dict and `self._panel_manager = TestLabPanelManager(self._data_extractor, self.test_history, layout)`
- [ ] Replace `_create_ship_panels` method body with delegation:
  ```python
  panels = self._panel_manager.create_ship_panels(test_id, self)
  self.ship_panels, self.component_panels, self.tabbed_ship_panel = panels
  ```
- [ ] Replace `_create_results_panel` method body with delegation:
  ```python
  callbacks = {
      'on_view_battle_states': self._on_view_battle_states,
      'on_use_seed': self._on_use_seed_from_run,
      'on_copy_results': self._on_copy_results,
  }
  panels = self._panel_manager.create_results_panel(
      test_id, self.ship_panels, self.tabbed_ship_panel, callbacks
  )
  self.results_panel, self.test_details_panel = panels
  ```
- [ ] Replace `_create_ui` method body with delegation:
  ```python
  self.btn_back, self._button_callbacks = self._panel_manager.create_ui_buttons(
      self.ui_manager, self._on_back
  )
  # Keep additional rect init that was after the buttons
  self.run_test_btn_rect = None
  self.run_headless_btn_rect = None
  self.tag_filter_rects = {}
  self.tag_exclude_rects = {}
  self.seed_mode_rects = {}
  self.seed_input_rect = None
  self.copy_seed_rect = None
  ```
- [ ] Remove now-unused imports from screen.py

**Notes:** The rect initializations (`run_test_btn_rect`, `tag_filter_rects`, etc.) in `_create_ui` are populated later during drawing. They should stay in screen.py as they are rendering state.

---

### Task 3.3: Run tests and verify [Simple]
**Tests:** `pytest tests/unit/ui/test_lab_scene/ tests/unit/test_lab/ -x`

- [ ] Run targeted tests for TestLabScreen
- [ ] Run full test suite: `pytest tests/ -n 12`
- [ ] Verify no import errors
- [ ] Verify line count of `screen.py` decreased by ~150+ lines
- [ ] Fix any failures discovered

**Notes:**

---

## Phase Completion Checklist
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to Complete
- [ ] Update plan.md phase table row to Complete
- [ ] Update plan.md Current State to point to next phase
