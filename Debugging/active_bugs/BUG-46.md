# BUG-46: Fleet Report ship top-down image too small

## Description
In the fleet report, the top down image of the ship should be enlarged so that the visible portion of the image is about the same height as the portrait.

## Reference Screenshot
C:\Developer\StarshipBattles\screenshots\screenshot_20260123_202105_670002_strategy_viewport.png

## Priority
Medium (Visual bug)

## Status
Awaiting Confirmation

## Root Cause (6th attempt)

The 5th fix correctly cropped to visible content and scaled to target_height, but it did not constrain the width. The `virtual_table.py` creates a **square** UIImage widget (`img_size x img_size`), and when the scaled surface was wider than this widget, `UIImage.set_image()` stretched the image to fill the square, distorting the aspect ratio.

The fundamental problem: `scale_image_by_visible_portion()` only constrained height, but the rendering widget constrains both dimensions. When a ship's visible content is wider than tall, height-only scaling produces an image wider than the widget, which then gets squished.

## Fix (6th attempt)

### 1. `game/ui/utils/pygame_utils.py` — `scale_image_by_visible_portion()`
Added optional `max_width` parameter. When provided:
- Scales visible content to fit within **both** `max_width` and `target_height` (using the smaller scale factor)
- Centers the result on a transparent canvas of exactly `(max_width, target_height)`
- This ensures the UIImage widget receives an exactly-sized surface with no distortion

Without `max_width`, behavior is unchanged (backward compatible).

### 2. `game/ui/screens/fleet_data_source.py` — `_get_ship_image()`
Now passes `max_width=56` (column width 60 minus padding) when calling for topdown images.

### Files Modified
1. `game/ui/utils/pygame_utils.py`: Added `max_width` parameter to `scale_image_by_visible_portion`
2. `game/ui/screens/fleet_data_source.py`: Updated topdown image call to pass `max_width=56`
3. `tests/unit/ui/test_utils.py`: Added 4 new tests for max_width behavior

### Tests
- 6 scale_image_by_visible_portion tests pass (2 existing + 4 new)
- Full suite: 12,976 passed (4 pre-existing failures in unrelated colony flag tests)

## Work Log
- 2026-01-23: Ticket created
- 2026-01-23: First fix (column width increase) - Rejected
- 2026-01-24: Second fix (visible-portion scaling) - Rejected
- 2026-01-24: Third fix (aspect ratio preservation) - Rejected
- 2026-02-10: Fourth fix (kept full canvas) - Rejected
- 2026-02-11: Fifth fix - Crop to visible area before scaling - Rejected (right height, but too wide)
- 2026-02-28: Sixth fix - Added `max_width` constraint to `scale_image_by_visible_portion`. Scales to fit within both width and height bounds while preserving aspect ratio. Centers result on transparent canvas matching widget dimensions.
