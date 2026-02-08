# Phase 2: Harvesting Engine

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-75 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Create engine to extract planetary resources to empire pool

---

## Tasks

### Task 2.1: Write TDD tests for HarvestingEngine [Medium]
**File:** `tests/unit/strategy/engine/test_harvesting_engine.py` (NEW)
**Tests:** `pytest tests/unit/strategy/engine/test_harvesting_engine.py -v`

- [ ] Create test file with TestHarvestingEngine class
- [ ] Test: single facility harvesting extracts resources
- [ ] Test: harvest amount = base_rate * planet quality
- [ ] Test: planet resource quantity reduced by harvest amount
- [ ] Test: empire resource_pool increased by harvest amount
- [ ] Test: multiple harvesters on same planet sum correctly
- [ ] Test: planet resource depletion (quantity goes to 0, not negative)
- [ ] Test: storage overflow handling (excess discarded)
- [ ] Test: non-operational facility skipped
- [ ] Test: facility without harvester ability skipped
- [ ] Test: empty colonies list handled

**Notes:**

---

### Task 2.2: Create EmpireHarvesterAbility [Simple]
**File:** `game/simulation/components/abilities/harvester.py`
**Tests:** `pytest tests/unit/simulation/abilities/test_empire_harvester.py -v`

- [ ] Write tests in `tests/unit/simulation/abilities/test_empire_harvester.py` (NEW)
- [ ] Create `EmpireHarvesterAbility` class extending Ability:
  ```python
  class EmpireHarvesterAbility(Ability):
      """Extracts planetary resources to empire pool each turn."""

      def __init__(self, component, data: Dict[str, Any]):
          super().__init__(component, data)
          self.resource_type = data.get('resource_type', '')
          self.base_rate = data.get('base_rate', 0.0)
          self._base_rate = self.base_rate

      def recalculate(self) -> None:
          modifier = self.get_effective_stat('harvest_mult', 1.0)
          self.base_rate = self._base_rate * modifier
  ```
- [ ] Add to ABILITY_REGISTRY in `game/simulation/components/abilities/__init__.py`

**Notes:**

---

### Task 2.3: Create HarvestingEngine class [Medium]
**File:** `game/strategy/engine/harvesting_engine.py` (NEW)
**Tests:** `pytest tests/unit/strategy/engine/test_harvesting_engine.py -v`

- [ ] Create `HarvestingEngine` class following PopulationEngine pattern
- [ ] Implement `__init__(self, *, registries: GameRegistries = None)`
- [ ] Implement `process_harvesting(empires: List[Empire]) -> None`:
  - Iterate: empire -> colonies -> facilities -> abilities
  - For each EmpireHarvesterAbility:
    - Calculate: `harvest = base_rate * planet.resources[type]['quality']`
    - available = planet.resources[type]['quantity']
    - actual_harvest = min(harvest, available)
    - Deduct from planet: `planet.resources[type]['quantity'] -= actual_harvest`
    - Add to empire: `empire.add_resources(type, actual_harvest)`
- [ ] Add logging for harvest events

**Notes:**

---

### Task 2.4: Add harvesting components to JSON [Simple]
**File:** `data/components.json`
**Tests:** Manual verification - start game and check registry

- [ ] Add `metals_harvester` component (base_rate: 100)
- [ ] Add `organics_harvester` component (base_rate: 100)
- [ ] Add `vapors_harvester` component (base_rate: 100)
- [ ] Add `radioactives_harvester` component (base_rate: 50)
- [ ] Add `exotics_harvester` component (base_rate: 25)
- [ ] All with `allowed_vehicle_types: ["Planetary Complex"]`
- [ ] All with appropriate `resource_cost` fields

**Notes:**

---

### Task 2.5: Integrate HarvestingEngine into TurnEngine [Simple]
**File:** `game/strategy/engine/turn_engine.py`
**Tests:** `pytest tests/integration/strategy/turn_engine/test_harvesting.py -v`

- [ ] Write integration test in `tests/integration/strategy/turn_engine/test_harvesting.py` (NEW)
- [ ] Add `_harvesting_engine` property with lazy initialization
- [ ] Call `harvesting_engine.process_harvesting(empires)` at turn start
- [ ] Add interface to `game/strategy/interfaces/engines.py` if needed

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 3
