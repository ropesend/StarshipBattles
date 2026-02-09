# BUG-76: Turn log does not show at start of each strategy layer turn

## Description
The log is supposed to show at the start of each strategy layer turn. It does not.

## Priority
High

## Status (Awaiting Confirmation)

## Work Log
### 2026-02-08 - Fix Applied
**Root Cause:** Off-by-one timing bug. In `GameSession.process_turn()`, events are logged at `turn_number=N`, then `turn_number` is incremented to `N+1`. When `_process_full_turn()` in StrategyScreen calls `get_turn_events()` afterward (with no argument), the facade queries for turn `N+1` but events were stored at turn `N` — returning an empty list, so the log window never opens.

**Fix:** Captured the turn number *before* calling `process_turn()` and passed it explicitly to `get_turn_events(turn=processed_turn)`.

**Files Modified:**
- `game/ui/screens/strategy_screen.py` - Capture turn number before processing, pass explicitly to event query
