# BUG-54: Planet Selection Hitbox Mismatch After Angle Increase

## Description
Recently the angle between the planets was increased in multiplanet sectors, now selecting individual smaller planets seems to be based on where they used to be placed rather than where they are placed now.

## Priority
High

## Status
Awaiting Confirmation

## Work Log
- 2026-01-24: Ticket created
- 2026-01-24: Fixed by synchronizing angle values between renderer and input handler:
  - `strategy_renderer.py` had updated Rev 5 angle values for planet positioning
  - `strategy_input_handler.py` was still using old Rev 4 angle values for selection hitboxes
  - Updated input handler to match renderer:
    - 2 planets: [30, -30] → [40, -40]
    - 3 planets: [15, 0, -45] → [46, 0, -46]
    - Added specific cases for 4 planets: [58, 23, -23, -58]
    - Added specific cases for 5 planets: [63, 31, 0, -31, -63]
    - Updated 6+ planets formula: [70 - i * (150 / max(1, smaller_count - 1))]
  - File modified: `game/ui/screens/strategy_input_handler.py:324-337`
