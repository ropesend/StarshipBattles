# Shard 07 — Test Audit Report

## Summary
- Shard: 07 | Files assigned: 104 | Files actually read: 104 | Total findings: 32 | Critical: 4 | Major: 10 | Minor: 18

## Findings

### tests/unit/simulation/systems/test_tick_phases.py
#### CAT-10: `test_create_default_phases_registers_expected_names_and_priorities` / `test_same_priority_maintains_insertion_order` / `test_custom_phase_alongside_others` [MINOR]
- **Location**: test_tick_phases.py:114-124 | **Issue**: Three tests verify registry ordering with structurally identical bodies (register phases, then check `[p.name for p in registry.phases]`). | **Suggestion**: Parameterize into a single test with `@pytest.mark.parametrize`. | **LOC affected**: 25
#### CAT-2: `test_object_without_methods_fails_protocol` [CRITICAL]
- **Location**: test_tick_phases.py:105-108 | **Issue**: Test relies on `isinstance(NotAPhase(), ITickPhase)` returning False — this depends entirely on `@runtime_checkable` protocol behavior, not on any production logic. Trivial pass: only verifies Python protocol mechanics. | **Suggestion**: Remove or replace with a structural test that exercises actual phase behavior. | **LOC affected**: 4

### tests/integration/ui/test_camera_zoom.py
#### CAT-12: `test_zoom_centers_on_mouse_simulation` [MINOR]
- **Location**: test_camera_zoom.py:51-97 | **Issue**: Contains step-by-step calculation logic (world_before, new_world_at_mouse, diff computation) plus multiple assert calls that form a mathematical derivation in the test body. | **Suggestion**: Split the derivation into a helper; keep only the final invariant assertions in the test. | **LOC affected**: 47

### tests/unit/simulation/test_battle_outcome_replay_id.py
#### CAT-1: `test_battle_outcome_has_replay_id_field_default_none` [CRITICAL]
- **Location**: test_battle_outcome_replay_id.py:23-33 | **Issue**: Test creates a BattleOutcome with no replay_id kwarg and asserts `hasattr(outcome, "replay_id")` + `outcome.replay_id is None`. This cannot fail if the dataclass field exists with a None default — it exercises attribute default mechanics, not business logic. | **Suggestion**: Replace with an integration-level assertion (e.g., extract_outcome with NullCaptureSink). | **LOC affected**: 11

### tests/unit/ui/screens/test_event_log_window.py
#### CAT-8: `_make_strategy_ui` helper [MINOR]
- **Location**: test_event_log_window.py:259-306 | **Issue**: Helper patches `StrategyUI.__init__` with a no-op lambda, then manually sets 25 individual attributes to construct a partial stub. Construction setup is >80% of several test methods. | **Suggestion**: Extract to a shared fixture or builder function; reduce per-test attribute plumbing. | **LOC affected**: 48
#### CAT-6: `_make_window` bypasses `__init__` [MAJOR]
- **Location**: test_event_log_window.py:44-88 | **Issue**: Patches `EventLogWindow.__init__` with a lambda no-op then manually wires 10+ attributes. This mocks the constructor — an internal implementation detail — rather than using `bypass_init` or constructing through the public API. | **Suggestion**: Use `bypass_init` context manager (already imported elsewhere in this shard) instead of `patch.object(__init__, ...)`. | **LOC affected**: 45

### tests/unit/strategy/engine/test_superweapon_order_processor.py
#### CAT-6: deep patching of `SuperweaponValidator.find_ship_with_ability` [MAJOR]
- **Location**: test_superweapon_order_processor.py:131,166,201,622,669,708,748,909,1049,1132, etc. | **Issue**: 10+ tests patch `game.strategy.engine.superweapon_order_processor.SuperweaponValidator.find_ship_with_ability` — an internal implementation detail. A refactor that changes the validator's method name or moves the find logic to a different module silently breaks these tests. | **Suggestion**: Use a mock `component_registry` that contains the expected ability so the real `find_ship_with_ability` path is exercised; or test via the processor's public `process_*` methods with a fully-configured mock fleet/ship. | **LOC affected**: ~200

### tests/unit/core/profiling/test_decorators.py
#### CAT-7: `time.sleep(0.02)` in `test_context_manager_measures_time` [MAJOR]
- **Location**: test_decorators.py:135-145 | **Issue**: Uses `time.sleep(0.02)` to create measurable elapsed time. While brief, this is a real latency call in a unit test. | **Suggestion**: Mock `time.perf_counter` to return incrementing values instead of actually sleeping. | **LOC affected**: 11

