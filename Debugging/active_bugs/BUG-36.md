# BUG-36: Load Design Screen shows formatting tags

## Description
In the Design Workshop, the Load Screen Design shows some of the formatting tags. Filters, and the design names both have formatting tags instead of the formatting.

Image: `C:\Developer\StarshipBattles\screenshots\screenshot_20260123_192225_324282_mouse_focus.png`

Screenshot shows `<b>Filters</b>` instead of bold "Filters", and design names like `<b>QS Complex</b>` and `<b>QS Escort</b>` displaying raw HTML tags.

## Priority
Medium (Visual bug)

## Status
Awaiting Confirmation

## Work Log
- 2026-01-23: Ticket created from user report.
- 2026-01-23: Root cause identified - UILabel was using `text=` parameter with HTML tags instead of `html_text=` parameter. Fixed by changing `text="<b>Filters</b>"` to `html_text="<b>Filters</b>"` on line 85, and similarly for design names on line 328 in `game/ui/screens/design_selector_window.py`.
