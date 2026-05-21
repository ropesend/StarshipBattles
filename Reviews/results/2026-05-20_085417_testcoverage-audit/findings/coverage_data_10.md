# Coverage Data — Shard 10

**Coverage source:** heuristic
**File count:** 43 | **LOC estimate:** 9597
**Tiers:** 0=7 1=1 2=29 3=6

**Note:** All data below is HEURISTIC — import-based name-grep matching. NOT proof of coverage.

### game/core/profiling.py (Tier 2: TIER_2_PARTIAL, 149 LOC, layer: core)
- Total symbols: 15 | Heuristically tested: 12
- Candidate test files (8):
  - tests/unit/core/profiling/conftest.py
  - tests/unit/core/profiling/test_decorators.py
  - tests/unit/core/profiling/test_persistence.py
  - tests/unit/core/profiling/test_singleton_threading.py
  - tests/unit/core/test_application_context.py
  - tests/unit/core/test_profiling_edge_cases.py
  - tests/unit/performance/test_profiler_perf.py
  - tests/unit/test_app_bootstrap_profiling.py
- Heuristically untested symbols (3):
  - get_default_profiler
  - Profiler.__init__
  - wrapper

### game/core/roles.py (Tier 2: TIER_2_PARTIAL, 247 LOC, layer: core)
- Total symbols: 14 | Heuristically tested: 11
- Candidate test files (5):
  - tests/unit/combat_lab/test_scenario_role_registry.py
  - tests/unit/core/test_role.py
  - tests/unit/core/test_role_registry.py
  - tests/unit/strategy/data/test_design_role_registry_invalidation.py
  - tests/unit/strategy/data/test_design_role_registry_loader.py
- Heuristically untested symbols (3):
  - RoleRegistry.__contains__
  - RoleRegistry._role_from_dict
  - RoleRegistry._fire_invalidation_callbacks

### game/core/state_machine.py (Tier 2: TIER_2_PARTIAL, 146 LOC, layer: core)
- Total symbols: 7 | Heuristically tested: 6
- Candidate test files (1):
  - tests/unit/core/test_state_machine.py
- Heuristically untested symbols (1):
  - ScreenStateMachine.__init__

### game/simulation/combat/families/projectile.py (Tier 0: TIER_0_NO_TESTS, 58 LOC, layer: simulation)
- Total symbols: 2 | Heuristically tested: 0
- Candidate test files: NONE (Tier 0)
- Heuristically untested symbols (2):
  - ProjectileHandler
  - ProjectileHandler.fire

### game/simulation/combat/telemetry.py (Tier 2: TIER_2_PARTIAL, 372 LOC, layer: simulation)
- Total symbols: 15 | Heuristically tested: 13
- Candidate test files (20):
  - tests/unit/combat_lab/services/test_ab_battle_runner.py
  - tests/unit/combat_lab/test_spec_compiler.py
  - tests/unit/simulation/battle_controller/test_outcome_emission.py
  - tests/unit/simulation/combat/test_hit_log_modifier_trace.py
  - tests/unit/simulation/combat/test_hit_log_recorder.py
  - tests/unit/simulation/combat/test_ship_stats_aggregator.py
  - tests/unit/simulation/combat/test_telemetry.py
  - tests/unit/simulation/combat/test_weapon_summary_aggregator.py
  - ... and 12 more
- Heuristically untested symbols (2):
  - ShipStatsAggregator._on_damage_event
  - HitLogRecorder._on_hit_event

### game/simulation/projectile_manager.py (Tier 3: TIER_3_APPARENTLY_COVERED, 187 LOC, layer: simulation)
- Total symbols: 10 | Heuristically tested: 10
- Candidate test files (3):
  - tests/unit/engine/collision_edge_cases/conftest.py
  - tests/unit/simulation/combat/test_weapon_dispatch_golden.py
  - tests/unit/simulation/test_projectile_manager.py

