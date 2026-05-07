# Test Suite Review -- Final Report

## Executive Summary
- Total tests reviewed: ~14,689 across 1,044 files
- Tests recommended for removal (validated): 160+ individual tests across 68 files (LOC: ~5,800)
- Tests flagged as happy-path-only: 78
- Source files with inadequate coverage: 52
- Cross-domain duplicates found: 28 distinct duplicate clusters
- Potential production bugs found: 5

---

## 1. Validated Removals (by priority)

### HIGH confidence (confirmed by validator)

#### TESTS_NOTHING_REAL -- Reimplemented Local Logic (zero game imports)
These files define local functions mimicking production logic and test those copies. They never import from `game.*` and provide zero regression protection.

| File | LOC | Validator |
|------|-----|-----------|
| `tests/unit/ui/battle_state_viewer/test_json_diff.py` | 347 | V3 |
| `tests/unit/ui/battle_state_viewer/test_ui_logic.py` | 178 | V3 |
| `tests/unit/ui/battle_state_viewer/test_viewer_ui.py` | 236 | V3 |
| `tests/unit/ui/test_lab_scene/test_logic.py` | 493 | V3 |
| `tests/unit/ui/test_lab_scene/test_rendering.py` | 361 | V3 |
| `tests/unit/ui/test_lab_scene/test_ui_components.py` | 306 | V3 |
| `tests/unit/ui/schematic_view/test_geometry.py` | 357 | V3 |
| `tests/unit/ui/schematic_view/test_rendering_logic.py` | 324 | V3 |
| `tests/unit/ui/left_panel/test_bulk_add.py` | 165 | V3 |
| `tests/unit/ui/left_panel/test_selection_hover.py` | 144 | V3 |
| `tests/unit/ui/left_panel/test_sorting_filtering.py` | 280 | V3 |
| **Subtotal** | **3,191** | |

#### TESTS_NOTHING_REAL -- Set-Then-Assert / Over-Mocked
| File | Tests to remove | LOC | Validator |
|------|----------------|-----|-----------|
| `tests/unit/ui/screens/test_workshop_screen_integration.py` | Entire file | 250 | V3 |
| `tests/unit/ui/screens/test_galaxy_test_screen.py` | Init/FPS/Camera attr tests | 140 | V3 |
| `tests/unit/ui/panels/test_design_report_panel.py` | Init + ShowPlaceholder (12 tests) | 150 | V3 |
| `tests/unit/ui/panels/test_planet_report_panel.py` | Init + UpdatePlanet (11 tests) | 120 | V3 |
| `tests/unit/ui/panels/test_design_stats_panel.py` | StatCalc + Formatting + RowsMap + LayerStatus | 110 | V3 |
| `tests/unit/ui/screens/test_strategy_screen.py` | 3 boundary tests (set-then-assert) | 25 | V3 |
| `tests/unit/strategy/data/test_ship_pod_storage.py` | Entire file (tests mock lambdas) | 74 | V2 |
| `tests/repro_issues/test_bug_14_multi_planet_offset.py` | Entire file (local arithmetic) | 337 | V4 |
| `tests/repro_issues/test_bug_16_raw_data_button.py` | Entire file (local math + inspect.getsource) | 64 | V4 |
| `tests/repro_issues/test_bug_17_drag_preview.py` | Entire file (inspect.getsource) | 62 | V4 |
| `tests/repro_issues/test_crash_planet_list.py` | Entire file (tests local MockPlanetListWindow) | 43 | V4 |
| `tests/integration/strategy/test_strategy_scene.py` | TestTurnManagement (2 tests, local lambdas) | 43 | V2 |
| `tests/integration/strategy/test_strategy_scene.py` | test_colonize_command_queues (tests Fleet.add_order) | 30 | V2 |
| **Subtotal** | | **~1,448** | |

#### TESTS_NOTHING_REAL -- Source-Text Matching (inspect.getsource)
| File | Tests | LOC | Validator |
|------|-------|-----|-----------|
| `tests/unit/ui/screens/test_strategy_renderer.py` | 2 getsource tests | 15 | V3 |
| `tests/unit/ui/screens/test_strategy_ui_menu.py` | 4 getsource tests | 30 | V3 |
| `tests/unit/ui/screens/test_planet_selection_window.py` | 2 getsource tests | 20 | V3 |
| **Subtotal** | | **65** | |

