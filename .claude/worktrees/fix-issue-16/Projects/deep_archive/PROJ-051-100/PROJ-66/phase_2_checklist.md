# Phase 2: Homeworld Presets Data [Simple]

**Objective:** Create homeworld presets JSON and loading logic
**Tests:** `pytest tests/unit/strategy/data/test_homeworld_presets.py -v`

---

## Task 2.1: Create Homeworld Presets JSON [Simple]
**File:** `game/data/homeworld_presets.json` (NEW)

- [x] Create JSON file with all 11 PlanetType presets
- [x] Each preset includes: `id`, `name`, `description`, `gravity_ideal`, `gravity_tolerance`, `temperature_ideal`, `temperature_tolerance`, `water_ideal`, `water_tolerance`, `radiation_tolerance`, `atmosphere_preferences`
- [x] Values derived from planet generation thresholds in `data/astrophysics.json` and `game/strategy/data/planet_gen.py`:
  - CONTINENTAL: gravity=1.0, temp=293K, water=0.60, radiation=0, O2:+50/N2:+30
  - ARID: gravity=1.0, temp=320K, water=0.10, radiation=+20, CO2:+30/N2:+20
  - PELAGIC: gravity=0.9, temp=290K, water=0.95, radiation=-10, O2:+50/N2:+30
  - MAGMA: gravity=1.2, temp=800K, water=0.0, radiation=+60, CO2:+40
  - CRYOPLANET: gravity=0.8, temp=200K, water=0.30, radiation=+10, CO2:+20/N2:+10
  - BARREN: gravity=0.6, temp=350K, water=0.0, radiation=+80, all atmosphere 0
  - JOVIAN: gravity=2.5, temp=200K, water=0.0, radiation=+40, H2:+80/He:+60
  - ICE_GIANT: gravity=1.5, temp=100K, water=0.0, radiation=+20, H2:+50/He:+40/CH4:+30
  - CHTHONIAN: gravity=2.0, temp=900K, water=0.0, radiation=+90, all atmosphere 0
  - ICE_DWARF: gravity=0.1, temp=100K, water=0.80, radiation=+10, all atmosphere 0
  - PLANETOID: gravity=0.05, temp=250K, water=0.0, radiation=+50, all atmosphere 0
- [x] Validate JSON is well-formed
**Notes:** Created game/data/homeworld_presets.json with all 11 presets

---

## Task 2.2: Create Preset Loading Utility [Simple]
**File:** `game/strategy/data/homeworld_presets.py` (NEW)
**Tests:** `pytest tests/unit/strategy/data/test_homeworld_presets.py -v`

- [x] Create `load_homeworld_presets()` function that reads JSON and returns dict of presets keyed by id
- [x] Create `get_preset_for_planet_type(planet_type_name: str)` function
- [x] Create `apply_preset_to_config(preset: dict, race_config: RaceConfig)` function that sets environment fields
- [x] Create `get_available_homeworld_names()` function returning list of names for dropdown
- [x] Write test: `test_load_homeworld_presets_returns_all_11`
- [x] Write test: `test_get_preset_for_continental`
- [x] Write test: `test_get_preset_for_jovian`
- [x] Write test: `test_apply_preset_to_config_sets_gravity`
- [x] Write test: `test_apply_preset_to_config_sets_atmosphere`
- [x] Write test: `test_apply_preset_to_config_sets_water`
- [x] Write test: `test_get_available_homeworld_names_returns_11`
- [x] Write test: `test_get_preset_for_invalid_type_returns_none`
- [x] Run tests: all pass
**Notes:** Created game/strategy/data/homeworld_presets.py with caching, 14 tests all passing

---

## Phase 2 Completion Checklist
- [x] All tasks above checked off
- [x] Run `pytest tests/unit/strategy/data/test_homeworld_presets.py -v` — all pass (14 tests)
- [x] Run `pytest tests/ --testmon` — no regressions
- [x] Homeworld presets JSON is valid and loads correctly