### tests/unit/strategy/engine/test_fleet_order_transfer.py
#### CAT-2: mock fixtures never exercise real SUT branches [CRITICAL]
- **Location**: test_fleet_order_transfer.py:90-118 | **Issue**: All three test_fleet_order_transfer tests use a fully-MagicMock `processor` and MagicMock `mock_fleet`/`mock_empire`/`mock_galaxy`. The SUT (`OrderProcessor.get_handler(OrderType.TRANSFER).execute_action_order`) is called on real production code, BUT the handler is looked up via `get_handler()` which routes through the real handler registry. The mock_fleet.get_current_order.return_value controls which code path executes — and all three tests set up failure paths (no order, wrong type, invalid params). These test only the handler's guard clauses against MagicMock inputs, not real transfer logic. | **Suggestion**: Add at least one test with a real ShipInstance/Fleet fixture to exercise an actual transfer computation. | **LOC affected**: 28

### tests/unit/simulation/combat/test_fleet_aura_cache.py
#### CAT-6: patches `_aggregate_ability_groups` [MAJOR]
- **Location**: test_fleet_aura_cache.py:83-88 | **Issue**: `test_uses_shared_aggregator` patches `game.simulation.combat.fleet_aura_manager._aggregate_ability_groups` — a module-private function whose signature may change on refactor. | **Suggestion**: Verify aggregation behavior through public FleetAuraManager interface (e.g., check bonus values after `initialize` with known abilities). | **LOC affected**: 6

### tests/unit/ui/screens/battle_setup/test_view_model.py
#### CAT-8: 6 identical `from game.ui.screens.battle_setup.view_model import BattleSetupViewModel` imports [MINOR]
- **Location**: test_view_model.py:14,28,35,48,61,75 | **Issue**: Every test method repeats the same import statement inside the method body. | **Suggestion**: Move the import to module level. | **LOC affected**: 6

### tests/unit/ui/screens/test_lab/test_test_run_card.py
#### CAT-11: `test_header_default_path_prioritizes_failed_validation` [MINOR]
- **Location**: test_test_run_card.py:135-151 | **Issue**: Asserts exact format strings like `"1P 1F 0W"` and `"Failed Metric:"` in blitted text. If formatting changes (e.g., spacing, label reword), this test fails even though the logic is correct. | **Suggestion**: Assert that the validation summary values are present rather than exact string format. | **LOC affected**: 17

### tests/unit/strategy/design_repository/test_save_design.py
#### CAT-11: `test_save_design_writes_file_with_metadata` [MINOR]
- **Location**: test_save_design.py:52-65 | **Issue**: Reads back the written JSON file and does an exact key-existence check (`"_metadata" in payload`). If metadata key name changes or structure evolves, this breaks. | **Suggestion**: Use DesignRepository's own `load_design_data` or `scan_designs` method to read back, or assert metadata via the DesignMetadata class rather than raw JSON. | **LOC affected**: 14

### tests/unit/strategy/engine/test_engine_validation.py
#### CAT-9: 12 near-identical engine validation test classes [MINOR]
- **Location**: test_engine_validation.py:39-319 | **Issue**: Twelve `Test*EngineValidation` classes each with identical structure: `test_valid_empires_pass` + `test_*_raises`. The helper functions `_empire()`, `_fleet()`, and the test pattern are repeated across 280 LOC. | **Suggestion**: Parameterize engine class/failure condition into a single test that iterates all engine types. | **LOC affected**: 280

### tests/unit/ui/screens/test_strategy_input_handler_transfer.py
#### CAT-9: three identical mode-test classes [MINOR]
- **Location**: test_strategy_input_handler_transfer.py:44-275 | **Issue**: Three classes (`TestStrategyInputHandlerTransfer`, `TestDropCargoMode`, `TestLoadCargoMode`) share identical test patterns (key-sets-mode, mode-left-click-opens-dialog, right-click-cancels, escape-cancels). | **Suggestion**: Parameterize by `(key, mode, direction)` tuple. | **LOC affected**: 230

