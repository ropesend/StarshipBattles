# Phase 3: Drop/Load Quick Commands

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-100 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Add D (Drop Cargo) and L (Load Cargo) commands with input-mode-then-click flow and a simplified CargoQuickDialog.

---

## Tasks

### Task 3.1: Add new InputAction enum values [Simple]
**File:** `game/core/input_actions.py`
**Tests:** `pytest tests/unit/core/ -k input`

- [x] Add after `FLEET_TRANSFER = "fleet.transfer"` (line 54):
  ```python
  FLEET_DROP_CARGO = "fleet.drop_cargo"
  FLEET_LOAD_CARGO = "fleet.load_cargo"
  ```
- [x] Add display names after `InputAction.FLEET_TRANSFER` entry (line 107):
  ```python
  InputAction.FLEET_DROP_CARGO: "Drop Cargo",
  InputAction.FLEET_LOAD_CARGO: "Load Cargo",
  ```
- [x] Add to "Fleet Commands" ACTION_GROUPS after `InputAction.FLEET_TRANSFER` (line 158):
  ```python
  InputAction.FLEET_DROP_CARGO,
  InputAction.FLEET_LOAD_CARGO,
  ```
- [x] Verify: `InputAction.FLEET_DROP_CARGO.value == "fleet.drop_cargo"` etc.

**Notes:** Complete - enum, display names, and groups updated.

### Task 3.2: Add default keybindings [Simple]
**File:** `data/default_keybindings.json`
**Tests:** Manual verification

- [x] Add after `"fleet.cancel_mode"` entry (line 27):
  ```json
  "fleet.drop_cargo": {"key": "K_d", "modifiers": []},
  "fleet.load_cargo": {"key": "K_l", "modifiers": []}
  ```
- [x] Verify: No binding conflicts (D was freed by Phase 1's Shift+D for design screen)

**Notes:** Complete - D and L keys mapped.

### Task 3.3: Add DROP_CARGO/LOAD_CARGO input mode handlers [Medium]
**File:** `game/ui/screens/strategy_input_handler.py`
**Tests:** `pytest tests/unit/ui/screens/test_strategy_input_handler_transfer.py`

- [x] In `_handle_keydown_mapped()`, after FLEET_TRANSFER block (~line 148), add handlers for DROP_CARGO and LOAD_CARGO
- [x] Add `'DROP_CARGO', 'LOAD_CARGO'` to ESC/cancel mode tuples (both mapped and legacy handlers)
- [x] Add `'DROP_CARGO', 'LOAD_CARGO'` to context list check (line 113)
- [x] Add import for `InputAction.FLEET_DROP_CARGO` and `InputAction.FLEET_LOAD_CARGO` (already imported via InputAction)

**Notes:** Complete - mapped handler, legacy ESC, and context list all updated.

### Task 3.4: Add click handlers for DROP_CARGO/LOAD_CARGO modes [Medium]
**File:** `game/ui/screens/strategy_input_handler.py`
**Tests:** `pytest tests/unit/ui/screens/test_strategy_input_handler_transfer.py`

- [x] Add `_handle_drop_cargo_mode_click(self, mx, my, button)` method
- [x] Add `_handle_load_cargo_mode_click(self, mx, my, button)` method (same pattern, direction='load')
- [x] Wire both into `handle_click()` dispatch
- [x] Verify: D key → click → `open_cargo_quick_dialog(fleet, hex, 'unload')` called

**Notes:** Complete - click handlers and dispatch wiring added.

### Task 3.5: Create CargoQuickDialog [Complex]
**New file:** `game/ui/screens/cargo_quick_dialog.py`
**Tests:** `pytest tests/unit/ui/screens/test_cargo_quick_dialog.py` (Phase 4)

- [x] Create `CargoQuickDialog(UIWindow)` class with constructor
- [x] `_setup_ui()`: Title label showing "Drop Cargo" or "Load Cargo", cargo list area, Confirm/Cancel buttons
- [x] `_populate_items()`: Query fleet cargo for 'unload' or colony populations for 'load'
- [x] Each cargo item row: Label text + UIHorizontalSlider + UIButton("All")
- [x] "All" button per item: sets slider to max value
- [x] `_issue_orders()` on Confirm: Issue IssueTransferCommand for each item with slider > 0
- [x] `process_event()`: Handle UI events (slider moves, button clicks, keyboard via InputMapper)
- [x] Handle no-colony case: If direction='unload' and no colony at hex, show message

**Notes:** Complete - ~280 lines, handles both drop and load with sliders and All buttons.

### Task 3.6: Wire CargoQuickDialog into window manager and UI [Simple]
**File:** `game/ui/screens/strategy_window_manager.py`
**File:** `game/ui/screens/strategy_ui.py`
**Tests:** `pytest tests/unit/ui/screens/test_cargo_quick_dialog.py` (Phase 4)

- [x] Add `open_cargo_quick_dialog()` to `strategy_window_manager.py`
- [x] Add `open_cargo_quick_dialog()` delegation to `strategy_ui.py`
- [x] Verify: `scene.ui.open_cargo_quick_dialog(fleet, hex, 'load')` opens dialog

**Notes:** Complete - window manager and UI wiring added.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] `pytest tests/ -n 12` passes: 7694 passed
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 4
