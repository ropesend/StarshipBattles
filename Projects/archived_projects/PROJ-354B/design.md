# PROJ-354B: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Origin

This project implements C4–C9 of the consensus plan at:
`AgentCoordination/Scratchpad/Discussion/20260505T034554Z_replay-end-state-verification/plans/replay_end_state_verification_r003.md`

That plan was the output of a 5-message inter-agent discussion between Claude and Codex. PROJ-354A is the sibling that implements C1–C3 (capture-side fidelity).

## Initial Analysis

### What we're building

A background verification subsystem that runs every captured replay through a deterministic re-run, compares the new outcome to the captured outcome, and writes a sidecar JSON file recording the verification result. Designed for a heavily moddable game: divergence between live and replay outcomes surfaces mod-induced determinism breaks the user couldn't otherwise see.

### High-level data flow

```
[live battle ends in run_battle]
       │
       ▼
[ReplayStore.on_battle_ended → persist(record) → on_record_persisted listeners fire]
       │
       ▼
[ReplayVerificationCoordinator._on_record_persisted (listener callback)]
       │
       ├── verification_enabled=False → write SKIPPED_DISABLED sidecar, done
       ├── queue full → write SKIPPED_QUEUE_FULL sidecar, done
       └── enqueue record into FIFO
              │
              ▼
       [worker thread, single, FIFO]
              │
              ▼
       _verify_one(record)
              │
              ├── build_replay_ship_builder(record, registry_provider, fallback_builder)
              ├── run_replay_headless(record, ai_factory, ship_builder, registry_provider)
              │      └── capture_context=None → no recursion (R5 mitigation)
              ├── verify_replay_outcome(record, replayed_outcome) -> ReplayVerificationResult
              └── write sidecar (PASSED / FAILED with diff / ERROR with exception info)
```

### Why this design (key constraints)

1. **Triggered post-persist of live battles, not user-clicks-Replay.** The user requirement is "background process that occurs when the simulator ends combat." Visual replay launch could ALSO verify (future opt-in), but the primary mode is live-capture-time.

2. **Pure verifier separated from background coordinator.** Per `docs/01_ARCHITECTURE.md` layer rules, the verifier (in `game/simulation/replay/`) imports only simulation/replay DTOs. The coordinator (in `game/strategy/services/`) is allowed to import simulation downward + ApplicationContext-injected services. This separation:
   - Enables the verifier to be reused in tests (and any future consumer) without depending on Strategy.
   - Keeps the threading + queue concerns out of the layer-pure verifier.

3. **Listener-based extension to `ReplayStore`.** Adding an `on_record_persisted` callback is preferable to threading the call through `SaveGameService` because:
   - It's a Replay-specific concern; `SaveGameService` shouldn't know about verification.
   - List-based listeners future-proof for additional subscribers (e.g., telemetry, debug tooling).
   - Failure isolation: each listener's exception is caught individually so one bad subscriber doesn't break others or the persist itself.

4. **Sidecar JSON, separate schema version.** Mutating the immutable `ReplayRecord` JSON to add verification status would break the atomic-write semantics. Sidecar avoids this. Separate `REPLAY_VERIFICATION_SCHEMA_VERSION` because verification schema lifecycle is independent.

5. **Single FIFO worker, queue cap 16, no thread-level hard timeout.** Codex pushback (r004) on hard timeout: a Python thread cannot terminate CPU-burning code without a process boundary. Process-boundary worker is out of scope; queue cap + drop-on-full provides bounded mitigation. If a hostile mod stalls the worker, subsequent verifications are dropped to `SKIPPED_QUEUE_FULL` sidecars — user sees the elision, can disable verification, can investigate.

6. **Test boundary at `BattleController.start_from_spec`, not `BattleScreen`.** Both paths route through `start_engine_from_spec` → `run_battle`, so equivalence at this boundary proves end-to-end equivalence. `BattleScreen` would couple tests to Pygame UI.

## Swarm Findings Summary

Three Explore agents ran during planning. Reports in `findings/` (not yet generated).

### Architecture (Agent 2: LLMBackgroundCall + composition root)

- `LLMBackgroundCall` (`game/services/llm/background.py:65-368`) is the canonical template:
  - Per-instance `threading.Lock` for state.
  - `threading.Event` for done signaling and cancel.
  - Module-level `_in_flight_lock + _in_flight_calls + _active_workers` counter for bounded concurrency.
  - Non-daemon worker, joinable on shutdown.
  - `shutdown_all_calls(timeout)` joins workers with bounded deadline.
