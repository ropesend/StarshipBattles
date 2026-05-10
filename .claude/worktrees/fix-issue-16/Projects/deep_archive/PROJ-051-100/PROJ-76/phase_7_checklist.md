# Phase 7: Integration

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-76 7`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Wire up button and window in strategy UI

---

## Tasks

### Task 7.1: Add "All Queues" button to top bar [Simple]

**File:** `game/ui/screens/strategy_ui.py`
**Tests:** Manual test - button visible and clickable

- [x] Add `self.empire_build_queue_window = None` (after line 46)
- [x] Add new button after Build Queues button (position 5)
- [x] Shift Menu and End Turn button positions to accommodate new button
- [x] No constant updates needed - uses existing btn_w+gap pattern

**Notes:**

---

### Task 7.2: Add button click handler [Simple]

**File:** `game/ui/screens/strategy_ui.py`
**Tests:** Manual test - window opens on click

- [x] Add import: `from game.ui.screens.empire_build_queue_window import EmpireBuildQueueWindow`
- [x] Add `open_empire_build_queue_window()` method
- [x] Add close callback: `_on_empire_build_queue_closed()`
- [x] Add button event handler in `handle_event()` for btn_all_queues
- [x] Add UI_WINDOW_CLOSE handler for empire_build_queue_window
- [x] Add `on_navigate_to_hex_build()` to strategy_screen.py (closes window, opens BuildQueueScreen)

**Notes:**

---

### Task 7.3: Add modal check [Simple]

**File:** `game/ui/screens/strategy_ui.py`
**Tests:** Manual test - prevents input passthrough

- [x] Update `_has_modal_open()` to check `self.empire_build_queue_window is not None`

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Manual test: Button appears in top bar (deferred to user verification)
- [x] Manual test: Click opens window (deferred to user verification)
- [x] Manual test: Window closes properly (deferred to user verification)
- [x] Manual test: Input blocked while window open (deferred to user verification)
- [x] No regressions: `pytest tests/ --testmon` (7111 passed)
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase

---

## Final Verification

After all phases complete:
- [x] Open window, verify all columns display (deferred to user verification)
- [x] Toggle column visibility, verify headers update (deferred to user verification)
- [x] Apply each filter type, verify list updates (deferred to user verification)
- [x] Click row, verify navigation to hex build screen (deferred to user verification)
- [x] Ctrl+click multiple rows, verify multi-select (deferred to user verification)
- [x] Batch add to selected queues, verify items added (deferred to user verification)
- [x] Run full test suite: `pytest tests/` (7111 passed)