#### SCAFFOLD_ONLY
| File | Tests | LOC | Validator |
|------|-------|-----|-----------|
| `tests/unit/core/test_protocols.py` | TestProtocolExistence (A6) + TestPROJ193ProtocolImports (A7) | 58 | V1 |
| `tests/unit/strategy/interfaces/test_engine_interfaces.py` | Entire file (ABC mechanics) | 476 | V2 |
| `tests/unit/simulation/systems/test_ship_stats_phase_ordering.py` | Entire file (2 hasattr tests) | 22 | V1 |
| `tests/unit/simulation/systems/test_ship_stats_calculator_phases.py` | 5 hasattr helper tests | 25 | V1 |
| `tests/unit/simulation/combat/test_battle_mode_handlers.py` | 6 interface-existence tests | 16 | V1 |
| `tests/unit/simulation/components/test_component_constants.py` | 6 hasattr enum tests | 30 | V1 |
| `tests/unit/strategy/adapters/test_simulation_adapter.py` | Import tests (2 tests) | 12 | V2 |
| `tests/unit/strategy/adapters/test_simulation_adapter.py` | Implementation tests (3 tests) | 24 | V2 |
| `tests/unit/strategy/interfaces/test_battle_resolver.py` | ~7 import/structural tests | 55 | V2 |
| 11 files with import-only scaffold tests | 1 test each | ~60 | V3 |
| `tests/unit/ui/mocks/__init__.py` | Dead empty module | 8 | V3 |
| `tests/unit/_verify_builder_imports.py` | Dead standalone script | 20 | V4 |
| `tests/projects/test_extract_phase.py` | 5 placeholder `pass` tests | 18 | V4 |
| **Subtotal** | | **~824** | |

#### DUPLICATE
| File | Tests | LOC | Validator |
|------|-------|-----|-----------|
| `tests/unit/builder/test_builder_data_loader.py` | Entire file (dup of workshop/) | 192 | V3 |
| `tests/unit/builder/test_builder_viewmodel.py` | ~12 core tests (dup of workshop/) | 300 | V3 |
| `tests/unit/builder/test_workshop_context_di.py` | 3 overlapping tests | 70 | V3 |
| `tests/unit/builder/test_workshop_viewmodel_di.py` | Entire file | 105 | V3 |
| `tests/unit/ui/screens/builder/test_mandatory_modifiers.py` | Entire file (dup of ownership) | 40 | V3 |
| `tests/unit/ui/test_superweapon_operations.py` | Init + property + error-path tests | 165 | V3 |
| `tests/unit/ui/screens/test_strategy_renderer_animation.py` | 3 elapsed-time tests | 20 | V3 |
| `tests/unit/ui/test_rendering_logic.py` | 4 duplicate rendering tests | 50 | V3 |
| `tests/unit/ai/test_ai_controller_edge_cases.py` | EngageDistance (6 tests) | 50 | V1 |
| `tests/unit/ai/test_ai_controller_edge_cases.py` | CapabilitiesCache (4 tests) | 60 | V1 |
| `tests/unit/simulation/combat/test_battle_mode_handlers.py` | TestModeCharacteristics (4 tests) | 34 | V1 |
| `tests/unit/simulation/ship_combat_engine/test_combat_ops.py` | Facade unit tests (partial) | 210 | V1 |
| `tests/unit/research/test_research_tracker_edge_cases.py` | Entire file | 149 | V4 |
| `tests/unit/abilities/test_colonize_planet.py` | Entire file (dup of test_colonize_harvester) | 180 | V4 |
| `tests/integration/strategy/test_hex_math_strategy.py` | Entire file (dup of core hex) | 97 | V2 |
| `tests/integration/strategy/test_commands.py` | 4 command class tests + 1 empty pass test | 100 | V2 |
| `tests/integration/strategy/production/test_queue.py` | Empty pass test | 15 | V2 |
| `tests/integration/colonization/test_validation.py` | Entire file (thin passthrough) | 86 | V4 |
| `tests/integration/strategy/test_colonize_logic.py` | 3 pod consumption + 4 validation tests | 185 | V4 |
| `tests/unit/strategy/engine/test_process_colonize_cargo.py` | 4 duplicate tests | 85 | V4 |
| `tests/unit/strategy/engine/test_fleet_order_transfer.py` | TestExecuteLoad + TestExecuteUnload (10 mock tests) | 162 | V4 |
| `tests/unit/strategy/engine/test_fleet_order_transfer.py` | TestTransferResult (2 tests) | 20 | V2 |
| `tests/unit/strategy/test_fleet_order_processor.py` | 3 dataclass tests | 35 | V4 |
| `tests/unit/strategy/test_fleet_order_processor.py` | TestOrderProcessorCreation (1 test) | 10 | V4 |
| `tests/integration/strategy/production/test_fleet_production_e2e.py` | 2 movement blocking + 1 save/load | 82 | V4 |
| **Subtotal** | | **~2,522** | |

