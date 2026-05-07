# Verification Report — PROJ-323 (P2 tier)

- **Source review:** `Reviews/results/2026-05-02_204633_test-review/`
- **Run date:** 2026-05-03
- **Priority tier:** P2 (CAT-8, CAT-9, CAT-10, CAT-11, CAT-12)
- **Batch summary:** 156 verified, 3 needs-rework, 1 rejected, 6 out-of-scope.

## Verified

| id | category | severity | file | test_name | suggestion |
|----|----------|----------|------|-----------|------------|
| S01-CAT8-001 | CAT-8 | MAJOR | tests/unit/builder/test_builder_improvements.py | test_loading_sync | Extract mock-ship creation into a shared helper. Mock only attributes the SUT actually reads. |
| S01-CAT10-001 | CAT-10 | MINOR | tests/unit/strategy/facade/test_system_dto.py | DTO creation + frozen tests cluster | Consolidate into @pytest.mark.parametrize. |
| S01-CAT10-002 | CAT-10 | MINOR | tests/unit/strategy/data/test_design_metadata_validation.py | Missing-field defaults cluster | Parametrize: @pytest.mark.parametrize('key,default', [...]). |
| S01-CAT10-003 | CAT-10 | MINOR | tests/unit/strategy/planet/test_planet_validation.py | Negative-value validation tests split | Merge the two parametrize blocks or leave as-is. |
| S01-CAT11-001 | CAT-11 | MINOR | tests/unit/strategy/engine/test_colonize_mission_handler.py | make_component_registry duplicate key | Remove the duplicate 'colony_pod' entry (lines 113-117). |
| S02-CAT8-001 | CAT-8 | MAJOR | tests/unit/ai/test_ai_controller_unit.py | 5+ levels of patch nesting + nonlocal | Extract _build_behavior_context helper if promoted, or restructure controller for separable context construction. |
| S02-CAT8-002 | CAT-8 | MINOR | tests/unit/ai/test_ai_controller_unit.py | TestCheckAvoidance complex mock chain | Extract _setup_avoidance_test(threats, ship_pos, ship_radius) helper. |
| S02-CAT9-001 | CAT-9 | MINOR | tests/unit/strategy/test_fleet_speed_calculator.py | Repeated mock construction across 7 tests | Extract _make_mock_ship_with_stats(mass, speed) helper. |
| S02-CAT9-002 | CAT-9 | MINOR | tests/unit/strategy/services/ability_sources/test_system_archetype.py | Repeated _MockSystem | Create @pytest.fixture for _MockSystem and parametrize archetype/abilities. |
| S02-CAT10-001 | CAT-10 | MINOR | tests/unit/strategy/test_fleet_speed_calculator.py | 7 calculate_ship_speed tests | Parametrize to one @pytest.mark.parametrize test. |
| S02-CAT10-002 | CAT-10 | MINOR | tests/unit/strategy/services/test_modifier_resolver.py | 7 resolve_size_multiplier tests | Parametrize. |
| S02-CAT10-003 | CAT-10 | MINOR | tests/unit/ui/screens/test_planet_data_source.py | Attr-value extraction tests | Parametrize to single test. |
| S02-CAT11-001 | CAT-11 | MINOR | tests/regression/test_deprecated_code_removed.py | EXPECTED_GAME_COUNT magic numbers | Remove the count-based tests or make them advisory-only. The hasattr checks already guard against reintroduced code. |
| S02-CAT12-001 | CAT-12 | MINOR | tests/integration/ui/test_race_setup_ships_smoke.py | test_every_portrait_is_2048x2048_or_in_allowlist | Split into two tests: allowlisted gaps and target-sized portraits. |
| S02-CAT12-002 | CAT-12 | MINOR | tests/integration/fleet_combat/test_combat_resource_consumption.py | Logic-heavy fuel/ammo tests | Extract resource consumption loop into helper. Test at ResourceState level directly; keep one integration scenario. |
| S03-CAT8-001 | CAT-8 | MAJOR | tests/unit/ui/screens/test_fleet_report_window.py | _make_fleet_report_window helper | Construct via real __init__ with mocked pygame_gui. |
| S03-CAT8-002 | CAT-8 | MAJOR | tests/unit/research/research_scene/test_callbacks.py | 5-7 nested patch blocks | Promote shared patches to class-level autouse fixture. |
| S03-CAT8-003 | CAT-8 | MAJOR | tests/unit/research/research_scene/test_initialization.py | 5-6 nested patch blocks | Promote shared patches to class-level fixture. |
| S03-CAT9-001 | CAT-9 | MINOR | tests/unit/ui/panels/test_race_identity_panel.py | Repeated bypass-init pattern | Extract bypass-init into helper or move imports to module scope. |
| S03-CAT9-002 | CAT-9 | MINOR | tests/unit/ui/panels/test_component_modifier_grid_panel.py | Repeated bypass-init pattern | Extract helper. |
| S03-CAT9-003 | CAT-9 | MINOR | tests/unit/ui/test_race_flag_gallery.py | Repeated bypass-init pattern | Extract helper. |
| S03-CAT9-004 | CAT-9 | MINOR | tests/unit/research/research_scene/test_callbacks.py | Identical mock setup repeated | Extract a shared fixture. |
| S03-CAT9-005 | CAT-9 | MINOR | tests/unit/research/research_scene/test_initialization.py | Identical mock setup across 7 tests | Extract a shared fixture. |
| S03-CAT9-006 | CAT-9 | MINOR | tests/unit/research/research_scene/test_cycle_detection.py | Repeated cycle-node structure | Extract helper for cycle setup. |
| S03-CAT10-001 | CAT-10 | MAJOR | tests/unit/strategy/engine/test_superweapon_command_handlers.py | Identical 3-test pattern across 6 handler classes | Parametrize across handlers. |
| S03-CAT12-001 | CAT-12 | MAJOR | tests/unit/ui/screens/test_planet_list_components.py | test_applies_owner_filters_updates_buttons | Assert observable end state instead of mock call patterns. |
| S03-CAT12-001b | CAT-12 | MINOR | tests/unit/services/llm/test_persistence.py | test_timing_is_reasonably_accurate (CAT-12 lens) | Use a mocked clock and assert directly on timer accuracy. |
| S04-CAT8-001 | CAT-8 | MINOR | tests/unit/strategy/test_engine_event_emission.py | Triple-nested with patch | Extract a class fixture or use patch.multiple to flatten. |
| S04-CAT8-002 | CAT-8 | MINOR | tests/unit/research/research_scene/test_interaction.py | Every test patches 6 classes | Promote shared patches to a class autouse fixture. |
| S04-CAT9-001 | CAT-9 | MINOR | tests/unit/strategy/test_engine_event_emission.py | 3 module helpers encode internals | Convert to fixtures that minimize implementation coupling. |
| S04-CAT9-002 | CAT-9 | MINOR | tests/unit/strategy/engine/test_harvesting_engine.py | _make_engine duplicated in 3 classes | Promote to module-level fixture. |
| S04-CAT9-003 | CAT-9 | MINOR | tests/unit/strategy/engine/test_empire_economy_calculator.py | _mock_race_registry duplicated | Promote to module-level fixture. |
| S04-CAT9-004 | CAT-9 | MINOR | tests/unit/ui/panels/test_system_tree_panel.py | 30+ __init__ patches duplicated | Address by switching to real construction; this duplication becomes moot. |
| S04-CAT10-001 | CAT-10 | MINOR | tests/unit/simulation/components/abilities/test_static_value_ability.py | positive/negative format pair | Parametrize. |
| S04-CAT12-001 | CAT-12 | MINOR | tests/unit/ui/test_race_browser_dialog.py | test_filter_races_by_name_returns_matches | Remove the else branch or guarantee _filter_races presence with @pytest.mark.skipif. |
| S04-CAT12-002 | CAT-12 | MINOR | tests/integration/gameplay_loop/test_turn_execution.py | 3 turn-execution tests with logic | Extract scenario helpers; keep at most one integration test per scenario. |
| S04-CAT12-003 | CAT-12 | MINOR | tests/integration/strategy/test_planet_physics.py | Conditional physics assertions | Split into two tests; remove conditional assertions. |
| S05-CAT8-001 | CAT-8 | MINOR | tests/unit/ui/test_detail_panel_rendering.py | Module cache deletion + 7 patches | Stop manipulating sys.modules; use a class autouse fixture for the patches. |
| S05-CAT9-001 | CAT-9 | MINOR | tests/unit/strategy/validation/test_colonize_validator.py | Repeated _make_planet helpers | Move to a module fixture with kwargs overrides. |
| S05-CAT9-002 | CAT-9 | MINOR | tests/unit/ui/utils/test_portraits.py | 7 method-level imports | Move imports to module top-level. |
| S05-CAT9-003 | CAT-9 | MINOR | tests/unit/ui/screens/test_build_queue_list_window.py | Redundant @patch decorators | Remove redundant decorators; rely on the fixture's existing patch. |
| S05-CAT10-001 | CAT-10 | MINOR | tests/unit/simulation/systems/test_battle_end_conditions.py | 3 duplicate parametrize blocks | Collapse into a single parametrized class. |
| S05-CAT10-002 | CAT-10 | MINOR | tests/unit/core/test_config_edge_cases.py | Boundary-value test classes | Parametrize with (attr_name, predicate) pairs. |
| S05-CAT10-003 | CAT-10 | MINOR | tests/unit/simulation/components/abilities/test_defense_isolation.py | 10 paired Attack/Defense tests | Parametrize across classes/modifiers. |
| S05-CAT10-004 | CAT-10 | MINOR | tests/unit/simulation/components/abilities/test_resource_consumption.py | 3 nearly-identical resource tests | Parametrize. |
| S05-CAT11-001 | CAT-11 | MINOR | tests/unit/ui/screens/test_empire_build_queue_window.py | Hardcoded 18-column set | Replace with a behavioral assertion on column purpose, not literal IDs. |
| S05-CAT12-001 | CAT-12 | MINOR | tests/unit/ai/test_advanced_behaviors.py | Vector arithmetic in test bodies | Acceptable for spatial behavior tests; document expected geometry in fixtures. |
| S06-CAT8-001 | CAT-8 | CRITICAL | tests/unit/ui/panels/test_design_report_panel.py | All tests bypass constructor | Construct via real __init__ with mocked pygame_gui. |
| S06-CAT8-002 | CAT-8 | CRITICAL | tests/unit/ui/screens/test_workshop_screen.py | All tests bypass constructor | Construct via real __init__ with mocked pygame_gui or migrate to integration tests. |
| S06-CAT8-003 | CAT-8 | MINOR | tests/unit/ui/screens/test_strategy_renderer.py | test_star_radius_nonlinear_scaling | Promote _hex_radius_to_screen to public helper or test through public draw assertions. |
| S06-CAT9-001 | CAT-9 | MINOR | tests/unit/ui/screens/test_fleet_data_source.py | Repeated view_model creation | Extract a fixture/factory. |
| S06-CAT9-002 | CAT-9 | MINOR | tests/unit/strategy/data/test_fleet_cargo_resources.py | _make_ship duplicates _make_cargo_ship | Extract to shared fixture. |
| S06-CAT9-003 | CAT-9 | MINOR | tests/unit/ui/components/filters/test_tri_state_widget.py | Repeated UIButton/UILabel patches | Move shared patches to class level. |
| S06-CAT10-002 | CAT-10 | MINOR | tests/unit/strategy/data/test_population_model.py | 2 max-population tests | Parametrize. |
| S06-CAT10-003 | CAT-10 | MINOR | tests/unit/ui/screens/test_fleet_data_source.py | 6 yes/no special-capability tests | Parametrize across (capability, return, expected) tuples. |
| S06-CAT10-004 | CAT-10 | MINOR | tests/unit/modifiers/test_defense_marker_bindings.py | 6 empty-bindings tests | Parametrize into a single test. |
| S06-CAT11-001 | CAT-11 | MINOR | tests/unit/core/test_combat_types.py | test_slots | Remove or merge. |
| S06-CAT12-001 | CAT-12 | MINOR | tests/unit/ui/screens/test_strategy_game_state_manager.py | test_stops_on_cancel_after_current_turn | Use side_effect that increments a Counter; assert outcome rather than internal call counts. |
| S06-CAT12-002 | CAT-12 | MINOR | tests/unit/ui/screens/test_strategy_game_state_manager.py | test_suppresses_event_log_during_loop_and_surfaces_combined_at_end | Compare sets or sequences with explicit equality. |
| S06-CAT12-003 | CAT-12 | MINOR | tests/unit/strategy/formulas/test_colony_output.py | test_partial_food_and_low_happiness_matches_hand_computation | Use hardcoded expected; provide a comment with derivation, not arithmetic. |
| S06-CAT12-004 | CAT-12 | MINOR | tests/integration/strategy/test_galaxy_gen.py | test_graph_connectivity | Extract BFS into a tests/helpers utility. |
| S06-CAT12-005 | CAT-12 | MINOR | tests/integration/research_workflow/test_workflow.py | test_multiple_turns_lead_to_breakthrough | Acceptable for stochastic process; consider seeding RNG. |
| S06-CAT12-006 | CAT-12 | MINOR | tests/integration/strategy/test_fleet_navigation_consistency.py | test_multi_turn_consistency | Extract grouping into helper. |
| S07-CAT8-001 | CAT-8 | MINOR | tests/unit/ui/screens/test_strategy_detail_formatter.py | 6 nested patch blocks | Use patch.multiple or a single context manager helper. |
| S07-CAT10-001 | CAT-10 | MAJOR | tests/unit/strategy/engine/test_superweapon_handler_validation.py | 5 near-identical direct-handler test classes | Parametrize across handlers. |
| S07-CAT10-002 | CAT-10 | MAJOR | tests/unit/strategy/engine/test_superweapon_handler_validation.py | 5 near-identical mission-handler test classes | Parametrize across mission handlers. |
| S07-CAT10-003 | CAT-10 | MINOR | tests/unit/strategy/data/test_ship_serialization.py | 6 round-trip attribute tests | Parametrize across attributes. |
| S07-CAT10-004 | CAT-10 | MINOR | tests/unit/ui/screens/test_superweapon_input_modes.py | Mode-setting and click-routing clusters | Parametrize each cluster. |
| S07-CAT10-005 | CAT-10 | MINOR | tests/unit/strategy/test_fleet_consumable_aggregator.py | True/False variant pairs | Parametrize. |
| S07-CAT10-006 | CAT-10 | MINOR | tests/unit/simulation/replay/test_battle_state_serialization.py | 19 field comparisons in round-trip | Replace with a helper iterating over field tuples. |
| S07-CAT11-001 | CAT-11 | MINOR | tests/unit/ui/screens/battle_setup/test_renderer.py | test_renderer_is_stateless_between_calls | Replace with behavioral assertion on stateless behavior. |
| S07-CAT11-002 | CAT-11 | MINOR | tests/unit/ui/test_unified_entry_guard.py | test_whitelist_size_locked | Keep as gate but use a constant defined alongside the whitelist. |
| S08-CAT8-001 | CAT-8 | MINOR | tests/unit/ui/screens/test_setup_screen.py | 3 setup_mocks fixtures | Promote to a single shared module-scoped fixture. |
| S08-CAT8-002 | CAT-8 | MINOR | tests/unit/ui/screens/test_cargo_quick_dialog_resolution.py | Live pygame.Rect + side_effect lambdas | Replace lambda chains with a fake mapper class. |
| S08-CAT8-003 | CAT-8 | MINOR | tests/unit/ui/panels/test_colony_demographic_view.py | _facade_for helper | Construct facade via real init with mocked dependencies; avoid attribute patching. |
| S08-CAT9-001 | CAT-9 | MINOR | tests/unit/ui/components/table/test_selection.py | Delayed imports per test method | Move imports to module top-level. |
| S08-CAT9-002 | CAT-9 | MINOR | tests/unit/simulation/systems/test_battle_engine_end_conditions.py | Near-identical mock_ship/mock_ship_team1 | Parametrize fixture. |
| S08-CAT9-003 | CAT-9 | MINOR | tests/unit/strategy/engine/test_organics_consumption_engine.py | _colony helper | Promote to class-scoped fixture. |
| S08-CAT10-001 | CAT-10 | MINOR | tests/unit/ui/panels/test_strategy_menu_panel.py | 6 button-callback tests | Parametrize. |
| S08-CAT10-002 | CAT-10 | MINOR | tests/unit/ui/screens/test_fleet_report_filters.py | TestSpecialCapabilityFilter (7 tests) | Parametrize across (ability, filter_key, expected) tuples. |
| S08-CAT10-003 | CAT-10 | MINOR | tests/unit/ui/screens/test_fleet_report_filters.py | TestFilterShipsSpaceyard | Parametrize. |
| S08-CAT10-004 | CAT-10 | MINOR | tests/unit/ui/screens/test_fleet_report_filters.py | TestFilterShipsCargo | Parametrize. |
| S08-CAT10-005 | CAT-10 | MINOR | tests/unit/strategy/data/test_battle_state_validation.py | Component + ShipState validation tests | Parametrize each cluster. |
| S08-CAT10-006 | CAT-10 | MINOR | tests/unit/simulation/systems/test_battle_engine_end_conditions.py | TestEscapeBasedMode 7 tests | Optional parametrization of common setup. |
| S08-CAT11-001 | CAT-11 | MINOR | tests/unit/strategy/data/test_event_validation.py | Exact event_type/message strings | Assert structural shape and field types instead of exact strings. |
| S08-CAT11-002 | CAT-11 | MINOR | tests/unit/strategy/data/test_battle_state_validation.py | Substring matching on exception messages | Assert exception type and structured field; not message text. |
| S08-CAT11-003 | CAT-11 | MINOR | tests/unit/strategy/data/test_superweapon_orders.py | Exact dict-structure assertions | Assert structural invariants; consider schema validation. |
| S08-CAT11-004 | CAT-11 | MINOR | tests/unit/strategy/facade/test_facade_dispatch.py | DISPATCH_CASES with 31 hardcoded entries | Generate from dispatch registry rather than hardcode names. |
| S08-CAT11-005 | CAT-11 | MINOR | tests/unit/ui/panels/test_strategy_menu_panel.py | Exact menu label/option-id assertions | Assert membership/structure rather than exact ordering. |
| S08-CAT12-001 | CAT-12 | MINOR | tests/unit/strategy/engine/test_resupply_engine.py | test_fuel_distributed_to_equalize_range | Use hardcoded expected with derivation comment. |
| S08-CAT12-002 | CAT-12 | MINOR | tests/unit/ui/screens/test_fleet_report_filters.py | TestCalculateFleetStats 9 tests | Hardcode expected values. |
| S08-CAT12-003 | CAT-12 | MINOR | tests/integration/strategy/test_habitability_on_economy.py | test_production_habitability_scales_drain | Test through public turn engine; use seeded fixtures. |
| S08-CAT12-004 | CAT-12 | MINOR | tests/unit/strategy/test_warp_logic_rework.py | test_angle_clearance_calculation | Promote _is_angle_clear to a public helper or test through public warp generation. |
| S08-CAT12-005 | CAT-12 | MINOR | tests/unit/strategy/test_happiness_engine.py | test_ideal_planet_food_ratio_one_base_half | Use hardcoded expected with derivation comment. |
| S09-CAT8-001 | CAT-8 | MINOR | tests/unit/simulation/test_battle_runner_di.py | test_no_simulation_call_to_get_default_registry_provider | Move to a pre-commit hook or CI check. |
| S09-CAT9-001 | CAT-9 | MINOR | tests/unit/strategy/test_quickstart_builder.py | Repeated spawn_initial_complexes setup | Extract a fixture and parametrize. |
| S09-CAT9-002 | CAT-9 | MINOR | tests/unit/core/test_protocols.py | Repeated local imports | Move imports to module top-level. |
| S09-CAT9-003 | CAT-9 | MINOR | tests/unit/ui/utils/test_formatters.py | 12 method-level imports | Hoist the import to module scope. |
| S09-CAT9-005 | CAT-9 | MINOR | tests/unit/ui/screens/builder/test_modifier_logic_smart_floor.py | Weak assertion | Tighten to `result == pytest.approx(0.1, abs=0.01)`. |
| S09-CAT10-001 | CAT-10 | MINOR | tests/unit/core/test_protocols.py | TypeGuard parametrize opportunity | Parametrize. |
| S09-CAT10-002 | CAT-10 | MINOR | tests/unit/strategy/data/test_loading.py | TestEdgeCases | Parametrize across (json_content, expected_ids). |
| S09-CAT10-003 | CAT-10 | MINOR | tests/unit/research/test_tech_node.py | TestTechNodePriceCurves | Parametrize across price_curve. |
| S09-CAT10-004 | CAT-10 | MINOR | tests/unit/strategy/test_engine_validation.py | 9+ engine validation classes | Collapse into one parametrized class with (engine_cls, valid_empire_kwargs, invalid_field_path). |
| S09-CAT10-005 | CAT-10 | MINOR | tests/unit/simulation/test_battle_runner.py | 5 module-level smoke tests | Extract _run_minimal_battle helper and parametrize. |
| S09-CAT11-001 | CAT-11 | MINOR | tests/unit/ui/test_new_game_setup.py | test_build_game_config_signature_default_matches_dataclass | Replace with a behavioral default-construction test. |
| S10-CAT9-001 | CAT-9 | MINOR | tests/unit/modifiers/test_projectile_weapon_bindings.py | Repeated imports | Hoist imports; consider merging tests. |
| S10-CAT9-002 | CAT-9 | MINOR | tests/unit/simulation/combat/test_fleet_aura_manager_modifier_stack.py | 4 similar helper functions | Consolidate into one parametrized factory; ~15 LOC savings. |
| S10-CAT9-003 | CAT-9 | MINOR | tests/unit/core/test_json_utils.py | TestLoadJsonRequired success path | Remove the success-path duplicate; keep error-path tests in TestLoadJsonRequired. |
| S10-CAT9-004 | CAT-9 | MINOR | tests/unit/strategy/fleet_navigation/test_service_edge_cases.py | Repeated mock fleet boilerplate | Extract _make_mock_fleet helper. |
| S10-CAT10-001 | CAT-10 | MINOR | tests/integration/strategy/turn_engine/test_resources.py | Full-turn duplicate setup | Extract setup helper; keep both tests for distinct properties. |
| S10-CAT10-002 | CAT-10 | MINOR | tests/unit/strategy/engine/test_planet_action_engine.py | 3 event-logging tests | Optional parametrization preserving descriptive names. |
| S10-CAT10-003 | CAT-10 | MINOR | tests/unit/simulation/services/test_modifier_service.py | 5+5 turret_mount duplicate tests | Parametrize the resolution logic; test both APIs against the same matrix. |
| S10-CAT10-004 | CAT-10 | MINOR | tests/unit/ui/screens/test_strategy_superweapons.py | 6 repeated no_fleet_returns_none tests | Parametrize with handler tuples. |
| S10-CAT10-005 | CAT-10 | MINOR | tests/unit/ui/screens/test_strategy_superweapons.py | 5 (of 6) fleet_without_ability tests | Parametrize the 5 identical tests; keep SelfDestruct separate. |
| S10-CAT10-006 | CAT-10 | MINOR | tests/unit/simulation/components/abilities/test_system_stabilizers.py | Stellar/Warp Stabilizer near-identical classes | Single parametrized class with (AbilityClass, expected_drain, activation, deactivation) tuples. |
| S10-CAT8-001 | CAT-8 | MAJOR | tests/unit/ai/test_combat_utils.py | _create_pdc_ship lambda hybrid | Use patch.object or real objects. |
| S10-CAT12-001 | CAT-12 | MINOR | tests/unit/simulation/test_physics_formulas.py | Inline physics formulas in boundary tests | Use shared compute helpers; keep boundary edge case wrappers minimal. |
| S10-CAT12-002 | CAT-12 | MINOR | tests/unit/strategy/data/test_planet_gen.py | Statistical sampling assertions | Replace with seeded RNG and exact assertions. |
| S11-CAT8-001 | CAT-8 | MINOR | tests/unit/ui/test_race_summary_panel.py | _refresh_with_mocked_uilabel | Convert to real construction or a class-scoped fixture. |
| S11-CAT8-002 | CAT-8 | MINOR | tests/unit/ui/components/table/test_virtual_table.py | Repetitive mock setup | Extract _build_virtual_table fixture. |
| S11-CAT8-003 | CAT-8 | MINOR | tests/unit/simulation/services/test_ship_stats_calculator_phases.py | _create_mock_ship 45 LOC | Use real Ship with sparse fixtures or simplify to dependency-injected ship. |
| S11-CAT8-004 | CAT-8 | MINOR | tests/unit/ui/screens/builder/test_modifier_control_row.py | 2 near-identical fixtures | Promote to module-level fixture. |
| S11-CAT8-005 | CAT-8 | MINOR | tests/integration/strategy/test_flat_shield_bonus.py | Deep helper nesting | Inline simpler helpers; flatten composition. |
| S11-CAT8-006 | CAT-8 | MINOR | tests/integration/conflict_resolution/test_three_empire_battle.py | test_three_empire_battle_reports_destroyed_fleets setup | Extract _three_empire_setup helper. |
| S11-CAT8-007 | CAT-8 | MINOR | tests/unit/strategy/test_planet_specific_colonization.py | 4 galaxy fixtures | Single factory _make_galaxy(*planet_specs). |
| S11-CAT8-008 | CAT-8 | MINOR | tests/unit/simulation/combat/test_fleet_aura_extended.py | _make_modifier_stack helper | Inline or simplify the factory. |
| S11-CAT8-009 | CAT-8 | MINOR | tests/unit/qa/test_caption_schemas_validate.py | Hardcoded schema list | Auto-discover *.schema.json in schemas dir. |
| S11-CAT8-010 | CAT-8 | MINOR | tests/unit/ui/components/table/test_virtual_table.py | test_update_visible_rows_disables_edge_action_buttons | Split into multiple smaller tests with explicit scroll positions. |
| S11-CAT8-011 | CAT-8 | MINOR | tests/unit/strategy/test_damage_calculator.py | Granular boundary test class | Same as F-10; keep distinct edge cases as-is. |
| S11-CAT9-001 | CAT-9 | MINOR | tests/unit/strategy/engine/test_planetary_yard_requirement.py | _make_yard_facility duplicates helper | Move to shared fixture. |
| S11-CAT10-001 | CAT-10 | MINOR | tests/unit/qa/test_testruncard_propulsion.py | 4 format-string tests | Parametrize. |
| S11-CAT10-003 | CAT-10 | MINOR | tests/unit/ui/screens/test_battle_panels_extended.py | expand/collapse toggle tests | Parametrize. |
| S11-CAT10-004 | CAT-10 | MINOR | tests/unit/strategy/test_colonization_facade.py | Success/failure duplicate patterns | Parametrize. |
| S11-CAT10-005 | CAT-10 | MINOR | tests/unit/strategy/test_colonization_facade.py | Pod-filtering tests | Parametrize. |
| S11-CAT10-006 | CAT-10 | MINOR | tests/unit/ui/utils/test_color_helpers.py | 5 get_hp_bar_color tests | Parametrize. |
| S11-CAT10-007 | CAT-10 | MINOR | tests/unit/ui/utils/test_color_helpers.py | 5 get_component_status_display tests | Parametrize. |
| S11-CAT10-008 | CAT-10 | MINOR | tests/unit/ui/utils/test_draw_helpers.py | 5 draw_stat_bar tests | Parametrize. |
| S11-CAT10-009 | CAT-10 | MINOR | tests/unit/ui/utils/test_resource_constants.py | ResourceColors/RESOURCE_ORDER_PRIORITY tests | Keep as-is. |
| S11-CAT10-010 | CAT-10 | MINOR | tests/unit/strategy/test_commands.py | Command property tests | Parametrize across (Command, kwargs, expected_type). |
| S11-CAT10-011 | CAT-10 | MINOR | tests/unit/strategy/test_resource_transfer.py | _execute_fleet_transfer 8 tests | Parametrize. |
| S11-CAT10-012 | CAT-10 | MINOR | tests/unit/strategy/data/test_fleet_validation.py | Missing-key tests | Parametrize. |
| S11-CAT11-001 | CAT-11 | MINOR | tests/unit/strategy/data/test_race_loader.py | test_race_has_valid_theme | Load valid themes from registry. |
| S11-CAT11-002 | CAT-11 | MINOR | tests/unit/qa/test_formation_files_have_professional_names.py | Profanity regex test | Move to pre-commit hook. |
| S11-CAT11-003 | CAT-11 | MINOR | tests/integration/data/test_portrait_load_success.py | test_portrait_load_success_no_warning | Assert zero WARNING-level records from the logger instead. |
| S11-CAT12-001 | CAT-12 | MINOR | tests/unit/builder/test_builder_validation.py | test_exclusive_group branching | Pre-compute boolean membership. |
| S11-CAT12-002 | CAT-12 | MINOR | tests/unit/builder/test_mass_validation.py | test_mass_validation try/finally mutation | Use a fixture that yields and cleans up. |
| S11-CAT12-003 | CAT-12 | MINOR | tests/unit/strategy/test_save_game_service.py | 6 setup_tmpdir autouse fixtures | Promote to a single shared fixture. |
| S11-CAT12-004 | CAT-12 | MINOR | tests/unit/ui/test_build_queue_portraits.py | test_load_resource_icons_fallback | Keep. |
| S11-CAT12-005 | CAT-12 | MINOR | tests/unit/strategy/data/test_full_roundtrip.py | _check_keys_are_strings / _check_serializable | Combine into one walker that checks both constraints. |
| S12-CAT8-001 | CAT-8 | MAJOR | tests/unit/ui/screens/test_build_queue_screen.py | Tautological error/edge case tests | Remove all tautological tests; rewrite to exercise real edge-case behavior. |
| S12-CAT8-002 | CAT-8 | MINOR | tests/unit/ui/screens/test_empire_build_queue_sidebar.py | _make_sidebar 4-level nested patches | Use patch.multiple or a fixture. |
| S12-CAT9-001 | CAT-9 | MAJOR | tests/unit/strategy/test_command_handlers.py | Duplicate _make_session_with_real_fleets | Promote to module-level helper. |
| S12-CAT10-001 | CAT-10 | MAJOR | tests/unit/strategy/test_command_handlers.py | 8+ handler error-path test clusters | Parametrize across (handler_cls, cmd_kwargs). |
| S12-CAT10-002 | CAT-10 | MINOR | tests/unit/strategy/test_planet_command_handlers.py | 3 handler classes 4 tests each | Parametrize across (handler_cls, cmd_attr_name, planet_attr_name, cmd_val, expected_val). |
| S12-CAT10-003 | CAT-10 | MINOR | tests/unit/simulation/components/test_ship_consumable_manager.py | consume_resource edge cases | Parametrize the 3 consume_resource cases; keep get_current_resource separate. |
| S12-CAT12-001 | CAT-12 | MINOR | tests/repro_issues/test_bug_13_weapons_report.py | test_prioritization_logic | Split into smaller tests; remove computed intermediate values from assertions. |

