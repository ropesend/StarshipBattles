# Phase 2: Move small hook logic onto named `TurnEngine` methods

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-428 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Depends on:** phase_1
**Review Mode:** standard
**Files (planned):**
- `game/strategy/engine/turn_engine.py`
- `game/strategy/engine/turn_phase_registry.py`
- `tests/unit/strategy/turn_engine/test_tick_phase_descriptors.py`

**Objective:** Replace the three small registry helpers
(`_log_turn_start_tick_1`, `_log_after_construction_tick_1`,
`_accumulate_env_events`) with named methods on `TurnEngine`. Do not create
a separate `TurnLogger` class unless `turn_engine.py` becomes materially
less clear.

---

## Tasks

### Task 3.1: Red tests for the three engine methods [Medium]
**File:** `tests/unit/strategy/turn_engine/test_tick_phase_descriptors.py`
**Tests:** `pytest tests/unit/strategy/turn_engine/test_tick_phase_descriptors.py`

- [ ] Add a failing test that calls `TurnEngine`'s tick-1 pre-harvesting
      log method directly and asserts the expected log line is emitted.
- [ ] Add a failing test that calls `TurnEngine`'s tick-1 post-production
      log method directly and asserts the expected log line is emitted.
- [ ] Add a failing test that calls `TurnEngine`'s env-event accumulation
      method directly and asserts `last_environmental_events` is updated.
- [ ] Confirm all three tests fail for the intended reason.

**Notes:**

### Task 3.2: Implement named methods on `TurnEngine` [Medium]
**File:** `game/strategy/engine/turn_engine.py`
**Tests:** `pytest tests/unit/strategy/turn_engine/test_tick_phase_descriptors.py`

- [ ] Implement the tick-1 pre-harvesting log method on `TurnEngine`,
      preserving the exact log line and gating (only on tick 1).
- [ ] Implement the tick-1 post-production log method on `TurnEngine`,
      preserving the exact log line and gating.
- [ ] Implement the env-event accumulation method on `TurnEngine`,
      preserving the contract that `last_environmental_events` accumulates
      returned events.
- [ ] Confirm the three new red tests now pass.

**Notes:**

### Task 3.3: Repoint registry hooks at the new methods [Simple]
**File:** `game/strategy/engine/turn_phase_registry.py`
**Tests:** `pytest tests/unit/strategy/turn_engine/ -x`

- [ ] Replace the descriptor wiring for the three hooks with resolver
      lambdas that bind to the new `TurnEngine` methods.
- [ ] Verify `DEFAULT_TICK_PHASE_LIST` and `DEFAULT_END_OF_TURN_PHASE_LIST`
      golden tests stay green.

**Notes:**

### Task 3.4: Delete the three small registry helpers [Simple]
**File:** `game/strategy/engine/turn_phase_registry.py`
**Tests:** `pytest tests/unit/strategy/turn_engine/ -x`

- [ ] Remove `_log_turn_start_tick_1` from `turn_phase_registry.py`.
- [ ] Remove `_log_after_construction_tick_1` from `turn_phase_registry.py`.
- [ ] Remove `_accumulate_env_events` from `turn_phase_registry.py`.
- [ ] Verify: focused turn-engine suite is green.
- [ ] Verify: `TURN PERF` output format is unchanged (manual visual check
      or characterization assertion).

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `pytest tests/unit/strategy/turn_engine/ -x` is green
- [ ] Update status at top of this file to `Complete (Committed)`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 3
