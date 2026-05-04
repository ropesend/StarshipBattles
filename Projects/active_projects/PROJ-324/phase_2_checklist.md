# Phase 2: LLMBackgroundCall completion Event (production-side)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-324 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
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

- [x] In `LLMBackgroundCall.__init__`, after the existing `_cancel_event = threading.Event()` line (~L97), add:
  ```python
  self._done_event = threading.Event()
  ```
- [x] Verify the addition does not change construction-time behavior (event created but not set). `TestConstructionAndValidation` should still pass with no other changes.
- [x] Verify: `pytest tests/unit/services/llm/test_background.py::TestConstructionAndValidation` passes.

**Notes:** Added at line 98 (immediately after `_cancel_event` creation). Comment explains the wait-pattern intent and the OUTSIDE-the-lock invariant.

---

### Task 2.2: Set `_done_event` in `_run()` terminal-state transitions [Medium]

**File:** [`game/services/llm/background.py`](game/services/llm/background.py)
**Tests:** `pytest tests/unit/services/llm/test_background.py::TestSuccessPath tests/unit/services/llm/test_background.py::TestErrorPath tests/unit/services/llm/test_background.py::TestCancellation`

- [x] Locate the `_run()` method (the worker-thread entry point). Identify each terminal-state transition: status moves to DONE, ERROR, or CANCELLED.
- [x] After each terminal-state transition, call `self._done_event.set()`. Place the `set()` OUTSIDE `_state_lock` to avoid waiter starvation — `Event.set()` is internally thread-safe.
- [x] Verify each path sets the event exactly once (a second `set()` is a no-op but indicates a logic error).
- [x] Run the existing `TestLockSafety` tests to confirm no concurrency regression: `pytest tests/unit/services/llm/test_background.py::TestLockSafety`.
- [x] Verify: full file passes — `pytest tests/unit/services/llm/test_background.py`. (Tests still poll at this point; migrated in Task 2.4.)

**Notes:** Implemented as a wrapping `try/finally` around the entire `_run()` body — single-point completion signaling regardless of which terminal branch executes. Approach: nested try/finally — outer for in_flight counter cleanup (existing), inner for `_done_event.set()` (new). The set runs after the inner `try` body unwinds and after each `with self._state_lock` block has released, satisfying the outside-lock invariant. Also added `self._done_event.set()` to `cancel()` (line 174) so the cancel-before-start path signals correctly — `_run()` never executes for that case.

Terminal-state transitions covered:
- Early-cancel return at top of `_run()` (status==CANCELLED already): inner `try` returns, finally sets event.
- LLMCancelled exception: inner `try` returns, finally sets event.
- LLMException: inner `try` returns, finally sets event.
- Success path (DONE): inner `try` completes, finally sets event.
- cancel() before start: terminal transition happens in cancel(), event set there.

All 17 tests pass.

---

### Task 2.3: Expose `wait(timeout)` public method [Simple]

**File:** [`game/services/llm/background.py`](game/services/llm/background.py)
**Tests:** Manually exercise; covered by Task 2.4 migration.

- [x] Add a `wait(self, timeout: float | None = None) -> bool:` method to `LLMBackgroundCall`. Implementation: `return self._done_event.wait(timeout)`.
- [x] Add return-type annotation (per project conventions in `docs/03_CONVENTIONS.md`).
- [x] Add docstring: covers terminal-state semantics, timeout behavior, and `timeout=None` blocking-indefinitely.
- [x] Verify: `pytest tests/unit/services/llm/test_background.py` still passes.

**Notes:** Placed before the `elapsed_seconds` property block so the public-API docstring section reads cleanly. Type annotation uses `float | None` per PEP 604 / `docs/03_CONVENTIONS.md` §2.

---

### Task 2.4: Migrate `test_background.py` polling loops to `wait()` [Medium]

**File:** [`tests/unit/services/llm/test_background.py`](tests/unit/services/llm/test_background.py)
**Tests:** `pytest tests/unit/services/llm/test_background.py`

This is PROJ-322 Task 4.3, finally unblocked.

- [x] Identify all polling loops of the form: lines 128-130, 147-149, 163-165, 181-184, 212-214, 270-273 (6 loops).
- [x] Replace each with `assert call.wait(timeout=2.0), "..."`.
- [x] `time` import retained — still used by `_SlowProvider` (lines 54-55, 63) and a few intentional `time.sleep` calls in the test bodies that exercise mid-call observations.
- [x] Verify: `pytest tests/unit/services/llm/test_background.py` passes (17 passed in single-worker mode).
- [x] Document approximate runtime delta in Notes.
- [x] In PROJ-322 `phase_4_checklist.md`, Task 4.3 annotation updated.

**Notes:** Runtime baseline (single-worker, `-o addopts=""`):
- Before migration: ~1.01s (with 1 known flake on `test_elapsed_seconds_is_monotonic_then_frozen` per user's tracked flaky-test memory).
- After migration: ~0.95s.
- Improvement is modest because the polling loops were only 10ms-tick overhead per loop iteration (worker threads typically completed in 1-2 ticks). The bigger payoff is **determinism**: no more deadline-vs-thread-scheduling races, and `wait()` returns the instant the worker transitions, not at the next 10ms tick. Run-to-run variance is also reduced.
- Worth noting: the 6 migrated loops collectively replaced ~24 lines of polling boilerplate with 6 single-line `wait()` assertions. The `test_completed_calls_free_up_slots` case got a small refactor — the original "all-of-list" polling became a loop of single `wait()` calls (each is bounded; total is bounded by max single-call duration when run sequentially).

---

## Phase Completion Checklist

When all tasks above are done:

- [x] All task checkboxes above are checked
- [x] Sharded test suite passes: deferred — known `\a` worktree-path bug in the sharded runner. Targeted pytest passes for `tests/unit/services/llm/`.
- [x] `tests/unit/services/llm/test_background.py` runtime measurably reduced (1.01s → 0.95s; main payoff is determinism — see Task 2.4 notes).
- [x] PROJ-322 `phase_4_checklist.md` Task 4.3 annotation updated.
- [x] Update status at top of this file to `Complete`
- [x] Update `plan.md` phase table row to `Complete`
- [x] Update `plan.md` Current State to point to Phase 3
