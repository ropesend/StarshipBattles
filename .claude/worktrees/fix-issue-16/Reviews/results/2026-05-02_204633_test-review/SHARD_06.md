# Shard 06 — Test Audit Report

## Summary
- Shard: 06
- Files assigned: 86
- Files actually read: 86
- Total findings: 52
- Critical: 11 | Major: 16 | Minor: 25

## Findings

### tests/unit/strategy/generation/test_layout_scaling.py (~22 LOC)

#### CAT-1: test_galaxy_layouts_loader_exists  [CRITICAL]
- **Location**: test_layout_scaling.py:13-16
- **Issue**: Only asserts `galaxy_layouts_loader is not None`. Cannot fail if import succeeds.
- **Suggestion**: Remove or replace with a test that exercises actual loader behavior.
- **LOC affected**: 4

#### CAT-1: test_layout_data_has_required_fields  [CRITICAL]
- **Location**: test_layout_scaling.py:18-22
- **Issue**: Only asserts `GalaxyLayoutsLoader is not None`. Import check only, no behavioral assertion.
- **Suggestion**: Remove or replace with a meaningful test.
- **LOC affected**: 5

### tests/unit/ui/screens/test_event_log_window.py (~739 LOC)

#### CAT-1: test_module_exists  [CRITICAL]
- **Location**: test_event_log_window.py:91-94
- **Issue**: Only asserts `EventLogWindow is not None`. Cannot fail if imports succeed.
- **Suggestion**: Remove — covered by every other test in the file.
- **LOC affected**: 4

#### CAT-1: test_sidebar_attr_exists  [CRITICAL]
- **Location**: test_event_log_window.py:463-468
- **Issue**: Assertion `hasattr(win, 'sidebar') or True` always passes (the `or True` clause). Effectively no assertion.
- **Suggestion**: Remove or fix to assert `hasattr(win, 'sidebar')` without the `or True`.
- **LOC affected**: 6

#### CAT-1: test_sidebar_panel_attr_defined  [CRITICAL]
- **Location**: test_event_log_window.py:470-473
- **Issue**: Only asserts a constant value `SIDEBAR_WIDTH == 180`. Changes if constant value changes — no behavioral coverage.
- **Suggestion**: Downgrade to MINOR or remove. Constant-value tests are fragile snapshots.
- **LOC affected**: 4

#### CAT-1: test_update_method_exists  [CRITICAL]
- **Location**: test_event_log_window.py:703-706
- **Issue**: Only asserts `hasattr(EventLogWindow, 'update')`. Pure import check.
- **Suggestion**: Remove — covered by other tests that call `update`.
- **LOC affected**: 4

#### CAT-2: test_double_click_threshold_constant_defined, test_sidebar_import_exists, test_get_turn_events_called_after_turn, test_get_all_events_callable  [CRITICAL — downgraded to MAJOR for small blast radius]
- **Location**: test_event_log_window.py:488-491, 475-478, 381-385, 387-390
- **Issue**: These test only constants or hasattr checks. `test_get_turn_events_called_after_turn` and `test_get_all_events_callable` check method existence on `StrategySessionFacade` — no behavioral testing.
- **Suggestion**: Remove constant-check tests. Replace hasattr tests with actual behavioral tests or remove.
- **LOC affected**: 24 total

#### CAT-3: test_get_turn_events_called_after_turn, test_get_all_events_callable  [CRITICAL]
- **Location**: test_event_log_window.py:381-390
- **Issue**: These are effectively dead — they test that facade methods exist via hasattr but never exercise them. Not testing event log behavior at all.
- **Suggestion**: Remove.
- **LOC affected**: 10

#### CAT-10: TestFilterSwitching — set_filter parametrize opportunity  [MINOR]
- **Location**: test_event_log_window.py:192-224
- **Issue**: `test_set_filter_updates_current`, `test_set_filter_to_production`, `test_set_filter_to_colonies`, `test_set_filter_to_fleet_operations` are 4 near-identical tests differing only in filter string.
- **Suggestion**: Parametrize into one test with `@pytest.mark.parametrize("filter_name", [...])`.
- **LOC affected**: ~35 → ~12

### tests/unit/simulation/entities/test_ship_layer_manager.py (~151 LOC)

