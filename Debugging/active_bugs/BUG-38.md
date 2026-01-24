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
