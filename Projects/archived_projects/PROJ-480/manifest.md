# PROJ-480 File Manifest

> Generated from `Reviews/results/2026-05-20_210550_test-review/` after independent verification.
> Every file appears in at least one `phase_N_checklist.md`; every checklist file appears here.
> Files marked _(coord)_ also appear in PROJ-478 or PROJ-479 plans — sequence work accordingly.

## Files

### Phase 1 — CAT-9 Simplification
| File | Type | Notes |
|------|------|-------|
| tests/unit/ui/screens/test_workshop_screen.py | Test | Subsumed by PROJ-478 Phase 2 _(coord)_ |
| tests/unit/ui/screens/test_system_selection_window.py | Test | Extract _make_system_selection_window helper |
| tests/unit/ui/screens/test_fleet_menu_items.py | Test | Extract local _make_* helpers (tied to HLP-004 _(coord)_) |
| tests/unit/strategy/test_physics_constants.py | Test | Parametrize 3 docstring-substring tests |
| tests/unit/ui/test_save_selection.py | Test | Single module autouse fixture (tied to HLP-005 _(coord)_) |
| tests/unit/core/test_hex_math_core.py | Test | Module-level import; remove 9 in-method imports |
| tests/unit/strategy/services/test_colonization_facade.py | Test | Module-level MockPlanetType (tied to HLP-002 _(coord)_) |
| tests/unit/strategy/engine/test_build_order_processor.py | Test | Use existing order_processor fixture |
| tests/unit/ui/screens/test_empire_build_queue_formatter.py | Test | Module-level imports |
| tests/unit/strategy/engine/test_engine_validation.py | Test | Parametrize 12 engine classes |
| tests/unit/ui/screens/test_strategy_input_handler_transfer.py | Test | Parametrize 3 mode-test classes |
| tests/unit/strategy/fleet_movement_engine/conftest.py | Test | Move mock_fleet to canonical conftest |
| tests/unit/ui/test_race_setup_screen.py | Test | Extract shared fixtures for inline mocks |
| tests/unit/ui/screens/test_strategy_menu_actions.py | Test | Convert _make_strategy_screen to fixture |
| tests/unit/simulation/combat/test_weapon_firing_system.py | Test | Create _make_ship_mock factory |
| tests/unit/ui/screens/test_transfer_dialog.py | Test | scope=module + MagicMock UIManager |
| tests/unit/ui/screens/test_cargo_quick_dialog.py | Test | scope=module + MagicMock UIManager |
| tests/unit/ui/utils/test_list_data_source_base.py | Test | Split multi-branch test |
| tests/unit/strategy/pathfinding/test_basic_paths.py | Test | Move find_path_* helpers to conftest |
| tests/unit/strategy/pathfinding/test_edge_cases.py | Test | Import find_path_* helpers from conftest |
| tests/unit/simulation/combat/test_damage_calculator.py | Test | Use mock_ship factory in later test classes |
| tests/unit/strategy/engine/test_harvesting_engine.py | Test | Remove 3 staticmethod _make_engine decls |
| tests/unit/strategy/engine/test_superweapons.py | Test | Normalize .items() vs .keys() parametrize |
| tests/unit/strategy/engine/test_planet_specific_colonization.py | Test | Remove duplicate 'colony_pod' dict keys |
| tests/unit/strategy/engine/test_action_execution_engine.py | Test | Parametrize on tick |

