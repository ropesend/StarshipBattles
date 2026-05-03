# Shard 07 — Test Audit Report

## Summary
- Shard: 07
- Files assigned: 80
- Files actually read: 80
- Total findings: 19
- Critical: 1 | Major: 8 | Minor: 10

## Findings

### tests/unit/test_app_public_api.py (~128 LOC)

#### CAT-1: test_configure_logging_callable [CRITICAL]
- **Location**: test_app_public_api.py:126
- **Issue**: Assertion `assert hasattr(app_mod, "configure_logging") or True` always passes because of the `or True` suffix. The test provides zero regression protection.
- **Suggestion**: Remove the `or True` clause and assert the actual presence/absence of `configure_logging` on the module.
- **LOC affected**: 1

### tests/unit/ui/screens/battle_setup/test_renderer.py (~64 LOC)

#### CAT-2: test_rebuild_ui_calls_renderer_rebuild [MAJOR]
- **Location**: test_renderer.py:54-64
- **Issue**: Uses `inspect.getsource(FleetBattleSetupScreen._rebuild_ui)` and string-search `"self.renderer.rebuild(self)" in src` to verify behavior. This tests source text rather than runtime behavior — the test passes if the source contains the right string even if the method is broken at runtime.
- **Suggestion**: Replace with a runtime test that mocks `renderer.rebuild` and asserts it was called with the screen instance.
- **LOC affected**: 11

#### CAT-11: test_renderer_is_stateless_between_calls [MINOR]
- **Location**: test_renderer.py:29-38
- **Issue**: Asserts `r.__dict__ == {}` — checks internal implementation state (an empty `__dict__`) rather than behavioral contract. A future refactor that adds a `__slots__` declaration would break this.
- **Suggestion**: Remove or replace with a behavioral test (e.g., assert that calling rebuild twice with different state produces correct results).
- **LOC affected**: 10

### tests/unit/simulation/test_unified_entry_guard.py (~741 LOC)

#### CAT-2: Multiple source-code grep/scan tests [MAJOR]
- **Location**: test_unified_entry_guard.py:70-78, 80-104, 115-142, 148-194, 204-227, 250-280, 286-296, 302-311, 584-597, 665-679, 685-741
- **Issue**: Approximately 15 test methods in this file exercise only regex/AST scans of production source code, never testing runtime behavior. Specific tests include: `test_whitelist_size_locked` (checks a constant equals 3), `test_no_unwhitelisted_BattleEngine_construction` (greps source), `test_no_def_setup_in_scenario_templates` (AST scan), `test_no_legacy_compatible_comments` (regex), `test_no_scenario_setup_calls_in_production` (grep), `test_no_direct_engine_update_or_start_teams` (grep), `test_no_engine_ref_closure` (grep), `test_no_run_headless_method_on_battle_controller` (regex), `test_battle_screen_start_team_shim_does_not_exist` (regex), `test_no_placeholder_stat_key_anywhere_in_compiler` (grep), and multiple fleet/storm compiler placeholder guards. Zero production code paths are exercised at runtime.
- **Suggestion**: These are contract-guard tests that serve a valid policy-enforcement purpose. Downgraded to MAJOR because blast radius is small (test-only file, no production code changes needed). Consider supplementing the critical invariants (e.g., `BattleScreen.start` deletion, `extract_battle_results` signature, `BattleController` outcome emission) with behavioral tests that actually call the APIs.
- **LOC affected**: ~500

#### CAT-11: test_whitelist_size_locked [MINOR]
- **Location**: test_unified_entry_guard.py:70-78
- **Issue**: Hardcoded assertion that `len(self.WHITELIST_FILES) == 3`. Adding a legitimate new whitelist entry breaks this test even when the architecture is sound.
- **Suggestion**: Replace with a check that the whitelist is a specific set of known-files, or check that any new entry has explicit justification.
- **LOC affected**: 9

### tests/unit/ui/screens/test_planet_selection_window.py (~63 LOC)

#### CAT-2: Default parameter inspection tests [MAJOR]
- **Location**: test_planet_selection_window.py:28-62
- **Issue**: Both `test_default_parameters_backward_compatible` and `test_custom_parameters_accepted` only inspect constructor signatures via `inspect.signature`, never instantiate the class or exercise any behavior. Zero regression protection for actual functionality.
- **Suggestion**: Replace with tests that instantiate `PlanetSelectionWindow` and verify window title, list label, and button visibility.
- **LOC affected**: 35

