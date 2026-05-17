# Phase 0: Characterization — pin current `restore()` behavior with focused tests

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-432 0`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Depends on:** none
**Review Mode:** lightweight
**Files (planned):**
- `tests/unit/strategy/turn_engine/test_turn_state_snapshot.py`

**Objective:** Write focused tests that pin the two invariants currently missing from `TurnStateSnapshot.restore()` — galaxy back-references on empires post-restore, and pursuer-tracker membership for `MOVE_TO_FLEET` / `JOIN_FLEET` orders post-restore. The tests **must fail** against today's `restore()` body; Phase 1's wiring additions are what makes them pass. Assertion shape mirrors `test_rehydrate_wires_galaxy_back_refs` and `test_rehydrate_rebuilds_pursuer_trackers` in the persistence-adapter suite.

---

## Tasks

### Task 0.1: Add `test_restore_wires_galaxy_back_refs` [Simple]
**File:** `tests/unit/strategy/turn_engine/test_turn_state_snapshot.py`

- [ ] In the `TestTurnStateSnapshotRestore` class, add a test that builds a snapshot from `minimal_game_session`, calls `snapshot.restore(session)`, and asserts `each_empire._galaxy is session.galaxy` for every restored empire.
- [ ] Run the test in isolation and confirm it **fails** today (current `restore()` does not call `empire.set_galaxy(...)`).

### Task 0.2: Add `test_restore_rebuilds_pursuer_trackers` [Standard]
**File:** `tests/unit/strategy/turn_engine/test_turn_state_snapshot.py`

- [ ] Build a session with a source fleet (`fleet_id=9001`) and a target fleet (`fleet_id=9002`) on the first empire, where source has a `MOVE_TO_FLEET` order pointing at target.
- [ ] Capture a snapshot, mutate the live state, then `snapshot.restore(session)`.
- [ ] Resolve `restored_source = session.galaxy.get_fleet_by_id(9001)` and `restored_target = session.galaxy.get_fleet_by_id(9002)`.
- [ ] Assert `restored_source.orders[0].target is restored_target` (resolution invariant — already passes today).
- [ ] Assert `restored_source in restored_target.pursuer_tracker.pursuers` — must **fail** today; Phase 1 makes it pass.
- [ ] Mirror the assertion shape used by `tests/unit/strategy/engine/session/test_persistence_adapter.py::TestRehydrate::test_rehydrate_rebuilds_pursuer_trackers`.

### Task 0.3: Confirm failing-state evidence [Simple]
**Tests:** `pytest tests/unit/strategy/turn_engine/test_turn_state_snapshot.py -x`

- [ ] Run the focused suite and capture the two new tests' failure output in the phase notes. Strict TDD requires the failing state be observed before Phase 1 begins.

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Two new tests added, both observed failing against current `restore()`
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 1
