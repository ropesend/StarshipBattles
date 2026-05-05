# Phase 3: Capture Pipeline

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-312 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete (worktree-proj-312-battle-replay; 15708/15708 passing)
**Objective:** Hook the unified battle entry/exit codepath to snapshot the
input `BattleSpec` and output `BattleOutcome` for every battle. Capture is
in-memory only at this stage — Phase 4 adds persistence. Capture must cover
both visual (`BattleController.start_from_spec`) and headless (`run_battle`)
callers without runtime overhead measurable in profiles.

**Depends on:** Phase 2 (ReplaySpec + ReplayOutcome serialization) complete.

---

## Tasks

### Task 3.1: Define the capture interface [Simple]
**File:** `game/simulation/replay/replay_capture.py` (NEW)
**Tests:** `pytest tests/unit/simulation/replay/test_capture_interface.py`

Capture is a strategy/UI-layer concern (writes to disk). The simulation
layer only fires events. Define a Protocol the upper layers implement.

- [x] Create `IReplayCaptureSink` Protocol in `replay_capture.py`:
      ```python
      class IReplayCaptureSink(Protocol):
          def on_battle_started(self, replay_spec: ReplaySpec, *,
                                context: ReplayCaptureContext) -> str: ...
              # returns replay_id for the outcome callback
          def on_battle_ended(self, replay_id: str,
                              outcome: ReplayOutcome) -> None: ...
      ```
- [x] Define `ReplayCaptureContext` frozen dataclass with `sector_name`,
      `sector_coords`, `turn_number`, `participating_empires`,
      `components_registry_hash`, `captured_at`. Filled by the caller (see
      Task 3.4) — strategy / Combat Lab / Battle Setup each pass their own
      context.
- [x] Module-level `get_default_capture_sink() / set_default_capture_sink()`
      accessor pair (mirrors `ApplicationContext` DI pattern in
      `docs/02_PATTERNS.md` §1).
- [x] Default sink is a `NullCaptureSink` no-op so simulation works without a
      registered sink (Combat Lab tests, headless CI).

**Notes:** [Filled during implementation]

### Task 3.2: Hook `start_engine_from_spec` for input capture [Medium]
**File:** `game/simulation/battle_runner.py`
**Tests:** `pytest tests/integration/replay/test_capture_pipeline.py`

`start_engine_from_spec` is the shared lower-level helper called by both
`run_battle` and `BattleController.start_from_spec`. ONE hook covers both.

- [x] Add an optional `capture_context: Optional[ReplayCaptureContext] = None`
      parameter to `start_engine_from_spec` (and its callers).
- [x] After the engine is constructed and seed is plumbed but BEFORE the
      tick loop, build a `ReplaySpec` via
      `ReplaySpec.from_battle_spec(spec, ship_instance_lookup=...)`.
- [x] Call `sink.on_battle_started(replay_spec, context=capture_context)` if
      both `capture_context` is non-None AND
      `get_default_capture_sink()` returns a non-null sink.
- [x] Capture the returned `replay_id`; thread it through to the engine /
      controller as `engine.replay_id` so the outcome hook can correlate.
- [x] Build `ship_instance_lookup`: walk the spec's nested ShipSpecs, for
      each one with `instance_ref is not None` call
      `ShipInstanceSerializer.to_dict(instance_ref)` to capture the
      strategy-side state at battle entry. ShipSpecs without an
      `instance_ref` (e.g., Combat Lab synthetic ships) get `None` snapshot.

**Notes:** [Filled during implementation]

### Task 3.3: Hook `extract_outcome` for output capture [Simple]
**File:** `game/simulation/battle_runner.py`
**Tests:** `pytest tests/integration/replay/test_capture_pipeline.py`

- [x] After `extract_outcome(engine, spec)` returns, build a `ReplayOutcome`
      from the resulting `BattleOutcome`.
- [x] If `engine.replay_id` was set in Task 3.2, call
      `sink.on_battle_ended(engine.replay_id, replay_outcome)` BEFORE the
      `post_battle_hook` runs (so capture cannot be perturbed by hook side
      effects).
- [x] If capture was not started (no context, or sink is null), skip the
      outcome callback.

**Notes:** [Filled during implementation]

### Task 3.4: Strategy-layer capture context [Medium]
**File:** `game/strategy/combat/spec_compiler.py` (likely)
**Tests:** `pytest tests/integration/replay/test_strategy_capture_context.py`

