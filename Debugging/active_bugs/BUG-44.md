# BUG-44: Fleet Report columns need reorder arrows

## Description
In the Fleet Report, the columns should be able to be re-ordered with arrows on either side like the planet list.

## Priority
Medium (Minor feature issue)

## Status
Awaiting Confirmation

## Work Log
- 2026-01-23: Ticket created
- 2026-01-23: Fixed. Added column reorder arrows to Fleet Report:
  - Modified `_rebuild_headers()` to create left/right arrow buttons on each column header
  - Added `_swap_columns()` method to swap column positions
  - Updated `update()` method to handle arrow button clicks
  - Pattern matches planet list window implementation
  - Files modified: `game/ui/screens/fleet_report_window.py`
