# PROJ-354B File Manifest

> Generated during /proj-start. Used by /proj-parallel for conflict detection.
> Updated if implementation discovers additional files.

## Files

### New (production)
| File | Type | Notes |
|------|------|-------|
| `game/simulation/replay/replay_verifier.py` | Production | Pure verifier: `ReplayVerificationResult`, `Difference`, `compute_outcome_diff`, `verify_replay_outcome`. Imports limited to stdlib + simulation/replay DTOs. NO Strategy/UI/AI imports. |
| `game/strategy/services/replay_verification_sidecar.py` | Production | Sidecar schema (`VerificationStatus`, `VerificationSource`, `VerificationSidecar`), `REPLAY_VERIFICATION_SCHEMA_VERSION`, `write_verification_sidecar`, `read_verification_sidecar`, `sidecar_path_for_replay` |
| `game/strategy/services/replay_verification_coordinator.py` | Production | `ReplayVerificationCoordinator` background service. Mirrors `LLMBackgroundCall` pattern. Module-level `_active_coordinators` + `shutdown_all_coordinators(timeout)` helper. |

### Modified (production)
| File | Type | Notes |
|------|------|-------|
| `game/strategy/services/replay_store.py` | Production | Phase 1: extend `ReplaySettings` (lines 56-86) + `load_replay_settings` (67-85) with `verification_enabled` and `verification_queue_cap`. Phase 2: extend `delete` (250-262) + `_evict_excess` (280-299) for sidecars. Phase 3: add `_on_record_persisted_listeners` + `add_on_record_persisted_listener` / `remove_on_record_persisted_listener` methods; fire listeners in `persist` (200-214). |
| `game/strategy/services/replay_resolver.py` | Production | Phase 3: add `verification_status` field to `ReplayLookup` (27-41); read sidecar in `resolve` (75-113) when present. |
| `game/app_bootstrap.py` | Production | Phase 5: construct `ReplayVerificationCoordinator` near `ApplicationContext.create_production()` (lines 157-159) and call `coordinator.start()`. **BLOCKED until prereq sink wiring lands.** |
| `game/run_loop.py` | Production | Phase 5: call `shutdown_all_coordinators(timeout=5.0)` alongside existing `shutdown_all_calls(timeout=5.0)` at lines 84-85. |

### New (tests)
| File | Type | Notes |
|------|------|-------|
| `tests/unit/strategy/services/test_replay_settings.py` (or extend existing) | Test | Phase 1 Task 1.1: settings defaults, override, malformed, type coercion. |
| `tests/unit/simulation/replay/test_replay_verifier.py` | Test | Phase 1 Task 1.2/1.3: verifier pass/fail/diff/cap cases. |
| `tests/unit/strategy/services/test_replay_verification_sidecar.py` | Test | Phase 2 Task 2.1: sidecar round-trip, atomic, missing/corrupt → None. |
| `tests/unit/strategy/services/test_replay_verification_coordinator.py` | Test | Phase 4 Task 4.1/4.5: coordinator queueing, cap, toggle, exception isolation, no-recursion. |
| `tests/integration/replay/test_verification_queue_integration.py` | Test | Phase 5 Task 5.3: end-to-end live battle → queue → sidecar. |
| `tests/integration/replay/test_headless_visual_equivalence.py` | Test | Phase 5 Task 5.4: `run_replay_headless` outcome == `BattleController.start_from_spec` outcome. Boundary at `BattleController`, not `BattleScreen`. |
| `tests/integration/replay/test_verification_uses_production_materializer.py` | Test | Phase 5 Task 5.5: coordinator uses `build_replay_ship_builder` (production), not hand-built test builder. |
| `tests/integration/replay/test_combat_lab_verification.py` | Test | Phase 6 Task 6.1: Combat Lab record verification with explicit fallback builder; ERROR when no snapshots and no fallback. |
| `tests/unit/simulation/replay/test_replay_verifier_imports.py` | Test | Phase 6 Task 6.2: AST lint — verifier doesn't import Strategy/UI/AI. |

### Modified (tests)
| File | Type | Notes |
|------|------|-------|
| `tests/integration/replay/test_replay_store.py` | Test | Phase 2 Task 2.2/2.3: new `test_delete_removes_sidecar`, `test_evict_removes_sidecars_alongside_records`. Phase 3 Task 3.1: new listener tests (subscribe, unsubscribe, multiple, exception isolation, no-listener path). |
| `tests/unit/strategy/test_replay_resolver.py` | Test | Phase 3 Task 3.2: new `verification_status` field tests. |

### Modified (docs)
| File | Type | Notes |
|------|------|-------|
| `docs/systems/combat_simulation.md` | Docs | Phase 6 Task 6.3: § 11 Background Verification subsection. |
| `docs/systems/strategy_layer.md` | Docs | Phase 6 Task 6.4: Replay Persistence section — sidecar schema/lifecycle, listener API, `verification_status`. |
| `docs/01_ARCHITECTURE.md` | Docs | Phase 6 Task 6.5: Strategy services table — register `ReplayVerificationCoordinator`. |

## Files NOT touched (out of scope)

| File | Why excluded |
|------|--------------|
| `game/services/llm/background.py` | Reference template only; reused via mirroring pattern, not extended. |
| `game/strategy/services/race_description_llm_controller.py` | Reference consumer pattern only. |
| `game/strategy/systems/save_game_service.py` | `set_replay_store` exists but is unused in production today. The user is wiring the prereq separately. |
| `game/simulation/battle_runner.py` | Capture path unchanged. |
| `game/simulation/battle_controller.py` | Visual-mode parallel hook unchanged. |
| `game/simulation/replay/replay_capture.py` | Sink protocol unchanged. |
| `game/simulation/replay/replay_player.py` | `run_replay_headless` and `build_replay_ship_builder` consumed as-is. |
| `combat_lab/design_loader.py` | `load_combat_lab_design` consumed as fallback builder; not modified. |
