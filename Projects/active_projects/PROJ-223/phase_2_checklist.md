# Phase 2: Leaf Type Round-Trip Coverage

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-223 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Cover all simple (non-nested or minimally-nested) serializable types with field-level round-trip tests.

---

## Tasks

### Task 2.1: Spectrum round-trip tests [Simple]
**File:** `tests/integration/save_load/test_roundtrip_stars.py` (NEW)
**Tests:** `pytest tests/integration/save_load/test_roundtrip_stars.py`

- [ ] Test to_dict includes all 9 bands
- [ ] Test from_dict restores all 9 bands
- [ ] Test round-trip with float precision tolerance

**Notes:**

### Task 2.2: Star round-trip tests [Simple]
**File:** `tests/integration/save_load/test_roundtrip_stars.py` (same file)
**Tests:** `pytest tests/integration/save_load/test_roundtrip_stars.py`

- [ ] Test all Star fields (name, mass, radius_hexes, temperature, luminosity, spectrum, star_type, color, age, location)
- [ ] Test color tuple→list conversion
- [ ] Test HexCoord location round-trip

**Notes:**

### Task 2.3: StormEffect and Storm round-trip tests [Simple]
**File:** `tests/integration/save_load/test_roundtrip_storms.py` (NEW)
**Tests:** `pytest tests/integration/save_load/test_roundtrip_storms.py`

- [ ] Test StormEffect all 5 fields + defaults for missing
- [ ] Test Storm all fields including nested StormEffect
- [ ] Test hex_offsets list of HexCoords round-trip

**Notes:**

### Task 2.4: WarpPoint round-trip tests [Simple]
**File:** `tests/integration/save_load/test_roundtrip_galaxy.py` (NEW)
**Tests:** `pytest tests/integration/save_load/test_roundtrip_galaxy.py`

- [ ] Test destination_id and location round-trip

**Notes:**

### Task 2.5: SpeciesPopulation round-trip tests [Simple]
**File:** `tests/integration/save_load/test_roundtrip_planet.py` (NEW)
**Tests:** `pytest tests/integration/save_load/test_roundtrip_planet.py`

- [ ] Test all 3 fields: race_id, count, happiness
- [ ] Test happiness default (0.5) when missing

**Notes:**

### Task 2.6: PlanetaryFacility round-trip tests [Simple]
**File:** `tests/integration/save_load/test_roundtrip_planet.py` (same)
**Tests:** `pytest tests/integration/save_load/test_roundtrip_planet.py`

- [ ] Test all 7 fields
- [ ] Test resource_levels with various values
- [ ] Test empty resource_levels

**Notes:**

### Task 2.7: RaceConfig round-trip tests [Simple]
**File:** `tests/integration/save_load/test_roundtrip_empire.py` (NEW)
**Tests:** `pytest tests/integration/save_load/test_roundtrip_empire.py`

- [ ] Test all 25+ fields
- [ ] Test atmosphere_preferences defaults
- [ ] Test optional field defaults

**Notes:**

### Task 2.8: Event and EventLog round-trip tests [Simple]
**File:** `tests/integration/save_load/test_roundtrip_events.py` (NEW)
**Tests:** `pytest tests/integration/save_load/test_roundtrip_events.py`

- [ ] Test Event all 6 fields
- [ ] Test EventLog with multiple events
- [ ] Test empty EventLog

**Notes:**

### Task 2.9: GameConfig and PlayerConfig round-trip tests [Simple]
**File:** `tests/integration/save_load/test_roundtrip_config.py` (NEW)
**Tests:** `pytest tests/integration/save_load/test_roundtrip_config.py`

- [ ] Test PlayerConfig all fields including optional
- [ ] Test GameConfig all fields including nested players
- [ ] Test color tuple→list conversion

**Notes:**

### Task 2.10: DesignMetadata round-trip tests [Simple]
**File:** `tests/integration/save_load/test_roundtrip_designs.py` (NEW)
**Tests:** `pytest tests/integration/save_load/test_roundtrip_designs.py`

- [ ] Test all 12 fields
- [ ] Test optional field defaults

**Notes:**

### Task 2.11: NodeState round-trip tests [Simple]
**File:** `tests/integration/save_load/test_roundtrip_research.py` (NEW)
**Tests:** `pytest tests/integration/save_load/test_roundtrip_research.py`

- [ ] Test all 3 fields
- [ ] Test defaults for missing fields

**Notes:**

### Task 2.12: FleetOrder round-trip tests (all 7 target formats) [Medium]
**File:** `tests/integration/save_load/test_roundtrip_orders.py` (NEW)
**Tests:** `pytest tests/integration/save_load/test_roundtrip_orders.py`

- [ ] Test all 7 target serialization formats
- [ ] Test execution_progress preservation
- [ ] Test all OrderType enum values

**Notes:** Fleet/planet refs NOT fully resolved here — that's Phase 4.

### Task 2.13: Run full test suite [Simple]
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
