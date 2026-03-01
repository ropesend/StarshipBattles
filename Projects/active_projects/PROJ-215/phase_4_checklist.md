# Phase 4: Fix Double-Click Navigation

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-215 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Investigate and fix double-click → camera navigation in the Event Log.

---

## Tasks

### Task 4.1: Investigate navigation callback chain [Medium]
**File:** `game/ui/screens/event_log_window.py`, `game/ui/screens/strategy_window_manager.py`
**Tests:** `pytest tests/unit/ui/screens/test_event_log_window.py`

- [ ] Add debug logging to `_handle_row_navigate()` to confirm it fires on double-click
- [ ] Verify `find_clicked_row()` returns valid index (check coordinate space: `event.pos` may be screen-space but table expects container-relative)
- [ ] Verify `on_navigate_callback` is set (not None) when window is created
- [ ] Check `_on_event_log_navigate()` in strategy_window_manager.py: verify `self.scene` has `_camera_nav` attribute
- [ ] Check if `center_on_hex()` is actually moving the camera

**Notes:**

### Task 4.2: Fix identified issues [Simple-Medium]
**File:** Depends on findings from 4.1
**Tests:** `pytest tests/unit/ui/screens/test_event_log_window.py`

- [ ] Fix whatever issue is identified in Task 4.1
- [ ] Add/update test for the fix

**Notes:**

### Task 4.3: Add navigation integration test [Simple]
**File:** `tests/unit/ui/screens/test_event_log_window.py`
**Tests:** `pytest tests/unit/ui/screens/test_event_log_window.py`

- [ ] Add test verifying double-click detection triggers navigate callback with correct hex coords
- [ ] Add test verifying navigation callback closes the event log window
- [ ] Verify existing navigation tests still pass

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