### game/simulation/replay/replay_serialization.py (Tier 2: TIER_2_PARTIAL, 634 LOC, layer: simulation)
- Total symbols: 39 | Heuristically tested: 14
- Candidate test files (3):
  - tests/unit/simulation/replay/test_replay_verifier.py
  - tests/unit/simulation/replay/test_serialization.py
  - tests/unit/simulation/test_battle_runner_component_hp.py
- Heuristically untested symbols (25):
  - _vec_to_list
  - _entry_vector_to_dict
  - _entry_vector_from_dict
  - _combat_policies_to_dict
  - _combat_policies_from_dict
  - _ship_spec_to_dict
  - _ship_spec_from_dict
  - _squadron_spec_to_dict
  - _squadron_spec_from_dict
  - _task_force_spec_to_dict
  - _task_force_spec_from_dict
  - _team_spec_to_dict
  - _team_spec_from_dict
  - _modifier_application_to_dict
  - _modifier_application_from_dict
  - ... and 10 more

### game/simulation/replay/replay_spec.py (Tier 0: TIER_0_NO_TESTS, 197 LOC, layer: simulation)
- Total symbols: 10 | Heuristically tested: 0
- Candidate test files: NONE (Tier 0)
- Heuristically untested symbols (10):
  - ReplayShipSpec
  - _capture_ships_in_team
  - walk
  - ReplaySpec
  - ReplaySpec.from_battle_spec
  - ReplaySpec.to_battle_spec
  - ReplaySpec.iter_ship_snapshots
  - ReplaySpec.to_dict
  - ReplaySpec.from_dict
  - _strip_instance_snapshots

### game/simulation/systems/battle_logger.py (Tier 0: TIER_0_NO_TESTS, 84 LOC, layer: simulation)
- Total symbols: 8 | Heuristically tested: 0
- Candidate test files: NONE (Tier 0)
- Heuristically untested symbols (8):
  - BattleLogger
  - BattleLogger.__init__
  - BattleLogger.__enter__
  - BattleLogger.__exit__
  - BattleLogger.__del__
  - BattleLogger.start_session
  - BattleLogger.log
  - BattleLogger.close

### game/strategy/data/fleet_consumable_aggregator.py (Tier 2: TIER_2_PARTIAL, 355 LOC, layer: strategy)
- Total symbols: 20 | Heuristically tested: 15
- Candidate test files (1):
  - tests/unit/strategy/data/test_fleet_consumable_aggregator.py
- Heuristically untested symbols (5):
  - FleetConsumableAggregator.__init__
  - FleetConsumableAggregator._accumulate_ship_costs
  - FleetConsumableAggregator.get_fleet_pod_capacity
  - FleetConsumableAggregator.get_fleet_pod_mass_used
  - FleetConsumableAggregator._distribute_cargo_to_fleet

### game/strategy/data/galaxy_system_generator.py (Tier 3: TIER_3_APPARENTLY_COVERED, 354 LOC, layer: strategy)
- Total symbols: 13 | Heuristically tested: 13
- Candidate test files (2):
  - tests/unit/strategy/data/test_galaxy_system_generator.py
  - tests/unit/strategy/data/test_intrinsic_rng_determinism.py

### game/strategy/data/race_point_budget.py (Tier 2: TIER_2_PARTIAL, 212 LOC, layer: strategy)
- Total symbols: 13 | Heuristically tested: 10
- Candidate test files (3):
  - tests/unit/strategy/data/test_race_point_budget_v2.py
  - tests/unit/strategy/test_race_randomizer.py
  - tests/unit/ui/screens/test_race_validator.py
- Heuristically untested symbols (3):
  - RacePointBudget.__init__
  - RacePointBudget._iter_paid_aptitudes
  - RacePointBudget.get_aptitude_breakdown

