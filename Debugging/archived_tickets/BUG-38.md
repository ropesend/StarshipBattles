# BUG-38: Load Design Screen should show portrait and top-down views

## Description
In the Design Workshop, the Load Design Screen should show a portrait and top down view of the designs in the list.

## Priority
Low (QoL improvement / Feature request)

## Status
Awaiting Confirmation

## Work Log
- 2026-01-23: Ticket created from user report.
- 2026-01-23: Implemented portrait thumbnails in design rows. Added `_load_portrait_thumbnail()` method that loads portrait from `assets/ShipThemes/{theme}/Portraits/{class}_Portrait.jpg` and falls back to a gradient placeholder with class initial. Replaced emoji placeholder with `UIImage` widget displaying the portrait. Files modified: `game/ui/screens/design_selector_window.py`.

---
### ❌ Fix Rejected [2026-01-24 10:40]
**Reason:** There is a nice portrait view but not top down view - the topdown view should be from the Skins directory of the ship's theme directory. Note that the skins may have a large transparent area, they should be sized based on the visible portion of the image, and this should be the same height as the portrait view.
**New Constraints:**
- Add top-down view in addition to portrait view
- Top-down image source: `assets/ShipThemes/{theme}/Skins/` directory
- Size based on visible (non-transparent) portion of the image
- Top-down view height should match portrait view height
---

- 2026-01-24: Implemented top-down view:
  - Added `_load_topdown_thumbnail()` method that loads from `assets/ShipThemes/{theme}/Skins/{class}.png`
  - Added `_get_visible_bounding_box()` helper to find non-transparent area of PNG
  - Top-down image is scaled so visible portion height matches portrait height (50px)
  - Top-down view displays alongside portrait in each design row
  - Handles multiple class name variations (spaces, underscores, case)
  File modified: `game/ui/screens/design_selector_window.py`
