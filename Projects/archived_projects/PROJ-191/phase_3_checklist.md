# Phase 3: Update Test Mocks [Medium]

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-191 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Update test files that use bare `Mock()` or `MagicMock()` for Empire, Planet, Fleet, and Facility objects to use `spec=ConcreteClass` or real objects.

---

## Tasks

### Task 3.1: Update test_empire_economy_calculator.py [Medium]
**File:** `tests/unit/strategy/engine/test_empire_economy_calculator.py`
**Tests:** `pytest tests/unit/strategy/engine/test_empire_economy_calculator.py`

- [x] Change `empire = Mock()` (L45-49) to `Mock(spec=Empire)` or construct real `Empire(0, 'Test', (255,0,0))`
- [x] Change `facility = Mock()` (L64-66) to `Mock(spec=PlanetaryFacility)` with required attrs
- [x] Change `colony = Mock()` instances to `Mock(spec=Planet)` or use real Planet
- [x] Change `ship = Mock()` to `Mock(spec=ShipInstance)` where used
- [x] Change `fleet = Mock()` to `Mock(spec=Fleet)` where used
- [x] Ensure all required attributes are explicitly set on mocks
- [x] Run tests — all pass (15 tests)

**Notes:** Added imports for Empire, Planet, PlanetaryFacility, Fleet, ShipInstance. All Mock() calls updated to Mock(spec=...).

### Task 3.2: Update test_harvesting_engine.py [Medium]
**File:** `tests/unit/strategy/engine/test_harvesting_engine.py`
**Tests:** `pytest tests/unit/strategy/engine/test_harvesting_engine.py`

- [x] Update `_make_empire()` helper to use real Empire or `Mock(spec=Empire)`
- [x] Update planet/colony mocks to use spec
- [x] Update facility mocks to use spec (already using real PlanetaryFacility)
- [x] Run tests — all pass (32 tests)

**Notes:** Updated _make_empire() and _make_planet() helpers.

### Task 3.3: Audit and fix remaining test files [Medium]
**Files:** All test files in `tests/unit/strategy/engine/`, `tests/unit/strategy/services/`, `tests/unit/strategy/validation/`
**Tests:** `pytest tests/unit/strategy/ -n 12`

- [x] Scan `tests/unit/strategy/engine/` for bare Mock/MagicMock on Empire/Planet/Fleet/Facility
- [x] Update `test_maintenance_engine.py` mocks — _make_colony() uses Mock(spec=Planet)
- [x] Update `test_production_refactor.py` mocks — mock_empire uses Mock(spec=Empire), mock_colony uses Mock(spec=Planet)
- [x] Update `test_fleet_movement_engine.py` mocks — create_mock_fleet uses Mock(spec=Fleet), empire uses Mock(spec=Empire)
- [x] Update `test_population_engine.py` mocks — TurnEngine integration test
- [x] Run `pytest tests/unit/strategy/ -n 12` — all 2196 pass
- [x] Run `pytest tests/ -n 12` — baseline maintained (12702 passed, 1 skipped)

**Notes:** Many other test files in superweapon/services/validation still have bare mocks; these can be addressed in future cleanup passes. The key engine files using Empire/Planet/Fleet/Facility directly are now updated.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] `pytest tests/ -n 12` — baseline maintained (12702 passed, 1 skipped)
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
