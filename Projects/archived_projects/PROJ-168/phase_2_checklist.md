# Phase 2: Update All 5 Call Sites

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-168 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Replace inline conversion code with function call at each of 5 sites

---

## Tasks

### Task 2.1: Update spiral_arm.py [Simple]
**File:** `game/strategy/generation/density/primitives/spiral_arm.py`
**Tests:** `pytest tests/unit/strategy/generation/density/test_density_map.py`

- [x] Add import: `from game.core.hex_math import hex_axial_to_cartesian` (line 7 area)
- [x] Replace lines 51-58 (dq/dr/x/y computation) with:
  ```python
  x, y = hex_axial_to_cartesian(q, r, self.center_q, self.center_r)
  ```
- [x] Verify `math` import still needed (yes — atan2, sqrt, log, etc.)
- [x] Run tests: `pytest tests/unit/strategy/generation/density/test_density_map.py`

**Notes:** Replaced 8 lines with 2 lines

### Task 2.2: Update linear.py [Simple]
**File:** `game/strategy/generation/density/primitives/linear.py`
**Tests:** `pytest tests/unit/strategy/generation/density/test_density_map.py`

- [x] Add import: `from game.core.hex_math import hex_axial_to_cartesian` (line 7 area)
- [x] Replace lines 49-55 (dq/dr/x/y computation) with:
  ```python
  x, y = hex_axial_to_cartesian(q, r, self.center_q, self.center_r)
  ```
- [x] Run tests

**Notes:** Replaced 7 lines with 2 lines

### Task 2.3: Update geometric.py [Simple]
**File:** `game/strategy/generation/density/primitives/geometric.py`
**Tests:** `pytest tests/unit/strategy/generation/density/test_density_map.py`

- [x] Add import: `from game.core.hex_math import hex_axial_to_cartesian` (line 8 area)
- [x] Replace lines 52-58 (dq/dr/x/y computation) with:
  ```python
  x, y = hex_axial_to_cartesian(q, r, self.center_q, self.center_r)
  ```
- [x] Run tests

**Notes:** Replaced 7 lines with 2 lines

### Task 2.4: Update noise.py (special case) [Simple]
**File:** `game/strategy/generation/density/primitives/noise.py`
**Tests:** `pytest tests/unit/strategy/generation/density/test_density_map.py`

- [x] Add import: `from game.core.hex_math import hex_axial_to_cartesian` (line 8 area)
- [x] Replace lines 92-94 with:
  ```python
  x, y = hex_axial_to_cartesian(q, r, -self.offset_q, -self.offset_r)
  x /= self.scale
  y /= self.scale
  ```
- [x] Verify mathematical equivalence:
  - Original: `x = (q + offset_q + (r + offset_r) * 0.5) / scale`
  - New: `x = ((q - (-offset_q)) + (r - (-offset_r)) * 0.5) / scale = (q + offset_q + (r + offset_r) * 0.5) / scale` ✓
- [x] Run tests

**Notes:** Used negative center values to match original offset semantics

### Task 2.5: Update region_classifier.py [Simple]
**File:** `game/strategy/generation/region_classifier.py`
**Tests:** `pytest tests/unit/strategy/generation/test_region_classifier.py`

- [x] Update import line 12: add `hex_axial_to_cartesian` to existing import
  ```python
  from game.core.hex_math import HexCoord, hex_axial_to_cartesian
  ```
- [x] Replace lines 173-178 (dq/dr/x/y with hardcoded constant) with:
  ```python
  x, y = hex_axial_to_cartesian(q, r, sp['center_q'], sp['center_r'])
  ```
- [x] Run tests: `pytest tests/unit/strategy/generation/test_region_classifier.py`

**Notes:** Eliminated hardcoded 0.8660254037844386 constant

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] `pytest tests/unit/strategy/generation/ -v` — 223 passed
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 3