## Needs Rework

| id | original suggestion | Claude's adjusted suggestion | rationale |
|----|---------------------|------------------------------|-----------|
| S06-CAT10-001 | Parametrize all 5 set-filter tests for ~35 LOC savings. | Parametrize the 3 truly identical tests; ~6 LOC savings (not 35). | Only 3 of 5 tests are parametrizable; original suggestion overstated savings. |
| S09-CAT9-004 | Extract _make_projectile helper across cited lines 1831-1840 and 1997-2007. | Extract a _make_projectile(position, velocity, ...) helper; verify accurate line ranges before refactor. | Original line refs are fictitious; pattern real but locations need re-verification. |
| S10-CAT8-002 | Reduce 3+ levels of nested patching by injecting dependencies. | Inject path-finder and resolver via DI rather than patching internals; or document why 2-level nesting is acceptable. | Nesting depth corrected to 2 levels; core fragility valid but description was imprecise. |

## Rejected

| id | original claim | contrary evidence (file:line) | rationale |
|----|----------------|-------------------------------|-----------|
| S10-CAT12-R01 | Verifies a behavioral invariant via set operations. The suggested isdisjoint() change is preference, not quality. | tests/unit/strategy/generation/test_storm_generator.py:181-190 | Test verifies a pure output invariant; not implementation-dependent logic. |

## Out of Scope

| id | claim | reason |
|----|-------|--------|
| S09-CAT12-OOS01 | Calls real find_path_deep_space and asserts hex adjacency (=1) as a hardcoded constant. Legitimate property-based test. | intentional_property_test |
| S09-CAT12-OOS02 | Calls real ShipCombatEngine.solve_lead and asserts against hardcoded 10.0. Comments document derivation. Legitimate behavioral test. | intentional_property_test |
| S09-CAT12-OOS03 | Directional property assertion (higher mass → lower speed). Verifier and original report agree this is fine. | intentional_property_test |
| S09-CAT12-OOS04 | Calls real system_count_slider_curve and asserts max_jump <= 1 hardcoded property. Legitimate property test. | intentional_property_test |
| S11-CAT10-OOS01 | 10 boundary tests are genuinely distinct edge cases (zero, exact, fractional, very small, very large, etc.). Parametrization would obscure differing assertion logic. | legitimate_distinct_or_integration |
| S11-CAT12-OOS01 | Legitimate integration tests exercising real drag-drop event paths through handle_event. Event simulation verbosity is inherent to pygame testing. | legitimate_distinct_or_integration |
