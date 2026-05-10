# BUG-41: Ship Structure section needs wider layout

## Description
In the design workshop, the Ship Structure section could be 25% wider, so that the cost doesn't overlap with the other information

## Priority
Medium

## Status
Awaiting Confirmation

## Work Log
- 2026-01-23: Ticket created
- 2026-01-23: Fixed. Made Ship Structure panel 25% wider:
  - Updated `PanelWidths.layer_panel` from 400 to 500
  - Updated `calculate_dynamic_layer_width()` to use 0.375 ratio (was 0.3) with bounds 375-625px (was 300-500px)
  - Files modified: `game/ui/screens/builder_utils.py`
  - Tests pass: builder tests (106 items)
