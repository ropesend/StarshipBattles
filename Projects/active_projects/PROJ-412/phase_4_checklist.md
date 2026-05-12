# Phase 4: UI Progress-Callback Coarsening (highest measured single win)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-412 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete (2026-05-12)
**Objective:** Reduce the per-tick UI redraw cost that the codex consult traced to [`game/ui/screens/strategy_game_state_manager.py:170-177`](../../../game/ui/screens/strategy_game_state_manager.py#L170) (`pygame.event.pump() + self._screen.draw(surface) + pygame.display.flip()` per tick × 100 ticks). The Phase 1.4 Probe B measurement showed that a 5-ms-per-tick callback adds **+543 ms / turn**; the user's real callback at 4K does similar work and almost certainly accounts for the bulk of the 2.5–3.7 s unaccounted-overhead gap.

This phase was originally Task 5.3. **Promoted from Phase 5 → Phase 4** because Probe B identified it as the single largest measurable win on the user's real game.

**Outcome:** Callback now fires at tick 1, every `PROGRESS_CALLBACK_INTERVAL` ticks (default 5), and tick 100 — 21 invocations per turn instead of 100. Interval is user-configurable via `output/settings/turn_engine_settings.json`. Repeated probe with a 5 ms synthetic callback: +543 ms / turn → **+114 ms / turn (~80% reduction)**. UX-visible effect: the "Tick N / 100" overlay advances in jumps of 5; both endpoints (1/100 and 100/100) still display. New `turn_engine_settings.py` module + 10 unit tests covering missing-file / corrupt-JSON / clamping. `docs/systems/strategy_layer.md` updated.

---

## Tasks

### Task 4.1: Add a contract test pinning the new callback cadence [Simple]

**File:** `tests/unit/strategy/turn_engine/test_turn_engine_progress_callback.py` (existing)
**Tests:** `pytest tests/unit/strategy/turn_engine/test_turn_engine_progress_callback.py -v`

- [ ] Read the existing test (codex consult: it pins exactly 100 invocations per turn at lines ~35-43)
- [ ] Add a new test that pins the new contract: **callback fires at tick 1, every Nth tick thereafter, and at tick 100** (so the UI always sees both endpoints). For default N=5: 1, 5, 10, 15, …, 95, 100 ⇒ 21 invocations per turn.
- [ ] The current "exactly 100 invocations" test must be retired or rewritten because the new cadence is a deliberate behavior change
- [ ] Failing test first: assert the new cadence against current code — should fail since current code fires every tick. Then implement Task 4.2 to make it pass.

**Notes:**

### Task 4.2: Implement callback cadence in `TurnEngine._process_tick` [Medium]

**File:** `game/strategy/engine/turn_engine.py`
**Tests:** Task 4.1's new cadence test; existing `test_turn_engine_progress_callback.py`; `bench_turn_processing.py`

- [ ] Read the current per-tick callback site at [turn_engine.py:695-703](../../../game/strategy/engine/turn_engine.py#L695)
- [ ] Add `PROGRESS_CALLBACK_INTERVAL = 5` module constant (or make it a `TurnEngine.__init__` kwarg if tests need different cadences — pick the smaller change)
- [ ] Fire the callback only when `tick == 1 or tick % PROGRESS_CALLBACK_INTERVAL == 0 or tick == TICKS_PER_TURN`. This guarantees the UI always sees the first and last tick and gets a regular cadence in between.
- [ ] The exception-suppression / try-except / WARNING log behaviour stays identical
- [ ] Verify: Task 4.1's new test passes; bench shows ~80% reduction in callback-related overhead on a probe with a synthetic 5-ms callback (i.e. baseline +543 ms drops to ~+110 ms)

**Notes:**

### Task 4.3: Update the UI callback comment & docs for the new contract [Simple]

**Files:** `game/ui/screens/strategy_game_state_manager.py` (just the comment block), `docs/systems/strategy_layer.md` (Progress callback section)
**Tests:** n/a (doc + comment)

- [ ] Update the inline `# Issue #7` comment in `strategy_game_state_manager.py:165-169` to note the new cadence: "fires at tick 1, every Nth tick, and tick 100 — see TurnEngine.PROGRESS_CALLBACK_INTERVAL"
- [ ] Update `docs/systems/strategy_layer.md` (the "Progress callback" section near line 200-207) to document the new cadence
- [ ] Note in the progress overlay UX: the "Tick N / 100" overlay will jump in increments of N rather than every tick — visible only as a slightly chunkier counter, not a UX regression

**Notes:**

### Task 4.4: Surface the UX change for user approval [Simple]

**File:** n/a (user checkpoint)
**Tests:** n/a

- [ ] Before merging, surface the new cadence to the user with a short before/after summary of the "PROCESSING TURN..." overlay update frequency
- [ ] Ask whether N=5 is acceptable, or whether the user prefers a different cadence (N=10, N=20, or "only update on phase boundaries")
- [ ] Record the chosen N in `decisions.md`

**Notes:**

---

## Phase Completion Checklist

When all tasks above are done:

- [ ] All task checkboxes above are checked
- [ ] New cadence test green; old "exactly 100" test removed or rewritten
- [ ] `bench_turn_processing.py` not regressed (the bench runs with `progress_callback=None`, so it should be unchanged)
- [ ] Existing rollback-on-failure tests still green
- [ ] User approved the new cadence value (Task 4.4)
- [ ] `docs/systems/strategy_layer.md` updated
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 5
