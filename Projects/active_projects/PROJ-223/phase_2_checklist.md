# Phase 2: Leaf Type Round-Trip Coverage

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-223 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Cover all simple (non-nested or minimally-nested) serializable types with field-level round-trip tests.

---

## Tasks

### Task 2.1: Spectrum round-trip tests [Simple]
**File:** `tests/integration/save_load/test_roundtrip_stars.py` (NEW)
**Tests:** `pytest tests/integration/save_load/test_roundtrip_stars.py`

- [x] Test to_dict includes all 9 bands
- [x] Test from_dict restores all 9 bands
- [x] Test round-trip with float precision tolerance

**Notes:** 5 tests in TestSpectrumRoundTrip class.

### Task 2.2: Star round-trip tests [Simple]
**File:** `tests/integration/save_load/test_roundtrip_stars.py` (same file)
**Tests:** `pytest tests/integration/save_load/test_roundtrip_stars.py`

- [x] Test all Star fields (name, mass, radius_hexes, temperature, luminosity, spectrum, star_type, color, age, location)
- [x] Test color tuple→list conversion
- [x] Test HexCoord location round-trip

**Notes:** 7 tests in TestStarRoundTrip class. Also tests star_type enum and nested spectrum.

### Task 2.3: StormEffect and Storm round-trip tests [Simple]
**File:** `tests/integration/save_load/test_roundtrip_storms.py` (NEW)
**Tests:** `pytest tests/integration/save_load/test_roundtrip_storms.py`

- [x] Test StormEffect all 5 fields + defaults for missing
- [x] Test Storm all fields including nested StormEffect
- [x] Test hex_offsets list of HexCoords round-trip

**Notes:** 7 tests across TestStormEffectRoundTrip and TestStormRoundTrip.

### Task 2.4: WarpPoint round-trip tests [Simple]
**File:** `tests/integration/save_load/test_roundtrip_galaxy.py` (NEW)
**Tests:** `pytest tests/integration/save_load/test_roundtrip_galaxy.py`

- [x] Test destination_id and location round-trip

**Notes:** 3 tests in TestWarpPointRoundTrip.

### Task 2.5: SpeciesPopulation round-trip tests [Simple]
**File:** `tests/integration/save_load/test_roundtrip_planet.py` (NEW)
**Tests:** `pytest tests/integration/save_load/test_roundtrip_planet.py`

- [x] Test all 3 fields: race_id, count, happiness
- [x] Test happiness default (0.5) when missing

**Notes:** 4 tests in TestSpeciesPopulationRoundTrip.

### Task 2.6: PlanetaryFacility round-trip tests [Simple]
**File:** `tests/integration/save_load/test_roundtrip_planet.py` (same)
**Tests:** `pytest tests/integration/save_load/test_roundtrip_planet.py`

- [x] Test all 7 fields
- [x] Test resource_levels with various values
- [x] Test empty resource_levels

**Notes:** 5 tests in TestPlanetaryFacilityRoundTrip.

### Task 2.7: RaceConfig round-trip tests [Simple]
**File:** `tests/integration/save_load/test_roundtrip_empire.py` (NEW)
**Tests:** `pytest tests/integration/save_load/test_roundtrip_empire.py`

- [x] Test all 25+ fields
- [x] Test atmosphere_preferences defaults
- [x] Test optional field defaults

**Notes:** 5 tests in TestRaceConfigRoundTrip.

### Task 2.8: Event and EventLog round-trip tests [Simple]
**File:** `tests/integration/save_load/test_roundtrip_events.py` (NEW)
**Tests:** `pytest tests/integration/save_load/test_roundtrip_events.py`

- [x] Test Event all 6 fields
- [x] Test EventLog with multiple events
- [x] Test empty EventLog

**Notes:** 9 tests across TestEventRoundTrip and TestEventLogRoundTrip.

### Task 2.9: GameConfig and PlayerConfig round-trip tests [Simple]
**File:** `tests/integration/save_load/test_roundtrip_config.py` (NEW)
**Tests:** `pytest tests/integration/save_load/test_roundtrip_config.py`

- [x] Test PlayerConfig all fields including optional
- [x] Test GameConfig all fields including nested players
- [x] Test color tuple→list conversion

**Notes:** 10 tests across TestPlayerConfigRoundTrip and TestGameConfigRoundTrip.

### Task 2.10: DesignMetadata round-trip tests [Simple]
**File:** `tests/integration/save_load/test_roundtrip_designs.py` (NEW)
**Tests:** `pytest tests/integration/save_load/test_roundtrip_designs.py`

- [x] Test all 12 fields
- [x] Test optional field defaults

**Notes:** 4 tests in TestDesignMetadataRoundTrip.

### Task 2.11: NodeState round-trip tests [Simple]
**File:** `tests/integration/save_load/test_roundtrip_research.py` (NEW)
**Tests:** `pytest tests/integration/save_load/test_roundtrip_research.py`

- [x] Test all 3 fields
- [x] Test defaults for missing fields

**Notes:** 4 tests in TestNodeStateRoundTrip.

### Task 2.12: FleetOrder round-trip tests (all 7 target formats) [Medium]
**File:** `tests/integration/save_load/test_roundtrip_orders.py` (NEW)
**Tests:** `pytest tests/integration/save_load/test_roundtrip_orders.py`

- [x] Test all 7 target serialization formats
- [x] Test execution_progress preservation
- [x] Test all OrderType enum values

**Notes:** 26 tests (15 + parametrized OrderType). All 7 target formats covered.

### Task 2.13: Run full test suite [Simple]
**Tests:** `pytest tests/ -n 12`

- [x] All tests pass, no regressions

**Notes:** 13,619 passed, 2 skipped.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Run `pytest tests/ -n 12` — 13,619 passed, 2 skipped
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
