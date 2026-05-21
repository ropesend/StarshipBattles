# Shard 09 — Test Audit Report
## Summary
- Shard: 09 | Files assigned: 87 | Files actually read: 87 | Total findings: 9 | Critical: 0 | Major: 2 | Minor: 7
## Findings

### tests/unit/simulation/components/abilities/test_superweapons.py
#### CAT-10: test_ability_instantiates + test_ability_via_create_ability + test_layer_is_strategic + test_allowed_scopes_is_self_only + test_default_scope_is_self + test_stat_bindings_empty + test_get_primary_value_returns_zero + test_action_time_default_with_boolean_marker + test_action_time_from_dict + test_action_time_default_with_dict_missing_key  [MINOR]
- **Location**: test_superweapons.py:42-162 | **Issue**: 10 test methods each use `@pytest.mark.parametrize("ability_name", SUPERWEAPON_ABILITIES.keys())` with identical parametrization over the same set of 6 abilities. The 10 method names differ only by the expected assertion value. | **Suggestion**: Collapse the 4 scope-related methods (layer+scope) into one parametrized method with multiple assertions, and the 3 action_time methods into one. Would reduce 10 methods to ~4. | **LOC affected**: ~120

### tests/unit/simulation/components/abilities/test_superweapons.py
#### CAT-9: test_get_ui_rows_returns_superweapon_row  [MINOR]
- **Location**: test_superweapons.py:113-126 | **Issue**: This test method uses a different parametrize form than the other 10 methods in the file (uses `.items()` instead of `.keys()`) but is the only UI-rows test in the class. It would fit better consolidated with the other identity tests in `TestSuperweaponRegistryPresence` or `TestSuperweaponAbilityInstantiation`. | **Suggestion**: Move to a combined parametrized test that checks registry presence, UI rows, and scope in one pass. | **LOC affected**: 14

### tests/integration/colonization/test_planet_specific_colonization.py
#### CAT-4: test_colonize_without_drop_pod_succeeds_at_command_time + test_fleet_with_no_pods_succeeds_at_command_time  [MAJOR]
- **Location**: test_planet_specific_colonization.py:309-337 and 638-659 | **Issue**: Both tests verify the same contract: "Fleet without a drop pod passes validation at command time." They use different fleet compositions (combat-ship-only vs fully-ship-without-pod) and assert the same result (`result.is_valid is True`). | **Suggestion**: Merge into a single parametrized test or keep one and delete the other. The combat-ship variant (line 309) is the stronger test. | **LOC affected**: ~50

### tests/integration/colonization/test_planet_specific_colonization.py
#### CAT-9: component_registry fixture has duplicate keys  [MINOR]
- **Location**: test_planet_specific_colonization.py:172-186 | **Issue**: The `component_registry` fixture defines `'colony_pod'` three times with identical content (lines 174-186). This is a copy-paste artifact — only one `'colony_pod'` entry is needed. Python dict takes the last value so it's silently non-breaking, but misleading. | **Suggestion**: Remove the duplicate `'colony_pod'` entries (lines 178-186). | **LOC affected**: 12

### tests/unit/ui/screens/test_build_queue_screen_lifecycle.py
#### CAT-3: _spy_invalidate asserts non-existent method — tests intentionally red (TDD Phase 2 not yet landed)  [CRITICAL]
- **Location**: test_build_queue_screen_lifecycle.py:877-891 | **Issue**: Helper function `_spy_invalidate(vt)` asserts `hasattr(vt, "invalidate_widget_caches")` and will raise `AssertionError` if the method does not exist. The docstring confirms: "On current main this assertion fails with a clear message — the test is intentionally red until Phase 2 lands" (line 885-886). Called by 4 tests: `test_PROJ410_task_1_2_yard_switch_invalidates_widget_caches`, `test_PROJ410_task_1_3_close_and_reopen_invalidates_cache`, `test_PROJ410_task_1_5_ship_yard_to_planetary_yard_invalidates`, `test_issue17_reopen_after_yard_switch_clears_stale_label_text`. All 4 tests will fail at `_spy_invalidate` call site. | **Suggestion**: These are valid TDD tests per AGENTS.md Rule 1, but they pollute CI results until the implementation lands. Either skip them with `@pytest.mark.skip(reason="PROJ-410 Phase 2 pending")` or move them to a separate file gated on the feature branch. | **LOC affected**: ~500

