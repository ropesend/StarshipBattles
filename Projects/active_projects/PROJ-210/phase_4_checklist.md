# Phase 4: FleetOrderProcessor Decomposition

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-210 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Decompose FleetOrderProcessor (648 lines) into focused order handlers
**Priority:** Major — prevents regression from PROJ-87's decomposition work
**Findings:** AR-003, CX-03, ROF-007

---

## Tasks

### Task 4.1: Extract Order Handler Pattern [Complex]
**Findings:** AR-003 (FleetOrderProcessor is 648 lines with mixed validation/execution)
**Files:** `game/strategy/engine/fleet_order_processor.py`, new handler modules
**Tests:** `pytest tests/unit/strategy/test_fleet_order*.py tests/integration/ -v`

- [ ] Inventory all order processing methods (COLONIZE, JOIN_FLEET, BUILD, MOVE, etc.)
- [ ] Design OrderHandler interface/protocol
- [ ] Extract process_colonize() (109 lines) → ColonizeOrderHandler
- [ ] Extract process_join_fleet() → JoinFleetOrderHandler
- [ ] Extract process_build() → BuildOrderHandler
- [ ] Extract superweapon processing → SuperweaponOrderHandler
- [ ] Refactor FleetOrderProcessor to dispatch to handlers
- [ ] Run targeted tests
- [ ] Run full suite: `pytest tests/ -n 12`
- [ ] Verify: FleetOrderProcessor.py < 200 lines (dispatcher only)

**Notes:** This follows the same CommandHandlerRegistry pattern already established in PROJ-87 for GameSession command dispatch. Reuse that pattern.

### Task 4.2: Separate Order Validation from Execution [Medium]
**Findings:** AR-003 (process_colonize mixes validation and mutation)
**Files:** Order handler modules from Task 4.1
**Tests:** `pytest tests/unit/strategy/test_fleet_order*.py -v`

- [ ] For each handler, separate validate() from execute()
- [ ] Validation returns success/error without side effects
- [ ] Execution only runs after validation passes
- [ ] Run tests

### Task 4.3: Extract FleetOrder Queue Manager [Simple]
**Findings:** ROF-004, ROF-007
**Files:** `game/strategy/data/fleet.py`, new `game/strategy/data/fleet_order_queue.py`
**Tests:** `pytest tests/unit/strategy/test_fleet*.py -v`

- [ ] Create FleetOrderQueue class managing `orders: List[FleetOrder]`
- [ ] Move: add_order, clear_orders, get_current_order, pop_order from Fleet
- [ ] Move: path reset logic on clear/pop
- [ ] Move: execution_progress tracking
- [ ] Update Fleet to use FleetOrderQueue
- [ ] Run tests

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] FleetOrderProcessor.py < 200 lines (dispatcher)
- [ ] Each order type has its own handler class
- [ ] Validation separated from execution
- [ ] Fleet order queue is encapsulated
- [ ] All tests passing (7,353 baseline)
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 5
