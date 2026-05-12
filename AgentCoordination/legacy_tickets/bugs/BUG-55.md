# BUG-55: Build Queue - No Selection Indication

## Description
In the build queue when selecting designs in the queue, there is no indication which design is selected, or even if there is a design selected, clicking on a design in the queue should select it. Clicking and holding should allow drag and drop as it currently does. If a design is selected and I press the remove selected button it should remove that design from the queue.

## Priority
Medium

## Status
Awaiting Confirmation

## Work Log
- 2026-01-24: Ticket created
- 2026-01-24: Fixed by implementing queue item selection:
  - Added `selected_queue_index` state variable to track selection
  - Added drag threshold (10px) to distinguish click-to-select from drag-to-reorder
  - Click on queue item now selects it (blue highlight border drawn)
  - Hold + drag still allows reordering as before
  - Implemented handler for "Remove Selected" button to remove selected item
  - Visual selection highlight drawn in `draw()` method (3px blue border)
  - File modified: `game/ui/screens/build_queue_screen.py`
