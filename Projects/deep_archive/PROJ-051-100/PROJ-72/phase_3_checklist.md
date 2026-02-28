# Phase 3: Route Menu Actions

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-72 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Handle menu option dispatch in StrategyScreen and scene callbacks in App.py

---

## Tasks

### Task 3.1: Add menu option handler to StrategyScreen [Medium]
**File:** `game/ui/screens/strategy_screen.py` (after `on_save_game_click()`, line ~537)
**Tests:** `pytest tests/ --testmon`

- [x] Add `on_menu_option(self, option)` method that dispatches based on option string:
  - `"save_game"` → calls `self.on_save_game_click()` (existing method)
  - `"load_game"` → calls `self._show_load_game_dialog()`
  - `"settings"` → calls `self._show_coming_soon("Settings")`
  - `"controls"` → calls `self._show_coming_soon("Controls")`
  - `"quit_to_menu"` → calls `self._confirm_quit_to_menu()`
  - `"quit_game"` → calls `self.scene_callback("quit_game")` if callback exists

- [x] Add `_show_load_game_dialog(self)` method:
  - Creates SaveSelectionWindow with strategy UI manager
  - Uses create_centered_rect(600, 500) for positioning

- [x] Add `_on_load_selected(self, save_path, turn_number=None)` method:
  - Calls `self.scene_callback("load_game", save_path=save_path, turn_number=turn_number)`

- [x] Add `_confirm_quit_to_menu(self)` method:
  - Creates UIConfirmationDialog with "Quit to Menu" title
  - Stores reference in `self._quit_confirm_dialog`

- [x] Add UIConfirmationDialog event handling:
  - Handled in `strategy_ui.py` handle_event() via UI_CONFIRMATION_DIALOG_CONFIRMED
  - When `_quit_confirm_dialog` confirmed → calls `scene._handle_quit_confirmed()`
  - `_handle_quit_confirmed()` clears dialog ref and calls scene_callback("quit_to_menu")
  - `_quit_confirm_dialog = None` initialized in `__init__`

- [x] Add `_show_coming_soon(self, feature_name)` method:
  - Creates UIMessageWindow with "Coming Soon!" message
  - Uses UIConfig.CONFIRM_DIALOG_WIDTH/HEIGHT for sizing

### Task 3.2: Extend App.py scene handler [Simple]
**File:** `game/app.py` (method `_handle_strategy_action`, line 553)
**Tests:** `pytest tests/ --testmon`

- [x] Add `"load_game"` handler:
  - Extracts save_path and turn_number from kwargs
  - Calls existing `self._on_load_game(save_path, turn_number)` if save_path present

- [x] Add `"quit_to_menu"` handler:
  - Logs info and calls `self._switch_scene(GameState.MENU, self._menu_scene)`

- [x] Add `"quit_game"` handler:
  - Logs info and sets `self.running = False`

**Notes:** All 22 new tests pass. 6652 total tests pass (1 pre-existing failure in test_protocols.py).

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
