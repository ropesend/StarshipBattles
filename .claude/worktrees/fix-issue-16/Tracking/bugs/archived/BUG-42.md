# BUG-42: Design Workshop remnants visible after exit

## Description
When I exit the Design Workshop, and the main strategy layer view is visible, there are portions of the Design Workshop that are still visible.

## Screenshot
![Strategy viewport with Design Workshop remnants](C:\Developer\StarshipBattles\screenshots\screenshot_20260123_195537_541041_strategy_viewport.png)

The screenshot shows a black vertical stripe on the right side of the strategy viewport, which appears to be a remnant UI element from the Design Workshop that was not properly cleared on exit.

## Priority
High

## Status
Awaiting Confirmation

## Work Log
- 2026-01-23: Ticket created
- 2026-01-23: Fixed. Added cleanup method to clear pygame_gui elements on exit:
  - Added `cleanup()` method to `DesignWorkshopGUI` that calls `ui_manager.clear_and_reset()`
  - Updated `on_builder_return()` in `app.py` to call `builder_scene.cleanup()` before state transition
  - Files modified: `game/ui/screens/workshop_screen.py`, `game/app.py`
  - Tests pass: workshop tests (37 items)

---
### ❌ Fix Rejected [2026-01-24 10:50]
**Reason:** There are still Design Workshop Remnants - A simple solution is Blank the screen and re-draw the whole UI when you go back to the strategy layer, this is also a problem with the fleet report, it leaves a lot of remnants behind as well
**New Constraints:**
- Blank the screen and re-draw the whole UI when returning to strategy layer
- This issue also affects the Fleet Report (leaves remnants behind) - same fix needed
---

- 2026-01-24: Fixed by adding full screen fill at start of `StrategyScene.draw()`:
  - Added `screen.fill((10, 10, 20))` as first line of draw method
  - This clears the entire screen before drawing, preventing remnants from any previous screen
  - Fixes both Design Workshop and Fleet Report remnant issues
  File modified: `game/ui/screens/strategy_scene.py:144-147`
