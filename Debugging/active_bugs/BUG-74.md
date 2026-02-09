# BUG-74: Normal new games should have homeworld complexes pre-built like quickstart

## Description
The normal new games should also have homeworld planets with the same complexes pre-built as the quickstart games.

## Priority
High

## Status (Awaiting Confirmation)

## Work Log
### 2026-02-08 - Fix Applied
**Root Cause:** The `_on_new_game_start()` method in `app.py` was missing the two calls that `_start_quickstart()` makes after saving: `copy_quickstart_designs()` and `spawn_initial_complexes()`. Normal new games created empty homeworlds while quickstart games got 7 pre-built facilities (shipyard, resource harvesters, resupply depot).

**Fix:** Added `QuickstartBuilder.copy_quickstart_designs()` and `QuickstartBuilder.spawn_initial_complexes()` calls to `_on_new_game_start()` after the initial save succeeds, matching the quickstart code path.

**Files Modified:**
- `game/app.py` - Added homeworld complex initialization to `_on_new_game_start()`