### game/strategy/data/ship_cargo_manager.py (Tier 2: TIER_2_PARTIAL, 463 LOC, layer: strategy)
- Total symbols: 27 | Heuristically tested: 18
- Candidate test files (4):
  - tests/unit/strategy/ship_instance/test_cargo_forwarder_removal.py
  - tests/unit/strategy/test_managers_phase_3b.py
  - tests/unit/strategy/test_ship_cargo_manager.py
  - tests/unit/ui/screens/test_fleet_report_filters.py
- Heuristically untested symbols (9):
  - _BaySlot
  - _BaySlot.accepts
  - ShipCargoManager.__init__
  - ShipCargoManager._enumerate_bays
  - ShipCargoManager._assign_carried_to_bays
  - ShipCargoManager._allowed_vehicle_types
  - ShipCargoManager.can_accept_vehicle
  - ShipCargoManager.load_vehicle
  - ShipCargoManager.unload_vehicle

### game/strategy/data/spatial_index.py (Tier 2: TIER_2_PARTIAL, 185 LOC, layer: strategy)
- Total symbols: 10 | Heuristically tested: 7
- Candidate test files (2):
  - tests/unit/strategy/data/test_spatial_index.py
  - tests/unit/strategy/generation/test_placement_strategies.py
- Heuristically untested symbols (3):
  - SpatialIndex.__init__
  - SpatialIndex._get_cell_key
  - SpatialIndex._get_nearby_cells

### game/strategy/data/species_population.py (Tier 3: TIER_3_APPARENTLY_COVERED, 43 LOC, layer: strategy)
- Total symbols: 2 | Heuristically tested: 2
- Candidate test files (21):
  - tests/unit/strategy/data/test_empire.py
  - tests/unit/strategy/data/test_planet_habitability_cache.py
  - tests/unit/strategy/data/test_population_model.py
  - tests/unit/strategy/data/test_species_population_characterization.py
  - tests/unit/strategy/engine/order_handlers/test_transfer_handler.py
  - tests/unit/strategy/engine/test_colonize_population.py
  - tests/unit/strategy/engine/test_empire_economy_calculator.py
  - tests/unit/strategy/engine/test_happiness_engine.py
  - ... and 13 more

### game/strategy/engine/component_activation_engine.py (Tier 2: TIER_2_PARTIAL, 136 LOC, layer: strategy)
- Total symbols: 4 | Heuristically tested: 3
- Candidate test files (3):
  - tests/unit/strategy/engine/test_component_activation_engine.py
  - tests/unit/strategy/engine/test_engine_validation.py
  - tests/unit/strategy/turn_engine/test_turn_engine_lazy_properties.py
- Heuristically untested symbols (1):
  - ComponentActivationEngine._tick_facility

### game/strategy/engine/minefield_balance.py (Tier 2: TIER_2_PARTIAL, 191 LOC, layer: strategy)
- Total symbols: 9 | Heuristically tested: 5
- Candidate test files (2):
  - tests/unit/simulation/systems/test_tactical_mine_resolver.py
  - tests/unit/strategy/engine/test_minefield_resolver.py
- Heuristically untested symbols (4):
  - MinefieldBalance.sensitivity_factor
  - _from_dict
  - load_minefield_balance
  - reset_minefield_balance_cache

### game/strategy/engine/order_handlers/superweapons.py (Tier 2: TIER_2_PARTIAL, 101 LOC, layer: strategy)
- Total symbols: 5 | Heuristically tested: 4
- Candidate test files (1):
  - tests/unit/strategy/engine/order_handlers/test_superweapon_dispatch.py
- Heuristically untested symbols (1):
  - SuperweaponHandlerAdapter.__init__

### game/strategy/engine/superweapon_order_processor.py (Tier 2: TIER_2_PARTIAL, 506 LOC, layer: strategy)
- Total symbols: 16 | Heuristically tested: 8
- Candidate test files (7):
  - tests/unit/strategy/engine/order_handlers/test_handler_registry_completeness.py
  - tests/unit/strategy/engine/test_superweapon_edge_cases.py
  - tests/unit/strategy/engine/test_superweapon_event_payloads.py
  - tests/unit/strategy/engine/test_superweapon_order_pop_matrix.py
  - tests/unit/strategy/engine/test_superweapon_order_processor.py
  - tests/unit/strategy/engine/test_superweapon_order_processor_gaps.py
  - tests/unit/strategy/engine/test_superweapon_stabilizers.py
