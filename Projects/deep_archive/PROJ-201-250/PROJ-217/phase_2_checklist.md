# Phase 2: Generation & Game Logic

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-217 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Update star generation, companion placement, orbit calculation, warp distance, superweapon code, entity registry, and spatial index to use `radius_hexes`.

---

## Tasks

### Task 2.1: Rewrite star size generation function [Medium]
**File:** `game/strategy/data/stars.py`
**Tests:** `pytest tests/unit/strategy/data/test_stars.py -k "test_star_generator"`

- [x] Rename `_map_radius_to_hexes()` → `_map_solar_radius_to_hex_radius()` (line ~346)
- [x] Change return type to `int`
- [x] Update function body with proper integer radius logic
- [x] Update call site in primary star generation (~line 486)
- [x] Update call site in companion generation (~line 515)
- [x] Update call site in random primary generation (~line 563)
- [x] Update call site in random companion generation (~line 608)
- [x] Update all Star constructor calls: `diameter_hexes=p_hex` → `radius_hexes=p_hex` (4 locations)

**Notes:** Complete. Function renamed with proper int return type and logarithmic scaling for giants.

### Task 2.2: Fix companion star placement [Simple]
**File:** `game/strategy/data/stars.py`
**Tests:** `pytest tests/integration/strategy/test_star_generation.py`

- [x] Update min_dist_hex formula: `int(p_hex * 2) + 2` → `p_hex + 2`

**Notes:** Complete. Both blueprint and random generation paths updated.

### Task 2.3: Fix planet orbit safe_start [Simple]
**File:** `game/strategy/data/planet_gen.py`
**Tests:** `pytest tests/unit/strategy/data/test_planet_gen.py`

- [x] Update safe_start formula: `int(primary.diameter_hexes / 2) + 2` → `primary.radius_hexes + 2`

**Notes:** Complete.

### Task 2.4: Update warp distance formula [Simple]
**File:** `game/strategy/data/galaxy_warp_generator.py`
**Tests:** `pytest tests/integration/strategy/test_warp_logic_rework.py`

- [x] Rename variable: `star_diam` → `star_radius`
- [x] Update formula: `star_diam * 1.5` → `star_radius * 3.0`
- [x] Update docstring

**Notes:** Complete. Formula preserves proportional relationship since r ≈ d/2.

### Task 2.5: Update superweapon Dyson Sphere creation [Simple]
**File:** `game/strategy/engine/superweapon_order_processor.py`
**Tests:** `pytest tests/unit/strategy/engine/test_superweapon_order_processor.py`

- [x] Update Dyson Sphere creation: `diameter_hexes=11.0` → `radius_hexes=6`
- [x] Update comment about zone radius

**Notes:** Complete.

### Task 2.6: Update galaxy entity registry [Simple]
**File:** `game/strategy/data/galaxy_entity_registry.py`
**Tests:** `pytest tests/unit/strategy/data/test_galaxy.py`

- [x] Update 3 checks: `planet.diameter_hexes > 0` → `planet.radius_hexes > 0`

**Notes:** Complete. Used replace_all.

### Task 2.7: Update galaxy spatial index [Simple]
**File:** `game/strategy/data/galaxy_spatial_index.py`
**Tests:** `pytest tests/unit/strategy/data/test_galaxy.py`

- [x] Update comment: `diameter_hexes` → `radius_hexes`
- [x] Update check: `planet.diameter_hexes > 0` → `planet.radius_hexes > 0`

**Notes:** Complete.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] No `diameter_hexes` references remain in production code under `game/` (except Phase 3 UI files)
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 3
