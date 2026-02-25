# Phase 4: Wire Into Turn Loop + Eradicate End-of-Turn [Complex]

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-187 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Integrate ActionExecutionEngine into `_process_tick()` as Phase 1.5, remove `_process_end_turn_orders()` entirely, and update FleetMovementEngine to skip action-order fleets.

**WARNING:** This is the highest-risk phase. Must be done atomically with Phase 5 (test migration).

---

## Tasks

### Task 4.1: Add ActionExecutionEngine to TurnEngine [Medium]
**File:** `game/strategy/engine/turn_engine.py`
**Tests:** `pytest tests/unit/strategy/turn_engine/`

- [ ] Add `_action_engine` parameter to `__init__` (optional, default None)
- [ ] Add lazy `action_engine` property (same pattern as other engines, lines 200-250)
- [ ] Default creation: `ActionExecutionEngine(order_processor=self.order_processor, action_time_resolver=ActionTimeResolver())`
- [ ] Add TYPE_CHECKING import for `IActionExecutionEngine`

**Notes:**

### Task 4.2: Add Phase 1.5 to _process_tick() [Medium]
**File:** `game/strategy/engine/turn_engine.py`
**Tests:** `pytest tests/unit/strategy/turn_engine/ && pytest tests/integration/strategy/turn_engine/`

- [ ] After Phase 1 (instant orders, line 354) and before Phase 2 (calculate moves, line 358), add:
  ```python
  # --- Phase 1.5: Action Orders (COLONIZE, TRANSFER, superweapons) ---
  self.action_engine.process_action_ticks(
      empires, galaxy, tick,
      component_registry=getattr(self._registries, 'components', None),
      all_empires=empires
  )
  ```
- [ ] Update docstring for `_process_tick()` to document Phase 1.5
- [ ] Update module-level docstring to reflect new architecture

**Notes:**

### Task 4.3: Remove end-of-turn order processing from process_turn() [Medium]
**File:** `game/strategy/engine/turn_engine.py`
**Tests:** `pytest tests/ --testmon`

- [ ] Delete the end-of-turn loop (lines 272-277):
  ```python
  # DELETE:
  for empire in empires:
      for fleet in list(empire.fleets):
          self._process_end_turn_orders(fleet, empire, galaxy, empires)
  ```
- [ ] Delete `_process_end_turn_orders()` method entirely (lines 368-384)
- [ ] Update `process_turn()` docstring

**Notes:**

### Task 4.4: Update FleetMovementEngine to skip action orders [Simple]
**File:** `game/strategy/engine/fleet_movement_engine.py`
**Tests:** `pytest tests/unit/strategy/ -k "movement"`

- [ ] In `collect_movements()` (lines 176-179), expand BUILD skip to also skip action orders:
  ```python
  from game.strategy.data.fleet import ACTION_ORDER_TYPES
  current_order = fleet.get_current_order()
  if current_order and current_order.type in ACTION_ORDER_TYPES:
      continue
  if current_order and current_order.type == OrderType.BUILD:
      continue
  ```

**Notes:**

### Task 4.5: Remove process_end_turn_orders from FleetOrderProcessor [Medium]
**File:** `game/strategy/engine/fleet_order_processor.py`
**Tests:** `pytest tests/ --testmon`

- [ ] Delete `process_end_turn_orders()` method (lines 575-663)
- [ ] Update module docstring to remove end-of-turn references
- [ ] Keep all individual processing methods: `process_colonize()`, `process_transfer()`, `process_join_fleet()` — now called by ActionExecutionEngine

**Notes:**

### Task 4.6: Update IOrderProcessor interface [Simple]
**File:** `game/strategy/interfaces/engines.py`
**Tests:** `pytest tests/unit/strategy/turn_engine/test_dependency_injection.py`

- [ ] Remove `process_end_turn_orders()` from `IOrderProcessor` abstract class (if present)
- [ ] Keep `process_instant_orders()` (still used for co-located JOIN_FLEET)

**Notes:**

### Task 4.7: Handle BUILD order completion in tick loop [Simple]
**File:** Determine best location during implementation
**Tests:** `pytest tests/ -k "build"`

- [ ] BUILD orders were previously auto-popped at end-of-turn when `construction_queue` was empty
- [ ] Move this logic into ActionExecutionEngine or ProductionEngine
- [ ] Preferred: ActionExecutionEngine checks BUILD on fleet's tick interval and pops when queue empty

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `_process_end_turn_orders()` fully deleted from turn_engine.py
- [ ] `process_end_turn_orders()` fully deleted from fleet_order_processor.py
- [ ] ActionExecutionEngine integrated as Phase 1.5 in tick loop
- [ ] FleetMovementEngine skips action-order fleets
- [ ] Proceed immediately to Phase 5 (test migration)
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
