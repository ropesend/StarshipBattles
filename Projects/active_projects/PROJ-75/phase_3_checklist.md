# Phase 3: Storage Aggregation

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-75 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Calculate empire storage capacity from storage components

---

## Tasks

### Task 3.1: Write TDD tests for EmpireStorageAbility [Simple]
**File:** `tests/unit/simulation/abilities/test_empire_storage.py` (NEW)
**Tests:** `pytest tests/unit/simulation/abilities/test_empire_storage.py -v`

- [ ] Create test file with TestEmpireStorageAbility class
- [ ] Test: ability creation with resource_type and capacity
- [ ] Test: ability recalculation with modifiers
- [ ] Test: ability in registry

**Notes:**

---

### Task 3.2: Create EmpireStorageAbility [Simple]
**File:** `game/simulation/components/abilities/harvester.py`
**Tests:** `pytest tests/unit/simulation/abilities/test_empire_storage.py -v`

- [ ] Create `EmpireStorageAbility` class extending Ability:
  ```python
  class EmpireStorageAbility(Ability):
      """Provides storage capacity for empire resource pool."""

      def __init__(self, component, data: Dict[str, Any]):
          super().__init__(component, data)
          self.resource_type = data.get('resource_type', '')
          self.capacity = data.get('capacity', 0.0)
          self._base_capacity = self.capacity

      def recalculate(self) -> None:
          modifier = self.get_effective_stat('storage_mult', 1.0)
          self.capacity = self._base_capacity * modifier
  ```
- [ ] Add to ABILITY_REGISTRY in `game/simulation/components/abilities/__init__.py`

**Notes:**

---

### Task 3.3: Write TDD tests for storage aggregation [Simple]
**File:** `tests/unit/strategy/engine/test_harvesting_engine.py`
**Tests:** `pytest tests/unit/strategy/engine/test_harvesting_engine.py -v`

- [ ] Test: recalculate_storage with single storage facility
- [ ] Test: recalculate_storage with multiple facilities
- [ ] Test: recalculate_storage with multiple resource types
- [ ] Test: recalculate_storage sets empire.max_storage correctly
- [ ] Test: non-operational facility storage not counted

**Notes:**

---

### Task 3.4: Add storage aggregation to HarvestingEngine [Simple]
**File:** `game/strategy/engine/harvesting_engine.py`
**Tests:** `pytest tests/unit/strategy/engine/test_harvesting_engine.py -v`

- [ ] Add `recalculate_storage(empires: List[Empire]) -> None` method:
  - For each empire, reset max_storage to empty dict
  - Iterate colonies -> facilities -> abilities
  - For each EmpireStorageAbility:
    - Add capacity to empire.max_storage[resource_type]
- [ ] Call recalculate_storage at start of process_harvesting

**Notes:**

---

### Task 3.5: Add storage components to JSON [Simple]
**File:** `data/components.json`
**Tests:** Manual verification - start game and check registry

- [ ] Add `resource_vault_metals` (capacity: 10000)
- [ ] Add `resource_vault_organics` (capacity: 10000)
- [ ] Add `resource_vault_vapors` (capacity: 10000)
- [ ] Add `resource_vault_radioactives` (capacity: 5000)
- [ ] Add `resource_vault_exotics` (capacity: 2500)
- [ ] All with `allowed_vehicle_types: ["Planetary Complex"]`
- [ ] All with appropriate `resource_cost` fields

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 4
