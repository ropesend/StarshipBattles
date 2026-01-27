# Phase 2: ResourceManagementEngine

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-36 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Extract resource consumption logic (~70 lines) to dedicated engine

---

## Tasks

### Task 2.1: Create ResourceManagementEngine file [Simple]
**File:** `game/strategy/engine/resource_management_engine.py` (NEW)
**Tests:** `pytest tests/unit/strategy/test_resource_management_engine.py`

- [ ] Create new file with module docstring:
  ```python
  """
  ResourceManagementEngine - Per-Turn Resource Consumption

  PROJ-36: Extracted from TurnEngine to handle resource consumption.

  Responsibilities:
  - Process per-turn resource consumption (1/100th per tick)
  - Detect resource depletion
  - Auto-disable components when resources depleted
  """
  ```
- [ ] Add imports: `typing`, `dataclasses`, `game.core.logger`, `game.core.registry`
- [ ] Create `ResourceDepletion` dataclass:
  ```python
  @dataclass
  class ResourceDepletion:
      ship_name: str
      resource_type: str
      components_disabled: List[str]
  ```
- [ ] Create `ResourceManagementEngine` class with empty `__init__` (stateless)
- [ ] Move `_process_per_turn_resources` logic (TurnEngine lines 254-283)
- [ ] Move `_auto_disable_components_for_resource` logic (TurnEngine lines 285-321)
- [ ] Add public method: `process_per_turn_consumption(tick, empires) -> List[ResourceDepletion]`
- [ ] Verify: File follows patterns in FleetMovementEngine

**Notes:**

---

### Task 2.2: Update TurnEngine to delegate resources [Simple]
**File:** `game/strategy/engine/turn_engine.py`
**Tests:** `pytest tests/unit/strategy/test_turn_engine.py -k resource`

- [ ] Add TYPE_CHECKING import for ResourceManagementEngine
- [ ] Add `_resource_engine: Optional['ResourceManagementEngine'] = None` to __init__
- [ ] Add lazy property `resource_engine`:
  ```python
  @property
  def resource_engine(self) -> 'ResourceManagementEngine':
      if self._resource_engine is None:
          from game.strategy.engine.resource_management_engine import ResourceManagementEngine
          self._resource_engine = ResourceManagementEngine()
      return self._resource_engine
  ```
- [ ] Replace `self._process_per_turn_resources(tick, empires)` call (line 226) with:
  ```python
  self.resource_engine.process_per_turn_consumption(tick, empires)
  ```
- [ ] Remove `_process_per_turn_resources` method (lines 254-283)
- [ ] Remove `_auto_disable_components_for_resource` method (lines 285-321)
- [ ] Remove unused imports (registry if no longer needed)
- [ ] Verify: TurnEngine compiles without errors

**Notes:**

---

### Task 2.3: Create/migrate resource tests [Simple]
**File:** `tests/unit/strategy/test_resource_management_engine.py` (NEW)
**Tests:** `pytest tests/unit/strategy/test_resource_management_engine.py`

- [ ] Create new test file with imports and fixtures
- [ ] Move `TestPerTurnResources` tests from test_turn_engine.py:
  - `test_consumes_resources_each_tick`
  - `test_skips_non_combat_ships`
  - `test_spreads_consumption_over_100_ticks`
- [ ] Move auto-disable tests:
  - `test_auto_disables_on_depletion`
  - `test_finds_components_with_per_turn_trigger`
  - `test_disables_matching_resource_type`
- [ ] Add test: Resource depletion cascade (multiple resources deplete same tick)
- [ ] Add test: Component already disabled, auto-disable called again (idempotent)
- [ ] Add test: Zero cost per-turn resource (should never disable)
- [ ] Add test: Rounding error check (100 ticks, verify no phantom loss)
- [ ] Update test imports to use ResourceManagementEngine
- [ ] Verify: All tests pass

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Run `pytest tests/unit/strategy/test_turn_engine.py` - passes
- [ ] Run `pytest tests/unit/strategy/test_resource_management_engine.py` - passes
- [ ] Run `pytest tests/integration/` - passes
- [ ] TurnEngine reduced by ~70 more lines
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 3
