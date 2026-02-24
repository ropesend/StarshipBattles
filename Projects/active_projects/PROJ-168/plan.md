# PROJ-168: Extract Hex-to-Cartesian Conversion Helper

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-168` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-168 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Add hex_axial_to_cartesian() | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Update callers | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Verification | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |

## Current State
**Last Updated:** 2026-02-23
**Active Phase:** Phase 2
**Last Action:** Phase 1 complete — hex_axial_to_cartesian() added with 7 unit tests
**Next Action:** Phase 2 — Update 5 call sites to use new function
**Blockers:** None

## Overview
Extract the duplicated hex-axial-to-Cartesian conversion pattern into a single utility function in `game/core/hex_math.py`. Five call sites across the density primitives and region classifier all implement the same 2-line formula: `x = dq + dr * 0.5; y = dr * sqrt(3)/2`. One site uses a hardcoded constant (`0.8660254037844386`) while the other four use `math.sqrt(3.0) / 2.0`.

**Origin:** Duplication & Consolidation Review (2026-02-23), finding STRAT-GEN CQ-002, verified as Tier 2 / Minor (5 confirmed duplications).

## Goals
- Eliminate 5 duplicated hex-to-Cartesian conversion implementations
- Unify the inconsistent constant representation (hardcoded vs computed)
- Add proper tests for the new utility function
- Zero behavioral change — pure refactor

## Scope
**In:**
- New `hex_axial_to_cartesian()` function in `game/core/hex_math.py`
- Unit tests for the new function
- Update 5 call sites to use the new function
- Update imports in affected files

**Out:**
- Changing the existing `hex_to_pixel()` function (different purpose — pixel scaling)
- Refactoring other patterns found in the review (separate projects)
- Gaussian falloff consolidation (STRAT-GEN CQ-005 — separate finding)
- Angle normalization consolidation (STRAT-GEN CQ-003 — separate finding)

## Key Files
| Component | File Path |
|-----------|-----------|
| New function home | `game/core/hex_math.py` (line ~133, after `hex_to_pixel`) |
| Caller 1 | `game/strategy/generation/density/primitives/spiral_arm.py:55-58` |
| Caller 2 | `game/strategy/generation/density/primitives/linear.py:53-55` |
| Caller 3 | `game/strategy/generation/density/primitives/geometric.py:56-58` |
| Caller 4 | `game/strategy/generation/density/primitives/noise.py:93-94` |
| Caller 5 | `game/strategy/generation/region_classifier.py:177-178` |
| Existing tests | `tests/unit/core/test_hex_math_core.py` |
| Density tests | `tests/unit/strategy/generation/density/test_density_map.py` |
| Region tests | `tests/unit/strategy/generation/test_region_classifier.py` |

## Baseline
- **Test suite:** 11994 passed, 1 skipped (2026-02-23)

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log

---

## Phases

### Phase 1: Add `hex_axial_to_cartesian()` to hex_math.py [Simple]
**Objective:** Create the shared utility function and add comprehensive tests
**Status:** Not Started

#### Task 1.1: Add `hex_axial_to_cartesian()` function [Simple]
**File:** `game/core/hex_math.py`
**Tests:** `pytest tests/unit/core/test_hex_math_core.py`
- [ ] Add new function after `hex_to_pixel()` (after line 133):
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
      This is a raw coordinate conversion without pixel scaling — for UI
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
- [ ] Add `hex_axial_to_cartesian` to module-level `__all__` if one exists, or verify it's importable
**Notes:**

#### Task 1.2: Add unit tests for new function [Simple]
**File:** `tests/unit/core/test_hex_math_core.py`
**Tests:** `pytest tests/unit/core/test_hex_math_core.py`
- [ ] Add import of `hex_axial_to_cartesian` to import block (line 10-21)
- [ ] Add new test class `TestHexAxialToCartesian` after `TestHexToPixel` (after line ~348):
  ```python
  class TestHexAxialToCartesian:
      """Tests for hex_axial_to_cartesian function."""

      def test_origin_returns_zero(self):
          """(0, 0) with default center returns (0.0, 0.0)."""
          x, y = hex_axial_to_cartesian(0, 0)
          assert x == 0.0
          assert y == 0.0

      def test_q_only_offset(self):
          """(1, 0) maps to (1.0, 0.0) — pure q movement."""
          x, y = hex_axial_to_cartesian(1, 0)
          assert x == 1.0
          assert y == 0.0

      def test_r_only_offset(self):
          """(0, 1) maps to (0.5, sqrt(3)/2)."""
          x, y = hex_axial_to_cartesian(0, 1)
          assert abs(x - 0.5) < 1e-10
          assert abs(y - math.sqrt(3.0) / 2.0) < 1e-10

      def test_with_center_offset(self):
          """center_q=5, center_r=3 produces correct delta."""
          x, y = hex_axial_to_cartesian(5, 3, center_q=5, center_r=3)
          assert x == 0.0
          assert y == 0.0

      def test_matches_hardcoded_constant(self):
          """Result matches the hardcoded 0.8660254037844386 constant."""
          _, y = hex_axial_to_cartesian(0, 1)
          assert abs(y - 0.8660254037844386) < 1e-15

      def test_negative_coords(self):
          """Negative coordinates produce correct signs."""
          x, y = hex_axial_to_cartesian(-2, -3)
          expected_x = -2 + (-3) * 0.5  # -3.5
          expected_y = -3 * math.sqrt(3.0) / 2.0
          assert abs(x - expected_x) < 1e-10
          assert abs(y - expected_y) < 1e-10

      def test_float_inputs(self):
          """Float q, r inputs work correctly."""
          x, y = hex_axial_to_cartesian(1.5, 2.5)
          expected_x = 1.5 + 2.5 * 0.5  # 2.75
          expected_y = 2.5 * math.sqrt(3.0) / 2.0
          assert abs(x - expected_x) < 1e-10
          assert abs(y - expected_y) < 1e-10
  ```
- [ ] Run tests: all new tests pass alongside existing tests
**Notes:**

---

### Phase 2: Update All 5 Call Sites [Simple]
**Objective:** Replace inline conversion code with function call at each site
**Status:** Not Started

#### Task 2.1: Update spiral_arm.py [Simple]
**File:** `game/strategy/generation/density/primitives/spiral_arm.py`
**Tests:** `pytest tests/unit/strategy/generation/density/test_density_map.py`
- [ ] Add import (line 7 area): `from game.core.hex_math import hex_axial_to_cartesian`
- [ ] Replace lines 51-58 (the 4 lines computing dq, dr, x, y):
  ```python
  # Before:
  dq = q - self.center_q
  dr = r - self.center_r
  # Convert hex axial to approximate Cartesian
  # x = q + r/2, y = r * sqrt(3)/2
  x = dq + dr * 0.5
  y = dr * math.sqrt(3.0) / 2.0

  # After:
  x, y = hex_axial_to_cartesian(q, r, self.center_q, self.center_r)
  ```
- [ ] Verify `math` import is still needed (yes — used for atan2, sqrt, log, cos, sin, radians, pi, exp elsewhere)
**Notes:**

#### Task 2.2: Update linear.py [Simple]
**File:** `game/strategy/generation/density/primitives/linear.py`
**Tests:** `pytest tests/unit/strategy/generation/density/test_density_map.py`
- [ ] Add import (line 7 area): `from game.core.hex_math import hex_axial_to_cartesian`
- [ ] Replace lines 49-55:
  ```python
  # Before:
  dq = q - self.center_q
  dr = r - self.center_r
  # Convert hex axial to approximate Cartesian
  x = dq + dr * 0.5
  y = dr * math.sqrt(3.0) / 2.0

  # After:
  x, y = hex_axial_to_cartesian(q, r, self.center_q, self.center_r)
  ```
- [ ] Verify `math` import is still needed (yes — used for cos, sin, exp elsewhere)
**Notes:**

#### Task 2.3: Update geometric.py [Simple]
**File:** `game/strategy/generation/density/primitives/geometric.py`
**Tests:** `pytest tests/unit/strategy/generation/density/test_density_map.py`
- [ ] Add import (line 8 area): `from game.core.hex_math import hex_axial_to_cartesian`
- [ ] Replace lines 52-58:
  ```python
  # Before:
  dq = q - self.center_q
  dr = r - self.center_r
  # Convert hex axial to approximate Cartesian
  x = dq + dr * 0.5
  y = dr * math.sqrt(3.0) / 2.0

  # After:
  x, y = hex_axial_to_cartesian(q, r, self.center_q, self.center_r)
  ```
- [ ] Verify `math` import is still needed (yes — used for sqrt, atan2, pi, exp, cos elsewhere)
**Notes:**

#### Task 2.4: Update noise.py [Simple]
**File:** `game/strategy/generation/density/primitives/noise.py`
**Tests:** `pytest tests/unit/strategy/generation/density/test_density_map.py`
- [ ] Add import (line 8 area): `from game.core.hex_math import hex_axial_to_cartesian`
- [ ] Replace lines 92-94. **Note:** noise.py has a slightly different pattern — it incorporates offset and scale inline:
  ```python
  # Before:
  x = (q + self.offset_q + (r + self.offset_r) * 0.5) / self.scale
  y = ((r + self.offset_r) * math.sqrt(3.0) / 2.0) / self.scale

  # After:
  x, y = hex_axial_to_cartesian(q, r, -self.offset_q, -self.offset_r)
  x /= self.scale
  y /= self.scale
  ```
  **Why `-self.offset_q`:** The original code adds the offset (`q + self.offset_q`), which is equivalent to subtracting a negative center. The function computes `dq = q - center_q`, so `center_q = -self.offset_q` gives `dq = q - (-offset_q) = q + offset_q`. Same for r.
- [ ] Verify the transformation is mathematically equivalent (critical — test must pass)
**Notes:**

#### Task 2.5: Update region_classifier.py [Simple]
**File:** `game/strategy/generation/region_classifier.py`
**Tests:** `pytest tests/unit/strategy/generation/test_region_classifier.py`
- [ ] Confirm `hex_axial_to_cartesian` is importable (file already imports `from game.core.hex_math import HexCoord` on line 12)
- [ ] Update import line 12 to: `from game.core.hex_math import HexCoord, hex_axial_to_cartesian`
- [ ] Replace lines 173-178:
  ```python
  # Before:
  dq = q - sp['center_q']
  dr = r - sp['center_r']
  # Convert hex axial to approximate Cartesian
  x = dq + dr * 0.5
  y = dr * 0.8660254037844386  # sqrt(3)/2

  # After:
  x, y = hex_axial_to_cartesian(q, r, sp['center_q'], sp['center_r'])
  ```
- [ ] This eliminates the hardcoded `0.8660254037844386` constant
**Notes:**

---

### Phase 3: Final Verification [Simple]
**Objective:** Confirm zero behavioral change across the full test suite
**Status:** Not Started

#### Task 3.1: Run full test suite [Simple]
**Tests:** `pytest tests/ -n 12`
- [ ] All 11994+ tests pass (same as baseline)
- [ ] No new warnings related to hex_math
- [ ] No skipped test changes

#### Task 3.2: Verify density map output consistency [Simple]
**Tests:** `pytest tests/unit/strategy/generation/density/ -v`
- [ ] All density tests pass with verbose output
- [ ] Re-run `pytest tests/unit/strategy/generation/test_region_classifier.py -v`
- [ ] All region classifier tests pass

---

## Verification Checklist

### Project Start (REQUIRED)
- [x] Run full test suite: `pytest tests/` — 11994 passed, 1 skipped (2026-02-23)

### After Each Phase
- [ ] Run `pytest tests/ --testmon` — all affected tests pass
- [ ] Verify density primitive behavior unchanged
- [ ] Verify region classification unchanged

### Final Verification
- [ ] Full test suite: `pytest tests/ -n 12` — all passing
- [ ] No behavioral change confirmed

---

## Audit Log
| Cycle | Date | Findings | Resolution |
|-------|------|----------|------------|
| 1 | | | |

## Completion Checklist
- [ ] All Phase 1 tasks checked off
- [ ] All Phase 2 tasks checked off
- [ ] All Phase 3 tasks checked off
- [ ] All tests passing (11994+)
- [ ] Audit passed
- [ ] User verified
