# BUG-50: Load Design Window - Right Edge Clipped

## Description
The load window in the Design Workshop The right edge of the box containing each design is clipped or overdrawn by something, there should be a vertical line to the right of the select button that closes the box on the right side.

**Screenshot:** C:\Developer\StarshipBattles\screenshots\screenshot_20260124_072523_402042_mouse_focus.png

## Priority
Medium

## Status
Awaiting Confirmation

## Work Log
- 2026-01-24: Ticket created
- 2026-01-24: Fixed by adjusting row width calculation:
  - Changed row_width calculation to use list_container width instead of main_panel width
  - Subtracted 25px to account for scrollbar width (20px) plus margins
  - This prevents the right border of design rows from being clipped by the scrollbar
  - File modified: `game/ui/screens/design_selector_window.py:283-286`
