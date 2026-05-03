# PROJ-322 File Manifest

> Generated during /proj-start. Used by /proj-parallel for conflict detection.
> Updated if implementation discovers additional files.

## Files

| File | Type | Notes |
|------|------|-------|
| `tests/fixtures/ui_widget_factory.py` | Production | NEW shared `make_ui_widget(Cls, **kwargs)` factory used across APC-001 cleanup (Phase 5 Task 5.0) |
| `tests/fixtures/test_ui_widget_factory.py` | Test | NEW smoke test for the widget factory (Phase 5 Task 5.0) |
| `tests/fixtures/cargo_mock_ship.py` | Production | NEW shared `make_cargo_mock_ship` factory (Phase 6 Task 6.3 / DUP-003) |
| `tests/fixtures/test_entities.py` | Production | NEW shared mock-ship/fleet/empire/planet factories (Phase 6 Task 6.4 / HLP-001) |
| `tests/fixtures/yard_facility.py` | Production | NEW shared yard-facility factories (Phase 6 Task 6.6 / HLP-003) |
| `tests/fixtures/mock_planet.py` | Production | NEW shared `make_mock_planet` factory (Phase 6 Task 6.7 / HLP-004) |
| `tests/unit/simulation/conftest.py` | Test | UPDATED to host `_make_ship_spec`/`_make_team`/`ship_builder` (Phase 6 Task 6.5 / HLP-002) |
| `tests/integration/builder/test_builder_drag_drop_real.py` | Test | Boundary-patch `_create_ui` (Phase 3 Task 3.1, Phase 5 Task 5.34 / APC-003-F08) |
| `tests/integration/builder/test_builder_ui_sync.py` | Test | Module-scope `setup_ui` (Phase 2 Task 2.1) |
| `tests/integration/data/test_pipeline_unification.py` | Test | Document data-contract coupling (Phase 4 Task 4.1) |
| `tests/integration/test_app_integration.py` | Test | Replace 3 source-inspection tests with behavioural ones (Phase 5 Task 5.20 / APC-002-F04) |
| `tests/repro_issues/test_bug_11_dialog_size.py` | Test | Module-scope pygame display autouse (Phase 2 Task 2.2) |
| `tests/unit/ai/test_ai.py` | Test | Decouple attack-run test from approach_distance constant (Phase 3 Task 3.2) |
| `tests/unit/assets/test_component_derivatives.py` | Test | `os.utime` instead of `time.sleep` for mtime (Phase 4 Task 4.2) |
| `tests/unit/builder/test_multi_selection_logic.py` | Test | Convert autouse to value-returning fixtures (Phase 3 Task 3.3) |
| `tests/unit/builder/test_workshop_viewmodel.py` | Test | Memoize/module-scope registries (Phase 2 Task 2.3) |
| `tests/unit/core/test_pure_loaders.py` | Test | Rescope `reset_registry` autouse to module/session (Phase 2 Task 2.4) |
| `tests/unit/modifiers/test_beam_weapon_bindings.py` | Test | Merge into `test_weapon_ability_bindings.py` (Phase 1 Task 1.1) |
| `tests/unit/modifiers/test_seeker_multi_ability.py` | Test | Replace getsource pattern check (Phase 5 Task 5.17 / APC-002-F01) |
| `tests/unit/modifiers/test_seeker_weapon_bindings.py` | Test | Remove duplicated recalculate tests (Phase 1 Task 1.2); replace inline MockComponent (Phase 3 Task 3.4) |
| `tests/unit/modifiers/test_weapon_ability_bindings.py` | Test | Receives merged tests from `test_beam_weapon_bindings.py` (Phase 1 Task 1.1) |
| `tests/unit/modifiers/test_weapons_isolation.py` | Test | Anchor for consolidated seeker recalculate coverage (Phase 1 Task 1.2) |
| `tests/unit/research/research_scene/test_reset_state.py` | Test | Replace call-sequence asserts with state asserts (Phase 3 Task 3.5) |
| `tests/unit/research/test_research_scene_di.py` | Test | Remove camera-import source-text test (Phase 3 Task 3.6, Phase 5 Task 5.22 / APC-002-F06) |
| `tests/unit/simulation/combat/test_exit_policy.py` | Test | Share BattleEngine + boundary fixtures (Phase 2 Task 2.5) |
| `tests/unit/simulation/components/test_component_resource_manager.py` | Test | Rescope MagicMock-tree fixtures (Phase 2 Task 2.6) |
| `tests/unit/simulation/components/test_modifier_manager.py` | Test | Remove deprecated `TestModifierManagerStandalone` (Phase 1 Task 1.3) |
| `tests/unit/simulation/entities/test_ship.py` | Test | Keep entity-level derelict tests (Phase 1 Task 1.4) |
| `tests/unit/simulation/test_combat.py` | Test | Remove duplicated derelict coverage (Phase 1 Task 1.4) |
| `tests/unit/simulation/projectile/test_ccd.py` | Test | Extract `_make_projectile` helper (Phase 3 Task 3.7) |
| `tests/unit/simulation/services/test_modifier_service.py` | Test | Rescope `full_registry` to class scope (Phase 2 Task 2.7) |
| `tests/unit/simulation/services/test_validation_service.py` | Test | Replace mock-delegate tests with behavioural ones (Phase 3 Task 3.8) |
| `tests/unit/simulation/systems/test_battle_engine_init_ship.py` | Test | Drive battle-engine through public API (Phase 3 Task 3.9, Phase 5 Task 5.28 / APC-003-F02) |
| `tests/unit/simulation/test_battle_runner.py` | Test | Receives shared helpers from conftest (Phase 6 Task 6.5 / HLP-002) |
| `tests/unit/simulation/test_battle_runner_di.py` | Test | Move helpers to conftest (Phase 1 Task 1.5, Phase 6 Task 6.5 / HLP-002) |
| `tests/unit/services/llm/test_background.py` | Test | Replace polling sleeps with Event sync (Phase 4 Task 4.3) |
| `tests/unit/services/llm/test_decorators.py` | Test | Mock clock for duration assertion (Phase 4 Task 4.4) |
| `tests/unit/services/llm/test_persistence.py` | Test | Mock clock for both-bound assertion (Phase 4 Task 4.5) |
| `tests/unit/services/llm/test_race_description_llm_controller.py` | Test | Event/clock sync (Phase 4 Task 4.6) |
| `tests/unit/strategy/conflict_resolution/test_battle_resolver_integration.py` | Test | Public-API rewrite (Phase 1 Task 1.6, Phase 5 Task 5.31 / APC-003-F05) |
| `tests/unit/strategy/data/test_auto_save.py` | Test | `os.utime` instead of sleep (Phase 4 Task 4.7) |
| `tests/unit/strategy/data/test_battle_state_validation.py` | Test | Parametrize 6 deletion tests (Phase 1 Task 1.7) |
| `tests/unit/strategy/data/test_colony_species_config.py` | Test | KEEP edge-case tests, document (Phase 1 Task 1.8 / NEEDS_REWORK) |
| `tests/unit/strategy/data/test_construction_queue_paused_persistence.py` | Test | Parametrize Planet/Fleet variants (Phase 1 Task 1.9) |
| `tests/unit/strategy/data/test_event_validation.py` | Test | Parametrize 5 missing-key tests (Phase 1 Task 1.10) |
| `tests/unit/strategy/data/test_fleet_cargo_resources.py` | Test | Migrate to shared cargo factory (Phase 6 Task 6.3 / DUP-003, Phase 6 Task 6.4 / HLP-001) |
| `tests/unit/strategy/data/test_group_policies.py` | Test | Replace hardcoded lists with registry-driven test (Phase 1 Task 1.11) |
| `tests/unit/strategy/engine/test_build_order_command_handler.py` | Test | Use registry public API (Phase 1 Task 1.12, Phase 5 Task 5.32 / APC-003-F06) |
| `tests/unit/strategy/engine/test_build_order_processor.py` | Test | Refactor or document entry point (Phase 3 Task 3.10 / NEEDS_REWORK) |
| `tests/unit/strategy/engine/test_planetary_yard_requirement.py` | Test | Migrate to shared yard factory (Phase 6 Task 6.6 / HLP-003) |
| `tests/unit/strategy/engine/test_resupply_engine.py` | Test | Consolidate helpers (Phase 2 Task 2.8); migrate to shared factories (Phase 6 Tasks 6.3/6.4/6.7) |
| `tests/unit/strategy/engine/test_superweapon_command_handlers.py` | Test | Parametrize fleet-not-found (Phase 1 Task 1.13); shared factory (Phase 6 Task 6.1/6.2 / DUP-001/DUP-002) |
| `tests/unit/strategy/engine/test_superweapon_edge_cases.py` | Test | Parametrize + consolidate (Phase 1 Task 1.14) |
| `tests/unit/strategy/engine/test_superweapon_handler_validation.py` | Test | Parameterized fixture factory (Phase 6 Task 6.1 / DUP-001) |
| `tests/unit/strategy/engine/test_superweapon_stabilizers.py` | Test | Accept positional-or-keyword in assertion (Phase 3 Task 3.11) |
| `tests/unit/strategy/facade/test_strategy_session_facade.py` | Test | Shared mock-fleet/empire factories (Phase 2 Task 2.9, Phase 6 Task 6.4 / HLP-001) |
| `tests/unit/strategy/fleet/test_space_yard.py` | Test | Module-level `make_ship_with_yard` (Phase 1 Task 1.15, Phase 6 Task 6.6 / HLP-003) |
| `tests/unit/strategy/fleet_movement_engine/test_basics.py` | Test | Inject path-finder via DI (Phase 3 Task 3.12, Phase 5 Task 5.33 / APC-003-F07) |
| `tests/unit/strategy/fleet_navigation/test_projection.py` | Test | Anchor for projection happy-path (Phase 1 Task 1.16) |
| `tests/unit/strategy/fleet_navigation/test_service_edge_cases.py` | Test | Document overlap (Phase 1 Task 1.16) |
| `tests/unit/strategy/generation/test_astrophysics.py` | Test | Module-scope loader fixture (Phase 2 Task 2.10) |
| `tests/unit/strategy/production_engine/test_tick_consumption.py` | Test | Migrate to shared yard factory (Phase 6 Task 6.6 / HLP-003) |
| `tests/unit/strategy/services/test_fleet_navigation_mutual_pursuit.py` | Test | Replace signature default check (Phase 5 Task 5.18 / APC-002-F02) |
| `tests/unit/strategy/services/test_fleet_navigation_no_mock_hack.py` | Test | Replace 3 source-inspection tests (Phase 5 Task 5.19 / APC-002-F03) |
| `tests/unit/strategy/test_command_handlers.py` | Test | Parametrize fleet-not-found (Phase 6 Task 6.2 / DUP-002) |
| `tests/unit/strategy/test_planet_specific_colonization.py` | Test | Migrate to shared planet factory (Phase 6 Task 6.7 / HLP-004) |
| `tests/unit/strategy/turn_engine/test_tick_mechanics.py` | Test | Inject fake movement_engine (Phase 3 Task 3.13, Phase 5 Task 5.30 / APC-003-F04) |
| `tests/unit/strategy/validation/test_colonize_validator.py` | Test | Migrate to shared planet factory (Phase 6 Task 6.7 / HLP-004) |
| `tests/unit/ui/components/table/test_virtual_table.py` | Test | Module-scoped autouse for pygame_gui patches (Phase 3 Task 3.14) |
| `tests/unit/ui/panels/test_component_modifier_grid_panel.py` | Test | APC-001 widget-factory migration (Phase 5 Task 5.4 / APC-001-F04) |
| `tests/unit/ui/panels/test_design_report_panel.py` | Test | APC-001 widget-factory migration (Phase 5 Task 5.9 / APC-001-F09) |
| `tests/unit/ui/panels/test_empire_treasury_panel.py` | Test | Module-scope fixtures (Phase 2 Task 2.11 / NEEDS_REWORK); public-refresh asserts (Phase 3 Task 3.15) |
| `tests/unit/ui/panels/test_modifier_editor_panel.py` | Test | Rescope fixture / collapse tests (Phase 2 Task 2.12) |
| `tests/unit/ui/panels/test_race_identity_panel.py` | Test | APC-001 widget-factory migration (Phase 5 Task 5.3 / APC-001-F03) |
| `tests/unit/ui/panels/test_system_tree_panel.py` | Test | APC-001 widget-factory migration (Phase 5 Task 5.8 / APC-001-F08) |
| `tests/unit/ui/screens/battle_setup/test_fleet_hierarchy_editor.py` | Test | Assert cloned ship attributes (Phase 3 Task 3.16) |
| `tests/unit/ui/screens/battle_setup/test_renderer.py` | Test | Replace `getsource(_rebuild_ui)` (Phase 5 Task 5.23 / APC-002-F07) |
| `tests/unit/ui/screens/battle_setup/test_view_model.py` | Test | Remove no-pygame-imports runtime check (Phase 5 Task 5.21 / APC-002-F05) |
| `tests/unit/ui/screens/builder/test_modifier_logic_service.py` | Test | Public API (Phase 3 Task 3.17, Phase 5 Task 5.27 / APC-003-F01) |
| `tests/unit/ui/screens/test_battle_panels_extended.py` | Test | Extract shared setup_mocks (Phase 1 Task 1.17); targeted patch.object (Phase 3 Task 3.18) |
| `tests/unit/ui/screens/test_battle_setup_logic.py` | Test | Module-scope autouse (Phase 2 Task 2.13) |
| `tests/unit/ui/screens/test_build_queue_list_window.py` | Test | Boundary-patch (Phase 3 Task 3.19, Phase 5 Task 5.29 / APC-003-F03) |
| `tests/unit/ui/screens/test_build_queue_screen.py` | Test | Class-scoped fixture (Phase 2 Task 2.14); APC-001 widget-factory migration (Phase 5 Task 5.15 / APC-001-F15) |
| `tests/unit/ui/screens/test_fleet_report_filters.py` | Test | Extract make_mock_ship to shared (Phase 2 Task 2.15, Phase 6 Task 6.4 / HLP-001) |
| `tests/unit/ui/screens/test_fleet_report_window.py` | Test | APC-001 widget-factory migration (Phase 5 Task 5.6 / APC-001-F06) |
| `tests/unit/ui/screens/test_fleet_report_window_multi_select.py` | Test | Boundary patches + shared factory (Phase 3 Task 3.20, Phase 5 Task 5.7 / APC-001-F07) |
| `tests/unit/ui/screens/test_new_game_setup_extended.py` | Test | Real `__init__` construction (Phase 3 Task 3.21, Phase 5 Task 5.12 / APC-001-F12) |
| `tests/unit/ui/screens/test_planet_list_window.py` | Test | Note bypass-init convention (Phase 3 Task 3.22) |
| `tests/unit/ui/screens/test_planet_selection_window.py` | Test | Construction tests (Phase 5 Task 5.24 / APC-002-F08) |
| `tests/unit/ui/screens/test_queue_selector.py` | Test | Rescope build_queue_screen fixture (Phase 2 Task 2.16) |
| `tests/unit/ui/screens/test_race_setup_screen.py` | Test | Class-scoped or rebuild helper (Phase 2 Task 2.17, Phase 5 Task 5.11 / APC-001-F11) |
| `tests/unit/ui/screens/test_save_selection.py` | Test | Module-level setup_tmpdir (Phase 2 Task 2.18); real pygame_gui events (Phase 3 Task 3.23); deterministic timestamps (Phase 4 Task 4.8) |
| `tests/unit/ui/screens/test_strategy_input_handler_hotkeys.py` | Test | Receives merged warp-hotkey activation tests (Phase 1 Task 1.18) |
| `tests/unit/ui/screens/test_strategy_modal_window.py` | Test | Real headless pygame_gui session (Phase 3 Task 3.24) |
| `tests/unit/ui/screens/test_strategy_screen.py` | Test | Test public surface (Phase 3 Task 3.25) |
| `tests/unit/ui/screens/test_strategy_window_manager_public_api.py` | Test | Behavioural registrar assertion (Phase 5 Task 5.26 / APC-002-F10) |
| `tests/unit/ui/screens/test_sub_window_hotkeys.py` | Test | Real construction (Phase 3 Task 3.26, Phase 5 Task 5.16 / APC-001-F16) |
| `tests/unit/ui/screens/test_warp_hotkey.py` | Test | Merge mode-activation into strategy-input-handler tests (Phase 1 Task 1.18) |
| `tests/unit/ui/screens/test_workshop_screen.py` | Test | APC-001 widget-factory migration (Phase 5 Task 5.10 / APC-001-F10) |
| `tests/unit/ui/services/test_ship_io.py` | Test | Rescope Ship fixtures (Phase 2 Task 2.19) |
| `tests/unit/ui/test_camera.py` | Test | Single module-scoped pygame.init fixture (Phase 2 Task 2.20) |
| `tests/unit/ui/test_new_game_setup.py` | Test | Behavioural default test (Phase 5 Task 5.25 / APC-002-F09) |
| `tests/unit/ui/test_race_description_panel.py` | Test | APC-001 widget-factory migration (Phase 5 Task 5.2 / APC-001-F02) |
| `tests/unit/ui/test_race_flag_gallery.py` | Test | APC-001 widget-factory migration (Phase 5 Task 5.5 / APC-001-F05) |
| `tests/unit/ui/test_race_portrait_gallery.py` | Test | APC-001 widget-factory migration (Phase 5 Task 5.1 / APC-001-F01) |
| `tests/unit/ui/test_race_summary_panel.py` | Test | APC-001 widget-factory migration (Phase 5 Task 5.14 / APC-001-F14) |
| `tests/unit/ui/test_race_theme_gallery.py` | Test | APC-001 widget-factory migration (Phase 5 Task 5.13 / APC-001-F13) |
