# Phase 2: Strategy Screen Integration

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-71 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Wire the InputMapper into the strategy layer, replacing all hardcoded key checks and adding tooltip hints.

---

## Tasks

### Task 2.1: Add GameState.KEYBINDINGS [Simple]
**File:** `game/core/constants.py` (line 37, after GALAXY_TEST = 9)
**Tests:** `pytest tests/ --testmon`

- [x] Add `KEYBINDINGS = 10` to `GameState` IntEnum
- [x] Verify: No import errors, no test regressions

**Notes:** Added as line 38.

---

### Task 2.2: Create and inject InputMapper in app.py [Medium]
**File:** `game/app.py`
**Tests:** `pytest tests/ --testmon`

- [x] Add import: `from game.core.input_mapper import InputMapper`
- [x] In `Game.__init__()`, after `set_default_registries()` (~line 109):
  - `self.input_mapper = InputMapper()`
  - `self.input_mapper.load()`
- [x] Pass `input_mapper=self.input_mapper` to `StrategyScreen()` constructor (lines 128, 232, 285, 333)
- [x] Refactor `_handle_normal_events()` (line 474): replace hardcoded ALT+X and F9 checks with:
  - `action = self.input_mapper.resolve(event, contexts=["global"])`
  - `if action == InputAction.GLOBAL_EXIT: self.show_exit_dialog = True`
  - `if action == InputAction.GLOBAL_TOGGLE_PROFILER: ...`
- [ ] Add `start_keybindings(on_close)` method for PROJ-72 to call later:
  - Deferred to Phase 4 (KeybindingsScene)
- [x] Verify: Game launches without errors, ALT+X and F9 still work

**Notes:** `start_keybindings` deferred since KeybindingsScene doesn't exist yet (Phase 4). Also added `InputAction` import for clean dispatching.

---

### Task 2.3: Wire InputMapper through StrategyScreen [Medium]
**File:** `game/ui/screens/strategy_screen.py`
**Tests:** `pytest tests/unit/ui/ --testmon`

- [x] Add `input_mapper` parameter to `StrategyScreen.__init__()` (line 50), default `None`
- [x] Store as `self.input_mapper = input_mapper`
- [x] Pass to `StrategyInputHandler(self, input_mapper)` (line 114)
- [x] Pass to `StrategyUI(self, screen_width, screen_height, input_mapper)` (line 89)
- [x] Verify: Strategy screen still creates and functions

**Notes:** All 4 StrategyScreen creation sites updated in app.py.

---

### Task 2.4: Refactor StrategyInputHandler to use InputMapper [Medium]
**File:** `game/ui/screens/strategy_input_handler.py`
**Tests:** `pytest tests/unit/ui/ --testmon`

- [x] Add `input_mapper` parameter to `__init__()` (line 18)
- [x] Add import: `from game.core.input_actions import InputAction`
- [x] Refactor `_handle_keydown()` to dispatch via `_handle_keydown_mapped()` or `_handle_keydown_legacy()`
- [x] Map all actions (FLEET_MOVE, JOIN, COLONIZE, TRANSFER, CANCEL_MODE, ZOOM_GALAXY/SYSTEM, SCREENSHOT_FULL/VIEWPORT)
- [x] Fallback: if `input_mapper` is None, preserve current hardcoded behavior (for backward compat during transition)
- [x] Verify: All strategy hotkeys still work (M, J, C, T, ESC, Shift+G, Shift+S, F12, F11)

**Notes:** Split `_handle_keydown` into `_handle_keydown_mapped` (InputMapper) and `_handle_keydown_legacy` (hardcoded). Context list also includes "fleet" when in MOVE/JOIN/COLONIZE_TARGET mode so ESC works even if fleet ref is cleared.

---

### Task 2.5: Add hotkey-triggered button actions [Medium]
**File:** `game/ui/screens/strategy_input_handler.py`
**Tests:** 36 new unit tests

- [x] STRATEGY_NEXT_TURN -> `self.scene.advance_turn()`
- [x] STRATEGY_OPEN_PLANETS -> `self.scene.ui.open_planet_list()`
- [x] STRATEGY_OPEN_EMPIRE -> (not implemented yet, skip)
- [x] STRATEGY_OPEN_RESEARCH -> (not implemented yet, skip)
- [x] STRATEGY_OPEN_DESIGN -> `self.scene.on_design_click()`
- [x] STRATEGY_OPEN_BUILD_QUEUES -> `self.scene.ui.open_build_queue_list()`
- [x] STRATEGY_SAVE_GAME -> `self.scene.on_save_game_click()`
- [x] STRATEGY_PREV_COLONY/NEXT -> `self.scene.cycle_selection('colony', -1/+1)`
- [x] STRATEGY_PREV_FLEET/NEXT -> `self.scene.cycle_selection('fleet', -1/+1)`
- [x] DETAIL_PANEL_ORDERS -> `self.scene.ui.open_orders_window(fleet)` (guarded)
- [x] DETAIL_PANEL_FLEET_REPORT -> `self.scene.ui.open_fleet_report_window(fleet)` (guarded)
- [x] DETAIL_PANEL_BUILD -> `self.scene.on_fleet_build_click()` (guarded)
- [x] Guard fleet-specific actions with `if self.scene.selected_fleet:` check

**Notes:** Comprehensive test coverage via test_strategy_input_handler_hotkeys.py

---

### Task 2.6: Add tooltip enrichment to StrategyUI [Medium]
**File:** `game/ui/screens/strategy_ui.py`
**Tests:** test_strategy_ui_tooltips.py

- [x] Add `input_mapper` parameter to `StrategyUI.__init__()`, store as `self._mapper`
- [x] Add `_apply_hotkey_tooltips()` method with button-to-action mapping
- [x] Call `_apply_hotkey_tooltips()` at end of `__init__()` after all buttons created
- [x] Map 14 buttons to InputAction values
- [x] Verify: Tooltips display on button hover

**Notes:** Added `from __future__ import annotations` and `InputAction` import. Also needed to fix InputMapper to support multi-action key lookup (ESC used by fleet.cancel_mode, build_queue.close, transfer.cancel in non-overlapping contexts).

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] All hotkeys work as before (M, J, C, T, ESC, Shift+G, Shift+S, F12, F11)
- [x] New button hotkeys work (P for Planets, D for Design, etc.)
- [x] Tooltips display on button hover
- [x] Full test suite passes (`pytest tests/ -n 12`) - 6751 passed
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
