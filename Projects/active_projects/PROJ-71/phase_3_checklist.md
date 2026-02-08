# Phase 3: Sub-Window Hotkey Integration

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-71 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Add hotkey support and tooltip enrichment to all sub-windows opened from the strategy layer.

---

## Tasks

### Task 3.1: Fleet Orders Window hotkeys [Medium]
**File:** `game/ui/screens/fleet_orders_window.py`
**Tests:** `pytest tests/ --testmon`

- [x] Add `input_mapper` parameter to `FleetOrdersWindow.__init__()`
- [x] Add keyboard event handling in `process_event()` via new `_handle_keydown()`:
  - `FLEET_ORDERS_UNDO` (Ctrl+Z) -> undo last delete
  - `FLEET_ORDERS_CLEAR` (Delete) -> clear all orders (with confirmation)
- [x] Add tooltips to btn_undo and btn_clear showing their hotkeys
- [x] Verify: Open Fleet Orders, press Ctrl+Z to undo, tooltip shows on hover

**Notes:** Added `_apply_tooltips()` and `_handle_keydown()` methods. `process_event` now dispatches KEYDOWN events through InputMapper before button handling.

---

### Task 3.2: Build Queue Screen hotkeys [Medium]
**File:** `game/ui/screens/build_queue_screen.py`
**Tests:** `pytest tests/ --testmon`

- [x] Add `input_mapper` parameter to `BuildQueueScreen.__init__()`
- [x] Add keyboard event handling:
  - `BUILD_QUEUE_CLOSE` (ESC) -> close screen
  - `BUILD_QUEUE_ADD` (A) -> add selected design to queue
  - `BUILD_QUEUE_REMOVE` (Delete) -> remove selected queue item
  - `BUILD_QUEUE_CAT_COMPLEXES` (1) -> switch to Complexes category
  - `BUILD_QUEUE_CAT_SHIPS` (2) -> switch to Ships category
  - `BUILD_QUEUE_CAT_SATELLITES` (3) -> switch to Satellites category
  - `BUILD_QUEUE_CAT_FIGHTERS` (4) -> switch to Fighters category
- [x] Add tooltips to Close, Add, Remove, and category buttons
- [x] Verify: Open Build Queue, press ESC to close, 1-4 switch categories

**Notes:** Added `_handle_keydown()`, `_handle_remove_hotkey()`, and `_apply_tooltips()` methods. Integrated into `handle_event()` before screenshot handling.

---

### Task 3.3: Transfer Dialog hotkeys [Medium]
**File:** `game/ui/screens/transfer_dialog.py`
**Tests:** `pytest tests/ --testmon`

- [x] Add `input_mapper` parameter to `TransferDialog.__init__()`
- [x] Add keyboard event handling:
  - `TRANSFER_CONFIRM` (Enter) -> issue transfer order
  - `TRANSFER_CANCEL` (ESC) -> close dialog
- [x] Add tooltips to btn_confirm and btn_cancel
- [x] Verify: Open Transfer Dialog, press Enter to confirm, ESC to cancel

**Notes:** Added `_handle_keydown()` and `_apply_tooltips()` methods. Integrated into `process_event()`.

---

### Task 3.4: Build Queue List Window hotkeys [Simple]
**File:** `game/ui/screens/build_queue_list_window.py`
**Tests:** `pytest tests/ --testmon`

- [x] Add `input_mapper` parameter to constructor
- [x] Add ESC handling to close the window via `_handle_keydown()`
- [x] Verify: Open Build Queues list, press ESC to close

**Notes:** Added `process_event()` override with `_handle_keydown()` dispatch. Reuses `BUILD_QUEUE_CLOSE` action.

---

### Task 3.5: Pass InputMapper to sub-window creation calls [Medium]
**File:** `game/ui/screens/strategy_ui.py`
**Tests:** `pytest tests/ --testmon`

- [x] Update `open_orders_window()` to pass `self._mapper` to `FleetOrdersWindow`
- [x] Update `open_transfer_dialog()` to pass `self._mapper` to `TransferDialog`
- [x] Update `open_build_queue_list()` to pass `self._mapper` to `BuildQueueListWindow`

**File:** `game/ui/screens/strategy_screen.py`
- [x] Update `on_build_yard_click()` to pass `self.input_mapper` to `BuildQueueScreen`
- [x] Update `on_fleet_build_click()` to pass `self.input_mapper` to `BuildQueueScreen`
- [x] Verify: All sub-windows receive mapper and hotkeys work within them

**Notes:** All five creation sites updated to pass input_mapper through.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Fleet Orders: Ctrl+Z undo works, tooltips show
- [x] Build Queue: ESC closes, 1-4 switch categories, Delete removes
- [x] Transfer Dialog: Enter confirms, ESC cancels
- [x] Build Queue List: ESC closes
- [x] Full test suite passes (`pytest tests/ -n 12`)
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