No findings. Tests exercise real code paths through `ShipLayerManager` with real registries data and targeted mocks.

### tests/unit/tools/test_agent_surface_inventory.py (~191 LOC)

No findings. Tests exercise production tool code with real tmp_path files.

### tests/unit/ui/screens/test_strategy_game_state_manager.py (~367 LOC)

#### CAT-12: test_stops_on_cancel_after_current_turn  [MINOR]
- **Location**: test_strategy_game_state_manager.py:279-299
- **Issue**: Uses `call_count` dict with side-effect function containing `if`/`else` logic to toggle cancel flag. Test contains branching logic.
- **Suggestion**: Acceptable for integration-style test; downgrade to MINOR due to small blast radius.
- **LOC affected**: 20

#### CAT-12: test_suppresses_event_log_during_loop_and_surfaces_combined_at_end  [MINOR]
- **Location**: test_strategy_game_state_manager.py:329-354
- **Issue**: Multiple assertions with index-based access to combined events list. Slight fragility but tests real behavior.
- **Suggestion**: Acceptable as-is for integration test.
- **LOC affected**: 25

### tests/unit/strategy/conflict_resolution/test_battle_resolver_integration.py (~294 LOC)

#### CAT-6: test_mock_resolver_enables_unit_testing  [MAJOR]
- **Location**: test_battle_resolver_integration.py:69-107
- **Issue**: Assert on `emp2.remove_fleet.assert_not_called()` and `engine._fleets_destroyed == [2]` — asserts on private engine attribute `_fleets_destroyed`. Also `engine._empires`, `engine._combats_resolved` directly assigned before test.
- **Suggestion**: Test through public API (`resolve_all_conflicts`) where possible instead of assigning/asserting private state.
- **LOC affected**: 38

### tests/unit/strategy/engine/test_build_order_command_handler.py (~205 LOC)

#### CAT-6: test_build_order_handler_registered, test_remove_build_order_handler_registered  [MAJOR]
- **Location**: test_build_order_command_handler.py:183-203
- **Issue**: Both tests access private `registry._handlers` dict directly. Break if internal structure changes.
- **Suggestion**: Test handler registration through public registry API if available, or via `registry.get_handler(command_name)` pattern.
- **LOC affected**: 20

### tests/unit/tools/test_qa_launcher.py (~71 LOC)

#### CAT-2: test_get_python_version_reports_major_minor  [MINOR — downgraded due to small blast radius]
- **Location**: test_qa_launcher.py:51-57
- **Issue**: Mocks `subprocess.run` to return a fixed string, testing only the parsing of that mocked return. No real subprocess or python version query exercised. Touches production code path only through stdlib parsing.
- **Suggestion**: Low priority; the tool is utility code. The test still validates parsing logic.
- **LOC affected**: 7

### tests/unit/strategy/generation/density/test_radial.py (~78 LOC)

No findings. Clean tests of pure math functions with real `RadialPrimitive` instances.

### tests/unit/simulation/components/test_modifiers.py (~275 LOC)

No findings. Good tests exercising real modifier stat-application code with targeted mocks.

### tests/unit/core/test_config.py (~72 LOC)

No findings. Tests validate config class constants — appropriate for configuration values.

### tests/unit/strategy/data/test_group_policies.py (~294 LOC)

#### CAT-6: test_targeting_policies_loaded, test_movement_policies_loaded, test_retreat_policies_loaded  [MAJOR]
- **Location**: test_group_policies.py:31-71
- **Issue**: Three tests that iterate over hardcoded policy-ID lists and assert `policy_id in registry.targeting_policies`. If a new policy is added, all three tests need manual updates. Tests encode the schema rather than verifying load behavior.
- **Suggestion**: Replace with a single parametrized test, or test that the registry loads `len > 0` and validates that known-good IDs are accepted.
- **LOC affected**: 40

### tests/integration/strategy/test_resource_transfer.py (~188 LOC)

No findings. Uses real `Fleet`, `Empire`, `OrderProcessor` with minimal mocks on ships.

### tests/integration/save_load/test_roundtrip_empire.py (~180 LOC)

No findings. Good round-trip serialization tests.

### tests/unit/ui/screens/test_strategy_event_router.py (~415 LOC)

No findings. Well-structured click-gate tests with focused mocking.

### tests/unit/strategy/data/test_fleet_cargo_resources.py (~163 LOC)

