# Phase 3: Storage Aggregation

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-75 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Calculate empire storage capacity from storage components

---

## Tasks

### Task 3.1: Write TDD tests for EmpireStorageAbility [Simple]
**File:** `tests/unit/simulation/abilities/test_empire_storage.py` (NEW)
**Tests:** `pytest tests/unit/simulation/abilities/test_empire_storage.py -v`

- [x] Create test file with TestEmpireStorageAbility class
- [x] Test: ability creation with resource_type and capacity
- [x] Test: ability recalculation with modifiers
- [x] Test: ability in registry

**Notes:** 10 tests covering creation, defaults, non-dict data, recalculate, primary value, UI rows, all resource types, and registry integration.

---

### Task 3.2: Create EmpireStorageAbility [Simple]
**File:** `game/simulation/components/abilities/harvester.py`
**Tests:** `pytest tests/unit/simulation/abilities/test_empire_storage.py -v`

- [x] Create `EmpireStorageAbility` class extending Ability
- [x] Add to ABILITY_REGISTRY in `game/simulation/components/abilities/__init__.py`

**Notes:** Added to harvester.py alongside ResourceHarvesterAbility. Registered as "EmpireStorage" in ABILITY_REGISTRY.

---

### Task 3.3: Write TDD tests for storage aggregation [Simple]
**File:** `tests/unit/strategy/engine/test_harvesting_engine.py`
**Tests:** `pytest tests/unit/strategy/engine/test_harvesting_engine.py -v`

- [x] Test: recalculate_storage with single storage facility
- [x] Test: recalculate_storage with multiple facilities
- [x] Test: recalculate_storage with multiple resource types
- [x] Test: recalculate_storage sets empire.max_storage correctly
- [x] Test: non-operational facility storage not counted

**Notes:** 9 tests in TestStorageAggregation class. Also updated existing overflow test to include storage facility.

---

### Task 3.4: Add storage aggregation to HarvestingEngine [Simple]
**File:** `game/strategy/engine/harvesting_engine.py`
**Tests:** `pytest tests/unit/strategy/engine/test_harvesting_engine.py -v`

- [x] Add `recalculate_storage(empires: List[Empire]) -> None` method
- [x] Call recalculate_storage at start of process_harvesting

**Notes:** Added recalculate_storage + _aggregate_empire_storage + _collect_storage_from_facility + _get_storage_info + _lookup_storage_in_registry. Supports both inline abilities and registry lookup.

---

### Task 3.5: Add storage components to JSON [Simple]
**File:** `data/components.json`
**Tests:** Manual verification - start game and check registry

- [x] Add `resource_vault_metals` (capacity: 10000)
- [x] Add `resource_vault_organics` (capacity: 10000)
- [x] Add `resource_vault_vapors` (capacity: 10000)
- [x] Add `resource_vault_radioactives` (capacity: 5000)
- [x] Add `resource_vault_exotics` (capacity: 2500)
- [x] All with `allowed_vehicle_types: ["Planetary Complex"]`
- [x] All with appropriate `resource_cost` fields

**Notes:** All 5 vaults added with StructuralIntegrity and CrewRequired abilities. Resource costs scale with rarity.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 4
