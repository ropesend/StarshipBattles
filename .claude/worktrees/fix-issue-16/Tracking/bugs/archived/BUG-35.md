# BUG-35: Strategy view smaller planets too compacted in multi-planet sectors

## Description
In the strategy view, with multiple planets in a sector, we can slightly increase the angle between the smaller planets to spread them out a little. They are too compacted and there is extra space.

**Reference Image (7-planet sector):**
`docs/screenshots/screenshot_20260123_190119_468158_strategy_viewport.png`

## Priority
Low

## Status
Awaiting Confirmation

## Work Log
- 2026-01-23: Ticket created.
- 2026-01-23: Fixed. Modified `_draw_system_details()` in `game/ui/screens/strategy_renderer.py` to increase angular spread between smaller planets:
  - 2 planets: 35° apart (was 30°)
  - 3 planets: 40° spread (was asymmetric 15°/0°/-45°)
  - 4 planets: new explicit angles [50°, 20°, -20°, -50°]
  - 5 planets: new explicit angles [55°, 27°, 0°, -27°, -55°]
  - 6+ planets: spread from 60° to -70° (130° arc, was 105°)

  This provides better spacing and uses more of the available hex area.

---
### ❌ Fix Rejected [2026-01-24 10:30]
**Reason:** Planets are still too tight together, try to increase the angle between the smaller planets by about 15%
**New Constraints:** Increase angular spread by approximately 15% from current values
---

- 2026-01-24: Rev 5 fix applied. Increased all angular spreads by 15%:
  - 2 planets: 40° (was 35°)
  - 3 planets: 46° (was 40°)
  - 4 planets: [58°, 23°, -23°, -58°] (was [50°, 20°, -20°, -50°])
  - 5 planets: [63°, 31°, 0°, -31°, -63°] (was [55°, 27°, 0°, -27°, -55°])
  - 6+ planets: 150° arc from 70° to -80° (was 130° arc from 60° to -70°)
  File modified: `game/ui/screens/strategy_renderer.py:356-371`
