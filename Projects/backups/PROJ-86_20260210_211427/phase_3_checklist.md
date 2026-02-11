# Phase 3: TestLabScreen Panel Manager [Simple]

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-86 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Extract panel/widget creation methods from TestLabScreen into a new `panel_manager.py` module. This removes ~209 lines of widget factory logic.

**File:** `game/ui/screens/test_lab/screen.py`
**New File:** `game/ui/screens/test_lab/panel_manager.py`
**Tests:** `pytest tests/unit/ui/test_lab_scene/ tests/unit/test_lab/ -x`

---

## Tasks

### Task 3.1: Create panel_manager.py [Simple]
**File:** `game/ui/screens/test_lab/panel_manager.py` (new)

- [x] Create new file `game/ui/screens/test_lab/panel_manager.py`
- [x] Create `class TestLabPanelManager` with constructor accepting:
  - `data_extractor` - TestLabDataExtractor instance (for `_load_component_data` callback in ComponentPanel)
  - `test_history` - TestHistory instance (for ResultsPanel)
  - `layout` - dict or object with layout constants (header_height, category_width, test_list_width, metadata_width)
- [x] Move `_create_ship_panels` logic into `PanelManager.create_ship_panels(self, test_id, screen)` method
  - Returns tuple: `(ship_panels, component_panels, tabbed_ship_panel)`
- [x] Move `_create_results_panel` logic into `PanelManager.create_results_panel(self, test_id, ship_panels, tabbed_ship_panel, callbacks)` method
  - `callbacks` dict with keys: `on_view_battle_states`, `on_use_seed`, `on_copy_results`
  - Returns tuple: `(results_panel, test_details_panel)`
- [x] Move `_create_ui` logic into `PanelManager.create_ui_buttons(self, ui_manager, on_back_callback)` method
  - Returns tuple: `(btn_back, button_callbacks_dict)`
- [x] Ensure imports: `pygame`, `pygame_gui`, `.ship_panels`, `.results_panel`, `.test_run_details`
- [x] Add docstrings to module and class

**Notes:** Panel manager created with 233 lines. Uses data_extractor.load_component_data callback directly.

---

### Task 3.2: Update screen.py to delegate to panel_manager [Simple]
**File:** `game/ui/screens/test_lab/screen.py`

- [x] Add import: `from .panel_manager import TestLabPanelManager`
- [x] In `TestLabScreen.__init__`, create layout dict and `self._panel_manager = TestLabPanelManager(self._data_extractor, self.test_history, layout)`
- [x] Replace `_create_ship_panels` method body with delegation
- [x] Replace `_create_results_panel` method body with delegation
- [x] Replace `_create_ui` method body with delegation
- [x] Remove now-unused imports from screen.py (ShipPanel, TabbedShipPanel, ComponentPanel, ResultsPanel, TestRunDetailsPanel, UIButton)

**Notes:** Removed 6 unused imports. Kept rect initializations in screen.py _create_ui.

---

### Task 3.3: Run tests and verify [Simple]
**Tests:** `pytest tests/unit/ui/test_lab_scene/ tests/unit/test_lab/ -x`

- [x] Run targeted tests for TestLabScreen: 114 passed
- [x] Run full test suite: `pytest tests/ -n 12`: 7524 passed
- [x] Verify no import errors
- [x] Verify line count of `screen.py` decreased by ~109 lines (2164→2055)
- [x] Fix any failures discovered: None

**Notes:** Total line reduction: Phase 1 (154) + Phase 2 (218) + Phase 3 (109) = 481 lines saved

---

## Phase Completion Checklist
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to Complete
- [x] Update plan.md phase table row to Complete
- [x] Update plan.md Current State to point to next phase
