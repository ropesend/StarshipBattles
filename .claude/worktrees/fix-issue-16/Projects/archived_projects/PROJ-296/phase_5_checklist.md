# Phase 5: Threading Helper [Medium]

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-296 5`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** `LLMBackgroundCall` — wraps a provider's `complete()` on a worker thread. Exposes `status`, `result`, `error`, `elapsed_seconds`. Supports cancel. Enforces `MAX_CONCURRENT_CALLS`. Adds shutdown-hook to `game/app.py`.

---

## Tasks

### Task 5.1: Implement `LLMBackgroundCall` [Complex]
**File:** `game/services/llm/background.py` (NEW)
**Tests:** `pytest tests/unit/services/llm/test_background.py`

- [x] Write failing tests (TDD):
  - **Status transitions:**
    - Newly constructed: `status == PENDING`
    - After `start()`: `status == RUNNING` (briefly), then `DONE` once worker finishes
    - On error: `status == ERROR`, `error` is the `LLMException`
    - On `cancel()`: `status == CANCELLED`, `result is None`
  - **Result correctness:**
    - With `stub_llm_provider` returning a fixed `CompletionResult`, after start+join, `result == that result`
  - **Error propagation:**
    - With a provider whose `complete()` raises `LLMNetworkError`, after start+join, `status == ERROR` and `error` is that exception
  - **`elapsed_seconds`:**
    - Returns 0.0 before start
    - After start, increases monotonically
    - After completion, frozen at the final value
  - **Cancel semantics:**
    - `cancel()` sets internal `threading.Event`; provider sees it via `cancel_token` kwarg between retries
    - Even if the provider's `complete()` later returns successfully, `status` stays `CANCELLED` and `result` is None
    - `cancel()` is idempotent
  - **`MAX_CONCURRENT_CALLS` enforcement:**
    - Constructing 3 calls and starting them all is OK
    - Starting a 4th raises `LLMConfigError` with context indicating "max concurrent calls"
    - When one of the first 3 completes (DONE / ERROR / CANCELLED), a new one CAN start
  - **Lock safety:**
    - 100 concurrent reads of `status` from different threads while the worker mutates it never raise / never see torn state (use `threading.Barrier` to align reads)
  - **`start()` is idempotent** — calling twice doesn't spawn two workers (returns early on second call)
- [x] Implement per design.md spec:
  - `CallStatus` enum: PENDING / RUNNING / DONE / ERROR / CANCELLED
  - Module-level counter `_in_flight_calls: int` and lock `_in_flight_lock`
  - `LLMBackgroundCall.__init__` validates inputs (raise `ValidationException` on empty messages or null provider) — Pattern 19/20
  - `start()`: check counter, increment under lock, raise `LLMConfigError` if `>= LLMConfig.MAX_CONCURRENT_CALLS`, spawn `threading.Thread(target=self._run, daemon=False)`, store start time
  - `_run()`: try call provider; on success set `_result` + `status = DONE` (UNLESS already CANCELLED); on `LLMException` set `_error` + `status = ERROR`; in finally decrement counter
  - `cancel()`: set `_cancel_event`, transition status to CANCELLED if not already terminal
  - All status reads/writes guarded by `_state_lock`

**Notes:**

### Task 5.2: Module-level shutdown hook [Medium]
**File:** `game/services/llm/background.py`, `game/app.py`
**Tests:** `pytest tests/unit/services/llm/test_background.py`

- [x] Write failing tests:
  - `shutdown_all_calls(timeout=5.0)` joins all in-flight worker threads with the given timeout
  - If timeout elapses with threads still alive, logs a warning and returns (does not hang)
  - After shutdown, `_in_flight_calls == 0`
- [x] Implement `shutdown_all_calls(timeout: float = 5.0) -> None` in `background.py`:
  - Iterates a module-level set `_active_workers: Set[threading.Thread]`
  - Calls `t.join(timeout=timeout)` on each
  - Logs warning for any thread that's still alive after join
  - Threads add themselves to `_active_workers` in `_run()` and remove themselves in the finally block
- [x] Add to `game/app.py`'s shutdown sequence (find where `pygame.quit()` is called; insert call to `shutdown_all_calls()` immediately before it). Likely site is around `game/app.py:600+`.
- [x] Add an integration test that constructs a long-running mock provider call, then calls `shutdown_all_calls(timeout=0.5)`, and verifies the warning was logged.

**Notes:**

### Task 5.3: Export from package [Simple]
**File:** `game/services/llm/__init__.py`
**Tests:** `pytest tests/unit/services/llm/`

- [x] Re-export `LLMBackgroundCall`, `CallStatus`, `shutdown_all_calls` in `__init__.py` `__all__`
- [x] Run all `tests/unit/services/llm/` — green

**Notes:**

---

## Phase Completion Checklist
- [x] All task checkboxes above are checked
- [x] ~13 new tests in `test_background.py`
- [x] `pytest tests/unit/services/llm/` — all green
- [x] No baseline regression (run `python Tools/test_sharded/test_sharded.py`)
- [x] Update status at top of this file to `Complete`
- [x] Update `plan.md` phase table row to `Complete`
- [x] Update `plan.md` Current State to point to Phase 6
