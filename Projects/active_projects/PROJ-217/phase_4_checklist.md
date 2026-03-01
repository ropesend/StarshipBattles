# Phase 4: Test Updates

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-217 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Update all test files to use `radius_hexes` with correct expected values. Full suite must pass.

---

## Tasks

### Task 4.1: Update `test_stars.py` [Medium]
**File:** `tests/unit/strategy/data/test_stars.py`
**Tests:** `pytest tests/unit/strategy/data/test_stars.py -v`

- [ ] Replace all `diameter_hexes=` → `radius_hexes=` in Star constructors
- [ ] Update serialization key: `'diameter_hexes'` → `'radius_hexes'`
- [ ] Update `test_star_occupied_hexes_small`: `radius_hexes=1` → expect 1 hex
- [ ] Update `test_star_occupied_hexes_large`: `radius_hexes=6` → expect 91 hexes, max distance 5
- [ ] Update `test_star_occupied_hexes_sub_hex`: `radius_hexes=1` → expect 1 hex
- [ ] Update `test_star_occupied_hexes_with_offset_location`: `radius_hexes=2` → expect 7 hexes, max distance 1
- [ ] Update generator tests: rename function references
- [ ] Update all math comments
- [ ] Run: `pytest tests/unit/strategy/data/test_stars.py -v` — all pass

**Notes:**

### Task 4.2: Update `test_planet_zones.py` [Simple]
**File:** `tests/unit/strategy/data/test_planet_zones.py`
**Tests:** `pytest tests/unit/strategy/data/test_planet_zones.py -v`

- [ ] Replace all `diameter_hexes=` → `radius_hexes=`
- [ ] Dyson Sphere fixture: `radius_hexes=6` → 91 hexes, distance ≤ 5
- [ ] Offset Dyson test: `radius_hexes=3` → 19 hexes, distance ≤ 2
- [ ] Update serialization tests: key and values
- [ ] Update roundtrip test values: `[0, 1, 2, 3, 4, 6]`
- [ ] Rename class `TestPlanetDiameterHexesSerialization` → `TestPlanetRadiusHexesSerialization`
- [ ] Run: `pytest tests/unit/strategy/data/test_planet_zones.py -v` — all pass

**Notes:**

### Task 4.3: Update `test_galaxy.py` helpers [Simple]
**File:** `tests/unit/strategy/data/test_galaxy.py`
**Tests:** `pytest tests/unit/strategy/data/test_galaxy.py -v`

- [ ] `make_test_star()`: `diameter_hexes=1.0` → `radius_hexes=1`
- [ ] `make_test_planet()`: `diameter_hexes=0.0` → `radius_hexes=0`
- [ ] Update all call sites in the file
- [ ] Run: `pytest tests/unit/strategy/data/test_galaxy.py -v` — all pass

**Notes:**

### Task 4.4: Update protocol tests [Simple]
**File:** `tests/unit/core/test_protocols.py`
**Tests:** `pytest tests/unit/core/test_protocols.py -v`

- [ ] Update Star/Planet constructors in IZoneOccupant tests
- [ ] Run: `pytest tests/unit/core/test_protocols.py -v` — all pass

**Notes:**

### Task 4.5: Update integration tests [Medium]
**Files:** `tests/integration/strategy/`
**Tests:** `pytest tests/integration/strategy/ -v`

- [ ] `test_star_generation.py`: Update constructors + assertions
- [ ] `test_warp_logic_rework.py`: Update constructors (lines 21, 30, 91)
- [ ] `test_radiation.py`: Update fixture (line 14)
- [ ] `test_superweapon_integration.py`: Update constructors (3+ locations)
- [ ] `tests/integration/strategy/facade/test_system_dto.py`
- [ ] `tests/integration/strategy/facade/test_system_queries.py`
- [ ] `tests/integration/colonization/test_planet_specific_colonization.py`
- [ ] Run: `pytest tests/integration/ -v` — all pass

**Notes:**

### Task 4.6: Update remaining unit tests [Medium]
**Files:** Multiple files under `tests/unit/`
**Tests:** `pytest tests/unit/ -v`

- [ ] `test_strategy_renderer.py`: mock `diameter_hexes` → `radius_hexes` (5 locations)
- [ ] `test_strategy_detail_fmt.py`: mock update (line 56)
- [ ] `test_star_validation.py`: constructors (lines 27, 51)
- [ ] `test_star_system_validation.py`: constructor (line 70)
- [ ] `test_planet_gen.py`: references (3 locations)
- [ ] `test_storm.py`: constructor (line 454)
- [ ] `test_storm_generator.py`: constructor (line 53)
- [ ] `test_colonize_validator.py`: constructors (6 locations)
- [ ] `test_colonize_mission_handler.py`: constructors
- [ ] `test_superweapon_order_processor.py`: constructors
- [ ] `test_strategy_colonization.py`: constructor (line 31)
- [ ] `tests/repro_facade_colonies.py`: constructors (lines 32, 66)
- [ ] Run: `pytest tests/unit/ -n 12` — all pass

**Notes:**

### Task 4.7: Full test suite verification [Simple]
**Tests:** `pytest tests/ -n 12`

- [ ] Run full test suite — all 13,040+ tests must pass
- [ ] Verify: `grep -r "diameter_hexes" game/ tests/` returns zero results
- [ ] Fix any remaining failures

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Full test suite passes (13,040+ tests)
- [ ] Zero `diameter_hexes` references in `game/` and `tests/`
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to "Complete"
