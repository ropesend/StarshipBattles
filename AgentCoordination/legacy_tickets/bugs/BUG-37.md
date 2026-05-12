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

---
### ❌ Fix Rejected [2026-01-24 10:35]
**Reason:** Either designs are not being correctly identified as obsolete, or they are not getting set as obsolete, I can't really tell.
The load window in the Design Workshop needs to give the option to make a ship obsolete - this can be a button just to the left of the select button. - when pressed the design needs to be updated as obsolete and the file saved. The window should not close.
There needs to be a visible indicator on the line that indicates if the ship is obsolete, right now nothing indicates this.
**New Constraints:**
- Add "Mark Obsolete" button to the left of the Select button in the Load Design window
- When pressed, update the design as obsolete and save the file (window stays open)
- Add visible indicator on each row showing whether the ship is obsolete
---

- 2026-01-24: Implemented obsolete toggle functionality:
  - Added "[OBS]" visual indicator on left side of row when design is obsolete
  - Added "Obsolete"/"Restore" toggle button to the left of Select button
  - Button calls `design_library.mark_obsolete()` to update and save the design file
  - Window stays open and list refreshes after toggling obsolete status
  File modified: `game/ui/screens/design_selector_window.py:295-399`