- Heuristically untested symbols (8):
  - SuperweaponResult
  - SuperweaponOrderProcessor.__init__
  - SuperweaponOrderProcessor._get_empire_mutator
  - SuperweaponOrderProcessor._get_nav_service
  - SuperweaponOrderProcessor._finalize_superweapon
  - SuperweaponOrderProcessor.execute_superweapon
  - SuperweaponOrderProcessor._get_system_at_hex
  - SuperweaponOrderProcessor._stabilizer_target_label

### game/strategy/engine/turn_state_snapshot.py (Tier 3: TIER_3_APPARENTLY_COVERED, 142 LOC, layer: strategy)
- Total symbols: 4 | Heuristically tested: 4
- Candidate test files (2):
  - tests/unit/strategy/engine/test_restore_path_parity.py
  - tests/unit/strategy/turn_engine/test_turn_state_snapshot.py

### game/strategy/facade/dto/colony_demographic_view.py (Tier 3: TIER_3_APPARENTLY_COVERED, 95 LOC, layer: strategy)
- Total symbols: 3 | Heuristically tested: 3
- Candidate test files (3):
  - tests/unit/strategy/facade/test_colony_demographic_view.py
  - tests/unit/ui/panels/test_planet_report_panel.py
  - tests/unit/ui/screens/test_strategy_detail_fmt.py

### game/strategy/facade/dto/container_snapshot.py (Tier 0: TIER_0_NO_TESTS, 54 LOC, layer: strategy)
- Total symbols: 2 | Heuristically tested: 0
- Candidate test files: NONE (Tier 0)
- Heuristically untested symbols (2):
  - ContainerSnapshotInfo
  - ContainerSnapshotInfo.mass_remaining

### game/strategy/facade/slices/planet_slice.py (Tier 2: TIER_2_PARTIAL, 246 LOC, layer: strategy)
- Total symbols: 10 | Heuristically tested: 6
- Candidate test files (2):
  - tests/unit/strategy/facade/slices/test_planet_slice.py
  - tests/unit/strategy/facade/test_container_snapshots.py
- Heuristically untested symbols (4):
  - PlanetSlice.__init__
  - PlanetSlice.build_planet_index
  - PlanetSlice.get_planet
  - _planet_staging_yard_snapshot

### game/strategy/interfaces/engines/production.py (Tier 0: TIER_0_NO_TESTS, 62 LOC, layer: strategy)
- Total symbols: 2 | Heuristically tested: 0
- Candidate test files: NONE (Tier 0)
- Heuristically untested symbols (2):
  - IProductionEngine
  - IProductionEngine.process_construction_tick

### game/strategy/services/design_cost_calculator.py (Tier 2: TIER_2_PARTIAL, 143 LOC, layer: strategy)
- Total symbols: 4 | Heuristically tested: 2
- Candidate test files (2):
  - tests/unit/strategy/engine/test_production_repro.py
  - tests/unit/strategy/services/test_design_cost_calculator.py
- Heuristically untested symbols (2):
  - DesignCostCalculator._apply_cost_multiplier
  - DesignCostCalculator._calculate_inline_cost

### game/strategy/services/design_validator.py (Tier 2: TIER_2_PARTIAL, 155 LOC, layer: strategy)
- Total symbols: 9 | Heuristically tested: 7
- Candidate test files (2):
  - tests/unit/quickstart/test_quickstart_designs.py
  - tests/unit/strategy/services/test_design_validator.py
- Heuristically untested symbols (2):
  - DesignValidator._check_layer_mass
  - DesignValidator._check_components_exist

