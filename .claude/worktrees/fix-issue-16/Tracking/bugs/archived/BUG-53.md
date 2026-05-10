# BUG-53: Load Design Panel - Overwritten by Component Modifier Grid

## Description
Initially when the load design panel is started the Component Modifier Grid overwrites portions of it.

**Screenshot:** C:\Developer\StarshipBattles\screenshots\screenshot_20260124_072422_521541_mouse_focus.png

## Priority
Medium

## Status
Awaiting Confirmation

## Work Log
- 2026-01-24: Ticket created
- 2026-01-24: Fixed by skipping custom drawing when modal windows are open:
  - Added check in `draw()` method to detect if any UIWindow is visible
  - When windows are open, skip drawing `component_modifier_grid_panel` and `detail_panel`
  - This prevents custom-drawn elements from overlapping pygame_gui modal windows
  - File modified: `game/ui/screens/workshop_screen.py:510-521`
