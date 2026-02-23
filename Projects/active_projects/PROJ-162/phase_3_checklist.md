# Phase 3: Fix Input Handler & Filter Tests

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-162 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Fix the 7 remaining test failures (6 input handler + 1 fleet report filter) caused by inadequate mock setup.

---

## Tasks

### Task 3.1: Fix test_strategy_input_handler_core.py [Simple]
**File:** `tests/unit/ui/screens/test_strategy_input_handler_core.py`
**Tests:** `pytest tests/unit/ui/screens/test_strategy_input_handler_core.py -v`

Root cause: `_resolve_click_target()` does `self.scene.camera.zoom >= 0.5` on MagicMock.

- [ ] In `mock_scene` fixture (line 23-43): Add `scene.camera.zoom = 1.0` after `scene.camera = MagicMock()` (line 38)
- [ ] Also add `scene._get_system_at_hex = MagicMock(return_value=None)` — `_resolve_click_target` calls this, and returning None skips the zoom comparison entirely (simplest fix for click tests that don't care about planet hit-testing)
- [ ] Verify: `TestTransferModeClick::test_click_in_transfer_mode_opens_dialog` passes
- [ ] Verify: `TestCargoModeClicks::test_click_in_drop_cargo_mode_opens_dialog` passes
- [ ] Verify: `TestCargoModeClicks::test_click_in_load_cargo_mode_opens_dialog` passes
- [ ] Verify: All other tests in this file still pass (52+ tests)

**Notes:** The cleanest fix is `scene._get_system_at_hex.return_value = None` because the tests don't care about planet hit-testing — they just want to verify the dialog opens at the raw hex. Setting zoom to a numeric value is a belt-and-suspenders approach.

---

### Task 3.2: Fix test_strategy_input_handler_transfer.py [Simple]
**File:** `tests/unit/ui/screens/test_strategy_input_handler_transfer.py`
**Tests:** `pytest tests/unit/ui/screens/test_strategy_input_handler_transfer.py -v`

Root cause: Same as Task 3.1 — camera.zoom is MagicMock.

- [ ] In `mock_scene` fixture (line 17-29): Add `scene.camera.zoom = 1.0` after `scene.camera = MagicMock()` (line 26)
- [ ] Also add `scene._get_system_at_hex = MagicMock(return_value=None)` for same reason as Task 3.1
- [ ] Verify: `test_transfer_mode_left_click_opens_dialog_at_clicked_hex` passes
- [ ] Verify: `test_drop_cargo_mode_left_click_opens_quick_dialog` passes
- [ ] Verify: `test_load_cargo_mode_left_click_opens_quick_dialog` passes
- [ ] Verify: All other tests in this file still pass

**Notes:**

---

### Task 3.3: Fix test_fleet_report_filters.py [Simple]
**File:** `tests/unit/ui/screens/test_fleet_report_filters.py`
**Tests:** `pytest tests/unit/ui/screens/test_fleet_report_filters.py -v`

Root cause: `make_mock_ship()` doesn't mock `get_cargo_capacity()`. Sort function calls `ship.get_cargo_capacity('passengers')` which returns MagicMock → comparison fails during `sorted()`.

- [ ] Find `make_mock_ship()` helper function (line 8-28)
- [ ] Add default `get_cargo_capacity` mock that returns 0:
  ```python
  ship.get_cargo_capacity = MagicMock(return_value=0)
  ```
- [ ] In `test_sort_by_transport` (line 535): Set transport capacity on the transport ship:
  ```python
  ship_with_pax.get_cargo_capacity = MagicMock(return_value=100)
  ```
  (The test currently sets `get_calculated_stats` cargo_storage but the sort function calls `get_cargo_capacity` instead)
- [ ] Verify: `test_sort_by_transport` passes
- [ ] Verify: All other fleet report filter tests still pass

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `pytest tests/unit/ui/screens/test_strategy_input_handler_core.py -v` — all pass
- [ ] `pytest tests/unit/ui/screens/test_strategy_input_handler_transfer.py -v` — all pass
- [ ] `pytest tests/unit/ui/screens/test_fleet_report_filters.py -v` — all pass
- [ ] `pytest tests/ --testmon` — no regressions
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
