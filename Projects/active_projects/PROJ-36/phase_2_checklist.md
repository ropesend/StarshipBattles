# Phase 2: ResourceManagementEngine

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-36 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Extract resource consumption logic (~70 lines) to dedicated engine

---

## Tasks

### Task 2.1: Create ResourceManagementEngine file [Simple]
**File:** `game/strategy/engine/resource_management_engine.py` (NEW)
**Tests:** `pytest tests/unit/strategy/test_resource_management_engine.py`

- [x] Create new file with module docstring:
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
- [x] Add imports: `typing`, `dataclasses`, `game.core.logger`, `game.core.registry`
- [x] Create `ResourceDepletion` dataclass:
  ```python
  @dataclass
  class ResourceDepletion:
      ship_name: str
      resource_type: str
      components_disabled: List[str]
  ```
- [x] Create `ResourceManagementEngine` class with empty `__init__` (stateless)
- [x] Move `_process_per_turn_resources` logic (TurnEngine lines 254-283)
- [x] Move `_auto_disable_components_for_resource` logic (TurnEngine lines 285-321)
- [x] Add public method: `process_per_turn_consumption(tick, empires) -> List[ResourceDepletion]`
- [x] Verify: File follows patterns in FleetMovementEngine

**Notes:** Created `game/strategy/engine/resource_management_engine.py` (116 lines) with all resource consumption logic extracted from TurnEngine.

---

### Task 2.2: Update TurnEngine to delegate resources [Simple]
**File:** `game/strategy/engine/turn_engine.py`
**Tests:** `pytest tests/unit/strategy/test_turn_engine.py -k resource`

- [x] Add TYPE_CHECKING import for ResourceManagementEngine
- [x] Add `_resource_engine: Optional['ResourceManagementEngine'] = None` to __init__
- [x] Add lazy property `resource_engine`:
  ```python
  @property
  def resource_engine(self) -> 'ResourceManagementEngine':
      if self._resource_engine is None:
          from game.strategy.engine.resource_management_engine import ResourceManagementEngine
          self._resource_engine = ResourceManagementEngine()
      return self._resource_engine
  ```
- [x] Replace `self._process_per_turn_resources(tick, empires)` call (line 226) with:
  ```python
  self.resource_engine.process_per_turn_consumption(tick, empires)
  ```
- [x] Remove `_process_per_turn_resources` method (lines 254-283)
- [x] Remove `_auto_disable_components_for_resource` method (lines 285-321)
- [x] Remove unused imports (registry if no longer needed)
- [x] Verify: TurnEngine compiles without errors

**Notes:** TurnEngine reduced from 338 to 282 lines (56 lines removed). Total reduction from original 479: 197 lines (41%).

---

### Task 2.3: Create/migrate resource tests [Simple]
**File:** `tests/unit/strategy/test_resource_management_engine.py` (NEW)
**Tests:** `pytest tests/unit/strategy/test_resource_management_engine.py`

- [x] Create new test file with imports and fixtures
- [x] Move `TestPerTurnResources` tests from test_turn_engine.py:
  - `test_consumes_resources_each_tick`
  - `test_skips_non_combat_ships`
  - `test_spreads_consumption_over_100_ticks`
- [x] Move auto-disable tests:
  - `test_auto_disables_on_depletion`
  - `test_finds_components_with_per_turn_trigger`
  - `test_disables_matching_resource_type`
- [x] Add test: Resource depletion cascade (multiple resources deplete same tick)
- [x] Add test: Component already disabled, auto-disable called again (idempotent)
- [x] Add test: Zero cost per-turn resource (should never disable)
- [x] Add test: Rounding error check (100 ticks, verify no phantom loss)
- [x] Update test imports to use ResourceManagementEngine
- [x] Verify: All tests pass

**Notes:** Created `tests/unit/strategy/test_resource_management_engine.py` with 24 tests. Removed `TestPerTurnResources` class from `test_turn_engine.py`. Updated test mocking to use `_resource_engine` instead of patching removed methods.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Run `pytest tests/unit/strategy/test_turn_engine.py` - passes (49 tests)
- [x] Run `pytest tests/unit/strategy/test_resource_management_engine.py` - passes (24 tests)
- [x] Run `pytest tests/integration/` - passes (44 tests)
- [x] TurnEngine reduced by ~70 more lines (56 lines actually, 338→282)
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 3