- `RaceDescriptionLLMController` (`game/strategy/services/race_description_llm_controller.py:84-310`) shows the consumer pattern — owns the call instance(s), polls in `update()`, fires `on_change` callback. The coordinator's analog is the listener registered on `ReplayStore`.
- `ApplicationContext` does NOT own background services like `LLMBackgroundCall`. They're owned by the screens/services that need them. Coordinator follows this: constructed in `app_bootstrap.py` and held alongside the `ReplayStore`.
- Production sink wiring is missing today: `set_replay_store(...)` is never called. The user is fixing this separately. PROJ-354B subscribes to whatever `ReplayStore` instance gets registered.

### Architecture (Agent 3: ReplayStore extension surface)

- `ReplayStore.persist` (lines 200-214) does atomic write via `save_json` (temp+rename). New listener fires AFTER successful write but BEFORE `_evict_excess` so subscribers see the path before any eviction churn.
- `_evict_excess` (lines 280-299) sorts by `st_mtime` and unlinks oldest. Sidecar eviction parses `replay_id` from filename and unlinks matching sidecar.
- `delete(replay_id)` (lines 250-262) currently unlinks one file. New code adds sidecar unlink with same try/except.
- `save_json` (`game/core/json_utils.py:148-204`) is atomic on POSIX and NTFS for same-volume renames. No race issue for same-dir sidecar writes.
- No existing sidecar pattern in codebase. Swarm confirmed; we're inventing it. Acceptable.
- `ReplayResolver.resolve` (lines 75-113) does file-system probe + `_safe_load`. Natural read site for sidecar status: after successful record load, before returning.

### Key Patterns to Reuse

- **Pattern #28 Background Service Call** (PROJ-296): direct template. `docs/02_PATTERNS.md:1449-1509`.
- **Pattern #1 ApplicationContext** (PROJ-258): coordinator dependencies via DI at construction time, not module globals. AI factory and registry provider come from the context.
- **Pattern #17 Serializable Protocol**: sidecar uses free-function `to_dict`/`from_dict` like the rest of replay code.

### Dependencies & Risks (full list in plan.md)

1. **R1: Sink wiring prerequisite blocks Phase 5.** Phases 1-4 complete in isolation; Phase 5 unblocks when prereq lands.
2. **R2: FP nondeterminism causes false positives.** Existing strict-equality test passes — implies determinism holds. If flake appears, comparator-policy in a separate change.
3. **R3: Hostile mod stalls verifier.** Mitigated by queue cap + single worker. Hard timeout requires process boundary; deferred.
4. **R4: Headless-vs-visual divergence.** Mitigated by Phase 5 Task 5.4 equivalence test.
5. **R5: No-recursion guarantee.** `run_replay_headless` passes `capture_context=None` to `run_battle`; the capture path's `if capture_context is not None` check at `battle_runner.py:180` ensures no recursion. Mitigated by Phase 4 Task 4.5 regression test.
6. **R6: Sidecar/replay race condition.** Replay record persists; sidecar follows seconds-to-minutes later. If user deletes save in between, `_notify_replay_store_save_deleted` fires before sidecar lands. Coordinator checks `store.save_root` is still active before writing sidecar; if not, drops result silently.
7. **R7: Atomic-rename on Windows.** `save_json` uses temp+`replace()`; atomic on NTFS for same-volume renames. Sidecars and records share dir → same volume.

### Opportunities Discovered

- Listener API enables future telemetry / debug subscribers without coordinator changes.
- Sidecar pattern is reusable for future per-save audit needs (e.g., mod-set fingerprint).

## Design Decisions

See [decisions.md](decisions.md) for the full log with rationale.

Key decisions:

- Verification triggers post-persist of live battles, NOT user-clicks-Replay (Codex r002 correction; matches user requirement).
- Single FIFO worker; queue cap 16; no thread-level hard timeout (Codex r004 correction; process boundary required for true timeout, out of scope).
- Sidecar file `replay_<id>.verification.json` with separate `REPLAY_VERIFICATION_SCHEMA_VERSION` (independent lifecycle from replay schema).
- List-based listener API on `ReplayStore` (future-proof; minimal API).
- Verifier in `game/simulation/replay/`; coordinator in `game/strategy/services/` (layer purity).
- Test boundary at `BattleController.start_from_spec`, NOT `BattleScreen` (Codex r004 correction; avoids Pygame UI).
- Combat Lab uses explicit synthetic-builder fallback (`combat_lab/design_loader.py::load_combat_lab_design`); NEVER silent global-registry fallback.

## Cross-references

- Sibling project: PROJ-354A (capture-side fidelity prerequisite).
- Inter-agent discussion: `AgentCoordination/Scratchpad/Discussion/20260505T034554Z_replay-end-state-verification/`
- Related GitHub issue: #8 (replay button disabled, https://github.com/ropesend/StarshipBattles/issues/8)
- Pattern reference: `docs/02_PATTERNS.md` Pattern #28 Background Service Call
- LLMBackgroundCall template: `game/services/llm/background.py`
