# Phase 3: Route Menu Actions

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-72 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Handle menu option dispatch in StrategyScreen and scene callbacks in App.py

---

## Tasks

### Task 3.1: Add menu option handler to StrategyScreen [Medium]
**File:** `game/ui/screens/strategy_screen.py` (after `on_save_game_click()`, line ~537)
**Tests:** `pytest tests/ --testmon`

- [ ] Add `on_menu_option(self, option)` method that dispatches based on option string:
  - `"save_game"` → calls `self.on_save_game_click()` (existing method)
  - `"load_game"` → calls `self._show_load_game_dialog()`
  - `"settings"` → calls `self._show_coming_soon("Settings")`
  - `"controls"` → calls `self._show_coming_soon("Controls")`
  - `"quit_to_menu"` → calls `self._confirm_quit_to_menu()`
  - `"quit_game"` → calls `self.scene_callback("quit_game")` if callback exists

- [ ] Add `_show_load_game_dialog(self)` method:
  ```python
  def _show_load_game_dialog(self):
      from game.ui.screens.save_selection_window import SaveSelectionWindow
      from game.ui.utils import create_centered_rect

      window_rect = create_centered_rect(600, 500, self.screen_width, self.screen_height)
      SaveSelectionWindow(
          window_rect,
          self.ui.manager,
          on_load_callback=self._on_load_selected,
          on_cancel_callback=lambda: None
      )
  ```

- [ ] Add `_on_load_selected(self, save_path, turn_number=None)` method:
  - Calls `self.scene_callback("load_game", save_path=save_path, turn_number=turn_number)`

- [ ] Add `_confirm_quit_to_menu(self)` method:
  ```python
  def _confirm_quit_to_menu(self):
      import pygame_gui.windows
      dialog_rect = pygame.Rect(0, 0, 400, 200)
      dialog_rect.center = (self.screen_width // 2, self.screen_height // 2)
      self._quit_confirm_dialog = pygame_gui.windows.UIConfirmationDialog(
          rect=dialog_rect,
          action_long_desc="Unsaved progress will be lost. Return to main menu?",
          manager=self.ui.manager,
          window_title="Quit to Menu"
      )
  ```

- [ ] Add UIConfirmationDialog event handling in `on_menu_option` or via a new handler:
  - Listen for `pygame_gui.UI_CONFIRMATION_DIALOG_CONFIRMED` event
  - When `self._quit_confirm_dialog` is confirmed, call `self.scene_callback("quit_to_menu")`
  - Track `self._quit_confirm_dialog = None` in `__init__`
  - Handle the confirmation event in the UI's `handle_event()` or in `StrategyInputHandler`

- [ ] Add `_show_coming_soon(self, feature_name)` method:
  ```python
  def _show_coming_soon(self, feature_name):
      import pygame_gui.windows
      from game.core.config import UIConfig
      dialog_rect = pygame.Rect(0, 0, UIConfig.CONFIRM_DIALOG_WIDTH, UIConfig.CONFIRM_DIALOG_HEIGHT)
      dialog_rect.center = (self.screen_width // 2, self.screen_height // 2)
      pygame_gui.windows.UIMessageWindow(
          rect=dialog_rect,
          html_message=f"<b>{feature_name}</b><br><br>Coming Soon!",
          manager=self.ui.manager,
          window_title=feature_name
      )
  ```

### Task 3.2: Extend App.py scene handler [Simple]
**File:** `game/app.py` (method `_handle_strategy_action`, line 553)
**Tests:** `pytest tests/ --testmon`

- [ ] Add `"load_game"` handler:
  ```python
  elif action == "load_game":
      save_path = kwargs.get("save_path")
      turn_number = kwargs.get("turn_number")
      if save_path:
          self._on_load_game(save_path, turn_number)
  ```
  (Reuses existing `_on_load_game` method at line 322)

- [ ] Add `"quit_to_menu"` handler:
  ```python
  elif action == "quit_to_menu":
      log_info("Returning to main menu from strategy")
      self._switch_scene(GameState.MENU, self._menu_scene)
  ```

- [ ] Add `"quit_game"` handler:
  ```python
  elif action == "quit_game":
      log_info("Quitting game from strategy menu")
      self.running = False
  ```

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
