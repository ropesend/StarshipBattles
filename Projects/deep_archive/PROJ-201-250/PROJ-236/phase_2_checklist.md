# Phase 2: Orbital Generation Config

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-236 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Create OrbitalGenerationConfig, wire planet_gen.py orbital/moon/surface magic numbers to config

---

## Tasks

### Task 2.1: Create OrbitalGenerationConfig with tests (TDD) [Medium]
**New File:** `game/strategy/data/orbital_generation_config.py`
**New Test:** `tests/unit/strategy/data/test_orbital_generation_config.py`
**Tests:** `pytest tests/unit/strategy/data/test_orbital_generation_config.py -v`

- [x] Create test file following `test_classification_config.py` pattern:
  - `TestOrbitalGenerationConfigDefaults`: verify all DEFAULT_* dict values
  - `TestOrbitalGenerationConfigFromJson`: verify JSON loading with overrides
  - `TestGetOrbitalGenerationConfig`: verify `@lru_cache` getter, fallback on error
  - Include `cache_clear()` in setup/teardown
- [x] Create `orbital_generation_config.py` following `resource_generation_config.py` template:
  - `DEFAULT_ORBITAL`:
    - `safe_start_offset`: 2 (planet_gen.py:103)
    - `max_orbital_distance`: 20 (planet_gen.py:104)
    - `default_planet_min`: 3, `default_planet_max`: 10 (planet_gen.py:112-125)
    - `orbital_distribution_mode`: 0.3 (planet_gen.py:157)
    - `max_placement_attempts`: 20 (planet_gen.py:149)
    - `hot_jupiter_log_mass_min`: 26.7, `hot_jupiter_log_mass_max`: 28.0 (planet_gen.py:170)
    - `hot_jupiter_orbit_min`: 2, `hot_jupiter_orbit_max`: 3 (planet_gen.py:154)
  - `DEFAULT_MASS_GENERATION`:
    - `small_bias_mu`: 24.0, `small_bias_sigma`: 0.8 (planet_gen.py:220-221)
    - `large_bias_mu`: 26.5, `large_bias_sigma`: 0.8 (planet_gen.py:225-226)
    - `default_mu`: 24.0, `default_sigma`: 1.0 (planet_gen.py:230-231)
    - `max_iterations`: 100 (planet_gen.py:237)
  - `DEFAULT_MOON_SYSTEM`:
    - `jupiter_threshold_log`: 27.27 (planet_gen.py:298)
    - `earth_threshold_log`: 24.77 (planet_gen.py:300)
    - `ceres_threshold_log`: 20.97 (planet_gen.py:304)
    - `jupiter_chance`: 0.88 (planet_gen.py:299)
    - `earth_chance`: 0.35 (planet_gen.py:301)
    - `ceres_chance`: 0.02 (planet_gen.py:306)
    - `max_chance_cap`: 0.95 (planet_gen.py:311)
    - `mass_ratio_min`: 0.00001, `mass_ratio_max`: 0.05 (planet_gen.py:321-322)
    - `max_moons_per_body`: 50 (planet_gen.py:268)
  - `DEFAULT_SURFACE`:
    - `active_body_activity_min`: 0.1, `active_body_activity_max`: 0.8 (planet_gen.py:427)
    - `active_body_mag_min`: 0.5, `active_body_mag_max`: 2.0 (planet_gen.py:428)
    - `small_body_activity_min`: 0.0, `small_body_activity_max`: 0.2 (planet_gen.py:430)
    - `small_body_mag_min`: 0.0, `small_body_mag_max`: 0.5 (planet_gen.py:431)
    - `water_temp_min`: 250, `water_temp_max`: 350 (planet_gen.py:434)
  - `_load_from_json()` / `_use_defaults()`, `@lru_cache` getter
- [x] Add `"orbital_generation"` section to `data/astrophysics.json`
- [x] Update `AstrophysicsLoader._validate_schema()`: add `"orbital_generation"` to `required_sections`
- [x] Run tests
**Notes:**

---

### Task 2.2: Write characterization tests for planet_gen.py [Simple]
**File:** `tests/unit/strategy/data/test_planet_gen.py`
**Tests:** `pytest tests/unit/strategy/data/test_planet_gen.py -v`