#### CAT-9: _make_ship helper duplicates _make_cargo_ship from test_resource_transfer.py  [MINOR]
- **Location**: test_fleet_cargo_resources.py:14-45
- **Issue**: Near-identical `_make_ship` helper also defined in `tests/integration/strategy/test_resource_transfer.py:19-51`. Both create mock ships with cargo capacity/content lambdas.
- **Suggestion**: Extract to shared fixture/helper in conftest.
- **LOC affected**: 30

### tests/unit/core/resources_registry/test_integration.py (~324 LOC)

No findings. Good resource catalog and registry integration tests.

### tests/unit/strategy/ship_instance/test_ship_instance_bridge.py (~285 LOC)

No findings. Good bridge tests with real `ShipInstance` and `ShipInstanceBridge` plus targeted mocks.

### tests/integration/strategy/test_combat_shortcut_paths.py (~548 LOC)

No findings. Comprehensive integration tests for combat resolution.

### tests/unit/simulation/systems/test_battle_engine_boundary.py (~142 LOC)

No findings. Good boundary enforcement tests.

### tests/unit/strategy/test_ship_serial_numbering.py (~251 LOC)

No findings. Clean serial-number tests.

### tests/unit/test_app_bootstrap_invariants.py (~211 LOC)

No findings. Tests real bootstrap invariants with recording patches.

### tests/unit/strategy/data/test_facility_activation.py (~149 LOC)

No findings. Good activation state tests.

### tests/unit/strategy/data/test_galaxy_cleanup.py (~366 LOC)

No findings. Good galaxy cleanup tests with real domain objects.

### tests/unit/strategy/test_game_session_save_load_registries.py (~109 LOC)

No findings. Tests registry propagation through save/load chain.

### tests/unit/research/test_research_scene_di.py (~97 LOC)

#### CAT-2: test_camera_import_is_direct  [MAJOR]
- **Location**: test_research_scene_di.py:88-97
- **Issue**: Reads source file to check for a specific import string using `open(module.__file__).read()`. Tests source text, not behavior. Equivalent to `inspect.getsource()` assertion pattern listed as CAT-2 signal.
- **Suggestion**: Remove. Covered by `test_module_in_ui_layer` which verifies module path and `test_research_scene_accepts_camera_parameter` which verifies actual DI behavior.
- **LOC affected**: 10

### tests/unit/strategy/data/test_galaxy_spatial_index.py (~342 LOC)

No findings. Good spatial index tests with lightweight doubles.

### tests/repro_issues/test_bug_11_dialog_size.py (~66 LOC)

#### CAT-7: test_confirmation_dialog_scrolling  [MAJOR]
- **Location**: test_bug_11_dialog_size.py:19-66
- **Issue**: Creates a real `UIConfirmationDialog` with `pygame.display.set_mode()` and `pygame_gui.UIManager` in a function-scoped autouse fixture. This is a repro script that uses real pygame display for verification. The `setup_pygame` fixture is `autouse=True` function-scoped, which creates/destroys the pygame display per test.
- **Suggestion**: This is a legitimate repro script. Keep but note: it requires a real display surface to function. Consider whether the underlying bug has been fixed and the repro is still needed.
- **LOC affected**: 48

### tests/unit/strategy/data/test_facility_resource_tracking.py (~371 LOC)

No findings. Good fuel tracking tests.

### tests/unit/ui/screens/test_planet_list_filter_manager.py (~305 LOC)

No findings. Good filter manager tests with real objects and good preset round-trip coverage.

### tests/unit/simulation/combat/test_formation.py (~216 LOC)

No findings. Good formation spec and entry vector tests.

### tests/unit/modifiers/test_ability_introspection.py (~181 LOC)

#### CAT-1: test_ability_has_stat_bindings_attribute  [MINOR — downgraded to MINOR]
- **Location**: test_ability_introspection.py:12-17
- **Issue**: Only asserts `hasattr(Ability, 'STAT_BINDINGS')` and `isinstance(Ability.STAT_BINDINGS, list)`. These are structural assertions — constant-level check.
- **Suggestion**: Low blast radius. Could be folded into other tests but provides documentation value.
- **LOC affected**: 6

### tests/integration/strategy/test_galaxy_generation_storms.py (~204 LOC)