### tests/unit/ui/screens/test_strategy_detail_formatter.py (~396 LOC)

#### CAT-8: test_show_detail_with_star_system [MINOR]
- **Location**: test_strategy_detail_formatter.py:89-123
- **Issue**: Uses 6 nested `with patch(...)` blocks (`is_star_system`, `is_star`, `is_planet`, `is_fleet`, `is_warp_point`, `is_sector_environment`) to test a single dispatch method. The setup exceeds 50% of the test body.
- **Suggestion**: Extract the 6 `patch` calls into a shared helper or fixture that returns a simplified context manager.
- **LOC affected**: 35

### tests/unit/strategy/engine/test_superweapon_handler_validation.py (~394 LOC)

#### CAT-10: 5 near-identical direct-handler test classes [MAJOR]
- **Location**: test_superweapon_handler_validation.py:87-192
- **Issue**: Five test classes (`TestImplodePlanetCommandHandlerPassesRegistry`, `TestStellerateStarCommandHandlerPassesRegistry`, `TestOpenWarpPointCommandHandlerPassesRegistry`, `TestCloseWarpPointCommandHandlerPassesRegistry`, `TestCreateDysonSphereCommandHandlerPassesRegistry`) each contain a single test with identical structure — the only differences are the handler class, command class, validator method name, and patched module path. This is a textbook `@pytest.mark.parametrize` case.
- **Suggestion**: Merge into one parametrized test class with parameters (handler_cls, cmd_cls, cmd_kwargs, validator_method, patch_path). Estimated consolidation from 5 classes / 5 tests → 1 parametrized test.
- **LOC affected**: ~105

#### CAT-10: 5 near-identical mission-handler test classes [MAJOR]
- **Location**: test_superweapon_handler_validation.py:199-393
- **Issue**: Same pattern as above — five mission-handler test classes with identical validator-pass and ability-rejection tests.
- **Suggestion**: Merge into one parametrized test class.
- **LOC affected**: ~195

### tests/unit/simulation/entities/test_ship_serialization.py (~861 LOC)

#### CAT-10: Round-trip attribute tests [MINOR]
- **Location**: test_ship_serialization.py:328-368
- **Issue**: Six test methods (`test_roundtrip_preserves_name`, `test_roundtrip_preserves_ship_class`, `test_roundtrip_preserves_theme_id`, `test_roundtrip_preserves_team_id`, `test_roundtrip_preserves_color`, `test_roundtrip_preserves_movement_policy`) have identical bodies differing only in attribute name and expected value. The parametrized version would be one test with `@pytest.mark.parametrize("attr", [...])`.
- **Suggestion**: Parametrize with attribute names and value accessors.
- **LOC affected**: ~40

### tests/unit/ui/screens/test_superweapon_input_modes.py (~228 LOC)

#### CAT-10: Mode-setting tests [MINOR]
- **Location**: test_superweapon_input_modes.py:49-102
- **Issue**: Five tests (`test_implode_planet_sets_mode`, `test_stellerate_star_sets_mode`, `test_open_warp_sets_mode`, `test_close_warp_sets_mode`, `test_dyson_sphere_sets_mode`) and five click-routing tests (lines 159-212) have identical bodies differing only in `InputAction`, mode string, and handler method name.
- **Suggestion**: Parametrize both clusters.
- **LOC affected**: ~100

### tests/unit/strategy/data/test_fleet_consumable_aggregator.py (~893 LOC)

