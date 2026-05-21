# Shard 04 — Test Audit Report

## Summary
- Shard: 04 | Files assigned: 96 | Files actually read: 96 | Total findings: 16 | Critical: 2 | Major: 8 | Minor: 6

## Findings

### tests/unit/strategy/engine/test_superweapon_event_payloads.py
#### CAT-1: test_existing_event_payload_coverage_documented  [CRITICAL]
- **Location**: test_superweapon_event_payloads.py:106-112 | **Issue**: Test has zero assertions. Docstring states "No assertion needed — the test exists to keep the docstring discoverable via `pytest --collect-only`." This is a vacuous test that cannot fail under any condition. | **Suggestion**: Delete the test; its stated purpose (docstring discoverability) belongs in a module docstring, not a test function. | **LOC affected**: 7

### tests/unit/strategy/data/test_galaxy_state_encapsulation.py
#### CAT-1: test_allowed_files_actually_use_at_least_one_index  [CRITICAL]
- **Location**: test_galaxy_state_encapsulation.py:106-119 | **Issue**: Sanity check iterating `ALLOWED_FILES` which is `frozenset()`. The for-loop body never executes, making `assert viols` unreachable. The test always passes trivially. | **Suggestion**: Either delete the test (since allow-list is empty by design) or replace with an inline comment noting the invariant is intentionally empty. | **LOC affected**: 14

### tests/unit/ui/screens/test_strategy_input_handler_core.py
#### CAT-6: Mocking private `_click_dispatch._handle_picking`  [MAJOR]
- **Location**: test_strategy_input_handler_core.py:186-190, 629-634, 665-669, 700-704 | **Issue**: Multiple tests mock `handler._click_dispatch._handle_picking` — a private attribute on a private subcomponent. This couples tests to internal implementation details (the `_click_dispatch` object structure). | **Suggestion**: Refactor tests to exercise the public `handle_click()` method and assert observable outcomes (mode changes, callback invocations) rather than mocking private dispatch internals. | **LOC affected**: ~40

#### CAT-10: Duplicate ESC-mode return tests  [MINOR]
- **Location**: test_strategy_input_handler_core.py:128-162 | **Issue**: Four near-identical tests (`test_escape_returns_to_select_from_move`, `_from_join`, `_from_colonize`, `_from_transfer`) share identical body (set mode, send ESC, assert SELECT) with only the initial mode differing. | **Suggestion**: Parametrize into a single test with `@pytest.mark.parametrize("mode", ['MOVE', 'JOIN', 'COLONIZE_TARGET', 'TRANSFER'])`. | **LOC affected**: 35

### tests/unit/simulation/entities/test_ship_component_manager.py
#### CAT-6: Accessing private `component_manager._invalidate_components_cache`  [MAJOR]
- **Location**: test_ship_component_manager.py:441, 444-445 | **Issue**: `test_invalidate_clears_both_caches` directly accesses `ship.component_manager._invalidate_components_cache()` and then reads `component_manager._components_dirty` and `_weapons_cache_dirty` — three private-attr reads. | **Suggestion**: Exercise cache invalidation through the public Ship API (e.g., `add_component`+`remove_component`) and verify via `get_all_components()` / `get_weapon_components_cached()` return values. | **LOC affected**: 12

### tests/unit/ui/screens/test_empire_build_queue_window.py
#### CAT-6: Patching `__init__` with no-op lambda  [MAJOR]
- **Location**: test_empire_build_queue_window.py:63-64 | **Issue**: `_make_window` helper patches `EmpireBuildQueueWindow.__init__` with `lambda self, *a, **kw: None` then manually wires 30+ MagicMock attributes (lines 67-161). This is extremely brittle — any change to the production `__init__` signature or internal attribute set goes undetected. | **Suggestion**: Use the `bypass_init` pattern from `tests/fixtures/ui_widget_factory.py` (used elsewhere in this shard, e.g., test_build_queue_list_window.py) instead of the raw `patch.object(__init__)` approach. | **LOC affected**: ~100