### tests/unit/simulation/entities/test_ship_stats.py
#### CAT-8: extensive mock setup for single assertion [MINOR]
- **Location**: test_ship_stats.py:12-55 | **Issue**: The test file defines `_TL_ABILITY`, `_VS_ABILITY`, `_HangarComponent` class with 4 methods, and constructs a 9-attribute `MagicMock` ship — all for one test function (`test_stats_aggregation_routes_hangar_abilities_to_launch_contributor`) that makes 4 assertions. | **Suggestion**: Extract hangar setup to a fixture if more hangar-component tests are added. | **LOC affected**: 43

### tests/unit/ui/screens/test_planet_abilities_controller_scanner.py
#### CAT-10: `test_*_label` tests could be parameterized [MINOR]
- **Location**: test_planet_abilities_controller_scanner.py:121-153 | **Issue**: `test_multiple_components_with_same_ability_get_instance_labels` and `test_singleton_ability_has_empty_instance_label` test the same scanner with different component counts. | **Suggestion**: Parameterize component count and expected labels. | **LOC affected**: 32

### tests/unit/ui/screens/test_strategy_detail_formatter.py
#### CAT-8: 6-level nested `with patch()` blocks [MINOR]
- **Location**: test_strategy_detail_formatter.py:129-151 | **Issue**: `test_show_detail_with_fleet_shows_fleet_buttons` and `test_show_detail_with_fleet_having_shipyard` each have 6-level nested `with patch(...)` blocks to control type-dispatch predicates (`is_star_system`, `is_star`, `is_planet`, `is_fleet`, `is_warp_point`, `is_sector_environment`). | **Suggestion**: Use `patch.multiple` (already used in `test_show_detail_with_star_system` at line 114) to flatten all 6 patches into one context manager. | **LOC affected**: 30

### tests/integration/ui/test_event_log_replay_e2e.py
#### CAT-5: `pygame_init` fixture creates real display [MAJOR]
- **Location**: test_event_log_replay_e2e.py:21-25 | **Issue**: The `pygame_init` fixture calls `pygame.init()` and `pygame.display.set_mode((1024, 768), pygame.HIDDEN)` per test. While hidden, this is function-scoped and creates a real graphical context (expensive). | **Suggestion**: Make the fixture module-scoped since all tests share the same display dimensions and it's read-only (no per-test display state changes). | **LOC affected**: 5

### tests/integration/ui/test_build_queue_enhanced_planet_report.py
#### CAT-5: `planet_report_panel` fixture constructs real pygame_gui elements [MAJOR]
- **Location**: test_build_queue_enhanced_planet_report.py:92-112 | **Issue**: The fixture creates a real `pygame_gui.elements.UIPanel`, `PlanetReportPanel`, and nested `pygame_gui.elements.UIImage` per test function. These are heavy UI constructions. | **Suggestion**: Use module-scoped fixture with shared panel, or test the logic layer (planet report formatting) separately from the pygame_gui widget tree. | **LOC affected**: 21

### tests/regression/test_generator_crew_requirement_design.py
#### CAT-12: `test_generator_without_crew_is_inactive` / `test_generator_with_crew_is_active` [MINOR]
- **Location**: test_generator_crew_requirement_design.py:32-106 | **Issue**: Both tests contain defensive fallback logic (`if layer_key is None: ... print(f"DEBUG...")`) plus manual ship construction (creating Component objects, appending to layers, setting `.ship`). The fallback print-branch is logic in the test body. | **Suggestion**: Move the layer-key resolution to a helper; remove debug print from test. | **LOC affected**: 75

### tests/unit/strategy/data/test_group_policies.py
#### CAT-4: `test_registry_loads_from_data_file` duplicate [MAJOR]
- **Location**: test_group_policies.py:20-29 | **Issue**: `test_registry_loads_from_data_file` asserts `len(registry.targeting_policies) > 0` and same for movement/retreat. The parameterized `test_policy_registry_structural_invariants` at line 31 covers the same ground (loads registry, asserts non-zero policies per axis) with better structural assertions. Two tests verify the same code path. | **Suggestion**: Remove `test_registry_loads_from_data_file`; the parameterized version is the canonical structural test. | **LOC affected**: 10

### tests/unit/ui/screens/test_orders_window.py
#### CAT-6: `_make_window` uses `bypass_init` [MAJOR]
- **Location**: test_orders_window.py:48-59 | **Issue**: Uses `bypass_init(OrdersWindow)` to skip real construction, then passes mocked `pygame.Rect`, `MagicMock(name="ui_manager")`, etc. While `bypass_init` is the accepted pattern, the test_window_instance_* tests all operate on a window whose `__init__` never ran — so they can't catch regressions in constructor behavior. | **Suggestion**: Add at least one integration test with a real (bypass_init-free) construction to verify the full two-stage lifecycle. | **LOC affected**: 12

