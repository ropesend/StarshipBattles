# Phase 4: Migrate Test Lab Buttons

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-14 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Replace legacy Button in test lab scene dialogs

---

## Tasks

### Task 4.1: Add UIManager to TestLabScene [Simple]
**File:** `ui/test_lab_scene.py`
**Tests:** `pytest tests/unit/ui/test_test_lab_scene.py -v`

- [ ] Add import at top of file:
  ```python
  import pygame_gui
  from pygame_gui.elements import UIButton
  ```
- [ ] In `TestLabScene.__init__()`, after getting screen dimensions, add:
  ```python
  self.ui_manager = pygame_gui.UIManager((self.screen_width, self.screen_height))
  self._button_callbacks = {}  # Maps UIButton -> callback function
  ```
- [ ] Verify: TestLabScene initializes without errors

**Notes:** [Filled during implementation]

---

### Task 4.2: Migrate JSONPopup Close Button [Simple]
**File:** `ui/test_lab_scene.py` (JSONPopup class, line ~52)
**Tests:** Manual - open JSON popup, click close

- [ ] Find `JSONPopup.__init__()` (around line 18)
- [ ] Find `self.close_button = Button(...)` line
- [ ] Replace with UIButton:
  ```python
  # Calculate button position relative to popup
  self.close_button = UIButton(
      relative_rect=pygame.Rect(self.x + self.width - 110, self.y + 10, 100, 40),
      text="Close",
      manager=scene.ui_manager  # Pass scene reference
  )
  ```
- [ ] Update `JSONPopup.handle_event()` to check pygame_gui events:
  ```python
  if event.type == pygame_gui.UI_BUTTON_PRESSED:
      if event.ui_element == self.close_button:
          self.close()
          return True
  ```
- [ ] Update `JSONPopup.close()` to kill button:
  ```python
  def close(self):
      self.is_open = False
      if hasattr(self, 'close_button'):
          self.close_button.kill()
  ```
- [ ] Remove legacy button draw call from `draw()` method
- [ ] Verify: JSON popup close button works

**Notes:** JSONPopup needs reference to scene for ui_manager. May need to pass `scene` to __init__.

---

### Task 4.3: Migrate ConfirmationDialog Buttons [Simple]
**File:** `ui/test_lab_scene.py` (ConfirmationDialog class, lines ~113-159)
**Tests:** Manual - trigger confirmation dialog, test confirm/cancel

- [ ] Find `ConfirmationDialog.__init__()` (around line 113)
- [ ] Replace `self.confirm_button = Button(...)` with UIButton
- [ ] Replace `self.cancel_button = Button(...)` with UIButton
- [ ] Update event handling for pygame_gui events:
  ```python
  if event.type == pygame_gui.UI_BUTTON_PRESSED:
      if event.ui_element == self.confirm_button:
          self._handle_confirm()
          return True
      elif event.ui_element == self.cancel_button:
          self._handle_cancel()
          return True
  ```
- [ ] Update close methods to kill buttons
- [ ] Remove legacy button draw calls
- [ ] Verify: Confirmation dialog buttons work

**Notes:** [Filled during implementation]

---

### Task 4.4: Migrate Back Button [Simple]
**File:** `ui/test_lab_scene.py` (line ~2321)
**Tests:** Manual - click Back in test lab

- [ ] Find `self.btn_back = Button(...)` (around line 2321)
- [ ] Replace with UIButton:
  ```python
  self.btn_back = UIButton(
      relative_rect=pygame.Rect(20, 20, 100, 40),
      text="Back",
      manager=self.ui_manager
  )
  self._button_callbacks[self.btn_back] = self._on_back
  ```
- [ ] Remove from `self.buttons` list (if it exists)
- [ ] Verify: Back button works

**Notes:** [Filled during implementation]

---

### Task 4.5: Update TestLabScene Event Loop [Medium]
**File:** `ui/test_lab_scene.py` (`handle_input()` method, around line 2852)
**Tests:** Full test lab functionality

- [ ] Add UIManager event processing at start of event loop:
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
- [ ] Update draw method to include UIManager:
  ```python
  # In draw() method, after drawing other elements:
  self.ui_manager.update(time_delta)  # time_delta in seconds
  self.ui_manager.draw_ui(screen)
  ```
- [ ] Remove legacy button draw/handle_event calls
- [ ] Verify: All test lab functionality works

**Notes:** time_delta may need to be passed through or calculated

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Run `pytest tests/ --testmon` - passes
- [ ] **MANUAL TESTS:**
  - [ ] Combat Lab scene loads
  - [ ] Back button works (returns to menu)
  - [ ] Select a test, right-click to open JSON popup
  - [ ] JSON popup close button works
  - [ ] Trigger a confirmation dialog (e.g., update expected values)
  - [ ] Confirm button works
  - [ ] Cancel button works
  - [ ] ESC key still closes popups/dialogs
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 5
