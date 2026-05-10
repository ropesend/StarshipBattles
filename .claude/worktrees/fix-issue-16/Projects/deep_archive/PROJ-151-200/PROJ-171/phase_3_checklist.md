# Phase 3: Celestial Bodies (Star, Spectrum, Planet)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> - Run `python Projects/scripts/validate_phase.py PROJ-171 3`
> - Ensure ALL boxes below are checked
> - Run phase tests: `pytest tests/unit/strategy/stars/ tests/unit/strategy/planet/ -v`

## Task 3.1: Validate Spectrum.from_dict() [Simple]
**File:** `game/strategy/data/stars.py:62-75`
**Tests:** `pytest tests/unit/strategy/stars/test_spectrum_validation.py`

- [x] Add imports for `require_keys`, `validate_non_negative` from `game.core.validation_helpers`
- [x] Add `require_keys(data, ['gamma_ray', 'xray', 'ultraviolet', 'blue', 'green', 'red', 'infrared', 'microwave', 'radio'], 'Spectrum')` at start
- [x] Add `validate_non_negative()` for each of the 9 spectrum fields
- [x] Create test file `tests/unit/strategy/stars/test_spectrum_validation.py`
- [x] Test: valid data → Spectrum created
- [x] Test: missing any one band (e.g. 'blue') → PersistenceException
- [x] Test: negative spectrum value → PersistenceException
- [x] Test: zero values → passes (zero is valid for a spectrum band)

**Notes:** 9 required float fields, all >= 0. Implemented with loop over all 9 spectrum keys for validation.

## Task 3.2: Validate Star.from_dict() [Medium]
**File:** `game/strategy/data/stars.py:123-138`
**Tests:** `pytest tests/unit/strategy/stars/test_star_validation.py`

- [x] Add imports for `require_keys`, `validate_enum`, `validate_positive`, `safe_from_dict`
- [x] Add `require_keys(data, ['name', 'mass', 'diameter_hexes', 'temperature', 'luminosity', 'spectrum', 'star_type', 'color', 'age', 'location'], 'Star')`
- [x] Replace `StarType[data['star_type']]` with `validate_enum(data['star_type'], StarType, 'star_type', 'Star')`
- [x] Add `validate_positive(data['mass'], 'mass', 'Star')`
- [x] Add `validate_positive(data['temperature'], 'temperature', 'Star')`
- [x] Add `validate_positive(data['luminosity'], 'luminosity', 'Star')`
- [x] Wrap `Spectrum.from_dict(data['spectrum'])` with safe_from_dict or try/except
- [x] Wrap `hex_from_dict(data['location'])` with try/except
- [x] Create test file `tests/unit/strategy/stars/test_star_validation.py`
- [x] Test: valid data → Star created
- [x] Test: missing 'name' → PersistenceException
- [x] Test: invalid star_type enum → PersistenceException with valid_values listed
- [x] Test: negative mass → PersistenceException
- [x] Test: corrupt spectrum data → PersistenceException mentioning 'Spectrum' context

**Notes:** 10 required fields. Star is a leaf node. Used safe_from_dict for Spectrum, manual try/except for location.

## Task 3.3: Validate Planet.from_dict() [Complex]
**File:** `game/strategy/data/planet.py:357-420`
**Tests:** `pytest tests/unit/strategy/planet/test_planet_validation.py`

- [x] Add imports for `require_keys`, `validate_enum`, `validate_positive`, `validate_non_negative`
- [x] Add `require_keys(data, ['name', 'location', 'orbit_distance', 'mass', 'radius', 'surface_area', 'density', 'surface_gravity', 'surface_pressure', 'surface_temperature', 'surface_water', 'tectonic_activity', 'magnetic_field', 'planet_type'], 'Planet')`
- [x] Replace `PlanetType[data['planet_type']]` with `validate_enum(data['planet_type'], PlanetType, 'planet_type', 'Planet')`
- [x] Add `validate_positive()` for: mass, radius, surface_area, density, surface_gravity
- [x] Add `validate_non_negative()` for: orbit_distance, surface_pressure, surface_water
- [x] Wrap facility deserialization loop in try/except per facility — skip bad with warning
- [x] Wrap population deserialization loop in try/except per population — skip bad with warning
- [x] Create test file `tests/unit/strategy/planet/test_planet_validation.py`
- [x] Test: valid data → Planet created
- [x] Test: missing 'name' → PersistenceException
- [x] Test: invalid planet_type → PersistenceException with valid types listed
- [x] Test: negative mass → PersistenceException
- [x] Test: bad facility in list → facility skipped, planet loads
- [x] Test: bad population in list → population skipped, planet loads
- [x] Verify existing test_planet_serialization.py still passes

**Notes:** 14 required fields. Resilient deserialization for facilities/populations with logger.warning.

## Phase 3 Completion
- [x] All tasks above checked
- [x] `pytest tests/unit/strategy/stars/ tests/unit/strategy/planet/ -v` — 67 passed
- [x] `pytest tests/integration/strategy/test_planet_serialization.py -v` — 8 passed
- [x] `pytest tests/ -n 12` — 12082 passed, 1 skipped (full suite verification)
