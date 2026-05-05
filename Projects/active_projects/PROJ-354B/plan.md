# PROJ-354B: Replay Background Verification Coordinator

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-354B` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-354B [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Settings + pure verifier | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Sidecar persistence + lifecycle | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. ReplayStore callback + listener wiring | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Background coordinator (single-worker FIFO queue) | Not Started | [phase_4_checklist.md](phase_4_checklist.md) |
| 5. Composition root wiring + integration tests | Not Started | [phase_5_checklist.md](phase_5_checklist.md) |
| 6. Combat Lab fallback + docs | Not Started | [phase_6_checklist.md](phase_6_checklist.md) |

## Current State
**Last Updated:** 2026-05-04 22:00
**Active Phase:** Planning (awaiting user approval)
**Last Action:** Plan drafted from r003 consensus + swarm research
**Next Action:** User approval, then begin Phase 1
**Blockers:**
1. **PROJ-354A must land first** — this project depends on `ComponentStateSpec` carrying `max_hp` and `status` for the verifier's diff to be diagnostic.
2. **Production sink wiring must land** — the user is handling this with codex separately. Specifically: `set_default_capture_sink(replay_store)` and `set_replay_store(replay_store)` must be called from the production composition root (likely `app_bootstrap.py:157-159` near `ApplicationContext.create_production`). Without this, `NullCaptureSink` is the active sink, no replays persist, and verification has nothing to fire on.

**Context for Next Agent:** Implements C4–C9 of the consensus plan at `AgentCoordination/Scratchpad/Discussion/20260505T034554Z_replay-end-state-verification/plans/replay_end_state_verification_r003.md`. The Phase A work is in PROJ-354A (sibling project). This project assumes both prerequisites above have landed before Phase 5 (composition root wiring) is exercised end-to-end; Phases 1–4 can be implemented and tested in isolation.

## Overview

Background end-state verification for captured replays. When a live battle persists a replay record, a coordinator queues that record, headlessly re-runs the battle from the captured spec, compares the new outcome against the captured outcome via strict dict-equality on `battle_outcome_to_dict`, and writes a sidecar JSON file with the verification result. Per-replay status (`pending`/`passed`/`failed`/`error`/`skipped_queue_full`/`skipped_disabled`) lives in `replay_<id>.verification.json` next to the replay record. Designed for a heavily moddable game: divergence between live and replay outcomes surfaces mod-induced determinism breaks the user couldn't otherwise see.

## Goals

- Verification runs automatically as a **background process** when the live simulator ends combat. Not on user-clicks-Replay (that's a future opt-in).
- Settings: `verification_enabled: bool = True`, `verification_queue_cap: int = 16`. Toggleable; default on.
- Pure verifier module compares `record.outcome.data` and `battle_outcome_to_dict(replayed_outcome)` for strict equality. Returns a `ReplayVerificationResult` with capped diff (first 25 entries + footer).
- Verifier dependency direction respects `docs/01_ARCHITECTURE.md` layer rules: pure verifier in `game/simulation/replay/` imports only simulation/replay DTOs; coordinator in strategy/services or above imports verifier + replay store + AI factory through DI.
- Single FIFO worker via `threading.Lock` + queue list. No parallelism in first pass. No thread-level hard timeout (process-boundary required for that — out of scope).
- Sidecar JSON: atomic write via existing `save_json` helper. Lifecycle tied to replay record (`ReplayStore.delete` and `_evict_excess` clean up sidecar too).
- `ReplayStore` exposes a list-based listener (`add_on_record_persisted_listener` / `remove_on_record_persisted_listener`) for the coordinator to subscribe to.
- Coordinator integrates with existing `shutdown_all_calls`-style shutdown sequence in `run_loop.py:84-85` (mirror the `LLMBackgroundCall` pattern).
- Combat Lab replays use the existing synthetic builder as explicit fallback (`combat_lab/design_loader.py::load_combat_lab_design`); no silent global-registry fallback.
- All 8 test items from r003 §C8 land:
  1. Component state round-trip (PROJ-354A — already covered)
  2. Distinct status extraction (PROJ-354A — already covered)
  3. Verifier unit tests (pass/fail/diff)
  4. Strategy/application integration: completed live battle queues verification only after persist + only when enabled
  5. Production materializer test
  6. No-recursion regression test (verification replay does NOT recursively create another replay record)
  7. Headless-vs-visual equivalence (boundary at `BattleController.start_from_spec`, NOT `BattleScreen`)
  8. Sidecar lifecycle (delete + evict + skipped_queue_full + skipped_disabled produce sidecars)
- Docs: `docs/systems/combat_simulation.md` and `docs/systems/strategy_layer.md` updated; `docs/01_ARCHITECTURE.md` updated to register the new cross-layer service.

## Scope

**In:**
- New file: `game/simulation/replay/replay_verifier.py` — pure verifier (`ReplayVerificationResult` dataclass + `verify_replay_outcome` function + `compute_outcome_diff` helper).
- New file: `game/strategy/services/replay_verification_coordinator.py` — `ReplayVerificationCoordinator` background service. Mirrors `LLMBackgroundCall` pattern (per docs/02_PATTERNS.md Pattern #28).
- New file: `game/strategy/services/replay_verification_sidecar.py` — schema + atomic write helper for `replay_<id>.verification.json`.
- New constant `REPLAY_VERIFICATION_SCHEMA_VERSION` (versioned independently of `REPLAY_SCHEMA_VERSION`).
- Extend `ReplaySettings` (`game/strategy/services/replay_store.py:56-86`) with `verification_enabled: bool = True` and `verification_queue_cap: int = 16`.
- Extend `ReplayStore` (`game/strategy/services/replay_store.py:102-322`):
  - Add `_on_record_persisted_listeners: List[Callable]` and `add_on_record_persisted_listener(callback)` / `remove_on_record_persisted_listener(callback)` methods.
  - Wire listener invocations after successful `persist(record)` and before `_evict_excess`.
  - Update `delete(replay_id)` (lines 250-262) to also unlink the sidecar.
  - Update `_evict_excess` (lines 280-299) to evict sidecars alongside replay records (match by replay_id).
- Extend `ReplayResolver.resolve()` (`game/strategy/services/replay_resolver.py:75-113`) to optionally read sidecar verification status (no-op when sidecar missing).
- Wire `ReplayVerificationCoordinator` into the production composition root (likely `game/app_bootstrap.py` near where `ApplicationContext.create_production()` is called, lines 157-159) — assumes prereq sink wiring lands here too.
- Wire shutdown into `run_loop.py:84-85` after `shutdown_all_calls(timeout=5.0)`.
- Combat Lab fallback wiring: when a record's `instance_snapshot` is None for all ships (Combat Lab/Battle Setup origin), the coordinator builds the verifier `ship_builder` using `combat_lab/design_loader.py::load_combat_lab_design` as the explicit fallback. NOT silent global-registry lookup.
- All tests in r003 §C8 (items 3–8 in this project; items 1–2 in PROJ-354A).
- Doc updates: `docs/systems/combat_simulation.md` § 11, `docs/systems/strategy_layer.md` Replay Persistence section, `docs/01_ARCHITECTURE.md` (register coordinator in Services / Strategy services table).

**Out:**
- Production sink wiring itself (`set_default_capture_sink(...)` in app_bootstrap). User is handling separately via codex.
- PROJ-354A scope (capture-side `max_hp`/`status` fields).
- Visual-replay verification (user clicks Replay → also verify). Future opt-in. Reserved sidecar `source: background | visual_replay` field for the future.
- Process-boundary hard timeout for hostile/runaway verifier code. Recorded as a follow-up; not in first pass. Queue cap + drop-on-full provides bounded mitigation.
- Auto-verify on every replay capture in a worker thread (i.e., this project's plan IS the "auto-verify on every replay capture" — no further "even more proactive" mode is in scope).
- UI for replay timeline / scrubber.
- UI surfacing of verification status badges in the Replay Browser. Mentioned in r003 as a future polish; deferred to a separate small project.

## Key Files Reference

### New files
| Component | File Path | Purpose |
|-----------|-----------|---------|
| Pure verifier | `game/simulation/replay/replay_verifier.py` | `verify_replay_outcome(record, replayed_outcome) -> ReplayVerificationResult`; pure layer; no Strategy/UI/AI imports |
| Coordinator | `game/strategy/services/replay_verification_coordinator.py` | Background service: queue, single worker, listener for `ReplayStore.on_record_persisted` |
| Sidecar helper | `game/strategy/services/replay_verification_sidecar.py` | Schema + atomic write/read for `replay_<id>.verification.json` |
| Verifier unit tests | `tests/unit/simulation/replay/test_replay_verifier.py` | Pass/fail/diff cases on `verify_replay_outcome` |
| Coordinator unit tests | `tests/unit/strategy/services/test_replay_verification_coordinator.py` | Queue ordering, cap enforcement, settings toggle, no-recursion |
| Sidecar tests | `tests/unit/strategy/services/test_replay_verification_sidecar.py` | Atomic write, lifecycle hooks (delete/evict) |
| Integration test (queue) | `tests/integration/replay/test_verification_queue_integration.py` | Live battle → persist → coordinator queues → verifier runs → sidecar written |
| Integration test (equivalence) | `tests/integration/replay/test_headless_visual_equivalence.py` | `run_replay_headless` outcome == `BattleController.start_from_spec` outcome |

### Modified files
| Component | File Path | Lines | Change |
|-----------|-----------|-------|--------|
| Settings dataclass | `game/strategy/services/replay_store.py` | 56-86 | Add `verification_enabled: bool = True`, `verification_queue_cap: int = 16` |
| `ReplayStore` listener API | `game/strategy/services/replay_store.py` | new methods | `add_on_record_persisted_listener(callback)`, `remove_on_record_persisted_listener(callback)` |
| `ReplayStore.persist` | `game/strategy/services/replay_store.py` | 200-214 | After write, before `_evict_excess`, fire listeners with `(record, path)` |
| `ReplayStore.delete` | `game/strategy/services/replay_store.py` | 250-262 | Also unlink `<replay_dir>/replay_<id>.verification.json` |
| `ReplayStore._evict_excess` | `game/strategy/services/replay_store.py` | 280-299 | After unlinking each replay record, also unlink its matching sidecar |
| `ReplayResolver.resolve` | `game/strategy/services/replay_resolver.py` | 75-113 | Read sidecar verification status if present; expose via new field on `ReplayLookup` |
| App bootstrap | `game/app_bootstrap.py` | 157-159 (near ApplicationContext.create_production) | Construct `ReplayVerificationCoordinator`, register listener on `ReplayStore` |
| Run loop shutdown | `game/run_loop.py` | 84-85 | Call coordinator's shutdown after `shutdown_all_calls(timeout=5.0)` |
| Combat sim docs | `docs/systems/combat_simulation.md` | § 11 | Document verification, sidecar schema, headless-vs-visual contract |
| Strategy layer docs | `docs/systems/strategy_layer.md` | Replay Persistence section | Sidecar layout, queue cap, settings |
| Architecture docs | `docs/01_ARCHITECTURE.md` | Strategy services table | Register `ReplayVerificationCoordinator` |

### Reference patterns (read-only — do not modify)
| Pattern | File:Line | Use |
|---------|-----------|-----|
| `LLMBackgroundCall` template | `game/services/llm/background.py:65-368` | Threading model for coordinator (lock + cancel event + done event + module-level concurrency counter + `shutdown_all_calls`) |
| `RaceDescriptionLLMController` example consumer | `game/strategy/services/race_description_llm_controller.py:84-310` | DI shape: provider + caption_loader + on_change. Polling pattern. |
| Atomic JSON writer | `game/core/json_utils.py:148-204` | `save_json` for sidecar writes |
| Pattern #28 Background Service Call | `docs/02_PATTERNS.md:1449-1509` | Canonical pattern for background work |
| ReplayRecord schema | `game/simulation/replay/replay_record.py:32-91` | What's in a record |
| `battle_outcome_to_dict` | `game/simulation/replay/replay_serialization.py:548-559` | Equality oracle source |
| `run_replay_headless` | `game/simulation/replay/replay_player.py:89-115` | Headless replay entry; caller must wire ship_builder/registry_provider |
| `build_replay_ship_builder` | `game/simulation/replay/replay_player.py:42-86` | Materializer; raises if no snapshots and no fallback |

## Decisions Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-05-04 | Project initialized | Phase B landing of consensus plan r003 |
| 2026-05-04 | Verification triggers post-persist of live battles, NOT user-clicks-Replay | Codex correction (r002). Matches user requirement: "background process that occurs when the simulator ends combat". User-replay verification reserved as future opt-in. |
| 2026-05-04 | Single FIFO worker, queue cap 16, no thread timeout | r003 §C6. Codex pushback (r004): thread-level timeout can't stop CPU-burning code without process boundary; out of scope. Cap + drop-on-full provides bounded mitigation. |
| 2026-05-04 | Sidecar file `replay_<id>.verification.json`, separate schema version | r003 §C7. Sidecar avoids mutating immutable replay JSON. Separate `REPLAY_VERIFICATION_SCHEMA_VERSION` because verification schema lifecycle is independent. |
| 2026-05-04 | List-based listener API on `ReplayStore` | Swarm finding: future-proofs for multiple subscribers (e.g., verification + telemetry). Single subscriber today; minimal API overhead. |
| 2026-05-04 | Verifier in `game/simulation/replay/`; coordinator in `game/strategy/services/` | r003 §C5. Verifier is layer-agnostic (works for Combat Lab too) and depends only on simulation DTOs. Coordinator depends on Strategy + ApplicationContext (AI factory, registry provider) and lives at the appropriate layer. |
| 2026-05-04 | Test boundary for headless-vs-visual = `BattleController.start_from_spec`, NOT `BattleScreen` | Codex correction (r004). Avoids Pygame UI dependency in tests. Both paths route through `start_engine_from_spec` → `run_battle`, so equivalence at this boundary proves equivalence at every downstream point. |
| 2026-05-04 | Combat Lab uses explicit synthetic-builder fallback | r003 Combat Lab Position. Explicit `fallback_builder=load_combat_lab_design` parameter on `build_replay_ship_builder` call site; NEVER silent global-registry fallback. |
| 2026-05-04 | No registration of `ReplayStore` as default capture sink in this project | This is the prerequisite the user is handling separately with codex. PROJ-354B assumes the wiring lands; if it hasn't by Phase 5, that phase blocks. |

## Initial Analysis

### Baseline test state

Same baseline as PROJ-354A: 17260 tests | 17256 passed | 0 failed | 4 skipped | 55.1s.

### Today's gaps (the things this project closes)

1. **No verifier exists.** Production never compares replay outcomes against captured outcomes. Tests do (`tests/integration/replay/test_replay_playback.py:120-136` does strict `==`), but in production it's "trust determinism" with no diagnostic.
2. **No background scheduler.** When a battle ends, the engine returns to the strategic turn engine; nothing else fires.
3. **`ReplayStore` has no post-persist callback.** Today it just writes the file; nothing observes the persistence.
4. **Sidecar pattern is novel.** Swarm confirmed no existing precedent in the codebase. We're inventing it. Acceptable; it's the right shape for the lifecycle.
5. **Settings don't have boolean toggles yet.** `ReplaySettings` has only `max_replays_per_save: int`. Pattern is well-established (`load_replay_settings` in `replay_store.py:67-85`); extension is mechanical.

### Dependency on prerequisites

**This project cannot be exercised end-to-end until BOTH:**
- PROJ-354A lands (without it, the verifier diff is less informative — it can still find divergence, but `max_hp`/`status` fields are absent so diagnostic precision drops).
- Production sink wiring lands (`set_default_capture_sink(replay_store)` and `set_replay_store(replay_store)` called from app_bootstrap). Without this, no replays persist in production, and the coordinator never fires.

Phases 1–4 implement components that test green in isolation (unit + integration tests can call the verifier/coordinator directly without going through production capture). Phase 5 wires into composition root and exercises end-to-end; if prereq isn't done, Phase 5 cannot complete.

## Swarm Findings Summary

### Architecture

- `LLMBackgroundCall` (`game/services/llm/background.py`) is the canonical background-service template. Wrap a synchronous call in a worker thread; expose `status` / `result` / `error` / `elapsed_seconds` properties with lock-protected reads; `cancel()` signals via `threading.Event`; `shutdown_all_calls(timeout)` joins workers with bounded timeout. Coordinator follows this shape.
- `RaceDescriptionLLMController` shows the consumer pattern: own the call instance(s), poll in `update()`, fire `on_change` callback. For the coordinator, the consumer is the listener registered on `ReplayStore`; no separate UI consumer is needed in this project (UI surfacing is a future polish).
- `ApplicationContext` (`game/context.py:31-58`) does NOT own the coordinator directly. Pattern: services like `RaceDescriptionLLMController` are owned by the screen/service that needs them, not by the context. Coordinator is owned by the composition root (constructed in `app_bootstrap.py`) and registered as a listener on the `ReplayStore` instance.
- `ReplayStore` is constructed and registered today via `set_replay_store(store)` (`game/strategy/systems/save_game_service.py:33-38`). Per swarm finding: **`set_replay_store` is NEVER called in production** — the function exists but no caller exists. That's the user's separate sink-wiring fix. PROJ-354B's coordinator subscribes to whatever store gets registered.

### Key Patterns to Reuse

- **Pattern #28 Background Service Call** (PROJ-296): direct template for coordinator. `docs/02_PATTERNS.md:1449-1509`.
- **Pattern #1 ApplicationContext** (PROJ-258): coordinator's dependencies (AI factory, registry provider) come from `ApplicationContext` at construction time. NOT module-level globals.
- **Pattern #2 Protocol + TypeGuard**: `IReplayCaptureSink` is the existing protocol; the post-persist listener API is a new informal protocol — `Callable[[ReplayRecord, Path], None]` is sufficient (no formal `Protocol` class needed for a single callback type).
- **Pattern #17 Serializable Protocol**: sidecar JSON uses free-function `to_dict`/`from_dict` like the rest of replay code.

### Risks Identified

1. **R1: Sink wiring prerequisite blocks Phase 5.** If user hasn't completed sink wiring before the implementer reaches Phase 5, that phase cannot complete. Mitigation: Phases 1–4 land independently and provide value in isolation (verifier callable from tests / future visual-replay path).
2. **R2: FP nondeterminism causes false-positive verification failures.** Existing test (`test_replay_playback.py`) does strict `==` and passes — implies determinism holds. Mitigation: ship strict; if flake appears, add comparator-policy setting in a separate change.
3. **R3: Hostile/runaway mod stalls verifier worker.** Mitigated by queue cap + drop-on-full + single-worker (no parallelism). NOT mitigated by hard timeout (out of scope per r003).
4. **R4: Headless-vs-visual divergence.** Both paths route through `start_engine_from_spec`; equivalence test catches drift. Mitigation: Phase 5 Task 5.4.
5. **R5: No-recursion guarantee.** When the coordinator runs `run_replay_headless` to verify, that headless run goes through `run_battle` — which itself has the capture path. The capture path checks `if capture_context is not None` (`battle_runner.py:180`) and `run_replay_headless` passes `capture_context=None` (per `replay_player.py:89-115` design). **Verification:** Phase 4 Task 4.5 has an explicit no-recursion regression test.
6. **R6: Sidecar/replay race condition.** Replay record write completes; sidecar write completes seconds-to-minutes later. If user deletes save in between, `_notify_replay_store_save_deleted` fires before sidecar lands. Mitigation: coordinator checks `store.save_root` is still active before writing sidecar; if not, drops the result silently (logged).
7. **R7: Atomic-rename on Windows.** `save_json` uses temp+`replace()` which is atomic on POSIX and atomic on NTFS for same-volume renames. Both replay records and sidecars are in the same dir → same volume. No issue.

### Opportunities Discovered

- **Listener API enables future telemetry.** A second listener (e.g., logging, metrics) can subscribe without coordinator changes.
- **Sidecar pattern reusable for save metadata.** If the codebase later wants per-save audit trails (e.g., "which mods were active when this replay was captured"), sidecars are the right shape. Out of scope here, but the precedent is established cleanly.

## Phases

### Phase 1: Settings + pure verifier [Medium]
**Objective:** Extend `ReplaySettings` and add the pure verifier module. No coordinator, no sidecar, no integration. Pure unit tests prove the verifier oracle.
**Status:** Not Started

#### Task 1.1: Extend `ReplaySettings` with verification fields [Simple]
**File:** `game/strategy/services/replay_store.py`
**Tests:** `pytest tests/unit/strategy/services/test_replay_settings.py -v` (or wherever existing settings tests live)

- [ ] At lines 56-86, extend `ReplaySettings`:
  ```python
  @dataclass(frozen=True)
  class ReplaySettings:
      max_replays_per_save: int = 50
      verification_enabled: bool = True
      verification_queue_cap: int = 16
  ```
- [ ] Update `load_replay_settings` to read both new keys with sensible fallbacks (mirroring the existing `max_replays_per_save` pattern at lines 79-85).
- [ ] Add unit tests proving:
  - Defaults when file is missing (`verification_enabled=True`, `verification_queue_cap=16`).
  - Override via JSON file.
  - Malformed JSON → defaults silently.
  - Type coercion (`"true"` string → `True`? clamp `verification_queue_cap` to ≥1).
- [ ] **Verify:** Settings tests pass; existing `max_replays_per_save` tests unaffected.

**Notes:**

#### Task 1.2: Write failing tests for pure verifier (TDD) [Medium]
**File:** `tests/unit/simulation/replay/test_replay_verifier.py` (NEW)
**Tests:** `pytest tests/unit/simulation/replay/test_replay_verifier.py -v`

- [ ] Test cases (failing initially):
  - **Pass case**: identical `BattleOutcome` dicts → `result.passed=True`, empty `diff`.
  - **Fail case (single field)**: differ on one ship's `current_hp` → `result.passed=False`, `len(diff)==1`, diff[0].path == `("teams", 0, "ships", 0, "components", 0, "current_hp")`.
  - **Fail case (multiple)**: differ on 5 fields → `len(diff)==5`.
  - **Fail case (capped)**: differ on 30 fields → `len(diff)==25` AND `result.diff_truncated` flag (or similar) AND a "and N more" footer field. Cap at 25.
  - **Different team_survivors**: different team-survivor counts caught.
  - **Round-trip identity**: `verify_replay_outcome(record, record.outcome.to_battle_outcome())` returns `passed=True`. (Sanity check.)
- [ ] **Verify:** All tests fail with import error (verifier module doesn't exist yet).

**Notes:**

#### Task 1.3: Implement pure verifier module [Medium]
**File:** `game/simulation/replay/replay_verifier.py` (NEW)
**Tests:** Phase 1.2's tests

- [ ] Create the module with imports limited to:
  - `dataclasses`, `typing` (stdlib)
  - `game.simulation.battle_outcome.BattleOutcome` (or wherever it lives)
  - `game.simulation.replay.replay_record.ReplayRecord`
  - `game.simulation.replay.replay_serialization.battle_outcome_to_dict`
- [ ] **DO NOT IMPORT**: anything from `game.strategy.*`, `game.ui.*`, `game.ai.*`. Lint test in Phase 6.
- [ ] Define `Difference` dataclass:
  ```python
  @dataclass(frozen=True)
  class Difference:
      path: Tuple[Any, ...]   # e.g., ("teams", 0, "ships", 0, "components", 0, "current_hp")
      expected: Any
      actual: Any
  ```
- [ ] Define `ReplayVerificationResult`:
  ```python
  @dataclass(frozen=True)
  class ReplayVerificationResult:
      replay_id: str
      passed: bool
      diff: Tuple[Difference, ...]
      diff_truncated: bool
      total_diff_count: int
  ```
- [ ] Implement `compute_outcome_diff(expected: Dict, actual: Dict, max_diffs: int = 25)`:
  - Recursive walk of dicts/lists/tuples; emit `Difference` per leaf mismatch.
  - Cap at `max_diffs`; if exceeded, `diff_truncated=True` and `total_diff_count` reflects actual count.
- [ ] Implement `verify_replay_outcome(record, replayed_outcome)`:
  - Compute `expected_dict = record.outcome.data` (already a dict)
  - Compute `actual_dict = battle_outcome_to_dict(replayed_outcome)`
  - Call `compute_outcome_diff` with default cap.
  - Return `ReplayVerificationResult(replay_id=record.replay_id, passed=(len(diff)==0 and not diff_truncated), diff=tuple(diff), diff_truncated=diff_truncated, total_diff_count=total)`.
- [ ] **Verify:** All Phase 1.2 tests pass.

**Notes:**

---

### Phase 2: Sidecar persistence + lifecycle [Medium]
**Objective:** Atomic sidecar JSON file at `replay_<id>.verification.json`. ReplayStore lifecycle (delete + evict) extended to handle sidecars. No coordinator yet.
**Status:** Not Started

#### Task 2.1: Sidecar schema + atomic writer module [Medium]
**File:** `game/strategy/services/replay_verification_sidecar.py` (NEW)
**Tests:** `pytest tests/unit/strategy/services/test_replay_verification_sidecar.py -v` (NEW)

- [ ] New constant `REPLAY_VERIFICATION_SCHEMA_VERSION = "1.0.0"`. Documented as separate from `REPLAY_SCHEMA_VERSION`.
- [ ] Define `VerificationStatus` enum: `PENDING`, `PASSED`, `FAILED`, `ERROR`, `SKIPPED_QUEUE_FULL`, `SKIPPED_DISABLED`.
- [ ] Define `VerificationSource` enum: `BACKGROUND`, `VISUAL_REPLAY` (reserved for future).
- [ ] Define `VerificationSidecar` frozen dataclass with fields:
  - `replay_id: str`
  - `schema_version: str`
  - `status: str` (`VerificationStatus.name`)
  - `source: str` (`VerificationSource.name`)
  - `verified_at: str` (ISO 8601 UTC)
  - `duration_ms: Optional[int]`
  - `diff: Optional[List[Dict]]` (serialized `Difference`s)
  - `error: Optional[Dict]` (`{"type": str, "message": str}` for infrastructure failures)
- [ ] Implement `write_verification_sidecar(replay_dir: Path, sidecar: VerificationSidecar) -> Optional[Path]`:
  - Path: `replay_dir / f"replay_{sidecar.replay_id}.verification.json"`
  - Use `save_json` (atomic temp+rename).
  - Returns Path on success, None on write failure (exception caught + logged).
- [ ] Implement `read_verification_sidecar(replay_dir: Path, replay_id: str) -> Optional[VerificationSidecar]`:
  - Returns None if file doesn't exist or fails to parse.
  - Logs at debug level only (not exception); the absence is normal pre-verification state.
- [ ] Implement `sidecar_path_for_replay(replay_dir: Path, replay_id: str) -> Path`: pure path helper.
- [ ] Tests cover:
  - Round-trip write → read.
  - Atomic write (verify temp file is gone after write succeeds).
  - Read of missing sidecar returns None.
  - Read of corrupt sidecar returns None.
  - Path helper returns correct format `replay_<id>.verification.json`.
- [ ] **Verify:** All sidecar tests pass.

**Notes:**

#### Task 2.2: Update `ReplayStore.delete` to also unlink sidecar [Simple]
**File:** `game/strategy/services/replay_store.py`
**Tests:** `pytest tests/integration/replay/test_replay_store.py -k delete -v`

- [ ] At lines 250-262, after the existing `path.unlink()`, also unlink the sidecar:
  ```python
  sidecar_path = sidecar_path_for_replay(rd, replay_id)
  if sidecar_path.exists():
      try:
          sidecar_path.unlink()
      except OSError:
          logger.exception("PROJ-354B failed to delete verification sidecar: %s", sidecar_path)
  ```
- [ ] Add new test `test_delete_removes_sidecar`: write replay record + sidecar → `store.delete(id)` → both files gone.
- [ ] **Verify:** existing `test_delete_removes_file` still passes; new sidecar test passes.

**Notes:**

#### Task 2.3: Update `_evict_excess` to also unlink sidecars [Simple]
**File:** `game/strategy/services/replay_store.py`
**Tests:** `pytest tests/integration/replay/test_replay_store.py -k evict -v`

- [ ] At lines 280-299, in the eviction loop, after each `p.unlink()` of a replay file, also unlink its sidecar (parse `replay_id` from filename or store `(file, replay_id)` pairs in the sorted list).
- [ ] Add new test `test_evict_removes_sidecars_alongside_records`: write 5 replay records + 5 sidecars; cap=3; persist 5; assert 2 oldest replays AND 2 oldest sidecars are gone.
- [ ] **Verify:** existing eviction tests still green; new sidecar test passes.

**Notes:**

---

### Phase 3: ReplayStore listener API + ReplayResolver sidecar read [Medium]
**Objective:** Add post-persist listener registration to `ReplayStore`; extend `ReplayResolver` to surface sidecar status. No coordinator yet (Phase 4).
**Status:** Not Started

#### Task 3.1: Listener API on `ReplayStore` [Medium]
**File:** `game/strategy/services/replay_store.py`
**Tests:** `pytest tests/integration/replay/test_replay_store.py -k listener -v`

- [ ] In `__init__` (lines 119-131), add `self._on_record_persisted_listeners: List[Callable[[ReplayRecord, Path], None]] = []`.
- [ ] Add public methods:
  ```python
  def add_on_record_persisted_listener(
      self,
      callback: Callable[[ReplayRecord, Path], None],
  ) -> None:
      if callback not in self._on_record_persisted_listeners:
          self._on_record_persisted_listeners.append(callback)

  def remove_on_record_persisted_listener(
      self,
      callback: Callable[[ReplayRecord, Path], None],
  ) -> None:
      if callback in self._on_record_persisted_listeners:
          self._on_record_persisted_listeners.remove(callback)
  ```
- [ ] In `persist` (lines 200-214), after successful write but BEFORE `_evict_excess`, fire listeners:
  ```python
  # ... existing write logic ...
  # Fire listeners (each in its own try/except so one bad listener doesn't block others)
  for listener in list(self._on_record_persisted_listeners):
      try:
          listener(record, path)
      except Exception:
          logger.exception(
              "PROJ-354B on_record_persisted listener raised; ignoring"
          )
  self._evict_excess()
  return path
  ```
- [ ] Tests:
  - **Subscribe**: `store.add_on_record_persisted_listener(fn)`; `store.persist(record)` → `fn` called once with `(record, path)`.
  - **Unsubscribe**: after `remove_on_record_persisted_listener(fn)`, `fn` not called.
  - **Multiple listeners**: 3 subscribed; all called in registration order.
  - **Listener exception isolation**: one listener raises; others still called; `persist` returns path successfully.
  - **No-listener path**: persist works fine when no listeners registered (existing behavior preserved).
- [ ] **Verify:** All tests pass; existing `ReplayStore` tests unaffected.

**Notes:**

#### Task 3.2: Extend `ReplayResolver.resolve` to read sidecar [Medium]
**File:** `game/strategy/services/replay_resolver.py`
**Tests:** `pytest tests/unit/strategy/test_replay_resolver.py -v`

- [ ] Read `ReplayResolver.resolve` (lines 75-113). Identify where it returns `ReplayLookup` after a successful record load.
- [ ] Add field `verification_status: Optional[str] = None` to `ReplayLookup` (around line 27-41).
- [ ] After loading the record, attempt `read_verification_sidecar(rd, replay_id)`:
  - If sidecar exists: set `verification_status` to the sidecar's status string.
  - If missing: `verification_status = None`.
  - On parse error: log debug, `verification_status = None`.
- [ ] Tests:
  - Missing sidecar → `verification_status is None`.
  - `passed` sidecar → `verification_status == "PASSED"`.
  - `failed` sidecar → `verification_status == "FAILED"`.
  - Corrupt sidecar → `verification_status is None` (no exception bubbles).
- [ ] **Verify:** Existing resolver tests unaffected; new sidecar field tested.

**Notes:**

---

### Phase 4: Background coordinator (single-worker FIFO queue) [Complex]
**Objective:** Implement `ReplayVerificationCoordinator`. Subscribe to `ReplayStore` listener; queue records; process FIFO with single worker; run headless; verify; write sidecar.
**Status:** Not Started

#### Task 4.1: Failing tests for coordinator (TDD) [Medium]
**File:** `tests/unit/strategy/services/test_replay_verification_coordinator.py` (NEW)
**Tests:** `pytest tests/unit/strategy/services/test_replay_verification_coordinator.py -v`

- [ ] Test cases (initial failing):
  - **Passes through verifier**: coordinator receives a record, runs the verifier, writes sidecar with `passed` status.
  - **Failed verification**: divergent record → sidecar with `failed` status + diff.
  - **Disabled toggle**: `verification_enabled=False` → record received → sidecar written with `skipped_disabled` status (NOT silently dropped).
  - **Queue cap full**: 17 records queued, cap 16 → 17th gets sidecar with `skipped_queue_full` status.
  - **Single worker**: 5 records queued; assert serial execution (worker count = 1; each completes before next starts).
  - **Worker exception isolation**: verifier raises → coordinator writes sidecar with `error` status + error info; subsequent queue items still process.
  - **Shutdown**: `coordinator.shutdown(timeout)` joins worker; further `on_record_persisted` calls are no-ops.
  - **No recursion**: when coordinator's headless run completes, that completion does NOT itself enqueue another verification (capture_context=None in headless path).
- [ ] **Verify:** All tests fail (coordinator module doesn't exist yet).

**Notes:**

#### Task 4.2: Coordinator skeleton + queue + threading primitives [Complex]
**File:** `game/strategy/services/replay_verification_coordinator.py` (NEW)
**Tests:** Phase 4.1's tests; some subset passes after this task

- [ ] Imports (respect dependency direction):
  - stdlib: `threading`, `queue`, `dataclasses`, `typing`, `time`, `pathlib`, `datetime`
  - `game.simulation.replay.replay_verifier.verify_replay_outcome`, `ReplayVerificationResult`, `Difference`
  - `game.simulation.replay.replay_record.ReplayRecord`
  - `game.simulation.replay.replay_player.run_replay_headless`, `build_replay_ship_builder`
  - `game.strategy.services.replay_store.ReplayStore, ReplaySettings`
  - `game.strategy.services.replay_verification_sidecar.*`
  - **DO NOT IMPORT**: `game.ui.*`, `game.app.*`. Hard-wired AI-construction is NOT allowed; AI factory must be DI-injected.
- [ ] Module-level concurrency counter (mirroring `LLMBackgroundCall._in_flight_calls` pattern at `game/services/llm/background.py:56-62`):
  ```python
  _coordinator_lock = threading.Lock()
  _active_coordinators: Set["ReplayVerificationCoordinator"] = set()
  ```
- [ ] `ReplayVerificationCoordinator` class:
  - `__init__(self, *, replay_store: ReplayStore, ai_factory, registry_provider, settings: ReplaySettings, fallback_ship_builder: Optional[Callable] = None, clock: Callable[[], datetime] = ..., logger: Optional = None)`
  - Internal state: `_queue: List[ReplayRecord]`, `_state_lock: threading.Lock`, `_worker: Optional[threading.Thread]`, `_shutdown_event: threading.Event`, `_in_flight: Optional[ReplayRecord]`.
  - `start()` — register listener on `replay_store`, start worker thread.
  - `_on_record_persisted(record, path)` — listener callback; under lock, enqueue record OR write `skipped_queue_full` sidecar if at cap; signal worker.
  - `_worker_loop()` — pop records FIFO; run `_verify_one(record)`; loop until shutdown event set AND queue empty.
  - `_verify_one(record)` — handles toggle check, headless run, verifier call, sidecar write. See Task 4.3.
  - `shutdown(timeout: float = 5.0)` — set shutdown event; join worker with timeout; deregister listener.
- [ ] **Verify:** Subset of Phase 4.1 tests pass (queueing, cap enforcement, shutdown).

**Notes:**

#### Task 4.3: Worker `_verify_one` implementation [Complex]
**File:** `game/strategy/services/replay_verification_coordinator.py`
**Tests:** Phase 4.1's tests should mostly pass after this; rest pass after Task 4.4

- [ ] Implement `_verify_one(record: ReplayRecord) -> None`:
  ```python
  def _verify_one(self, record: ReplayRecord) -> None:
      replay_dir = self._replay_store._replay_dir()
      if replay_dir is None:
          # Save root cleared mid-verification; drop silently.
          return

      if not self._settings.verification_enabled:
          self._write_sidecar(record, status=VerificationStatus.SKIPPED_DISABLED, ...)
          return

      start = time.monotonic()
      try:
          ship_builder = build_replay_ship_builder(
              record,
              registry_provider=self._registry_provider,
              fallback_builder=self._fallback_ship_builder,
          )
          replayed_outcome = run_replay_headless(
              record,
              ai_factory=self._ai_factory,
              ship_builder=ship_builder,
              registry_provider=self._registry_provider,
          )
          # capture_context=None inside run_replay_headless → no recursion
          result = verify_replay_outcome(record, replayed_outcome)
          duration_ms = int((time.monotonic() - start) * 1000)
          status = VerificationStatus.PASSED if result.passed else VerificationStatus.FAILED
          self._write_sidecar(
              record,
              status=status,
              duration_ms=duration_ms,
              diff=([_difference_to_dict(d) for d in result.diff] if not result.passed else None),
              error=None,
          )
      except Exception as exc:
          duration_ms = int((time.monotonic() - start) * 1000)
          self._write_sidecar(
              record,
              status=VerificationStatus.ERROR,
              duration_ms=duration_ms,
              error={"type": type(exc).__name__, "message": str(exc)},
          )
  ```
- [ ] Implement `_write_sidecar(record, *, status, duration_ms=None, diff=None, error=None)`:
  - Check `replay_dir` is still valid (defensive against save deletion mid-verification per R6).
  - Build `VerificationSidecar` instance with `verified_at=self._clock().isoformat()`.
  - Call `write_verification_sidecar(replay_dir, sidecar)`.
- [ ] **Verify:** Phase 4.1 tests for "passes through verifier", "failed verification", "worker exception isolation" all pass.

**Notes:**

#### Task 4.4: Listener registration + shutdown integration [Medium]
**File:** `game/strategy/services/replay_verification_coordinator.py`
**Tests:** Remaining Phase 4.1 tests + new

- [ ] In `start()`: `self._replay_store.add_on_record_persisted_listener(self._on_record_persisted)`. Add to `_active_coordinators` under module-level lock.
- [ ] In `shutdown(timeout)`:
  - Set `_shutdown_event`.
  - Wake worker (queue.put or condition variable signal).
  - Join worker with bounded timeout.
  - `self._replay_store.remove_on_record_persisted_listener(self._on_record_persisted)`.
  - Remove from `_active_coordinators` under module-level lock.
  - Idempotent (calling `shutdown` twice does nothing).
- [ ] Module-level helper `shutdown_all_coordinators(timeout: float = 5.0)` mirroring `shutdown_all_calls` at `background.py:345-368`. Joins all active coordinators with shared deadline.
- [ ] **Verify:** All Phase 4.1 tests green.

**Notes:**

#### Task 4.5: No-recursion regression test [Simple]
**File:** `tests/unit/strategy/services/test_replay_verification_coordinator.py` (extended)
**Tests:** Same file

- [ ] Add test `test_verification_replay_does_not_recursively_create_replay_record`:
  - Set up a `ReplayStore` with a writable temp dir.
  - Construct a coordinator.
  - Call `coordinator._on_record_persisted(record, path)` directly.
  - After worker completes, count files in `<replay_dir>` matching `replay_<other_id>_*.json` — should be 0 (only the original + its sidecar, no new replay records).
- [ ] **Verify:** Test passes; no recursion.

**Notes:**

---

### Phase 5: Composition root wiring + integration tests [Complex]
**Objective:** Wire the coordinator into production startup; integrate with existing shutdown sequence; add end-to-end integration tests; add the headless-vs-visual equivalence test. **This phase requires production sink wiring (PROJ-354B prerequisite) to fully complete; if not done, tests can use a manually-wired coordinator + store but the production wiring step itself is blocked.**
**Status:** Not Started

#### Task 5.1: Wire coordinator into `app_bootstrap.py` [Medium]
**File:** `game/app_bootstrap.py`
**Tests:** Manual smoke + Phase 5.3 integration test
**BLOCKED until production sink wiring lands** (the `set_default_capture_sink` + `set_replay_store` calls).

- [ ] At the appropriate point in production bootstrap (likely near `ApplicationContext.create_production()` at lines 157-159), and AFTER the prerequisite sink-wiring lines:
  - Construct `ReplayStore(...)` if not already done by the prerequisite work.
  - Construct `ReplayVerificationCoordinator(replay_store=store, ai_factory=ctx.ai_factory_or_equivalent, registry_provider=ctx.registry_manager, settings=load_replay_settings(), ...)`.
  - Call `coordinator.start()`.
  - Hold a reference to the coordinator in the same place that holds the store (likely a module-level or app-level attribute).
- [ ] **Verify:** Game starts without errors; coordinator's worker thread is running.

**Notes:**

#### Task 5.2: Wire shutdown into `run_loop.py` [Simple]
**File:** `game/run_loop.py`
**Tests:** Manual smoke; verify clean shutdown

- [ ] At lines 84-85 (where `shutdown_all_calls(timeout=5.0)` is called), add `shutdown_all_coordinators(timeout=5.0)` BEFORE `pygame.quit()`. Order matters: drain background work before tearing down resources.
- [ ] **Verify:** Game shuts down cleanly with no thread-still-alive warnings; verify with `python -c "import threading; ..."` smoke if needed.

**Notes:**

#### Task 5.3: Integration test — live battle → verification queue → sidecar [Complex]
**File:** `tests/integration/replay/test_verification_queue_integration.py` (NEW)
**Tests:** Same file

- [ ] Set up: `ReplayStore` with writable temp dir + capture sink wired; `ReplayVerificationCoordinator` constructed with real AI factory and registry provider.
- [ ] Run a small deterministic battle that produces a known outcome via `run_battle`.
- [ ] Wait for coordinator to finish (use `coordinator.wait_for_idle(timeout)` helper added during this task, OR poll for sidecar existence with bounded timeout).
- [ ] Assert sidecar at `replay_<id>.verification.json` exists with `status=PASSED` (assuming determinism holds, which it should for the test's small battle).
- [ ] Verify settings toggle: with `verification_enabled=False`, sidecar exists but with `status=SKIPPED_DISABLED`.
- [ ] **Verify:** Both paths green.

**Notes:**

#### Task 5.4: Headless-vs-visual equivalence test [Medium]
**File:** `tests/integration/replay/test_headless_visual_equivalence.py` (NEW)
**Tests:** Same file

- [ ] Build a replay record via a known battle.
- [ ] Run replay via `run_replay_headless(record, ai_factory=..., ship_builder=build_replay_ship_builder(record, registry_provider=...), registry_provider=...)` → outcome A.
- [ ] Run replay via `BattleController.start_from_spec(replay_record_to_spec(record), config=BattleConfig(replay_mode=True, ...), ai_factory=..., ship_builder=the_same_production_replay_builder, registry_provider=...)`. Drive the controller through `update()` calls until `is_battle_over()`. Get outcome B from `controller.get_outcome()`.
- [ ] Assert `battle_outcome_to_dict(A) == battle_outcome_to_dict(B)`.
- [ ] Boundary is `BattleController`, NOT `BattleScreen` — no Pygame UI dependency.
- [ ] **Verify:** Test passes (proves the verifier's headless oracle matches the visual replay path).

**Notes:**

#### Task 5.5: Production materializer test [Medium]
**File:** `tests/integration/replay/test_verification_uses_production_materializer.py` (NEW)
**Tests:** Same file

- [ ] Set up coordinator wired with `build_replay_ship_builder` (production materializer), NOT a hand-built test builder.
- [ ] Run a battle that produces a record with non-empty `instance_snapshot` blobs.
- [ ] Trigger verification.
- [ ] Assert that `build_replay_ship_builder` was used (e.g., via spy/mock) AND the verification passes (proves the materializer integrates with the verifier).
- [ ] **Verify:** Test green.

**Notes:**

---

### Phase 6: Combat Lab fallback + docs + lint [Medium]
**Objective:** Wire Combat Lab fallback builder; lint verifier dependency direction; update docs.
**Status:** Not Started

#### Task 6.1: Combat Lab fallback wiring [Medium]
**File:** `game/strategy/services/replay_verification_coordinator.py`
**Tests:** `pytest tests/integration/replay/test_combat_lab_verification.py -v` (NEW)

- [ ] In `_verify_one`, when calling `build_replay_ship_builder`, pass `fallback_builder=self._fallback_ship_builder`. The coordinator's `__init__` already accepts this; the composition root passes it as `combat_lab.design_loader.load_combat_lab_design`.
- [ ] **DO NOT** silent-fall-back to global registry lookup. If `build_replay_ship_builder` raises, the verifier emits an `ERROR` sidecar; the user sees diagnostic info instead of a phantom green.
- [ ] New test: load a Combat Lab record (synthetic, `instance_snapshot=None`) → coordinator runs with fallback → verification passes.
- [ ] New test: load a record with no fallback wired AND no snapshots → verification ERRORs with a specific message.
- [ ] **Verify:** Both tests pass.

**Notes:**

#### Task 6.2: Verifier dependency direction lint [Simple]
**File:** `tests/unit/simulation/replay/test_replay_verifier_imports.py` (NEW)
**Tests:** Same file

- [ ] Static check: parse `game/simulation/replay/replay_verifier.py` AST and assert no imports from `game.strategy.*`, `game.ui.*`, `game.ai.*`.
- [ ] **Verify:** Test passes; if it fails, the verifier module has accidentally crossed a layer boundary.

**Notes:**

#### Task 6.3: Update `docs/systems/combat_simulation.md` [Medium]
**File:** `docs/systems/combat_simulation.md`
**Tests:** Manual review

- [ ] In § 11 Replay Capture & Playback, add a new subsection "Background Verification":
  - Explain the post-persist trigger.
  - Document the sidecar schema and file path.
  - Document `verification_enabled` and `verification_queue_cap` settings.
  - Note `run_replay_headless` requires caller-supplied `ship_builder` and `registry_provider`; the coordinator handles this.
  - Document the no-recursion guarantee (capture_context=None in headless path).
- [ ] Update the `> **Last verified:**` blockquote.
- [ ] **Verify:** Documented behavior matches implementation.

**Notes:**

#### Task 6.4: Update `docs/systems/strategy_layer.md` [Medium]
**File:** `docs/systems/strategy_layer.md`
**Tests:** Manual review

- [ ] In the Replay Persistence section, add:
  - Sidecar schema overview.
  - Sidecar lifecycle (delete + evict alongside replay record).
  - `ReplayStore.add_on_record_persisted_listener` API.
  - `ReplayResolver.resolve` returns `verification_status` field.
- [ ] Update the `> **Last verified:**` blockquote.
- [ ] **Verify:** Documented behavior matches implementation.

**Notes:**

#### Task 6.5: Update `docs/01_ARCHITECTURE.md` [Simple]
**File:** `docs/01_ARCHITECTURE.md`
**Tests:** Manual review

- [ ] In the Strategy services table (around line 175), add `ReplayVerificationCoordinator` row pointing to `game/strategy/services/replay_verification_coordinator.py`.
- [ ] Update the `> **Last verified:**` blockquote.
- [ ] **Verify:** Table reflects new service.

**Notes:**

#### Task 6.6: Full sharded suite green [Medium]
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [ ] Run full sharded suite. Compare to baseline + PROJ-354A new tests + PROJ-354B new tests.
- [ ] Acceptance: all tests pass; zero regressions.
- [ ] **Verify:** Investigate any failures.

**Notes:**

---

## Verification Checklist

### Project Start (REQUIRED)
- [x] Read `docs/` foundation docs (01_ARCHITECTURE, 02_PATTERNS, 03_CONVENTIONS) — done during planning
- [x] Run full test suite: 17256 passed at baseline

### After Each Phase
- [ ] Run `pytest tests/ --testmon` — affected tests pass
- [ ] Update `Current State` in this plan with handoff context

### Final Verification (after Phase 6)
- [ ] Full sharded suite: `python Tools/test_sharded/test_sharded.py` — all green
- [ ] Manual smoke (assumes prereq sink wiring landed): start a fresh game, run a battle, verify a `replay_<id>.verification.json` sidecar appears with `status=PASSED`.
- [ ] Manual smoke: toggle `verification_enabled=False` in `output/settings/replay_settings.json`; restart; run a battle; verify sidecar has `status=SKIPPED_DISABLED`.
- [ ] Verify changes are consistent with `docs/` — Phase 6 covers this

---

## Audit Log
| Cycle | Date | Findings | Resolution |
|-------|------|----------|------------|
| 1 | | | |

## Completion Checklist
- [ ] All Phase 1 tasks checked off
- [ ] All Phase 2 tasks checked off
- [ ] All Phase 3 tasks checked off
- [ ] All Phase 4 tasks checked off
- [ ] All Phase 5 tasks checked off
- [ ] All Phase 6 tasks checked off
- [ ] All tests passing (sharded suite green)
- [ ] Audit passed (no significant issues)
- [ ] User verified
