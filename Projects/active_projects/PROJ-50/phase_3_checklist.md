# Phase 3: Strategy Layer Services

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-50 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Remove fallbacks from strategy services

---

## Tasks

### Task 3.1: Update ShipStatsCalculator [Simple]
**File:** `game/strategy/services/ship_stats_calculator.py`
**Tests:** `pytest tests/unit/strategy/test_ship_stats_calculator*.py -v`

- [x] Remove import of `get_default_registry_provider` (line 20)
- [x] Remove import of `get_default_registries` (line 19)
- [x] Remove `_get_registries_fallback()` static method (lines 72-90)
- [x] Change constructor: `registries: Optional[GameRegistries] = None` to `registries: GameRegistries`
- [x] Remove fallback in `__init__` (line 68)
- [x] Add validation: `if registries is None: raise TypeError("registries is required")`

**Notes:** Updated test_service_injection.py to test strict DI instead of fallback behavior.

---

### Task 3.2: Update ResourceManagementEngine [Simple]
**File:** `game/strategy/engine/resource_management_engine.py`
**Tests:** `pytest tests/unit/strategy/ -v`

- [x] Remove import of `get_default_registry_provider` (line 17)
- [x] Remove fallback conditional (line ~117)
- [x] Make registries required in constructor
- [x] Add validation

**Notes:** Updated TurnEngine to pass registries with fallback for tests. Updated ResourceManagementEngine test files (conftest.py, test_consumption.py, test_auto_disable.py, test_initialization.py) to use mock_registries fixture.

---

### Additional Work

- [x] Update TurnEngine to accept registries parameter and pass to ResourceManagementEngine
- [x] Update ShipInstance.get_calculated_stats() to get registries with fallback for tests

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Run `pytest tests/unit/strategy/ -v` - all pass (838 passed)
- [x] Run `grep -r "get_default_registry_provider" game/strategy/services/` - returns 0 (only __pycache__)
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 4
