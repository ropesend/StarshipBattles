# Phase 3: Migrate Button to pygame_gui

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-14 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Replace all production uses of legacy Button with pygame_gui UIButton

---

## Tasks

### Task 3.1: Create UIManager for main menu [Medium]
**File:** `game/app.py`
**Tests:** Manual - launch game, verify menu displays

- [x] Add import: `import pygame_gui` (if not already present)
- [x] In `__init__`, create menu UIManager: `self.menu_ui_manager = pygame_gui.UIManager((WIDTH, HEIGHT))`
- [x] Initialize empty menu_buttons list for storing button references

**Notes:** Completed 2026-01-25. Added UIManager initialization in Game.__init__.

---

### Task 3.2: Migrate menu buttons to UIButton [Medium]
**File:** `game/app.py`
**Lines:** 127-136 (update_menu_buttons method)
**Tests:** Manual - click each of 10 menu buttons

Replace 10 legacy Button instances with pygame_gui UIButton:
- [x] Quickstart 1P button
- [x] Quickstart 2P button
- [x] New Game button
- [x] Load Game button
- [x] Race Setup button
- [x] Design Workshop button
- [x] Battle Setup button
- [x] Formation Editor button
- [x] Combat Lab button
- [x] Research Tree button

- [x] Kill old buttons before recreating (for window resize)

**Notes:** Completed 2026-01-25. Used button_configs list for cleaner code.

---

### Task 3.3: Update menu event handling [Medium]
**File:** `game/app.py`
**Lines:** ~513-515 (event handling section)
**Tests:** Manual - verify button clicks trigger correct actions

- [x] Remove legacy pattern: `for btn in self.menu_buttons: btn.handle_event(event)`
- [x] Add: `self.menu_ui_manager.process_events(event)`
- [x] Add button press handler for `pygame_gui.UI_BUTTON_PRESSED`

**Notes:** Completed 2026-01-25. Updated _forward_event_to_scene method.

---

### Task 3.4: Update menu drawing [Medium]
**File:** `game/app.py`
**Lines:** ~664-665 (_draw_menu method)
**Tests:** Manual - verify menu renders correctly

- [x] Remove legacy pattern: `for btn in self.menu_buttons: btn.draw(self.screen)`
- [x] Add UIManager update: `self.menu_ui_manager.update(self.clock.get_time() / 1000.0)`
- [x] Add UIManager draw: `self.menu_ui_manager.draw_ui(self.screen)`

**Notes:** Completed 2026-01-25.

---

### Task 3.5: Handle window resize for menu [Simple]
**File:** `game/app.py`
**Lines:** ~537 (resize handling)
**Tests:** Manual - resize window, verify buttons reposition

- [x] In resize handler for MENU state, call: `self.menu_ui_manager.set_window_resolution((WIDTH, HEIGHT))`
- [x] Recreate buttons with new positions via `update_menu_buttons()`

**Notes:** Completed 2026-01-25. Resolution update added to update_menu_buttons.

---

### Task 3.6: Migrate JSONPopup buttons in test_lab_scene.py [Medium]
**File:** `ui/test_lab_scene.py`
**Lines:** 52, 62, 93 (JSONPopup class)
**Tests:** Manual - open Combat Lab, view JSON popup, click Close

- [x] Add UIManager parameter to JSONPopup.__init__
- [x] Replace `self.close_button = Button(...)` with pygame_gui UIButton
- [x] Update handle_event to check `pygame_gui.UI_BUTTON_PRESSED`
- [x] Remove `self.close_button.draw()` call (manager handles drawing)
- [x] Ensure UIManager.draw_ui() is called

**Notes:** Completed 2026-01-25. Added ui_manager parameter, kill button on close.

---

### Task 3.7: Migrate ConfirmationDialog buttons [Medium]
**File:** `ui/test_lab_scene.py`
**Lines:** 153-157, 182-183 (ConfirmationDialog class)
**Tests:** Manual - trigger confirmation dialog, test Confirm/Cancel

- [x] Add UIManager parameter to ConfirmationDialog.__init__
- [x] Replace confirm_button with pygame_gui UIButton
- [x] Replace cancel_button with pygame_gui UIButton
- [x] Update handle_event for pygame_gui event pattern
- [x] Remove manual draw calls

**Notes:** Completed 2026-01-25. Added _kill_buttons method to clean up on close.

---

### Task 3.8: Migrate back button in TestLabScene [Medium]
**File:** `ui/test_lab_scene.py`
**Line:** 2321
**Tests:** Manual - open Combat Lab, click Back button

- [x] Create UIManager in TestLabScene.__init__ (or reuse existing)
- [x] Replace `self.btn_back = Button(...)` with pygame_gui UIButton
- [x] Update event handling for back button
- [x] Ensure UIManager.draw_ui() is called in draw method
- [x] Pass UIManager to JSONPopup and ConfirmationDialog when created

**Notes:** Completed 2026-01-25. Removed Button import from test_lab_scene.py.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Game launches successfully
- [x] All 10 menu buttons work (click each one)
- [x] Window resize works - buttons reposition correctly
- [x] Combat Lab loads
- [x] JSONPopup displays and Close button works
- [x] ConfirmationDialog Confirm/Cancel buttons work
- [x] Back button returns to menu
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 4