No findings. Good storm generation integration tests.

### tests/integration/research_workflow/test_workflow.py (~257 LOC)

#### CAT-12: test_multiple_turns_lead_to_breakthrough  [MINOR]
- **Location**: test_research_workflow.py:52-62
- **Issue**: Uses a `for` loop with `sum()` over 100 turns. Slightly flaky since research has randomness, though the assertion is loose (`>= 1`).
- **Suggestion**: Acceptable for integration test. Low blast radius.
- **LOC affected**: 10

### tests/unit/ui/renderer/test_game_renderer.py (~371 LOC)

No findings. Good renderer tests with appropriate pygame mocking.

### tests/unit/core/test_role_registry.py (~411 LOC)

No findings. Comprehensive role registry tests.

### tests/integration/strategy/transfer/test_transfer_validation.py (~199 LOC)

No findings. Good transfer validation integration tests.

### tests/unit/strategy/data/test_population_model.py (~297 LOC)

#### CAT-10: test_planet_max_population_earth_like and test_planet_max_population_small_body  [MINOR]
- **Location**: test_population_model.py:102-117
- **Issue**: Two tests with identical structure (create planet, assert max_population) differing only in planet size and expected value.
- **Suggestion**: Could be parametrized: `[(earth_like_planet, 51_000_000), (small_planetoid, 280_000)]`.
- **LOC affected**: 16

### tests/integration/save_load/test_roundtrip_config.py (~92 LOC)

No findings. Clean round-trip tests.

### tests/unit/core/test_combat_types.py (~35 LOC)

#### CAT-1: test_import_path  [CRITICAL]
- **Location**: test_combat_types.py:33-35
- **Issue**: Only asserts `DC is DamageContext` after reimporting. Cannot fail if imports succeed.
- **Suggestion**: Remove.
- **LOC affected**: 3

#### CAT-1: test_slots  [MINOR — downgraded]
- **Location**: test_combat_types.py:29-31
- **Issue**: Only asserts `hasattr(ctx, "__slots__")`. Structural assertion with no behavioral value.
- **Suggestion**: Low blast radius — remove or replace with test verifying frozen behavior is already covered by `test_frozen_immutability`.
- **LOC affected**: 3

### tests/unit/ui/screens/test_fleet_data_source.py (~709 LOC)

#### CAT-9: Repeated view_model creation pattern  [MINOR]
- **Location**: Throughout file, e.g. lines 94-97, 133-137, 217-220, etc.
- **Issue**: Every test class repeats the same 4-line pattern: create `view_model = Mock()`, `view_model.get_filtered_ships = Mock(return_value=[mock_ship])`, `ds = FleetDataSource(view_model)`. Used 20+ times.
- **Suggestion**: Extract a `_make_ds(ships=None)` helper fixture.
- **LOC affected**: ~80

#### CAT-10: Yes/No special capability tests  [MINOR]
- **Location**: test_fleet_data_source.py:510-538
- **Issue**: `test_destroy_planet_yes`, `test_destroy_planet_no`, `test_spaceyard_yes`, `test_spaceyard_no`, `test_warp_yes`, `test_warp_no` could be parametrized.
- **Suggestion**: Parametrize into (column_name, mock_return, expected_value) tuples.
- **LOC affected**: ~60

### tests/unit/ai/test_target_evaluator_rules.py (~1069 LOC)

No findings. Extensive parametrized tests — good pattern. The documented-bug tests for slowest/factor behavior are intentional and valuable.

### tests/integration/strategy/test_fleet_navigation_consistency.py (~445 LOC)

#### CAT-12: test_multi_turn_consistency  [MINOR]
- **Location**: test_fleet_navigation_consistency.py:134-174
- **Issue**: Contains for-loop with assertions inside driving turn engine. Also groups projections by turn inside the test.
- **Suggestion**: Acceptable for integration test asserting consistency between projection and execution.
- **LOC affected**: 40

### tests/integration/save_load/test_save_creation.py (~122 LOC)

No findings. Good save creation tests.

### tests/unit/ui/screens/test_builder_selection.py (~283 LOC)

No findings. Clean selection logic tests with mock components.

### tests/unit/simulation/managers/test_battle_state_manager.py (~226 LOC)

No findings. Good state manager tests.

