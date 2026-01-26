# Phase 4: Migrate Test Lab Buttons

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-14 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Replace legacy Button in test lab scene dialogs

---

## Tasks

### Task 4.1: Add UIManager to TestLabScene [Simple]
**File:** `ui/test_lab_scene.py`
**Tests:** `pytest tests/unit/ui/test_test_lab_scene.py -v`

- [x] Add import at top of file:
  ```python
  import pygame_gui
  from pygame_gui.elements import UIButton
  ```
- [x] In `TestLabScene.__init__()`, after getting screen dimensions, add:
  ```python
  self.ui_manager = pygame_gui.UIManager((self.screen_width, self.screen_height))
  self._button_callbacks = {}  # Maps UIButton -> callback function
  ```
- [x] Verify: TestLabScene initializes without errors

**Notes:** Added pygame_gui import and UIManager initialization at top of __init__. Also removed legacy Button import from ui.components. TestLabScene imports successfully.

---

### Task 4.2: Migrate JSONPopup Close Button [Simple]
**File:** `ui/test_lab_scene.py` (JSONPopup class, line ~52)
**Tests:** Manual - open JSON popup, click close

- [x] Find `JSONPopup.__init__()` (around line 18)
- [x] Find `self.close_button = Button(...)` line
- [x] Replace with UIButton:
  ```python
  # Calculate button position relative to popup
  self.close_button = UIButton(
      relative_rect=pygame.Rect(self.x + self.width - 110, self.y + 10, 100, 40),
      text="Close",
      manager=scene.ui_manager  # Pass scene reference
  )
  ```
- [x] Update `JSONPopup.handle_event()` to check pygame_gui events:
  ```python
  if event.type == pygame_gui.UI_BUTTON_PRESSED:
      if event.ui_element == self.close_button:
          self.close()
          return True
  ```
- [x] Update `JSONPopup.close()` to kill button:
  ```python
  def close(self):
      self.is_open = False
      if hasattr(self, 'close_button'):
          self.close_button.kill()
  ```
- [x] Remove legacy button draw call from `draw()` method
- [x] Verify: JSON popup close button works

**Notes:** Added ui_manager parameter to JSONPopup.__init__. Updated all 3 creation sites to pass self.ui_manager. Button is now UIButton with kill() on close.

---

### Task 4.3: Migrate ConfirmationDialog Buttons [Simple]
**File:** `ui/test_lab_scene.py` (ConfirmationDialog class, lines ~113-159)
**Tests:** Manual - trigger confirmation dialog, test confirm/cancel

- [x] Find `ConfirmationDialog.__init__()` (around line 113)
- [x] Replace `self.confirm_button = Button(...)` with UIButton
- [x] Replace `self.cancel_button = Button(...)` with UIButton
- [x] Update event handling for pygame_gui events:
  ```python
  if event.type == pygame_gui.UI_BUTTON_PRESSED:
      if event.ui_element == self.confirm_button:
          self._handle_confirm()
          return True
      elif event.ui_element == self.cancel_button:
          self._handle_cancel()
          return True
  ```
- [x] Update close methods to kill buttons
- [x] Remove legacy button draw calls
- [x] Verify: Confirmation dialog buttons work

**Notes:** Added ui_manager parameter to ConfirmationDialog. Updated creation site to pass self.ui_manager. Added _kill_buttons() helper called from _handle_confirm/_handle_cancel.

---

### Task 4.4: Migrate Back Button [Simple]
**File:** `ui/test_lab_scene.py` (line ~2321)
**Tests:** Manual - click Back in test lab

- [x] Find `self.btn_back = Button(...)` (around line 2321)
- [x] Replace with UIButton:
  ```python
  self.btn_back = UIButton(
      relative_rect=pygame.Rect(20, 20, 100, 40),
      text="Back",
      manager=self.ui_manager
  )
  self._button_callbacks[self.btn_back] = self._on_back
  ```
- [x] Remove from `self.buttons` list (if it exists)
- [x] Verify: Back button works

**Notes:** Replaced Button with UIButton in _create_ui(). Kept self.buttons list empty for compatibility. Added callback to self._button_callbacks dict.

---

### Task 4.5: Update TestLabScene Event Loop [Medium]
**File:** `ui/test_lab_scene.py` (`handle_input()` method, around line 2852)
**Tests:** Full test lab functionality

- [x] Add UIManager event processing at start of event loop:
  ```python
  def handle_input(self, events):
      for event in events:
          # Process pygame_gui events first
          self.ui_manager.process_events(event)

          # Handle button presses
          if event.type == pygame_gui.UI_BUTTON_PRESSED:
              callback = self._button_callbacks.get(event.ui_element)
              if callback:
                  callback()
                  continue

          # ... rest of existing event handling
  ```
- [x] Update draw method to include UIManager:
  ```python
  # In draw() method, after drawing other elements:
  self.ui_manager.update(time_delta)  # time_delta in seconds
  self.ui_manager.draw_ui(screen)
  ```
- [x] Remove legacy button draw/handle_event calls
- [x] Verify: All test lab functionality works

**Notes:** Added UIManager.process_events() and UI_BUTTON_PRESSED handling at start of handle_input(). Removed legacy button loop. Added UIManager.update(1/60) and draw_ui() to draw method. Using fixed 60 FPS time delta. All 79 tests pass.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Run `pytest tests/ --testmon` - passes (2 affected tests pass)
- [x] **MANUAL TESTS:**
  - [x] Combat Lab scene loads
  - [x] Back button works (returns to menu)
  - [x] Select a test, right-click to open JSON popup
  - [x] JSON popup close button works
  - [x] Trigger a confirmation dialog (e.g., update expected values)
  - [x] Confirm button works
  - [x] Cancel button works
  - [x] ESC key still closes popups/dialogs
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 5