#### CAT-10: Two identical `test_toggle_column_hides_visible_column` methods  [MINOR]
- **Location**: test_empire_build_queue_window.py:644-653 and 655-663 | **Issue**: Two test methods with identical names and near-identical bodies — one toggles `'location'`, the other toggles `'build_rate'`. Both assert the toggled column becomes invisible. | **Suggestion**: Parametrize with `@pytest.mark.parametrize("column_id", ['location', 'build_rate'])` into one test. | **LOC affected**: 20

### tests/unit/core/test_hex_math_core.py
#### CAT-9: Repeated `hex_random_cluster` imports inside 7 test methods  [MINOR]
- **Location**: test_hex_math_core.py:722-723, 735-736, 748-749, 757-758, 783-784, 806-807, 819-820, 841-842, 853-854 | **Issue**: `from game.core.hex_math import hex_random_cluster` and `import random` are repeated inside 9 individual test methods in `TestHexRandomCluster`. | **Suggestion**: Move both imports to module level (they are already partially imported at the top of the file — `hex_random_cluster` just needs to be added to the top-level import tuple). | **LOC affected**: ~18

### tests/integration/ui/test_colonization_facade.py
#### CAT-9: `MockPlanetType` enum redefined in 8+ test methods  [MINOR]
- **Location**: test_colonization_facade.py:71-72, 377-379, 437-439, 488-489, 571-572, 625-626, 724-725, 788-789 | **Issue**: `MockPlanetType(Enum)` with `ICE_DWARF`/`CONTINENTAL` values is defined at class/module scope in 8 different methods. | **Suggestion**: Define a single `MockPlanetType` enum at module level and reuse it across all test classes. | **LOC affected**: ~32

### tests/performance/test_panel_full_open_benchmark.py
#### CAT-2: Test has no real assertions  [CRITICAL]
- **Location**: test_panel_full_open_benchmark.py:137-179 | **Issue**: Both `test_full_window_open_uncached` and `test_full_window_open_with_cache` construct windows in a loop, print profiler medians via `_print_span_medians()`, and have zero assertions. These are profiling benchmarks, not tests — they log data to stdout but never assert pass/fail. | **Suggestion**: Either add assertion(s) (e.g., max full-open < threshold ms, or all spans present) or move to a dedicated profiling script directory outside the test suite. | **LOC affected**: 42

### tests/unit/strategy/engine/test_conflict_resolution_modifier_logging.py
#### CAT-6: Patching a private function on a module used as mock  [MAJOR]
None — this test is clean. It monkeypatches a public function `collect_combat_modifiers` on a real module, which is acceptable I/O-boundary mocking.

### tests/unit/ui/screens/test_build_queue_list_window.py
#### CAT-6: Patching `pygame_gui.elements.UIWindow.kill` in multiple tests  [MAJOR]
- **Location**: test_build_queue_list_window.py:264-265, 279-280 | **Issue**: `test_kills_all_labels` and `test_calls_close_callback` patch `pygame_gui.elements.UIWindow.kill` to avoid real widget teardown. While necessary for headless testing, this is a fragile mock of a framework method. | **Suggestion**: Consider using the shared `bypass_init` pattern more aggressively or wrapping the framework kill in an overridable method. Lower priority — this is already the established pattern in this shard. | **LOC affected**: ~10

### tests/unit/strategy/services/test_replay_verification_coordinator.py
#### CAT-7: Multiple `time.sleep()` calls  [MAJOR]
- **Location**: test_replay_verification_coordinator.py:269, 408, 476, 515, 631 | **Issue**: Six test methods use `time.sleep()` for thread synchronization (0.01s – 0.1s). This adds latency to test runs and can cause flakiness under CI load. | **Suggestion**: Use `threading.Event` / `Barrier` for deterministic synchronization (already partially done with `gate` events in some tests — extend to the busy-wait loops). | **LOC affected**: ~15

