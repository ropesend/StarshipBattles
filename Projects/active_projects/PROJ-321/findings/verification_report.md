# PROJ-321 Verification Report

> **Path errata (2026-05-03):** Several file paths cited in the review tables below were stale. The implementation manifest and phase checklists use corrected paths. See `../manifest.md` for the canonical paths.

- **Source review directory:** `Reviews/results/2026-05-02_204633_test-review/`
- **Run date:** 2026-05-03
- **Priority tier:** P0 (categories CAT-1, CAT-2, CAT-3)
- **Batch summary:** 79 verified / 1 needs-rework / 3 rejected / 3 out-of-scope out of 78 OpenCode CONFIRMED candidates for this tier.

## Verified

| id | category | severity | file | test_name | suggestion |
|----|----------|----------|------|-----------|------------|
| S01-CAT1-001 | CAT-1 | CRITICAL | `tests/integration/strategy/production/test_queue.py` | test_production_progress | Remove or implement — delete the dead test or add actual assertions; convert to pytest.skip if refactoring still needed. |
| S01-CAT1-002 | CAT-1 | CRITICAL | `tests/unit/ai/test_ai.py` | test_navigate_to_rotates_ship | Add concrete assertion on ship.angle change, or remove and mark with @pytest.mark.skip(reason='Visual verification only'). |
| S01-CAT1-003 | CAT-1 | MINOR | `tests/unit/builder/test_builder_improvements.py` | test_image_scale_factor | Add post-draw assertions or document as smoke test and pair with a behavioral test. |
| S01-CAT1-004 | CAT-1 | MINOR | `tests/unit/ui/screens/battle_setup/test_fleet_hierarchy_editor.py` | test_editor_has_no_instance_state | Remove. Alternatively rename to TestEditorStatelessProperty with explanatory docstring. |
| S01-CAT2-001 | CAT-2 | CRITICAL | `tests/unit/ui/test_race_portrait_gallery.py` | All RacePortraitGallery tests | Rewrite tests to instantiate through normal constructor with mocked pygame_gui dependencies, or migrate to integration tests. |
| S01-CAT2-002 | CAT-2 | MAJOR | `tests/unit/ui/test_race_description_panel.py` | All RaceDescriptionPanel tests | Rewrite to use real construction with mocked pygame_gui, or migrate to integration tests. |
| S01-CAT2-003 | CAT-2 | MAJOR | `tests/unit/modifiers/test_seeker_multi_ability.py` | test_seeker_does_not_use_direct_stats_access | Remove. Behavioral tests test_seeker_endurance_applies_modifier_correctly already verify correct output values. |
| S01-CAT2-004 | CAT-2 | MINOR | `tests/unit/strategy/services/test_fleet_navigation_mutual_pursuit.py` | test_get_destination_default_self_fleet_is_none | Replace with behavioral test test_no_self_fleet_falls_back_to_intercept (line 152) which verifies fallback. |
| S01-CAT2-005 | CAT-2 | MINOR | `tests/unit/simulation/entities/test_ship_component_manager_di.py` | Source-content scan | Keep as-is. If scan logic is duplicated, consider a shared helper. |
| S01-CAT3-001 | CAT-3 | MAJOR | `tests/repro_issues/repro_warp_bug.py` | Standalone repro script | Delete the file. Bugs are covered by proper pytest tests elsewhere. |
| S02-CAT1-001 | CAT-1 | CRITICAL | `tests/unit/services/llm/test_package_imports.py` | test_services_package_importable | Remove — package importability is already validated by other tests. |
| S02-CAT1-002 | CAT-1 | CRITICAL | `tests/unit/services/llm/test_package_imports.py` | test_llm_package_importable | Remove. |
| S02-CAT2-001 | CAT-2 | CRITICAL | `tests/unit/test_modifier_logic.py` | Entire file | Remove entire file. |
| S02-CAT3-001 | CAT-3 | CRITICAL | `tests/regression/test_deprecated_code_removed.py` | test_fleet_movement_simulator_import_fails | Remove this test. The removed module has been gone long enough that regression risk is negligible. |
| S02-CAT3-002 | CAT-3 | MINOR | `tests/repro_issues/repro_load_cargo_bug.py` | Standalone repro script | Review whether bug is still present. If fixed, remove. If still present, convert to focused pytest test in appropriate integration test dir. |
| S03-CAT1-001 | CAT-1 | CRITICAL | `tests/unit/ui/panels/test_race_identity_panel.py` | test_identity_panel_creates_successfully | Remove tautological assertion or replace with real construction-path assertion. |
| S03-CAT1-002 | CAT-1 | CRITICAL | `tests/unit/ui/panels/test_race_identity_panel.py` | test_auto_generate_faction_name_override_preserved | Remove or replace with assertion that the production override-preservation logic actually runs. |
| S03-CAT1-003 | CAT-1 | CRITICAL | `tests/unit/ui/panels/test_component_modifier_grid_panel.py` | 6 trivial store-and-assert tests | Remove the 6 trivially-passing tests or rewrite to exercise real subscription/wiring through the real constructor. |
| S03-CAT1-004 | CAT-1 | CRITICAL | `tests/unit/ui/test_race_flag_gallery.py` | 4 attribute-existence tests | Remove. Replace with real-construction tests that verify the attributes are populated by __init__. |
| S03-CAT1-005 | CAT-1 | CRITICAL | `tests/unit/ui/screens/test_fleet_report_window.py` | 9 mock-assignment-only edge case tests | Remove. Replace with tests that exercise the real selection/edge-case behavior. |
| S03-CAT2-001 | CAT-2 | CRITICAL | `tests/unit/ui/panels/test_race_identity_panel.py` | Most tests bypass-init | Rewrite to construct through real __init__ with mocked pygame_gui, or migrate to integration tests. |
| S04-CAT1-001 | CAT-1 | CRITICAL | `tests/unit/ui/screens/test_battle_setup_state.py` | test_screen_owns_a_view_model | Remove or rewrite to verify that the real constructor wires the view_model. |
| S04-CAT1-002 | CAT-1 | CRITICAL | `tests/integration/test_app_integration.py` | test_menu_ui_manager_created_on_demand | Rewrite to actually invoke the lazy-creation path and assert that menu_ui_manager becomes a real UIManager. |
| S04-CAT1-003 | CAT-1 | CRITICAL | `tests/unit/ui/screens/battle_setup/test_view_model.py` | test_can_construct_without_registries_or_state | Remove or assert specific post-construction state. |
| S04-CAT2-001 | CAT-2 | MAJOR | `tests/unit/strategy/services/test_fleet_navigation_no_mock_hack.py` | test_accepts_can_warp_parameter | Replace with a behavioral test that calls find_hybrid_path with can_warp and verifies pathfinding behavior changes. |
| S04-CAT2-002 | CAT-2 | CRITICAL | `tests/unit/strategy/services/test_fleet_navigation_no_mock_hack.py` | test_no_mock_capabilities_class_in_compute_path | Remove. Replace with behavioral test that verifies real production path does not need MockCapabilities. |
| S04-CAT2-003 | CAT-2 | CRITICAL | `tests/unit/strategy/services/test_fleet_navigation_no_mock_hack.py` | test_can_warp_overrides_fleet_check | Rewrite to either let exceptions propagate or use a focused assertion on observable state. |
| S04-CAT2-004 | CAT-2 | CRITICAL | `tests/integration/test_app_integration.py` | Source text scan for broken call pattern | Replace with behavioral assertion that the production call uses correct kwargs at runtime. |
| S04-CAT2-005 | CAT-2 | MAJOR | `tests/integration/test_app_integration.py` | test_start_quickstart_1p_uses_helper / 2p_uses_helper | Replace with a single behavioral test that calls _start_quickstart with each player_count value. |
| S04-CAT2-006 | CAT-2 | CRITICAL | `tests/unit/ui/panels/test_system_tree_panel.py` | 30+ tests use patch.object(cls, '__init__', ...) | Construct widgets through real __init__ with mocked pygame_gui or migrate to integration tests. |
| S04-CAT2-007 | CAT-2 | CRITICAL | `tests/unit/data/test_test_infrastructure.py` | 8 test_no_duplicate_* methods | Move to a Tools/ linter or pre-commit hook; remove from pytest suite. |
| S04-CAT2-008 | CAT-2 | CRITICAL | `tests/unit/ui/screens/battle_setup/test_view_model.py` | test_no_pygame_import_in_view_model_module | Move to Tools/ linter or pre-commit hook. |
| S05-CAT1-001 | CAT-1 | MINOR | `tests/unit/simulation/components/abilities/test_superweapons.py` | Trivial Pass | Remove. Add zero incremental protection. |
| S06-CAT1-001 | CAT-1 | CRITICAL | `tests/unit/strategy/generation/test_layout_scaling.py` | test_galaxy_layouts_loader_exists | Delete entire file (only 22 LOC of import checks). |
| S06-CAT1-002 | CAT-1 | CRITICAL | `tests/unit/strategy/generation/test_layout_scaling.py` | test_layout_data_has_required_fields | Delete; included in deletion of entire file. |
| S06-CAT1-003 | CAT-1 | CRITICAL | `tests/unit/ui/screens/test_event_log_window.py` | test_module_exists | Remove. |
| S06-CAT1-004 | CAT-1 | CRITICAL | `tests/unit/ui/screens/test_event_log_window.py` | test_sidebar_attr_exists | Fix to `assert hasattr(win, 'sidebar')` or remove. |
| S06-CAT1-005 | CAT-1 | CRITICAL | `tests/unit/ui/screens/test_event_log_window.py` | test_sidebar_panel_attr_defined | Remove. Replace with a behavioral test that uses the constant. |
| S06-CAT1-006 | CAT-1 | CRITICAL | `tests/unit/ui/screens/test_event_log_window.py` | test_update_method_exists | Remove. Behavioral update tests cover this. |
| S06-CAT1-007 | CAT-1 | MAJOR | `tests/unit/ui/screens/test_event_log_window.py` | 4 constant/hasattr tests | Remove or consolidate into a single import-and-attribute smoke test. |
| S06-CAT1-008 | CAT-1 | CRITICAL | `tests/unit/ui/screens/test_event_log_window.py` | 2 facade hasattr tests | Remove or merge with behavioral facade tests. |
| S06-CAT1-009 | CAT-1 | CRITICAL | `tests/unit/core/test_combat_types.py` | test_import_path | Remove. |
| S06-CAT1-010 | CAT-1 | CRITICAL | `tests/unit/simulation/factories/test_ai_factory.py` | 5 existence/attribute tests | Remove all 5 trivial tests. |
| S07-CAT1-001 | CAT-1 | MAJOR | `tests/unit/ui/test_app_public_api.py` | test_configure_logging_callable | Remove the test or replace with a meaningful contract assertion. |
| S07-CAT2-001 | CAT-2 | MAJOR | `tests/unit/ui/screens/battle_setup/test_renderer.py` | test_rebuild_ui_calls_renderer_rebuild | Replace with a behavioral test that calls _rebuild_ui and asserts renderer.rebuild was called. |
| S07-CAT2-002 | CAT-2 | MAJOR | `tests/unit/ui/test_unified_entry_guard.py` | 21 source-scan tests | Move scan-based tests to a CI/lint step; keep only runtime behavioral tests in pytest. |
| S07-CAT2-003 | CAT-2 | MAJOR | `tests/unit/ui/screens/test_planet_selection_window.py` | Signature-only tests | Replace with behavioral tests that construct PlanetSelectionWindow with each parameter combination. |
| S08-CAT1-001 | CAT-1 | CRITICAL | `tests/unit/ui/panels/test_strategy_menu_panel.py` | 7 TestMenuPanelConstants tests | Replace with a single smoke test verifying menu construction works end-to-end. |
| S08-CAT1-002 | CAT-1 | CRITICAL | `tests/unit/strategy/data/test_superweapon_orders.py` | 6 test_*_order_type_exists tests | Replace with a single hasattr-loop test or remove. |
| S08-CAT1-003 | CAT-1 | CRITICAL | `tests/unit/strategy/facade/test_strategy_session_facade_public_api.py` | Public API contract tests | Keep as a contract guard but rename and document; consider moving to a lint step. |
| S08-CAT1-004 | CAT-1 | CRITICAL | `tests/unit/simulation/test_simulation_constants.py` | test_constants_exist | Remove only the 5 hasattr trivia; keep behavioral tests. |
| S08-CAT1-005 | CAT-1 | CRITICAL | `tests/unit/ui/screens/test_empire_build_queue_viewmodel.py` | 3 TestBuildQueueWindowEvents tests | Remove or consolidate into a single attribute-list test. |
| S08-CAT1-006 | CAT-1 | CRITICAL | `tests/unit/strategy/data/test_fleet_display_name.py` | test_two_empires_have_independent_display_numbers | Strengthen to assert independence under interleaved increments, or accept as documentation. |
| S08-CAT3-001 | CAT-3 | CRITICAL | `tests/repro_issues/test_bug_12_energy_gen.py` | WORKING-AS-DESIGNED guard | Move to tests/regression/ with rename; keep as design-intent regression guard. |
| S08-CAT3-002 | CAT-3 | CRITICAL | `tests/unit/ai/interfaces/test_controllable_adapter_edge_cases.py` | TestAttributeDelegationRemoved | Keep as documented removal guard. |
| S09-CAT1-001 | CAT-1 | CRITICAL | `tests/unit/strategy/services/test_intercept_edge_cases.py` | 3 import-existence tests | Delete entire file. |
| S09-CAT1-002 | CAT-1 | CRITICAL | `tests/unit/ui/test_race_theme_gallery.py` | Self-fulfilling assertion tests | Remove. Replace with real-construction tests. |
| S09-CAT1-003 | CAT-1 | MAJOR | `tests/unit/ui/utils/test_race_asset_loader.py` | test_load_portrait_full_has_correct_signature | Remove or replace with a behavioral call. |
| S09-CAT1-004 | CAT-1 | MAJOR | `tests/unit/ui/panels/test_planet_report_panel.py` | test_function_exists | Remove. |
| S09-CAT2-001 | CAT-2 | CRITICAL | `tests/unit/strategy/data/test_production_rates.py` | 3 classes reimplement turn-calculation locally | Rewrite to call production _get_facility_production_rates and assert against fixture data; remove local arithmetic. |
| S09-CAT3-001 | CAT-3 | CRITICAL | `tests/repro_issues/repro_facade_colonies.py` | Standalone repro script | Convert to focused pytest test or delete and add coverage in tests/integration/strategy/facade/test_validation_queries.py. |
| S09-CAT3-002 | CAT-3 | MAJOR | `tests/unit/strategy/test_ship_stat_querier.py` | TestShipStatQuerierCachedSummary | Remove the empty class. |
| S09-CAT3-003 | CAT-3 | MAJOR | `tests/unit/strategy/test_commands.py` | test_handle_command | Remove. |
| S10-CAT1-001 | CAT-1 | CRITICAL | `tests/unit/ui/test_sprites.py` | test_atlas_fallback_logic | Remove. |
| S10-CAT1-002 | CAT-1 | CRITICAL | `tests/integration/ui/build_queue_screen/test_crash_tooltips.py` | test_apply_tooltips_crash_none_buttons | Add an assertion verifying buttons are present and tooltips applied. |
| S10-CAT1-003 | CAT-1 | CRITICAL | `tests/unit/ui/screens/test_menu_scene.py` | test_button_config_with_3_buttons | Delete the duplicate. |
| S11-CAT1-001 | CAT-1 | CRITICAL | `tests/unit/ui/test_race_summary_panel.py` | test_race_summary_panel_stores_race_config | Remove. Replace with construction-path test. |
| S11-CAT1-002 | CAT-1 | CRITICAL | `tests/unit/ui/test_race_summary_panel.py` | test_on_load_race_callback_stored / test_has_load_button_reference | Remove. |
| S11-CAT1-003 | CAT-1 | MINOR | `tests/unit/ui/test_race_summary_panel.py` | Feat12 button callback storage tests | Remove. |
| S11-CAT1-004 | CAT-1 | MINOR | `tests/unit/ui/screens/test_strategy_screen.py` | No session/turn_engine/galaxy property tests | Replace with a behavioral test of the protected protocol. |
| S11-CAT1-005 | CAT-1 | MINOR | `tests/unit/ui/screens/test_design_selector_window.py` | 5 init attribute tests | Remove or merge into a real-construction test. |
| S11-CAT2-001 | CAT-2 | CRITICAL | `tests/unit/qa/test_testruncard_propulsion.py` | Entire file | Delete entire file. |
| S11-CAT2-002 | CAT-2 | MAJOR | `tests/unit/ai/interfaces/test_controllable_adapter.py` | ABC interface tests + 130-LOC mock classes | Keep ~20 LOC contract checks; delete the two 30-method mock classes. |
| S11-CAT2-003 | CAT-2 | MINOR | `tests/unit/strategy/test_commands.py` | test_command_name_property | Remove. |
| S12-CAT1-001 | CAT-1 | MINOR | `tests/unit/ui/screens/test_strategy_window_manager_public_api.py` | test_can_construct_with_input_mapper_and_asset_resolver | Keep as-is (documented contract guard). |
| S12-CAT1-002 | CAT-1 | MINOR | `tests/integration/test_main_integration.py` | test_import_main | Narrow except to ImportError; pytest.skip for non-import errors. |
| S12-CAT2-001 | CAT-2 | CRITICAL | `tests/unit/ui/screens/test_build_queue_screen.py` | Entire file uses bypass-init | Migrate to integration tests with headless pygame_gui setup; remove bypass-init unit tests. |
| S12-CAT2-002 | CAT-2 | MAJOR | `tests/unit/ui/screens/test_strategy_window_manager_public_api.py` | TestModalSlotCleanupContract | Replace source-inspection with behavioral assertion; keep the _on_closed slot-clearing test. |
| S12-CAT2-003 | CAT-2 | MAJOR | `tests/unit/ui/panels/test_ship_detail_panel.py` | Init/state tests use bypass | Remove tautological TestShipDetailPanelInit; for behavioral classes, switch to real construction with mocked deps. |

