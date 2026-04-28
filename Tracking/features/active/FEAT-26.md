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
Pending

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