- [x] Add seeded test pinning `_calculate_moon_chance` for Jupiter mass (1.89e27) → expect 0.88
- [x] Add seeded test pinning `_calculate_moon_chance` for Earth mass (5.97e24) → expect ~0.35
- [x] Add seeded test pinning `_calculate_moon_chance` for Mars mass (6.39e23) → expect ~0.23
- [x] Add seeded test pinning `_calculate_moon_chance` for Ceres mass (9.39e20) → expect 0.02
- [x] Add seeded tests pinning `_generate_mass_constrained` with each bias ("small", "large", None)
- [x] Add seeded tests pinning `_generate_surface_flags` for hot/cold/temperate bodies
**Notes:**

---

### Task 2.3: Wire planet_gen.py to OrbitalGenerationConfig [Medium]
**File:** `game/strategy/data/planet_gen.py`
**Tests:** `pytest tests/unit/strategy/data/test_planet_gen.py tests/unit/strategy/data/test_planet_classification_logic.py -v`

- [x] Add lazy import: `from game.strategy.data.orbital_generation_config import get_orbital_generation_config` inside methods
- [x] `_generate_orbital_slots` (lines 87-178):
  - `primary.radius_hexes + 2` → `+ cfg.safe_start_offset` (line 103)
  - `max_dist = 20` → `cfg.max_orbital_distance` (line 104)
  - `random.randint(3, 10)` → `random.randint(cfg.default_planet_min, cfg.default_planet_max)` (lines 112, 116, 125)
  - `0.3` → `cfg.orbital_distribution_mode` (line 157)
  - `range(20)` → `range(cfg.max_placement_attempts)` (line 149)
  - `26.7` / `28.0` → `cfg.hot_jupiter_log_mass_min` / `cfg.hot_jupiter_log_mass_max` (line 170)
  - `max(2, min(dist, 3))` → `max(cfg.hot_jupiter_orbit_min, min(dist, cfg.hot_jupiter_orbit_max))` (line 154)
- [x] `_generate_mass_constrained` (lines 199-243):
  - Small bias `24.0`/`0.8` → `cfg.small_bias_mu`/`cfg.small_bias_sigma` (lines 220-221)
  - Large bias `26.5`/`0.8` → `cfg.large_bias_mu`/`cfg.large_bias_sigma` (lines 225-226)
  - Default `24.0`/`1.0` → `cfg.default_mu`/`cfg.default_sigma` (lines 230-231)
  - `range(100)` → `range(cfg.max_iterations)` (line 237)
- [x] `_calculate_moon_chance` (lines 280-311):
  - `27.27` → `cfg.jupiter_threshold_log` (line 298)
  - `24.77` → `cfg.earth_threshold_log` (lines 300, 302, 306)
  - `20.97` → `cfg.ceres_threshold_log` (lines 304, 306)
  - `0.88` → `cfg.jupiter_chance` (lines 299, 303)
  - `0.35` → `cfg.earth_chance` (lines 301, 303, 307)
  - `0.02` → `cfg.ceres_chance` (lines 306, 307, 309)
  - `0.95` → `cfg.max_chance_cap` (line 311)
- [x] `_generate_moon_mass` (lines 313-327):
  - `0.00001` → `cfg.mass_ratio_min` (line 321)
  - `0.05` → `cfg.mass_ratio_max` (line 322)
- [x] `_generate_moons` (lines 245-278):
  - `50` → `cfg.max_moons_per_body` (line 268)
- [x] `_generate_surface_flags` (lines 418-441):
  - `0.1, 0.8` → `cfg.active_body_activity_min, cfg.active_body_activity_max` (line 427)
  - `0.5, 2.0` → `cfg.active_body_mag_min, cfg.active_body_mag_max` (line 428)
  - `0, 0.2` → `cfg.small_body_activity_min, cfg.small_body_activity_max` (line 430)
  - `0, 0.5` → `cfg.small_body_mag_min, cfg.small_body_mag_max` (line 431)
  - `250` / `350` → `cfg.water_temp_min` / `cfg.water_temp_max` (line 434)
- [x] Run characterization tests — all pass
- [x] Run full planet gen tests — all pass
**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] `pytest tests/unit/strategy/data/test_planet_gen.py tests/unit/strategy/data/test_orbital_generation_config.py tests/unit/strategy/data/test_planet_classification_logic.py -v` — all pass
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 3