## Needs Rework

| id | original suggestion | Claude's adjusted suggestion | rationale |
|----|---------------------|------------------------------|-----------|
| S03-CAT2-002 | Test concrete production subclasses through the ABC interface, not local in-test stubs. | Add tests for concrete production subclasses (e.g., FleetReportDataSource) in addition to the ABC contract tests. | Severity adjusted CRITICAL → MAJOR; ABC contract tests provide value but concrete subclass coverage missing. |

## Rejected

| id | original claim | contrary evidence (file:line) | rationale |
|----|----------------|-------------------------------|-----------|
| S08-CAT2-R01 | Phase 1 claimed 'tests nothing real / no game.* imports' but the file imports real StrategySessionFacade from game.strategy.facade. | `tests/unit/strategy/facade/test_facade_indices.py` lines 12-74 | Imports real StrategySessionFacade; Phase 1 'No game.* imports' claim is factually false. |
| S08-CAT2-R02 | Phase 1 claimed all tests are mocked but every test imports real production SingleSelect/MultiSelect/NoSelect classes with zero mocking. | `tests/unit/ui/components/table/test_selection.py` lines 6-224 | Imports real production selection classes; tests exercise them directly. |
| S08-CAT2-R03 | Phase 1 claimed 'tests nothing real' but file imports real ShipControllableAdapter from game.ai.interfaces.controllable. | `tests/unit/ai/interfaces/test_controllable_adapter_edge_cases.py` lines 54-365 | Imports real ShipControllableAdapter; tests exercise adapter delegation through mocks. |

## Out of Scope

| id | claim | reason |
|----|-------|--------|
| S01-CAT2-OOS01 | AST static-analysis enforcement of architectural import constraints. | ast_guard_intentional |
| S01-CAT2-OOS02 | AST static-analysis guard for DI compliance (PROJ-300). | ast_guard_intentional |
| S05-CAT2-OOS01 | Intentional contract pin per PROJ-309 sub-phase 3.2; pins public symbols/methods using inspect.signature() and isinstance(getattr(...), property). | ast_guard_intentional |
