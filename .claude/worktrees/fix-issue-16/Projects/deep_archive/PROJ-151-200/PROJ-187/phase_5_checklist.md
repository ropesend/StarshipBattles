# Phase 5: Test Migration [Complex]

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-187 5`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Update all tests that depend on end-of-turn order execution to work with tick-based execution.

**KEY BEHAVIOR CHANGE:** Orders that previously executed instantly at end-of-turn now require action ticks. A fleet with speed 5 gets action ticks every 20 sub-ticks. A 1-cost action completes on tick 20. Tests calling `process_turn()` should mostly work since actions still complete within a turn. Tests calling `process_end_turn_orders()` directly must be rewritten.

---

## Tasks

### Task 5.1: Find all affected tests [Medium]
**Tests:** Grep + analysis

- [x] Grep for `process_end_turn_orders` in all test files — these call the deleted method directly
- [x] Grep for `_process_end_turn_orders` in all test files
- [x] Grep for tests that mock `process_end_turn_orders` on order processor
- [x] Grep for tests checking order execution timing/sequence after `process_turn()`
- [x] Create categorized list of all affected test files

**Notes:**
Phase 4 already migrated tests. Analysis shows:
- All `process_end_turn_orders` calls are to `FleetOrderProcessor` (method still exists)
- No tests call `TurnEngine._process_end_turn_orders` (deleted method)
- References in comments/docstrings explain migration
- Files affected: test_advanced_fleet_orders.py, test_colonize_logic.py, test_dependency_injection.py, mock_engines.py, test_engine_interfaces.py, test_fleet_order_processor.py, test_action_execution_engine.py, test_build_order_processor.py

### Task 5.2: Update direct-call tests [Medium]
**Files:** Various test files identified in 5.1
**Tests:** Run each updated test file individually

- [x] Tests that called `process_end_turn_orders()` directly must switch to:
  - Call `action_engine.process_action_ticks()` at correct tick, OR
  - Call individual processor methods (`process_colonize()`, `process_transfer()`) directly, OR
  - Run through `_process_tick()` or full `process_turn()`
- [x] Update mock setups that mock `process_end_turn_orders`
- [x] Update any tests that check for `process_end_turn_orders` existence

**Notes:**
Already completed in Phase 4:
- test_turn_processing.py: Rewrote for ActionExecutionEngine architecture
- test_dependency_injection.py: Updated to verify action_engine delegation
- test_colonize_logic.py: Uses FleetOrderProcessor directly
- test_advanced_fleet_orders.py: Uses FleetOrderProcessor directly
- MockOrderProcessor: Already has process_end_turn_orders mock

### Task 5.3: Update integration tests [Complex]
**Files:** `tests/integration/strategy/turn_engine/`, `tests/integration/colonization/`, `tests/integration/gameplay_loop/`
**Tests:** `pytest tests/integration/ --testmon`

- [x] Tests using `process_turn()` should mostly work if fleets have speed >= 1
- [x] For tests expecting immediate execution: ensure fleet speed allows action to complete within the turn
- [x] For multi-tick actions (superweapons with action_time > 1): run enough turns or ensure fleet speed is high enough
- [x] Update assertions that check order state after `process_turn()` — orders now pop during ticks, not at end

**Notes:**
All integration tests pass. Tests use process_turn() which correctly routes through ActionExecutionEngine.
Verified 100 integration tests pass across turn_engine, colonization, and gameplay_loop directories.

### Task 5.4: Run full test suite and fix remaining failures [Medium]
**Tests:** `pytest tests/ -n 12`

- [x] Run full suite, document all failures
- [x] Fix each failure category systematically
- [x] Ensure test count is maintained (12,366 passed baseline — no deleted tests without replacement)

**Notes:**
Full test suite: 12,445 passed, 1 skipped
Test count increased from baseline (12,366 -> 12,445) due to new ActionExecutionEngine tests
No regressions from Phase 4 migration

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] `pytest tests/ -n 12` — all tests pass
- [x] Baseline test count maintained or increased (12,445 > 12,366)
- [x] No tests skip that didn't skip before (1 skip unchanged)
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
