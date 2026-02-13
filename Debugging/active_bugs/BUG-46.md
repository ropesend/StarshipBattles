# BUG-46: Fleet Report ship top-down image too small

## Description
In the fleet report, the top down image of the ship should be enlarged so that the visible portion of the image is about the same height as the portrait.

## Reference Screenshot
C:\Developer\StarshipBattles\screenshots\screenshot_20260123_202105_670002_strategy_viewport.png

## Priority
Medium (Visual bug)

## Status
In-Progress

## Root Cause (5th attempt)

The previous fixes all had the same fundamental problem: `scale_image_by_visible_portion()` in `game/ui/utils.py` scaled the **full image canvas** (including all transparent padding) based on visible height, but then `pygame_gui.UIImage.set_image()` scaled the entire result (transparent padding included) back down to fit the 56x46 widget rect. This cancelled out the visible-portion scaling, leaving the ship tiny.

Additionally, `get_visible_bounding_box()` used slow pixel-by-pixel Python iteration (O(width*height) calls) to detect visible content.

## Fix

### 1. `game/ui/utils.py` — `get_visible_bounding_box()`
Replaced pixel-by-pixel Python loop with native `surface.get_bounding_rect(min_alpha=10)` (C-level, orders of magnitude faster). Also now correctly detects single-pixel visible content.

### 2. `game/ui/utils.py` — `scale_image_by_visible_portion()`
**Key change:** Now **crops to the visible area first**, then scales the cropped content to target_height. The returned surface contains only visible content (no transparent padding), so when `UIImage.set_image()` renders it, the ship fills the widget instead of being a tiny dot in a sea of transparency.

Before: Scale full canvas → UIImage shrinks back → tiny ship
After: Crop visible → Scale visible to target_height → UIImage displays at correct size

### Files Modified
1. `game/ui/utils.py`: Both functions rewritten
2. `tests/unit/ui/test_utils.py`: Updated tests for new behavior

### Tests
All 31 UI utils tests pass.

## Work Log
- 2026-01-23: Ticket created
- 2026-01-23: First fix (column width increase) - Rejected
- 2026-01-24: Second fix (visible-portion scaling) - Rejected
- 2026-01-24: Third fix (aspect ratio preservation) - Rejected
- 2026-02-10: Fourth fix (kept full canvas) - Rejected
- 2026-02-11: Fifth fix - Crop to visible area before scaling. Uses native C bounding rect. Returned surface contains only visible content.

---
### ❌ Fix Rejected [2026-02-11 20:55]
**Reason:** The fix is only partially fixed, it is the right height, but it should be scaled keeping its aspect ratio intact, it has been scaled to be too wide now.
**New Constraints:** Scale the top-down image keeping its original aspect ratio intact. Reference screenshot: `C:\Dev\Starship Battles\output\screenshots\screenshot_20260211_205501_018240_strategy_viewport.png`
---
