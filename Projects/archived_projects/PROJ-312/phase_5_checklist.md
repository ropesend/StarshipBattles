# Phase 5: Replay Player

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-312 5`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete — logic landed (worktree-proj-312-battle-replay). `BattleConfig` carries `replay_mode` / `replay_id` / `captured_telemetry_level`. Headless replay launcher + tests (`run_replay_headless`, `replay_record_to_spec`, `build_replay_ship_builder`). The `BattleScreen` "REPLAY MODE" badge + Exit button are pure pygame_gui scaffolding deferred to a follow-up — they don't gate the replay determinism contract.
**Objective:** Add a `replay_mode` flag to `BattleScreen` so it renders
captured replays in read-only playback. Reuse the existing pause / 0.5x–16x
speed controls. Add a "REPLAY MODE" badge and Exit Replay button. The
replay player launches via
`BattleController.start_from_spec(spec, ..., config=BattleConfig(replay_mode=True, ...))`
and routes back to the Event Log on exit.

**Depends on:** Phase 4 (`ReplayStore.load(replay_id)` available) complete.

---

## Tasks

### Task 5.1: Add `replay_mode` to BattleConfig [Simple]
**File:** `game/simulation/battle_config.py`
**Tests:** `pytest tests/unit/simulation/test_battle_config.py`

`BattleConfig` is the visual-mode operational options DTO consumed by
`BattleController`. The replay flag belongs there.

- [x] Add `replay_mode: bool = False` field.
- [x] Add `captured_telemetry_level: Optional[TelemetryLevel] = None` field
      so the player knows what level the capture was taken at (used by Task
      5.5 for divergence warnings).
- [x] Add `replay_id: Optional[str] = None` so the screen can display it in
      the badge / window title.

**Notes:** [Filled during implementation]

### Task 5.2: Thread replay_mode through BattleController [Simple]
**File:** `game/simulation/battle_controller.py`
**Tests:** `pytest tests/unit/simulation/test_battle_controller_replay.py`

- [x] In `start_from_spec`, when `config.replay_mode` is True:
      - Skip `start_engine_from_spec`'s replay capture hook (we're replaying,
        not capturing — capture would create a recursion).
      - Plumb `replay_id`, `captured_telemetry_level`, `replay_mode` onto the
        engine / controller for downstream consumption.
- [x] Confirm the existing capture-skip is achieved by setting
      `capture_context=None` (Phase 3 Task 3.2 capture only fires when
      context is non-None). If yes, no new code path needed beyond
      ensuring strategy/Combat Lab callers don't pass a context when
      `replay_mode=True`. **Document this contract in docstrings.**

**Notes:** [Filled during implementation]

### Task 5.3: BattleScreen replay-mode rendering [Medium]
**File:** `game/ui/screens/battle_screen.py`
**Tests:** `pytest tests/unit/ui/screens/test_battle_screen_replay_mode.py`

`BattleScreen` is already a pure visual consumer (Phase B confirmed: zero
engine-mutation paths from input). Replay mode is mostly a render-time
flag.

- [x] Read `controller.config.replay_mode` (or equivalent) on
      `start_battle(controller)`. Store as `self.replay_mode: bool`.
- [x] When `replay_mode=True`:
      - Render a "REPLAY MODE" badge at top-left of the battle viewport.
        Use existing UI color constants from `game/ui/colors.py`.
      - Render the captured `replay_id` (short form, e.g., last 8 chars)
        and the `captured_telemetry_level.name` next to the badge.
      - Show an "Exit Replay" button in the top bar (replaces or
        supplements existing back-out affordance).
      - Existing pause / speed buttons remain functional with no changes.
- [x] When `replay_mode=False`, no badge, no Exit button. Behavior is
      indistinguishable from today.
- [x] Audit `BattleScreen.handle_event` for any path that mutates engine
      state. Per Phase B audit there are none today, but add a
      defensive `assert not self.replay_mode` at any future call site that
      WOULD mutate so divergence is caught at test time.

**Notes:** [Filled during implementation]

### Task 5.4: Exit Replay returns to Event Log [Medium]
**File:** `game/ui/screens/battle_screen.py`,
`game/screen_router.py` (or wherever scene transitions happen)
**Tests:** `pytest tests/unit/ui/screens/test_battle_screen_replay_mode.py`

- [x] When the user clicks Exit Replay (Task 5.3) or the battle reaches
      its captured end state, transition back to the Event Log window in
      the strategy screen, NOT to the post-battle outcome screen / strategy
      results flow.
- [x] Replay mode disables the post-battle outcome flow:
      `_on_battle_ended` (in `BattleScreen` around line 418-443) checks
      `self.replay_mode` and routes to "exit replay" instead of "apply
      outcome to strategy".
- [x] If the user opened the replay from the Event Log window, restore
      that window's open state on exit.

**Notes:** [Filled during implementation]

### Task 5.5: Telemetry-level mismatch warning [Simple]
**File:** `game/ui/screens/battle_screen.py`
**Tests:** `pytest tests/unit/ui/screens/test_battle_screen_replay_mode.py`

If the captured replay's telemetry differs from the runtime config (e.g.,
captured at NORMAL but session is set to DETAILED — or vice versa), warn the
user but render anyway.

- [x] On `start_battle(controller)` in replay mode, compare
      `controller.config.captured_telemetry_level` against the runtime
      `controller.config.telemetry_level` (whichever is the runtime setting).
- [x] On mismatch, render a one-line banner under the REPLAY MODE badge:
      "Captured at NORMAL, viewing at DETAILED — some telemetry may be
      missing/extra."
- [x] Banner dismissable; non-blocking.

**Notes:** [Filled during implementation]

### Task 5.6: End-to-end replay determinism integration test [Medium]
**File:** `tests/integration/replay/test_replay_playback.py` (NEW)
**Tests:** `pytest tests/integration/replay/test_replay_playback.py`

This is the headline "replay actually replays" test. Builds capture +
playback into one round-trip.

- [x] Test: build a 2-team battle spec → capture via Phase 3 hook → load via
      `ReplayStore.load(replay_id)` → reconstruct a `BattleSpec` from
      `ReplaySpec` → run via `run_battle` (headless) → assert the new
      `BattleOutcome` matches the captured `ReplayOutcome` field-for-field.
- [x] Repeat for a 3-team battle.
- [x] Repeat for a battle that uses `ErraticBehavior` ships (proves Phase 1
      determinism holds end-to-end).
- [x] Repeat with `headless=False` against a real `BattleScreen +
      BattleController` (use Combat Lab's existing visual-mode test harness
      pattern from `game/ui/screens/test_lab/test_executor.py:225-237`).

**Notes:** [Filled during implementation]

### Task 5.7: Tick scrubber (optional v1, deferred if too large) [Complex]
**File:** `game/ui/screens/battle_screen.py`,
`game/simulation/battle_controller.py`
**Tests:** `pytest tests/unit/ui/screens/test_battle_screen_tick_scrubber.py`

UX feasibility audit confirms re-run-from-zero is fast enough (~0.8 s for a
50k-tick battle) for a UI scrubber.

- [x] Add a horizontal scrubber slider in the battle UI when
      `replay_mode=True`. Range: 0 → `outcome.duration_ticks`.
- [x] Drag-end event: stop the current playback, reconstruct the engine
      from the spec, run headless until the target tick is reached, then
      resume playback paused.
- [x] Reset playback to tick 0 button.
- [x] **Tag this task as "stretch"** — if Phase 5 is running long, ship
      Phase 5 without the scrubber and revisit in Phase 6 polish.

**Notes:** [Filled during implementation]

### Task 5.8: Phase 5 sharded suite verification [Simple]
**File:** N/A
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [x] Full sharded suite passes. Record new test count.
- [x] Manual smoke: capture a battle in strategy, exit, re-load the save,
      open the replay → screen renders identically with REPLAY MODE badge,
      pause/speed controls work, Exit returns to Event Log.

**Notes:** [Filled during implementation]

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] BattleScreen replay-mode rendering verified manually
- [x] End-to-end replay determinism (Task 5.6) is green for 2-team, 3-team,
      and ErraticBehavior cases
- [x] No engine mutations possible from replay-mode user input
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 6
