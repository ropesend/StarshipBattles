# Phase 5: Type Hints and Interface Cleanup

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-233 5`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Add comprehensive type hints and remove stale `harvesting_engine` parameter from IProductionEngine.

---

## Tasks

### Task 5.1: Add type hints to `production_engine.py` [Simple]
**File:** `game/strategy/engine/production_engine.py`
**Tests:** `pytest tests/unit/strategy/production_engine/ -v`

- [ ] Add `TYPE_CHECKING` block at top of file:
  ```python
  from typing import TYPE_CHECKING
  if TYPE_CHECKING:
      from game.core.registry import GameRegistries
      from game.strategy.data.empire import Empire
      from game.strategy.data.galaxy import Galaxy
      from game.strategy.data.planet import Planet
  ```
- [ ] Type `__init__`: `def __init__(self, registries: Optional['GameRegistries'] = None):`
- [ ] Type `process_construction_tick`:
  - `empires: List['Empire']`
  - `galaxy: Optional['Galaxy']`
- [ ] Type `_process_queue_tick_dynamic`:
  - `empire: 'Empire'`
  - `galaxy: Optional['Galaxy']`
  - `colony_or_fleet: Any` (keep `Any` since it's `Union[Planet, Fleet]` but both are imported conditionally)
- [ ] Type `_validate_queue_item`: `colony_or_fleet: Any`, `galaxy: Optional['Galaxy']`
- [ ] Type `_check_affordability`: `empire: 'Empire'`
- [ ] Type `_log_resource_shortage`: `empire: 'Empire'`, `colony_or_fleet: Any`
- [ ] Type `_apply_resource_consumption`: `empire: 'Empire'`
- [ ] Type `_complete_item`: `empire: 'Empire'`, `colony_or_fleet: Any`, `galaxy: Optional['Galaxy']`
- [ ] Run tests: All pass

**Notes:**

### Task 5.2: Add type hints to `production_spawner.py` [Simple]
**File:** `game/strategy/engine/production_spawner.py`
**Tests:** `pytest tests/unit/strategy/production_engine/test_spawning.py -v`

- [ ] Add `TYPE_CHECKING` block:
  ```python
  from typing import TYPE_CHECKING
  if TYPE_CHECKING:
      from game.core.registry import GameRegistries
      from game.strategy.data.empire import Empire
      from game.strategy.data.galaxy import Galaxy
      from game.strategy.data.planet import Planet
  ```
- [ ] Type `__init__`: `registries: Optional['GameRegistries'] = None`
- [ ] Type all `empire` params as `'Empire'`
- [ ] Type all `galaxy` params as `Optional['Galaxy']`
- [ ] Type all `planet` params as `'Planet'`
- [ ] Type `_resolve_planet_location` return: `-> Tuple[Optional[List], str, Optional[List]]`
- [ ] Run tests: All pass

**Notes:**

### Task 5.3: Remove stale `harvesting_engine` from IProductionEngine [Simple]
**File:** `game/strategy/interfaces/engines.py`
**Tests:** `pytest tests/unit/strategy/interfaces/ tests/unit/strategy/turn_engine/ -v`

- [ ] Remove `harvesting_engine: Any = None` from `process_construction_tick` signature (line 146)
- [ ] Remove `harvesting_engine` from the docstring Args section (line 160)
- [ ] Update the Example line in the class docstring (line 136): remove `harvesting_engine` from call
- [ ] Verify: The actual `ProductionEngine.process_construction_tick` already doesn't have this param (confirmed in PROJ-161)
- [ ] Verify: `TurnEngine._process_tick` does not pass `harvesting_engine` (confirmed: line 463-466 of turn_engine.py only passes `tick, empires, galaxy, save_path=save_path`)

**Notes:**

### Task 5.4: Update mock implementations [Simple]
**Files:** `tests/unit/strategy/mocks/mock_engines.py`, `tests/unit/strategy/interfaces/test_engine_interfaces.py`
**Tests:** `pytest tests/unit/strategy/interfaces/ tests/unit/strategy/turn_engine/test_dependency_injection.py -v`

- [ ] In `tests/unit/strategy/mocks/mock_engines.py`:
  - Remove `harvesting_engine=None` from `process_construction_tick` signature (~line 97-100)
  - Remove `harvesting_engine` from the tuple stored in `process_construction_tick_calls`
  - Update docstring/comment about tracked args (~line 91)
- [ ] In `tests/unit/strategy/interfaces/test_engine_interfaces.py`:
  - Find `MockProductionEngine` class (~line 351-354)
  - Remove `harvesting_engine=None` from `process_construction_tick` signature
- [ ] Run tests: All pass

**Notes:**

### Task 5.5: Final full suite verification [Simple]
**Tests:** `pytest tests/ -n 12`

- [ ] Run full test suite
- [ ] Verify: Same 17 pre-existing failures (none new)
- [ ] Verify: `production_engine.py` is under 600 lines
- [ ] Verify: `production_spawner.py` is under 300 lines
- [ ] Verify: `production_math.py` is under 50 lines

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to indicate project complete