### tests/unit/ui/screens/test_setup_screen.py
#### CAT-10: test_handle_event_method_exists + test_update_method_exists + test_draw_method_exists  [MINOR]
- **Location**: test_setup_screen.py:389-408 | **Issue**: Three methods in `TestBattleSetupScreenISceneProtocol` follow an identical pattern: create screen, check `hasattr(screen, method)` and `callable(screen.method)`. Only the method name differs. | **Suggestion**: Parametrize: `@pytest.mark.parametrize("method", ["handle_event", "update", "draw"])` with one test body. | **LOC affected**: 20

### tests/unit/ui/screens/test_race_setup_screen.py
#### CAT-9: Repeated mock function definitions inline in test methods  [MINOR]
- **Location**: test_race_setup_screen.py:155-167, 173-190, 304-309, 345-352, etc. | **Issue**: At least 10 test methods in `TestRaceSetupTabNavigation`, `TestRaceSetupDataFlow`, `TestRaceSetupValidation`, and other classes define ad-hoc mock functions (`mock_show_step`, `mock_update_config`, `mock_validate_for_save`, etc.) in the test body. These one-off mocks add ~5-10 LOC per test. | **Suggestion**: Extract a shared `_make_race_setup_screen_with_mock` helper that installs a configurable mock delegate set, or use `unittest.mock.patch` to patch the real methods directly. | **LOC affected**: ~150

### tests/unit/strategy/engine/test_production_engine_queue.py
#### CAT-10: test_construction_queue_paused_skips_colony_base_queue + test_fleet_pause_flag_blocks_fleet_queue_processing  [MINOR]
- **Location**: test_production_engine_queue.py:125-143 and 245-258 | **Issue**: Both tests verify that a `construction_queue_paused=True` flag blocks queue progress. One is for planet colonies, the other for fleets. The test bodies are structurally identical (create item, set pause flag, assert resources_consumed == 0.0). | **Suggestion**: Parametrize with colony vs fleet variants. | **LOC affected**: 33

### tests/unit/strategy/engine/test_planet_energy_engine.py
#### CAT-10: test_energy_generation_increases_energy + test_multiple_generators_stack + test_generation_and_drain_balance + test_shield_drains_energy  [MINOR]
- **Location**: test_planet_energy_engine.py:211-269 | **Issue**: Four tests in `TestPlanetEnergyEngine` each create a mock planet/facility/empire, call `process_energy_tick`, and assert `planet.energy == pytest.approx(...)`. The setup follows the same `_make_facility` + `_make_planet` + `_make_empire` pattern differing only in facility composition and expected energy value. | **Suggestion**: Consolidate into one parametrized test: `@pytest.mark.parametrize("facilities,initial_energy,expected", [...])`. | **LOC affected**: ~60

## File Coverage Verification

