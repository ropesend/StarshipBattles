# BUG-39: Load Design Screen incorrectly calculates mass

## Description
In the Design Workshop, the Load Design Screen does not correctly calculate the mass of the design.

Image: `C:\Developer\StarshipBattles\screenshots\screenshot_20260123_193125_595845_mouse_focus.png`

Screenshot shows designs with "Mass: 0" which appears incorrect.

## Priority
Medium (Minor feature issue)

## Status
Awaiting Confirmation

## Work Log
- 2026-01-23: Ticket created from user report.
- 2026-01-23: Root cause identified - `DesignMetadata.from_design_file()` was looking for `mass` at the top level of the JSON, but ship designs store mass inside `expected_stats.mass`. Fixed by checking `expected_stats.mass` first, then falling back to top-level `mass`. File modified: `game/strategy/data/design_metadata.py`.
