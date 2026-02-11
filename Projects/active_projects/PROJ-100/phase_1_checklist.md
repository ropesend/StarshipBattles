# Phase 1: T Key Input Mode + Keybinding Standardization

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-100 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Change T key from immediately opening transfer dialog to entering TRANSFER input mode (click hex, then dialog opens). Standardize keybindings so screen openers use Shift+Key.

---

## Tasks

### Task 1.1: Change T key to set TRANSFER input mode [Simple]
**File:** `game/ui/screens/strategy_input_handler.py`
**Tests:** `pytest tests/unit/ui/screens/test_strategy_input_handler_transfer.py tests/unit/ui/screens/test_strategy_input_handler_hotkeys.py`

- [ ] In `_handle_keydown_mapped()` (line 142-148): Replace `open_transfer_dialog(fleet, fleet.location)` with `self.input_mode = 'TRANSFER'` and log message
- [ ] In `_handle_keydown_legacy()` (line 226-232): Same change — set `self.input_mode = 'TRANSFER'` instead of opening dialog
- [ ] Add `'TRANSFER'` to ESC/cancel mode tuple in mapped handler (line 151): `('MOVE', 'COLONIZE_TARGET', 'JOIN', 'TRANSFER')`
- [ ] Add `'TRANSFER'` to ESC/cancel mode tuple in legacy handler (line 215): `('MOVE', 'COLONIZE_TARGET', 'JOIN', 'TRANSFER')`
- [ ] Add `'TRANSFER'` to context list check (line 113): `self.input_mode in ('MOVE', 'JOIN', 'COLONIZE_TARGET', 'TRANSFER')`
- [ ] Verify: Press T with fleet selected → `input_mode == 'TRANSFER'`

**Notes:**

### Task 1.2: Add TRANSFER mode click handler [Medium]
**File:** `game/ui/screens/strategy_input_handler.py`
**Tests:** `pytest tests/unit/ui/screens/test_strategy_input_handler_transfer.py`

- [ ] Add `_handle_transfer_mode_click(self, mx, my, button)` method after `_handle_colonize_mode_click` (~line 359):
  ```python
  def _handle_transfer_mode_click(self, mx, my, button):
      if button == 1:  # Left Click
          world_pos = self.scene.camera.screen_to_world((mx, my))
          target_hex = pixel_to_hex(world_pos.x, world_pos.y, self.scene.hex_size)
          fleet = self.scene.selected_fleet
          self.scene.ui.open_transfer_dialog(fleet, target_hex)
          self.input_mode = 'SELECT'
          return True
      elif button == 3:  # Right click cancels
          self.input_mode = 'SELECT'
          log_debug("Input Mode: SELECT")
          return True
      return False
  ```
- [ ] Wire into `handle_click()` dispatch (lines 260-268): Add `elif self.input_mode == 'TRANSFER': return self._handle_transfer_mode_click(mx, my, button)` after COLONIZE_TARGET check
- [ ] Verify: In TRANSFER mode, left-click calls `open_transfer_dialog` with clicked hex coordinates

**Notes:**

### Task 1.3: Standardize keybindings — screen openers to Shift+Key [Simple]
**File:** `data/default_keybindings.json`
**Tests:** `pytest tests/unit/ui/screens/test_strategy_input_handler_hotkeys.py`

- [ ] Line 14: `"strategy.open_planets"`: change `"modifiers": []` → `"modifiers": ["shift"]`
- [ ] Line 15: `"strategy.open_empire"`: change `"modifiers": []` → `"modifiers": ["shift"]`
- [ ] Line 16: `"strategy.open_research"`: change `"modifiers": []` → `"modifiers": ["shift"]`
- [ ] Line 17: `"strategy.open_design"`: change `"modifiers": []` → `"modifiers": ["shift"]`
- [ ] Line 18: `"strategy.open_build_queues"`: change `"modifiers": []` → `"modifiers": ["shift"]`
- [ ] Verify: Shift+P/E/R/D/B opens respective screens, plain P/E/R/D/B no longer do

**Notes:** Fleet commands (M/J/C/T/O/F) stay on plain keys. Save (Ctrl+S), Zoom (Shift+G/S) already use modifiers.

### Task 1.4: Update existing tests [Medium]
**Files:**
- `tests/unit/ui/screens/test_strategy_input_handler_transfer.py`
- `tests/unit/ui/screens/test_strategy_input_handler_hotkeys.py`

- [ ] `test_t_key_triggers_transfer_dialog` (transfer file line 19-37): Change assertion from `open_transfer_dialog.assert_called_once_with(...)` to `assert handler.input_mode == 'TRANSFER'`
- [ ] `test_t_triggers_transfer_dialog` (hotkeys file line 85-92): Change assertion from `open_transfer_dialog.assert_called_once_with(...)` to `assert handler.input_mode == 'TRANSFER'`
- [ ] Add `test_transfer_mode_left_click_opens_dialog_at_clicked_hex`: Set mode to TRANSFER, simulate left click, verify `open_transfer_dialog` called with fleet + resolved hex
- [ ] Add `test_transfer_mode_right_click_cancels_to_select`: Set mode to TRANSFER, simulate right click, verify mode reset to SELECT
- [ ] Add `test_escape_cancels_transfer_mode`: Set mode to TRANSFER, press ESC, verify mode reset to SELECT
- [ ] Update any hotkey tests that use plain P/E/R/D/B keys to use shift modifier (check `test_strategy_input_handler_hotkeys.py` for affected tests)
- [ ] Run: `pytest tests/unit/ui/screens/test_strategy_input_handler_transfer.py tests/unit/ui/screens/test_strategy_input_handler_hotkeys.py -v`
- [ ] Run: `pytest tests/ --testmon`

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `pytest tests/ --testmon` passes
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 2
