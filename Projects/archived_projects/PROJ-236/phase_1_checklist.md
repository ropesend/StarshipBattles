# Phase 1: Star Generation Config + Constants

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-236 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Create StarGenerationConfig, extract Stefan-Boltzmann group, name physics constants, fix while-True loop

---

## Tasks

### Task 1.1: Create StarGenerationConfig with tests (TDD) [Medium]
**New File:** `game/strategy/data/star_generation_config.py`
**New Test:** `tests/unit/strategy/data/test_star_generation_config.py`
**Tests:** `pytest tests/unit/strategy/data/test_star_generation_config.py -v`

- [x] Create test file following `test_classification_config.py` pattern (229 lines):
  - `TestStarGenerationConfigDefaults`: verify all DEFAULT_* dict values
  - `TestStarGenerationConfigFromJson`: verify JSON loading with overrides
  - `TestGetStarGenerationConfig`: verify `@lru_cache` getter, fallback on error
  - Include `cache_clear()` in setup/teardown
- [x] Create `star_generation_config.py` following `resource_generation_config.py` template:
  - `DEFAULT_TYPE_WEIGHTS`: 8 StarType weights from `stars.py:255-264` (`MAIN_SEQUENCE: 0.525, RED_DWARF: 0.250, RED_GIANT: 0.070, BLUE_GIANT: 0.060, BROWN_DWARF: 0.030, WHITE_DWARF: 0.030, NEUTRON_STAR: 0.020, BLACK_HOLE: 0.015`)
  - `DEFAULT_MASS_GENERATION`: `sigma=0.8, min_mass=0.1, max_mass=100.0, max_attempts=1000`
  - `DEFAULT_SYSTEM_PROBABILITIES`: `count_thresholds=[{"count": 4, "cumulative": 0.001}, {"count": 3, "cumulative": 0.011}, {"count": 2, "cumulative": 0.111}], default_count=1, age_min=0.1, age_max=10.0, age_unit=1e9`
  - `DEFAULT_COMPANION_SPACING`: `ring_multiplier=10, jitter_min=2, jitter_max=8, min_offset=2, collision_limit=100`
  - `DEFAULT_STEFAN_BOLTZMANN_TYPES`: dict keyed by StarType name for RED_GIANT, BROWN_DWARF, WHITE_DWARF — each with mass adjustment params, radius params, temp_range, fixed color
  - `_load_from_json()` / `_use_defaults()` methods
  - `@lru_cache` `get_star_generation_config()` function
- [x] Add `"star_generation"` section to `data/astrophysics.json` with exact matching values
- [x] Update `AstrophysicsLoader._validate_schema()` (line 119): add `"star_generation"` to `required_sections`
- [x] Run tests — all new tests pass
**Notes:** 12 tests in 3 test classes, all passing. Config file is 197 lines. JSON section added with all default values. AstrophysicsLoader updated.

---

### Task 1.2: Write characterization tests for star generation [Simple]
**File:** `tests/unit/strategy/data/test_stars.py`
**Tests:** `pytest tests/unit/strategy/data/test_stars.py -v`

- [x] Add seeded-random golden-output tests for `_determine_type_and_radius`:
  - Seed random, force `_roll_star_type` to return each StarType in turn
  - Assert exact 6-tuple output `(star_type, mass, radius, temperature, luminosity, color)` for each
  - Use `@pytest.mark.parametrize` with 8 cases (one per StarType)
- [x] Add seeded tests for `_generate_mass` (verify output within bounds)
- [x] Add seeded tests for `_kelvin_to_rgb` at key temperatures (3000K, 5778K, 10000K, 40000K)
- [x] These pin current behavior before any refactoring
**Notes:** Added TestDetermineTypeCharacterization class with 19 tests: 8 parametrized validity tests, 6 fixed-color tests, 2 kelvin-to-rgb derivation tests, 1 Stefan-Boltzmann formula test, 1 mass adjustment test, 1 kelvin known values test. Used unittest.mock.patch.object to force each StarType. Existing mass and kelvin tests already covered by TestStarGenerator. Total: 51 tests passing.

---

### Task 1.3: Extract Stefan-Boltzmann group into helper [Medium]
**File:** `game/strategy/data/stars.py` (lines 266-338)
**Tests:** `pytest tests/unit/strategy/data/test_stars.py -v`

