# Shard 06 — Test Audit Report

## Summary
- Shard: 06 | Files assigned: 91 | Files actually read: 91 | Total findings: 20 | Critical: 0 | Major: 9 | Minor: 11

## Findings

### tests/unit/ui/test_weapons_report_layout.py

#### CAT-5: test_button_creation_widths [MAJOR]
- **Location**: test_weapons_report_layout.py:16-35 | **Issue**: The autouse `setup` fixture is function-scoped and creates a real pygame display (set_mode + UIManager) for every test, even though conftest.py already ensures SDL_VIDEODRIVER=dummy. All tests in the class share the same surface/manager state. Use class-scoped fixture.
- **Suggestion**: Change `@pytest.fixture(autouse=True)` to `@pytest.fixture(autouse=True, scope="class")` and restructure as class-scoped setup, since the single test in this file reuses the same display surface.
- **LOC affected**: 20

### tests/unit/ui/screens/test_design_selector_window.py

#### CAT-8: test_design_row_layout [MINOR]
- **Location**: test_design_selector_window.py:489-498 | **Issue**: `test_design_row_layout` has 5 nested `with patch()` blocks to mock pygame_gui constructors. This pattern repeats identically in `test_design_row_with_spaces_in_design_id` (lines 509-518) and `test_design_row_with_fullstops_in_design_id` (lines 534-543).
- **Suggestion**: Extract the nested patch stack into a shared context-manager helper (e.g., a `_patched_row_creation` fixture or helper function) and reuse across all three tests.
- **LOC affected**: 60

#### CAT-10: TestDesignSelectorUICreation class [MINOR]
- **Location**: test_design_selector_window.py:447-546 | **Issue**: `test_rebuild_design_list_clears_existing` and `test_rebuild_design_list_creates_rows` share nearly identical setup (create window, set filtered_designs, mock _create_design_row). Only the assertion differs. `test_design_row_layout`, `test_design_row_with_spaces_in_design_id`, `test_design_row_with_fullstops_in_design_id` differ only in the design_id and expected assertion about object_id sanitization.
- **Suggestion**: Parametrize the three design-ID sanitization tests with `@pytest.mark.parametrize("design_id,expect_fail", [("BS Battleship GC", " "), ("v2.0_cruiser", ".")])`.
- **LOC affected**: 120

#### CAT-11: test_mine_filter_propagates_to_search_designs [MINOR]
- **Location**: test_design_selector_window.py:803-814 | **Issue**: Asserts `call_args[1]["filters"]["vehicle_type"] == "Mine"` using positional indexing into mock call_args. If the method signature changes (adds a third argument), the test silently breaks. The same pattern exists across many other filter tests (lines 189, 201, 215, etc.).
- **Suggestion**: Replace `call_args[1]['filters']['vehicle_type']` with keyword-arg assertions: `library.search_designs.assert_called_with(filters={"vehicle_type": "Mine"})` or at minimum `library.search_designs.call_args.kwargs["filters"]["vehicle_type"]`.
- **LOC affected**: 130

### tests/unit/strategy/superweapon/test_superweapon_order_pop_matrix.py

(Note: actual path is tests/unit/strategy/engine/test_superweapon_order_pop_matrix.py)

#### CAT-10: Superweapon order-pop test clusters [MINOR]
- **Location**: test_superweapon_order_pop_matrix.py:119-509 | **Issue**: Five test classes (`TestImplodePlanetOrderPop`, `TestStellerateStarOrderPop`, `TestOpenWarpPointOrderPop`, `TestCloseWarpPointOrderPop`, `TestCreateDysonSphereOrderPop`) each contain three tests with identical structure: `test_success_pops_order`, `test_failure_no_target_pops_order`, `test_failure_no_ship_pops_order`. The only differences are the superweapon type, the component_id, the process method called, and in one case whether fleet_consumed is asserted. This is ~15 tests with near-identical bodies.
- **Suggestion**: Parametrize across superweapon type tuples: `@pytest.mark.parametrize("weapon_type,order_type,component_id,process_method,fleet_consumed", [...])`. The 15 individual tests collapse to 3 parametrized tests (success, no-target, no-ship) × 1 parametrize decorator.
- **LOC affected**: 390

### tests/unit/ui/screens/test_strategy_input_handler_hotkeys.py

