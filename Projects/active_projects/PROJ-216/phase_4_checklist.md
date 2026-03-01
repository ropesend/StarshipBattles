# Phase 4: Integration Tests

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-216 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Add integration tests to prevent regression of the click-to-order pipeline.

---

## Tasks

### Task 4.1: Create click gate integration test [Medium]
**File:** `tests/unit/ui/strategy/test_click_gate_integration.py` (new)
**Tests:** `pytest tests/unit/ui/strategy/test_click_gate_integration.py`

- [ ] Create test class `TestClickGateIntegration`
- [ ] Test: `test_map_click_not_blocked_by_hidden_buttons` - Create StrategyUI with hidden buttons, verify `handle_click()` returns False for map area coordinates
- [ ] Test: `test_map_click_blocked_by_confirmation_dialog` - Create dialog, verify clicks on dialog area are blocked
- [ ] Test: `test_sidebar_click_always_blocked` - Verify clicks in sidebar area return True
- [ ] Test: `test_top_bar_click_blocked` - Verify clicks in top bar area return True

**Notes:** Uses real pygame_gui UIManager with actual element creation where practical, MagicMock for complex dependencies.

### Task 4.2: Create move order end-to-end test [Medium]
**File:** `tests/integration/ui/test_move_order_registration.py` (new)
**Tests:** `pytest tests/integration/ui/test_move_order_registration.py`

- [ ] Create test class `TestMoveOrderRegistration`
- [ ] Test: `test_move_command_reaches_game_session` - Create FleetOperations with real facade and GameSession, call `execute_move()`, verify `fleet.orders` contains a MOVE order
- [ ] Test: `test_click_dispatcher_routes_move_to_fleet_ops` - Create ClickModeDispatcher in MOVE mode, simulate click, verify fleet_ops.handle_move_designation() is called

**Notes:** These tests bypass the UI click gate (already tested in 4.1) and test the command dispatch chain.

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
