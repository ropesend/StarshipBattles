# Phase 3: Drop/Load Quick Commands

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-100 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Add D (Drop Cargo) and L (Load Cargo) commands with input-mode-then-click flow and a simplified CargoQuickDialog.

---

## Tasks

### Task 3.1: Add new InputAction enum values [Simple]
**File:** `game/core/input_actions.py`
**Tests:** `pytest tests/unit/core/ -k input`

- [ ] Add after `FLEET_TRANSFER = "fleet.transfer"` (line 54):
  ```python
  FLEET_DROP_CARGO = "fleet.drop_cargo"
  FLEET_LOAD_CARGO = "fleet.load_cargo"
  ```
- [ ] Add display names after `InputAction.FLEET_TRANSFER` entry (line 107):
  ```python
  InputAction.FLEET_DROP_CARGO: "Drop Cargo",
  InputAction.FLEET_LOAD_CARGO: "Load Cargo",
  ```
- [ ] Add to "Fleet Commands" ACTION_GROUPS after `InputAction.FLEET_TRANSFER` (line 158):
  ```python
  InputAction.FLEET_DROP_CARGO,
  InputAction.FLEET_LOAD_CARGO,
  ```
- [ ] Verify: `InputAction.FLEET_DROP_CARGO.value == "fleet.drop_cargo"` etc.

**Notes:**

### Task 3.2: Add default keybindings [Simple]
**File:** `data/default_keybindings.json`
**Tests:** Manual verification

- [ ] Add after `"fleet.cancel_mode"` entry (line 27):
  ```json
  "fleet.drop_cargo": {"key": "K_d", "modifiers": []},
  "fleet.load_cargo": {"key": "K_l", "modifiers": []}
  ```