#### TRIVIAL_CONSTANT
| File | Tests | LOC | Validator |
|------|-------|-----|-----------|
| `tests/unit/core/test_config.py` | 4 pure value equality tests | 50 | V1 |
| `tests/unit/core/test_constants.py` | 2 import/float scaffold tests + 3 subsumable tests | 40 | V1 |
| `tests/unit/core/test_error_codes.py` | TestErrorCodeCategories (subsumed by MinimumSet) | 12 | V1 |
| `tests/unit/entities/test_ship.py` | test_constant_exists (DEFAULT_MAX_MASS) | 4 | V1 |
| `tests/unit/entities/test_ship_stat_querier.py` | TestShipStatQuerierInitialization (2 tests) | 20 | V1 |
| `tests/unit/strategy/engine/test_commands.py` | TestCommandType (2 tests) | 8 | V2 |
| `tests/unit/strategy/engine/test_commands.py` | test_with_origin_hex (1 test) | 5 | V2 |
| `tests/unit/strategy/engine/test_planet_energy_cache.py` | test_cached_values_reused | 13 | V2 |
| `tests/unit/strategy/events/test_event_types.py` | 13 constant-equality tests + 2 count tests | 42 | V2 |
| `tests/unit/strategy/engine/test_fleet_order_transfer.py` | TestTransferResult defaults | 20 | V2 |
| `tests/integration/strategy/test_fleet_movement.py` | test_fleet_initialization | 5 | V2 |
| `tests/unit/ui/screens/test_strategy_renderer_animation.py` | 2 rotation constant tests | 10 | V3 |
| `tests/unit/ui/screens/test_camera_navigator.py` | Method existence test | 3 | V3 |
| `tests/unit/ui/screens/test_keybindings_scene.py` | GameState constant test | 5 | V3 |
| `tests/unit/ui/screens/test_menu_scene.py` | BG_COLOR constant test | 5 | V3 |
| `tests/unit/strategy/generation/density/test_geometric.py` | `assert d1 != d2 or True` (always passes) | 11 | V2 |
| `tests/unit/strategy/generation/density/test_spiral_arm.py` | `assert d1 != d2 or True` (always passes) | 12 | V2 |
| **Subtotal** | | **~265** | |

#### DUPLICATE -- Repro Issues Now Covered by Proper Unit Tests
| File | LOC | Validator |
|------|-----|-----------|
| `tests/repro_issues/test_bug_01_crew_delay.py` | 113 | V4 |
| `tests/repro_issues/test_bug_02_seeker.py` | 37 | V4 |
| `tests/repro_issues/test_bug_03_validation.py` | 104 | V4 |
| `tests/repro_issues/test_bug_05_logistics.py` | 108 | V4 |
| `tests/repro_issues/test_bug_05_rejected_fix.py` | 91 | V4 |
| `tests/repro_issues/test_bug_05_deep_repro.py` | 157 | V4 |
| `tests/repro_issues/test_bug_06_combat_propulsion.py` | 147 | V4 |
| `tests/repro_issues/test_bug_07_crash.py` | 59 | V4 |
| `tests/repro_issues/test_bug_08_fuel_validation.py` | 59 | V4 |
| `tests/repro_issues/test_bug_09_endurance.py` | 80 | V4 |
| `tests/repro_issues/test_bug_10_logistics_update.py` | 112 | V4 |
| `tests/unit/test_builder_refactor.py` | 36 | V4 |
| `tests/unit/performance/reproduce_scaling.py` | 41 | V4 |
| **Subtotal** | | **~1,144** | |

### MEDIUM confidence (confirmed or downgraded but still removable)

