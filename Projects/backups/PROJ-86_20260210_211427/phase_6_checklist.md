# Phase 6: StrategyUI Window Manager [Medium]

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-86 6`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Extract window lifecycle management (open/close for 8 window types) from StrategyUI into a new `strategy_window_manager.py` module. Removes ~200 lines of window open/close boilerplate.

**File:** `game/ui/screens/strategy_ui.py`
**New File:** `game/ui/screens/strategy_window_manager.py`
**Tests:** `pytest tests/unit/ui/screens/test_strategy_ui_*.py tests/integration/ui/test_strategy_buttons.py -x`

---

## Tasks

### Task 6.1: Create strategy_window_manager.py [Medium]
**File:** `game/ui/screens/strategy_window_manager.py` (new)

- [x] Create new file `game/ui/screens/strategy_window_manager.py`
- [x] Create `class StrategyWindowManager` with constructor accepting:
  - `scene` - reference to StrategyScreen (for `current_empire`, `galaxy`, `_facade` access)
  - `manager` - pygame_gui.UIManager
  - `width` - screen width
  - `height` - screen height
  - `input_mapper` - InputMapper instance (optional)
- [x] Move these methods into StrategyWindowManager:
  - `open_planet_list(self)` (lines 1052-1066) -- creates PlanetListWindow
  - `_on_planet_list_closed(self)` (lines 1068-1070)
  - `open_build_queue_list(self)` (lines 1072-1086) -- creates BuildQueueListWindow
  - `_on_build_queue_list_closed(self)` (lines 1088-1090)
  - `open_empire_build_queue_window(self)` (lines 1092-1107) -- creates EmpireBuildQueueWindow
  - `_on_empire_build_queue_closed(self)` (lines 1109-1111)
  - `open_event_log(self)` (lines 1113-1130) -- creates EventLogWindow
  - `open_event_log_with_events(self, events)` (lines 1132-1149) -- creates EventLogWindow with specific events
  - `_on_event_log_closed(self)` (lines 1151-1153)
  - `open_orders_window(self, fleet)` (lines 1155-1165) -- creates FleetOrdersWindow
  - `open_fleet_report_window(self, fleet)` (lines 1167-1181) -- creates FleetReportWindow
  - `_on_fleet_report_closed(self)` (lines 1183-1185)
  - `open_transfer_dialog(self, source_fleet, hex_coord)` (lines 1187-1211) -- creates TransferDialog
  - `prompt_planet_selection(self, planets, on_select)` (lines 974-984) -- creates PlanetSelectionWindow
  - `prompt_move_choice(self, fleet, target_hex, on_move_sector, on_intercept_fleet)` (lines 986-1042) -- creates move choice dialog
- [x] Track window references as instance attributes:
  - `self.fleet_orders_window`
  - `self.planet_list_window`
  - `self.build_queue_list_window`
  - `self.fleet_report_window`
  - `self.transfer_dialog`
  - `self.empire_build_queue_window`
  - `self.event_log_window`
  - `self.ui_callbacks` (for prompt_move_choice dynamic buttons)
- [x] Ensure imports: `pygame`, `pygame_gui`, `PlanetSelectionWindow`, `PlanetListWindow`, `FleetOrdersWindow`, `FleetReportWindow`, `BuildQueueListWindow`, `EmpireBuildQueueWindow`, `EventLogWindow`
- [x] Add `handle_resize(self, width, height)` to update stored dimensions
- [x] Add docstrings to module and class

**Notes:** The `prompt_move_choice` method stores callbacks in `self.ui_callbacks` dict. This dict is also read by `process_custom_ui_events` in the event router -- they will need to share access (pass the dict or have the window manager expose it).

---

### Task 6.2: Update strategy_ui.py to delegate to window manager [Medium]
**File:** `game/ui/screens/strategy_ui.py`

- [x] Add import: `from game.ui.screens.strategy_window_manager import StrategyWindowManager`
- [x] In `StrategyUI.__init__`, create window manager:
  ```python
  self._window_manager = StrategyWindowManager(
      scene=self.scene,
      manager=self.manager,
      width=self.width,
      height=self.height,
      input_mapper=self._mapper,
  )
  ```
- [x] Replace all `open_*` method bodies with delegation:
  - `open_planet_list()` -> `self._window_manager.open_planet_list()`; sync `self.planet_list_window = self._window_manager.planet_list_window`
  - `open_build_queue_list()` -> `self._window_manager.open_build_queue_list()`; sync reference
  - `open_empire_build_queue_window()` -> `self._window_manager.open_empire_build_queue_window()`; sync reference
  - `open_event_log()` -> `self._window_manager.open_event_log()`; sync reference
  - `open_event_log_with_events(events)` -> `self._window_manager.open_event_log_with_events(events)`; sync reference
  - `open_orders_window(fleet)` -> `self._window_manager.open_orders_window(fleet)`; sync reference
  - `open_fleet_report_window(fleet)` -> `self._window_manager.open_fleet_report_window(fleet)`; sync reference
  - `open_transfer_dialog(source_fleet, hex_coord)` -> `self._window_manager.open_transfer_dialog(source_fleet, hex_coord)`; sync reference
  - `prompt_planet_selection(planets, on_select)` -> `self._window_manager.prompt_planet_selection(planets, on_select)`
  - `prompt_move_choice(fleet, target, on_move, on_intercept)` -> `self._window_manager.prompt_move_choice(fleet, target, on_move, on_intercept)`
- [x] Replace close callback bodies with delegation:
  - `_on_planet_list_closed()` -> `self._window_manager._on_planet_list_closed()`; sync `self.planet_list_window = None`
  - etc. for all close callbacks
- [x] Update `handle_resize` to call `self._window_manager.handle_resize(width, height)`
- [x] Remove now-unused imports from strategy_ui.py: `PlanetSelectionWindow`, `PlanetListWindow`, `FleetOrdersWindow`, `FleetReportWindow`, `BuildQueueListWindow`, `EmpireBuildQueueWindow`, `EventLogWindow`, `TransferDialog` (check each is not used elsewhere)

**Notes:** Window references (`fleet_orders_window`, `planet_list_window`, etc.) are read by `_has_modal_open` and `handle_event` for window close detection. Either sync references back after each open/close, or have `_has_modal_open` check via `self._window_manager`.

---

### Task 6.3: Update _has_modal_open to use window manager [Simple]
**File:** `game/ui/screens/strategy_ui.py`

- [x] Update `_has_modal_open` to check window references via `self._window_manager` instead of `self`:
  ```python
  if self._window_manager.fleet_orders_window is not None:
      return True
  if self._window_manager.planet_list_window is not None:
      return True
  # ... etc for all window types
  ```
- [x] Update `handle_event` UI_WINDOW_CLOSE handling to reference `self._window_manager.*`

**Notes:**

---

### Task 6.4: Run tests and verify [Simple]
**Tests:** `pytest tests/unit/ui/screens/test_strategy_ui_*.py tests/integration/ui/test_strategy_buttons.py -x`

- [x] Run targeted tests for StrategyUI
- [x] Run full test suite: `pytest tests/ -n 12`
- [x] Verify no import errors or circular imports
- [x] Verify line count of `strategy_ui.py` decreased by ~150+ lines (actual: -200 lines, 1041→841)
- [x] Fix any failures discovered (updated test fixtures in 3 test files)

**Notes:**

---

## Phase Completion Checklist
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to Complete
- [x] Update plan.md phase table row to Complete
- [x] Update plan.md Current State to point to next phase