#### CAT-10: Fleet mode-activation hotkey cluster [MINOR]
- **Location**: test_strategy_input_handler_hotkeys.py:70-175 | **Issue**: Seven tests (`test_m_triggers_move_mode`, `test_j_triggers_join_mode`, `test_c_triggers_colonize_mode`, `test_t_sets_transfer_mode`, `test_w_triggers_warp_target_mode`, and three ignore-without-fleet variants) share identical structure: create handler with mapper, set selected_fleet, fire keydown, check input_mode. These differ only in key, mode, and (for W) a capability check.
- **Suggestion**: Parametrize: `@pytest.mark.parametrize("key,mode,fleet_required,capability_check", [(K_m, 'MOVE', True, None), (K_j, 'JOIN', True, None), ...])`. The 7 tests collapse to 1 parametrized test.
- **LOC affected**: 105

#### CAT-10: Zoom hotkey cluster [MINOR]
- **Location**: test_strategy_input_handler_hotkeys.py:178-208 | **Issue**: Four zoom tests (`test_shift_g_zooms_galaxy`, `test_shift_s_zooms_system`, `test_kp_plus_zooms_in`, `test_kp_minus_zooms_out`) share identical structure differing only in key, modifiers, and the camera nav method called.
- **Suggestion**: Parametrize across (key, mod, expected_method) tuples. 4 tests become 1.
- **LOC affected**: 30

#### CAT-10: Button hotkey cluster [MINOR]
- **Location**: test_strategy_input_handler_hotkeys.py:211-317 | **Issue**: Eleven tests spanning `TestNewHotkeyButtonActions` (Enter, Shift+P, Shift+D, Shift+B, Ctrl+S, comma, period, [, ], O, F) share the pattern: press key → assert scene method called. Ditto for the three ignore-without-fleet variants of O and F.
- **Suggestion**: Parametrize across (key, mod, method_name, method_args, fleet_required) tuples. ~13 tests collapse to 2-3 parametrized tests.
- **LOC affected**: 107

### tests/unit/strategy/services/test_race_description_llm_controller.py

#### CAT-7: test_cancel_bio_while_running [MAJOR]
- **Location**: test_race_description_llm_controller.py:325 | **Issue**: `time.sleep(0.02)` is used to let the worker enter blocking state before cancelling. This introduces latency and flaky timing. Also present at line 343 in `test_cancel_all` and line 364 in `test_cancel_socio_while_running`.
- **Suggestion**: Replace `time.sleep(0.02)` with a polling loop that waits for the controller state to transition from IDLE to RUNNING (using `_wait_until` helper already defined in the file at line 133).
- **LOC affected**: 50

### tests/unit/ui/screens/test_empire_build_queue_formatter.py