| File | Tests | LOC | Notes |
|------|-------|-----|-------|
| `tests/unit/core/test_combat_types.py` | test_slots | 4 | Downgraded to MEDIUM |
| `tests/unit/simulation/components/test_modifier_manager.py` | 3 deprecated static tests | 37 | Remove with deprecated prod code |
| `tests/unit/strategy/engine/test_build_order_command_handler.py` | 4 IssueBuildOrderCommand tests | 24 | Downgraded; not dup of test_commands but trivial |
| `tests/unit/strategy/engine/test_fleet_order_transfer.py` | 3 validation tests | 56 | Dup of test_transfer_order.py |
| `tests/unit/ai/test_controllable_adapter.py` | TestMockImplementation | 100 | Keep TestIControllableAbstractContract |
| `tests/unit/ai/test_ai_controller_edge_cases.py` | TestScoreAndSort (2 tests) | 40 | Evaluation failure test has some unique value |
| `tests/integration/strategy/facade/test_empire_dto.py` | 3 frozen tests | 45 | Python feature, not logic |
| `tests/integration/strategy/facade/test_fleet_dto.py` | 3 frozen tests | 40 | Python feature, not logic |
| `tests/integration/strategy/facade/test_system_dto.py` | 4 frozen tests | 50 | Python feature, not logic |
| `tests/unit/strategy/engine/test_superweapon_handler_validation.py` | 5 direct-handler "rejects" tests | 100 | Keep the 10 "passes_component_registry" tests |
| `tests/repro_issues/test_bug_12_energy_gen.py` | Entire file | 110 | Cross-cutting value; V4 downgraded to LOW |
| `tests/unit/strategy/data/test_production_rates.py` | TestProductionRatesJson | 54 | Data file contract; V2 downgraded |
| `tests/unit/ui/screens/test_strategy_menu_panel.py` | 3 count/label tests | 25 | Keep uniqueness + panel sizing |
| **Subtotal** | | **~685** | |

### Rejected claims (reviewer was wrong)

