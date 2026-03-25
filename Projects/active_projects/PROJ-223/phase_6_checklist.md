# Phase 6: Live State Comparison Harness

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-223 6`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Build a harness usable from QA sessions to snapshot, save/load, and compare game state.

---

## Tasks

### Task 6.1: Create state snapshot utility [Medium]
- [x] Create `snapshot_game_state()` function
- [x] Create `compare_game_states()` function with expected-difference filtering
- [x] Create `SaveLoadVerifier` class with `verify_round_trip()` method
- [x] Create `VerificationReport` dataclass
- [x] Write unit tests
- [x] Run tests: `pytest tests/unit/infrastructure/test_state_snapshot.py`

**Notes:** Auto-ignores save_path and storm hex_offsets. Handles tuple→list JSON conversion.

### Task 6.2: Create verification integration test [Medium]
- [x] Test verify_round_trip with minimal game session → passes
- [x] Test verify_round_trip with populated game session → passes
- [x] Test deliberate corruption → verification catches it
- [x] Test report includes timing and size stats

**Notes:** 10 tests across unit and integration files.

### Task 6.3: Run full test suite (final verification) [Simple]
- [x] All tests pass: 13,714 passed, 2 skipped
- [x] Verify total test count increased by expected amount (280 new tests from baseline 13,434)
- [x] Record final test count: 13,714

**Notes:**

---

## Phase Completion Checklist
- [x] All task checkboxes above are checked
- [x] Run `pytest tests/ -n 12` — 13,714 passed, 2 skipped
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to indicate project complete