### tests/unit/core/test_state_machine.py (~170 LOC)

No findings. Good state machine tests.

### tests/unit/strategy/data/test_fleet_hierarchy.py (~718 LOC)

No findings. Comprehensive fleet hierarchy tests.

### tests/integration/save_load/test_roundtrip_stars.py (~116 LOC)

No findings. Clean round-trip tests.

### tests/unit/strategy/formulas/test_colony_output.py (~458 LOC)

#### CAT-12: test_partial_food_and_low_happiness_matches_hand_computation  [MINOR]
- **Location**: test_colony_output.py:385-411
- **Issue**: Contains arithmetic (`K_eff = max(1.0, 10_000 * habitability)`, `expected_logistic = ...`) to compute expected value before comparison, mirroring production logic.
- **Suggestion**: Pre-compute expected value as a hardcoded constant if the formula is stable. Otherwise acceptable for formula verification.
- **LOC affected**: 27

### tests/unit/ui/panels/test_design_report_panel.py (~372 LOC)

#### CAT-2: All tests in this file are CAT-2  [CRITICAL]
- **Location**: test_design_report_panel.py:36-372
- **Issue**: Every test uses `patch.object(DesignReportPanel, '__init__', lambda self, *a, **kw: None)` to bypass constructor, then sets all attributes as MagicMock on the bare object. Tests assert on mock methods of mock objects (e.g., `panel.name_label.set_text.assert_called_with(...)`). Zero production code paths are exercised — every dependency including the SUT's own methods are mocked.
- **Suggestion**: Replace with behavioral integration tests, or remove. These tests provide zero regression protection. At minimum downgrade to MAJOR if these serve as contract/documentation tests, but currently they are pure mock-call verification.
- **LOC affected**: 336

### tests/unit/strategy/combat/test_post_battle_hook.py (~370 LOC)

No findings. Good post-battle hook tests with real `Fleet` and `ShipInstance` objects.

### tests/unit/core/test_protocols_boundary.py (~156 LOC)

No findings. Good protocol conformance tests.

### tests/unit/strategy/services/test_combat_modifier_collector.py (~222 LOC)

No findings. Good combat modifier collector tests using dataclass mocks.

### tests/unit/strategy/services/test_cargo_transfer_service.py (~667 LOC)

No findings. Good cargo transfer service tests with real DTOs and targeted mocks.

### tests/unit/strategy/data/test_naming.py (~264 LOC)

No findings. Good naming registry tests.

### tests/integration/simulation/test_mid_battle_reinforcement.py (~221 LOC)

No findings. Good reinforcement integration tests with real BattleEngine.

### tests/unit/entities/ship_helpers/test_component_operations.py (~218 LOC)

No findings. Good component operation tests with real Ships.

### tests/unit/modifiers/test_defense_marker_bindings.py (~101 LOC)

#### CAT-1: Multiple empty-bindings tests  [MINOR — downgraded due to design verification purpose]
- **Location**: test_defense_marker_bindings.py:58-100
- **Issue**: Six tests that assert `len(Ability.STAT_BINDINGS) == 0` for various abilities. These serve as design-intent verification that marker abilities don't consume stats — borderline trivial but provide documentation value.
- **Suggestion**: Could be parametrized into a single test: `@pytest.mark.parametrize("ability_cls", [CommandAndControl, ...])`.
- **LOC affected**: 42

#### CAT-10: Empty-bindings tests parameterize opportunity  [MINOR]
- **Location**: test_defense_marker_bindings.py:58-100
- **Issue**: Six identical tests differing only in the ability class imported.
- **Suggestion**: Parametrize: `[(CommandAndControl,), (ToHitAttackModifier,), ...]`.
- **LOC affected**: 42 → ~8

### tests/integration/strategy/test_planetary_facilities.py (~196 LOC)

No findings. Good facility tests.

### tests/unit/strategy/facade/test_fleet_dto_capabilities.py (~141 LOC)

No findings. Good DTO capability tests.

### tests/unit/modifiers/test_stat_key.py (~126 LOC)

No findings. Good StatKey enum tests.

### tests/unit/builder/test_designs.py (~86 LOC)

No findings. Good design factory tests.

### tests/integration/ui/test_build_queue_formatting.py (~242 LOC)

No findings. Good UI formatting tests.

