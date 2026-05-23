# Phase 4: CAT-7 Sleep/Latency

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-479 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Replace the 3 verified CAT-7 `time.sleep` clusters from review `2026-05-20_210550_test-review`. Each cluster uses `time.sleep` to wait for nondeterministic state (worker startup, status transition, monotonic-clock advancement). Replace with `threading.Event` synchronization or existing `_wait_until` polling helpers for determinism + CI speedup.

---

## Tasks

### Task 4.1: test_background.py — 3 sleeps in monotonic-clock / cancel tests
**File:** `tests/unit/services/llm/test_background.py`
**Tests:** `pytest tests/unit/services/llm/test_background.py`

- [ ] Replace `time.sleep(0.01)` at line 141 (in `test_elapsed_seconds_is_monotonic_then_frozen`) with `threading.Event`-based wait until elapsed > 0.
- [ ] Replace `time.sleep(0.05)` at line 149 (verifies elapsed is frozen after completion) with event-based wait for completion signal.
- [ ] Replace `time.sleep(0.02)` at line 201 (in `test_cancel_marks_status_cancelled`) with event-based wait for worker-started signal before issuing cancel.
- [ ] Verify: `pytest tests/unit/services/llm/test_background.py` passes; cumulative latency drops ≥ 0.08s per run.

### Task 4.2: test_replay_verification_coordinator.py — 5 sleeps for thread sync
**File:** `tests/unit/services/replay/test_replay_verification_coordinator.py`
**Tests:** `pytest tests/unit/services/replay/test_replay_verification_coordinator.py`

- [ ] Replace `time.sleep(0.01)` at line 269 with `threading.Event` / `Barrier` deterministic sync. Extend the existing gate-event pattern used elsewhere in the test.
- [ ] Replace `time.sleep(0.1)` at line 408 with event-based sync.
- [ ] Replace `time.sleep(0.01)` at line 476 with event-based sync.
- [ ] Replace `time.sleep(0.01)` at line 515 with event-based sync.
- [ ] Replace `time.sleep(0.05)` at line 631 with event-based sync.
- [ ] Verify: `pytest tests/unit/services/replay/test_replay_verification_coordinator.py` passes; cumulative latency drops ≥ 0.17s per run.

### Task 4.3: test_race_description_llm_controller.py — 3 sleeps then cancel
**File:** `tests/unit/strategy/services/test_race_description_llm_controller.py`
**Tests:** `pytest tests/unit/strategy/services/test_race_description_llm_controller.py`

- [ ] Replace `time.sleep(0.02)` at lines 325, 343, 364 with `_wait_until(lambda: controller.bio_status == FieldStatus.RUNNING)` — the helper already exists at line 133 of the same file.
- [ ] Verify: `pytest tests/unit/strategy/services/test_race_description_llm_controller.py` passes; cumulative latency drops ≥ 0.06s per run.

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase (Phase 5 — DUP cluster consolidation)

_Source review: `Reviews/results/2026-05-20_210550_test-review/`. See [findings/source_review.md](findings/source_review.md) for the link._
