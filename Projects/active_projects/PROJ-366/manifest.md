# PROJ-366 File Manifest

> Generated during /proj-start. Used by /proj-parallel for conflict detection.
> Updated if implementation discovers additional files.

## Files modified or created

| File | Type | Phase | Notes |
|------|------|-------|-------|
| `game/app_bootstrap.py` | Production (modify) | 1, 2 | Construct `ReplayStore`, call `set_default_capture_sink(store)` + `set_replay_store(store)` (Phase 1); construct + `start()` `ReplayVerificationCoordinator`; extend `BootstrapResult` with `replay_store` + `replay_verification_coordinator` fields (Phase 2). Wrap each in `_timed_phase` blocks. |
| `game/run_loop.py` | Production (modify) | 2 | Add `shutdown_all_coordinators(timeout=5.0)` between `shutdown_all_calls(timeout=5.0)` and `pygame.quit()`. |
| `tests/unit/test_app_bootstrap_invariants.py` | Test (modify) | 1, 2 | Add Invariant 7: `set_default_capture_sink(store)` is called once after `ApplicationContext.create_production()`. Add Invariant 8: `replay_verification_coordinator.start()` is called and the listener is registered on `replay_store`. |
| `tests/integration/replay/test_verification_queue_integration.py` | Test (new) | 3 | End-to-end: live battle → sidecar `status=PASSED`; `verification_enabled=False` → sidecar `status=SKIPPED_DISABLED`. Cleanup via `reset_default_capture_sink` + `set_replay_store(None)`. |
| `tests/integration/replay/test_headless_visual_equivalence.py` | Test (new) | 3 | `run_replay_headless` outcome dict == `BattleController.start_from_spec` outcome dict. Boundary: `BattleController`, NOT `BattleScreen` (no Pygame UI). |
| `tests/integration/replay/test_verification_uses_production_materializer.py` | Test (new) | 3 | Spy/monkeypatch around `build_replay_ship_builder`; trigger battle; assert spy called and sidecar `status=PASSED`. |
| `tests/integration/replay/test_combat_lab_verification.py` | Test (new) | 4 | Combat Lab synthetic record + fallback wired → sidecar `status=PASSED`. No fallback wired → sidecar `status=ERROR` with diagnostic message. |
| `tests/unit/simulation/replay/test_replay_verifier_imports.py` | Test (new) | 4 | AST lint: `replay_verifier.py` has no `game.strategy.*` / `game.ui.*` / `game.ai.*` imports. |
| `docs/systems/combat_simulation.md` | Documentation (modify) | 4 | § 11 Replay Capture & Playback — add "Background Verification" subsection (post-persist trigger, sidecar schema, settings, no-recursion guarantee). Update `> **Last verified:**` blockquote. |
| `docs/systems/strategy_layer.md` | Documentation (modify) | 4 | Replay Persistence section — add sidecar schema/lifecycle, `add_on_record_persisted_listener` API, `verification_status` field on `ReplayLookup`. Update `> **Last verified:**` blockquote. |
| `docs/01_ARCHITECTURE.md` | Documentation (modify) | 4 | Strategy services table — add `ReplayVerificationCoordinator` row pointing to `game/strategy/services/replay_verification_coordinator.py`. Update `> **Last verified:**` blockquote. |
| `Projects/active_projects/PROJ-354B/plan.md` | Documentation (modify) | 4 | Quick Status table: mark Phases 5-6 as `Complete (via PROJ-366)`. Update Current State to point at the resolution. |

## Files referenced for context (read, do not modify)

| File | Purpose |
|------|---------|
| `game/simulation/replay/replay_capture.py:118` | `set_default_capture_sink(sink)` API; default sink is `NullCaptureSink` |
| `game/strategy/systems/save_game_service.py:33` | `set_replay_store(store)` API; `_notify_replay_store_save_or_load` lifecycle hook |
| `game/strategy/services/replay_store.py` | `ReplayStore` class — implements `IReplayCaptureSink`; constructor signature; `replay_dir` public property (audit-remediation `27e297815`) |
| `game/strategy/services/replay_verification_coordinator.py:151-217` | `ReplayVerificationCoordinator.__init__` + `start()` semantics |
| `game/strategy/services/replay_verification_coordinator.py:74` | `shutdown_all_coordinators(timeout)` module helper |
| `game/strategy/services/replay_ship_builder.py` | `build_replay_ship_builder` — production materializer (extracted from `replay_player.py` in audit-remediation) |
| `game/services/llm/background.py:345-368` | `shutdown_all_calls` reference pattern |
| `game/ai/ai_factory.py` | `AIControllerFactory` |
| `game/core/registry.py` | `get_default_registry_provider()` |
| `game/combat_lab/design_loader.py` | `load_combat_lab_design` synthetic-builder fallback |
| `game/simulation/replay/replay_player.py:89` | `run_replay_headless(record, *, ai_factory, ship_builder, registry_provider)` |
| `game/simulation/battle_controller.py:58` | `BattleController.__init__` (ai_factory parameter) — used by Phase 3 equivalence test |
| `Projects/active_projects/PROJ-354B/plan.md` | Parent project plan (Phases 1-4 complete; Phases 5-6 blocked) |
| `Projects/active_projects/PROJ-354B/decisions.md` | Audit-remediation decisions; AR-001 layer-violation fix is foundation for verifier-import lint |
