# PROJ-333 — Phase 1 Checklist

Per-file characterization tests. Target: 8–15 behaviors per file × 5 engines (split into 8 test modules) ≈ **65–75 behaviors** after trimming duplicates with existing tests. Mid-point ≈ **70**.

Each item below is one test function. File-level checkboxes track per-file commit progress (one file = one commit).

---

## `tests/unit/strategy/engine/test_production_engine_queue.py` (~15 behaviors)

- [ ] File created and committed
- [ ] `test_init_raises_validation_when_registries_none`
- [ ] `test_set_current_turn_updates_field_for_habitability_cache`
- [ ] `test_process_construction_tick_validates_resource_pool_not_none`
- [ ] `test_construction_queue_paused_skips_colony_base_queue`
- [ ] `test_per_facility_pause_skips_only_that_shipyard`
- [ ] `test_fleet_without_space_shipyard_is_skipped`
- [ ] `test_fleet_pause_flag_blocks_fleet_queue_processing`
- [ ] `test_fleet_yard_count_multiplies_production_rate`
- [ ] `test_complex_only_queue_stops_on_non_complex_item`
- [ ] `test_fleet_complex_without_planet_at_hex_returns_stop`
- [ ] `test_queue_item_missing_total_cost_is_skipped_with_warning`
- [ ] `test_queue_item_not_a_dict_is_skipped`
- [ ] `test_max_queue_iterations_limits_inner_loop_to_10`
- [ ] `test_first_tick_clears_shortage_logged_flags`
- [ ] `test_habitability_multiplier_scales_production_rate_for_colony_only`

---

## `tests/unit/strategy/engine/test_production_engine_consumption.py` (~12 behaviors)

- [ ] File created and committed
- [ ] `test_check_affordability_routes_to_planet_stockpile_when_context_planet`
- [ ] `test_check_affordability_routes_to_fleet_cargo_when_context_fleet`
- [ ] `test_check_affordability_falls_back_to_empire_pool_when_no_context_type`
- [ ] `test_apply_resource_consumption_updates_resources_consumed_dict`
- [ ] `test_log_resource_shortage_picks_largest_shortfall_ratio_as_limiting`
- [ ] `test_log_resource_shortage_emitted_once_per_item_per_turn`
- [ ] `test_check_item_completion_uses_completion_epsilon`
- [ ] `test_complete_item_pops_queue_and_calls_spawner`
- [ ] `test_calculate_tick_expenditure_returns_none_for_zero_rate_required_resource`
- [ ] `test_calculate_tick_expenditure_returns_empty_for_already_complete_item`
- [ ] `test_update_turns_remaining_zero_when_no_ticks_needed`
- [ ] `test_calculate_design_cost_caches_result_in_design_data`

---

## `tests/unit/strategy/engine/test_production_spawner.py` (~13 behaviors)

- [ ] File created and committed
- [ ] `test_spawn_dispatches_complex_to_create_and_place_facility_for_colony`
- [ ] `test_spawn_dispatches_drop_pod_to_staging_yard_for_colony`
- [ ] `test_spawn_dispatches_default_ship_path_for_colony_default_type`
- [ ] `test_spawn_dispatches_to_fleet_ship_when_owner_is_fleet`
- [ ] `test_spawn_dispatches_to_fleet_complex_when_fleet_and_complex_type`
- [ ] `test_load_design_returns_empty_dict_when_no_save_path`
- [ ] `test_load_design_returns_empty_dict_when_load_fails`
- [ ] `test_spawn_ship_creates_new_fleet_with_unique_id_from_galaxy`
- [ ] `test_spawn_ship_calculates_global_location_via_system_resolution`
- [ ] `test_spawn_to_staging_yard_uses_design_data_from_item_when_present`
- [ ] `test_spawn_to_staging_yard_logs_warning_when_full`
- [ ] `test_spawn_fleet_complex_uses_target_planet_id_when_specified`
- [ ] `test_spawn_fleet_complex_falls_back_to_first_planet_when_target_id_missing`

---

## `tests/unit/strategy/consumable_management_engine/test_characterization.py` (~10 behaviors — supplements existing 3 files)

- [ ] File created and committed
- [ ] `test_init_raises_validation_when_registries_none`
- [ ] `test_validate_tick_inputs_raises_when_fleet_ships_is_none`
- [ ] `test_non_combat_capable_ship_is_skipped`
- [ ] `test_zero_cost_resource_is_skipped`
- [ ] `test_per_tick_consumption_is_one_hundredth_of_per_turn_total`
- [ ] `test_failed_consume_resource_triggers_auto_disable_and_returns_depletion`
- [ ] `test_auto_disable_handles_layers_as_list_format`
- [ ] `test_auto_disable_handles_layers_as_dict_with_components_key`
- [ ] `test_auto_disable_skips_unknown_component_id`
- [ ] `test_auto_disable_only_targets_per_turn_trigger_for_matching_resource`

---

