# PROJ-159: Rewrite Transfer Validator Tests as Integration Tests

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-159` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-159 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Test Infrastructure | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Core Validation Tests | Complete | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Cleanup & Verify | Complete | [phase_3_checklist.md](phase_3_checklist.md) |

## Current State
**Last Updated:** 2026-02-22
**Active Phase:** Complete - Awaiting User Verification
**Last Action:** Completed all 3 phases - old tests deleted, new tests passing
**Next Action:** User review and commit
**Blockers:** None
**Context:**
- Created 13 integration tests replacing 20 failing unit tests
- Tests use real Planet/Fleet objects instead of MagicMock to satisfy is_planet() protocol
- All new tests passing; old test file deleted
- Test count: 11943 passed (+3 from baseline), 19 failed (pre-existing UI issues)

## Overview
Rewrite the 20 failing `test_transfer_validator.py` tests to use real `Planet` and `Fleet` objects instead of `MagicMock`. The current tests fail because `MagicMock(spec=Planet)` doesn't satisfy the `is_planet()` protocol check (`isinstance(obj, IPlanet)` returns `False` for mocks).

## Goals
- Replace failing mock-based unit tests with working integration tests
- Use real `Planet`, `Fleet`, and `ShipInstance` objects
- Consolidate from 30 tests to ~12 core scenarios (remove implementation-detail tests)
- Improve long-term maintainability by testing behavior, not implementation

## Scope
**In:**
- Rewrite `tests/unit/strategy/validation/test_transfer_validator.py` → move to `tests/integration/strategy/`
- Create reusable test fixtures for transfer scenarios
- Delete tests that verify implementation details (validation order, constants existence)

**Out:**
- Modifying `TransferValidator` implementation
- Modifying the `is_planet()` protocol system
- Adding new validation logic

## Key Files
| Component | File Path |
|-----------|-----------|
| Failing tests (DELETE) | `tests/unit/strategy/validation/test_transfer_validator.py` |
| Validator (NO CHANGES) | `game/strategy/validation/transfer_validator.py` |
| Protocol | `game/core/protocols.py:165-189, 326-328` |
| Planet class | `game/strategy/data/planet.py:138-201` |
| Fleet class | `game/strategy/data/fleet.py` |
| Existing patterns | `tests/integration/strategy/test_colonize_logic.py` |
| Ship factory | `tests/conftest.py:272-305` |

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log

---

## Decisions Log
| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02-22 | Use real Planet objects instead of fixing mocks | Protocol-based type checking (`isinstance`) can't work with MagicMock |
| 2026-02-22 | Move to integration tests | Tests need real object graph; fits existing integration test patterns |
| 2026-02-22 | Consolidate to ~12 core tests | Remove implementation-detail tests per CLAUDE.md guidance |
| 2026-02-22 | Use lightweight MockGalaxy pattern | From test_colonize_logic.py - minimal setup, proven pattern |

## Initial Analysis

### Root Cause of Failures
```python
# transfer_validator.py line 72
from game.core.protocols import is_planet, is_fleet

if is_planet(target):  # isinstance(target, IPlanet) - FAILS for MagicMock
    # Planet-specific validation (SKIPPED for mocks!)