- [x] Load config at method start: `cfg = get_star_generation_config()`
- [x] Create `_compute_stefan_boltzmann_type(star_type, mass, cfg)` helper method (~20 lines):
  - Reads type-specific params from `cfg.stefan_boltzmann_types[star_type.name]`
  - Adjusts mass per type's adjustment mode
  - Computes radius from params
  - Picks temperature from range
  - Computes luminosity via `(radius ** 2) * ((temperature / SOLAR_TEMP_K) ** 4)`
  - Returns fixed color from params
  - Returns `(mass, radius, temperature, luminosity, color)`
- [x] In `_determine_type_and_radius`: add early check for `star_type in _SB_TYPES` set, delegate to helper
- [x] Keep BLUE_GIANT, RED_DWARF, NEUTRON_STAR, BLACK_HOLE, MAIN_SEQUENCE as explicit if/elif branches (unchanged logic, but use named constants from config for their magic numbers)
- [x] Run characterization tests — identical outputs for identical seeds
**Notes:** Extracted `_compute_stefan_boltzmann_type` (35 lines). Added `_SB_TYPES` frozenset. All 51 unit tests + 20 integration tests pass. Removed 3 elif branches (RED_GIANT, BROWN_DWARF, WHITE_DWARF) and replaced with single SB dispatch. Net reduction: ~15 lines from the if/elif chain.

---

### Task 1.4: Replace _TYPE_WEIGHTS and mass/system/companion magic numbers [Simple]
**File:** `game/strategy/data/stars.py`
**Tests:** `pytest tests/unit/strategy/data/test_stars.py tests/integration/strategy/test_star_generation.py -v`

- [x] Replace `_TYPE_WEIGHTS` class variable in `_roll_star_type` with `cfg.type_weights` (line 344)
- [x] In `_generate_mass` (line 238): replace `0.8` sigma → `cfg.mass_sigma`, `0.1`/`100.0` → `cfg.mass_min`/`cfg.mass_max`
- [x] In `_generate_mass`: add `cfg.max_attempts` iteration cap to `while True` loop, with log-space fallback
- [x] In `_generate_random_stars` (lines 640-644): replace `0.001`/`0.011`/`0.111` with `cfg.system_count_thresholds`
- [x] In `_generate_random_stars` (line 661): replace `random.uniform(0.1, 10.0) * 1e9` with `random.uniform(cfg.age_min, cfg.age_max) * cfg.age_unit`
- [x] In `_generate_companions` (line 523): replace `i * 10` → `i * cfg.companion_ring_multiplier`, `randint(2, 8)` → `randint(cfg.companion_jitter_min, cfg.companion_jitter_max)`
- [x] In `_generate_companions` (line 514): replace `+ 2` → `+ cfg.companion_min_offset`
- [x] In `_generate_companions` (line 530): replace `100` → `cfg.companion_collision_limit`
- [x] Also updated age in `generate_from_blueprint` (was also hardcoded 0.1-10.0 * 1e9)
- [x] Run tests — 71 passed (51 unit + 20 integration)
**Notes:** Fixed unbounded while-True in `_generate_mass` — now uses `for _ in range(cfg.mass_max_attempts)` with log-space fallback. `_roll_star_type` now uses `StarType[type_name]` enum lookup from string keys in config. `_TYPE_WEIGHTS` class variable kept for backward compat but no longer used by `_roll_star_type`.

---

### Task 1.5: Name physics constants [Simple]
**File:** `game/strategy/data/stars.py`
**Tests:** `pytest tests/unit/strategy/data/test_stars.py -v`

- [x] Add Kelvin-to-RGB named constants at module level with Tanner Helland citation (10 constants)
- [x] Update `_kelvin_to_rgb` to use named constants (lines 350-387)
- [x] Add spectrum named constants (WIEN_DISPLACEMENT_CONSTANT, _SPECTRUM_SIGMA, _SPECTRUM_JITTER_RANGE, _WAVELENGTHS dict)
- [x] Update `_generate_spectrum` to use named constants — also refactored to use dict comprehension for intensities
- [x] Add hex radius mapping constants (_HEX_RADIUS_LOG_COEFF, _HEX_RADIUS_LOG_OFFSET, _HEX_RADIUS_MIN, _HEX_RADIUS_MAX)
- [x] Update `_map_solar_radius_to_hex_radius` to use named constants
- [x] Run tests — 71 passed (51 unit + 20 integration)
**Notes:** All 22 named constants added at module level. Kelvin-to-RGB coefficients documented with Tanner Helland citation. Spectrum generation refactored to iterate over _WAVELENGTHS dict instead of 9 individual variables. All physics/math constants stay as module-level, not in JSON.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] `pytest tests/unit/strategy/data/test_stars.py tests/unit/strategy/data/test_star_generation_config.py tests/integration/strategy/test_star_generation.py -v` — 71 passed
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 2
