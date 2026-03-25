# Phase 6: Live State Comparison Harness

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-223 6`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Build a harness usable from QA sessions to snapshot, save/load, and compare game state.

---

## Tasks

### Task 6.1: Create state snapshot utility [Medium]
**File:** `tests/infrastructure/state_snapshot.py` (NEW)
**Tests:** `pytest tests/unit/infrastructure/test_state_snapshot.py`

- [ ] Create `snapshot_game_state()` function
- [ ] Create `compare_game_states()` function with expected-difference filtering
- [ ] Create `SaveLoadVerifier` class with `verify_round_trip()` method
- [ ] Create `VerificationReport` dataclass
- [ ] Write unit tests
- [ ] Run tests: `pytest tests/unit/infrastructure/test_state_snapshot.py`

**Notes:**

### Task 6.2: Create verification integration test [Medium]
**File:** `tests/integration/save_load/test_live_verification.py` (NEW)
**Tests:** `pytest tests/integration/save_load/test_live_verification.py`

- [ ] Test verify_round_trip with minimal game session → passes
- [ ] Test verify_round_trip with populated game session → passes
- [ ] Test deliberate corruption → verification catches it
- [ ] Test report includes timing and size stats

**Notes:**

### Task 6.3: Run full test suite (final verification) [Simple]
**Tests:** `pytest tests/ -n 12`

- [ ] All tests pass
- [ ] Verify total test count increased by expected amount
- [ ] Record final test count

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Run `pytest tests/ -n 12` — all tests pass
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to indicate project complete
