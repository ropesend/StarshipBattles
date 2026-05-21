# PROJ-466 File Manifest

> Generated during /proj-start. Used by /proj-parallel for conflict detection.
> Updated if implementation discovers additional files.

## Files

| File | Type | Notes |
|------|------|-------|
| game/screen_router.py | Production | Phase 1: guard `GameSession(...)` (lines 209, 266) with `except SessionInitializationError` |
| game/ui/screens/new_game_setup_controller.py | Production | Phase 1: guard `on_start_callback` (line 186); keep window alive on failure |
| game/simulation/replay/replay_serialization.py | Production | Phase 2/3: TypeError/ValueError -> PersistenceException (115, 139); log unknown TelemetryLevel (558-561) |
| game/strategy/engine/turn_engine.py | Production | Phase 2: merge BattleResolutionError context into EnginePhaseError (322-333) |
| game/strategy/data/planetary_facility.py | Production | Phase 2: ValueError -> ValidationException(RESOURCE_NOT_FOUND) (149) |
| game/strategy/data/ship_stats_cache.py | Production | Phase 2: ValueError -> ValidationException(MISSING_DEPENDENCY) (41) |
| game/strategy/data/fleet_capability_calculator.py | Production | Phase 2: ValueError -> ValidationException(MISSING_DEPENDENCY) (70, 138) |
| game/simulation/battle_runner.py | Production | Phase 2: RuntimeError -> ValidationException(MISSING_DEPENDENCY) (314) |
| game/strategy/engine/happiness_engine.py | Production | Phase 2: add code=INVALID_STATE to ValidationException (96) |
| game/ui/services/modifier_icon_service.py | Production | Phase 2: remove gratuitous Exception from catch tuple (81) |
| game/ui/screens/battle_state_viewer.py | Production | Phase 2: surface JSONDecodeError instead of silent pass (135) |
| game/strategy/data/component_activation_state.py | Production | Phase 3: require_keys+PersistenceException in from_dict (136); StateException in start_activating/deactivating (77, 93) |
| game/strategy/services/fleet_write_service.py | Production | Phase 3: NotImplementedError -> ValidationException (57, 65) |
| game/services/llm/types.py | Production | Phase 3: safe __repr__ for CompletionResult (63) and Message (41) |
| game/ui/services/image/types.py | Production | Phase 3: safe __repr__ for ImageResult (14) |
| game/services/llm/background.py | Production | Phase 3: %r -> %s in worker exception log (293) |
| game/ui/services/image/background.py | Production | Phase 3: %r -> %s in worker exception log (226) |
| game/assets/asset_manager.py | Production | Phase 3: OSError parity in load_planet_image (319); manifest log level (58-60) |
| game/core/roles.py | Production | Phase 3: RoleRegistryReadOnlyError -> GameException base (61) |
| game/strategy/engine/handlers/construction_queue.py | Production | Phase 3: log swallowed validation failure (160) |
| game/strategy/engine/minefield_balance.py | Production | Phase 3: json.load -> json_utils.load_json (162) |
| game/ui/screens/workshop_data_reloader.py | Production | Phase 3: use shared get_tk_root() (22-27) |
| game/ai/satellite_controller.py | Production | Phase 3: logger.debug on silent get_position AttributeError catch (106-109) |
| tests/unit/test_screen_router.py | Test | Phase 1: 2 new SessionInitializationError dialog tests |
| tests/unit/ui/screens/test_new_game_setup_controller.py | Test | Phase 1: 1 new keep-window-alive-on-session-init-error test |
| tests/unit/strategy/test_proj466_exception_hygiene.py | Test | Phase 2/3: new module — domain-exception swaps (replay/planetary/ship_stats/fleet_cap/fleet_write/component_activation) |
| tests/unit/strategy/turn_engine/test_turn_engine_phase_timing.py | Test | Phase 2: 2 new BattleResolutionError context-merge tests |
| tests/unit/ui/screens/test_battle_state_viewer.py | Test | Phase 2: 2 new JSON-decode diff_error tests |
| tests/unit/ui/services/test_modifier_icon_service.py | Test | Phase 2: 2 new narrowed-catch tests (OSError caught, ValueError propagates) |
| tests/unit/test_proj466_phase3_hardening.py | Test | Phase 3: new module — DTO reprs, roles base class, construction-queue logging, minefield json_utils |
| tests/unit/simulation/replay/test_serialization.py | Test | Phase 2: updated 2 boundary tests for PersistenceException |
| tests/unit/strategy/ship_instance/test_ship_stats_cache.py | Test | Phase 2: updated for ValidationException |
| tests/unit/strategy/data/test_fleet_capability_calculator.py | Test | Phase 2: updated for ValidationException |
| tests/unit/strategy/services/test_fleet_write_service.py | Test | Phase 3: updated for ValidationException |
| tests/unit/simulation/test_battle_runner_di.py | Test | Phase 2: updated for ValidationException |
| tests/unit/strategy/data/test_component_activation_state.py | Test | Phase 3: updated 3 tests for StateException |
| tests/unit/core/test_asset_manager.py | Test | Phase 3: updated missing-manifest log-level test (error -> warning) |
| tests/unit/ui/screens/test_workshop_data_reloader.py | Test | Phase 3: updated 2 tests for get_tk_root() |
| game/screen_router.py | Production | Phase 4: removed `_on_new_game_start` SessionInitializationError catch (controller owns new-game failure UX); quickstart keeps its guard |
| game/strategy/engine/minefield_balance.py | Production | Phase 4: restored explicit missing-file WARNING (json_utils.load_json logs missing at DEBUG) |
| game/assets/asset_manager.py | Production | Phase 4: OSError parity on the stellar-object fallback loop too |
