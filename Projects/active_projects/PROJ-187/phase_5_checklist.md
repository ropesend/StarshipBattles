# Phase 5: Test Migration [Complex]

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-187 5`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Update all tests that depend on end-of-turn order execution to work with tick-based execution.

**KEY BEHAVIOR CHANGE:** Orders that previously executed instantly at end-of-turn now require action ticks. A fleet with speed 5 gets action ticks every 20 sub-ticks. A 1-cost action completes on tick 20. Tests calling `process_turn()` should mostly work since actions still complete within a turn. Tests calling `process_end_turn_orders()` directly must be rewritten.

---

## Tasks

### Task 5.1: Find all affected tests [Medium]
**Tests:** Grep + analysis

- [ ] Grep for `process_end_turn_orders` in all test files — these call the deleted method directly
- [ ] Grep for `_process_end_turn_orders` in all test files
- [ ] Grep for tests that mock `process_end_turn_orders` on order processor
- [ ] Grep for tests checking order execution timing/sequence after `process_turn()`
- [ ] Create categorized list of all affected test files

**Notes:**

### Task 5.2: Update direct-call tests [Medium]
**Files:** Various test files identified in 5.1
**Tests:** Run each updated test file individually

- [ ] Tests that called `process_end_turn_orders()` directly must switch to:
  - Call `action_engine.process_action_ticks()` at correct tick, OR
  - Call individual processor methods (`process_colonize()`, `process_transfer()`) directly, OR
  - Run through `_process_tick()` or full `process_turn()`
- [ ] Update mock setups that mock `process_end_turn_orders`
- [ ] Update any tests that check for `process_end_turn_orders` existence

**Notes:**

### Task 5.3: Update integration tests [Complex]
**Files:** `tests/integration/strategy/turn_engine/`, `tests/integration/colonization/`, `tests/integration/gameplay_loop/`
**Tests:** `pytest tests/integration/ --testmon`

- [ ] Tests using `process_turn()` should mostly work if fleets have speed >= 1
- [ ] For tests expecting immediate execution: ensure fleet speed allows action to complete within the turn
- [ ] For multi-tick actions (superweapons with action_time > 1): run enough turns or ensure fleet speed is high enough
- [ ] Update assertions that check order state after `process_turn()` — orders now pop during ticks, not at end

**Notes:**

### Task 5.4: Run full test suite and fix remaining failures [Medium]
**Tests:** `pytest tests/ -n 12`

- [ ] Run full suite, document all failures
- [ ] Fix each failure category systematically
- [ ] Ensure test count is maintained (12,366 passed baseline — no deleted tests without replacement)

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `pytest tests/ -n 12` — all tests pass
- [ ] Baseline test count maintained or increased
- [ ] No tests skip that didn't skip before
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