## `tests/unit/strategy/fleet_movement_engine/test_characterization.py` (~12 behaviors — supplements existing 3 files)

- [ ] File created and committed
- [ ] `test_validate_tick_inputs_raises_when_fleet_location_is_none`
- [ ] `test_get_effective_speed_returns_base_when_no_get_system_at_location`
- [ ] `test_get_effective_speed_returns_base_when_no_system_at_hex`
- [ ] `test_get_effective_speed_returns_base_when_modifier_is_one`
- [ ] `test_get_effective_speed_floors_via_int_truncation_after_multiplier`
- [ ] `test_collect_movements_skips_action_order_fleets`
- [ ] `test_collect_movements_skips_build_order_fleets`
- [ ] `test_collect_movements_uses_tick_modulo_interval`
- [ ] `test_apply_movement_returns_stranded_when_no_movement_resources`
- [ ] `test_apply_movement_warp_blocked_when_no_capability_pops_one_order`
- [ ] `test_apply_movement_consumes_warp_resources_when_distance_gt_1`
- [ ] `test_filter_jump_past_drops_larger_fleet_on_swap_parity_with_id_tiebreak`

---

## `tests/unit/strategy/engine/test_order_processor_colonize.py` (~10 behaviors)

- [ ] File created and committed
- [ ] `test_process_colonize_returns_false_when_no_current_order`
- [ ] `test_process_colonize_returns_false_when_validation_fails`
- [ ] `test_process_colonize_resolves_any_planet_picks_first_unowned`
- [ ] `test_process_colonize_returns_false_when_no_drop_pod_in_fleet`
- [ ] `test_process_colonize_adds_colony_pops_order_and_deploys_pod`
- [ ] `test_process_colonize_seeds_stockpile_from_design_initial_stockpile`
- [ ] `test_process_colonize_logs_colony_founded_event_with_system_and_local_hex`
- [ ] `test_execute_action_order_routes_colonize_with_component_registry`
- [ ] `test_execute_action_order_logs_error_and_pops_when_colonize_missing_registry`
- [ ] `test_deploy_drop_pod_warns_and_returns_when_no_pod_found`

---

## `tests/unit/strategy/engine/test_order_processor_transfer.py` (~12 behaviors)

- [ ] File created and committed
- [ ] `test_process_transfer_returns_false_when_target_not_dict`
- [ ] `test_process_transfer_load_population_auto_resolves_colony_at_fleet_hex`
- [ ] `test_process_transfer_load_population_no_colony_returns_success_skipped`
- [ ] `test_process_transfer_target_fleet_lookup_searches_galaxy_empires`
- [ ] `test_process_transfer_target_fleet_falls_back_to_owner_empire_when_galaxy_lacks_empires_attr`
- [ ] `test_process_transfer_drop_pod_skips_location_check`
- [ ] `test_process_transfer_load_passengers_caps_by_population_count`
- [ ] `test_process_transfer_load_passengers_with_species_id_targets_specific_species`
- [ ] `test_process_transfer_unload_passengers_creates_new_species_population_when_absent`
- [ ] `test_process_transfer_load_resource_caps_by_planet_stockpile`
- [ ] `test_load_pod_from_staging_yard_iterates_in_reverse`
- [ ] `test_unload_pod_to_staging_yard_returns_count_unloaded`

---

## `tests/unit/strategy/engine/test_order_processor_instant.py` (~10 behaviors)

- [ ] File created and committed
- [ ] `test_process_instant_orders_validates_orders_not_none`
- [ ] `test_process_instant_orders_collects_only_co_located_join_fleet_candidates`
- [ ] `test_elect_canonical_merges_picks_more_ships_in_mutual_pair`
- [ ] `test_elect_canonical_merges_uses_smaller_id_tiebreak_on_equal_ships`
- [ ] `test_phase_c_skips_when_source_no_longer_in_empire_emits_absorbed_by_other_merge`
- [ ] `test_phase_c_skips_when_target_absorbed_mid_iteration_pops_stale_order`
- [ ] `test_execute_fleet_merge_logs_fleet_joined_event_with_ship_count`
- [ ] `test_process_join_fleet_pops_order_when_target_invalid_destroyed`
- [ ] `test_process_join_fleet_pops_order_when_not_at_same_location`
- [ ] `test_emit_join_cancelled_no_op_when_event_bus_none`

---

## Trimming Note

Behaviors above sum to **94** if all OrderProcessor split-files are counted separately. Trim duplicates against existing coverage during execution (`test_production_refactor.py`, `test_production_spawner_staging_yard.py`, `test_order_processor_fleet_merge.py`, the existing consumable / fleet-movement conftests + tests) to land in the **65–75** band per master plan.

## Phase 1 Exit

- [ ] All 8 test files created and committed (one commit per file).
- [ ] Full sharded suite green: `python Tools/test_sharded/test_sharded.py`.
- [ ] No production-file diffs in `game/strategy/engine/`.
- [ ] Final test count recorded in this checklist.
