# Phase 7: StrategyUI Panel & Event Managers [Medium]

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-86 7`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Extract panel layout initialization and event routing from StrategyUI into two new modules: `strategy_panel_manager.py` and `strategy_event_router.py`. Two smaller extractions in one phase.

**File:** `game/ui/screens/strategy_ui.py`
**New Files:** `game/ui/screens/strategy_panel_manager.py`, `game/ui/screens/strategy_event_router.py`
**Tests:** `pytest tests/unit/ui/screens/test_strategy_ui_*.py tests/integration/ui/test_strategy_buttons.py -x`

---

## Tasks

### Task 7.1: Analyze __init__ for extractable panel creation [Simple]
**File:** `game/ui/screens/strategy_ui.py`

- [ ] Read `StrategyUI.__init__` (lines 43-366) and identify the panel creation block
- [ ] Document which widgets/panels are created and what references are stored on `self`
- [ ] Identify the boundary between "configuration/state init" (stays) and "UI widget creation" (extracts)
- [ ] Note which widgets are referenced by event handlers and detail formatter

**Notes:** The `__init__` creates panels (system_panel, sector_panel, detail_panel), buttons (btn_planets, btn_design, etc.), labels (lbl_resources), tree panels, graphs, and portrait image. All are stored as `self.*` attributes. The factory function must return all these references.

---

### Task 7.2: Create strategy_panel_manager.py [Medium]
**File:** `game/ui/screens/strategy_panel_manager.py` (new)

- [ ] Create new file `game/ui/screens/strategy_panel_manager.py`
- [ ] Create function `create_strategy_panels(manager, width, height, sidebar_width, scene)` that:
  - Creates all three sidebar panels (system, sector, detail)
  - Creates all buttons (btn_planets, btn_design, btn_build_queues, btn_all_queues, btn_menu, btn_events, btn_raw_data, btn_colonize, btn_build_yard, btn_orders, btn_fleet_report, btn_build_fleet)
  - Creates labels (system_header, sector_header, lbl_resources)
  - Creates tree panels (system_tree, sector_tree)
  - Creates graphs (spectrum_graph, atmosphere_graph, graph_rect, graph_image)
  - Creates portrait image (portrait_image, detail_text)
  - Returns a dataclass or dict with all widget references
- [ ] Create function `resize_strategy_panels(widgets, manager, width, height, sidebar_width)` that handles resize logic from `handle_resize` (lines 454-509)
- [ ] Move `_apply_hotkey_tooltips` logic (lines 367-402) into a standalone function `apply_hotkey_tooltips(buttons, input_mapper)`
- [ ] Ensure imports: `pygame`, `pygame_gui`, `UIConfig`, `SystemTreePanel`, `SpectrumGraph`, `AtmosphereGraph`, `StrategyMenuPanel`, `Paths`
- [ ] Add docstrings

**Notes:** Using module-level factory functions (not a class) since the panel manager has no persistent state beyond what it creates. The created widgets are stored on the StrategyUI instance.

---

### Task 7.3: Create strategy_event_router.py [Medium]
**File:** `game/ui/screens/strategy_event_router.py` (new)

- [ ] Create new file `game/ui/screens/strategy_event_router.py`
- [ ] Create `class StrategyEventRouter` with constructor accepting:
  - `ui` - reference to StrategyUI (for accessing widgets, window manager, detail formatter, scene)
- [ ] Move `handle_event(self, event)` logic (lines 841-957) into `StrategyEventRouter.route_event(self, event)`
  - References to `self.manager` become `self.ui.manager`
  - References to `self.btn_*` become `self.ui.btn_*`
  - References to `self.fleet_orders_window` etc. become `self.ui._window_manager.*`
  - References to `self.open_*` become `self.ui.open_*` or `self.ui._window_manager.open_*`
  - Colonize button logic (lines 884-925) stays as-is but routes through `self.ui`
- [ ] Move `process_custom_ui_events(self, event)` logic (lines 1044-1049) into `StrategyEventRouter.process_custom_events(self, event)`
  - Accesses `self.ui._window_manager.ui_callbacks`
- [ ] Move `handle_click(self, mx, my, button)` logic (lines 959-970) into `StrategyEventRouter.handle_click(self, mx, my, button)`
- [ ] Move `on_ui_selection(self, obj)` logic (lines 836-839) into `StrategyEventRouter.on_ui_selection(self, obj)`
- [ ] Move `_has_modal_open(self)` logic (lines 792-834) into `StrategyEventRouter.has_modal_open(self)`
  - Checks `self.ui._window_manager.*` and `self.ui.menu_panel`
- [ ] Ensure imports: `pygame`, `pygame_gui`, `game.core.protocols.is_fleet`, `game.core.logger.log_debug`
- [ ] Add docstrings

**Notes:** The event router has the most complex dependencies -- it touches buttons, windows, scene, and calls open methods. Keep it as a thin routing layer that delegates to the window manager and detail formatter.

---

### Task 7.4: Update strategy_ui.py to delegate to panel manager and event router [Medium]
**File:** `game/ui/screens/strategy_ui.py`

- [ ] Add imports: `from game.ui.screens.strategy_panel_manager import create_strategy_panels, resize_strategy_panels, apply_hotkey_tooltips` and `from game.ui.screens.strategy_event_router import StrategyEventRouter`
- [ ] In `__init__`, replace panel creation block with:
  ```python
  widgets = create_strategy_panels(self.manager, self.width, self.height, self.sidebar_width, self.scene)
  # Unpack all widget references onto self
  self.system_panel = widgets['system_panel']
  self.sector_panel = widgets['sector_panel']
  self.detail_panel = widgets['detail_panel']
  # ... etc for all widgets
  ```
- [ ] Create event router: `self._event_router = StrategyEventRouter(self)`
- [ ] Replace `handle_event` body with: `self._event_router.route_event(event)`
- [ ] Replace `process_custom_ui_events` body with: `self._event_router.process_custom_events(event)`
- [ ] Replace `handle_click` body with: `return self._event_router.handle_click(mx, my, button)`
- [ ] Replace `on_ui_selection` body with: `self._event_router.on_ui_selection(obj)`
- [ ] Replace `_has_modal_open` body with: `return self._event_router.has_modal_open()`
- [ ] Replace `handle_resize` body with: `resize_strategy_panels(self, self.manager, width, height, self.sidebar_width)` plus update stored width/height and manager resolution
- [ ] Replace `_apply_hotkey_tooltips` body with delegation to `apply_hotkey_tooltips`
- [ ] Remove now-unused imports

**Notes:** After Phase 7, StrategyUI.__init__ should be significantly shorter -- just creating the sub-managers and unpacking widget references. The remaining code is `show_system_info`, `show_sector_info`, `_update_resource_display`, `update`, `draw`, `toggle/open/close_menu_panel`, `hide_ui`, `show_ui`, and `_get_object_asset`.

---

### Task 7.5: Run tests and verify [Simple]
**Tests:** `pytest tests/unit/ui/screens/test_strategy_ui_*.py tests/integration/ui/test_strategy_buttons.py -x`

- [ ] Run targeted tests for StrategyUI
- [ ] Run full test suite: `pytest tests/ -n 12`
- [ ] Verify no import errors or circular imports between the new modules
- [ ] Verify line count of `strategy_ui.py` is ~600 lines or less
- [ ] Fix any failures discovered

**Notes:**

---

## Phase Completion Checklist
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to Complete
- [ ] Update plan.md phase table row to Complete
- [ ] Update plan.md Current State to point to next phase
