# Phase 2: LLMBackgroundCall completion Event (production-side)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-324 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Add a `_done_event: threading.Event` to `LLMBackgroundCall`, set it in `_run()` after each terminal-state transition, expose `wait(timeout=None)` as a public method. This unblocks PROJ-322 Task 4.3 by replacing the test-side `time.monotonic` polling deadline pattern with deterministic event-based waits.

**Required reading:**
- [`design.md`](design.md) — LLMBackgroundCall Implementation Pattern section
- [`game/services/llm/background.py`](game/services/llm/background.py) — full file before editing
- [`tests/unit/services/llm/test_background.py`](tests/unit/services/llm/test_background.py) — see how `TestLockSafety` tests the existing concurrency

**Parallelism:** Fully file-disjoint from PROJ-326 and PROJ-325. May run **in parallel with Phase 1 of this same project** (Phase 1 touches `game/ui/screens/`, Phase 2 touches `game/services/llm/`). If a parallel agent is running Phase 1, coordinate so neither modifies `tests/fixtures/ui_widget_factory.py` simultaneously (Phase 1 task 1.1 modifies it; Phase 2 does not).

**Estimate:** ~1 hour LLM-paced (per OpenCode 322-review CRIT-002).

---

## Tasks

### Task 2.1: Add `_done_event` to `LLMBackgroundCall.__init__` [Simple]

**File:** [`game/services/llm/background.py`](game/services/llm/background.py)
**Tests:** `pytest tests/unit/services/llm/test_background.py`

- [ ] In `LLMBackgroundCall.__init__`, after the existing `_cancel_event = threading.Event()` line (~L97), add:
  ```python
  self._done_event = threading.Event()
  ```
- [ ] Verify the addition does not change construction-time behavior (event created but not set). `TestConstructionAndValidation` should still pass with no other changes.
- [ ] Verify: `pytest tests/unit/services/llm/test_background.py::TestConstructionAndValidation` passes.

**Notes:** [Filled during implementation]

---

### Task 2.2: Set `_done_event` in `_run()` terminal-state transitions [Medium]

**File:** [`game/services/llm/background.py`](game/services/llm/background.py)
**Tests:** `pytest tests/unit/services/llm/test_background.py::TestSuccessPath tests/unit/services/llm/test_background.py::TestErrorPath tests/unit/services/llm/test_background.py::TestCancellation`

- [ ] Locate the `_run()` method (the worker-thread entry point). Identify each terminal-state transition: status moves to DONE, ERROR, or CANCELLED.
- [ ] After each terminal-state transition, call `self._done_event.set()`. Place the `set()` OUTSIDE `_state_lock` to avoid waiter starvation — `Event.set()` is internally thread-safe.
- [ ] Verify each path sets the event exactly once (a second `set()` is a no-op but indicates a logic error).
- [ ] Run the existing `TestLockSafety` tests to confirm no concurrency regression: `pytest tests/unit/services/llm/test_background.py::TestLockSafety`.
- [ ] Verify: full file passes — `pytest tests/unit/services/llm/test_background.py`. (Tests still poll at this point; migrated in Task 2.4.)

**Notes:** [Filled during implementation. Document line numbers of each terminal-state transition.]

---

### Task 2.3: Expose `wait(timeout)` public method [Simple]

**File:** [`game/services/llm/background.py`](game/services/llm/background.py)
**Tests:** Manually exercise; covered by Task 2.4 migration.

- [ ] Add a `wait(self, timeout: float | None = None) -> bool:` method to `LLMBackgroundCall`. Implementation: `return self._done_event.wait(timeout)`.
- [ ] Add return-type annotation (per project conventions in `docs/03_CONVENTIONS.md`).
- [ ] Add docstring: "Block until the call reaches a terminal state, or until `timeout` seconds elapse. Returns True if a terminal state was reached, False if timed out. Returns immediately if already in a terminal state."
- [ ] Verify: `pytest tests/unit/services/llm/test_background.py` still passes.

**Notes:** [Filled during implementation]

---

### Task 2.4: Migrate `test_background.py` polling loops to `wait()` [Medium]

**File:** [`tests/unit/services/llm/test_background.py`](tests/unit/services/llm/test_background.py)
**Tests:** `pytest tests/unit/services/llm/test_background.py`

This is PROJ-322 Task 4.3, finally unblocked.

- [ ] Identify all polling loops of the form:
  ```python
  deadline = time.monotonic() + 2.0
  while call.status not in (CallStatus.DONE, CallStatus.ERROR) and time.monotonic() < deadline:
      time.sleep(0.01)
  ```
  Per the Explore investigation, these live around lines 128-130, 147-149, 163-165, 181-184, 212-214, 270-273.
- [ ] Replace each with:
  ```python
  assert call.wait(timeout=2.0), "call did not complete within 2s"
  ```
- [ ] Remove now-unused `time` and `time.monotonic` imports if no other call sites remain.
- [ ] Verify: `pytest tests/unit/services/llm/test_background.py` passes — should be **deterministically faster** than before (no 10ms polling overhead).
- [ ] Document approximate runtime delta in Notes — this is part of the test-runtime reduction goal that motivates PROJ-327.
- [ ] In PROJ-322 `phase_4_checklist.md`, find Task 4.3 and update its `**DEFERRED-OUT-OF-SCOPE` annotation to `**RESOLVED IN PROJ-324 Phase 2 Task 2.4 (commit <SHA>)**`.

**Notes:** [Filled during implementation. Record before/after runtime of `test_background.py`.]

---

## Phase Completion Checklist

When all tasks above are done:

- [ ] All task checkboxes above are checked
- [ ] Sharded test suite passes: `python Tools/test_sharded/test_sharded.py`
- [ ] `tests/unit/services/llm/test_background.py` runtime measurably reduced (record in Notes for Task 2.4)
- [ ] PROJ-322 `phase_4_checklist.md` Task 4.3 annotation updated
- [ ] Update status at top of this file to `Complete`
- [ ] Update `plan.md` phase table row to `Complete`
- [ ] Update `plan.md` Current State to point to Phase 3
