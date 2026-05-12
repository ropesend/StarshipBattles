# Phase 6: Remaining Orchestration (snapshot, `_run_phases`)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-412 6`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** The remaining orchestration items after the callback was promoted into Phase 4. Specifically: `TurnStateSnapshot.capture` and the per-call cost of `_run_phases`. Both are gated on remeasurement — Phase 1 Probe A showed snapshot saves only 0.7 ms / turn on the synthetic bench, so this phase may be cut entirely on the user's real game.

Both tasks are independently optional. Drop either if Phase 1 / 5 remeasurement shows < 50 ms / turn impact.

---

## Tasks

### Task 6.1: Reduce `TurnStateSnapshot.capture` cost [Medium] ⚠ gated on remeasurement

**Files:** `game/strategy/engine/turn_state_snapshot.py`, `game/strategy/engine/turn_engine.py`
**Tests:** rollback-on-failure tests in `tests/unit/strategy/turn_engine/`; bench

- [ ] Phase 1 Probe A showed only **0.7 ms / turn** savings on the synthetic bench. Before doing any work, rerun the probe on the user's actual save game. If the saving is still < 50 ms / turn → **cut this task** and record in decisions.md.
- [ ] If the user-game probe shows material cost: identify what `TurnStateSnapshot.capture` actually copies (full `empire.to_dict()` + `galaxy.to_dict()` per [turn_state_snapshot.py:53-68](../../../game/strategy/engine/turn_state_snapshot.py#L53))
- [ ] Narrow the snapshot to the fields actually needed by `restore` — likely `resource_pool`, `colonies[*].stockpile`, `colonies[*].facilities`, fleet `ships[*].components`. Confirm by reading `TurnStateSnapshot.restore`.
- [ ] Failing test first: a unit test asserts that `capture` + `restore` round-trips the minimal-fields set without functional regression
- [ ] If still heavyweight after narrowing, consider copy-on-write — but only if real-game measurement justifies the additional complexity
- [ ] Verify: existing rollback-on-`EnginePhaseError` tests still pass; bench shows reduction in the per-turn one-time cost

**Notes:**

### Task 6.2: Trim per-tick orchestration cost in `_run_phases` [Medium] ⚠ gated on remeasurement

**Files:** `game/strategy/engine/turn_engine.py`, `game/strategy/engine/turn_phase_registry.py`
**Tests:** `tests/unit/strategy/turn_engine/`; bench

- [ ] Phase 1 named-phase breakdown shows no measurable orchestration overhead on the synthetic bench (sum-of-phases ≈ total). On the user's real game the gap was ~30–45%, but Probe B identified the callback as the primary culprit. Confirm any remaining unaccounted overhead after Phase 4 (callback) lands before doing this work. If < 50 ms / turn → **cut this task**.
- [ ] If still material: move `from game.core.exceptions import EnginePhaseError; from game.core.error_codes import ErrorCode` out of `_time_phase` (likely already done in Phase 2 — confirm)
- [ ] Consider pre-resolving `phase.callable_target(self)` and `phase.timing_bucket` *once* per `TurnEngine` instance instead of every tick. Store a flat list of (callable, args_resolver, bucket_key, pre_hook, post_hook) tuples on `__init__`. Re-derive only if `tick_phases` is replaced (tests do this).
- [ ] Avoid allocating fresh tuples inside `args_resolver` callbacks when the args are constant per-tick — but only if the descriptor change does not require touching the frozen descriptor list contract
- [ ] Failing test first: assert that the new `_run_phases` still routes through `_time_phase`, still wraps exceptions as `EnginePhaseError`, still honors pre/post hooks
- [ ] Verify: golden tests `test_default_tick_phase_list.py` / `test_default_end_of_turn_phase_list.py` still green; `test_turn_engine_phase_timing.py` still green

**Notes:**

---

## Phase Completion Checklist

When all tasks above are done (or explicitly cut after remeasurement):

- [ ] All task checkboxes above are checked or task is cut + recorded in decisions.md
- [ ] `bench_turn_processing.py` not regressed
- [ ] Rollback-on-failure tests still green
- [ ] Phase descriptor golden tests still green (no reorder, no rename)
- [ ] No regression in mid-turn characterization tests
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 7