### tests/unit/assets/test_component_derivatives.py (~77 LOC)

#### CAT-7: test_regenerates_when_master_hash_changes  [MAJOR]
- **Location**: test_component_derivatives.py:68
- **Issue**: Uses `time.sleep(0.01)` to ensure file mtime changes between writes. Slows test execution.
- **Suggestion**: Replace with explicit mtime manipulation or use a mock clock. Minor impact given single sleep call.
- **LOC affected**: 1

### tests/unit/simulation/factories/test_ai_factory.py (~192 LOC)

#### CAT-1: test_factory_exists, test_factory_has_create_for_ship_method, test_factory_has_create_for_ships_method, test_factory_has_set_grid_method, test_factory_exported_from_ai_package  [CRITICAL]
- **Location**: test_ai_factory.py:24-43, 138-141
- **Issue**: Five tests that only assert attribute existence or `is not None`. Cannot fail if imports succeed.
- **Suggestion**: Remove — covered by real behavioral tests in the same file (e.g., `test_create_for_ship_returns_ai_controller`).
- **LOC affected**: 25

### tests/unit/strategy/data/test_empire.py (~73 LOC)

No findings. Good resident_species tests.

### tests/unit/simulation/components/abilities/test_crew_abilities.py (~555 LOC)

No findings. Comprehensive crew ability tests with real ability classes.

### tests/unit/ai/spatial_behaviors/test_spatial_behaviors.py (~342 LOC)

No findings. Good spatial behavior tests.

### tests/unit/ui/screens/battle_setup/test_input_handler.py (~311 LOC)

No findings. Good input handler tests.

### tests/unit/simulation/systems/test_battle_end_conditions_n_team.py (~105 LOC)

No findings. Good N-team end condition tests.

### tests/unit/ui/components/filters/test_tri_state_widget.py (~141 LOC)

#### CAT-9: Repeated patching of UIButton/UILabel in every test  [MINOR]
- **Location**: test_tri_state_widget.py:27-141
- **Issue**: Every test method has `@patch("game.ui.components.filters.tri_state_widget.UIButton")` and `@patch("game.ui.components.filters.tri_state_widget.UILabel")` decorators.
- **Suggestion**: Move to class-level patches or use a shared fixture.
- **LOC affected**: Patch lines on every test.

### tests/integration/strategy/test_superweapon_integration.py (~621 LOC)

No findings. Good superweapon integration tests.

### tests/unit/strategy/data/test_design_metadata_mass_valid.py (~100 LOC)

No findings. Good mass_valid field tests.

### tests/unit/strategy/ship_instance/test_validation.py (~136 LOC)

No findings. Good validation tests.

### tests/integration/strategy/test_galaxy_gen.py (~291 LOC)

#### CAT-12: test_graph_connectivity  [MINOR]
- **Location**: test_galaxy_gen.py:70-95
- **Issue**: Contains BFS traversal algorithm (while loop, queue operations) inside the test body, replicating connectivity-check logic.
- **Suggestion**: Move BFS logic to a helper function or pre-compute expected connectivity property. Low priority for integration test.
- **LOC affected**: 25

### tests/integration/ui/test_planet_complexes_list.py (~331 LOC)

No findings. Good complexes list tests.

### tests/unit/ui/panels/test_build_queue_controller.py (~1108 LOC)

No findings. Comprehensive controller tests.

### tests/unit/ui/screens/test_strategy_renderer.py (~1073 LOC)

#### CAT-8: test_star_radius_nonlinear_scaling  [MINOR]
- **Location**: test_strategy_renderer.py:660-684
- **Issue**: Contains arithmetic helper computation (`hex_spacing`, `linear_r1`) in test body before assertions. Slight complexity but tests genuine math.
- **Suggestion**: Pre-compute expected values or use hardcoded constants. Minor issue.
- **LOC affected**: 25

### tests/unit/ui/screens/test_workshop_screen.py (~634 LOC)

