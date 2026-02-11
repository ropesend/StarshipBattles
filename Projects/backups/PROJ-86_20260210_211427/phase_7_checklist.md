# Phase 7: StrategyUI Panel & Event Managers [Medium]

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-86 7`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Extract panel layout initialization and event routing from StrategyUI into two new modules: `strategy_panel_manager.py` and `strategy_event_router.py`. Two smaller extractions in one phase.

**File:** `game/ui/screens/strategy_ui.py`
**New Files:** `game/ui/screens/strategy_panel_manager.py`, `game/ui/screens/strategy_event_router.py`
**Tests:** `pytest tests/unit/ui/screens/test_strategy_ui_*.py tests/integration/ui/test_strategy_buttons.py -x`

---

## Tasks

### Task 7.1: Analyze __init__ for extractable panel creation [Simple]
**File:** `game/ui/screens/strategy_ui.py`

- [x] Read `StrategyUI.__init__` (lines 43-366) and identify the panel creation block
- [x] Document which widgets/panels are created and what references are stored on `self`
- [x] Identify the boundary between "configuration/state init" (stays) and "UI widget creation" (extracts)
- [x] Note which widgets are referenced by event handlers and detail formatter

**Notes:** Analyzed __init__ - ~348 lines of panel/widget creation. 40+ widget references stored on self. Event handlers reference btn_*, system_tree, sector_tree, detail_text, current_selection, menu_panel.

---

### Task 7.2: Create strategy_panel_manager.py [Medium]
**File:** `game/ui/screens/strategy_panel_manager.py` (new)

- [x] Create new file `game/ui/screens/strategy_panel_manager.py`
- [x] Create function `create_strategy_panels(manager, width, height, sidebar_width, scene)` that:
  - Creates all three sidebar panels (system, sector, detail)
  - Creates all buttons (btn_planets, btn_design, btn_build_queues, btn_all_queues, btn_menu, btn_events, btn_raw_data, btn_colonize, btn_build_yard, btn_orders, btn_fleet_report, btn_build_fleet)
  - Creates labels (system_header, sector_header, lbl_resources)
  - Creates tree panels (system_tree, sector_tree)
  - Creates graphs (spectrum_graph, atmosphere_graph, graph_rect, graph_image)
  - Creates portrait image (portrait_image, detail_text)
  - Returns a dataclass or dict with all widget references
- [x] Create function `resize_strategy_panels(widgets, manager, width, height, sidebar_width)` that handles resize logic from `handle_resize` (lines 454-509)
- [x] Move `_apply_hotkey_tooltips` logic (lines 367-402) into a standalone function `apply_hotkey_tooltips(buttons, input_mapper)`
- [x] Ensure imports: `pygame`, `pygame_gui`, `UIConfig`, `SystemTreePanel`, `SpectrumGraph`, `AtmosphereGraph`, `StrategyMenuPanel`, `Paths`
- [x] Add docstrings

**Notes:** Created StrategyWidgets dataclass with all 40+ widget references. Factory function returns dataclass instance. 476 lines total.

---

### Task 7.3: Create strategy_event_router.py [Medium]
**File:** `game/ui/screens/strategy_event_router.py` (new)

- [x] Create new file `game/ui/screens/strategy_event_router.py`
- [x] Create `class StrategyEventRouter` with constructor accepting:
  - `ui` - reference to StrategyUI (for accessing widgets, window manager, detail formatter, scene)
- [x] Move `handle_event(self, event)` logic into `StrategyEventRouter.route_event(self, event)`
- [x] Move `process_custom_ui_events(self, event)` logic into `StrategyEventRouter.process_custom_events(self, event)`
- [x] Move `handle_click(self, mx, my, button)` logic into `StrategyEventRouter.handle_click(self, mx, my, button)`
- [x] Move `on_ui_selection(self, obj)` logic into `StrategyEventRouter.on_ui_selection(self, obj)`
- [x] Move `_has_modal_open(self)` logic into `StrategyEventRouter.has_modal_open(self)`
- [x] Ensure imports: `pygame`, `pygame_gui`, `game.core.protocols.is_fleet`, `game.core.logger.log_debug`
- [x] Add docstrings

**Notes:** Created StrategyEventRouter class (271 lines) with all event handling methods. Extracted colonize button logic into `_handle_colonize_button()`.

---

### Task 7.4: Update strategy_ui.py to delegate to panel manager and event router [Medium]
**File:** `game/ui/screens/strategy_ui.py`

- [x] Add imports: `from game.ui.screens.strategy_panel_manager import create_strategy_panels, resize_strategy_panels, apply_hotkey_tooltips` and `from game.ui.screens.strategy_event_router import StrategyEventRouter`
- [x] In `__init__`, replace panel creation block with factory call and widget unpacking
- [x] Create event router: `self._event_router = StrategyEventRouter(self)`
- [x] Replace `handle_event` body with: `self._event_router.route_event(event)`
- [x] Replace `handle_click` body with: `return self._event_router.handle_click(mx, my, button)`
- [x] Replace `on_ui_selection` body with: `self._event_router.on_ui_selection(obj)`
- [x] Replace `_has_modal_open` body with: `return self._event_router.has_modal_open()`
- [x] Replace `handle_resize` body with delegation
- [x] Replace `_apply_hotkey_tooltips` body with delegation
- [x] Remove now-unused imports (InputAction, is_fleet, log_debug, SpectrumGraph, AtmosphereGraph, SystemTreePanel)

**Notes:** strategy_ui.py reduced from 841 to 381 lines (-460 lines, 55% reduction!). Far exceeded the ~600 line target.

---

### Task 7.5: Run tests and verify [Simple]
**Tests:** `pytest tests/unit/ui/screens/test_strategy_ui_*.py tests/integration/ui/test_strategy_buttons.py -x`

- [x] Run targeted tests for StrategyUI
- [x] Run full test suite: `pytest tests/ -n 12`
- [x] Verify no import errors or circular imports between the new modules
- [x] Verify line count of `strategy_ui.py` is ~600 lines or less
- [x] Fix any failures discovered

**Notes:** Updated 3 test files with event_router fixture (test_strategy_ui_menu.py, test_event_log_window.py, test_bug_16_raw_data_button.py). 7524 tests passing.

---

## Phase Completion Checklist
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to Complete
- [x] Update plan.md phase table row to Complete
- [x] Update plan.md Current State to point to next phase
