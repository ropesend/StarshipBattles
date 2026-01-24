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
