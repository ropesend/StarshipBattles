# Phase 4: Tests for Drop/Load

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-100 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Comprehensive test coverage for Drop/Load commands and CargoQuickDialog.

---

## Tasks

### Task 4.1: Input handler tests for D/L keys [Medium]
**File:** `tests/unit/ui/screens/test_strategy_input_handler_transfer.py`
**Tests:** `pytest tests/unit/ui/screens/test_strategy_input_handler_transfer.py -v`

- [x] Add `test_d_triggers_drop_cargo_mode`: Press D with fleet selected → `handler.input_mode == 'DROP_CARGO'`
- [x] Add `test_l_triggers_load_cargo_mode`: Press L with fleet selected → `handler.input_mode == 'LOAD_CARGO'`
- [x] Add `test_d_ignored_without_fleet`: Press D without fleet → mode stays SELECT
- [x] Add `test_l_ignored_without_fleet`: Press L without fleet → mode stays SELECT
- [x] Add `test_drop_cargo_mode_left_click_opens_quick_dialog`: Set mode DROP_CARGO, simulate left click → verify `open_cargo_quick_dialog(fleet, hex, 'unload')` called
- [x] Add `test_load_cargo_mode_left_click_opens_quick_dialog`: Set mode LOAD_CARGO, simulate left click → verify `open_cargo_quick_dialog(fleet, hex, 'load')` called
- [x] Add `test_drop_cargo_mode_right_click_cancels`: Set mode DROP_CARGO, right click → mode resets to SELECT
- [x] Add `test_load_cargo_mode_right_click_cancels`: Set mode LOAD_CARGO, right click → mode resets to SELECT
- [x] Add `test_escape_cancels_drop_cargo_mode`: Set mode DROP_CARGO, press ESC → mode resets to SELECT
- [x] Add `test_escape_cancels_load_cargo_mode`: Set mode LOAD_CARGO, press ESC → mode resets to SELECT
- [x] Verify: All tests pass

**Notes:** Follow the mock_scene fixture pattern from existing tests.

### Task 4.2: CargoQuickDialog tests [Complex]
**New file:** `tests/unit/ui/screens/test_cargo_quick_dialog.py`
**Tests:** `pytest tests/unit/ui/screens/test_cargo_quick_dialog.py -v`

- [x] Add `TestCargoQuickDialog` class following `TestTransferDialog` fixture pattern:
  - `mock_manager` fixture: `pygame_gui.UIManager((800, 600))`
  - `mock_scene` fixture with `scene._facade` mock
  - `mock_fleet` fixture with `fleet.id`, `fleet.fleet_id`, `fleet.location`
- [x] Add `test_init_populates_items_for_unload`: Create dialog with direction='unload', mock fleet with passengers → verify cargo items populated from fleet data
- [x] Add `test_init_populates_items_for_load`: Create dialog with direction='load', mock colony at hex with population → verify cargo items populated from colony data
- [x] Add `test_all_button_sets_slider_to_max`: Click "All" button → verify slider value set to maximum
- [x] Add `test_confirm_dispatches_transfer_commands`: Set up item selections → click confirm → verify `IssueTransferCommand` created with correct direction/amount and dispatched via facade
- [x] Add `test_confirm_with_max_amount_uses_zero`: When slider at max, confirm sends amount=0 (engine convention for "all")
- [x] Add `test_cancel_closes_dialog`: Click cancel → verify dialog killed
- [x] Add `test_empty_cargo_shows_no_items`: Create dialog with no cargo → verify empty state handled gracefully
- [x] Add `test_no_colony_for_unload_shows_no_items`: Unload at hex without colony → verify no items (bonus test)
- [x] Add `test_load_with_no_colony_shows_no_items`: Load at hex without colony → verify no items (bonus test)
- [x] Verify: All tests pass

**Notes:** Follow `test_transfer_dialog.py` pattern for mock setup and facade interaction testing.

### Task 4.3: Full test suite verification [Simple]
**Tests:** `pytest tests/ -n 12`

- [x] Run full test suite: `pytest tests/ -n 12`
- [x] Verify: All 7713 tests pass (baseline 7694 + 19 new tests)
- [x] Verify: No regressions in existing transfer, hotkey, or input handler tests

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] `pytest tests/ -n 12` full suite passes
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to "Complete - Ready for Audit"