#### CAT-10: True/False variant tests [MINOR]
- **Location**: test_fleet_consumable_aggregator.py:84-108, 191-207
- **Issue**: Pairs of tests like `has_resources_for_movement_true` + `has_resources_for_movement_false` and `has_resources_for_warp_true` + `has_resources_for_warp_false` differ only in return values and expected booleans. Same for `consume_returns_true_on_success` / `consume_returns_false_when_insufficient` pairs.
- **Suggestion**: Parametrize with `(return_value, expected)`` tuples.
- **LOC affected**: ~60

### tests/unit/simulation/test_battle_state_serialization.py (~1394 LOC)

#### CAT-10: Round-trip field comparisons [MINOR]
- **Location**: test_battle_state_serialization.py:306-328
- **Issue**: `test_round_trip_minimal` asserts 19 individual field comparisons in a row. While each assertion is valid, this pattern of identical-structure per-field checks could be simplified at the module level.
- **Suggestion**: Low priority — consider extracting a `assert_ship_state_equal(restored, original)` helper if this pattern repeats across multiple test classes.
- **LOC affected**: 23

### tests/unit/ui/screens/test_race_setup_screen.py (~1256+ LOC)

#### CAT-5: Heavy bypass-init fixture [MINOR]
- **Location**: test_race_setup_screen.py:31-148
- **Issue**: The `_make_race_setup_screen` helper (function-scoped) builds ~50 mock objects for each test. While individual mocks are cheap, the setup is extensive and many tests only use a subset. Function scope causes repeated reconstruction for every test.
- **Suggestion**: Downgraded to MINOR because the mocks are lightweight MagicMock instances. Consider class-scoped fixture for the base mock set, with per-test overrides where needed.
- **LOC affected**: ~118 (setup helper)

## File Coverage Verification
| File | Status | Findings |
|------|--------|----------|
| tests/unit/simulation/components/test_facing_angle_modifier.py | Read ✓ | 0 |
| tests/unit/simulation/combat/test_ability_stat_registry.py | Read ✓ | 0 |
| tests/unit/simulation/entities/test_ship_external_stats_serialization_guard.py | Read ✓ | 0 |
| tests/unit/strategy/data/test_fleet_consumable_aggregator.py | Read ✓ | 1 |
| tests/unit/core/test_application_context.py | Read ✓ | 0 |
| tests/unit/simulation/entities/test_ship_serialization.py | Read ✓ | 1 |
| tests/unit/ui/builder/test_weapons_viewmodel.py | Read ✓ | 0 |
| tests/unit/simulation/test_battle_outcome_replay_id.py | Read ✓ | 0 |
| tests/unit/research/test_research_tracker.py | Read ✓ | 0 |
| tests/unit/strategy/data/test_race_point_budget_v2.py | Read ✓ | 0 |
| tests/integration/ui/test_camera_zoom.py | Read ✓ | 0 |
| tests/unit/strategy/engine/test_population_engine.py | Read ✓ | 0 |
| tests/unit/entities/test_component_di.py | Read ✓ | 0 |
| tests/unit/core/test_role.py | Read ✓ | 0 |
| tests/integration/ui/test_strategy_buttons.py | Read ✓ | 0 |
| tests/unit/services/llm/test_factory.py | Read ✓ | 0 |
| tests/integration/strategy/facade/test_facade_integration.py | Read ✓ | 0 |
| tests/unit/strategy/engine/test_atmosphere_engine.py | Read ✓ | 0 |
| tests/unit/simulation/combat/test_telemetry.py | Read ✓ | 0 |
| tests/unit/ui/screens/test_event_log_replay_button.py | Read ✓ | 0 |
| tests/unit/strategy/engine/test_superweapon_handler_validation.py | Read ✓ | 2 |
| tests/unit/ui/test_sprite_loading.py | Read ✓ | 0 |
| tests/unit/test_app_public_api.py | Read ✓ | 1 |
| tests/unit/ui/screens/test_battle_screen_edge_cases.py | Read ✓ | 0 |
| tests/integration/strategy/combat/test_suppressor_effects.py | Read ✓ | 0 |
| tests/unit/ui/test_battle_screen.py | Read ✓ | 0 |
| tests/unit/ui/test_colors.py | Read ✓ | 0 |
| tests/unit/strategy/facade/test_population_dtos.py | Read ✓ | 0 |
| tests/unit/ui/screens/test_camera_navigator.py | Read ✓ | 0 |
| tests/unit/ui/screens/test_strategy_window_manager.py | Read ✓ | 0 |
| tests/unit/builder/test_requirement_abilities.py | Read ✓ | 0 |
| tests/unit/ui/screens/battle_setup/test_renderer.py | Read ✓ | 2 |
| tests/unit/simulation/components/abilities/test_planetary_abilities.py | Read ✓ | 0 |
| tests/integration/strategy/test_fleet_registration_lifecycle.py | Read ✓ | 0 |
| tests/unit/ui/screens/test_workshop_event_router_select_component.py | Read ✓ | 0 |
| tests/repro_issues/test_bug_11_hull_update.py | Read ✓ | 0 |
| tests/integration/strategy/test_warp_orders.py | Read ✓ | 0 |
| tests/unit/research/tech_tree/test_queries.py | Read ✓ | 0 |
| tests/unit/ui/screens/test_race_setup_screen.py | Read ✓ | 1 |
| tests/unit/modifiers/test_multi_ability_effects.py | Read ✓ | 0 |
| tests/unit/tools/test_regenerate_ship_portraits.py | Read ✓ | 0 |
| tests/unit/ui/services/test_design_loader_adapter.py | Read ✓ | 0 |
| tests/unit/ui/screens/test_build_queue_helpers.py | Read ✓ | 0 |
| tests/unit/ui/panels/test_strategy_widgets.py | Read ✓ | 0 |
| tests/unit/simulation/abilities/test_empire_storage.py | Read ✓ | 0 |
| tests/unit/ui/components/table/test_header.py | Read ✓ | 0 |
| tests/unit/systems/test_layer_restrictions_refactor.py | Read ✓ | 0 |
| tests/unit/ui/screens/test_strategy_detail_formatter.py | Read ✓ | 1 |
| tests/unit/strategy/test_game_session.py | Read ✓ | 0 |
| tests/unit/strategy/pathfinding/test_intercept_recursion.py | Read ✓ | 0 |
| tests/unit/core/test_constants.py | Read ✓ | 0 |
| tests/unit/strategy/generation/density/test_ring.py | Read ✓ | 0 |
| tests/unit/ui/screens/test_planet_selection_window.py | Read ✓ | 1 |
| tests/unit/modifiers/test_formula_error_handling.py | Read ✓ | 0 |
| tests/unit/ui/screens/test_planet_abilities_window_lifecycle.py | Read ✓ | 0 |
| tests/unit/simulation/services/test_registry_loader.py | Read ✓ | 0 |
| tests/unit/strategy/consumable_management_engine/test_auto_disable.py | Read ✓ | 0 |
| tests/integration/ui/build_queue_screen/test_basics.py | Read ✓ | 0 |
| tests/unit/entities/test_ability_interface.py | Read ✓ | 0 |
| tests/unit/simulation/test_unified_entry_guard.py | Read ✓ | 2 |
| tests/unit/simulation/components/abilities/test_stat_keys.py | Read ✓ | 0 |
| tests/integration/strategy/combat/test_damage_persistence.py | Read ✓ | 0 |
| tests/unit/simulation/battle_controller/test_utilities.py | Read ✓ | 0 |
| tests/unit/simulation/test_battle_state_serialization.py | Read ✓ | 1 |
| tests/unit/strategy/pathfinding/test_basic_paths.py | Read ✓ | 0 |
| tests/unit/workshop/test_quick_add.py | Read ✓ | 0 |
| tests/unit/strategy/empire/test_empire_validation.py | Read ✓ | 0 |
| tests/unit/strategy/data/test_component_activation_state.py | Read ✓ | 0 |
| tests/unit/ui/screens/test_fleet_detail_fmt.py | Read ✓ | 0 |
| tests/unit/strategy/test_fleet_battle_adapter.py | Read ✓ | 0 |
| tests/unit/simulation/components/test_size_mount_sub_one.py | Read ✓ | 0 |
| tests/unit/core/test_validation_helpers.py | Read ✓ | 0 |
| tests/unit/modifiers/test_crew_resource_bindings.py | Read ✓ | 0 |
| tests/unit/ai/test_policy_manager.py | Read ✓ | 0 |
| tests/unit/builder/test_fleet_composition.py | Read ✓ | 0 |
| tests/unit/simulation/components/abilities/test_defense_integration.py | Read ✓ | 0 |
| tests/unit/workshop/test_move_component.py | Read ✓ | 0 |
| tests/unit/core/test_service_injection.py | Read ✓ | 0 |
| tests/unit/ui/screens/test_superweapon_input_modes.py | Read ✓ | 1 |
| tests/unit/strategy/engine/test_action_execution_engine.py | Read ✓ | 0 |

## Context Usage Estimate
- Total LOC read (test files + production code): ~28,000 (80 test files ≈ 23,751 + production code imports read inline)
- Approximate headroom: Medium (200-500K remaining)
