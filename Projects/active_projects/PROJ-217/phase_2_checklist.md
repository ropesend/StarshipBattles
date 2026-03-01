# Phase 2: Generation & Game Logic

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-217 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Update star generation, companion placement, orbit calculation, warp distance, superweapon code, entity registry, and spatial index to use `radius_hexes`.

---

## Tasks

### Task 2.1: Rewrite star size generation function [Medium]
**File:** `game/strategy/data/stars.py`
**Tests:** `pytest tests/unit/strategy/data/test_stars.py -k "test_star_generator"`

- [ ] Rename `_map_radius_to_hexes()` → `_map_solar_radius_to_hex_radius()` (line ~346)
- [ ] Change return type to `int`
- [ ] Update function body:
  ```python
  def _map_solar_radius_to_hex_radius(self, radius_sol, star_type) -> int:
      """Map solar radius to hex radius (1-6)."""
      if star_type in (StarType.NEUTRON_STAR, StarType.BLACK_HOLE, StarType.WHITE_DWARF):
          return 1
      if radius_sol < 0.8:
          return 1
      if radius_sol < 2.0:
          return 2
      if radius_sol < 5.0:
          return 2
      import math
      log_r = math.log10(radius_sol)
      hex_radius = 1.73 * log_r + 0.8
      hex_radius = min(6, max(1, int(round(hex_radius))))
      return hex_radius
  ```
- [ ] Update call site in primary star generation (~line 486): `self._map_radius_to_hexes(p_rad, p_type)` → `self._map_solar_radius_to_hex_radius(p_rad, p_type)`
- [ ] Update call site in companion generation (~line 515): same rename
- [ ] Update call site in random primary generation (~line 563): same rename
- [ ] Update call site in random companion generation (~line 608): same rename
- [ ] Update all Star constructor calls: `diameter_hexes=p_hex` → `radius_hexes=p_hex` (4 locations: ~lines 494, 535, 570, 610)

**Notes:**

### Task 2.2: Fix companion star placement [Simple]
**File:** `game/strategy/data/stars.py`
**Tests:** `pytest tests/integration/strategy/test_star_generation.py`

- [ ] Update min_dist_hex formula (line ~507):
  ```python
  # Old: min_dist_hex = int(p_hex * 2) + 2
  min_dist_hex = p_hex + 2
  ```

**Notes:**

### Task 2.3: Fix planet orbit safe_start [Simple]
**File:** `game/strategy/data/planet_gen.py`
**Tests:** `pytest tests/unit/strategy/data/test_planet_gen.py`

- [ ] Update safe_start formula (line 103):
  ```python
  # Old: safe_start = int(primary.diameter_hexes / 2) + 2
  safe_start = primary.radius_hexes + 2
  ```

**Notes:**

### Task 2.4: Update warp distance formula [Simple]
**File:** `game/strategy/data/galaxy_warp_generator.py`
**Tests:** `pytest tests/integration/strategy/test_warp_logic_rework.py`

- [ ] Rename variable: `star_diam` → `star_radius` (line 42)
- [ ] Update formula: `scaled_dist = base_dist + (star_diam * 1.5)` → `scaled_dist = base_dist + (star_radius * 3.0)` (line ~45)

**Notes:** Old: `15 + d*1.5`. New: `15 + r*3.0` preserves proportional relationship since r ≈ d/2.

### Task 2.5: Update superweapon Dyson Sphere creation [Simple]
**File:** `game/strategy/engine/superweapon_order_processor.py`
**Tests:** `pytest tests/unit/strategy/engine/test_superweapon_order_processor.py`

- [ ] Update Dyson Sphere creation (line 538): `diameter_hexes=11.0` → `radius_hexes=6`
- [ ] Update comment about zone radius (line ~478)

**Notes:**

### Task 2.6: Update galaxy entity registry [Simple]
**File:** `game/strategy/data/galaxy_entity_registry.py`
**Tests:** `pytest tests/unit/strategy/data/test_galaxy.py`

- [ ] Update 3 checks: `planet.diameter_hexes > 0` → `planet.radius_hexes > 0` (lines 58, 84, 113)

**Notes:**

### Task 2.7: Update galaxy spatial index [Simple]
**File:** `game/strategy/data/galaxy_spatial_index.py`
**Tests:** `pytest tests/unit/strategy/data/test_galaxy.py`

- [ ] Update comment: `diameter_hexes` → `radius_hexes` (line 176)
- [ ] Update check: `planet.diameter_hexes > 0` → `planet.radius_hexes > 0` (line 177)

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] No `diameter_hexes` references remain in production code under `game/`
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 3
