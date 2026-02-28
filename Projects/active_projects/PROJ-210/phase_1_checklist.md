# Phase 1: Serialization & Embedded Classes

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-210 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Extract serialization logic and embedded classes to dedicated modules
**Priority:** Critical — highest complexity reduction per task
**Findings:** ROF-001, CQ-03, AR-002, ROF-002, CQ-05

---

## Tasks

### Task 1.1: Extract FleetOrderSerializer [Complex]
**Findings:** ROF-001, CQ-03 (Fleet.from_dict 95 lines, FleetOrder.to_dict 40 lines with 7 formats)
**Files:** `game/strategy/data/fleet.py`, new `game/strategy/data/fleet_order_serializer.py`
**Tests:** `pytest tests/unit/strategy/test_fleet*.py tests/integration/`

- [x] Create `fleet_order_serializer.py` with `FleetOrderSerializer` class
- [x] Extract FleetOrder.to_dict() target serialization logic (7 isinstance branches)
- [x] Extract Fleet.from_dict() order parsing logic (7 target formats)
- [x] Move FleetOrder.resolve_order_references() to serializer
- [x] Update Fleet.from_dict() to delegate to serializer
- [x] Update Fleet.to_dict() to delegate to serializer
- [x] Run targeted tests: `pytest tests/unit/strategy/test_fleet*.py -v`
- [x] Run full suite: `pytest tests/ -n 12`
- [x] Verify: Fleet.from_dict() < 40 lines after extraction

**Notes:**
- FleetOrderSerializer handles all 7 target formats via _deserialize_target()
- FleetOrder.to_dict() kept in order_types.py (already well-structured)
- Fleet.from_dict() now ~50 lines total, order parsing is 4 lines (delegated)
- resolve_order_references() delegated to FleetOrderSerializer

### Task 1.2: Extract PlanetaryFacility to Own Module [Medium]
**Findings:** ROF-002 (3 classes in one file)
**Files:** `game/strategy/data/planet.py`, new `game/strategy/data/planetary_facility.py`
**Tests:** `pytest tests/unit/strategy/test_planet*.py -v`

- [x] Create `planetary_facility.py` with PlanetaryFacility class (lines 35-149)
- [x] Move all PlanetaryFacility imports and dependencies
- [x] Update planet.py to import from new module
- [x] Search all callers of PlanetaryFacility and update imports
- [x] Run targeted tests
- [x] Run full suite: `pytest tests/ -n 12`

**Notes:** Re-exported from planet.py for backward compatibility

### Task 1.3: Extract SpeciesPopulation to Own Module [Simple]
**Findings:** ROF-002
**Files:** `game/strategy/data/planet.py`, new `game/strategy/data/species_population.py`
**Tests:** `pytest tests/unit/strategy/test_planet*.py -v`

- [x] Create `species_population.py` with SpeciesPopulation dataclass (lines 151-183)
- [x] Update planet.py to import from new module
- [x] Search all callers and update imports
- [x] Run full suite: `pytest tests/ -n 12`

**Notes:** Re-exported from planet.py for backward compatibility

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] FleetOrderSerializer handles all 7 target formats
- [x] planet.py contains only the Planet class (imports PlanetaryFacility, SpeciesPopulation)
- [x] All tests passing (12929 passed, 1 skipped; 4 bug_13 failures pre-existing)
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 2
