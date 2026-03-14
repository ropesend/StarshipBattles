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
Awaiting Confirmation

## Work Log
- 2026-03-14: Created from QA Session 20260314_074413.
- 2026-03-14: **Fixed.** Root cause confirmed: star and Dyson sphere rendering formulas were missing `sqrt(3)` multiplier for hex geometry. For flat-topped hexes, adjacent hex centers are `sqrt(3) * hex_size` apart, not `hex_size`. The formula `radius_hexes * hex_size * zoom` was ~1.73x too small.
  - **Phase 0:** Checked PROJ-217 (Standardize Star Measurement to Radius) — that project renamed `diameter_hexes` → `radius_hexes` but didn't fix the pixel conversion factor. Fix preserves PROJ-217 naming.
  - **Phase 1:** Added `test_star_radius_accounts_for_hex_geometry` — confirmed radius was 20 instead of expected 34 for a radius-2 star.
  - **Phase 2:** Added `math.sqrt(3)` multiplier to both star (line 528) and Dyson sphere (line 706) formulas.
  - **Files modified:** `game/ui/screens/strategy_renderer.py`, `tests/unit/ui/screens/test_strategy_renderer.py`
  - **Tests:** 13168 passed, 2 skipped, 0 failures (full suite).
