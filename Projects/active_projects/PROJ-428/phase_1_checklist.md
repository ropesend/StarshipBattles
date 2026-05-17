# Phase 1: Freeze the real contract with red tests

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-428 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Depends on:** none
**Review Mode:** standard
**Files (planned):**
- `tests/unit/strategy/turn_engine/test_turn_engine_phase_320_movement_diff.py`
- `tests/unit/strategy/turn_engine/test_tick_phase_descriptors.py`

**Objective:** Add failing / characterization tests that pin the real
behavioral contract of the six registry hooks before any code moves. Tests
must fail for the intended reason in a scratch experiment but pass against
the current code (i.e. they characterize what exists).

---

## Tasks

### Task 1.1: Characterization tests for environmental events [Simple]
**File:** `tests/unit/strategy/turn_engine/test_tick_phase_descriptors.py`
**Tests:** `pytest tests/unit/strategy/turn_engine/test_tick_phase_descriptors.py`

- [ ] Add a test that confirms `ctx.last_environmental_events` accumulates
      every environmental event returned through the env-event hook over a
      turn.
- [ ] Verify the test passes against current code.

**Notes:**

### Task 1.2: Characterization tests for movement snapshot [Medium]
**File:** `tests/unit/strategy/turn_engine/test_turn_engine_phase_320_movement_diff.py`
**Tests:** `pytest tests/unit/strategy/turn_engine/test_turn_engine_phase_320_movement_diff.py`

- [ ] Add a test that confirms `movement_calc` stores both `move_queue`
      and `pre_movement_locations` on the turn context.
- [ ] Add a test that confirms `movement_apply` computes `moved_fleet_ids`
      from the diff between `pre_movement_locations` and post-movement
      locations.
- [ ] Verify both tests pass against current code.

**Notes:**

### Task 1.3: Characterization tests for `_booster_dirty` propagation [Medium]
**File:** `tests/unit/strategy/turn_engine/test_turn_engine_phase_320_movement_diff.py`
**Tests:** `pytest tests/unit/strategy/turn_engine/test_turn_engine_phase_320_movement_diff.py`

- [ ] Add a test that confirms `_booster_dirty` flips only for empires
      whose fleets actually moved (not for empires whose fleets stood
      still).
- [ ] Verify the test passes against current code.

**Notes:**

### Task 1.4: Characterization tests for minefield call contract [Complex]
**File:** `tests/unit/strategy/turn_engine/test_turn_engine_phase_320_movement_diff.py`
**Tests:** `pytest tests/unit/strategy/turn_engine/test_turn_engine_phase_320_movement_diff.py`

- [ ] Add a test that confirms
      `MinefieldResolver.resolve_minefield_entry(...)` is invoked with
      `registries=engine._registries` for each moved fleet.
- [ ] Add a test that confirms fleets emptied by minefield damage are
      removed from the owning empire.
- [ ] Verify both tests pass against current code.

**Notes:**

### Task 1.5: Confirm characterization tests are valid red gates [Simple]
**File:** (mental experiment, not committed)

- [ ] Temporarily stub out each behavior in a local branch and confirm
      the characterization tests fail for the intended reason.
- [ ] Revert the stub.
- [ ] Verify: characterization suite is green on the unmodified code.

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `pytest tests/unit/strategy/turn_engine/ -x` is green
- [ ] Update status at top of this file to `Complete (Committed)`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 2
