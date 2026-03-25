# Phase 3: Compound Type Round-Trip Coverage

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-223 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Cover compound types (those containing nested serializable objects) with field-level round-trip tests.

---

## Tasks

### Task 3.1: Planet round-trip tests (with facilities and populations) [Medium]
**File:** `tests/integration/save_load/test_roundtrip_planet.py` (extend)
**Tests:** `pytest tests/integration/save_load/test_roundtrip_planet.py`

- [ ] Test Planet with all 25+ physics/classification fields
- [ ] Test nested facilities and populations round-trip
- [ ] Test resources, atmosphere, construction_queue, owner_id, visual fields
- [ ] Test PlanetType enum round-trip

**Notes:**

### Task 3.2: StarSystem round-trip tests (with all children) [Medium]
**File:** `tests/integration/save_load/test_roundtrip_galaxy.py` (extend)
**Tests:** `pytest tests/integration/save_load/test_roundtrip_galaxy.py`

- [ ] Test StarSystem with stars, warp_points, planets, storms
- [ ] Test region_id optional field
- [ ] Test deserialize_list error isolation

**Notes:**

### Task 3.3: ShipInstance round-trip tests (field-level) [Medium]
**File:** `tests/integration/save_load/test_roundtrip_ships.py` (NEW)
**Tests:** `pytest tests/integration/save_load/test_roundtrip_ships.py`

- [ ] Test all 15 fields including design_data (large nested dict)
- [ ] Test resource_levels, component_toggles, cargo_contents
- [ ] Test registries parameter passed and stored

**Notes:**

### Task 3.4: Fleet round-trip tests (with ships and orders) [Medium]
**File:** `tests/integration/save_load/test_roundtrip_fleet.py` (NEW)
**Tests:** `pytest tests/integration/save_load/test_roundtrip_fleet.py`

- [ ] Test all core fields + nested ships and orders
- [ ] Test path list (HexCoords) round-trip
- [ ] Test registries passed to ShipInstance during from_dict

**Notes:**

### Task 3.5: Empire round-trip tests (with fleets and economy) [Medium]
**File:** `tests/integration/save_load/test_roundtrip_empire.py` (extend)
**Tests:** `pytest tests/integration/save_load/test_roundtrip_empire.py`

- [ ] Test all core fields + nested fleets
- [ ] Test colony_ids, built_ship_designs, counters, economy fields
- [ ] Test optional fields: flag_id, portrait_id, race_config

**Notes:** Colony resolution tested in Phase 4.

### Task 3.6: Galaxy round-trip tests [Medium]
**File:** `tests/integration/save_load/test_roundtrip_galaxy.py` (extend)
**Tests:** `pytest tests/integration/save_load/test_roundtrip_galaxy.py`

- [ ] Test radius, _next_planet_id, systems array
- [ ] Test spatial indexes rebuilt after from_dict

**Notes:**

### Task 3.7: ResearchTracker round-trip tests [Simple]
**File:** `tests/integration/save_load/test_roundtrip_research.py` (extend)
**Tests:** `pytest tests/integration/save_load/test_roundtrip_research.py`

- [ ] Test all ResearchTracker fields
- [ ] Test node_states with multiple entries
- [ ] Test empty tracker

**Notes:**

### Task 3.8: Run full test suite [Simple]
**Tests:** `pytest tests/ -n 12`

- [ ] All tests pass, no regressions

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Run `pytest tests/ -n 12` — all tests pass
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
