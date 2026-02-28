# Phase 1: Serialization & Embedded Classes

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-210 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Extract serialization logic and embedded classes to dedicated modules
**Priority:** Critical — highest complexity reduction per task
**Findings:** ROF-001, CQ-03, AR-002, ROF-002, CQ-05

---

## Tasks

### Task 1.1: Extract FleetOrderSerializer [Complex]
**Findings:** ROF-001, CQ-03 (Fleet.from_dict 95 lines, FleetOrder.to_dict 40 lines with 7 formats)
**Files:** `game/strategy/data/fleet.py`, new `game/strategy/data/fleet_order_serializer.py`
**Tests:** `pytest tests/unit/strategy/test_fleet*.py tests/integration/`

- [ ] Create `fleet_order_serializer.py` with `FleetOrderSerializer` class
- [ ] Extract FleetOrder.to_dict() target serialization logic (7 isinstance branches)
- [ ] Extract Fleet.from_dict() order parsing logic (7 target formats)
- [ ] Move FleetOrder.resolve_order_references() to serializer
- [ ] Update Fleet.from_dict() to delegate to serializer
- [ ] Update Fleet.to_dict() to delegate to serializer
- [ ] Run targeted tests: `pytest tests/unit/strategy/test_fleet*.py -v`
- [ ] Run full suite: `pytest tests/ -n 12`
- [ ] Verify: Fleet.from_dict() < 40 lines after extraction

**Notes:** The 7 target formats are: HexCoord, Fleet ref, Planet ref, transfer params, warp params, implosion target, standard. Each needs its own serialization method.

### Task 1.2: Extract PlanetaryFacility to Own Module [Medium]
**Findings:** ROF-002 (3 classes in one file)
**Files:** `game/strategy/data/planet.py`, new `game/strategy/data/planetary_facility.py`
**Tests:** `pytest tests/unit/strategy/test_planet*.py -v`

- [ ] Create `planetary_facility.py` with PlanetaryFacility class (lines 35-149)
- [ ] Move all PlanetaryFacility imports and dependencies
- [ ] Update planet.py to import from new module
- [ ] Search all callers of PlanetaryFacility and update imports
- [ ] Run targeted tests
- [ ] Run full suite: `pytest tests/ -n 12`

### Task 1.3: Extract SpeciesPopulation to Own Module [Simple]
**Findings:** ROF-002
**Files:** `game/strategy/data/planet.py`, new `game/strategy/data/species_population.py`
**Tests:** `pytest tests/unit/strategy/test_planet*.py -v`

- [ ] Create `species_population.py` with SpeciesPopulation dataclass (lines 151-183)
- [ ] Update planet.py to import from new module
- [ ] Search all callers and update imports
- [ ] Run full suite: `pytest tests/ -n 12`

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] FleetOrderSerializer handles all 7 target formats
- [ ] planet.py contains only the Planet class
- [ ] All tests passing (7,353 baseline)
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 2
