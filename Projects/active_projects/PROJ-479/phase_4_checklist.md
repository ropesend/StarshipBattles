# Phase 4: CAT-7 Sleep/Latency

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-479 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Replace the 3 verified CAT-7 `time.sleep` clusters from review `2026-05-20_210550_test-review`. Each cluster uses `time.sleep` to wait for nondeterministic state (worker startup, status transition, monotonic-clock advancement). Replace with `threading.Event` synchronization or existing `_wait_until` polling helpers for determinism + CI speedup.

---

## Tasks

### Task 4.1: test_background.py — 3 sleeps in monotonic-clock / cancel tests
**File:** `tests/unit/services/llm/test_background.py`
**Tests:** `pytest tests/unit/services/llm/test_background.py`

- [x] Replaced both sleeps in `test_elapsed_seconds_is_monotonic_then_frozen` with deterministic `call.wait(timeout=2.0)` + post-completion-snapshot equality check.
- [x] Replaced `time.sleep(0.02)` in `test_cancel_marks_status_cancelled` with deterministic poll for `call.status == CallStatus.RUNNING`.
- [x] Verify: 19 tests pass.

### Task 4.2: test_replay_verification_coordinator.py — 5 sleeps for thread sync
**File:** `tests/unit/services/replay/test_replay_verification_coordinator.py`
**Tests:** `pytest tests/unit/services/replay/test_replay_verification_coordinator.py`

- _NEEDS_REWORK_ (per skeptical-check verification):
  - Line 269 `time.sleep(0.01)`: micro-yield inside a deterministic `while _is_worker_busy()` poll loop — already best practice; replacing it with event sync would require adding an event in production code (out of scope).
  - Line 407 `time.sleep(0.1)`: "tiny grace" wait to verify the listener does NOT fire after shutdown. This is an inherently time-based absence assertion — no event can prove the absence.
  - Line 476 `time.sleep(0.1)`: same absence-of-work pattern.
  - Line 515 `time.sleep(0.01)`: micro-yield inside another deterministic poll loop.
  - Line 631 `time.sleep(0.05)`: deliberate sleep inside a fake runner used to test concurrency cap semantics. This is test-fixture behavior, not test latency.
  - _(Actual path: `tests/unit/strategy/services/test_replay_verification_coordinator.py` — plan path was wrong.)_
- [x] Verify: tests pass (no change required).

### Task 4.3: test_race_description_llm_controller.py — 3 sleeps then cancel
**File:** `tests/unit/strategy/services/test_race_description_llm_controller.py`
**Tests:** `pytest tests/unit/strategy/services/test_race_description_llm_controller.py`

- [x] Replaced all 3 `time.sleep(0.02)` calls with `_wait_until(...controller.[bio|socio]_status == FieldStatus.RUNNING...)`.
- [x] Verify: 15 tests pass.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase (Phase 5 — DUP cluster consolidation)

_Source review: `Reviews/results/2026-05-20_210550_test-review/`. See [findings/source_review.md](findings/source_review.md) for the link._
