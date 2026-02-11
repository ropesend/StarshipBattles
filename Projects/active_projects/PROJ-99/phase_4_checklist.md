# Phase 4: Integration

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-99 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Wire the EmpirePanelWindow into the existing strategy UI event/window infrastructure so the Empire button opens the panel and keyboard shortcut works.

---

## Tasks

### Task 4.1: Add to StrategyWindowManager [Simple]
**File:** `game/ui/screens/strategy_window_manager.py`
**Tests:** `pytest tests/ -n 12` (full regression)

- [x] Add import at top (after line 20, with other window imports):
  ```python
  from game.ui.screens.empire_panel_window import EmpirePanelWindow
  ```
- [x] Add `self.empire_panel_window = None` in `__init__` (after line 84, with other window refs)
- [x] Add new section after Event Log Window section (after line 230):
  ```python
  # =========================================================================
  # Empire Panel Window
  # =========================================================================

  def open_empire_panel(self) -> None:
      """Open the Empire Panel Window."""
      if self.empire_panel_window:
          self.empire_panel_window.kill()

      empire = self.scene.current_empire

      w, h = int(self.width * 0.9), int(self.height * 0.9)
      rect = pygame.Rect((self.width - w) / 2, (self.height - h) / 2, w, h)

      self.empire_panel_window = EmpirePanelWindow(
          rect,
          self.manager,
          empire,
          on_close_callback=self._on_empire_panel_closed,
      )

  def _on_empire_panel_closed(self) -> None:
      """Callback when empire panel window is closed."""
      self.empire_panel_window = None
  ```

**Notes:** Complete

### Task 4.2: Add to StrategyEventRouter [Simple]
**File:** `game/ui/screens/strategy_event_router.py`
**Tests:** `pytest tests/ -n 12` (full regression)

- [x] In `has_modal_open()`, add after line 74 (after `event_log_window` check):
  ```python
  if wm.empire_panel_window is not None:
      return True
  ```
- [x] In `_handle_button_pressed()`, add new elif (after line 158 `btn_events` handler):
  ```python
  elif event.ui_element == ui.btn_empire:
      ui.open_empire_panel()
  ```
- [x] In `_handle_window_close()`, add after line 240 (after `event_log_window` close):
  ```python
  elif event.ui_element == wm.empire_panel_window:
      wm._on_empire_panel_closed()
  ```

**Notes:** Complete

### Task 4.3: Add delegation method to StrategyUI [Simple]
**File:** `game/ui/screens/strategy_ui.py`
**Tests:** `pytest tests/ -n 12` (full regression)

- [x] Add at the end of the Window Management Delegation section (after existing delegation methods, around line 380):
  ```python
  def open_empire_panel(self):
      """Open the Empire Panel Window."""
      self._window_manager.open_empire_panel()
  ```

**Notes:** Complete

### Task 4.4: Add keyboard shortcut handler [Simple]
**File:** `game/ui/screens/strategy_input_handler.py`
**Tests:** `pytest tests/ -n 12` (full regression)

- [x] In `_handle_keydown_mapped()`, add after line 175 (`STRATEGY_OPEN_BUILD_QUEUES` handler):
  ```python
  elif action == InputAction.STRATEGY_OPEN_EMPIRE:
      self.scene.ui.open_empire_panel()
  ```
- [x] Verify: `InputAction.STRATEGY_OPEN_EMPIRE` already exists in `input_actions.py:42` (no change needed there)

**Notes:** Complete

### Task 4.5: Full regression test [Simple]
**Tests:** `pytest tests/ -n 12`

- [x] Run full test suite: `pytest tests/ -n 12`
- [x] Verify baseline: 7691 tests passing, 0 failures
- [x] If any failures, investigate and fix before completing

**Notes:** Fixed 2 test fixtures missing empire_panel_window field

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Full test suite passes: `pytest tests/ -n 12`
- [ ] Manual test: click Empire button → window opens with 3 tabs
- [ ] Manual test: Treasury tab shows production/expenses/storage data
- [ ] Manual test: Population tab shows portrait, flag, and species attributes
- [ ] Manual test: Tab switching works correctly
- [ ] Manual test: Window close (X button) works and button re-opens
- [ ] Manual test: Keyboard shortcut opens the panel
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to indicate project complete
