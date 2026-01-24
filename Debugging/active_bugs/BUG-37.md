# BUG-37: Load Design Screen obsolete filter not working correctly

## Description
In the Design Workshop, the Load Design Screen does not appear to let you make ships as obsolete, or filter the obsolete ships. When clicking "filter obsolete", the Select button keeps moving further to the left.

## Priority
Medium (Minor feature issue)

## Status
Awaiting Confirmation

## Work Log
- 2026-01-23: Ticket created from user report.
- 2026-01-23: Fixed Select button drift issue. Root cause: `_rebuild_design_list()` was calculating `row_width` from `list_container.get_container().get_rect().width - 20`, then setting `set_scrollable_area_dimensions(row_width, ...)`. Each refresh would read the previously-shrunk width and subtract 20 again, causing cumulative shrinkage. Fixed by using `main_panel.get_container().get_rect().width - 30` as a stable reference.
- 2026-01-23: Note: "Cannot mark ships obsolete" - the Load Design Screen is a read-only selector window. Marking obsolete would be a feature for the Design Workshop editor. Consider creating separate feature ticket if needed.