```

`MagicMock(spec=Planet)` does not implement `IPlanet` protocol, so `is_planet()` returns `False`.

### Baseline
- **Total tests:** 30
- **Passing:** 10 (constant checks, null checks)
- **Failing:** 20 (all tests involving `is_planet()` check)

## Swarm Findings Summary

### Planet Class Requirements
- Planet is a `@dataclass` with 13 mandatory physical fields
- TransferValidator only uses: `name`, `owner_id`, `location`, `total_population`, `populations`
- Physical fields can use Earth-like defaults

### Fleet Cargo System
- `Fleet.get_fleet_cargo_capacity()` sums capacity from all ships
- Ship capacity from `CargoStorage` ability in design layers
- Can set cargo directly: `ship.cargo_contents["passengers"] = amount`

### Reusable Patterns
- **MockGalaxy**: `tests/integration/strategy/test_colonize_logic.py:32-43`
- **Ship with cargo**: `tests/unit/strategy/engine/test_colonize_population.py:41-67`

---

## Phases

### Phase 1: Create Test Infrastructure [Simple]
**Objective:** Create reusable fixtures and helper functions for transfer tests

#### Task 1.1: Create transfer test conftest [Simple]
**File:** `tests/integration/strategy/transfer/conftest.py` (NEW)
**Tests:** N/A - fixture file
- [x] Create directory `tests/integration/strategy/transfer/`
- [x] Create `conftest.py` with imports
- [x] Add `create_test_planet()` factory:
  ```python
  def create_test_planet(
      name: str = "Test Colony",
      owner_id: int = 0,
      population_count: int = 1000,
      location: HexCoord = HexCoord(0, 0)
  ) -> Planet:
      return Planet(
          name=name, location=location, orbit_distance=1,
          mass=5.972e24, radius=6.371e6, surface_area=5.1e14,
          density=5514.0, surface_gravity=9.81, surface_pressure=101325.0,
          surface_temperature=288.0, surface_water=0.71,
          tectonic_activity=0.3, magnetic_field=1.0,
          owner_id=owner_id,
          populations=[SpeciesPopulation(race_id="human", count=population_count)]
      )
  ```
- [x] Add `create_transport_ship()` using CargoStorage ability pattern
- [x] Add `create_transport_fleet()` combining fleet + ship
- [x] Add `MockGalaxy` class with `get_system_at_location()` method

#### Task 1.2: Add pytest fixtures [Simple]
**File:** `tests/integration/strategy/transfer/conftest.py`
- [x] `@pytest.fixture colonized_planet` (owner_id=0, pop=1000)
- [x] `@pytest.fixture uncolonized_planet` (owner_id=None)
- [x] `@pytest.fixture transport_fleet` (capacity=100, current=0)
- [x] `@pytest.fixture loaded_fleet` (capacity=100, current=50)
- [x] `@pytest.fixture mock_galaxy` with planet at fleet location

---

### Phase 2: Write Core Validation Tests [Medium]
**Objective:** Write ~12 core integration tests covering key validation scenarios

#### Task 2.1: Load validation tests [Simple]
**File:** `tests/integration/strategy/transfer/test_transfer_validation.py` (NEW)
**Tests:** `pytest tests/integration/strategy/transfer/ -v`
- [x] `test_load_passengers_success` - valid load from colony to fleet
- [x] `test_load_fails_when_fleet_full` - NO_CARGO_SPACE error
- [x] `test_load_fails_when_colony_empty` - NO_POPULATION error

#### Task 2.2: Unload validation tests [Simple]
**File:** `tests/integration/strategy/transfer/test_transfer_validation.py`
- [x] `test_unload_passengers_success` - valid unload
- [x] `test_unload_fails_when_fleet_empty` - NO_CARGO_TO_UNLOAD error

#### Task 2.3: General validation tests [Simple]
**File:** `tests/integration/strategy/transfer/test_transfer_validation.py`
- [x] `test_fails_when_fleet_not_at_planet` - NOT_AT_PLANET
- [x] `test_fails_when_planet_uncolonized` - NOT_COLONIZED
- [x] `test_fails_when_fleet_none` - FLEET_NOT_FOUND
- [x] `test_fails_when_planet_none` - TARGET_NOT_FOUND
- [x] `test_fails_with_invalid_direction` - INVALID_DIRECTION
- [x] `test_fails_with_invalid_cargo_type` - INVALID_CARGO_TYPE

#### Task 2.4: Species-specific edge cases [Simple]
**File:** `tests/integration/strategy/transfer/test_transfer_validation.py`
- [x] `test_load_specific_species_success`
- [x] `test_load_specific_species_not_present_fails`

---

### Phase 3: Delete Old Tests and Verify [Simple]
**Objective:** Remove old failing tests, verify full suite passes

#### Task 3.1: Delete old test file [Simple]
**File:** `tests/unit/strategy/validation/test_transfer_validator.py` (DELETE)
**Tests:** `pytest tests/ -k transfer -v`
- [x] Delete `tests/unit/strategy/validation/test_transfer_validator.py`
- [x] Delete empty directory if applicable (kept - contains other valid tests)
- [x] Verify new tests run

#### Task 3.2: Full test suite verification [Simple]
**Tests:** `pytest tests/ -n 12`
- [x] Run full test suite
- [x] Verify no regressions (20 validator failures removed, 19 pre-existing UI failures remain)
- [x] Document final test count: 11943 passed (+3), 19 failed (-20), 2 skipped

---

## Verification
- [x] All phase checklists complete
- [x] All 12+ new integration tests passing (13 tests)
- [x] Old test file deleted
- [x] Full test suite run (19 pre-existing failures unrelated to PROJ-159)
- [ ] Audit passed
- [ ] User verified
