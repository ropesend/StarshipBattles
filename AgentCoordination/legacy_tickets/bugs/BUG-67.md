# BUG-67: Strategy Layer - Add "Build Queues" Button to Top Bar

## Description

In the strategy layer there should be a button on the top named "Build Queues" that load the list of all build queues.

## Priority
Medium

## Status
Awaiting Confirmation

## Work Log

### Fix Applied (2026-02-07)

**Root Cause:** No top bar button existed for viewing all active build queues.

**Changes:**

1. **`game/ui/screens/strategy_ui.py`**:
   - Added `btn_build_queues` button between "Design" and "Save Game" in the top bar
   - Shifted Save Game and End Turn buttons one position right
   - Added click handler calling `open_build_queue_list()`
   - Added `build_queue_list_window` tracking variable and `UI_WINDOW_CLOSE` cleanup
   - Added to `_has_modal_open()` to block scroll-zoom when window is open
   - Added `open_build_queue_list()` and `_on_build_queue_list_closed()` methods

2. **`game/ui/screens/build_queue_list_window.py`** (new file):
   - `BuildQueueListWindow` - simple UIWindow listing all active build queues
   - Iterates empire colonies and fleets, showing location, design, turns remaining, and type
   - Shows "No active build queues." when queue is empty

**Result:** Clicking "Build Queues" in the top bar opens a summary window of all active build queues across planets and fleets.

**Tests:** All 1113 UI + strategy tests pass.
