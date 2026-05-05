# PROJ-366: Production replay sink wiring + verification coordinator bootstrap

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-366` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-366 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 0. replay_ship_builder registry-provider contract repair (CRIT) | Not Started | [phase_0_checklist.md](phase_0_checklist.md) |
| 1. Sink wiring + ReplayStore + bootstrap-test cleanup | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Coordinator + start + run-loop shutdown + Combat Lab fallback adapter | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Integration tests (live battle → sidecar; headless-vs-visual; production materializer; no-recursion) | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Combat Lab fallback test + verifier-import lint + docs | Not Started | [phase_4_checklist.md](phase_4_checklist.md) |

## Current State
**Last Updated:** 2026-05-05
**Active Phase:** Planning (just scaffolded)
**Last Action:** Project created from PROJ-354B Phases 5-6 unblock, after confirming codex is not handling the prereq sink wiring.
**Next Action:** Begin Phase 1: construct `ReplayStore` and call `set_default_capture_sink(store)` + `set_replay_store(store)` from `app_bootstrap.py`.
**Blockers:** None. PROJ-354A and PROJ-354B Phases 1-4 have all landed.

**Context for Next Agent:**
PROJ-354B's plan.md asserted that "the user is handling the production sink wiring with codex separately." The user clarified on 2026-05-05 that codex is NOT handling this. PROJ-366 picks up exactly the work that PROJ-354B Phases 5-6 had marked BLOCKED. Phases 1-4 of PROJ-354B are complete (commits `9dabe9042`, `ad42e4d78`, `93608a438`, `ef20ea35d`) and the audit-remediation commit `27e297815` resolved 5 CRIT + 13 MAJ findings against the verifier/sidecar/coordinator. Sharded suite is currently at 17797 passed, 0 failed.

## Overview

Two things are unwired in `game/app_bootstrap.py`:

1. `set_default_capture_sink(replay_store)` — without this, `NullCaptureSink` is the active sink, so live battles never persist replay records.
2. `set_replay_store(replay_store)` — without this, `SaveGameService` save/load/delete hooks never reach the store, so the store's `save_root` never tracks the active save folder.

Once wired, the existing PROJ-354B `ReplayVerificationCoordinator` can subscribe to `ReplayStore.add_on_record_persisted_listener` and run the post-persist verification pipeline. Phase 5 of PROJ-354B (composition root + integration tests) and Phase 6 (Combat Lab fallback + docs + lint) become unblocked and are landed in this project.

## Goals

- Production calls `set_default_capture_sink(replay_store)` and `set_replay_store(replay_store)` exactly once during `bootstrap()` after `InputMapper.load(...)`, before profiler total/save_history/return.
- Production constructs `ReplayVerificationCoordinator` with real `AIControllerFactory` and `get_default_registry_provider()` injection, calls `coordinator.start()`, and exposes both objects on `BootstrapResult` (alongside the existing `ctx`, `screen`, etc.).
- `RunLoop.run()` calls `shutdown_all_coordinators(timeout=5.0)` immediately after `shutdown_all_calls(timeout=5.0)`, before `pygame.quit()`.
- Combat Lab replays use the explicit synthetic-builder fallback (`combat_lab/design_loader.py::load_combat_lab_design`) — no silent global-registry fallback.
- Headless verification of a captured replay produces a `replay_<id>.verification.json` sidecar with `status=PASSED` for a deterministic battle.
- Headless-vs-visual equivalence test pins outcome equality at the `BattleController.start_from_spec` boundary (no Pygame UI dependency).
- Production materializer test proves `build_replay_ship_builder` is the path the coordinator uses.
- Verifier dependency-direction lint asserts `game/simulation/replay/replay_verifier.py` has no `game.strategy.*` / `game.ui.*` / `game.ai.*` imports (already true after audit-remediation commit `27e297815`; we lock it in with a test).
- Docs updated: `docs/systems/combat_simulation.md` § 11, `docs/systems/strategy_layer.md` Replay Persistence, `docs/01_ARCHITECTURE.md` Strategy services table.

## Scope

**In:**
- `game/app_bootstrap.py` — construct `ReplayStore`, call `set_default_capture_sink(store)`, call `set_replay_store(store)`, construct `ReplayVerificationCoordinator(...).start()`, expose both on `BootstrapResult`.
- `game/run_loop.py` — call `shutdown_all_coordinators(timeout=5.0)` immediately after `shutdown_all_calls(timeout=5.0)`, before `pygame.quit()`.
- `tests/unit/test_app_bootstrap_invariants.py` — new invariants pinning sink-wiring order: `ApplicationContext.create_production()` → `set_default_capture_sink(store)` → `set_replay_store(store)` → coordinator `start()`.
- New integration tests under `tests/integration/replay/`:
  - `test_verification_queue_integration.py` — live battle → sidecar with `status=PASSED`; toggle case → `status=SKIPPED_DISABLED`.
  - `test_headless_visual_equivalence.py` — `run_replay_headless` outcome dict == `BattleController.start_from_spec` outcome dict.
  - `test_verification_uses_production_materializer.py` — coordinator wires `build_replay_ship_builder` (not a hand-built test stub).
  - `test_combat_lab_verification.py` — Combat Lab synthetic record verifies via fallback builder; no-fallback + no-snapshots → ERROR sidecar.
- New unit test `tests/unit/simulation/replay/test_replay_verifier_imports.py` — AST lint verifying no upward imports.
- Doc updates: `docs/systems/combat_simulation.md` § 11, `docs/systems/strategy_layer.md` Replay Persistence, `docs/01_ARCHITECTURE.md` Strategy services table.

**Out:**
- Changes to the verifier itself, the coordinator implementation, or the sidecar schema. (PROJ-354B + audit-remediation already shipped these; PROJ-366 only wires them.)
- UI surfacing of verification status badges in the Replay Browser (deferred to a future polish project per PROJ-354B plan).
- Visual-replay verification (user clicks Replay → also verify). Sidecar `source` field reserves `VISUAL_REPLAY` for the future.
- Process-boundary timeout for hostile/runaway verifier code.
- Save/load metadata changes — the store's `save_root` lifecycle is already wired through the existing `SaveGameService._notify_replay_store_*` hooks; this project just connects the missing register-the-store call.
- New AI factory or new registry provider plumbing — production already has both; we inject what exists.

## Key Files Reference

### Modified files (production)

| Component | File Path | Change |
|-----------|-----------|--------|
| Bootstrap | `game/app_bootstrap.py` | Construct `ReplayStore`, call `set_default_capture_sink(store)` + `set_replay_store(store)`, construct + `start()` `ReplayVerificationCoordinator`, expose both on `BootstrapResult` |
| Run loop shutdown | `game/run_loop.py` | Add `shutdown_all_coordinators(timeout=5.0)` between `shutdown_all_calls(...)` and `pygame.quit()` |

### Modified files (tests)

| File | Change |
|------|--------|
| `tests/unit/test_app_bootstrap_invariants.py` | Add invariants for sink-wiring order + coordinator presence on `BootstrapResult` |

### New files

| File | Purpose |
|------|---------|
| `tests/integration/replay/test_verification_queue_integration.py` | End-to-end: live battle → sidecar PASSED / toggle → SKIPPED_DISABLED |
| `tests/integration/replay/test_headless_visual_equivalence.py` | `run_replay_headless` ≡ `BattleController.start_from_spec` outcome dict |
| `tests/integration/replay/test_verification_uses_production_materializer.py` | Coordinator uses `build_replay_ship_builder`, not a hand-built stub |
| `tests/integration/replay/test_combat_lab_verification.py` | Combat Lab fallback path; no-fallback + no-snapshots → ERROR sidecar |
| `tests/unit/simulation/replay/test_replay_verifier_imports.py` | AST lint: no upward imports from the verifier module |

### Reference files (read, do not modify)

| File | Why |
|------|-----|
| `game/simulation/replay/replay_capture.py:118` | `set_default_capture_sink(sink)` API |
| `game/strategy/systems/save_game_service.py:33` | `set_replay_store(store)` API; `_notify_replay_store_save_or_load` lifecycle hooks |
| `game/strategy/services/replay_store.py` | `ReplayStore` constructor (settings + save_root + json_writer + clock); implements `IReplayCaptureSink` |
| `game/strategy/services/replay_verification_coordinator.py:151-217` | Coordinator constructor signature + `start()` semantics |
| `game/strategy/services/replay_ship_builder.py` | Production materializer (`build_replay_ship_builder`) |
| `game/services/llm/background.py:345-368` | `shutdown_all_calls` reference pattern; PROJ-354B mirrors this in `shutdown_all_coordinators` |
| `game/ai/ai_factory.py` | `AIControllerFactory` — instantiated for the coordinator |
| `game/core/registry.py` | `get_default_registry_provider()` — registry source for the coordinator |
| `game/combat_lab/design_loader.py` (`load_combat_lab_design`) | Combat Lab synthetic builder (the explicit fallback per PROJ-354B Phase 6) |
| `game/strategy/services/replay_store.py:210` | `replay_dir` public property (added in PROJ-354B audit-remediation `27e297815`) |

## Decisions Log

See [decisions.md](decisions.md) for the full table. Highlights:
- Codex is NOT handling the sink wiring (user-clarified 2026-05-05) — PROJ-366 owns it.
- Both `ReplayStore` and `ReplayVerificationCoordinator` constructed eagerly in `bootstrap()` (not lazy) so the first battle's record is captured and verified.
- Coordinator DI uses fresh `AIControllerFactory()` + `get_default_registry_provider()` + `load_replay_settings()` + `load_combat_lab_design` fallback — all already in production today.
- Equivalence test boundary at `BattleController.start_from_spec`, not `BattleScreen` — no Pygame UI dependency.

## Phases

### Phase 0: replay_ship_builder registry-provider contract repair [Critical]
**Objective:** Repair `IRegistryProvider` contract usage in
`game/strategy/services/replay_ship_builder.py` (calls non-existent
`get_registries()`). Without this fix, every coordinator verification call
raises `AttributeError` and writes ERROR sidecars.
**Status:** Not Started

See `phase_0_checklist.md` for tasks.

### Phase 1: Sink wiring + ReplayStore + bootstrap-test cleanup [Medium]
**Objective:** `ReplayStore` constructed in `bootstrap()`; sink + store registered globally; existing `SaveGameService._notify_replay_store_*` hooks now route to a real store. Bootstrap test modules grow autouse cleanup so the new coordinator threads don't leak into the next test.
**Status:** Not Started

See `phase_1_checklist.md` for tasks.

### Phase 2: Coordinator + start + run-loop shutdown + Combat Lab fallback adapter [Medium]
**Objective:** `ReplayVerificationCoordinator` constructed and started in `bootstrap()`; exposed on `BootstrapResult`; `shutdown_all_coordinators` wired into `run_loop.py`. Combat Lab fallback adapter (DesignOnlyMaterializer wrapper) wired at construction time.
**Status:** Not Started

See `phase_2_checklist.md` for tasks.

### Phase 3: Integration tests [Complex]
**Objective:** End-to-end coverage proves sink + coordinator + verifier produce sidecars in production-equivalent fixtures via the strategy adapter (production `ship_instance_lookup`); equivalence test pins headless ≡ controller. Includes no-recursion assertion.
**Status:** Not Started

See `phase_3_checklist.md` for tasks.

### Phase 4: Combat Lab fallback test + docs + verifier-import lint [Medium]
**Objective:** Test the Combat Lab fallback path end-to-end; verifier dependency direction locked in by lint test; docs updated.
**Status:** Not Started

See `phase_4_checklist.md` for tasks.

## Verification Checklist

### Project Start (REQUIRED)
- [ ] Read `docs/01_ARCHITECTURE.md`, `docs/02_PATTERNS.md`, `docs/03_CONVENTIONS.md`
- [ ] Read PROJ-354B `plan.md`, `decisions.md` (especially audit-remediation section), Phase 5 & 6 checklists
- [ ] Read `game/app_bootstrap.py`, `game/run_loop.py`, `game/strategy/services/replay_store.py`, `game/strategy/services/replay_verification_coordinator.py`
- [ ] Confirm baseline: `python Tools/test_sharded/test_sharded.py` shows 17797 passed (or current baseline)

### After Each Phase
- [ ] Run focused tests for the touched files
- [ ] Update `Current State` in this plan with handoff context
- [ ] Update phase checklist boxes

### Final Verification
- [ ] Full sharded suite green: `python Tools/test_sharded/test_sharded.py`
- [ ] Manual smoke (if display available): start a fresh game, run a battle, verify `replay_<id>.json` AND `replay_<id>.verification.json` exist under `output/saves/<save>/replays/`
- [ ] Toggle smoke: set `verification_enabled=False` in `output/settings/replay_settings.json`; restart; run a battle; verify sidecar has `status=SKIPPED_DISABLED`
- [ ] Docs match implementation
- [ ] Update PROJ-354B's `plan.md` Quick Status to mark Phases 5-6 as `Complete (via PROJ-366)`

## Audit Log
| Cycle | Date | Findings | Resolution |
|-------|------|----------|------------|
| 1 | | | |

## Completion Checklist
- [ ] All Phase 1 tasks checked off
- [ ] All Phase 2 tasks checked off
- [ ] All Phase 3 tasks checked off
- [ ] All Phase 4 tasks checked off
- [ ] All tests passing (sharded suite green)
- [ ] PROJ-354B Quick Status updated
- [ ] Audit passed
- [ ] User verified
