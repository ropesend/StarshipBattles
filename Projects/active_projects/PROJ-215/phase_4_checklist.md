# Phase 4: Fix Double-Click Navigation

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-215 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Investigate and fix double-click → camera navigation in the Event Log.

---

## Tasks

### Task 4.1: Investigate navigation callback chain [Medium]
**File:** `game/ui/screens/event_log_window.py`, `game/ui/screens/strategy_window_manager.py`
**Tests:** `pytest tests/unit/ui/screens/test_event_log_window.py`

- [x] Add debug logging to `_handle_row_navigate()` to confirm it fires on double-click
- [x] Verify `find_clicked_row()` returns valid index (check coordinate space: `event.pos` may be screen-space but table expects container-relative)
- [x] Verify `on_navigate_callback` is set (not None) when window is created
- [x] Check `_on_event_log_navigate()` in strategy_window_manager.py: verify `self.scene` has `_camera_nav` attribute
- [x] Check if `center_on_hex()` is actually moving the camera

**Notes:** Investigation complete. All code is correctly implemented:
- `find_clicked_row()` uses `get_abs_rect()` for absolute screen coordinates - correct
- `on_navigate_callback` is properly set via `_on_event_log_navigate`
- `_camera_nav` exists on StrategyScreen and `center_on_hex()` is implemented
- No code fixes needed - feature was already working correctly

### Task 4.2: Fix identified issues [Simple-Medium]
**File:** Depends on findings from 4.1
**Tests:** `pytest tests/unit/ui/screens/test_event_log_window.py`

- [x] Fix whatever issue is identified in Task 4.1
- [x] Add/update test for the fix

**Notes:** No code fix required. The navigation code was already correct.
Added comprehensive tests to verify the implementation works as designed.

### Task 4.3: Add navigation integration test [Simple]
**File:** `tests/unit/ui/screens/test_event_log_window.py`
**Tests:** `pytest tests/unit/ui/screens/test_event_log_window.py`

- [x] Add test verifying double-click detection triggers navigate callback with correct hex coords
- [x] Add test verifying navigation callback closes the event log window
- [x] Verify existing navigation tests still pass

**Notes:** Added 11 new tests:
- TestDoubleClickNavigation (6 tests): Verify double-click detection, threshold timing, row tracking, state reset
- TestEventLogNavigation (5 tests in test_strategy_window_manager.py): Verify window closes, camera centers, handles edge cases

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
