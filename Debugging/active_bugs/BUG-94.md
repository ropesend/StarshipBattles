# BUG-94: Star visual radius too small relative to hex grid

## Description

Stars on the strategy map are rendered significantly smaller than their defined hex radius. A radius-2 star should have its edge extend roughly halfway into the 2nd ring of hexes, but currently it barely extends past the center hex. Similarly, a radius-3 star's edge only reaches about halfway into the 2nd ring when it should reach halfway into the 3rd ring.

The root cause is the screen radius formula in `strategy_renderer.py`:
```python
screen_star_r = max(3, int(star.radius_hexes * self.hex_size * self.camera.zoom))
```
This uses `hex_size = 10`, but the actual screen distance per hex ring is much larger than 10 pixels. The formula needs to account for the true hex grid geometry (hex height/width at the current zoom level) rather than using the raw `hex_size` constant as a simple multiplier.

### Screenshots

[![Radius-2 star (white) barely extends past center hex](../../tools/qa_observer/session_data/20260314_074413/images/bug_capture_074508.png)](../../tools/qa_observer/session_data/20260314_074413/images/bug_capture_074508.png)
*Radius-2 star — edge should reach ~halfway into the 2nd hex ring*

[![Radius-3 star (red) only fills ~2 hex rings instead of 3](../../tools/qa_observer/session_data/20260314_074413/images/bug_capture_074622.png)](../../tools/qa_observer/session_data/20260314_074413/images/bug_capture_074622.png)
*Radius-3 star — edge should reach ~halfway into the 3rd hex ring*

## Priority
Medium

## Status
Pending

## Work Log
- 2026-03-14: Created from QA Session 20260314_074413.