### Phase 2 — CAT-8 Needless Complexity
| File | Type | Notes |
|------|------|-------|
| tests/integration/resource_system/test_resource_pipeline.py | Test | Split 73-line monolithic test |
| tests/unit/ui/screens/test_build_queue_panel_factory.py | Test | Extract setup helper |
| tests/unit/ui/test_detail_panel_rendering.py | Test | Class-scoped pygame_gui fixture |
| tests/unit/ai/test_ai_controller_unit.py | Test | Extract patch helper; _make_ai_controller |
| tests/unit/ui/screens/test_event_log_window.py | Test | Convert _make_strategy_ui to fixture |
| tests/unit/ui/test_camera.py | Test | patch.multiple for 13 TestCameraUpdateInput methods |
| tests/unit/simulation/entities/test_ship_stats.py | Test | Compress 43-line setup to fixture |
| tests/unit/ui/screens/test_strategy_detail_formatter.py | Test | patch.multiple for 6-level nesting |
| tests/unit/ui/screens/battle_setup/test_view_model.py | Test | Module-level BattleSetupViewModel import |
| tests/unit/strategy/test_container.py | Test | Inline 5 trivial wrappers |
| tests/unit/strategy/engine/test_resupply_engine.py | Test | Move factories to engine/conftest.py _(coord)_ |
| tests/unit/ui/screens/test_new_game_setup_extended.py | Test | Single-fixture 7-layer mock |
| tests/unit/ui/screens/test_strategy_game_state_manager.py | Test | Merge _make_*_state_manager helpers |
| tests/unit/ui/test_modifier_impact_grid.py | Test | Extract pygame init fixture |
| tests/unit/ui/screens/test_fleet_report_filters.py | Test | Move make_mock_ship to fixtures/ship_mocks.py |
| tests/unit/ui/test_race_summary_panel.py | Test | Extract _refresh_with_mocked_uilabel _(coord with PROJ-479)_ |
| tests/repro_issues/test_bug_04_display.py | Test | Conftest fixture for 15-patch setup |
| tests/unit/ui/screens/test_design_selector_window.py | Test | Shared context-manager helper |
| tests/unit/ui/panels/test_empire_treasury_panel.py | Test | Class-scope 4-decorator stack (+ Phase 3 parametrize) |
| tests/unit/ui/screens/test_strategy_screen.py | Test | patch.multiple for 7-patch (also Phase 3 of PROJ-479) |
| tests/unit/ui/test_structure_visibility.py | Test | patch.multiple for 8-patch |
| tests/unit/strategy/services/test_fleet_navigation_action_timing.py | Test | Extract double-patch helper |
| tests/unit/ui/screens/test_strategy_screen_selection.py | Test | Extract patcher_selection fixture |
| tests/unit/strategy/data/test_tech_preset_loader.py | Test | Autouse fixture for TECH_PRESETS_DIR patch |
| tests/unit/ui/screens/test_build_queue_formatting.py | Test | Move MockSession to integration conftest |

### Phase 3 — CAT-10 Parametrize
| File | Type | Notes |
|------|------|-------|
| tests/unit/ui/screens/test_build_queue_helpers.py | Test | Parametrize 6+7 helper tests |
| tests/unit/ui/screens/test_fleet_report_window_multi_select.py | Test | Parametrize 3 null-guard tests |
| tests/regression/test_deprecated_code_removed.py | Test | Parametrize 4+4 hasattr guards |
| tests/unit/systems/test_event_bus.py | Test | Parametrize 3 ValidationException |
| tests/unit/strategy/test_engine_event_emission.py | Test | Parametrize 9 event-emission tests |
| tests/unit/strategy/data/test_squadron_characterization.py | Test | Parametrize 5 round-trip tests |
| tests/unit/simulation/entities/test_ship_physics.py | Test | Parametrize 4 angle tests |
| tests/unit/simulation/ship_combat_engine/test_cooldowns.py | Test | Parametrize 5 shield-regen tests |
| tests/unit/simulation/test_formula_exceptions.py | Test | Module-level FormulaEvaluator import |
| tests/unit/modifiers/test_invalid_operation_handling.py | Test | Parametrize 4 op-type tests |
| tests/unit/ui/screens/test_system_selection_window.py | Test | Parametrize 2 cancel/confirm |
| tests/unit/ui/screens/test_planet_menu_items.py | Test | Parametrize 5+ capability matrix tests |
| tests/unit/ui/screens/test_fleet_menu_items.py | Test | Parametrize 10+ FMS row tests |
| tests/unit/ui/screens/test_strategy_input_handler_core.py | Test | Parametrize 4 escape-mode tests |
| tests/unit/ui/screens/test_empire_build_queue_window.py | Test | Parametrize duplicate-name test |
| tests/unit/simulation/entities/test_ship_fleet_attrs.py | Test | Parametrize 2 attr pairs |
| tests/unit/strategy/fleet_navigation/test_destination_path.py | Test | NavigationState fixture |
| tests/unit/ui/screens/test_design_selector_window.py | Test | Extract _assert_design_row_with_id helper |
| tests/unit/ui/screens/test_strategy_input_handler_hotkeys.py | Test | 3 cluster parametrizations |
| tests/unit/ui/screens/test_planet_abilities_controller_scanner.py | Test | Parametrize 2 instance_label tests |
| tests/unit/ui/screens/test_setup_screen.py | Test | Parametrize 3 hasattr+callable tests |
| tests/unit/strategy/engine/test_production_engine_queue.py | Test | Parametrize 2 resources_consumed tests |
| tests/unit/strategy/engine/test_planet_energy_engine.py | Test | Parametrize 4 generator tests |
| tests/unit/ui/services/test_ship_io.py | Test | Parametrize IO-specific properties (after DUP-003 in PROJ-479) |
| tests/unit/strategy/facade/test_fleet_dto.py | Test | Merge 2 immutable-tuple tests |
| tests/unit/simulation/entities/test_ship_serialization.py | Test | Parametrize 5 roundtrip tests _(coord)_ |
| tests/unit/strategy/turn_engine/test_turn_engine_lazy_properties.py | Test | Parametrize 18 isinstance tests |
| tests/integration/strategy/test_deterministic_generation.py | Test | Parametrize 4 deterministic-gen tests |
| tests/unit/ui/screens/test_event_log_data_source.py | Test | Parametrize 4 category-icon tests |
| tests/unit/ui/utils/test_portraits.py | Test | Parametrize 4 get_ship_class_color tests |
| tests/unit/ui/screens/test_battle_results_screen.py | Test | Parametrize 6 _hp_color tests |
| tests/unit/strategy/services/test_fleet_pursuer_tracker.py | Test | Parametrize 3 setup-shared tests |
| tests/unit/ui/screens/test_battle_screen_simulation.py | Test | 3 cluster parametrizations |
| tests/unit/ui/screens/test_research_renderer.py | Test | 10+7 visibility/margin parametrizations |
| tests/unit/ui/screens/test_new_game_setup_controller.py | Test | Parametrize 2 callback tests |
| tests/unit/strategy/fleet/test_warp_resources.py | Test | Parametrize 3 warp_resource_costs |
| tests/unit/strategy/utility/test_naming.py | Test | Parametrize 16 to_roman tests |
| tests/unit/ui/screens/test_event_log_sidebar.py | Test | Parametrize 4 attr tests |
| tests/unit/strategy/engine/test_superweapon_order_processor_gaps.py | Test | Parametrize 5 TestStabilizerCancellation |
| tests/unit/simulation/systems/test_tick_phases.py | Test | Parametrize 3 registry-read tests |
| tests/unit/ui/panels/test_empire_treasury_panel.py | Test | Parametrize 4 _format_value tests |
| tests/unit/strategy/engine/test_superweapon_command_handlers.py | Test | Parametrize 5 handler-class tests |
| tests/unit/strategy/validation/test_superweapon_validator.py | Test | Parametrize 5 validator-class clusters |
| tests/unit/strategy/empire/test_empire_validation.py | Test | Parametrize 3 missing-field tests |
| tests/unit/strategy/engine/test_base_command_handler.py | Test | Parametrize 2 resolve_fleet tests |
| tests/unit/strategy/engine/test_superweapons.py | Test | Resolve .items() vs .keys() (Phase 1 Task 1.26) |

