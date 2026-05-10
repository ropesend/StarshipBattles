# Phase 2: Harvesting Engine

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-75 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Create engine to extract planetary resources to empire pool

---

## Tasks

### Task 2.1: Write TDD tests for HarvestingEngine [Medium]
**File:** `tests/unit/strategy/engine/test_harvesting_engine.py` (NEW)
**Tests:** `pytest tests/unit/strategy/engine/test_harvesting_engine.py -v`

- [x] Create test file with TestHarvestingEngine class
- [x] Test: single facility harvesting extracts resources
- [x] Test: harvest amount = base_rate * planet quality
- [x] Test: planet resource quantity reduced by harvest amount
- [x] Test: empire resource_pool increased by harvest amount
- [x] Test: multiple harvesters on same planet sum correctly
- [x] Test: planet resource depletion (quantity goes to 0, not negative)
- [x] Test: storage overflow handling (excess discarded)
- [x] Test: non-operational facility skipped
- [x] Test: facility without harvester ability skipped
- [x] Test: empty colonies list handled

**Notes:** 16 tests total including additional edge cases: zero quantity, zero quality, missing resource type, multiple resource types, registry-based lookup, empty empires list.

---

### Task 2.2: Create EmpireHarvesterAbility [Simple]
**File:** `game/simulation/components/abilities/harvester.py`
**Tests:** `pytest tests/unit/simulation/abilities/test_empire_harvester.py -v`

- [x] SKIPPED: Existing ResourceHarvesterAbility already has resource_type and base_harvest_rate fields
- [x] SKIPPED: No new ability class needed - HarvestingEngine reads abilities directly from design_data
- [x] SKIPPED: Already registered in ABILITY_REGISTRY as "ResourceHarvester"

**Notes:** Design called for a new EmpireHarvesterAbility, but the existing ResourceHarvesterAbility already stores resource_type and base_harvest_rate. The HarvestingEngine scans facility design_data for ResourceHarvester abilities directly, avoiding unnecessary abstraction.

---

### Task 2.3: Create HarvestingEngine class [Medium]
**File:** `game/strategy/engine/harvesting_engine.py` (NEW)
**Tests:** `pytest tests/unit/strategy/engine/test_harvesting_engine.py -v`

- [x] Create `HarvestingEngine` class following PopulationEngine pattern
- [x] Implement `__init__(self, *, registries: GameRegistries = None)`
- [x] Implement `process_harvesting(empires: List[Empire]) -> None`
- [x] Add logging for harvest events
- [x] Implements IHarvestingEngine interface

**Notes:** Supports both inline abilities in design_data and registry-based component ID lookup. Follows exact pattern from ResupplyEngine for scanning facility components.

---

### Task 2.4: Add harvesting components to JSON [Simple]
**File:** `data/components.json`
**Tests:** Manual verification - start game and check registry

- [x] Update `metal_harvester` component (base_rate: 100)
- [x] Update `organic_harvester` component (base_rate: 100)
- [x] Update `vapor_harvester` component (base_rate: 100)
- [x] Update `radioactive_harvester` component (base_rate: 50)
- [x] Update `exotic_harvester` component (base_rate: 25)
- [x] All with `allowed_vehicle_types: ["Planetary Complex"]`
- [x] All with appropriate `resource_cost` fields

**Notes:** Components already existed with lower base_harvest_rate values. Updated rates and resource_cost values to match the economy scale. Named metal_harvester (not metals_harvester) per existing convention.

---

### Task 2.5: Integrate HarvestingEngine into TurnEngine [Simple]
**File:** `game/strategy/engine/turn_engine.py`
**Tests:** `pytest tests/integration/strategy/turn_engine/test_harvesting.py -v`

- [x] Write integration test in `tests/integration/strategy/turn_engine/test_harvesting.py` (NEW)
- [x] Add `_harvesting_engine` property with lazy initialization
- [x] Call `harvesting_engine.process_harvesting(empires)` at turn start
- [x] Add IHarvestingEngine interface to `game/strategy/interfaces/engines.py`
- [x] Added harvesting_engine constructor parameter for DI

**Notes:** 4 integration tests: mock call verification, full E2E, ordering (harvesting before production), and storage cap.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 3
