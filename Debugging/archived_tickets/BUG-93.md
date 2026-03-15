## Description

**Category:** Bug
**Title:** Fleet move targeting state cannot be completed or canceled
**Description:** When a fleet is selected and the move command ('M' hotkey) is initiated, clicking on a destination hex fails to create the move order. Furthermore, the player cannot cancel out of this targeting state (e.g., by pressing 'Escape'), leaving them trapped in the targeting mode until they end the turn or attempt other indirect overrides.
**Screenshot:**
[![Screenshot](c:\Developer\StarshipBattles\tools\qa_observer\session_data\20260228_125515\images\bug_capture_125916.png)](c:\Developer\StarshipBattles\tools\qa_observer\session_data\20260228_125515\images\bug_capture_125916.png)
*Screenshot demonstrates the game state while trapped in the fleet movement targeting mode without the ability to complete or intuitively cancel the order.*

## Priority
Critical

## Status (Awaiting Confirmation)

## Work Log

### 2026-02-28 — Fix Applied

**Root Cause:** In `game/ui/screens/strategy_click_dispatcher.py`, the `_handle_move_mode_click()` method only handled `'choice'` and `'success'` result types from `handle_move_designation()`. When the result was `'error'` (e.g., unreachable destination, fleet is building) or `None` (no fleet selected), the handler returned `True` (event consumed) but never reset `input_mode` from `'MOVE'` back to `'SELECT'`. This trapped the player in MOVE targeting mode.

Subsequent clicks would repeat the same error, and while Escape (via `FLEET_CANCEL_MODE`) and right-click cancel _should_ work as escape hatches, the fundamental issue was that every failed move click left the player stuck.

**Fix:** Added an `else` branch in `_handle_move_mode_click()` that resets `input_mode` to `'SELECT'` when the result is neither `'choice'` nor `'success'`. This covers both error results and None results.

**Files Modified:**
- `game/ui/screens/strategy_click_dispatcher.py` — Added error/None handling in `_handle_move_mode_click()`
- `tests/unit/ui/screens/test_strategy_input_handler_core.py` — Added 3 new tests:
  - `test_move_mode_error_returns_to_select` — Verifies unreachable error exits MOVE mode
  - `test_move_mode_error_building_returns_to_select` — Verifies building error exits MOVE mode
  - `test_move_mode_success_returns_to_select` — Verifies successful move exits MOVE mode

**Regression:** 1582 UI screen tests passed (0 failures).
