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

---
### ❌ Fix Rejected [2026-03-14 09:00]
**Reason:** The sqrt(3) fix improved things but the scaling is not uniform across all star sizes. Radius-2 stars now look perfect, but radius-4 stars are still too small (edge ends at border of 3rd ring instead of halfway into 4th ring) and radius-1 stars are slightly too big (overfill the center hex). The formula needs a non-linear adjustment or per-radius tuning rather than a single linear multiplier.

**New Constraints:**
- Radius-2 is the reference — its current size is correct and should not change
- Radius-1 stars should be slightly smaller than they currently are (should not overflow the center hex)
- Radius-4 stars need to be larger — edge should reach halfway into the outermost hex ring
- The star edge for any radius-N star should extend to approximately the midpoint of the Nth hex ring

[![Radius-4 star still too small after fix](../../tools/qa_observer/session_data/20260314_085600/images/bug_capture_085952.png)](../../tools/qa_observer/session_data/20260314_085600/images/bug_capture_085952.png)
*Radius-4 star — edge should reach halfway into the 4th ring but only reaches the edge of the 3rd*

[![Radius-1 star slightly too big after fix](../../tools/qa_observer/session_data/20260314_085600/images/bug_capture_090023.png)](../../tools/qa_observer/session_data/20260314_085600/images/bug_capture_090023.png)
*Radius-1 star — slightly overfills the center hex, should be a bit smaller*

[![Radius-2 star looks perfect](../../tools/qa_observer/session_data/20260314_085600/images/bug_capture_090052.png)](../../tools/qa_observer/session_data/20260314_085600/images/bug_capture_090052.png)
*Radius-2 star — this is the correct size, use as reference*
---

### ✅ Fix v2 Applied [2026-03-14]
**Approach:** Replaced linear `radius_hexes * sqrt(3) * hex_size * zoom` with a non-linear power curve: `2 * hex_spacing * (radius_hexes / 2) ^ 1.2`.

- **Anchor:** Radius-2 produces identical result to the linear formula (34px at hex_size=10, zoom=1.0).
- **Radius-1:** Power curve reduces from 17px → ~15px (doesn't overflow center hex).
- **Radius-4:** Power curve increases from 69px → ~79px (reaches further into 4th ring).
- **Implementation:** Extracted `_hex_radius_to_screen()` helper method used by both star and Dyson sphere rendering.
- **Tests:** Updated `test_star_radius_accounts_for_hex_geometry` (radius-2 anchor), added `test_star_radius_nonlinear_scaling` (verifies r1 < linear, r2 = linear, r4 > linear).
- **Files modified:** `game/ui/screens/strategy_renderer.py`, `tests/unit/ui/screens/test_strategy_renderer.py`
- **Tests:** 66/66 strategy renderer tests pass.