### tests/unit/ui/screens/builder/test_modifier_utils.py
#### CAT-9: redundant class definitions duplicated in other tests [MINOR]
- **Location**: test_modifier_utils.py:10-17 | **Issue**: `_Modifier` and `_SpecialModifier` classes are defined locally; similar stub classes appear in `test_workshop_viewmodel_selection.py` and `test_builder_selection.py`. | **Suggestion**: Extract to a shared test fixture/helper module. | **LOC affected**: 8

### tests/unit/simulation/combat/test_fleet_aura_cache.py
#### CAT-1: `test_providers_dirty_flag_exists` [CRITICAL]
- **Location**: test_fleet_aura_cache.py:44-47 | **Issue**: Asserts `hasattr(mgr, '_providers_dirty')`. A test that passes if the attribute exists and fails if renamed; cannot verify correctness of the dirty-flag logic. | **Suggestion**: Remove this attribute-existence test; the behavioral tests below (`test_update_with_no_changes_skips_recalculation`, `test_invalidate_forces_recalculation`) already validate the caching contract. | **LOC affected**: 4

### tests/unit/strategy/fleet_movement_engine/conftest.py
#### CAT-9: mock_fleet fixture duplicates across test modules [MINOR]
- **Location**: fleet_movement_engine/conftest.py:21-38 | **Issue**: The `mock_fleet` fixture defined here is nearly identical to the one in `test_fleet_order_transfer.py` (lines 21-36) — both create `MagicMock(spec=Fleet)` with similar attributes. | **Suggestion**: Consolidate into a shared conftest at a higher directory level. | **LOC affected**: 18

### tests/unit/research/research_controls/test_reset_state.py
#### CAT-6: binds real method to mock via lambda [MAJOR]
- **Location**: test_reset_state.py:30 | **Issue**: `panel.reset = lambda t, tt: rc.ResearchControlPanel.reset(panel, t, tt)` — binds the unbound production method to a MagicMock instance. This is fragile: if the method signature changes, the lambda still "works" (it accepts any args) and silently passes the wrong arguments. | **Suggestion**: Use `MagicMock(wraps=rc.ResearchControlPanel)` or test through the panel's public interface without reassigning `reset`. | **LOC affected**: 1

### tests/integration/quickstart/test_quickstart_flow.py
#### CAT-5: `full_quickstart_1p` / `full_quickstart_2p` fixtures are heavy [MAJOR]
- **Location**: test_quickstart_flow.py:19-63 | **Issue**: Both fixtures run full `GameSession` construction, `SaveGameService.save_game()`, `QuickstartBuilder.copy_quickstart_designs()`, and `QuickstartBuilder.spawn_initial_complexes()` per test. This includes filesystem I/O (save/load). | **Suggestion**: Make these fixtures module-scoped to share the expensive setup across all tests in the class. | **LOC affected**: 45

### tests/unit/strategy/planet_atmosphere/test_generation.py
#### CAT-12: `test_greenhouse_warming` with for-loop logic [MINOR]
- **Location**: test_generation.py:146-167 | **Issue**: Uses `for _ in range(20)` loop with `if "CO2" in composition` branching inside the test body. The assertion at the end has conditional logic: `assert warming_found or len(temps) == 0`. | **Suggestion**: Extract the sampling loop to a helper; assert the helper's output directly. | **LOC affected**: 22

### tests/unit/ai/test_ai_controller_interface.py
#### CAT-5: `mock_ship` fixture sets 22 attributes [MINOR]
- **Location**: test_ai_controller_interface.py:63-88 | **Issue**: The `mock_ship` fixture manually sets 22 attributes on a MagicMock to mimic a full ship object. While necessary for the adapter tests, this setup is duplicated in `test_controllable_adapter.py` (not in this shard). | **Suggestion**: Move to a shared fixture module if both files coexist. | **LOC affected**: 26

## File Coverage Verification

