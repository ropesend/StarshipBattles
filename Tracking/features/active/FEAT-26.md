# FEAT-26: Wire replay_id through to Event Log and add Replay button on combat entries

## Description
PROJ-312 captures every battle automatically to a per-save sidecar at
`output/saves/<save>/replays/replay_<uuid>.json` (ring-buffered to 50
per save), but the user has no way to open one. The
[`ReplayResolver`](../../../game/strategy/services/replay_resolver.py)
service is ready to resolve replay files for playback; the
[replay player](../../../game/simulation/battle_runner.py) supports
replay mode. The only missing piece is the wiring between the simulation
layer's `replay_id` and the strategy-layer Event Log, plus the UI
button to invoke the resolver.

## Required changes

### 1. Thread `replay_id` through `BattleResult`
- Extend `IBattleResolver.resolve_battle()` to surface the `replay_id`
  generated at
  [`battle_runner.py:187`](../../../game/simulation/battle_runner.py#L187).
- Add `replay_id: str | None` to `BattleResult`.

### 2. Log `replay_id` to the event bus
- `ConflictResolutionEngine._log_combat_result()` at
  [conflict_resolution_engine.py:99-148](../../../game/strategy/engine/conflict_resolution_engine.py#L99-L148)
  must pass `replay_id=...` into the `log_event` call so the event row
  carries it.
- Persist `replay_id` through the event row's `details=kwargs` channel
  (see
  [game_session.py:179-195](../../../game/strategy/engine/game_session.py#L179-L195))
  so saved games retain it across reload.

### 3. Add Replay button to Event Log combat rows
- In
  [event_log_window.py](../../../game/ui/screens/event_log_window.py),
  add a per-row Replay action on combat-category entries. The button
  is disabled (greyed) on rows that have no `replay_id` (legacy events
  from before this lands).
- On click: call `ReplayResolver.resolve(replay_id)`. Dispatch the
  resolved record to the existing combat renderer in replay mode
  (`BattleConfig.replay_mode=True` — see `run_replay_headless` in
  [battle_runner.py](../../../game/simulation/battle_runner.py) for
  the equivalent headless entry).
- Surface the `ReplayResolver` graceful-degradation states
  (`missing` / `corrupt` / `version_drift` / `registry_drift`) as a
  toast or modal — never a crash.
- Render a "REPLAY MODE" badge somewhere in the renderer while the
  replay is active (a simple pygame_gui label is fine for v1).

## Acceptance
- Every combat entry written after this feature lands carries a
  `replay_id` and a clickable Replay button in the Event Log.
- Clicking it plays back the captured battle in the existing combat
  renderer with the REPLAY MODE badge visible.
- Missing or corrupt sidecars surface a user-facing toast, not a
  crash.
- `BattleResult.replay_id` is populated from every battle path —
  Combat Lab, Battle Setup, and strategy-layer combat all share the
  field.
- Older saves whose event rows pre-date this change still load and
  display correctly with the Replay button disabled on those legacy
  rows.

## Out of scope
- Replay scrubbing / pause / fast-forward / playback-speed controls
  (v2 polish; v1 just plays through).
- A standalone Replay Browser screen — the project plan designates
  the Event Log as the canonical entry point. A browser screen can
  be a separate follow-up.
- Save-format migration for old saves; legacy rows just disable the
  button.
- Per-row tooltip showing replay file size or capture timestamp.

## Priority
Medium — the PROJ-312 backend is sitting idle without this, and the
user explicitly asked for the post-battle viewing capability during
QA.

## Status
Awaiting Confirmation

## Related
- **PROJ-312** (active, all 6 phases code-complete) — the project
  plan explicitly defers "UI scaffolding for the Replay button +
  REPLAY MODE badge" as a follow-up against the stable backend. This
  ticket is that follow-up.

## Work Log
- 2026-04-28: Created from QA Session 20260428_052952. User asked
  during the session whether (a) the real-time combat simulator was
  actually being used for strategy battles, and (b) post-battle
  viewing worked. Investigation confirmed (a) yes —
  `SimulationBattleResolver.resolve_battle()` → `run_battle()` is
  the unified entry — and (b) battles are captured to disk but
  cannot be opened from the UI. This ticket closes the gap.

---

### 📝 User Update [2026-04-28 19:23]

**Observation:** During QA Session 20260428_190154 [19:23:10 –
19:24:20] the user explicitly cited the missing replay capability as
a problem:

> "When combat is occurring I'm still not able to see any replay."

This confirms the gap FEAT-26 already covers is observable in the
wild — players hit it during normal play, not just in
investigation. **No scope change to this ticket.**

The same observation also surfaced an unrelated combat-resolution
bug (weaponless ship "winning" with kills=0) which has been filed
separately as
[BUG-126](../../bugs/active/BUG-126.md). FEAT-26 and BUG-126
should be considered companion fixes — closing FEAT-26 alone makes
BUG-126's "no replay to verify what really happened" symptom
disappear, but the underlying simulation-shortcut behaviour remains
until BUG-126 is also addressed.

---

- 2026-04-29: Implementation landed on branch `worktree-feat-feat-26`
  off main (post-BUG-123 d4eabd657 + post-BUG-126 2868fea55).
  Plumbing path threads `engine.replay_id` through `BattleOutcome`
  (`battle_outcome.py`) → `BattleResult` (`battle_resolver.py`) →
  `COMBAT_RESOLVED.details["replay_id"]` (`conflict_resolution_engine.py`).
  Empty-string canonicalisation at the `extract_outcome` seam keeps
  "no replay" a single signal. UI: new generic `replay_action`
  single-button column type in `VirtualTable` (distinct from the
  build-queue 4-button `actions` column); `EventLogWindow` accepts
  `replay_resolver` + `launch_replay_callback` kwargs and dispatches
  per-row clicks through `_handle_replay_click`; `EventLogRegistrar`
  builds `ReplayResolver.from_registries(...)` from the active save's
  `ReplayStore` + the loaded component registry; new
  `Game.start_replay(record)` wraps `replay_record_to_spec` +
  `BattleConfig(replay_mode=True, replay_id=..., captured_telemetry_level=...)`
  through the widened `screen_router.start_battle(spec, *, headless=False, config=None)`.
  `BattleScreen.draw_hud` renders a top-center "REPLAY MODE" badge
  when `controller.config.replay_mode is True`. Graceful-degradation
  on missing/corrupt/version_drift surfaces a `UIMessageWindow`
  toast; registry_drift warns and proceeds with launch.

  **Tests** (37 new): `test_battle_outcome_replay_id.py`,
  `test_battle_resolver_replay_id.py`,
  `test_conflict_resolution_event_replay.py`,
  `test_simulation_adapter.py::TestSimulationAdapterReplayId`,
  `test_event_log_replay_button.py`, `test_event_log_data_source.py`
  (column-count assertions bumped 8 → 9),
  `test_event_log_graceful_degradation.py`,
  `test_event_log_replay_e2e.py`. Full regression
  (`pytest tests/ -n 12`): **16122 passed, 3 skipped, 0 failures**
  (sharded runner has a pre-existing escape-sequence bug on Python
  3.13 unrelated to FEAT-26; xdist `-n 12` is the documented
  alternative per CLAUDE.md).

  **Deferred to follow-up tickets** (per loose-acceptance interpretation
  approved by team-lead):
  - Combat Lab + Battle Setup capture (only strategy battles
    populate `replay_id` in v1; the field exists on every
    `BattleResult` regardless).
  - `engine.replay_id` typed-attribute cleanup (currently
    `# type: ignore[attr-defined]` on `BattleEngine`).
  - `docs/systems/strategy_layer.md` replay capture/playback section
    (file held by FEAT-27 during this implementation; will land in a
    separate follow-up doc PR after FEAT-27 merges).

---
