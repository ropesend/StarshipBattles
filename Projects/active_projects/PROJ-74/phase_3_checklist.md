# Phase 3: ResupplyEngine Core

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-74 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Create engine to process fuel generation at facilities

---

## Tasks

### Task 3.1: Write TDD tests for ResupplyEngine [Medium]
**File:** `tests/unit/strategy/engine/test_resupply_engine.py` (NEW)
**Tests:** `pytest tests/unit/strategy/engine/test_resupply_engine.py`

- [x] Create test file with necessary imports and fixtures
- [x] Write `test_engine_requires_registries_strict_di`
- [x] Write `test_process_fuel_generation_adds_to_facility`
- [x] Write `test_generation_respects_max_storage`
- [x] Write `test_non_operational_facility_no_generation`
- [x] Write `test_facility_without_synthesizer_no_generation`
- [x] Verify: All tests fail (TDD red phase)

**Notes:** 14 total tests written including extra edge cases (energy generator, multiple empires, already full, empty inputs, accumulation, dataclass validation)

---

### Task 3.2: Create ResupplyEngine class [Medium]
**File:** `game/strategy/engine/resupply_engine.py` (NEW)
**Tests:** `pytest tests/unit/strategy/engine/test_resupply_engine.py`

- [x] Create new file with imports
- [x] Create ResupplyEvent dataclass
- [x] Create ResupplyEngine class with strict DI
- [x] Implement `process_fuel_generation(self, tick: int, empires) -> List[ResupplyEvent]`:
  - Iterates empires → colonies → facilities
  - Checks is_operational
  - Checks for ResourceGeneration ability with resource="fuel"
  - Adds fuel/100 per tick (spread over 100 ticks per turn)
  - Respects max storage capacity via facility.add_fuel()
  - Returns list of ResupplyEvent
- [x] Verify: All tests from Task 3.1 pass (TDD green phase)

**Notes:** Uses _get_fuel_generation_rate() helper that scans design_data layers for ResourceGeneration abilities with resource="fuel". Uses ShipStatsCalculator._get_ability_list() for consistent ability scanning. Placeholder process_fleet_resupply() for Phase 4.

---

### Task 3.3: Add IResupplyEngine interface [Simple]
**File:** `game/strategy/interfaces/engines.py`
**Tests:** N/A (interface only)

- [x] Add import for ABC if not present
- [x] Add IResupplyEngine interface with process_fuel_generation and process_fleet_resupply
- [x] Update ResupplyEngine to inherit from IResupplyEngine
- [x] Added IResupplyEngine to __all__ exports

**Notes:** Interface follows existing pattern (IResourceEngine, IPopulationEngine etc.)

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Run `pytest tests/ --testmon` - all tests pass
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 4
