# BUG-33: Planet Graphics Don't Move With Column Reorder

## Description
In the Planet List window, When you try to move the column containing the graphic of the planet, the header moves to the right, but the actual planet graphic stays in the left hand column. The graphics need to move with the columns.

**Reference Image:** `C:\Developer\StarshipBattles\screenshots\screenshot_20260123_181857_479325_planet_list.png`
(Shows planets overlapping the Name column - the planets should be in the second column)

## Priority
Medium

## Status
Awaiting Confirmation

## Work Log
### 2026-01-23 - Fix Implemented
**Root Cause:** In `_rebuild_row_pool()`, the icon column widget was created with hardcoded position `(5, 5)` instead of using the calculated `x_off` offset like text columns. When columns are reordered, `_rebuild_row_pool()` recreates widgets in the new order, but the icon always appeared at position (5, 5) regardless of its column position.

**Solution:** Changed the icon widget creation to use `x_off + 5` for the x-coordinate instead of hardcoded `5`, matching how text columns are positioned.

**Files Modified:**
- `game/ui/screens/planet_list_window.py` (line 568):
  - Changed `pygame.Rect(5, 5, 40, 40)` to `pygame.Rect(x_off + 5, 5, 40, 40)`

**Testing:** All planet-related unit tests pass. Manual testing required to confirm planet graphics move correctly with column reordering.