### game/ui/components/filters/tri_state_widget.py (Tier 2: TIER_2_PARTIAL, 128 LOC, layer: ui)
- Total symbols: 8 | Heuristically tested: 5
- Candidate test files (1):
  - tests/unit/ui/components/filters/test_tri_state_widget.py
- Heuristically untested symbols (3):
  - TriStateFilterWidget.__init__
  - TriStateFilterWidget.check_pressed
  - TriStateFilterWidget._update_visuals

### game/ui/components/table/column_manager.py (Tier 2: TIER_2_PARTIAL, 176 LOC, layer: ui)
- Total symbols: 12 | Heuristically tested: 10
- Candidate test files (4):
  - tests/unit/ui/components/table/test_column_manager.py
  - tests/unit/ui/components/table/test_header.py
  - tests/unit/ui/components/table/test_virtual_table.py
  - tests/unit/ui/screens/test_event_log_window.py
- Heuristically untested symbols (2):
  - TableColumnManager.is_column_visible
  - TableColumnManager.get_toggleable_columns

### game/ui/interfaces/__init__.py (Tier 0: TIER_0_NO_TESTS, 25 LOC, layer: ui)
- Total symbols: 0 | Heuristically tested: 0
- Candidate test files: NONE (Tier 0)

### game/ui/panels/strategy_widgets.py (Tier 2: TIER_2_PARTIAL, 191 LOC, layer: ui)
- Total symbols: 7 | Heuristically tested: 6
- Candidate test files (1):
  - tests/unit/ui/panels/test_strategy_widgets.py
- Heuristically untested symbols (1):
  - DataGraph.__init__

### game/ui/renderer/game_renderer.py (Tier 2: TIER_2_PARTIAL, 171 LOC, layer: ui)
- Total symbols: 2 | Heuristically tested: 1
- Candidate test files (2):
  - tests/unit/ui/conftest.py
  - tests/unit/ui/renderer/test_game_renderer.py
- Heuristically untested symbols (1):
  - scale

### game/ui/research/research_controls.py (Tier 2: TIER_2_PARTIAL, 475 LOC, layer: ui)
- Total symbols: 13 | Heuristically tested: 1
- Candidate test files (1):
  - tests/unit/research/research_controls/conftest.py
- Heuristically untested symbols (12):
  - ResearchControlPanel
  - ResearchControlPanel._create_ui
  - ResearchControlPanel.handle_event
  - ResearchControlPanel.update_selected_node
  - ResearchControlPanel.clear_selection
  - ResearchControlPanel.update_budget_display
  - ResearchControlPanel._toggle_auto_spread
  - ResearchControlPanel._update_auto_spread_button
  - ResearchControlPanel._update_allocation_slider_range
  - ResearchControlPanel.update_turn_log
  - ResearchControlPanel.clear_log
  - ResearchControlPanel.reset

### game/ui/screens/build_queue_list_window.py (Tier 2: TIER_2_PARTIAL, 224 LOC, layer: ui)
- Total symbols: 12 | Heuristically tested: 7
- Candidate test files (2):
  - tests/unit/ui/screens/test_build_queue_list_window.py
  - tests/unit/ui/screens/test_sub_window_hotkeys.py
- Heuristically untested symbols (5):
  - BuildQueueRow
  - BuildQueueRowCollector._rows_from_owner
  - BuildQueueListUiBuilder
  - BuildQueueListWindow.rebuild_list
  - BuildQueueListWindow.process_event

### game/ui/screens/empire_build_queue_filter_manager.py (Tier 3: TIER_3_APPARENTLY_COVERED, 242 LOC, layer: ui)
- Total symbols: 10 | Heuristically tested: 10
- Candidate test files (3):
  - tests/unit/ui/screens/test_build_queue_data_source.py
  - tests/unit/ui/screens/test_empire_build_queue_filter_manager.py
  - tests/unit/ui/screens/test_empire_build_queue_window.py

### game/ui/screens/planet_abilities_window.py (Tier 2: TIER_2_PARTIAL, 278 LOC, layer: ui)
- Total symbols: 6 | Heuristically tested: 3
- Candidate test files (1):
  - tests/unit/ui/screens/test_planet_abilities_window_lifecycle.py
