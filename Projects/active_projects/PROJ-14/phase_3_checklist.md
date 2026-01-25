# Phase 3: Migrate Main Menu Buttons

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-14 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Replace legacy Button with pygame_gui UIButton in main menu

**CRITICAL:** This is the highest-risk phase. The main menu is the first thing users see. Test thoroughly!

---

## Tasks

### Task 3.1: Add UIManager to Game class [Simple]
**File:** `game/app.py`
**Tests:** `pytest tests/unit/test_app_integration.py -v`

- [ ] Add import at top of file (around line 10):
  ```python
  import pygame_gui
  ```
- [ ] In `__init__()` method, after `pygame.display.set_mode()`, add:
  ```python
  self.menu_ui_manager = pygame_gui.UIManager((WIDTH, HEIGHT))
  self._menu_button_callbacks = {}  # Maps UIButton -> callback function
  ```
- [ ] Verify: App still initializes without errors

**Notes:** [Filled during implementation]

---

### Task 3.2: Migrate update_menu_buttons() [Medium]
**File:** `game/app.py` (lines 125-137)
**Tests:** Manual - launch game and verify menu displays

- [ ] Change import from `from ui import Button` to:
  ```python
  from pygame_gui.elements import UIButton
  ```
- [ ] Rewrite `update_menu_buttons()` method:
  ```python
  def update_menu_buttons(self):
      # Clear old buttons if they exist
      for btn in getattr(self, 'menu_buttons', []):
          btn.kill()
      self._menu_button_callbacks.clear()

      self.menu_buttons = []
      button_data = [
          ("Quickstart 1P", self.start_quickstart_1p),
          ("Quickstart 2P", self.start_quickstart_2p),
          ("New Game", self.start_strategy_layer),
          ("Load Game", self.show_load_menu),
          ("Race Setup", self.start_race_setup),
          ("Design Workshop", self.start_builder),
          ("Battle Setup", self.start_battle_setup),
          ("Formation Editor", self.start_formation_editor),
          ("Combat Lab", self.start_test_lab),
          ("Research Tree", self.start_research_tree),
      ]

      for i, (text, callback) in enumerate(button_data):
          btn = UIButton(
              relative_rect=pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 - 320 + i * 70, 200, 50),
              text=text,
              manager=self.menu_ui_manager
          )
          self.menu_buttons.append(btn)
          self._menu_button_callbacks[btn] = callback
  ```
- [ ] Verify: No syntax errors

**Notes:** [Filled during implementation]

---

### Task 3.3: Update Event Handling [Medium]
**File:** `game/app.py`
**Tests:** Manual - click each menu button

- [ ] Find `_forward_event_to_scene()` method
- [ ] In the `if self.state == MENU:` block, replace legacy button handling with:
  ```python
  if self.state == MENU:
      self.menu_ui_manager.process_events(event)
      if event.type == pygame_gui.UI_BUTTON_PRESSED:
          callback = self._menu_button_callbacks.get(event.ui_element)
          if callback:
              callback()
              return  # Event consumed
  ```
- [ ] Remove legacy button loop: `for btn in self.menu_buttons: btn.handle_event(event)`
- [ ] Verify: Events are processed correctly

**Notes:** [Filled during implementation]

---

### Task 3.4: Update Rendering [Simple]
**File:** `game/app.py`
**Tests:** Visual - menu buttons render correctly

- [ ] Find `_draw_menu()` method
- [ ] Add UIManager update (needs frame_time parameter):
  ```python
  # In _draw_menu(), add after background drawing:
  self.menu_ui_manager.update(frame_time)  # frame_time in seconds
  self.menu_ui_manager.draw_ui(self.screen)
  ```
- [ ] Remove legacy button draw loop: `for btn in self.menu_buttons: btn.draw(self.screen)`
- [ ] Verify: Buttons render with pygame_gui styling

**Notes:** May need to check where frame_time comes from - typically from `clock.tick() / 1000.0`

---

### Task 3.5: Update Resize Handling [Simple]
**File:** `game/app.py`
**Tests:** Resize window - buttons reposition correctly

- [ ] Find `_handle_resize()` method
- [ ] Add UIManager resize call:
  ```python
  self.menu_ui_manager.set_window_resolution((WIDTH, HEIGHT))
  ```
- [ ] `update_menu_buttons()` is already called - this recreates buttons at new positions
- [ ] Verify: Resize window, buttons reposition correctly

**Notes:** [Filled during implementation]

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Run `pytest tests/ --testmon` - passes
- [ ] **CRITICAL MANUAL TESTS:**
  - [ ] Launch game - menu displays
  - [ ] All 10 buttons visible with pygame_gui styling
  - [ ] Click "Quickstart 1P" - enters strategy mode
  - [ ] Click "Quickstart 2P" - enters strategy mode
  - [ ] Click "New Game" - shows dialog
  - [ ] Click "Load Game" - shows dialog
  - [ ] Click "Race Setup" - shows dialog
  - [ ] Click "Design Workshop" - enters builder
  - [ ] Click "Battle Setup" - enters battle setup
  - [ ] Click "Formation Editor" - enters formation editor
  - [ ] Click "Combat Lab" - enters test lab
  - [ ] Click "Research Tree" - enters research tree
  - [ ] Resize window - buttons reposition
  - [ ] Hover states work (buttons change appearance on hover)
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 4

**ROLLBACK PLAN:** If buttons don't work, `git revert` to restore legacy Button
