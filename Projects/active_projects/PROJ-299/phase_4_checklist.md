# Phase 4: RaceDescriptionLLMController (MVVM extract) [Complex]

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-299 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Pygame-free controller owning the LLM call lifecycle. Holds two `LLMBackgroundCall`s (bio + socio), tracks status per-field, dispatches calls in parallel, handles cancel + re-roll cancel-and-restart, exposes `on_change` callback for UI rebuild.

**See `design.md` § "RaceDescriptionLLMController state machine" for the full API spec.**

---

## Tasks

### Task 4.1: Implement `FieldStatus` enum + class skeleton [Simple]
**File:** `game/strategy/services/race_description_llm_controller.py` (NEW)
**Tests:** `pytest tests/unit/strategy/services/test_race_description_llm_controller.py`

- [ ] Write failing tests:
  - `FieldStatus` enum has IDLE, RUNNING, DONE, ERROR, CANCELLED
  - `RaceDescriptionLLMController.__init__(race_config, provider, caption_loader, on_change)` constructs cleanly
  - Initial `bio_status == FieldStatus.IDLE`, `socio_status == FieldStatus.IDLE`
  - `bio_elapsed_seconds == 0.0`, `socio_elapsed_seconds == 0.0`
  - `bio_error is None`, `socio_error is None`
- [ ] Implement the enum + class skeleton with property accessors. Methods `generate_bio` etc. raise `NotImplementedError` for now.
- [ ] Run tests, confirm pass

**Notes:**

### Task 4.2: Implement `generate_bio` and `generate_socio` (state transitions) [Complex]
**File:** Same file as 4.1
**Tests:** Same file

- [ ] Write failing tests:
  - `generate_bio()` from IDLE transitions bio_status to RUNNING (briefly, then to DONE on stub provider)
  - `generate_bio()` calls `build_bio_prompt(race_config, captions)` to assemble the messages
  - `generate_bio()` constructs `LLMBackgroundCall` with `timeout_seconds=90` (overrides PROJ-296 default 60)
  - `generate_bio()` is idempotent: calling twice while RUNNING does nothing
  - `update()` polls the underlying call; on DONE, populates `race_config.bio_description`, transitions to DONE
  - `update()` invokes `on_change` callback whenever a state transition happens
  - On ERROR (provider raises LLMException), transitions to ERROR with the exception captured in `bio_error`
  - Same set for `generate_socio` / socio_status / `race_config.socio_description`
  - **Parallel test**: `generate_bio()` then immediately `generate_socio()` — both end up in RUNNING; both complete independently
- [ ] Implement using PROJ-296 `LLMBackgroundCall`:
  - Inject `provider` parameter into the call
  - Pass `timeout_seconds=90`
  - Store the call on `self._bio_call` / `self._socio_call`
  - `update()` reads `call.status` and translates to `FieldStatus`
- [ ] Run tests, confirm pass

**Notes:**

### Task 4.3: Implement `cancel_bio`, `cancel_socio`, `cancel_all` [Medium]
**File:** Same file
**Tests:** Same file

- [ ] Write failing tests:
  - `cancel_bio()` while RUNNING transitions to CANCELLED (per PROJ-296 LLMBackgroundCall.cancel semantics)
  - `cancel_bio()` from any non-RUNNING state is a no-op
  - `cancel_all()` cancels both fields if both are RUNNING
  - After CANCELLED, `race_config.bio_description` is NOT modified (preserves prior text)
- [ ] Implement
- [ ] Run tests, confirm pass

**Notes:**

### Task 4.4: Implement `re_roll_bio` and `re_roll_socio` [Medium]
**File:** Same file
**Tests:** Same file

- [ ] Write failing tests:
  - `re_roll_bio()` from DONE transitions: cancels prior call (no-op since done), starts a new call, transitions bio_status to RUNNING
  - `re_roll_bio()` while bio is RUNNING: cancels the in-flight call, starts a new one. Final state is RUNNING with the NEW call's elapsed_seconds (not stale)
  - `re_roll_bio()` doesn't disturb socio_status or socio_call
  - Stale results from the cancelled call do NOT overwrite the new call's result (rely on PROJ-296 request-id versioning + explicit cancel)
- [ ] Implement: call `cancel_bio()` first, then `generate_bio()`
- [ ] Run tests, confirm pass

**Notes:**

### Task 4.5: Handle MAX_CONCURRENT_CALLS exhaustion [Medium]
**File:** Same file
**Tests:** Same file

- [ ] Write failing test:
  - When `LLMBackgroundCall.start()` raises `LLMConfigError` (because the global counter is at 3), `generate_bio()` catches it and transitions bio_status to ERROR with the exception captured. Does NOT propagate the exception to the caller.
- [ ] Implement: wrap the `call.start()` in try/except LLMConfigError → set ERROR state.
- [ ] Run test, confirm pass

**Notes:**

---

## Phase Completion Checklist
- [ ] All task checkboxes above are checked
- [ ] ~12 new tests in `test_race_description_llm_controller.py`
- [ ] `pytest tests/unit/strategy/services/` — all green
- [ ] No regression
- [ ] Update status at top of this file to `Complete`
- [ ] Update `plan.md` phase table row to `Complete`
- [ ] Update `plan.md` Current State to point to Phase 5
