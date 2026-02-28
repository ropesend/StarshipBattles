# Phase 3: Planet Decomposition

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-210 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Separate Planet's entangled responsibilities into focused modules
**Priority:** Major — reduces Planet from 5 domains to 1 (physical + coordinates)
**Findings:** ROF-003, ROF-005, ROF-008, CQ-05, AR-006

---

## Tasks

### Task 3.1: Extract Shared ConstructionQueue Abstraction [Medium]
**Findings:** ROF-003 (identical construction_queue on Fleet, Planet, PlanetaryFacility)
**Files:** `fleet.py`, `planet.py`, `build_queue_source.py`, new `construction_queue.py`
**Tests:** `pytest tests/unit/strategy/test_build*.py tests/unit/strategy/test_fleet*.py tests/unit/strategy/test_planet*.py -v`

- [ ] Analyze construction_queue usage in Fleet, Planet, PlanetaryFacility
- [ ] Create `ConstructionQueue` class with shared queue management
- [ ] Replace inline `construction_queue: List[Dict]` with ConstructionQueue instances
- [ ] Update build_queue_source.py to work with new abstraction
- [ ] Run targeted tests
- [ ] Run full suite: `pytest tests/ -n 12`

### Task 3.2: Extract Planet Resource/Economy Methods [Medium]
**Findings:** ROF-005 (add_production, can_build_type, has_space_shipyard scattered across Planet)
**Files:** `game/strategy/data/planet.py`, new `game/strategy/data/planet_economy.py`
**Tests:** `pytest tests/unit/strategy/test_planet*.py -v`

- [ ] Create `planet_economy.py` with PlanetEconomy helper
- [ ] Move: add_production(), can_build_type(), has_space_shipyard property
- [ ] Move: resource tracking (resources dict, add_fuel concerns)
- [ ] Update Planet to delegate to PlanetEconomy
- [ ] Update callers
- [ ] Run full suite: `pytest tests/ -n 12`

### Task 3.3: Extract Planet Grid Topology [Simple]
**Findings:** ROF-008 (diameter_hexes, occupied_hexes with hex geometry in Planet)
**Files:** `game/strategy/data/planet.py`
**Tests:** `pytest tests/unit/strategy/test_planet*.py -v`

- [ ] Assess if occupied_hexes can be moved to planet_physics.py or a grid helper
- [ ] Move hex geometry calculations (hex_circle_filled usage) out of Planet
- [ ] Planet should store diameter_hexes but delegate hex calculations
- [ ] Run tests

### Task 3.4: Consolidate PlanetaryFacility Component Scanning [Simple]
**Findings:** AR-006 (PlanetaryFacility.get_max_fuel_storage iterates design_data components directly)
**Files:** `planetary_facility.py` (extracted in Phase 1), `component_inspector.py`
**Tests:** `pytest tests/unit/strategy/ -v`

- [ ] Refactor PlanetaryFacility to use component_inspector service
- [ ] Eliminate manual design_data component iteration
- [ ] Run tests

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Planet.py < 300 lines
- [ ] Planet only has: physical properties, coordinates, species list, facility list
- [ ] Economy/production logic extracted to PlanetEconomy
- [ ] ConstructionQueue is a shared abstraction
- [ ] All tests passing (7,353 baseline)
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 4
