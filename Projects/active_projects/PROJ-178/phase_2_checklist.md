# Phase 2: PlanetaryFacility & SpeciesPopulation from_dict

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-178 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Extract inline deserialization into proper `from_dict` classmethods using `require_keys`, matching the codebase pattern.

---

## Tasks

### Task 2.1: Add PlanetaryFacility.from_dict classmethod [Medium]
**File:** `game/strategy/data/planet.py`
**Tests:** `pytest tests/unit/strategy/planet/test_planet_validation.py tests/unit/strategy/data/test_facility_resource_tracking.py tests/unit/strategy/data/test_facility_construction_queue.py`

- [ ] Add `from_dict` classmethod to PlanetaryFacility class (after line 41)
- [ ] Use `require_keys(data, ['instance_id', 'design_id', 'name', 'design_data'], 'PlanetaryFacility')`
- [ ] Update Planet.from_dict facilities loop (lines 418-436) to call `PlanetaryFacility.from_dict(f)`
- [ ] Update exception catching: `except (PersistenceException, KeyError, TypeError) as e:`
- [ ] Add PersistenceException import if not already present in scope
- [ ] Verify all existing facility tests pass

**Notes:**

### Task 2.2: Add SpeciesPopulation.from_dict classmethod [Simple]
**File:** `game/strategy/data/planet.py`
**Tests:** `pytest tests/unit/strategy/planet/test_planet_validation.py tests/unit/strategy/data/test_population_model.py`

- [ ] Find SpeciesPopulation dataclass definition
- [ ] Add `from_dict` classmethod with `require_keys(data, ['race_id', 'count'], 'SpeciesPopulation')`
- [ ] Update Planet.from_dict populations loop (lines 438-452) to call `SpeciesPopulation.from_dict(p)`
- [ ] Update exception catching: `except (PersistenceException, KeyError, TypeError) as e:`
- [ ] Verify all existing population tests pass

**Notes:**

### Task 2.3: Add tests for PlanetaryFacility.from_dict validation [Simple]
**File:** `tests/unit/strategy/planet/test_planet_validation.py` (or new test file)
**Tests:** `pytest tests/unit/strategy/planet/`

- [ ] Test valid data creates PlanetaryFacility
- [ ] Test missing each required key (instance_id, design_id, name, design_data) raises PersistenceException
- [ ] Test optional fields default correctly (is_operational=True, construction_queue=[], resource_levels={})

**Notes:**

### Task 2.4: Add tests for SpeciesPopulation.from_dict validation [Simple]
**File:** `tests/unit/strategy/planet/test_planet_validation.py` (or new test file)
**Tests:** `pytest tests/unit/strategy/planet/`

- [ ] Test valid data creates SpeciesPopulation
- [ ] Test missing required key (race_id, count) raises PersistenceException
- [ ] Test happiness defaults to 0.5

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `pytest tests/unit/strategy/planet/ tests/unit/strategy/data/` passes
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