- [ ] Verify: No binding conflicts (D was freed by Phase 1's Shift+D for design screen)

**Notes:**

### Task 3.3: Add DROP_CARGO/LOAD_CARGO input mode handlers [Medium]
**File:** `game/ui/screens/strategy_input_handler.py`
**Tests:** `pytest tests/unit/ui/screens/test_strategy_input_handler_transfer.py`

- [ ] In `_handle_keydown_mapped()`, after FLEET_TRANSFER block (~line 148), add:
  ```python
  elif action == InputAction.FLEET_DROP_CARGO:
      if self.scene.selected_fleet:
          self.input_mode = 'DROP_CARGO'
          log_debug("Input Mode: DROP_CARGO - Click target hex.")
      else:
          log_debug("Select a fleet first.")

  elif action == InputAction.FLEET_LOAD_CARGO:
      if self.scene.selected_fleet:
          self.input_mode = 'LOAD_CARGO'
          log_debug("Input Mode: LOAD_CARGO - Click target hex.")
      else:
          log_debug("Select a fleet first.")
  ```
- [ ] Add `'DROP_CARGO', 'LOAD_CARGO'` to ESC/cancel mode tuples (both mapped and legacy handlers)
- [ ] Add `'DROP_CARGO', 'LOAD_CARGO'` to context list check (line 113)
- [ ] Add import for `InputAction.FLEET_DROP_CARGO` and `InputAction.FLEET_LOAD_CARGO` (already imported via InputAction)

**Notes:** No legacy handler needed for D/L — new features don't need legacy fallback.

### Task 3.4: Add click handlers for DROP_CARGO/LOAD_CARGO modes [Medium]
**File:** `game/ui/screens/strategy_input_handler.py`
**Tests:** `pytest tests/unit/ui/screens/test_strategy_input_handler_transfer.py`

- [ ] Add `_handle_drop_cargo_mode_click(self, mx, my, button)` method:
  ```python
  def _handle_drop_cargo_mode_click(self, mx, my, button):
      if button == 1:
          world_pos = self.scene.camera.screen_to_world((mx, my))
          target_hex = pixel_to_hex(world_pos.x, world_pos.y, self.scene.hex_size)
          fleet = self.scene.selected_fleet
          self.scene.ui.open_cargo_quick_dialog(fleet, target_hex, 'unload')
          self.input_mode = 'SELECT'
          return True
      elif button == 3:
          self.input_mode = 'SELECT'
          log_debug("Input Mode: SELECT")
          return True
      return False
  ```
- [ ] Add `_handle_load_cargo_mode_click(self, mx, my, button)` method (same pattern, direction='load')
- [ ] Wire both into `handle_click()` dispatch:
  ```python
  elif self.input_mode == 'DROP_CARGO':
      return self._handle_drop_cargo_mode_click(mx, my, button)
  elif self.input_mode == 'LOAD_CARGO':
      return self._handle_load_cargo_mode_click(mx, my, button)
  ```
- [ ] Verify: D key → click → `open_cargo_quick_dialog(fleet, hex, 'unload')` called

**Notes:**

### Task 3.5: Create CargoQuickDialog [Complex]
**New file:** `game/ui/screens/cargo_quick_dialog.py`
**Tests:** `pytest tests/unit/ui/screens/test_cargo_quick_dialog.py` (Phase 4)

- [ ] Create `CargoQuickDialog(UIWindow)` class with constructor:
  `(relative_rect, manager, fleet, hex_coord, direction, scene, input_mapper=None)`
- [ ] `_setup_ui()`: Title label showing "Drop Cargo" or "Load Cargo", cargo list area, Confirm/Cancel buttons
- [ ] `_populate_items()`:
  - For `'unload'` (drop): Query fleet's current cargo via `facade.get_fleet(fleet_id)` → `passengers_current`
  - For `'load'`: Query colony populations at hex via `facade.get_planets_at_hex(hex_coord)` + `facade.get_planet(planet_id)` → `population_details`
- [ ] Each cargo item row: Label text + UIHorizontalSlider + UIButton("All")
- [ ] "All" button per item: sets slider to max value
- [ ] `_issue_orders()` on Confirm:
  - For each item with slider value > 0:
  - If slider at max, use amount=0 (engine convention for "all")
  - Otherwise use slider value as amount
  - Create `IssueTransferCommand(fleet_id, planet_id, cargo_type, direction, amount, species_id)`
  - Dispatch via `facade.handle_command(cmd)`
  - Close dialog on success
- [ ] `process_event()`: Handle UI events (slider moves, button clicks, keyboard via InputMapper)
- [ ] Handle no-colony case: If direction='unload' and no colony at hex, show message "No colony at this location"
- [ ] Estimated size: ~150-200 lines

**Notes:** Reuses `IssueTransferCommand` as-is. No backend changes needed.

### Task 3.6: Wire CargoQuickDialog into window manager and UI [Simple]
**File:** `game/ui/screens/strategy_window_manager.py`
**File:** `game/ui/screens/strategy_ui.py`
**Tests:** `pytest tests/unit/ui/screens/test_cargo_quick_dialog.py` (Phase 4)

- [ ] Add to `strategy_window_manager.py` after `open_transfer_dialog` method (~line 310):
  ```python
  def open_cargo_quick_dialog(self, fleet, hex_coord, direction) -> None:
      from game.ui.screens.cargo_quick_dialog import CargoQuickDialog
      win_w, win_h = 500, 450
      win_rect = pygame.Rect(0, 0, win_w, win_h)
      win_rect.center = (self.width // 2, self.height // 2)
      CargoQuickDialog(
          relative_rect=win_rect, manager=self.manager,
          fleet=fleet, hex_coord=hex_coord, direction=direction,
          scene=self.scene, input_mapper=self._mapper,
      )
  ```
- [ ] Add to `strategy_ui.py` after `open_transfer_dialog` delegation (~line 380):
  ```python
  def open_cargo_quick_dialog(self, fleet, hex_coord, direction):
      self._window_manager.open_cargo_quick_dialog(fleet, hex_coord, direction)
  ```
- [ ] Verify: `scene.ui.open_cargo_quick_dialog(fleet, hex, 'load')` opens dialog

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `pytest tests/ --testmon` passes
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 4
