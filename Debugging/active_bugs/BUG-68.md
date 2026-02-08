# BUG-68: Fleet Report - Ship Selection and Ship Report Panel

## Description

In the Fleet Report I need to be able to select a ship, the Ship report should show on the right side. Once selected I need to be able to remove a ship from the fleet.

## Priority
Medium

## Status
Awaiting Confirmation

## Work Log

### Fix Applied (2026-02-07)

**Root Cause:** The Fleet Report already had ship selection (click a row) and a ShipDetailPanel on the right showing full ship stats. The missing piece was a "Remove from Fleet" button.

**Changes:**

1. **`game/ui/panels/ship_detail_panel.py`**:
   - Added `on_remove_ship` callback parameter to constructor
   - Added `btn_remove` attribute tracking the remove button
   - Added "Remove from Fleet" button at the bottom of the ship display (only shown when callback is provided)
   - Updated `process_event()` to handle remove button clicks, calling the callback with the current ship

2. **`game/ui/screens/fleet_report_window.py`**:
   - Passed `on_remove_ship=self._on_remove_ship` to ShipDetailPanel constructor
   - Added `_on_remove_ship(ship)` method that:
     - Calls `fleet.remove_ship(ship)` to remove the ship
     - Clears selection
     - Recreates the view model with updated ship list
     - Refreshes the ship list and sidebar stats

**Existing features confirmed working:**
- Ship selection by clicking rows in the center list
- Ship detail panel on the right with: images, status, HP, resources, component damage (collapsible layers), combat record
- `Fleet.remove_ship()` method already existed with speed recalculation

**Tests:** All 6519 tests pass.
