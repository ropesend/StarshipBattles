# BUG-69: Strategy View - Scroll Wheel Zoom Locks Up

## Description

The scroll wheel gets locked out of the strategy view occasionally, rolling the wheel has no impact on the zoom level.

## Priority
High

## Status
Awaiting Confirmation

## Work Log

### Root Cause
In `strategy_ui.py`, the `UI_WINDOW_CLOSE` event handler was incorrectly nested inside the `UI_BUTTON_PRESSED` event block (line 742). Because the event type can't be both `UI_BUTTON_PRESSED` and `UI_WINDOW_CLOSE`, the window close handlers never executed. This meant `fleet_orders_window` and `fleet_report_window` were never set back to `None` when closed.

Since `_has_modal_open()` checks these references, it returned `True` permanently after any fleet orders or fleet report window was opened and closed. The `update_input()` method blocks mousewheel events when `_has_modal_open()` is True, causing zoom to lock up.

Additionally, the `transfer_dialog` window close was not handled at all.

### Fix
1. Moved the `UI_WINDOW_CLOSE` handler out of the `UI_BUTTON_PRESSED` block to be a separate top-level event check
2. Added `transfer_dialog` cleanup to the `UI_WINDOW_CLOSE` handler

### Files Modified
- `game/ui/screens/strategy_ui.py` - Fixed event handler nesting and added transfer_dialog cleanup

### Test
All 1570 strategy tests pass. No regressions.