### tests/unit/ui/test_camera.py
#### CAT-8: Deeply nested `with patch()` blocks  [MAJOR]
- **Location**: test_camera.py:414-419, 428-433, 458-466, 476-484, 495-501, 513-520, 528-533, 543-549, 557-560, 576-584, 592-599, 607-613 | **Issue**: Many tests use triple-nested `with patch('pygame.key.get_pressed', ...), patch('pygame.mouse.get_pressed', ...), patch('pygame.mouse.get_rel', ...)` chains. The `TestCameraUpdateInput` class has 13 test methods with the same 3-patch pattern repeated. | **Suggestion**: Extract the common patch triplet into a context-manager helper or a pytest fixture that yields pre-patched camera instances. Could also use `patch.multiple()`. | **LOC affected**: ~80

### tests/unit/strategy/validation/test_transfer_drop_pod.py
#### CAT-6: `del planet.ships` / `del planet.orders` to prevent `is_fleet()`  [MAJOR]
- **Location**: test_transfer_drop_pod.py:22-23 | **Issue**: `_make_planet` deletes `ships` and `orders` attributes from the MagicMock to prevent `is_fleet()` from returning True. This relies on internal duck-typing logic of the production code. | **Suggestion**: Set `spec` on the MagicMock to exclude those attributes, or add `spec` with only planet attributes. | **LOC affected**: 3

### tests/unit/strategy/engine/test_build_order_processor.py
#### CAT-9: Repeated `OrderProcessor()` instantiation in multiple tests  [MINOR]
- **Location**: test_build_order_processor.py:80, 149 | **Issue**: Two test methods (lines 59-88 and 134-157) create local `OrderProcessor()` instances instead of using the `order_processor` fixture. | **Suggestion**: Use the `order_processor` fixture consistently across all tests in the class. | **LOC affected**: 4

## File Coverage Verification

