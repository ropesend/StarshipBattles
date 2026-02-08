# Phase 5: TurnEngine Integration

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-74 5`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Wire ResupplyEngine into turn processing

---

## Tasks

### Task 5.1: Write integration tests [Medium]
**File:** `tests/integration/strategy/turn_engine/test_resupply.py` (NEW)
**Tests:** `pytest tests/integration/strategy/turn_engine/test_resupply.py`

- [ ] Create test file with fixtures for empire, colony, fleet, facility

- [ ] Write `test_turn_processes_fuel_generation`:
  - Create colony with fuel synthesizer facility
  - Process one turn
  - Verify fuel accumulated in facility

- [ ] Write `test_turn_processes_fleet_resupply`:
  - Create colony with fuel in facility
  - Create fleet at colony location with partial fuel
  - Process one turn
  - Verify fleet refueled

- [ ] Write `test_resupply_before_movement_gives_fuel`:
  - Create fleet with low fuel at resupply location
  - Give fleet move order
  - Process turn
  - Verify fleet moved (was refueled before movement)

- [ ] Write `test_full_turn_resupply_and_movement`:
  - Create complete scenario: empire, colony, facility, fleet
  - Process multiple turns
  - Verify fuel generation, resupply, and movement all work together

- [ ] Verify: All tests fail initially (no integration yet)

**Notes:**

---

### Task 5.2: Add resupply_engine property to TurnEngine [Simple]
**File:** `game/strategy/engine/turn_engine.py`
**Tests:** `pytest tests/unit/strategy/turn_engine/`

- [ ] Add import for ResupplyEngine and IResupplyEngine:
  ```python
  from game.strategy.engine.resupply_engine import ResupplyEngine
  if TYPE_CHECKING:
      from game.strategy.interfaces.engines import IResupplyEngine
  ```

- [ ] Add parameter to `__init__` (around line 95):
  ```python
  resupply_engine: Optional['IResupplyEngine'] = None,
  ```

- [ ] Add instance variable:
  ```python
  self._resupply_engine: Optional['IResupplyEngine'] = resupply_engine
  ```

- [ ] Add property with lazy initialization (follow existing pattern ~line 200):
  ```python
  @property
  def resupply_engine(self) -> 'IResupplyEngine':
      """Return resupply engine, lazily creating default if not injected."""
      if self._resupply_engine is None:
          self._resupply_engine = ResupplyEngine(registries=self._registries)
      return self._resupply_engine
  ```

- [ ] Verify: Property works correctly

**Notes:**

---

### Task 5.3: Integrate into _process_tick [Simple]
**File:** `game/strategy/engine/turn_engine.py`
**Tests:** `pytest tests/integration/strategy/turn_engine/test_resupply.py`

- [ ] Find `_process_tick()` method (around line 254)
- [ ] Find Phase 0 resource consumption section (around line 269)
- [ ] Add resupply phases after resource consumption:
  ```python
  # --- Phase 0a: Fuel generation at facilities ---
  self.resupply_engine.process_fuel_generation(tick, empires)

  # --- Phase 0b: Fleet resupply from facilities ---
  self.resupply_engine.process_fleet_resupply(tick, empires, galaxy)
  ```

- [ ] Verify: All integration tests pass

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Run `pytest tests/ --testmon` - all tests pass
- [ ] Run `pytest tests/ -n 12` - full suite passes
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 6