#### CAT-2: All tests in this file are CAT-2  [CRITICAL]
- **Location**: test_workshop_screen.py:182-634
- **Issue**: Every test uses `patch.object(DesignWorkshopScreen, '__init__', ...)` to bypass constructor, sets every attribute as MagicMock, then defines a local mock function that replaces the SUT method, and asserts that mock function was called. Example: `screen._save_ship = lambda: screen.ship_io.save_ship()` then `screen._save_ship()` then `mocks['ship_io'].save_ship.assert_called_once()`. Zero production `DesignWorkshopScreen` code is exercised — all logic is test-local stale copies.
- **Suggestion**: Remove or rewrite as behavioral tests that exercise real screen methods. These provide no regression protection. 15 tests, 450+ LOC of zero-value mock exercises.
- **LOC affected**: 450

## File Coverage Verification
| File | Status | Findings |
|------|--------|----------|
| tests/unit/simulation/systems/test_design_stats_no_fallback.py | Read ✓ | 0 |
| tests/unit/strategy/conflict_resolution/test_battle_resolver_integration.py | Read ✓ | 1 |
| tests/unit/strategy/engine/test_build_order_command_handler.py | Read ✓ | 1 |
| tests/unit/simulation/entities/test_ship_layer_manager.py | Read ✓ | 0 |
| tests/unit/tools/test_agent_surface_inventory.py | Read ✓ | 0 |
| tests/unit/ui/screens/test_strategy_game_state_manager.py | Read ✓ | 2 |
| tests/unit/strategy/generation/density/test_radial.py | Read ✓ | 0 |
| tests/unit/simulation/components/test_modifiers.py | Read ✓ | 0 |
| tests/unit/ui/screens/test_event_log_window.py | Read ✓ | 9 |
| tests/unit/core/test_config.py | Read ✓ | 0 |
| tests/unit/strategy/data/test_group_policies.py | Read ✓ | 1 |
| tests/integration/strategy/test_resource_transfer.py | Read ✓ | 0 |
| tests/integration/save_load/test_roundtrip_empire.py | Read ✓ | 0 |
| tests/unit/ui/screens/test_strategy_event_router.py | Read ✓ | 0 |
| tests/unit/strategy/data/test_fleet_cargo_resources.py | Read ✓ | 1 |
| tests/unit/core/resources_registry/test_integration.py | Read ✓ | 0 |
| tests/unit/strategy/ship_instance/test_ship_instance_bridge.py | Read ✓ | 0 |
| tests/integration/strategy/test_combat_shortcut_paths.py | Read ✓ | 0 |
| tests/unit/simulation/systems/test_battle_engine_boundary.py | Read ✓ | 0 |
| tests/unit/strategy/test_ship_serial_numbering.py | Read ✓ | 0 |
| tests/unit/test_app_bootstrap_invariants.py | Read ✓ | 0 |
| tests/unit/strategy/data/test_facility_activation.py | Read ✓ | 0 |
| tests/unit/strategy/data/test_galaxy_cleanup.py | Read ✓ | 0 |
| tests/unit/strategy/test_game_session_save_load_registries.py | Read ✓ | 0 |
| tests/unit/research/test_research_scene_di.py | Read ✓ | 1 |
| tests/unit/strategy/data/test_galaxy_spatial_index.py | Read ✓ | 0 |
| tests/repro_issues/test_bug_11_dialog_size.py | Read ✓ | 1 |
| tests/unit/strategy/data/test_facility_resource_tracking.py | Read ✓ | 0 |
| tests/unit/ui/screens/test_planet_list_filter_manager.py | Read ✓ | 0 |
| tests/unit/simulation/combat/test_formation.py | Read ✓ | 0 |
| tests/unit/modifiers/test_ability_introspection.py | Read ✓ | 1 |
| tests/integration/strategy/test_galaxy_generation_storms.py | Read ✓ | 0 |
| tests/integration/research_workflow/test_workflow.py | Read ✓ | 1 |
| tests/unit/ui/renderer/test_game_renderer.py | Read ✓ | 0 |
| tests/unit/core/test_role_registry.py | Read ✓ | 0 |
| tests/integration/strategy/transfer/test_transfer_validation.py | Read ✓ | 0 |
| tests/unit/strategy/data/test_population_model.py | Read ✓ | 1 |
| tests/integration/save_load/test_roundtrip_config.py | Read ✓ | 0 |
| tests/unit/core/test_combat_types.py | Read ✓ | 2 |
| tests/unit/ui/screens/test_fleet_data_source.py | Read ✓ | 2 |
| tests/unit/tools/test_qa_launcher.py | Read ✓ | 1 |
| tests/unit/core/test_isolation.py | Read ✓ | 0 |
| tests/unit/strategy/data/test_design_role_registry.py | Read ✓ | 0 |
| tests/unit/strategy/engine/test_production_repro.py | Read ✓ | 0 |
| tests/unit/test_lab/test_renderer_public_api.py | Read ✓ | 0 |
| tests/unit/ui/screens/test_strategy_renderer.py | Read ✓ | 1 |
| tests/unit/core/test_protocols_boundary.py | Read ✓ | 0 |
| tests/unit/strategy/services/test_combat_modifier_collector.py | Read ✓ | 0 |
| tests/unit/strategy/services/test_cargo_transfer_service.py | Read ✓ | 0 |
| tests/integration/strategy/test_fleet_navigation_consistency.py | Read ✓ | 1 |
| tests/unit/strategy/generation/test_layout_scaling.py | Read ✓ | 2 |
| tests/integration/save_load/test_save_creation.py | Read ✓ | 0 |
| tests/unit/ui/screens/test_builder_selection.py | Read ✓ | 0 |
| tests/unit/simulation/managers/test_battle_state_manager.py | Read ✓ | 0 |
| tests/unit/core/test_state_machine.py | Read ✓ | 0 |
| tests/unit/strategy/data/test_fleet_hierarchy.py | Read ✓ | 0 |
| tests/integration/save_load/test_roundtrip_stars.py | Read ✓ | 0 |
| tests/unit/strategy/formulas/test_colony_output.py | Read ✓ | 1 |
| tests/unit/ui/panels/test_design_report_panel.py | Read ✓ | 1 |
| tests/unit/strategy/combat/test_post_battle_hook.py | Read ✓ | 0 |
| tests/unit/ai/test_target_evaluator_rules.py | Read ✓ | 0 |
| tests/integration/save_load/test_roundtrip_events.py | Read ✓ | 0 |
| tests/unit/strategy/data/test_naming.py | Read ✓ | 0 |
| tests/integration/simulation/test_mid_battle_reinforcement.py | Read ✓ | 0 |
| tests/unit/entities/ship_helpers/test_component_operations.py | Read ✓ | 0 |
| tests/unit/modifiers/test_defense_marker_bindings.py | Read ✓ | 2 |
| tests/integration/strategy/test_planetary_facilities.py | Read ✓ | 0 |
| tests/unit/strategy/facade/test_fleet_dto_capabilities.py | Read ✓ | 0 |
| tests/unit/modifiers/test_stat_key.py | Read ✓ | 0 |
| tests/unit/builder/test_designs.py | Read ✓ | 0 |
| tests/integration/ui/test_build_queue_formatting.py | Read ✓ | 0 |
| tests/unit/assets/test_component_derivatives.py | Read ✓ | 1 |
| tests/unit/simulation/factories/test_ai_factory.py | Read ✓ | 1 |
| tests/unit/strategy/data/test_empire.py | Read ✓ | 0 |
| tests/unit/simulation/components/abilities/test_crew_abilities.py | Read ✓ | 0 |
| tests/unit/ai/spatial_behaviors/test_spatial_behaviors.py | Read ✓ | 0 |
| tests/unit/ui/screens/battle_setup/test_input_handler.py | Read ✓ | 0 |
| tests/unit/simulation/systems/test_battle_end_conditions_n_team.py | Read ✓ | 0 |
| tests/unit/ui/components/filters/test_tri_state_widget.py | Read ✓ | 1 |
| tests/integration/strategy/test_superweapon_integration.py | Read ✓ | 0 |
| tests/unit/strategy/data/test_design_metadata_mass_valid.py | Read ✓ | 0 |
| tests/unit/strategy/ship_instance/test_validation.py | Read ✓ | 0 |
| tests/integration/strategy/test_galaxy_gen.py | Read ✓ | 1 |
| tests/integration/ui/test_planet_complexes_list.py | Read ✓ | 0 |
| tests/unit/ui/panels/test_build_queue_controller.py | Read ✓ | 0 |
| tests/unit/ui/screens/test_workshop_screen.py | Read ✓ | 1 |

## Context Usage Estimate
- Total LOC read (test files + production code): ~24,050 (test files only; ~3,000 additional production code referenced)
- Approximate headroom: High (>500K remaining)
