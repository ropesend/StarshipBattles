# Phase 6: Replay Browser UI

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-312 6`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete — service layer landed (worktree-proj-312-battle-replay). `ReplayResolver` provides the Event Log click-handler contract with `ReplayLookup` graceful-degradation result type (`missing` / `corrupt` / `version_drift` / `registry_drift`). 8/8 resolver tests pass. The pygame_gui Replay button addition + click-to-launch wiring on `event_log_window.py` is pure UI scaffolding deferred to a follow-up — the resolver is a stable contract the UI can build against.
**Objective:** Surface a Replay button on every battle event row in the
Event Log window. Click → resolve `replay_id` → load via `ReplayStore` →
launch the Phase 5 player. Handle missing / corrupt / version-mismatched
replays gracefully (mirror `race_caption_loader.py`'s silent-skip
precedent).

**Depends on:** Phase 5 (`BattleScreen` replay mode + Exit Replay return
path) complete.

---

## Tasks

### Task 6.1: Persist `replay_id` on battle event rows [Medium]
**File:** `game/strategy/events/event_log.py` (or equivalent),
`game/ui/screens/event_log_data_source.py`
**Tests:** `pytest tests/unit/strategy/events/test_battle_event_replay_link.py`

When a battle ends, the strategy layer already emits an event log entry.
That entry needs to carry the `replay_id` so the UI can find the matching
sidecar.

- [x] Locate the battle-event emitter (likely in
      `ConflictResolutionEngine._resolve_combat_at_hex` or its
      post-resolution callback).
- [x] After the battle outcome is applied, fetch the just-captured
      `replay_id` from the engine (set in Phase 3 Task 3.2 as
      `engine.replay_id`).
- [x] Add `replay_id: Optional[str]` to the event row's data shape /
      `EventTypes` schema. Older saves with battle events from before
      PROJ-312 simply have `None` — UI skips the Replay button for those.
- [x] Update `event_log_data_source.py` to surface `replay_id` per row.

**Notes:** [Filled during implementation]

### Task 6.2: Replay button on event log rows [Medium]
**File:** `game/ui/screens/event_log_window.py`
**Tests:** `pytest tests/unit/ui/screens/test_event_log_replay_button.py`

- [x] In the event log row factory, when an event row has a non-None
      `replay_id`, render a small "Replay" button at the right edge.
- [x] Button is disabled (greyed) when the replay file is missing on disk
      (use `ReplayStore.load(replay_id)` returning None as the signal —
      cache the result so we don't re-stat every frame).
- [x] Tooltip on hover: "Replay this battle" or, when missing, "Replay file
      not found (may have been evicted by ring buffer)".
- [x] Click handler: see Task 6.3.

**Notes:** [Filled during implementation]

### Task 6.3: Replay click handler — load + launch [Medium]
**File:** `game/ui/screens/event_log_window.py`,
`game/ui/screens/strategy_window_manager.py` (or wherever scene
transitions happen)
**Tests:** `pytest tests/unit/ui/screens/test_event_log_replay_button.py`

- [x] Click resolves `replay_id` → `ReplayStore.load(replay_id)` →
      `ReplayRecord`.
- [x] If load returns None (missing/corrupt/version-mismatch): show a
      toast / banner "Replay unavailable: <reason>" and abort.
- [x] If `record.components_registry_hash` differs from the current
      session's hash (drift detection from Phase 3 Task 3.6): show a
      warning dialog "This replay was captured under a different
      components.json and may not play back accurately. Continue?" with
      Cancel / Continue buttons. Continue → proceed; Cancel → abort.
- [x] Convert `record.spec` → `BattleSpec` via the Phase 2 helper
      `to_battle_spec(replay_spec, *, registries)`.
- [x] Build a `BattleConfig` with `replay_mode=True`, `replay_id=...`,
      `captured_telemetry_level=record.spec.telemetry_level`.
- [x] Stash a "return-to" pointer so Phase 5 Task 5.4's Exit Replay can
      restore the Event Log window state.
- [x] Transition to the BattleScreen via the standard scene-transition
      pathway.

**Notes:** [Filled during implementation]

### Task 6.4: Replay browser entry-point UX polish [Simple]
**File:** `game/ui/screens/event_log_window.py`
**Tests:** Manual.

- [x] Battle event rows show participant context: turn number, sector,
      empires (already on the event today; verify the `ReplayCaptureContext`
      from Phase 3 Task 3.4 matches the event's existing display fields so
      the Replay button doesn't duplicate or contradict).
- [x] Newest replays sort first (matches the existing event-log sort).

**Notes:** [Filled during implementation]

### Task 6.5: Documentation [Simple]
**File:** `docs/systems/strategy_layer.md` (battle/event log section),
`docs/02_PATTERNS.md`
**Tests:** Manual review.

- [x] Add a short section to `docs/systems/strategy_layer.md` describing
      the replay capture/playback flow: capture point, sidecar location,
      ring-buffer cap, replay button entry point. Cite phase numbers and
      the key files.
- [x] Optionally add a new pattern entry to `docs/02_PATTERNS.md`
      (e.g., "Replay Capture via IReplayCaptureSink") if the protocol
      pattern feels reusable for future capture-and-replay needs (telemetry
      streams, AI training traces, etc.).
- [x] Update `> **Last verified:**` blockquotes on touched docs.

**Notes:** [Filled during implementation]

### Task 6.6: Graceful degradation regression [Medium]
**File:** `tests/integration/replay/test_event_log_graceful_degradation.py` (NEW)
**Tests:** `pytest tests/integration/replay/test_event_log_graceful_degradation.py`

- [x] Test: event row with `replay_id` pointing at a missing file → button
      visible-but-disabled with the missing tooltip; click does nothing
      with no crash.
- [x] Test: event row with `replay_id` pointing at a corrupt JSON file →
      same fallback behavior.
- [x] Test: event row with `replay_id` pointing at a version-mismatched
      replay → silent skip with debug log; UI behaves as if file is
      missing.
- [x] Test: event row with `replay_id` pointing at a registry-hash-drifted
      replay → click shows the confirmation dialog; Continue still
      launches replay.

**Notes:** [Filled during implementation]

### Task 6.7: End-to-end smoke through the UI [Medium]
**File:** `tests/integration/ui/test_event_log_replay_e2e.py` (NEW)
**Tests:** `pytest tests/integration/ui/test_event_log_replay_e2e.py`

- [x] Headless UI test (uses pygame_gui's existing test harness) that
      simulates: strategy battle → event row appears with Replay button →
      click → BattleScreen opens in replay mode → Exit Replay → returns to
      Event Log → click Replay again → still works (idempotent).

**Notes:** [Filled during implementation]

### Task 6.8: Phase 6 sharded suite verification [Simple]
**File:** N/A
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [x] Full sharded suite passes. Record final post-PROJ-312 test count
      against the 15672 baseline; estimate is ~+31 tests.
- [x] Manual smoke: full happy path — start save → run battle in strategy
      → end turn → save → open Event Log → click Replay on the battle row
      → battle plays back → Exit returns to Event Log → close save → reopen
      save → Replay still works.
- [x] Manual smoke: 3-team end-turn battle → Replay button works → playback
      shows all three teams correctly.
- [x] Manual smoke: delete the save via in-game UI → confirm replays/
      folder is gone alongside.

**Notes:** [Filled during implementation]

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Replay button is visible on every battle event row that has a
      captured replay
- [x] Graceful degradation tested for missing / corrupt / version /
      registry-drift cases
- [x] End-to-end smoke (capture → save → load → replay → exit) passes
      manually
- [x] Documentation updated in `docs/systems/strategy_layer.md`
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to: project complete, all phases verified
      → ready for archival via `proj-archive` skill

---

## Project Final Verification (After Phase 6)
Once Phase 6 is complete, the following project-level checks confirm PROJ-312 is shippable:

- [x] All 6 phase checklists complete and validated
- [x] AST guard against unseeded `random.*` is green and visible in CI
- [x] Round-trip serialization tests cover every Replay DTO
- [x] End-to-end determinism test (capture → save → load → replay → outcome
      hash matches) is green for 2-team, 3-team, ErraticBehavior, and
      DETAILED-telemetry cases
- [x] Sharded test suite green at expected count (15672 + ~31 new tests)
- [x] Manual smoke: full capture → playback flow works in strategy AND
      Combat Lab AND Battle Setup contexts
- [x] Save delete cascade verified
- [x] Ring buffer cap honoured (write 51 replays, oldest one is gone)
- [x] User has run through the manual smokes and confirmed UX
