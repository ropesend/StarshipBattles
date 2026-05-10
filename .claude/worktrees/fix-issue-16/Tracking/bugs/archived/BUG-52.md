# BUG-52: Design Workshop - Rightmost Panel Should Extend Full Height

## Description
In the Design Workshop The right most panel should extend from the top of the screen to the bottom, there is an unused portion in the bottom right. The Requirements and Recommendations can be moved down and made larger.

## Priority
Low

## Status
Awaiting Confirmation

## Work Log
- 2026-01-24: Ticket created
- 2026-01-24: Fixed by extending right panel to full height:
  - Changed right_panel height from `self.height - self.bottom_bar_height - self.weapons_report_height`
    to `self.height - self.bottom_bar_height`
  - The right panel now extends from top to bottom (minus only the bottom bar)
  - This gives more space for the Requirements and Recommendations sections
  - File modified: `game/ui/screens/workshop_screen.py:178-184`
