# Phase 3: Celestial Bodies (Star, Spectrum, Planet)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> - Run `python Projects/scripts/validate_phase.py PROJ-171 3`
> - Ensure ALL boxes below are checked
> - Run phase tests: `pytest tests/unit/strategy/stars/ tests/unit/strategy/planet/ -v`

## Task 3.1: Validate Spectrum.from_dict() [Simple]
**File:** `game/strategy/data/stars.py:62-75`
**Tests:** `pytest tests/unit/strategy/stars/test_spectrum_validation.py`

- [ ] Add imports for `require_keys`, `validate_non_negative` from `game.core.validation_helpers`
- [ ] Add `require_keys(data, ['gamma_ray', 'xray', 'ultraviolet', 'blue', 'green', 'red', 'infrared', 'microwave', 'radio'], 'Spectrum')` at start
- [ ] Add `validate_non_negative()` for each of the 9 spectrum fields
- [ ] Create test file `tests/unit/strategy/stars/test_spectrum_validation.py`
- [ ] Test: valid data → Spectrum created
- [ ] Test: missing any one band (e.g. 'blue') → PersistenceException
- [ ] Test: negative spectrum value → PersistenceException
- [ ] Test: zero values → passes (zero is valid for a spectrum band)

**Notes:** 9 required float fields, all >= 0.

## Task 3.2: Validate Star.from_dict() [Medium]
**File:** `game/strategy/data/stars.py:123-138`
**Tests:** `pytest tests/unit/strategy/stars/test_star_validation.py`

- [ ] Add imports for `require_keys`, `validate_enum`, `validate_positive`, `safe_from_dict`
- [ ] Add `require_keys(data, ['name', 'mass', 'diameter_hexes', 'temperature', 'luminosity', 'spectrum', 'star_type', 'color', 'age', 'location'], 'Star')`
- [ ] Replace `StarType[data['star_type']]` with `validate_enum(data['star_type'], StarType, 'star_type', 'Star')`
- [ ] Add `validate_positive(data['mass'], 'mass', 'Star')`
- [ ] Add `validate_positive(data['temperature'], 'temperature', 'Star')`
- [ ] Add `validate_positive(data['luminosity'], 'luminosity', 'Star')`
- [ ] Wrap `Spectrum.from_dict(data['spectrum'])` with safe_from_dict or try/except
- [ ] Wrap `hex_from_dict(data['location'])` with try/except
- [ ] Create test file `tests/unit/strategy/stars/test_star_validation.py`
- [ ] Test: valid data → Star created
- [ ] Test: missing 'name' → PersistenceException
- [ ] Test: invalid star_type enum → PersistenceException with valid_values listed
- [ ] Test: negative mass → PersistenceException
- [ ] Test: corrupt spectrum data → PersistenceException mentioning 'Spectrum' context

**Notes:** 10 required fields. Star is a leaf node.

## Task 3.3: Validate Planet.from_dict() [Complex]
**File:** `game/strategy/data/planet.py:357-420`
**Tests:** `pytest tests/unit/strategy/planet/test_planet_validation.py`

- [ ] Add imports for `require_keys`, `validate_enum`, `validate_positive`, `validate_non_negative`
- [ ] Add `require_keys(data, ['name', 'location', 'orbit_distance', 'mass', 'radius', 'surface_area', 'density', 'surface_gravity', 'surface_pressure', 'surface_temperature', 'surface_water', 'tectonic_activity', 'magnetic_field', 'planet_type'], 'Planet')`
- [ ] Replace `PlanetType[data['planet_type']]` with `validate_enum(data['planet_type'], PlanetType, 'planet_type', 'Planet')`
- [ ] Add `validate_positive()` for: mass, radius, surface_area, density, surface_gravity
- [ ] Add `validate_non_negative()` for: orbit_distance, surface_pressure, surface_water
- [ ] Wrap facility deserialization loop in try/except per facility — skip bad with warning
- [ ] Wrap population deserialization loop in try/except per population — skip bad with warning
- [ ] Create test file `tests/unit/strategy/planet/test_planet_validation.py`
- [ ] Test: valid data → Planet created
- [ ] Test: missing 'name' → PersistenceException
- [ ] Test: invalid planet_type → PersistenceException with valid types listed
- [ ] Test: negative mass → PersistenceException
- [ ] Test: bad facility in list → facility skipped, planet loads
- [ ] Test: bad population in list → population skipped, planet loads
- [ ] Verify existing test_planet_serialization.py still passes

**Notes:** 14 required fields. Nested facility and population sub-objects. Most complex method.

## Phase 3 Completion
- [ ] All tasks above checked
- [ ] `pytest tests/unit/strategy/stars/ tests/unit/strategy/planet/ -v` — all pass
- [ ] `pytest tests/integration/strategy/test_planet_serialization.py -v` — still passes
- [ ] `pytest tests/ --testmon` — no regressions
