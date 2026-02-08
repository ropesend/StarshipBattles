# Phase 3: Sub-Window Hotkey Integration

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-71 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Add hotkey support and tooltip enrichment to all sub-windows opened from the strategy layer.

---

## Tasks

### Task 3.1: Fleet Orders Window hotkeys [Medium]
**File:** `game/ui/screens/fleet_orders_window.py`
**Tests:** `pytest tests/ --testmon`

- [ ] Add `input_mapper` parameter to `FleetOrdersWindow.__init__()`
- [ ] Add keyboard event handling in `handle_event()` or new `_handle_keydown()`:
  - `FLEET_ORDERS_UNDO` (Ctrl+Z) -> undo last delete
  - `FLEET_ORDERS_CLEAR` -> clear all orders (with confirmation)
- [ ] Add tooltips to btn_undo and btn_clear showing their hotkeys
- [ ] Verify: Open Fleet Orders, press Ctrl+Z to undo, tooltip shows on hover

**Notes:**

---

### Task 3.2: Build Queue Screen hotkeys [Medium]
**File:** `game/ui/screens/build_queue_screen.py`
**Tests:** `pytest tests/ --testmon`

- [ ] Add `input_mapper` parameter to `BuildQueueScreen.__init__()`
- [ ] Add keyboard event handling:
  - `BUILD_QUEUE_CLOSE` (ESC) -> close screen
  - `BUILD_QUEUE_ADD` -> add selected design to queue
  - `BUILD_QUEUE_REMOVE` (Delete) -> remove selected queue item
  - `BUILD_QUEUE_CAT_COMPLEXES` (1) -> switch to Complexes category
  - `BUILD_QUEUE_CAT_SHIPS` (2) -> switch to Ships category
  - `BUILD_QUEUE_CAT_SATELLITES` (3) -> switch to Satellites category
  - `BUILD_QUEUE_CAT_FIGHTERS` (4) -> switch to Fighters category
- [ ] Add tooltips to Close, Add, Remove, and category buttons
- [ ] Verify: Open Build Queue, press ESC to close, 1-4 switch categories

**Notes:**

---

### Task 3.3: Transfer Dialog hotkeys [Medium]
**File:** `game/ui/screens/transfer_dialog.py`
**Tests:** `pytest tests/ --testmon`

- [ ] Add `input_mapper` parameter to `TransferDialog.__init__()`
- [ ] Add keyboard event handling:
  - `TRANSFER_CONFIRM` (Enter) -> issue transfer order
  - `TRANSFER_CANCEL` (ESC) -> close dialog
- [ ] Add tooltips to btn_confirm and btn_cancel
- [ ] Verify: Open Transfer Dialog, press Enter to confirm, ESC to cancel

**Notes:**

---

### Task 3.4: Build Queue List Window hotkeys [Simple]
**File:** `game/ui/screens/build_queue_list_window.py`
**Tests:** `pytest tests/ --testmon`

- [ ] Add `input_mapper` parameter to constructor
- [ ] Add ESC handling to close the window
- [ ] Verify: Open Build Queues list, press ESC to close

**Notes:**

---

### Task 3.5: Pass InputMapper to sub-window creation calls [Medium]
**File:** `game/ui/screens/strategy_ui.py`
**Tests:** `pytest tests/ --testmon`

- [ ] Update `open_orders_window()` (~line 896) to pass `self._mapper` to `FleetOrdersWindow`
- [ ] Update `open_fleet_report_window()` (~line 906) - add mapper param if fleet report gets hotkeys
- [ ] Update `open_transfer_dialog()` (~line 926) to pass `self._mapper` to `TransferDialog`
- [ ] Update `open_build_queue_list()` (~line 877) to pass `self._mapper` to `BuildQueueListWindow`

**File:** `game/ui/screens/strategy_screen.py`
- [ ] Update `on_build_yard_click()` to pass `self.input_mapper` to `BuildQueueScreen`
- [ ] Update `on_fleet_build_click()` to pass `self.input_mapper` to `BuildQueueScreen`
- [ ] Verify: All sub-windows receive mapper and hotkeys work within them

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Fleet Orders: Ctrl+Z undo works, tooltips show
- [ ] Build Queue: ESC closes, 1-4 switch categories, Delete removes
- [ ] Transfer Dialog: Enter confirms, ESC cancels
- [ ] Build Queue List: ESC closes
- [ ] Full test suite passes (`pytest tests/ -n 12`)
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