| File | Read | LOC |
|------|------|-----|
| tests/unit/simulation/systems/test_tick_phases.py | Yes | 180 |
| tests/integration/ui/test_camera_zoom.py | Yes | 97 |
| tests/unit/ui/screens/builder/test_modifier_utils.py | Yes | 62 |
| tests/integration/strategy/combat/test_storm_shield_interference.py | Yes | 395 |
| tests/unit/simulation/test_battle_outcome_replay_id.py | Yes | 120 |
| tests/unit/ui/screens/test_per_player_ui_state.py | Yes | 78 |
| tests/unit/strategy/save_game_service/test_error_handling.py | Yes | 500 |
| tests/unit/strategy/test_fleet_capability_calculator_di.py | Yes | 190 |
| tests/unit/strategy/combat/test_spec_compiler_formation.py | Yes | 173 |
| tests/unit/simulation/entities/test_ship_stats.py | Yes | 55 |
| tests/unit/strategy/ship_instance/test_registries_di.py | Yes | 202 |
| tests/unit/strategy/engine/order_handlers/test_base.py | Yes | 102 |
| tests/unit/ui/screens/test_planet_abilities_controller_scanner.py | Yes | 285 |
| tests/unit/tools/test_codex_ship_theme_creator_skill.py | Yes | 122 |
| tests/unit/core/profiling/test_decorators.py | Yes | 158 |
| tests/unit/ui/screens/battle_setup/test_view_model.py | Yes | 93 |
| tests/unit/ui/screens/test_lab/test_test_run_card.py | Yes | 165 |
| tests/unit/strategy/engine/test_superweapon_order_processor.py | Yes | 1248 |
| tests/unit/strategy/engine/test_fleet_order_transfer.py | Yes | 119 |
| tests/unit/simulation/combat/test_fleet_aura_cache.py | Yes | 88 |
| tests/unit/strategy/design_repository/test_save_design.py | Yes | 102 |
| tests/unit/ai/test_ai_controller_interface.py | Yes | 327 |
| tests/fixtures/test_ui_widget_factory.py | Yes | 345 |
| tests/unit/simulation/replay/test_replay_verifier.py | Yes | 307 |
| tests/integration/simulation/test_three_team_battle.py | Yes | 260 |
| tests/unit/strategy/data/test_design_role_registry_invalidation.py | Yes | 158 |
| tests/unit/simulation/test_projectile_manager.py | Yes | 1522 |
| tests/unit/ui/screens/test_orders_window.py | Yes | 215 |
| tests/fixtures/test_make_minimal_spec.py | Yes | 224 |
| tests/unit/simulation/components/test_component_clone_propagates_ship.py | Yes | 122 |
| tests/unit/ui/screens/test_event_log_window.py | Yes | 842 |
| tests/unit/data/test_data_validation.py | Yes | 248 |
| tests/unit/ui/screens/test_workshop_viewmodel_selection.py | Yes | 106 |
| tests/unit/entities/test_bridge_requirement_removal.py | Yes | 56 |
| tests/unit/strategy/data/test_ship_instance_container_views.py | Yes | 112 |
| tests/unit/strategy/data/test_fleet_capability_calculator.py | Yes | 74 |
| tests/unit/strategy/fleet_movement_engine/test_warp.py | Yes | 182 |
| tests/integration/ui/test_build_queue_enhanced_planet_report.py | Yes | 512 |
| tests/unit/ui/screens/test_builder_selection.py | Yes | 283 |
| tests/unit/core/test_paths_config.py | Yes | 198 |
| tests/unit/strategy/data/test_galaxy_planet_star_loc_ceilings.py | Yes | 119 |
| tests/unit/ui/panels/test_build_queue_drag_handler.py | Yes | 652 |
| tests/integration/test_fms_d_launch_in_battle_e2e.py | Yes | 284 |
| tests/unit/strategy/planet_atmosphere/test_generation.py | Yes | 282 |
| tests/unit/ui/test_sprite_loading.py | Yes | 66 |
| tests/integration/simulation/test_four_team_battle.py | Yes | 205 |
| tests/unit/strategy/data/test_galaxy_add_warp_point.py | Yes | 54 |
| tests/unit/ui/screens/test_transfer_controller.py | Yes | 234 |
| tests/integration/ui/test_event_log_replay_e2e.py | Yes | 208 |
| tests/integration/quickstart/test_quickstart_flow.py | Yes | 146 |
| tests/unit/strategy/adapters/test_simulation_adapter_registry_threading.py | Yes | 251 |
| tests/unit/simulation/test_battle_state_live_object_bridges.py | Yes | 535 |
| tests/unit/ui/test_sprites.py | Yes | 312 |
| tests/integration/save_load/test_reference_integrity.py | Yes | 201 |
| tests/unit/core/test_validation.py | Yes | 395 |
| tests/unit/simulation/battle_controller/test_utilities.py | Yes | 118 |
| tests/unit/core/test_resource_catalog_mass_per_unit.py | Yes | 133 |
| tests/unit/strategy/facade/slices/test_empire_slice.py | Yes | 110 |
| tests/unit/strategy/ship_instance/test_validation.py | Yes | 137 |
| tests/unit/ui/screens/test_strategy_input_handler_transfer.py | Yes | 275 |
| tests/unit/strategy/production_engine/conftest.py | Yes | 50 |
| tests/integration/strategy/test_save_round_trip_phase3.py | Yes | 42 |
| tests/unit/strategy/ship_instance/test_cargo_forwarder_removal.py | Yes | 51 |
| tests/unit/tools/test_validate_agent_surfaces.py | Yes | 1209 |
| tests/unit/strategy/test_managers_phase_3b.py | Yes | 151 |
| tests/unit/strategy/engine/test_production_resource_source_contract.py | Yes | 165 |
| tests/unit/ui/screens/test_race_validator.py | Yes | 304 |
| tests/unit/ui/test_race_theme_gallery.py | Yes | 273 |
| tests/unit/builder/test_io_interactive.py | Yes | 115 |
| tests/unit/strategy/services/test_ability_metadata_effects.py | Yes | 184 |
| tests/unit/ui/screens/test_planet_list_filter_manager.py | Yes | 305 |
| tests/unit/ui/screens/test_strategy_modal_hidden_input.py | Yes | 122 |
| tests/unit/research/research_controls/test_reset_state.py | Yes | 269 |
| tests/unit/strategy/engine/test_production_spawner_staging_yard.py | Yes | 220 |
| tests/unit/strategy/data/test_empire.py | Yes | 123 |
| tests/unit/strategy/combat/test_battle_assembly.py | Yes | 233 |
| tests/unit/strategy/fleet_movement_engine/conftest.py | Yes | 38 |
| tests/unit/strategy/fleet_movement_engine/test_characterization.py | Yes | 325 |
| tests/unit/simulation/test_battle_runner_di.py | Yes | 287 |
| tests/integration/strategy/test_galaxy_generation_storms.py | Yes | 204 |
| tests/regression/test_generator_crew_requirement_design.py | Yes | 110 |
| tests/unit/ui/screens/test_event_log_no_copy.py | Yes | 35 |
| tests/unit/fixtures/test_battle_fixtures.py | Yes | 142 |
| tests/unit/research/tech_tree/test_validation.py | Yes | 258 |
| tests/unit/core/registry/test_singleton_and_thread.py | Yes | 243 |
| tests/unit/strategy/data/test_group_policies.py | Yes | 278 |
| tests/unit/ui/interfaces/test_battle_ui.py | Yes | 352 |
| tests/repro_issues/test_bug_11_dialog_size.py | Yes | 73 |
| tests/unit/simulation/entities/test_ship_resource_stat.py | Yes | 89 |
| tests/unit/tools/test_loc_tool.py | Yes | 64 |
| tests/unit/ui/screens/test_race_setup_delegate_factory.py | Yes | 96 |
| tests/unit/core/math_utils/test_helpers.py | Yes | 153 |
| tests/unit/strategy/services/test_ability_iterator.py | Yes | 414 |
| tests/unit/test_app_delegators.py | Yes | 130 |
| tests/unit/ui/test_race_portrait_gallery.py | Yes | 337 |
| tests/unit/strategy/ship_instance/test_convenience_methods.py | Yes | 112 |
| tests/unit/services/llm/conftest.py | Yes | 87 |
| tests/unit/ui/services/battle_ui_service/conftest.py | Yes | 120 |
| tests/unit/quickstart/conftest.py | Yes | 67 |
| tests/unit/strategy/interfaces/test_engine_inheritance.py | Yes | 61 |
| tests/unit/ui/screens/test_strategy_fleet_ops.py | Yes | 187 |
| tests/unit/strategy/design_catalog/test_catalog.py | Yes | 218 |
| tests/unit/strategy/engine/test_engine_validation.py | Yes | 319 |
| tests/unit/ui/screens/test_strategy_detail_formatter.py | Yes | 400 |

## Context Usage Estimate
~65,000 tokens consumed across 104 file reads + report generation.
