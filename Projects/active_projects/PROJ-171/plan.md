# PROJ-171: Deserialization Input Validation

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-171` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-171 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Validation Helper Infrastructure | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Galaxy Core (Galaxy, StarSystem, WarpPoint) | Complete | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Celestial Bodies (Star, Spectrum, Planet) | Complete | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Empire & Fleet (Empire, Fleet, ShipInstance) | Not Started | [phase_4_checklist.md](phase_4_checklist.md) |
| 5. Simulation State (ShipState, ComponentState, Event, DesignMetadata) | Not Started | [phase_5_checklist.md](phase_5_checklist.md) |

## Current State
**Last Updated:** 2026-02-24
**Active Phase:** Phase 4
**Last Action:** Phase 3 complete - Celestial bodies validation (Spectrum, Star, Planet) with 67 new tests
**Next Action:** Start Phase 4 - Empire & Fleet validation (ShipInstance, Fleet, Empire)
**Blockers:** None
**Baseline:** 12082 passed, 1 skipped

## Overview

20 `from_dict` / deserialization methods were audited across `game/`. Only 3 validate well; 4 have **no validation at all**, and 11 have **partial validation** with significant gaps. Corrupt or malformed save data currently produces cryptic `KeyError` or `TypeError` crashes instead of meaningful `PersistenceException` messages. This project adds structured input validation to all 15 under-validated methods, using the PROJ-45 exception hierarchy (`PersistenceException`, `ValidationException`) with error codes and context dicts.

## Goals
- Add required-field validation to all from_dict methods that use direct `data["key"]` access
- Add enum validation (try/except around enum conversions) for PlanetType, StarType, OrderType, LayerType
- Wrap all from_dict methods in try/except that converts KeyError/TypeError to PersistenceException with context
- Add range validation for critical numeric fields (mass > 0, radius > 0, HP >= 0)
- Write negative-input tests for every from_dict method (missing keys, wrong types, invalid enums)
- Produce clear, actionable error messages that identify the corrupt field and its value

## Scope
**In:**
- 15 from_dict methods that need validation improvements (4 NO_VALIDATION + 11 PARTIAL_VALIDATION)
- New tests for invalid input handling (~60-80 new test cases)
- A thin validation helper module to reduce boilerplate

**Out:**
- Methods that already validate well (EventLog.from_dict — uses .get() with empty list default)
- RaceConfig.from_dict() — already fully defensive with .get() defaults on ALL fields
- LayerData.from_definition() — already fully defensive
- to_dict() methods — serialization is trusted internal code
- Changing the data format or adding versioning (separate concern)
- Adding validation to non-from_dict code paths (covered by PROJ-170)

## Key Files
| Component | File Path | Methods |
|-----------|-----------|---------|
| Exception hierarchy | `game/core/exceptions.py` | PersistenceException, ValidationException |
| Error codes | `game/core/error_codes.py` | P003 CORRUPT_DATA, V001 VALIDATION_FAILED |
| Galaxy core | `game/strategy/data/galaxy.py` | Galaxy.from_dict():879, StarSystem.from_dict():77, WarpPoint.from_dict():35 |
| Planet | `game/strategy/data/planet.py` | Planet.from_dict():357 |
| Stars | `game/strategy/data/stars.py` | Star.from_dict():123, Spectrum.from_dict():62 |
| Empire | `game/strategy/data/empire.py` | Empire.from_dict():168 |
| Fleet | `game/strategy/data/fleet.py` | Fleet.from_dict():343 |
| Ship instance | `game/strategy/data/ship_instance.py` | ShipInstance.from_dict():632 |
| Ship serializer | `game/simulation/entities/ship_serialization.py` | ShipSerializer.from_dict():123, _load_components():164 |
| Battle state | `game/simulation/battle_state.py` | ComponentState.from_dict():50, ShipState.from_dict():146 |
| Event | `game/strategy/events/event_log.py` | Event.from_dict():40 |
| Design metadata | `game/strategy/data/design_metadata.py` | DesignMetadata.from_dict():58 |
| Tech tree | `game/research/data/tech_tree.py` | TechTree.load_from_json():28 |
| Existing tests | `tests/unit/strategy/fleet/test_serialization.py` | Fleet round-trip tests |
| Existing tests | `tests/unit/strategy/ship_instance/test_serialization.py` | ShipInstance round-trip tests |
| Existing tests | `tests/unit/simulation/entities/test_ship_serialization.py` | Ship serialization tests |
| Existing tests | `tests/unit/simulation/test_battle_state_serialization.py` | Battle state round-trip tests |
| Existing tests | `tests/integration/strategy/test_planet_serialization.py` | Planet round-trip tests |

## Decisions Log
| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02-23 | Use PersistenceException (not ValidationException) for from_dict errors | from_dict receives external/saved data — this is a persistence boundary, not input validation |
| 2026-02-23 | Create validation helper module | 15 methods × same pattern = worth a helper to reduce boilerplate |
| 2026-02-23 | Skip bad children in collections (log + continue) | One bad planet shouldn't lose entire galaxy — resilient degradation |
| 2026-02-23 | Fail on missing required scalar fields | Missing name/id/location = object can't exist — fail fast |
| 2026-02-23 | Soft dependency on PROJ-170 | Can proceed independently but ideally after PROJ-170 establishes exception patterns |

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log
- Review source: `Reviews/results/2026-02-23_180421_focused_exception-handling-migration-audit/findings/deserialization_report.md`
- PROJ-170: Exception Handling Migration (soft dependency)

---

## Phases

### Phase 1: Validation Helper Infrastructure [Simple]
**Objective:** Create a minimal validation helper to reduce boilerplate across 15 from_dict methods.
**Status:** Not Started

#### Task 1.1: Create deserialization validation helper module [Medium]
**File:** `game/core/validation_helpers.py` (NEW)
**Tests:** `pytest tests/unit/core/test_validation_helpers.py`
- [ ] Create `game/core/validation_helpers.py` with these helpers:
  - `require_keys(data, keys, context)` — raise PersistenceException if any required keys missing
  - `validate_enum(value, enum_class, field_name, context)` — validate and return enum member
  - `validate_positive(value, field_name, context)` — raise if not > 0
  - `validate_non_negative(value, field_name, context)` — raise if < 0
  - `validate_range(value, min_val, max_val, field_name, context)` — raise if outside range
  - `safe_from_dict(from_dict_fn, data, context)` — wrap from_dict call, convert KeyError/TypeError to PersistenceException with chaining
- [ ] Add imports: `from game.core.exceptions import PersistenceException` and `from game.core.error_codes import ErrorCode`
- [ ] All helpers use `ErrorCode.CORRUPT_DATA.value` as the error code
- [ ] All helpers include the `context` string parameter in the error message and exception context dict
- [ ] Add `__all__` exports
**Notes:**

#### Task 1.2: Write tests for validation helpers [Simple]
**File:** `tests/unit/core/test_validation_helpers.py` (NEW)
**Tests:** `pytest tests/unit/core/test_validation_helpers.py`
- [ ] Test `require_keys` — happy path (all keys present, no exception)
- [ ] Test `require_keys` — missing one key → PersistenceException with correct context
- [ ] Test `require_keys` — missing multiple keys → lists all missing
- [ ] Test `validate_enum` — valid enum name → returns member
- [ ] Test `validate_enum` — invalid enum name → PersistenceException with valid_values in context
- [ ] Test `validate_positive` — positive value passes
- [ ] Test `validate_positive` — zero raises
- [ ] Test `validate_positive` — negative raises
- [ ] Test `validate_non_negative` — zero passes
- [ ] Test `validate_non_negative` — negative raises
- [ ] Test `validate_range` — in range passes
- [ ] Test `validate_range` — below min raises with min/max in context
- [ ] Test `validate_range` — above max raises
- [ ] Test `safe_from_dict` — successful call returns result
- [ ] Test `safe_from_dict` — KeyError → PersistenceException with `from e` chaining
- [ ] Test `safe_from_dict` — TypeError → PersistenceException with `from e` chaining
**Notes:**

---

### Phase 2: Galaxy Core (Galaxy, StarSystem, WarpPoint) [Medium]
**Objective:** Add validation to the galaxy deserialization chain. These are nested: Galaxy → StarSystem → WarpPoint/Star/Planet.
**Status:** Not Started

#### Task 2.1: Validate WarpPoint.from_dict() [Simple]
**File:** `game/strategy/data/galaxy.py:35-41`
**Tests:** `pytest tests/unit/strategy/galaxy/test_warp_point_validation.py`
- [ ] Add `require_keys(data, ['destination_id', 'location'], 'WarpPoint')` at start of method
- [ ] Wrap `hex_from_dict(data['location'])` in try/except, convert to PersistenceException with context
- [ ] Write test: missing destination_id → PersistenceException
- [ ] Write test: missing location → PersistenceException
- [ ] Write test: malformed location dict (e.g. missing 'q') → PersistenceException
- [ ] Write test: valid data still works (regression)
**Notes:** 2 required fields. Simplest method — good warmup.

#### Task 2.2: Validate StarSystem.from_dict() [Medium]
**File:** `game/strategy/data/galaxy.py:77-93`
**Tests:** `pytest tests/unit/strategy/galaxy/test_star_system_validation.py`
- [ ] Add `require_keys(data, ['name', 'global_location'], 'StarSystem')` at start
- [ ] Wrap nested Star.from_dict() calls — if one star fails, log warning and skip (don't lose entire system)
- [ ] Wrap nested WarpPoint.from_dict() calls — if one fails, log warning and skip
- [ ] Wrap nested Planet.from_dict() calls — if one planet fails, log warning and skip
- [ ] Write test: missing name → PersistenceException mentioning 'StarSystem'
- [ ] Write test: missing global_location → PersistenceException
- [ ] Write test: one bad star in list → system loads without that star (logged warning)
- [ ] Write test: valid data still works (regression)
**Notes:** Decision: skip bad children with logging, fail on missing scalars.

#### Task 2.3: Validate Galaxy.from_dict() [Medium]
**File:** `game/strategy/data/galaxy.py:879-928`
**Tests:** `pytest tests/unit/strategy/galaxy/test_galaxy_validation.py`
- [ ] Add `require_keys(data, ['radius'], 'Galaxy')` at start
- [ ] Add `validate_positive(data['radius'], 'radius', 'Galaxy')`
- [ ] Wrap each system entry — validate 'coord' and 'system' keys exist in each sys_entry
- [ ] If one system fails to deserialize, log warning and skip (don't lose entire galaxy)
- [ ] Write test: missing radius → PersistenceException
- [ ] Write test: radius <= 0 → PersistenceException
- [ ] Write test: system entry missing 'coord' → PersistenceException or skipped with warning
- [ ] Write test: valid data still works (regression)
**Notes:** Galaxy.from_dict() rebuilds indexes after deserialization. Validation must run before indexing.

---

### Phase 3: Celestial Bodies (Star, Spectrum, Planet) [Medium]
**Objective:** Add validation to Star, Spectrum, and Planet deserialization.
**Status:** Not Started

#### Task 3.1: Validate Spectrum.from_dict() [Simple]
**File:** `game/strategy/data/stars.py:62-75`
**Tests:** `pytest tests/unit/strategy/stars/test_spectrum_validation.py`
- [ ] Add `require_keys(data, ['gamma_ray', 'xray', 'ultraviolet', 'blue', 'green', 'red', 'infrared', 'microwave', 'radio'], 'Spectrum')`
- [ ] Add `validate_non_negative()` for each of the 9 spectrum fields
- [ ] Write test: missing any one band → PersistenceException
- [ ] Write test: negative spectrum value → PersistenceException
- [ ] Write test: valid data still works
**Notes:** 9 required float fields, all >= 0.

#### Task 3.2: Validate Star.from_dict() [Medium]
**File:** `game/strategy/data/stars.py:123-138`
**Tests:** `pytest tests/unit/strategy/stars/test_star_validation.py`
- [ ] Add `require_keys(data, ['name', 'mass', 'diameter_hexes', 'temperature', 'luminosity', 'spectrum', 'star_type', 'color', 'age', 'location'], 'Star')`
- [ ] Replace `StarType[data['star_type']]` with `validate_enum(data['star_type'], StarType, 'star_type', 'Star')`
- [ ] Add `validate_positive()` for mass, temperature, luminosity, age
- [ ] Wrap `Spectrum.from_dict()` with `safe_from_dict()` or try/except with context
- [ ] Wrap `hex_from_dict()` with error context
- [ ] Write test: missing name → PersistenceException
- [ ] Write test: invalid star_type enum → PersistenceException listing valid values
- [ ] Write test: negative mass → PersistenceException
- [ ] Write test: valid data still works
**Notes:** 10 required fields.

#### Task 3.3: Validate Planet.from_dict() [Complex]
**File:** `game/strategy/data/planet.py:357-420`
**Tests:** `pytest tests/unit/strategy/planet/test_planet_validation.py`
- [ ] Add `require_keys(data, ['name', 'location', 'orbit_distance', 'mass', 'radius', 'surface_area', 'density', 'surface_gravity', 'surface_pressure', 'surface_temperature', 'surface_water', 'tectonic_activity', 'magnetic_field', 'planet_type'], 'Planet')`
- [ ] Replace `PlanetType[data['planet_type']]` with `validate_enum(data['planet_type'], PlanetType, 'planet_type', 'Planet')`
- [ ] Add `validate_positive()` for mass, radius, surface_area, density, surface_gravity
- [ ] Add `validate_non_negative()` for orbit_distance, surface_pressure, surface_water
- [ ] Wrap facility deserialization in try/except — skip bad facilities with warning log
- [ ] Wrap population deserialization in try/except — skip bad populations with warning log
- [ ] Write test: missing name → PersistenceException
- [ ] Write test: invalid planet_type → PersistenceException
- [ ] Write test: negative mass → PersistenceException
- [ ] Write test: bad facility in list → facility skipped, planet loads
- [ ] Write test: valid data still works (regression with existing test_planet_serialization.py)
**Notes:** 14 required fields. Planet has nested facility and population sub-objects.

---

### Phase 4: Empire & Fleet (Empire, Fleet, ShipInstance) [Medium]
**Objective:** Add validation to the empire/fleet deserialization chain.
**Status:** Not Started

#### Task 4.1: Validate ShipInstance.from_dict() [Simple]
**File:** `game/strategy/data/ship_instance.py:632-652`
**Tests:** `pytest tests/unit/strategy/ship_instance/test_validation.py`
- [ ] Add `require_keys(data, ['instance_id', 'design_id', 'name', 'owner_id'], 'ShipInstance')`
- [ ] Write test: missing instance_id → PersistenceException
- [ ] Write test: missing design_id → PersistenceException
- [ ] Write test: valid data still works (regression with existing tests)
**Notes:** 4 required fields, rest have .get() defaults. Simple.

#### Task 4.2: Validate Fleet.from_dict() [Complex]
**File:** `game/strategy/data/fleet.py:343-417`
**Tests:** `pytest tests/unit/strategy/fleet/test_fleet_validation.py`
- [ ] Add `require_keys(data, ['id', 'owner_id'], 'Fleet')`
- [ ] Wrap `OrderType[order_data['type']]` with `validate_enum()` — currently crashes on invalid order type
- [ ] Wrap `ShipInstance.from_dict()` calls — skip bad ships with warning log
- [ ] Wrap order restoration in try/except — skip bad orders with warning log
- [ ] Write test: missing id → PersistenceException
- [ ] Write test: missing owner_id → PersistenceException
- [ ] Write test: invalid OrderType → PersistenceException
- [ ] Write test: bad ship in ships list → ship skipped, fleet loads
- [ ] Write test: valid data still works (regression with existing tests)
**Notes:** Fleet has complex order restoration with multiple format variants. Validate the enum conversion; don't deep-validate every order variant.

#### Task 4.3: Validate Empire.from_dict() [Medium]
**File:** `game/strategy/data/empire.py:168-225`
**Tests:** `pytest tests/unit/strategy/empire/test_empire_validation.py`
- [ ] Add `require_keys(data, ['id', 'name', 'color'], 'Empire')`
- [ ] Wrap `RaceConfig.from_dict()` call with `safe_from_dict()` or try/except with context
- [ ] Wrap `Fleet.from_dict()` calls — skip bad fleets with warning log
- [ ] Write test: missing id → PersistenceException
- [ ] Write test: missing name → PersistenceException
- [ ] Write test: bad fleet in list → fleet skipped, empire loads
- [ ] Write test: valid data still works
**Notes:** Empire already handles missing planets gracefully. Main gap is required field validation and fleet error isolation.

---

### Phase 5: Simulation State (ShipState, ComponentState, Event, DesignMetadata) [Simple]
**Objective:** Add validation to simulation battle state and remaining leaf methods.
**Status:** Not Started

#### Task 5.1: Validate ComponentState.from_dict() [Simple]
**File:** `game/simulation/battle_state.py:50-59`
**Tests:** `pytest tests/unit/simulation/test_battle_state_validation.py`
- [ ] Add `require_keys(data, ['component_id', 'current_hp', 'max_hp', 'is_active', 'layer'], 'ComponentState')`
- [ ] Add `validate_non_negative(data['current_hp'], 'current_hp', 'ComponentState')`
- [ ] Add `validate_positive(data['max_hp'], 'max_hp', 'ComponentState')`
- [ ] Write test: missing component_id → PersistenceException
- [ ] Write test: negative current_hp → PersistenceException
- [ ] Write test: valid data still works (regression with existing tests)
**Notes:** 5 required fields.

#### Task 5.2: Validate ShipState.from_dict() [Medium]
**File:** `game/simulation/battle_state.py:146-174`
**Tests:** `pytest tests/unit/simulation/test_battle_state_validation.py`
- [ ] Add `require_keys(data, ['ship_id', 'name', 'ship_class', 'theme_id', 'team_id', 'color', 'ai_strategy', 'position', 'velocity', 'angle', 'current_hp', 'max_hp', 'current_shields', 'max_shields'], 'ShipState')`
- [ ] Validate `data['color']` is a sequence of length >= 3
- [ ] Validate `data['position']` is a sequence of length >= 2
- [ ] Validate `data['velocity']` is a sequence of length >= 2
- [ ] Wrap `ComponentState.from_dict()` calls — skip bad components with warning log
- [ ] Write test: missing ship_id → PersistenceException
- [ ] Write test: invalid color format (not a list/tuple) → PersistenceException
- [ ] Write test: valid data still works (regression with existing tests)
**Notes:** 14 required fields. Has tuple conversions.

#### Task 5.3: Validate Event.from_dict() [Simple]
**File:** `game/strategy/events/event_log.py:40-50`
**Tests:** `pytest tests/unit/strategy/events/test_event_validation.py`
- [ ] Add `require_keys(data, ['event_type', 'category', 'turn', 'empire_id', 'message'], 'Event')`
- [ ] Write test: missing event_type → PersistenceException
- [ ] Write test: valid data still works
**Notes:** 5 required fields.

#### Task 5.4: Validate DesignMetadata.from_dict() [Simple]
**File:** `game/strategy/data/design_metadata.py:58-79`
**Tests:** `pytest tests/unit/strategy/data/test_design_metadata_validation.py`
- [ ] Add `require_keys(data, ['design_id', 'name'], 'DesignMetadata')`
- [ ] Write test: missing design_id → PersistenceException
- [ ] Write test: valid data still works
**Notes:** Only 2 required fields. Rest already have .get() defaults.

---

## Verification Checklist

### Project Start (REQUIRED)
- [ ] Run full test suite: `pytest tests/ -n 12` — all tests pass (establishes baseline)

### After Each Phase
- [ ] Run `pytest tests/ --testmon` — all affected tests pass
- [ ] Run targeted tests for modified modules
- [ ] Verify existing round-trip serialization tests still pass

### Final Verification
- [ ] Run full test suite: `pytest tests/ -n 12` (NOT --testmon, full verification)
- [ ] Load an existing save file — verify no crashes
- [ ] Corrupt a save file manually (remove a field) — verify PersistenceException with clear message
- [ ] Verify all PersistenceException messages include: which class, which field, what was wrong

---

## Audit Log
| Cycle | Date | Findings | Resolution |
|-------|------|----------|------------|
| 1 | | | |

## Completion Checklist
- [ ] Phase 1 complete (validation helpers + tests)
- [ ] Phase 2 complete (Galaxy/StarSystem/WarpPoint)
- [ ] Phase 3 complete (Star/Spectrum/Planet)
- [ ] Phase 4 complete (Empire/Fleet/ShipInstance)
- [ ] Phase 5 complete (ShipState/ComponentState/Event/DesignMetadata)
- [ ] All tests passing
- [ ] Existing serialization tests still pass (regression)
- [ ] ~60-80 new validation tests added
- [ ] Audit passed
- [ ] User verified
