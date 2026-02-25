# Phase 3: Update Test Mocks [Medium]

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-191 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Update test files that use bare `Mock()` or `MagicMock()` for Empire, Planet, Fleet, and Facility objects to use `spec=ConcreteClass` or real objects.

---

## Tasks

### Task 3.1: Update test_empire_economy_calculator.py [Medium]
**File:** `tests/unit/strategy/engine/test_empire_economy_calculator.py`
**Tests:** `pytest tests/unit/strategy/engine/test_empire_economy_calculator.py`

- [ ] Change `empire = Mock()` (L45-49) to `Mock(spec=Empire)` or construct real `Empire(0, 'Test', (255,0,0))`
- [ ] Change `facility = Mock()` (L64-66) to `Mock(spec=PlanetaryFacility)` with required attrs
- [ ] Change `colony = Mock()` instances to `Mock(spec=Planet)` or use real Planet
- [ ] Change `ship = Mock()` to `Mock(spec=ShipInstance)` where used
- [ ] Change `fleet = Mock()` to `Mock(spec=Fleet)` where used
- [ ] Ensure all required attributes are explicitly set on mocks
- [ ] Run tests — all pass

**Notes:** `test_population_engine.py` uses real Empire/Planet objects — follow that pattern where practical.

### Task 3.2: Update test_harvesting_engine.py [Medium]
**File:** `tests/unit/strategy/engine/test_harvesting_engine.py`
**Tests:** `pytest tests/unit/strategy/engine/test_harvesting_engine.py`

- [ ] Update `_make_empire()` helper to use real Empire or `Mock(spec=Empire)`
- [ ] Update planet/colony mocks to use spec
- [ ] Update facility mocks to use spec
- [ ] Run tests — all pass

**Notes:**

### Task 3.3: Audit and fix remaining test files [Medium]
**Files:** All test files in `tests/unit/strategy/engine/`, `tests/unit/strategy/services/`, `tests/unit/strategy/validation/`
**Tests:** `pytest tests/unit/strategy/ -n 12`

- [ ] Scan `tests/unit/strategy/engine/` for bare Mock/MagicMock on Empire/Planet/Fleet/Facility
- [ ] Update `test_superweapon_*.py` mocks if needed
- [ ] Update `test_fleet_order_processor.py` mocks if needed
- [ ] Update `test_maintenance_*.py` mocks if needed
- [ ] Scan `tests/unit/strategy/services/` for relevant mock updates
- [ ] Scan `tests/unit/strategy/validation/` for relevant mock updates
- [ ] Run `pytest tests/unit/strategy/ -n 12` — all pass
- [ ] Run `pytest tests/ -n 12` — baseline maintained

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `pytest tests/ -n 12` — baseline maintained (12699+ passed)
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