| File | Lines | Read | Status |
|------|-------|------|--------|
| tests/unit/builder/test_fleet_composition.py | 147 | YES | Reviewed |
| tests/repro_issues/test_bug_12_hull_layer_addition.py | 49 | YES | Reviewed |
| tests/unit/simulation/components/abilities/test_superweapons.py | 162 | YES | Reviewed |
| tests/unit/simulation/entities/test_ship_layer_manager.py | 151 | YES | Reviewed |
| tests/unit/ai/test_ai_protocols.py | 246 | YES | Reviewed |
| tests/projects/phase_workflow/test_state.py | 318 | YES | Reviewed |
| tests/integration/strategy/test_demographics_loop.py | 279 | YES | Reviewed |
| tests/unit/simulation/systems/test_battle_end_conditions_n_team.py | 105 | YES | Reviewed |
| tests/unit/ui/screens/test_setup_screen.py | 436 | YES | Reviewed |
| tests/unit/strategy/data/test_fleet_hierarchy.py | 718 | YES | Reviewed |
| tests/unit/test_lab/test_visual_run.py | 446 | YES | Reviewed |
| tests/integration/strategy/test_commands.py | 284 | YES | Reviewed |
| tests/unit/ai/test_policy_manager.py | 228 | YES | Reviewed |
| tests/unit/strategy/engine/test_planet_energy_engine.py | 458 | YES | Reviewed |
| tests/unit/strategy/engine/test_game_session_projection_boundary.py | 135 | YES | Reviewed |
| tests/unit/core/test_string_utils.py | 57 | YES | Reviewed |
| tests/unit/ui/filters/test_filter_state.py | 16 | YES | Reviewed |
| tests/unit/builder/test_builder_improvements.py | 107 | YES | Reviewed |
| tests/unit/strategy/fleet_navigation/test_projection.py | 288 | YES | Reviewed |
| tests/unit/simulation/systems/test_battle_engine_init_ship.py | 124 | YES | Reviewed |
| tests/unit/ui/screens/test_race_setup_screen.py | 1276 | YES | Reviewed |
| tests/unit/core/test_constants.py | 44 | YES | Reviewed |
| tests/unit/ui/screens/test_workshop_viewmodel_pick_up.py | 192 | YES | Reviewed |
| tests/unit/ui/screens/test_food_allocation_editor.py | 436 | YES | Reviewed |
| tests/unit/test_exit_dialog.py | 170 | YES | Reviewed |
| tests/unit/strategy/combat/test_fighter_group_combat_join.py | 114 | YES | Reviewed |
| tests/unit/strategy/engine/test_quality_engine.py | 158 | YES | Reviewed |
| tests/unit/strategy/services/test_ability_metadata_contracts.py | 182 | YES | Reviewed |
| tests/unit/tools/test_summarize_test_baseline.py | 91 | YES | Reviewed |
| tests/unit/ui/renderer/test_game_renderer.py | 371 | YES | Reviewed |
| tests/unit/core/test_protocols_common.py | 35 | YES | Reviewed |
| tests/unit/simulation/systems/test_battle_logger.py | 317 | YES | Reviewed |
| tests/unit/ui/screens/test_click_gate_integration.py | 479 | YES | Reviewed |
| tests/static_guards/test_no_legacy_storage_fields.py | 428 | YES | Reviewed |
| tests/unit/strategy/data/test_facility_resource_tracking.py | 434 | YES | Reviewed |
| tests/unit/validation/test_mini_weapon_resource_consumption.py | 124 | YES | Reviewed |
| tests/unit/simulation/battle_controller/test_start_from_spec.py | 264 | YES | Reviewed |
| tests/unit/simulation/services/test_modifier_service.py | 1039 | YES | Reviewed |
| tests/unit/ai/spatial_behaviors/test_spatial_behaviors.py | 437 | YES | Reviewed |
| tests/unit/strategy/engine/test_pod_transfer.py | 258 | YES | Reviewed |
| tests/unit/core/resources_registry/test_integration.py | 324 | YES | Reviewed |
| tests/unit/strategy/test_fleet_speed_calculator.py | 243 | YES | Reviewed |
| tests/unit/strategy/facade/test_facade_robust_resolution.py | 92 | YES | Reviewed |
| tests/unit/simulation/projectile_guidance/conftest.py | 49 | YES | Reviewed |
| tests/integration/ui/build_queue_screen/test_basics.py | 510 | YES | Reviewed |
| tests/unit/strategy/services/ability_sources/test_planet_intrinsic.py | 121 | YES | Reviewed |
| tests/unit/core/test_simulation_constants.py | 54 | YES | Reviewed |
| tests/unit/ui/screens/test_save_selection_window.py | 262 | YES | Reviewed |
| tests/unit/simulation/systems/test_exit_policy.py | 143 | YES | Reviewed |
| tests/unit/strategy/facade/test_star_info_dto.py | 215 | YES | Reviewed |
| tests/integration/strategy/test_habitability_on_economy.py | 370 | YES | Reviewed |
| tests/unit/strategy/data/test_fighter_wing.py | 119 | YES | Reviewed |
| tests/unit/ui/test_empire_asset_loading.py | 369 | YES | Reviewed |
| tests/unit/ui/services/battle_ui_service/test_state_and_integration.py | 623 | YES | Reviewed |
| tests/unit/strategy/engine/test_colonize_mission_handler.py | 277 | YES | Reviewed |
| tests/unit/strategy/data/test_group_policy_registry_characterization.py | 218 | YES | Reviewed |
| tests/integration/strategy/combat/test_suppressor_effects.py | 322 | YES | Reviewed |
| tests/unit/strategy/data/test_order_serializer.py | 419 | YES | Reviewed |
| tests/fixtures/test_perf_smoke_scenario.py | 86 | YES | Reviewed |
| tests/unit/strategy/turn_engine/test_dependency_injection.py | 465 | YES | Reviewed |
| tests/integration/strategy/test_radiation.py | 68 | YES | Reviewed |
| tests/unit/ui/screens/strategy_render/test_grid_and_storms.py | 111 | YES | Reviewed |
| tests/integration/colonization/test_planet_specific_colonization.py | 683 | YES | Reviewed |
| tests/unit/strategy/adapters/test_no_ai_import.py | 49 | YES | Reviewed |
| tests/unit/strategy/engine/order_handlers/test_superweapon_dispatch.py | 91 | YES | Reviewed |
| tests/unit/simulation/components/test_component_stats_calculator.py | 252 | YES | Reviewed |
| tests/unit/ui/screens/test_build_queue_screen_lifecycle.py | 1352 | YES | Reviewed |
| tests/unit/strategy/turn_engine/test_turn_engine_phase_320_movement_diff.py | 159 | YES | Reviewed |
| tests/integration/test_design_load_warp_capability.py | 186 | YES | Reviewed |
| tests/unit/simulation/components/abilities/test_stat_keys.py | 264 | YES | Reviewed |
| tests/integration/strategy/production/test_fleet_production_e2e.py | 372 | YES | Reviewed |
| tests/unit/strategy/engine/test_production_normalisation.py | 125 | YES | Reviewed |
| tests/unit/strategy/test_race_randomizer.py | 591 | YES | Reviewed |
| tests/unit/simulation/entities/stat_contributors/test_launch.py | 119 | YES | Reviewed |
| tests/integration/test_fms_a_e2e.py | 344 | YES | Reviewed |
| tests/integration/ui/test_battle_setup_three_sides.py | 120 | YES | Reviewed |
| tests/unit/strategy/engine/test_command_registry_thirdparty.py | 137 | YES | Reviewed |
| tests/integration/strategy/test_fleet_through_unstable_warp_point.py | 106 | YES | Reviewed |
| tests/integration/replay/test_event_log_graceful_degradation.py | 158 | YES | Reviewed |
| tests/unit/strategy/data/test_cargo_tracking.py | 377 | YES | Reviewed |
| tests/unit/research/research_scene/conftest.py | 36 | YES | Reviewed |
| tests/unit/strategy/engine/test_component_activation_engine.py | 226 | YES | Reviewed |
| tests/unit/validation/test_maintenance_components.py | 138 | YES | Reviewed |
| tests/unit/ui/test_battle_screen.py | 169 | YES | Reviewed |
| tests/unit/strategy/engine/test_production_engine_queue.py | 437 | YES | Reviewed |
| tests/unit/ui/panels/test_build_queue_catalog_threading.py | 54 | YES | Reviewed |
| tests/unit/strategy/pathfinding/test_hybrid_and_intercept.py | 648 | YES | Reviewed |

## Context Usage Estimate
- Files in shard: 87
- Approximate lines read: ~24,800
- Files with findings: 9
- Categories with findings: CAT-3 (1), CAT-4 (1), CAT-9 (3), CAT-10 (4)
- Severity distribution: CRITICAL 1 (TDD red-tests), MAJOR 1 (duplicate coverage), MINOR 7
