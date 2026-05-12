# BUG-31: Planet Selection in Zoomed Strategy Layer

## Description
In the strategy Layer, when you zoom in on a sector containing multiple planets, you should be able to select the planet on the screen by left clicking on it, they are separated out in their sector.

**Reference Image:** `C:\Developer\StarshipBattles\screenshots\screenshot_20260123_181634_287376_strategy_viewport.png`

## Priority
Medium

## Status
Awaiting Confirmation

## Work Log
### 2026-01-23 - Fix Implemented
**Root Cause:** When zoomed in (>= 1.5x), the renderer visually spreads planets within a hex (largest planet left, smaller planets arranged around it using polar coordinates). However, the picking logic only checked which hex was clicked using `pixel_to_hex()` - it didn't account for the visual positions of individual planets.

**Solution:** Added `_hit_test_planets()` method to `strategy_input_handler.py` that:
1. Computes the same expanded planet positions as the renderer (using identical layout algorithm)
2. Performs hit-testing against each planet's screen position and drawn radius
3. Returns the specific planet clicked, which is then prioritized in selection

**Files Modified:**
- `game/ui/screens/strategy_input_handler.py`:
  - Added `_hit_test_planets()` method (lines 276-367)
  - Modified `_handle_picking()` to call hit-test when zoomed >= 1.5x

**Testing:** All unit tests pass. Manual testing required to confirm planets can be clicked individually when zoomed in.