#### CAT-9: Repeated import inside test methods [MINOR]
- **Location**: test_empire_build_queue_formatter.py:235-270 | **Issue**: `get_resource_rate_text` and `get_resource_total_text` are imported inside each test method body in `TestGetResourceRateText` and `TestGetResourceTotalText` classes. The same import (`from game.ui.screens.empire_build_queue_formatter import get_resource_rate_text`) appears 8 times across the two classes.
- **Suggestion**: Move the imports to module level (they're pure functions with no side effects) or to class-level fixtures.
- **LOC affected**: 40

### tests/unit/strategy/conflict_resolution/conftest.py

#### CAT-5: Function-scoped fixtures [MAJOR]
- **Location**: conftest.py:12-35 | **Issue**: `mock_fleet` and `mock_empire` fixtures are function-scoped. Since they return stateless MagicMock objects and never mutate, they could be session-scoped.
- **Suggestion**: Change to `scope="session"` — these are pure stubs with no mutable state.
- **LOC affected**: 24

### tests/unit/simulation/armor_mechanics/conftest.py

#### CAT-5: Function-scoped fixtures [MAJOR]
- **Location**: conftest.py:6-35 | **Issue**: `mock_ship_with_emissive` and `mock_ship_base` are function-scoped MagicMock fixtures that return stateless objects.
- **Suggestion**: Change to `scope="session"`.
- **LOC affected**: 29

### tests/unit/ui/screens/strategy_render/test_hex_outlines.py

#### CAT-6: Mock internal detail assertion [MAJOR]
- **Location**: test_hex_outlines.py:101-106 | **Issue**: `test_draw_dispatches_inner_hex_outlines_by_ownership_state` asserts on `renderer._draw_inner_hex.call_args_list` matching exact float positions derived from hex geometry (`8.660254037844386`). This is mocking an internal implementation detail (`_draw_inner_hex`), and the exact float values are fragile to hex math changes.
- **Suggestion**: Assert that `_draw_inner_hex` was called the expected number of times with the correct colors at position-independent levels, or test at a higher abstraction level.
- **LOC affected**: 15

### tests/unit/ui/screens/test_fleet_report_sidebar.py

#### CAT-6: Patch-stack mocking internal modules [MAJOR]
- **Location**: test_fleet_report_sidebar.py:38-58 | **Issue**: The `_create_sidebar` helper patches both `game.ui.screens.fleet_report_sidebar.UILabel` AND `game.ui.widgets.column_toggle_section.UILabel` with identical mocks. This 3-level nested patch stack mocks internal implementation modules, not I/O boundaries.
- **Suggestion**: Use the `make_ui_widget` factory pattern (from `tests.fixtures.ui_widget_factory`) already in use elsewhere in the codebase.
- **LOC affected**: 20

### tests/unit/strategy/generation/density/conftest.py

#### CAT-5: Function-scoped primitive fixtures [MAJOR]
- **Location**: conftest.py:17-89 | **Issue**: All 8 primitive fixtures (radial_primitive, ring_primitive, etc.) are function-scoped and return simple immutable data objects (the primitives themselves don't hold state).
- **Suggestion**: Change to `scope="session"` — the primitive constructors produce deterministic objects.
- **LOC affected**: 73

### tests/unit/strategy/consumable_management_engine/test_characterization.py

#### CAT-6: Mocking internal method [MAJOR]
- **Location**: test_characterization.py:92 | **Issue**: `test_failed_consume_resource_triggers_auto_disable_and_returns_depletion` patches `engine._auto_disable_components_for_resource`, which is a private method on the class under test. Mocking a private method of the SUT is brittle — if the method is renamed the test breaks without any real behavior change.
- **Suggestion**: Verify the auto-disable behavior by asserting the observable side effects (component disabled state, depletion entry returned) rather than patching the private method.
- **LOC affected**: 10

### tests/unit/strategy/formulas/test_colony_output.py

#### CAT-12: test_high_happiness_scales_logistic_term [MINOR]
- **Location**: test_colony_output.py:436-452 | **Issue**: Test body contains the logic `rate_giddy == pytest.approx(rate_normal * 2.0, rel=1e-9)` — it computes two growth rates and asserts their ratio. This is effectively a logic-heavy test with computed expected values. The relatively tight tolerance of `rel=1e-9` is also fragile to floating-point drift.
- **Suggestion**: Pre-compute the expected rate value and assert directly rather than asserting a ratio relationship that re-derives the formula internally.
- **LOC affected**: 17

### tests/unit/ui/panels/test_design_report_panel.py

#### CAT-11: test_width_returns_750 [MINOR]
- **Location**: test_design_report_panel.py:267-273 | **Issue**: `assert width == 750` — hardcoded constant check. If the UI width constant changes, this test fails even though the method is correct.
- **Suggestion**: Assert `width > 0` and `isinstance(width, int)`, or assert against the named constant (e.g., `UIConfig.DESIGN_REPORT_WIDTH`) if one exists.
- **LOC affected**: 7

### tests/unit/ui/screens/test_workshop_event_router_select_component.py

#### CAT-11: test_dragged_item_mass_reflects_design_mass_budget [MINOR]
- **Location**: test_workshop_event_router_select_component.py:79-91 | **Issue**: Test reimplements the bridge mass formula locally: `expected = 50.0 * (2000.0 / 1000.0) ** 0.5`. If the formula in data/components.json changes, the test fails with a wrong expected value while the code is correct.
- **Suggestion**: Assert `gui.controller.dragged_item.mass > 0` and `gui.controller.dragged_item.ship is gui.ship`, then rely on the formula regression being caught by dedicated formula tests. Alternatively, load the expected value from data/components.json.
- **LOC affected**: 12

## File Coverage Verification

| File | LOC | Read | Contains test functions? | Has findings? |
|------|-----|------|------------------------|---------------|
| tests/unit/strategy/services/ability_sources/test_intrinsic_roll.py | 157 | Yes | Yes | No |
| tests/unit/strategy/data/test_fleet_display_name.py | 133 | Yes | Yes | No |
| tests/unit/simulation/components/test_modifier_schema.py | 354 | Yes | Yes | No |
| tests/unit/ui/screens/test_design_selector_window.py | 814 | Yes | Yes | CAT-8, CAT-10, CAT-11 |
| tests/unit/ui/test_weapons_report_layout.py | 63 | Yes | Yes | CAT-5 |
| tests/unit/strategy/data/test_fleet_order_resolution.py | 414 | Yes | Yes | No |
| tests/unit/strategy/turn_engine/test_turn_snapshot_capture_failure.py | 70 | Yes | Yes | No |
| tests/integration/strategy/test_three_empire_battle.py | 174 | Yes | Yes | No |
| tests/unit/strategy/consumable_management_engine/test_characterization.py | 223 | Yes | Yes | CAT-6 |
| tests/unit/strategy/conflict_resolution/conftest.py | 35 | Yes | No (fixtures only) | CAT-5 |
| tests/unit/strategy/test_game_session_events.py | 217 | Yes | Yes | No |
| tests/unit/ui/screens/builder/test_schematic_view.py | 36 | Yes | Yes | No |
| tests/unit/strategy/generation/density/conftest.py | 93 | Yes | No (fixtures only) | CAT-5 |
| tests/unit/ui/screens/test_fleet_report_sidebar.py | 191 | Yes | Yes | CAT-6 |
| tests/integration/ui/test_stats_render.py | 71 | Yes | Yes | No |
| tests/integration/test_fms_c_e2e.py | 245 | Yes | Yes | No |
| tests/unit/modifiers/test_formula_error_handling.py | 163 | Yes | Yes | No |
| tests/unit/strategy/data/test_no_method_body_over_5_loc.py | 83 | Yes | Yes | No |
| tests/unit/strategy/generation/test_region_classifier.py | 562 | Yes | Yes | No |
| tests/unit/ui/components/table/test_column_manager.py | 213 | Yes | Yes | No |
| tests/unit/strategy/data/test_ship_cargo_manager_per_bay.py | 216 | Yes | Yes | No |
| tests/unit/simulation/armor_mechanics/conftest.py | 37 | Yes | No (fixtures only) | CAT-5 |
| tests/unit/ui/screens/builder/test_modifier_config_size_mount.py | 89 | Yes | Yes | No |
| tests/unit/strategy/conflict_resolution/test_battle_resolver_integration.py | 322 | Yes | Yes | No |
| tests/integration/save_load/test_save_creation.py | 122 | Yes | Yes | No |
| tests/unit/ui/test_config.py | 73 | Yes | Yes | No |
| tests/unit/builder/test_selection_refinements.py | 79 | Yes | Yes | No |
| tests/integration/replay/test_verification_queue_integration.py | 299 | Yes | Yes | No |
| tests/integration/fleet_combat/test_service_integration.py | 208 | Yes | Yes | No |
| tests/integration/test_fms_c_carrier_ai_launch.py | 279 | Yes | Yes | No |
| tests/unit/strategy/formulas/test_colony_output.py | 465 | Yes | Yes | CAT-12 |
| tests/unit/ui/screens/strategy_render/test_hex_outlines.py | 146 | Yes | Yes | CAT-6 |
| tests/unit/simulation/entities/test_signature_bonus.py | 63 | Yes | Yes | No |
| tests/unit/simulation/components/abilities/test_ability_scope_extensions.py | 73 | Yes | Yes | No |
| tests/unit/simulation/replay/test_replay_player.py | 114 | Yes | Yes | No |
| tests/unit/research/test_research_tracker.py | 648 | Yes | Yes | No |
| tests/unit/builder/test_builder_drag_drop_real.py | 245 | Yes | Yes | No |
| tests/integration/strategy/combat/test_flat_shield_bonus.py | 205 | Yes | Yes | No |
| tests/unit/ui/screens/test_lab/test_dialogs.py | 111 | Yes | Yes | No |
| tests/unit/strategy/engine/test_conflict_deployed_group_trigger.py | 164 | Yes | Yes | No |
| tests/unit/simulation/entities/test_ship_loader.py | 820 | Yes | Yes | No |
| tests/unit/strategy/data/test_planet_gen.py | 736 | Yes | Yes | No |
| tests/unit/strategy/fleet_movement_engine/test_batch.py | 196 | Yes | Yes | No |
| tests/unit/strategy/engine/test_production_spawner.py | 582 | Yes | Yes | No |
| tests/unit/core/test_protocols.py | 479 | Yes | Yes | No |
| tests/unit/conftest.py | 26 | Yes | No (pytest hook only) | No |
| tests/unit/strategy/engine/test_superweapon_order_pop_matrix.py | 552 | Yes | Yes | CAT-10 |
| tests/unit/ui/screens/test_strategy_input_handler_hotkeys.py | 526 | Yes | Yes | CAT-10 (×3 clusters) |
| tests/unit/systems/test_layer_refinements.py | 136 | Yes | Yes | No |
| tests/unit/ui/screens/test_empire_build_queue_formatter.py | 320 | Yes | Yes | CAT-9 |
| tests/integration/save_load/test_roundtrip_orders.py | 156 | Yes | Yes | No |
| tests/unit/ai/test_satellite_controller.py | 146 | Yes | Yes | No |
| tests/unit/strategy/turn_engine/test_turn_engine_phase_timing.py | 308 | Yes | Yes | No |
| tests/unit/research/research_scene/test_callbacks.py | 244 | Yes | Yes | No |
| tests/unit/core/test_exceptions.py | 432 | Yes | Yes | No |
| tests/unit/test_lab/conftest.py | 21 | Yes | No (fixtures only) | No |
| tests/unit/strategy/turn_engine/test_turn_engine_validation.py | 58 | Yes | Yes | No |
| tests/unit/fixtures/test_paths.py | 113 | Yes | Yes | No |
| tests/unit/strategy/data/test_galaxy_cleanup.py | 338 | Yes | Yes | No |
| tests/unit/tools/test_qa_launcher.py | 56 | Yes | Yes | No |
| tests/integration/strategy/production/test_queue.py | 178 | Yes | Yes | No |
| tests/unit/strategy/services/test_race_description_llm_controller.py | 469 | Yes | Yes | CAT-7 |
| tests/unit/ui/screens/test_transfer_mass_preview.py | 376 | Yes | Yes | No |
| tests/unit/strategy/facade/test_system_dto.py | 458 | Yes | Yes | No |
| tests/unit/research/test_research_service_edge_cases.py | 253 | Yes | Yes | No |
| tests/integration/strategy/test_production_rates.py | 362 | Yes | Yes | No |
| tests/unit/test_app_bootstrap_profiling.py | 140 | Yes | Yes | No |
| tests/unit/simulation/entities/stat_contributors/test_weapons.py | 57 | Yes | Yes | No |
| tests/unit/strategy/data/test_storm.py | 523 | Yes | Yes | No |
| tests/unit/workshop/test_workshop_viewmodel.py | 525 | Yes | Yes | No |
| tests/unit/strategy/fleet/test_build_order.py | 103 | Yes | Yes | No |
| tests/unit/strategy/services/test_fleet_navigation_invalidate_paths.py | 61 | Yes | Yes | No |
| tests/unit/strategy/validation/test_colonize_validator.py | 1283 | Yes | Yes | No |
| tests/unit/simulation/combat/test_beam_hit_tracking.py | 101 | Yes | Yes | No |
| tests/unit/ui/screens/test_fleet_context_menu_position.py | 53 | Yes | Yes | No |
| tests/unit/tools/test_agent_skill_prefix_renamer.py | 303 | Yes | Yes | No |
| tests/unit/simulation/components/abilities/test_ability_base.py | 934 | Yes | Yes | No |
| tests/unit/systems/test_main_integration.py | 86 | Yes | Yes | No |
| tests/unit/strategy/engine/test_order_processor_no_legacy_helpers.py | 91 | Yes | Yes | No |
| tests/unit/ui/screens/test_workshop_event_router_select_component.py | 91 | Yes | Yes | CAT-11 |
| tests/unit/ui/screens/test_workshop_viewmodel_layer_ops.py | 155 | Yes | Yes | No |
| tests/unit/strategy/services/test_planet_economy_projector.py | 703 | Yes | Yes | No |
| tests/integration/strategy/test_stabilizer_blocks_superweapon.py | 342 | Yes | Yes | No |
| tests/integration/strategy/test_superweapon_integration.py | 633 | Yes | Yes | No |
| tests/unit/ui/panels/test_component_modifier_grid_panel.py | 323 | Yes | Yes | No |
| tests/unit/strategy/services/test_effect_ability_display.py | 41 | Yes | Yes | No |
| tests/unit/strategy/services/test_task_group_suggester.py | 185 | Yes | Yes | No |
| tests/unit/strategy/data/test_bay_inventory.py | 105 | Yes | Yes | No |
| tests/unit/strategy/turn_engine/test_turn_engine_end_of_turn_order.py | 169 | Yes | Yes | No |
| tests/unit/ui/panels/test_design_report_panel.py | 312 | Yes | Yes | CAT-11 |
| tests/integration/ui/test_fleet_ops_facade.py | 326 | Yes | Yes | No |

## Context Usage Estimate

All 91 files read. ~24,255 LOC reviewed. Total findings: 20 (9 MAJOR, 11 MINOR). No CRITICAL findings (CAT-1/2/3/13). The shard is predominantly high-quality integration and characterization tests. Main improvement vectors: parametrization opportunity (CAT-10 in 3 large test files), fixture scope optimization (CAT-5 in 4 conftest files), and a few mocking-brittleness patches (CAT-6 in 4 files).
