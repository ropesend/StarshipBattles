# Phase 4: Integration Tests

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-216 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Add integration tests to prevent regression of the click-to-order pipeline.

---

## Tasks

### Task 4.1: Create click gate integration test [Medium]
**File:** `tests/unit/ui/screens/test_click_gate_integration.py` (new)
**Tests:** `pytest tests/unit/ui/screens/test_click_gate_integration.py`

- [x] Create test class `TestClickGateIntegration`
- [x] Test: `test_map_click_not_blocked_by_hidden_buttons` - Create StrategyUI with hidden buttons, verify `handle_click()` returns False for map area coordinates
- [x] Test: `test_map_click_blocked_by_confirmation_dialog` - Create dialog, verify clicks on dialog area are blocked
- [x] Test: `test_sidebar_click_always_blocked` - Verify clicks in sidebar area return True
- [x] Test: `test_top_bar_click_blocked` - Verify clicks in top bar area return True

**Notes:** 27 tests created covering all blocking UI elements (windows, dialogs, menu panel, top/resource bars).

### Task 4.2: Create move order end-to-end test [Medium]
**File:** `tests/integration/ui/test_move_order_registration.py` (new)
**Tests:** `pytest tests/integration/ui/test_move_order_registration.py`

- [x] Create test class `TestMoveOrderRegistration`
- [x] Test: `test_move_command_reaches_game_session` - Create FleetOperations with real facade and GameSession, call `execute_move()`, verify `fleet.orders` contains a MOVE order
- [x] Test: `test_click_dispatcher_routes_move_to_fleet_ops` - Create ClickModeDispatcher in MOVE mode, simulate click, verify fleet_ops.handle_move_designation() is called

**Notes:** 16 tests created covering move order registration, click dispatcher routing for all modes.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
