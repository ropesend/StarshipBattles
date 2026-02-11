# BUG-46: Fleet Report ship top-down image too small

## Description
In the fleet report, the top down image of the ship should be enlarged so that the visible portion of the image is about the same height as the portrait.

## Reference Screenshot
C:\Developer\StarshipBattles\screenshots\screenshot_20260123_202105_670002_strategy_viewport.png

## Priority
Medium (Visual bug)

## Status
Awaiting Confirmation

## Work Log
- 2026-01-23: Ticket created
- 2026-01-23: Fixed. Enlarged top-down ship image in Fleet Report:
  - Increased 'topdown' column width from 44 to 60 pixels
  - Increased target size for topdown images from (40, row_height-4) to (56, row_height-4)
  - Files modified: `game/ui/screens/fleet_report_window.py`

---
### ❌ Fix Rejected [2026-01-24 10:45]
**Reason:** Top down images are still too small, the image has a large transparent background. I want it sized based on its visible component. The visible component should be about as tall as the portrait view picture.
**New Constraints:**
- Size the top-down image based on its visible (non-transparent) portion, not the full image dimensions
- The visible component height should match the portrait view height
---

- 2026-01-24: Fixed by implementing visible-portion-based sizing:
  - Added `_scale_by_visible_portion()` method that finds non-transparent area and scales based on it
  - Added `_get_visible_bounding_box()` helper to detect visible pixels
  - Top-down images now scale so visible height matches portrait height (row_height - 4)
  - Cropped result shows only the visible portion, no excess transparency
  File modified: `game/ui/screens/fleet_report_window.py:593-720`

---
### ❌ Fix Rejected [2026-01-24 07:35]
**Reason:** the top down view is the correct height, but it should keep the same aspect ratio as the original image. similar to the image used in the load design screen within the design workshop.
**New Constraints:** Maintain original aspect ratio when scaling the top-down image (reference: Load Design screen in Design Workshop).
---

- 2026-01-24: Fixed by preserving original aspect ratio:
  - Modified `_scale_by_visible_portion()` to return full scaled image instead of cropping
  - Scales based on visible height but keeps entire image (including transparent areas)
  - This maintains original aspect ratio like the Load Design screen
  - File modified: `game/ui/screens/fleet_report_window.py:650-686`

---
### ❌ Fix Rejected [2026-02-10 18:45]
**Reason:** The image is still too small. Need to determine the dimensions of the visible portion and scale based on that. The top-down view should be the same height as the portrait view.
**New Constraints:**
- Determine the dimensions of the visible (non-transparent) portion of the top-down image
- Scale based on those visible dimensions
- The top-down view visible height must match the portrait view height
- Reference screenshot: `output/screenshots/screenshot_20260210_184052_486643_strategy_viewport.png`
---
