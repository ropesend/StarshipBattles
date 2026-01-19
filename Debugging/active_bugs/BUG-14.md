# BUG-14: Multi-Planet Sectors Need Planet Position Offset

## Description
In the strategy layer, Planets that exist in a sector with multiple planets should be moved towards the right, by about 1/4 of the diameter of the largest planet.

## Status
Awaiting Confirmation

## Work Log

### 2026-01-18 - Phase 1: Reproduction (Red)

**Test File Created:** `tests/repro_issues/test_bug_14_multi_planet_offset.py`

**Test Cases:**
1. `test_multi_planet_group_offset_to_right` - Verifies planets in multi-planet sectors are offset RIGHT
2. `test_single_planet_no_offset` - Ensures single-planet sectors remain centered (passes)
3. `test_offset_magnitude_quarter_diameter` - Validates offset calculation of 1/4 diameter (passes)
4. `test_renderer_offset_direction` - Integration test for renderer behavior

**Failing Test Output:**
```
FAILED tests/repro_issues/test_bug_14_multi_planet_offset.py::TestMultiPlanetPositionOffset::test_multi_planet_group_offset_to_right
AssertionError: BUG CONFIRMED: Multi-planet group offset is to the LEFT (-60.0), should be to the RIGHT (positive value like 12.5)

FAILED tests/repro_issues/test_bug_14_multi_planet_offset.py::TestRendererMultiPlanetLogic::test_renderer_offset_direction
AssertionError: BUG REPRODUCED: Largest planet at x=440.0 is LEFT of center (500). Should be RIGHT of center at approximately x=512.5

========================= 2 failed, 2 passed in 1.76s =========================
```

**Root Cause Identified:**
In `game/ui/screens/strategy_renderer.py:360`, the largest planet offset is calculated as:
```python
final_offset = pygame.math.Vector2(-hex_px_radius * 0.6, 0)
```
This negative X offset moves planets to the LEFT. The bug description specifies they should move to the RIGHT by 1/4 of the largest planet's diameter.

### 2026-01-18 - Phase 2: The Fix (Green)

**File Modified:** `game/ui/screens/strategy_renderer.py`

**Changes Made (lines 348-369):**
```python
# BEFORE (buggy):
final_offset = pygame.math.Vector2(-hex_px_radius * 0.6, 0)

# AFTER (fixed):
base_r = hex_px_radius * 0.25
largest_diameter = base_r * 2
group_offset_x = largest_diameter * 0.25  # Offset right by 1/4 of largest diameter

# For largest planet:
final_offset = pygame.math.Vector2(group_offset_x, 0)

# For smaller planets (also shifted right):
final_offset = pygame.math.Vector2(dist + group_offset_x, 0).rotate(angle)
```

**Technical Approach:**
1. Calculate `group_offset_x` as 1/4 of the largest planet's diameter (per bug description)
2. Apply positive X offset to largest planet (moves RIGHT instead of LEFT)
3. Add `group_offset_x` to smaller planets' distance before rotation to keep group cohesive

**Test Results:**
```
========================= 4 passed in 1.64s =========================
```

**Regression Tests:**
```
====================== 234 passed, 82 warnings in 6.75s =======================
```

All strategy and UI tests pass with no regressions.

---
### ❌ Fix Rejected [2026-01-18 17:45]
**Reason:** Moved too much, probably should have moved it half as much, shif it a little to the left. it should be about as far left of center as it currently is right of center.
**New Constraints:** Offset should be approximately half the current value; final position should be left of center (mirroring current right-of-center position)
---
