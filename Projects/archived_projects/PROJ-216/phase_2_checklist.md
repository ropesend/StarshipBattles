# Phase 2: Fix Click Gate

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-216 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Replace the overly broad `get_hovering_any_element()` check with a targeted check that only blocks clicks when actual modal windows or interactive overlays are under the cursor.

---

## Tasks

### Task 2.1: Replace `get_hovering_any_element()` with explicit window check [Medium]
**File:** `game/ui/screens/strategy_event_router.py`
**Tests:** `pytest tests/unit/ui/strategy/ --testmon`

- [x] Replace the current click gate logic (lines 269-272) with explicit modal/window checks
- [x] Add `_is_blocking_ui_element_at()` method to StrategyEventRouter
- [x] Verify the method correctly checks all windows that should block
- [x] Verify attribute names match actual window_manager attributes

**Implementation Notes:**
- Replaced `get_hovering_any_element()` with explicit window checks
- Checks all 8 window types from window_manager
- Also checks menu_panel, top_bar, resource_bar
- Uses `window.alive()` to skip dead windows

**Notes:** Check `strategy_window_manager.py` for the exact attribute names used for windows.

### Task 2.2: Add unit tests for the new click gate [Medium]
**File:** `tests/unit/ui/strategy/test_strategy_event_router.py` (new or existing)
**Tests:** `pytest tests/unit/ui/strategy/ -k "event_router" --testmon`

- [x] Test: click on map area with no windows open -> returns False (click passes through)
- [x] Test: click on sidebar area -> returns True (blocked)
- [x] Test: click on map area with fleet_orders_window open at that position -> returns True
- [x] Test: click on map area with confirmation dialog open at that position -> returns True
- [x] Test: click on top_bar area -> returns True (blocked)
- [x] Test: click on map area with hidden buttons (btn_colonize visible=0) -> returns False (NOT blocked)

**Implementation Notes:**
- Created `test_strategy_event_router.py` with 19 comprehensive tests
- Tests cover all window types, bars, menu panel, and edge cases (dead windows)

**Notes:** Use MagicMock for window_manager and ui elements.

### Task 2.3: Remove or finalize diagnostic logging from Phase 1 [Simple]
**File:** `game/ui/screens/strategy_event_router.py`, `game/ui/screens/strategy_input_handler.py`
**Tests:** `pytest tests/unit/ui/strategy/ --testmon`

- [x] Remove the diagnostic `logger.debug` calls added in Phase 1 Tasks 1.1/1.2
- [x] Or convert to permanent debug-level logging if desired (user decision at implementation time)

**Notes:** Removed the "BLOCKED by UI hover check" diagnostic from strategy_event_router.py (it was replaced by the new implementation). Kept the debug logging in strategy_input_handler.py as it's useful for ongoing debugging.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