Each spec compiler builds the `ReplayCaptureContext` reflecting *its* domain
inputs. Strategy is the primary path for replay capture.

- [x] Locate `build_strategy_battle_spec` (Pattern #13 in
      `docs/02_PATTERNS.md`). Extend the call site (in
      `ConflictResolutionEngine` or wherever it's invoked) to build a
      `ReplayCaptureContext` containing:
      - `sector_name`: derived from system + hex
      - `sector_coords`: the contested hex `(q, r)`
      - `turn_number`: from `GameSession.current_turn` or equivalent
      - `participating_empires`: tuple of empire display names (in team order)
      - `components_registry_hash`: stable hash of `data/components.json`
        contents at game start (cached per session — see Task 3.6)
      - `captured_at`: `datetime.utcnow().isoformat()`
- [x] Pass the context through to `run_battle` / `start_from_spec`.

**Notes:** [Filled during implementation]

### Task 3.5: Combat Lab + Battle Setup capture contexts [Simple]
**File:** `combat_lab/spec_compiler.py`,
`game/ui/screens/battle_setup/spec_compiler.py`
**Tests:** `pytest tests/integration/replay/test_combat_lab_capture.py`

- [x] Combat Lab: build a `ReplayCaptureContext` with `sector_name="Combat
      Lab"`, `sector_coords=None`, `turn_number=None`,
      `participating_empires=("Test",)` (or scenario name).
- [x] Battle Setup (manual-mode UI): similarly populate with
      `sector_name="Manual Battle"`, etc.
- [x] Document in
      `docs/guides/simulation_testing.md` that Combat Lab battles ARE
      captured by default — useful for replay-based regression debugging.

**Notes:** [Filled during implementation]

### Task 3.6: Components registry hash helper [Simple]
**File:** `game/simulation/replay/replay_serialization.py`
**Tests:** `pytest tests/unit/simulation/replay/test_components_hash.py`

Used for drift detection (Phase 6 surfaces warnings on registry mismatch).

- [x] Add `compute_components_registry_hash(registries) -> str` returning a
      stable SHA256 of `(component_id, ability_dict)` tuples sorted by id.
      The function should be deterministic across runs given identical
      `components.json` contents.
- [x] Cache the result per-session if it appears on a hot path. (Compute
      once at game start, reuse for every battle.)

**Notes:** [Filled during implementation]

### Task 3.7: Telemetry-level pinning [Simple]
**File:** `game/simulation/replay/replay_capture.py`
**Tests:** `pytest tests/integration/replay/test_telemetry_pinning.py`

The captured telemetry level must be embedded in the `ReplaySpec` so playback
can warn on mismatch (Phase 5).

- [x] Confirm `ReplaySpec` already serializes `telemetry_level` (Phase 2
      Task 2.5). If yes, no work needed here beyond a regression test:
      capture a battle at DETAILED, deserialize, assert
      `replay_spec.telemetry_level == "DETAILED"`.

**Notes:** [Filled during implementation]

### Task 3.8: N-team capture parity [Simple]
**File:** `tests/integration/replay/test_capture_n_team.py` (NEW)
**Tests:** `pytest tests/integration/replay/test_capture_n_team.py`

PROJ-275 supports 2-8 teams with non-sequential team_ids.

- [x] Test capture/round-trip for 2-team battle (baseline).
- [x] Test capture/round-trip for 3-team battle.
- [x] Test capture/round-trip for 5-team battle with non-sequential team_ids
      `{1, 3, 5, 7, 9}`.
- [x] For each, assert `ReplaySpec.teams` length and `team_id` values are
      preserved across round-trip.

**Notes:** [Filled during implementation]

### Task 3.9: Phase 3 sharded suite verification [Simple]
**File:** N/A
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [x] Full sharded suite passes. Record new test count.
- [x] Profile a representative battle with capture enabled vs disabled;
      confirm overhead is ≤2% per-battle (capture is once-per-battle, not
      per-tick).

**Notes:** [Filled during implementation]

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] `IReplayCaptureSink` is documented as the simulation→strategy boundary
- [x] Capture is verified to fire for `run_battle`, `start_from_spec`, AND
      Combat Lab + Battle Setup paths
- [x] N-team determinism test (Task 3.8) is green
- [x] No measurable per-tick performance impact
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 4