- Heuristically untested symbols (3):
  - PlanetAbilitiesUiBuilder
  - PlanetAbilitiesUiBuilder.build
  - PlanetAbilitiesWindow.process_event

### game/ui/screens/race_browser_dialog.py (Tier 2: TIER_2_PARTIAL, 338 LOC, layer: ui)
- Total symbols: 11 | Heuristically tested: 8
- Candidate test files (2):
  - tests/unit/ui/screens/test_race_browser_dialog.py
  - tests/unit/ui/test_race_browser_dialog.py
- Heuristically untested symbols (3):
  - RaceBrowserDialogUiBuilder
  - RaceBrowserDialogUiBuilder.build
  - RaceBrowserDialog._render_row_surface

### game/ui/screens/star_list_filter_manager.py (Tier 2: TIER_2_PARTIAL, 85 LOC, layer: ui)
- Total symbols: 5 | Heuristically tested: 2
- Candidate test files (1):
  - tests/unit/ui/screens/test_star_list_window.py
- Heuristically untested symbols (3):
  - StarListFilterManager.toggle_type
  - StarListFilterManager.set_all_types
  - StarListFilterManager.get_filter_state

### game/ui/screens/strategy_build_queue_manager.py (Tier 2: TIER_2_PARTIAL, 338 LOC, layer: ui)
- Total symbols: 10 | Heuristically tested: 8
- Candidate test files (3):
  - tests/unit/ui/screens/test_strategy_build_queue_manager.py
  - tests/unit/ui/screens/test_strategy_screen_composition.py
  - tests/unit/ui/screens/test_viewing_empire_anchor.py
- Heuristically untested symbols (2):
  - StrategyBuildQueueManager._design_catalog_for_empire
  - StrategyBuildQueueManager._active_theme_id

### game/ui/screens/strategy_fleet_command_router.py (Tier 2: TIER_2_PARTIAL, 328 LOC, layer: ui)
- Total symbols: 10 | Heuristically tested: 9
- Candidate test files (1):
  - tests/unit/ui/screens/test_strategy_fleet_command_router.py

### game/ui/screens/strategy_game_state_manager.py (Tier 2: TIER_2_PARTIAL, 580 LOC, layer: ui)
- Total symbols: 15 | Heuristically tested: 12
- Candidate test files (2):
  - tests/unit/ui/screens/test_strategy_game_state_manager.py
  - tests/unit/ui/screens/test_strategy_screen_composition.py
- Heuristically untested symbols (3):
  - StrategyGameStateManager.__init__
  - StrategyGameStateManager._iter_snapshot_windows
  - StrategyGameStateManager._restore_incoming_player_state

### game/ui/screens/strategy_render/overlay.py (Tier 0: TIER_0_NO_TESTS, 52 LOC, layer: ui)
- Total symbols: 1 | Heuristically tested: 0
- Candidate test files: NONE (Tier 0)
- Heuristically untested symbols (1):
  - draw_processing_overlay

### game/ui/screens/test_lab/details/__init__.py (Tier 1: TIER_1_NO_SYMBOLS_TESTED, 13 LOC, layer: ui)
- Total symbols: 0 | Heuristically tested: 0
- Candidate test files (1):
  - tests/unit/test_lab/test_test_run_details_public_api.py

### game/ui/screens/transfer_grid_renderer.py (Tier 2: TIER_2_PARTIAL, 436 LOC, layer: ui)
- Total symbols: 12 | Heuristically tested: 8
- Candidate test files (2):
  - tests/unit/ui/screens/test_transfer_grid_renderer.py
  - tests/unit/ui/screens/test_transfer_mass_preview.py
- Heuristically untested symbols (4):
  - TransferGridRenderer._add_row
  - TransferGridRenderer.update_mass_preview
  - TransferDialogUiBuilder
  - TransferDialogUiBuilder.build