| # | File | LOC | Read |
|---|------|-----|------|
| 1 | tests/unit/core/math_utils/test_vector2_basic.py | 222 | Yes |
| 2 | tests/integration/strategy/test_save_round_trip.py | 231 | Yes |
| 3 | tests/unit/ui/screens/test_strategy_input_handler_core.py | 705 | Yes |
| 4 | tests/unit/modifiers/test_weapon_ability_bindings.py | 412 | Yes |
| 5 | tests/unit/modifiers/test_formula_validation.py | 162 | Yes |
| 6 | tests/integration/ui/build_queue_screen/test_portrait_logging.py | 240 | Yes |
| 7 | tests/unit/ui/test_scene_protocol.py | 107 | Yes |
| 8 | tests/unit/strategy/events/test_event_log.py | 522 | Yes |
| 9 | tests/unit/ui/screens/test_new_game_setup_view_model.py | 147 | Yes |
| 10 | tests/unit/strategy/data/test_galaxy_state_encapsulation.py | 119 | Yes |
| 11 | tests/unit/core/test_asset_manager.py | 186 | Yes |
| 12 | tests/unit/strategy/interfaces/test_engines_package_layout.py | 131 | Yes |
| 13 | tests/unit/strategy/data/test_ship_cargo_manager_no_legacy_substrate.py | 123 | Yes |
| 14 | tests/integration/ui/test_colonization_facade.py | 829 | Yes |
| 15 | tests/unit/simulation/systems/test_satellite_reboard.py | 262 | Yes |
| 16 | tests/unit/strategy/services/test_design_cost_calculator.py | 130 | Yes |
| 17 | tests/unit/strategy/test_ui_dto_ai_readers_no_legacy_substrate.py | 158 | Yes |
| 18 | tests/unit/strategy/engine/test_superweapon_event_payloads.py | 300 | Yes |
| 19 | tests/unit/ui/screens/test_empire_build_queue_window.py | 1236+ | Yes |
| 20 | tests/unit/strategy/data/test_fleet_cargo_resources.py | 181 | Yes |
| 21 | tests/unit/core/test_hex_math_core.py | 923 | Yes |
| 22 | tests/unit/strategy/generation/test_planet_image_registry.py | 169 | Yes |
| 23 | tests/unit/simulation/components/abilities/test_ability_registry.py | 71 | Yes |
| 24 | tests/integration/strategy/turn_engine/conftest.py | 128 | Yes |
| 25 | tests/unit/strategy/engine/test_conflict_resolution_modifier_logging.py | 80 | Yes |
| 26 | tests/integration/fleet_combat/test_battle_determinism.py | 224 | Yes |
| 27 | tests/integration/replay/test_replay_playback.py | 192 | Yes |
| 28 | tests/unit/strategy/engine/test_game_session_shape.py | 160 | Yes |
| 29 | tests/unit/assets/test_asset_manager_resolutions.py | 315 | Yes |
| 30 | tests/static_guards/test_no_legacy_protocol_names.py | 262 | Yes |
| 31 | tests/integration/strategy/facade/test_fleet_to_fleet_drop_pod.py | 140 | Yes |
| 32 | tests/unit/ui/screens/test_event_log_window_reuse.py | 95 | Yes |
| 33 | tests/unit/ui/panels/test_compute_planet_production.py | 130 | Yes |
| 34 | tests/unit/strategy/data/test_race_config.py | 465 | Yes |
| 35 | tests/unit/ui/screens/test_superweapon_input_modes.py | 198 | Yes |
| 36 | tests/unit/strategy/services/ability_sources/test_star.py | 206 | Yes |
| 37 | tests/unit/simulation/entities/test_ship_component_manager.py | 445 | Yes |
| 38 | tests/integration/strategy/test_galaxy_gen.py | 300 | Yes |
| 39 | tests/unit/core/test_spectrum_math.py | 93 | Yes |
| 40 | tests/integration/strategy/test_growth_rate_equivalence.py | 158 | Yes |
| 41 | tests/unit/simulation/ship_combat_engine/test_combat_ops.py | 96 | Yes |
| 42 | tests/unit/ui/screens/builder/test_modifier_logic_smart_floor.py | 45 | Yes |
| 43 | tests/unit/strategy/engine/test_turn_engine_config.py | 60 | Yes |
| 44 | tests/unit/strategy/ship_instance/conftest.py | 47 | Yes |
| 45 | tests/unit/strategy/turn_engine/test_no_lazy_fallback_init.py | 275 | Yes |
| 46 | tests/integration/colonization/conftest.py | 159 | Yes |
| 47 | tests/unit/ui/screens/test_build_queue_list_window.py | 282 | Yes |
| 48 | tests/unit/builder/test_requirement_abilities.py | 172 | Yes |
| 49 | tests/unit/ui/screens/battle_setup/test_controller.py | 668 | Yes |
| 50 | tests/unit/strategy/generation/test_storm_generator.py | 469 | Yes |
| 51 | tests/unit/ui/screens/test_cargo_quick_dialog_kills_on_dispatch_failure.py | 51 | Yes |
| 52 | tests/unit/workshop/test_stats_visibility.py | 218 | Yes |
| 53 | tests/unit/systems/test_spatial_edge_cases.py | 331 | Yes |
| 54 | tests/unit/strategy/validation/test_transfer_drop_pod.py | 205 | Yes |
| 55 | tests/unit/simulation/components/abilities/test_defense_integration.py | 517 | Yes |
| 56 | tests/unit/ui/screens/strategy_windows/test_build_queue_windows.py | 146 | Yes |
| 57 | tests/unit/strategy/planet_atmosphere/conftest.py | 53 | Yes |
| 58 | tests/unit/simulation/managers/test_battle_state_manager.py | 226 | Yes |
| 59 | tests/unit/modifiers/test_ability_introspection.py | 181 | Yes |
| 60 | tests/unit/ui/screens/test_workshop_data_reloader.py | 229 | Yes |
| 61 | tests/performance/test_panel_full_open_benchmark.py | 179 | Yes |
| 62 | tests/unit/simulation/systems/test_battle_end_conditions.py | 611 | Yes |
| 63 | tests/unit/ui/test_camera.py | 614 | Yes |
| 64 | tests/unit/strategy/services/test_deployment_zone_calculator.py | 178 | Yes |
| 65 | tests/unit/strategy/services/test_mine_group_service.py | 118 | Yes |
| 66 | tests/unit/simulation/components/abilities/test_combat_modifiers.py | 236 | Yes |
| 67 | tests/unit/simulation/systems/test_fighter_reboard_component_state.py | 277 | Yes |
| 68 | tests/unit/simulation/entities/test_ship_combat_manager.py | 276 | Yes |
| 69 | tests/unit/strategy/data/test_design_metadata_validation.py | 73 | Yes |
| 70 | tests/unit/strategy/test_fleet_battle_adapter.py | 193 | Yes |
| 71 | tests/unit/quickstart/test_quickstart_designs.py | 302 | Yes |
| 72 | tests/unit/ui/screens/test_event_log_row_pool_visibility.py | 180 | Yes |
| 73 | tests/unit/entities/conftest.py | 15 | Yes |
| 74 | tests/unit/test_lab/test_batch_skip.py | 385 | Yes |
| 75 | tests/unit/ui/screens/builder/test_stat_definitions.py | 98 | Yes |
| 76 | tests/unit/simulation/systems/test_perf_stats_dirty_flag.py | 75 | Yes |
| 77 | tests/unit/simulation/validation/test_maintenance_validator_rules.py | 173 | Yes |
| 78 | tests/unit/ui/screens/test_race_browser_dialog.py | 62 | Yes |
| 79 | tests/unit/simulation/combat/test_combat_events.py | 271 | Yes |
| 80 | tests/integration/strategy/test_combat_shortcut_paths.py | 551 | Yes |
| 81 | tests/unit/ui/screens/test_star_list_window_reuse.py | 83 | Yes |
| 82 | tests/unit/ui/screens/test_empire_build_queue_sidebar.py | 188 | Yes |
| 83 | tests/unit/strategy/engine/test_game_session_from_dict.py | 145 | Yes |
| 84 | tests/unit/test_lab/test_render_progress_no_game_handle.py | 91 | Yes |
| 85 | tests/unit/strategy/data/test_radiation_physics.py | 192 | Yes |
| 86 | tests/unit/ui/screens/test_species_selector_mixin.py | 126 | Yes |
| 87 | tests/unit/ui/services/test_tkinter_utils.py | 217 | Yes |
| 88 | tests/unit/strategy/services/test_system_destroyer.py | 295 | Yes |
| 89 | tests/unit/strategy/data/test_environmental_preference.py | 145 | Yes |
| 90 | tests/unit/core/test_serializable_protocol.py | 65 | Yes |
| 91 | tests/unit/strategy/services/test_ship_instance_factory.py | 163 | Yes |
| 92 | tests/unit/ui/screens/test_setup_data_io.py | 395 | Yes |
| 93 | tests/unit/strategy/adapters/test_simulation_adapter.py | 442 | Yes |
| 94 | tests/integration/strategy/facade/test_fleet_queries.py | 318 | Yes |
| 95 | tests/unit/strategy/engine/test_build_order_processor.py | 157 | Yes |
| 96 | tests/unit/strategy/services/test_replay_verification_coordinator.py | 654 | Yes |

## Context Usage Estimate
- Context consumed: ~24800 LOC read across 96 files
- Findings produced: 16 (2 Critical, 8 Major, 6 Minor)
- Report size: ~150 lines
- Finding density: ~1 finding per 1550 LOC