### Phase 4 — CAT-11 Fragile Assertion
| File | Type | Notes |
|------|------|-------|
| tests/unit/strategy/persistence/test_persistence_adapter.py | Test | Key-by-key dict validation |
| tests/unit/strategy/data/test_caption_schemas_validate.py | Test | issuperset() not exact set equality |
| tests/unit/strategy/engine/order_handlers/test_join_fleet_handler.py | Test | Contains-key assertion |
| tests/unit/ui/screens/test_design_selector_window.py | Test | call_args.kwargs not [1] |
| tests/unit/ui/panels/test_design_report_panel.py | Test | Named constant for width |
| tests/unit/ui/screens/test_workshop_event_router_select_component.py | Test | Property assertions |
| tests/unit/ui/screens/test_lab/test_test_run_card.py | Test | Regex / contains-key |
| tests/unit/ui/screens/builder/test_weapons_renderer.py | Test | Structural string asserts |
| tests/unit/ui/screens/strategy_windows/test_list_windows.py | Test | Named layout constants |
| tests/unit/strategy/engine/test_order_processor_colonize.py | Test | get() per-key asserts |
| tests/unit/regression/test_bug_regressions_2026_01.py | Test | Intermediate formula var |

### Phase 5 — CAT-12 Logic-Heavy
| File | Type | Notes |
|------|------|-------|
| tests/unit/builder/test_ship_loading.py | Test | Extract per-ship validation helper |
| tests/unit/strategy/services/test_empire_economy_caching.py | Test | Scenario fixture |
| tests/unit/ui/screens/test_build_queue_panel_factory.py | Test | Use Paths module not 5-deep dirname |
| tests/unit/simulation/systems/test_battle_engine_tick.py | Test | Parametrize counts + strict invariant |
| tests/unit/ui/test_new_game_setup.py | Test | all() generator expressions |
| tests/integration/ui/test_camera_zoom.py | Test | Pre-computed constants |
| tests/regression/test_generator_crew_requirement_design.py | Test | Remove defensive branches |
| tests/unit/strategy/planet_atmosphere/test_generation.py | Test | Seeded RNG deterministic assertion |
| tests/integration/research_workflow/test_workflow.py | Test | Seeded RNG; remove silent passes |
| tests/integration/gameplay_loop/test_commands_colonization.py | Test | Deterministic completion calc |
| tests/integration/test_complex_workflow.py | Test | Deterministic setup, no retry |
| tests/unit/strategy/engine/order_handlers/test_order_processor_facade.py | Test | Remove meta-test |
| tests/unit/ui/screens/battle_setup/test_spec_compiler.py | Test | Extract snapshot helper |
| tests/unit/strategy/formulas/test_colony_output.py | Test | Pre-computed expected value |
