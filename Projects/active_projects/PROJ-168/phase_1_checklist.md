# Phase 1: Add hex_axial_to_cartesian() to hex_math.py

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-168 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Create the shared utility function and add comprehensive tests

---

## Tasks

### Task 1.1: Add `hex_axial_to_cartesian()` function [Simple]
**File:** `game/core/hex_math.py`
**Tests:** `pytest tests/unit/core/test_hex_math_core.py`

- [x] Add new function after `hex_to_pixel()` (after line 133):
  ```python
  def hex_axial_to_cartesian(
      q: float,
      r: float,
      center_q: float = 0.0,
      center_r: float = 0.0
  ) -> Tuple[float, float]:
      """
      Convert axial hex coordinates to approximate Cartesian (x, y).

      Maps flat-topped hexagonal axial coordinates to a 2D Cartesian plane.
      This is a raw coordinate conversion without pixel scaling - for UI
      rendering, use hex_to_pixel() instead.

      Args:
          q: Axial q coordinate
          r: Axial r coordinate
          center_q: Center q to compute relative offset (default 0.0)
          center_r: Center r to compute relative offset (default 0.0)

      Returns:
          Tuple (x, y) in Cartesian coordinates
      """
      dq = q - center_q
      dr = r - center_r
      x = dq + dr * 0.5
      y = dr * (math.sqrt(3.0) / 2.0)
      return x, y
  ```
- [x] Verify function is importable (no `__all__` restriction in hex_math.py)

**Notes:** Function added after hex_to_pixel() at line 136

### Task 1.2: Add unit tests [Simple]
**File:** `tests/unit/core/test_hex_math_core.py`
**Tests:** `pytest tests/unit/core/test_hex_math_core.py`

- [x] Add `hex_axial_to_cartesian` to import block (line 10-21)
- [x] Add `TestHexAxialToCartesian` test class with 7 tests:
  - `test_origin_returns_zero` — (0,0) → (0.0, 0.0)
  - `test_q_only_offset` — (1,0) → (1.0, 0.0)
  - `test_r_only_offset` — (0,1) → (0.5, sqrt(3)/2)
  - `test_with_center_offset` — same q,r as center → (0.0, 0.0)
  - `test_matches_hardcoded_constant` — y matches 0.8660254037844386
  - `test_negative_coords` — correct signs
  - `test_float_inputs` — float q,r work
- [x] Run: `pytest tests/unit/core/test_hex_math_core.py` — all pass

**Notes:** All 7 tests pass (75 total in test file)

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] `pytest tests/unit/core/test_hex_math_core.py` passes
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 2
