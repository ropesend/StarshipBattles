# Phase 3: ActionExecutionEngine [Complex]

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-187 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Create the core engine that processes tick-based action orders. Not yet wired into the turn loop — tested in isolation.

---

## Tasks

### Task 3.1: Define IActionExecutionEngine interface [Simple]
**File:** `game/strategy/interfaces/engines.py`
**Tests:** N/A (interface only)

- [x] Add `IActionExecutionEngine` ABC with method: `process_action_ticks(empires, galaxy, tick, component_registry=None, all_empires=None) -> List[ActionTickResult]`
- [x] Add to `__all__` list

**Notes:** Added interface with full docstring following existing pattern.

### Task 3.2: Define ACTION_ORDER_TYPES and MOVEMENT_ORDER_TYPES constants [Simple]
**File:** `game/strategy/data/fleet.py`
**Tests:** N/A (constants only)

- [x] Define `ACTION_ORDER_TYPES: frozenset` = `{COLONIZE, TRANSFER, LOAD_POPULATION, UNLOAD_POPULATION, JOIN_FLEET, IMPLODE_PLANET, STELLERATE_STAR, OPEN_WARP_POINT, CLOSE_WARP_POINT, CREATE_DYSON_SPHERE, SELF_DESTRUCT}`
- [x] Define `MOVEMENT_ORDER_TYPES: frozenset` = `{MOVE, MOVE_TO_FLEET, WARP}`
- [x] These exclude BUILD (persistent, handled by ProductionEngine)

**Notes:** Added as frozensets immediately after OrderType enum.

### Task 3.3: Implement ActionExecutionEngine [Complex]
**File:** `game/strategy/engine/action_execution_engine.py` (new)
**Tests:** `pytest tests/unit/strategy/engine/test_action_execution_engine.py` (new)

- [x] Create `ActionTickResult` dataclass: `fleet_id, order_type, action_completed: bool, fleet_consumed: bool, execution_progress: int, action_time: int`
- [x] Create `ActionExecutionEngine` class with DI: `__init__(self, order_processor, action_time_resolver)`
- [x] Implement `process_action_ticks(empires, galaxy, tick, component_registry=None, all_empires=None)`:
  1. Iterate all empires -> fleets (copy list since fleets may be consumed)
  2. Skip fleets with speed <= 0
  3. Compute interval = `int(100 // fleet.speed)`, safety floor to 1
  4. Skip if `tick % interval != 0`
  5. Get current order; skip if None, or type in MOVEMENT_ORDER_TYPES, or BUILD
  6. Increment `order.execution_progress += 1`
  7. Resolve `action_time` via `ActionTimeResolver`
  8. If `execution_progress >= action_time`: delegate to `order_processor` methods
  9. Return list of `ActionTickResult`
- [x] Handle fleet consumption: after action executes, check if fleet was removed
- [x] Handle BUILD order auto-pop: check if `fleet.construction_queue` is empty on BUILD orders

**Notes:** Implemented with full IActionExecutionEngine interface. Uses ActionTimeResolver statically.

### Task 3.4: Write comprehensive unit tests [Medium]
**File:** `tests/unit/strategy/engine/test_action_execution_engine.py` (new)
**Tests:** `pytest tests/unit/strategy/engine/test_action_execution_engine.py`

- [x] Test progress accumulates correctly over ticks
- [x] Test action executes when progress reaches threshold (action_time=1)
- [x] Test multi-tick action (action_time=3) takes 3 action ticks
- [x] Test speed-5 fleet completes action_time=1 on tick 20
- [x] Test speed-1 fleet completes action_time=1 on tick 100
- [x] Test speed-0 fleet is skipped
- [x] Test MOVE/MOVE_TO_FLEET/WARP/BUILD orders are skipped
- [x] Test fleet consumed by action (e.g., stellerate star) is handled
- [x] Test order popped after action completes
- [x] Test multi-order chain: first action completes, second becomes active

**Notes:** 31 tests covering all requirements + additional edge cases.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] `pytest tests/` passes (12,446 passed, 1 skipped)
- [x] ActionExecutionEngine fully tested in isolation (not yet wired into TurnEngine)
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
