# Phase 3: ResupplyEngine Core

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-74 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Create engine to process fuel generation at facilities

---

## Tasks

### Task 3.1: Write TDD tests for ResupplyEngine [Medium]
**File:** `tests/unit/strategy/engine/test_resupply_engine.py` (NEW)
**Tests:** `pytest tests/unit/strategy/engine/test_resupply_engine.py`

- [ ] Create test file with necessary imports and fixtures
- [ ] Write `test_engine_requires_registries_strict_di`:
  ```python
  def test_engine_requires_registries_strict_di():
      """ResupplyEngine must raise TypeError if registries is None."""
      with pytest.raises(TypeError):
          ResupplyEngine(registries=None)
  ```
- [ ] Write `test_process_fuel_generation_adds_to_facility`
- [ ] Write `test_generation_respects_max_storage`
- [ ] Write `test_non_operational_facility_no_generation`
- [ ] Write `test_facility_without_synthesizer_no_generation`
- [ ] Verify: All tests fail (TDD red phase)

**Notes:**

---

### Task 3.2: Create ResupplyEngine class [Medium]
**File:** `game/strategy/engine/resupply_engine.py` (NEW)
**Tests:** `pytest tests/unit/strategy/engine/test_resupply_engine.py`

- [ ] Create new file with imports:
  ```python
  from dataclasses import dataclass
  from typing import List, Optional, TYPE_CHECKING

  from game.core.logger import log_info
  from game.core.registry import GameRegistries

  if TYPE_CHECKING:
      pass
  ```

- [ ] Create ResupplyEvent dataclass:
  ```python
  @dataclass
  class ResupplyEvent:
      """Record of a resupply operation."""
      facility_name: str
      fuel_generated: float
      fuel_transferred: float = 0.0
      fleet_id: Optional[int] = None
  ```

- [ ] Create ResupplyEngine class with strict DI:
  ```python
  class ResupplyEngine:
      """Engine for processing fuel generation and resupply."""

      def __init__(self, *, registries: GameRegistries):
          if registries is None:
              raise TypeError("registries is required for ResupplyEngine")
          self._registries = registries
  ```

- [ ] Implement `process_fuel_generation(self, tick: int, empires) -> List[ResupplyEvent]`:
  - Iterate empires → colonies → facilities
  - Check is_operational
  - Check for ResourceGeneration ability with resource="fuel"
  - Add fuel/100 per tick (spread over 100 ticks per turn)
  - Respect max storage capacity
  - Return list of ResupplyEvent

- [ ] Verify: All tests from Task 3.1 pass (TDD green phase)

**Notes:**

---

### Task 3.3: Add IResupplyEngine interface [Simple]
**File:** `game/strategy/interfaces/engines.py`
**Tests:** N/A (interface only)

- [ ] Add import for ABC if not present
- [ ] Add IResupplyEngine interface:
  ```python
  class IResupplyEngine(ABC):
      """Abstract interface for resupply processing."""

      @abstractmethod
      def process_fuel_generation(
          self,
          tick: int,
          empires: List
      ) -> List:
          """Process fuel generation at facilities."""
          pass

      @abstractmethod
      def process_fleet_resupply(
          self,
          tick: int,
          empires: List,
          galaxy: Any
      ) -> List:
          """Process fuel transfer from facilities to fleets."""
          pass
  ```

- [ ] Update ResupplyEngine to inherit from IResupplyEngine

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Run `pytest tests/ --testmon` - all tests pass
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 4
