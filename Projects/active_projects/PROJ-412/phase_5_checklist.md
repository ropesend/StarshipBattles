# Phase 4: Orchestration Overhead (snapshot, progress callback, `_run_phases`)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-412 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Address the 2.5–3.7 s "unaccounted overhead" gap. Specifically: `TurnStateSnapshot.capture`, the per-tick `progress_callback`, and the per-call cost of `_run_phases`. Only the items Phase 1 measurement actually confirms as material proceed.

---

## Tasks

### Task 4.1: Reduce `TurnStateSnapshot.capture` cost [Medium]

**Files:** `game/strategy/engine/turn_state_snapshot.py`, `game/strategy/engine/turn_engine.py`
**Tests:** rollback-on-failure tests in `tests/unit/strategy/turn_engine/`; bench

- [ ] Identify what `TurnStateSnapshot.capture` actually copies (full `empire.to_dict()` + `galaxy.to_dict()` per swarm-03)
- [ ] Narrow the snapshot to the fields actually needed by `restore` — likely only `resource_pool`, `colonies[*].stockpile`, `colonies[*].facilities`, and fleet `ships[*].components`. Confirm by reading `TurnStateSnapshot.restore`.
- [ ] Failing test first: a unit test asserts that `capture` + `restore` round-trips the minimal-fields set without functional regression
- [ ] If the snapshot is heavyweight even after narrowing, consider copy-on-write — but only if Phase 1 measurement justifies the additional complexity
- [ ] Verify: existing rollback-on-`EnginePhaseError` tests still pass; bench shows reduction in the per-turn one-time cost

**Notes:**

### Task 4.2: Trim per-tick orchestration cost in `_run_phases` [Medium]

**Files:** `game/strategy/engine/turn_engine.py`, `game/strategy/engine/turn_phase_registry.py`
**Tests:** `tests/unit/strategy/turn_engine/`; bench

- [ ] Confirm Phase 1's measurement that `_run_phases` adds ≈ 100–200 ms per turn over 1500 invocations
- [ ] Move `from game.core.exceptions import EnginePhaseError; from game.core.error_codes import ErrorCode` out of `_time_phase` (likely already done in Phase 2)
- [ ] Consider pre-resolving `phase.callable_target(self)` and `phase.timing_bucket` *once* per `TurnEngine` instance instead of every tick. Store a flat list of (callable, args_resolver, bucket_key, pre_hook, post_hook) tuples on `__init__`. Re-derive only if `tick_phases` is replaced (tests do this).
- [ ] Avoid allocating fresh tuples inside `args_resolver` callbacks when the args are constant per-tick — but only if the descriptor change does not require touching the frozen descriptor list contract
- [ ] Failing test first: assert that the new `_run_phases` still routes through `_time_phase`, still wraps exceptions as `EnginePhaseError`, still honors pre/post hooks
- [ ] Verify: golden tests `test_default_tick_phase_list.py` / `test_default_end_of_turn_phase_list.py` still green; `test_turn_engine_phase_timing.py` still green

**Notes:**

### Task 4.3: Investigate the `progress_callback` overhead [Medium]

**Files:** wherever the UI registers its progress callback (likely `game/ui/screens/strategy_screen.py` or `game/strategy/facade/strategy_session_facade.py`); `game/strategy/engine/turn_engine.py`
**Tests:** characterization test for the callback contract; bench

- [ ] Use Phase 1 Task 1.4 Probe B's measurement: if a noop callback yields ≥ 200 ms / turn improvement, the UI side is doing real work
- [ ] Find the UI callback implementation; document what it does per tick (likely a pygame event pump or partial redraw)
- [ ] Options to evaluate, in order of preference:
  - (a) Coalesce: only invoke the callback every Nth tick (e.g. every 5 ticks → 20 callback calls/turn instead of 100). This is a UX trade-off — surface it to the user.
  - (b) Move the UI repaint out of the callback into a separate thread / async pump. Risky; only if (a) is unacceptable.
  - (c) If the callback is purely event-pumping for responsiveness, consider whether the existing pygame loop already covers that and the per-tick callback is redundant.
- [ ] **User checkpoint required**: any UX-visible change (e.g. coarser progress bar) needs explicit approval before merging
- [ ] Failing test first: contract test pinning the new callback cadence
- [ ] Verify: bench shows the expected reduction; the UI still updates the "Tick N / 100" overlay visibly during a turn

**Notes:**

---

## Phase Completion Checklist

When all tasks above are done:

- [ ] All task checkboxes above are checked
- [ ] `bench_turn_processing.py` shows the unaccounted-overhead gap from Phase 1 reduced by ≥ 50%
- [ ] Rollback-on-failure tests still green
- [ ] `test_turn_engine_progress_callback.py` updated to reflect the new cadence (and remains green)
- [ ] Phase descriptor golden tests still green (no reorder, no rename)
- [ ] No regression in mid-turn characterization tests
- [ ] User signed off on any UX-visible cadence change to the progress overlay
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 5