| Claim | File | Why it should stay |
|-------|------|-------------------|
| DI source-reading tests | `test_ship_component_manager_di.py` | Guards real architectural constraint (PROJ-252 DI compliance) |
| Component getters/ops | `tests/unit/entities/ship_helpers/` | Substantial unique coverage not in simulation/ tests |
| Formation integrity adapter | `test_ai_controller_interface.py` | Tests documented bug fix with distinct adapter code path |
| Colonize validator consolidation | `test_colonize_validator.py` | 1247 LOC is thorough edge case testing, not duplication |
| TestEventQueries duplicate | `test_strategy_session_facade.py` | Claimed duplicate file does not exist |
| Empire fleet ID tests | `tests/integration/strategy/test_empire.py` | Includes real serialization round-trip test |
| Roman numerals | `tests/integration/strategy/test_naming.py` | Only test of to_roman() in codebase (relocate, don't delete) |
| Font constants | `tests/unit/ui/test_fonts.py` | Guards against silent rendering breaks |
| Production rates unit/integration | Two test_production_rates.py files | Test entirely different things (data vs calculation) |

---

## 2. Happy-Path-Only Tests (by priority)

### HIGH priority (critical source code)

| Area | What's missing | Source |
|------|---------------|--------|
| `component_loader.py` (64.2% cov) | Error paths: missing file, malformed JSON, cache hits, DI guards | S1-agent2 |
| `order_processor.py` fleet-to-fleet transfers | `_execute_fleet_transfer` (lines 379-396) has zero coverage | S2-agent2 |
| `order_processor.py` staging yard pods | `_load_pod_from_staging_yard`, `_unload_pod_to_staging_yard` zero coverage | S2-agent2 |
| `DamageCalculator` event emissions | No test passes event_bus; SHIELD_HIT, COMPONENT_DESTROYED events untested | S1-agent3 |
| `FleetAuraManager` (79.3% cov) | `get_active_bonuses()` untested, external config modifiers untested | S1-agent3 |
| `FormulaEvaluator` (85.5% cov) | Comparison operators, ternary, list/tuple literals, security-critical paths | S1-agent1 |
| `StrategySessionFacade` dispatch helpers | All 26 `dispatch_*` methods (UI-to-engine mutation path) zero coverage | S2-agent4 |
| `FleetInfo` order conversion | COLONIZE, MOVE_TO_FLEET, JOIN_FLEET, TRANSFER DTO conversions untested | S2-agent4 |
| `design_validator.py` `_check_layer_mass` | Entire method (60 lines, 33% of file) untested | S2-agent3 |
| `dump_crash_snapshot` | Debugging lifeline with zero test coverage (both success and error) | S2-agent2 |
| `turn_state_snapshot.py` restore | Fleet re-registration and order reference resolution partially tested | S2-agent2 |
| `order_serializer.py` colonize_params | Colonize serialization format completely untested | S1-data |
| `ErraticBehavior` (AI) | Entire class (66 lines) has zero unit tests; leash constraint critical | S1-agent4 |
| `transfer_dialog.py` (75.4% cov) | Transfer exceeding capacity, zero-amount, error from facade | S3-agent1 |
| `strategy_game_state_manager.py` | Exception during process_turn, auto-save failure | S3-agent1 |

### MEDIUM priority

| Area | What's missing | Source |
|------|---------------|--------|
| `ship_layer_manager.py` | `migrate_components=True` path (lines 152-166) untested | S1-agent2 |
| `ship_design_stats.py` | Toggle filtering and damage application branches | S1-agent2 |
| `VehicleDesignService` | Exception handling in add_component, validate_design internal path | S1-agent3 |
| `SimulationDesignLoader` (69.6%) | Data validation and unexpected error branches | S1-agent3 |
| `combat_utils.py` IControllable paths | IControllable isinstance branches never triggered in tests | S1-agent4 |
| `fleet_consumable_aggregator.py` | `load_cargo_to_fleet()`, `unload_cargo_from_fleet()`, `get_capability_summary()` untested | S1-data |
| `planet_action_engine.py` (82.9%) | Activate from non-INACTIVE, fallback paths in _find_target_facility | S2-agent2 |
| `planet_energy_engine.py` (83.6%) | `get_shield_info()`, `get_activatable_ability_info()` zero coverage | S2-agent2 |
| `empire_economy_calculator.py` | Ship/fleet maintenance cost calculation untested | S2-agent2 |
| `transfer_validator.py` | Fleet-to-fleet validation, passenger load edge cases | S2-agent3 |
| `strategic_ability_scanner.py` | Component activation state filtering, missing scope field | S2-agent3 |
| `action_time_resolver.py` | ACTIVATE_ABILITY / DEACTIVATE_ABILITY timing untested | S2-agent3 |
| `fleet_cargo_projector.py` (42.3%) | Entire `get_projected_cargo` method body untested | S2-agent3 |
| `homeworld_presets.py` | `apply_preset_to_config()` entire body untested | S1-data |
| `build_queue_source.py` (64.7%) | `_get_planetary_yard_size_multiplier()`, `get_build_rate_booster_mult()` | S1-data |
| Research `calculate_depth()` | No cycle guard; could stack overflow on cyclic data | S4-agent1 |
| Research `set_rp_budget` | Budget reduction does not clamp existing allocations | S4-agent1 |

---

## 3. Coverage Gaps (by priority)

### Critical (0-30% coverage, important code)

| Source file | Stmts | Coverage | Priority | Source |
|-------------|-------|----------|----------|--------|
| `planet_abilities_window.py` | 119 | 0.0% | HIGH | S3-agent1 |
| `battle_results_screen.py` | 167 | 0.0% | HIGH | S3-agent2 |
| `atmosphere_target_editor.py` | 131 | 0.0% | MEDIUM | S3-agent2 |
| `settings_window.py` | 45 | 0.0% | MEDIUM | S3-agent2 |
| `test_lab/test_run_details.py` | 610 | 5.2% | HIGH | S3-agent5 |
| `test_lab/test_run_card.py` | 237 | 5.9% | MEDIUM | S3-agent5 |
| `test_lab/renderer.py` | 663 | 6.8% | HIGH | S3-agent5 |
| `galaxy_test/system_mode.py` | 270 | 9.3% | LOW | S3-agent2 |
| `setup_renderer.py` | 100 | 10.0% | LOW | S3-agent2 |
| `galaxy_test/galaxy_mode.py` | 192 | 10.4% | LOW | S3-agent2 |
| `test_lab/results_panel.py` | 156 | 10.3% | MEDIUM | S3-agent5 |
| `test_lab/component_dropdown.py` | 82 | 11.0% | MEDIUM | S3-agent5 |
| `test_lab/screen_input_handler.py` | 186 | 11.8% | HIGH | S3-agent5 |
| `test_lab/dialogs.py` | 142 | 13.4% | MEDIUM | S3-agent5 |
| `star_list_window.py` | 259 | 13.9% | HIGH | S3-agent1 |
| `planet_order_validator.py` | 80 | 15.0% | HIGH | S2-agent3 |
| `planet_command_handlers.py` | 78 | 17.9% | HIGH | S2-agent2 |
| `planet_selection_window.py` | 73 | 17.8% | MEDIUM | S3-agent1 |
| `test_lab/ship_panels.py` | 127 | 18.1% | LOW | S3-agent5 |
| `json_diff.py` (UI utils) | 47 | 19.1% | HIGH | S3-agent3 |
| `research_controls.py` | 206 | 19.4% | LOW | S3-agent3 |
| `planet_list_window.py` | 333 | 20.7% | HIGH | S3-agent1 |
| `empire_panel_window.py` | 172 | 20.9% | HIGH | S3-agent1 |
| `galaxy_test/screen.py` | 150 | 21.3% | LOW | S3-agent2 |
| `battle_ui.py` (screens) | 121 | 21.5% | MEDIUM | S3-agent2 |
| `star_data_source.py` | 75 | 22.7% | MEDIUM | S3-agent1 |
| `scrollable_json_panel.py` | 223 | 24.2% | MEDIUM | S3-agent3 |
| `research_renderer.py` | 143 | 25.2% | LOW | S3-agent3 |
| `system_tree_panel.py` | 311 | 26.4% | MEDIUM | S3-agent1 |
| `strategy_camera_nav.py` | 96 | 27.1% | MEDIUM | S3-agent1 |
| `hit_effects.py` | 120 | 29.2% | LOW | S3-agent3 |
| `race_setup_screen.py` | 511 | 29.2% | MEDIUM | S3-agent2 |
| `battle_state_viewer.py` | 127 | 29.9% | MEDIUM | S3-agent2 |
| `fleet_selection_window.py` | 33 | 30.3% | LOW | S3-agent1 |
| `new_game_setup_screen.py` | 281 | 30.2% | HIGH | S3-agent2 |
| `weapons_renderer.py` (builder) | -- | 30.2% | MEDIUM | S3-agent4 |

### Major (30-60% coverage)

| Source file | Stmts | Coverage | Source |
|-------------|-------|----------|--------|
| `strategy_renderer.py` | 687 | 36.0% | S3-agent1 |
| `ship_detail_panel.py` | 175 | 36.6% | S3-agent3 |
| `workshop_ship_io.py` | -- | 34.5% | S3-agent4 |
| `battle_panels.py` | 333 | 39.0% | S3-agent2 |
| `strategy_event_router.py` | 211 | 40.3% | S3-agent1 |
| `fleet_cargo_projector.py` | 26 | 42.3% | S2-agent3 |
| `builder_widgets.py` | 141 | 42.6% | S3-agent3 |
| `layer_panel.py` (builder) | -- | 42.5% | S3-agent4 |
| `left_panel.py` (builder) | -- | 43.1% | S3-agent4 |
| `workshop_data_reloader.py` | -- | 43.3% | S3-agent4 |
| `weapons_panel.py` (builder) | -- | 43.9% | S3-agent4 |
| `star_list_filter_manager.py` | 19 | 47.4% | S3-agent1 |
| `ship_stats_renderer.py` | 186 | 47.8% | S3-agent3 |
| `test_lab/screen.py` | 349 | 47.3% | S3-agent5 |
| `test_lab/test_executor.py` | 235 | 49.4% | S3-agent5 |
| `modifier_row.py` (builder) | -- | 50.3% | S3-agent4 |
| `homeworld_presets.py` | 43 | 53.5% | S1-data |
| `base_gallery.py` | 92 | 54.3% | S3-agent3 |
| `workshop_event_router.py` | -- | 54.0% | S3-agent4 |
| `event_log_window.py` | 151 | 53.0% | S3-agent1 |
| `design_selector_window.py` | 204 | 57.4% | S3-agent2 |
| `race_library.py` | 132 | 57.6% | S2-agent3 |
| `interaction_controller.py` | -- | 58.0% | S3-agent4 |
| `orbital_generation_config.py` | 103 | 60.2% | S1-data |

### Minor (60-80% coverage)

| Source file | Stmts | Coverage | Source |
|-------------|-------|----------|--------|
| `component_loader.py` | 151 | 64.2% | S1-agent2 |
| `build_queue_source.py` | 167 | 64.7% | S1-data |
| `classification_config.py` | 76 | 65.8% | S1-data |
| `design_validator.py` | 119 | 67.2% | S2-agent3 |
| `game_settings.py` | 40 | 67.5% | S3-agent3 |
| `star_generation_config.py` | 63 | 68.3% | S1-data |
| `design_loader.py` | 46 | 69.6% | S1-agent3 |
| `empire_build_queue_window.py` | 258 | 70.2% | S3-agent1 |
| `galaxy_spatial_index.py` | 59 | 72.9% | S1-data |
| `turn_state_snapshot.py` | 46 | 73.9% | S2-agent2 |
| `strategy_session_facade.py` | -- | 74.7% | S2-agent4 |
| `fleet_dto.py` | -- | 75.5% | S2-agent4 |
| `battle_state.py` | 277 | 75.5% | S1-agent3 |
| `workshop_screen.py` | -- | 75.6% | S3-agent4 |
| `modifier_manager.py` | 129 | 76.7% | S1-agent2 |
| `fleet_aura_manager.py` | 150 | 79.3% | S1-agent3 |
| `layer_iterator.py` | 46 | 80.4% | S1-agent1 |
| `design_library.py` | -- | 81.0% | S2-agent4 |
| `component_inspector.py` | 103 | 82.5% | S2-agent3 |
| `planet_gen.py` | 257 | 82.5% | S1-data |
| `planet_action_engine.py` | 170 | 82.9% | S2-agent2 |
| `ship_instance.py` | 223 | 83.0% | S1-data |
| `planet_energy_engine.py` | 122 | 83.6% | S2-agent2 |

---

## 4. Cross-Domain Dedup Recommendations

### Colonization (validated by V4)
- **"Ownership transfer" tested in 6 locations:** Keep `test_process_colonize_validation.py` (unit) and `test_commands_colonization.py` (integration). Remove 4 others.
- **"Ship/fleet stays" tested in 9 locations:** Keep `test_planet_specific_colonization.py::TestFleetRemovalBehavior`. Remove 7 others.
- **"Universal drop pod" tested in 3 locations:** Remove `test_process_colonize_cargo.py::test_colonize_universal_drop_pod_succeeds`.
- **"Any planet picks first unowned" tested in 5 locations:** Keep unit + validator tests. Remove 3 integration dups.
- **`ColonizePlanet` ability class tested in 2 files:** Remove `test_colonize_planet.py`, keep `test_colonize_harvester.py`.
- **Helper duplication:** `make_colony_ship()` defined in 7 files; consolidate into shared conftest.

### Superweapons (validated by V4)
- **Init/property tests duplicated** in `test_superweapon_operations.py` vs `test_strategy_superweapons.py`. Remove former.
- **"Rejects fleet without ability" tested in 2 files:** Remove 5 direct-handler duplicates from `test_superweapon_handler_validation.py`; keep 10 unique "passes_component_registry" tests.

### Transfer Orders (validated by V4)
- **Load/unload passengers tested in mock vs real-object files:** Remove 10 mock-only tests from `test_fleet_order_transfer.py`; keep real-object tests in `test_transfer_order.py`.

### Builder/Workshop (validated by V3)
- **4 duplicate files in `tests/unit/builder/`** mirroring `tests/unit/workshop/`: Remove duplicates, migrate unique tests.

### Shared Mock Classes
- `MockGalaxy` defined in 8+ files -- consolidate into shared conftest
- `_make_shipyard()` defined in 5 files -- consolidate
- `MockGameSession` copy-pasted in 3 save_game_service test files -- consolidate into conftest

---

## 5. Production Bugs Found

### BUG-1: Shadowed `TestHullAutoEquip` class (CONFIRMED)
- **File:** `tests/unit/entities/test_ship.py` (lines 276 and 403)
- **Impact:** First class's `test_hull_auto_equip` method never executes. Python silently replaces the first class with the second.
- **Fix:** Rename the first class (e.g., `TestHullAutoEquipLegacy`) so its test runs.

### BUG-2: Shadowed `TestGameStateQueries` class (CONFIRMED)
- **File:** `tests/unit/strategy/facade/test_strategy_session_facade.py` (lines 453 and 695)
- **Impact:** `test_get_turn_number` and `test_get_human_player_ids` silently never execute.
- **Fix:** Rename one class (e.g., `TestGameStateQueriesPhase4`).

### BUG-3: `assert X or True` no-op assertions (CONFIRMED)
- **Files:** `test_geometric.py` line 86, `test_spiral_arm.py` line 78, `test_layout_loader.py` line 150
- **Impact:** These assertions always pass regardless of actual values.
- **Fix:** Remove `or True` from assertions, or rewrite with deterministic inputs.

### BUG-4: Potential `NameError` in `save_game_service.py` (UNCONFIRMED)
- **File:** `game/strategy/systems/save_game_service.py` line 463
- **Impact:** `json.JSONDecodeError` referenced but only `from json import JSONDecodeError` is imported. If the except clause triggers, it would raise `NameError: name 'json' is not defined`.
- **Fix:** Change to `except JSONDecodeError:` or add `import json`.

### BUG-5: Research budget reduction does not clamp allocations (UNCONFIRMED)
- **File:** `game/research/data/research_tracker.py` lines 206-213
- **Impact:** If budget is reduced below total allocated RP, `get_total_allocated()` can exceed budget. `get_remaining_rp()` returns 0 but UI may show inconsistent state.
- **Fix:** Add allocation clamping in `set_rp_budget()` or document as intentional.

---

## 6. Recommended Action Order

1. **Fix production bugs (BUG-1 through BUG-5)** -- highest impact, lowest risk. Shadowed test classes mean tests are silently not running. The `assert or True` bugs mean 3 tests provide zero validation. Estimated effort: 1-2 hours.

2. **Delete reimplemented-logic test files (3,191 LOC)** -- the 11 files with zero `game.*` imports. These provide false confidence and inflate test counts. No regression risk since they test no production code.

3. **Write tests for `planet_command_handlers.py` (17.9% coverage)** and `planet_order_validator.py` (15.0% coverage)** -- these are the worst-covered strategy engine files and handle user-facing planet order commands.

4. **Write tests for `component_loader.py` (64.2% coverage)** -- lowest coverage in simulation domain, critical for data loading error paths.

5. **Delete duplicate test files** -- start with the 4 `tests/unit/builder/` files duplicating `tests/unit/workshop/`, then the colonization duplicates. Estimated 2,500 LOC removal.

6. **Write tests for `battle_results_screen.py` (0% coverage)** -- user-facing screen shown after every battle.

7. **Write tests for `new_game_setup_screen.py` (30.2% coverage)** -- critical user-facing flow for starting new games.

8. **Delete scaffold/trivial tests** -- hasattr tests, import-only tests, enum existence checks. Low LOC per file but many files; batch cleanup.

9. **Write tests for `order_processor.py` fleet-to-fleet transfer and staging yard paths** -- production features with zero coverage.

10. **Write tests for `StrategySessionFacade` dispatch helpers** -- zero coverage on the entire UI-to-engine mutation path (26 methods).

11. **Delete repro issue files now covered by unit tests** -- 13 files, ~1,144 LOC. Verify each duplicate target exists before deletion.

12. **Consolidate shared test infrastructure** -- extract `make_colony_ship()`, `MockGalaxy`, `_make_shipyard()` into shared conftest files.

13. **Write tests for Combat Lab UI** (`test_run_details.py` at 5.2%, `renderer.py` at 6.8%) -- extract pure functions (`_format_check_pair`, `_is_condition_verified`) and test them.

14. **Write tests for `DamageCalculator` event emissions and `FleetAuraManager` gaps** -- HIGH priority simulation coverage gaps.

15. **Address colonize_validator test-to-source ratio** -- consolidate fixtures to reduce 1,247 LOC to ~700 LOC without losing coverage.

---

## 7. Statistics

- **Estimated LOC reduction from validated removals:** ~5,800 (HIGH confidence: ~5,100; MEDIUM confidence: ~700)
- **Estimated new tests needed for coverage gaps:** ~120-150 new test methods across ~25 test files
- **Current coverage:** 71.9% (36,045 / 50,128 lines)
- **Projected after improvements:** ~74-75% (conservative: removing dead tests reduces test LOC but not source coverage; adding ~150 tests for the critical/major gaps would cover an estimated 800-1,200 additional source lines, bringing coverage to roughly 73.5-74.5%)

### Breakdown by category
| Category | Files | Est. LOC |
|----------|-------|----------|
| Reimplemented local logic (zero game imports) | 11 | 3,191 |
| Set-then-assert / over-mocked | 13 groups | 1,448 |
| Source-text matching (inspect.getsource) | 3 files | 65 |
| Scaffold / dead code | ~20 items | 824 |
| Duplicate tests | 25+ groups | 2,522 |
| Trivial constants | 17 items | 265 |
| Repro issues now covered | 13 files | 1,144 |
| **Total (with overlap removed)** | | **~5,800** |

Note: Some items appear in multiple categories. The total is deduplicated -- items flagged by multiple agents/validators are counted once.
