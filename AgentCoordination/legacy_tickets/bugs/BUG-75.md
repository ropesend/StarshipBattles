# BUG-75: Planet details panel dimensions mismatch in planets list vs strategy layer

## Description
The Planet details panel on the right side of the planets list should be the same dimensions as the one in the main strategy layer.

## Priority
Medium

## Status (Awaiting Confirmation)

## Work Log
### 2026-02-08 - Fix Applied
**Root Cause:** The planet details panel in the planets list window used `detail_panel_width = 600` while the strategy layer used 580px width. This caused a 20px width mismatch between the two views.

**Fix:** Changed `detail_panel_width` from 600 to 580 in `planet_list_window.py` to match the strategy layer's panel width.

**Files Modified:**
- `game/ui/screens/planet_list_window.py` - Changed detail panel width from 600 to 580
