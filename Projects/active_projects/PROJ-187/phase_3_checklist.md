# Phase 3: ActionExecutionEngine [Complex]

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-187 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Create the core engine that processes tick-based action orders. Not yet wired into the turn loop — tested in isolation.

---

## Tasks

### Task 3.1: Define IActionExecutionEngine interface [Simple]
**File:** `game/strategy/interfaces/engines.py`
**Tests:** N/A (interface only)

- [ ] Add `IActionExecutionEngine` ABC with method: `process_action_ticks(empires, galaxy, tick, component_registry=None, all_empires=None) -> List[ActionTickResult]`
- [ ] Add to `__all__` list

**Notes:**

### Task 3.2: Define ACTION_ORDER_TYPES and MOVEMENT_ORDER_TYPES constants [Simple]
**File:** `game/strategy/data/fleet.py`
**Tests:** N/A (constants only)

- [ ] Define `ACTION_ORDER_TYPES: frozenset` = `{COLONIZE, TRANSFER, LOAD_POPULATION, UNLOAD_POPULATION, JOIN_FLEET, IMPLODE_PLANET, STELLERATE_STAR, OPEN_WARP_POINT, CLOSE_WARP_POINT, CREATE_DYSON_SPHERE, SELF_DESTRUCT}`
- [ ] Define `MOVEMENT_ORDER_TYPES: frozenset` = `{MOVE, MOVE_TO_FLEET, WARP}`
- [ ] These exclude BUILD (persistent, handled by ProductionEngine)

**Notes:**

### Task 3.3: Implement ActionExecutionEngine [Complex]
**File:** `game/strategy/engine/action_execution_engine.py` (new)
**Tests:** `pytest tests/unit/strategy/engine/test_action_execution_engine.py` (new)

- [ ] Create `ActionTickResult` dataclass: `fleet_id, order_type, action_completed: bool, fleet_consumed: bool, execution_progress: int, action_time: int`
- [ ] Create `ActionExecutionEngine` class with DI: `__init__(self, order_processor, action_time_resolver)`
- [ ] Implement `process_action_ticks(empires, galaxy, tick, component_registry=None, all_empires=None)`:
  1. Iterate all empires -> fleets (copy list since fleets may be consumed)
  2. Skip fleets with speed <= 0
  3. Compute interval = `int(100 // fleet.speed)`, safety floor to 1
  4. Skip if `tick % interval != 0`
  5. Get current order; skip if None, or type in MOVEMENT_ORDER_TYPES, or BUILD
  6. Increment `order.execution_progress += 1`
  7. Resolve `action_time` via `ActionTimeResolver`
  8. If `execution_progress >= action_time`: delegate to `order_processor` methods
  9. Return list of `ActionTickResult`
- [ ] Handle fleet consumption: after action executes, check if fleet was removed
- [ ] Handle BUILD order auto-pop: check if `fleet.construction_queue` is empty on BUILD orders

**Notes:**

### Task 3.4: Write comprehensive unit tests [Medium]
**File:** `tests/unit/strategy/engine/test_action_execution_engine.py` (new)
**Tests:** `pytest tests/unit/strategy/engine/test_action_execution_engine.py`

- [ ] Test progress accumulates correctly over ticks
- [ ] Test action executes when progress reaches threshold (action_time=1)
- [ ] Test multi-tick action (action_time=3) takes 3 action ticks
- [ ] Test speed-5 fleet completes action_time=1 on tick 20
- [ ] Test speed-1 fleet completes action_time=1 on tick 100
- [ ] Test speed-0 fleet is skipped
- [ ] Test MOVE/MOVE_TO_FLEET/WARP/BUILD orders are skipped
- [ ] Test fleet consumed by action (e.g., stellerate star) is handled
- [ ] Test order popped after action completes
- [ ] Test multi-order chain: first action completes, second becomes active

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `pytest tests/ --testmon` passes
- [ ] ActionExecutionEngine fully tested in isolation (not yet wired into TurnEngine)
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
