# Phase 4: All Layers - MINOR Findings

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-110 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Add edge case and expansion tests for all MINOR findings across Foundation, Simulation, and Strategy layers (TCG-FND-011 through TCG-FND-021, TCG-SIM-010 through TCG-SIM-018, TCG-STR-009 through TCG-STR-015). Expected: ~95 new tests.

---

## Foundation MINOR Tasks

### Task 4.1: Vector2 Edge Cases (TCG-FND-011) [Simple]
**File:** `tests/unit/core/test_math_vector2.py` (NEW)
**Source:** `game/core/math.py` (236 LOC)
**Existing:** No unit tests for Vector2
**Tests:** `pytest tests/unit/core/test_math_vector2.py`

__getitem__ / __len__:
- [ ] `test_getitem_index_0_returns_x` - v[0] == v.x
- [ ] `test_getitem_index_1_returns_y` - v[1] == v.y
- [ ] `test_getitem_index_2_raises_index_error` - v[2] raises IndexError
- [ ] `test_len_returns_2` - len(v) == 2

normalize:
- [ ] `test_normalize_zero_vector_returns_zero` - Vector2(0,0).normalize() == Vector2(0,0)
- [ ] `test_normalize_unit_vector_unchanged` - Already unit-length stays same

rotate:
- [ ] `test_rotate_negative_angle` - rotate(-90) correct
- [ ] `test_rotate_360_returns_original` - rotate(360) ~= original
- [ ] `test_rotate_720_returns_original` - rotate(720) ~= original

angle_to:
- [ ] `test_angle_to_right` - (0,0).angle_to((1,0)) == 0
- [ ] `test_angle_to_up` - (0,0).angle_to((0,-1)) == -90 (screen coords)
- [ ] `test_angle_to_same_point` - angle_to self is 0

as_int_tuple:
- [ ] `test_as_int_tuple_truncates` - (1.9, 2.1) -> (1, 2)
- [ ] `test_as_int_tuple_negative` - (-0.5, -1.7) -> (0, -1)

**Estimated tests: ~14**

---

### Task 4.2: Logger Module Unit Tests (TCG-FND-012) [Simple]
**File:** `tests/unit/core/test_logger.py` (NEW)
**Source:** `game/core/logger.py` (109 LOC)
**Existing:** No unit tests
**Tests:** `pytest tests/unit/core/test_logger.py`

Note: Must mock `Paths.BATTLE_LOG` and `os.makedirs` to avoid file I/O.

Singleton:
- [ ] `test_logger_singleton_same_instance` - Logger() is Logger()
- [ ] `test_logger_reset_creates_new_instance` - After reset(), new instance

Enabled flag:
- [ ] `test_set_enabled_false_suppresses_logs` - Messages not logged when disabled
- [ ] `test_set_enabled_true_allows_logs` - Messages logged when enabled

Module-level functions:
- [ ] `test_log_debug_delegates` - log_debug() calls _logger.log()
- [ ] `test_log_info_delegates` - log_info() calls _logger.info()
- [ ] `test_log_warning_delegates` - log_warning() calls _logger.warning()
- [ ] `test_log_error_delegates` - log_error() calls _logger.error()

Event handler:
- [ ] `test_set_event_handler_registers_callback` - Callback stored
- [ ] `test_log_event_calls_handler` - Handler invoked with event_type and kwargs
- [ ] `test_log_event_no_handler_no_crash` - No handler registered -> no error
- [ ] `test_log_event_handler_exception_caught` - Exception in handler -> logged, not raised

**Estimated tests: ~12**

---

### Task 4.3: Profiling Error Paths (TCG-FND-013) [Simple]
**File:** `tests/unit/core/test_profiling_edge_cases.py` (NEW)
**Source:** `game/core/profiling.py` (180 LOC)
**Existing:** `tests/unit/core/test_recording.py`, `tests/unit/core/test_persistence.py`
**Tests:** `pytest tests/unit/core/test_profiling_edge_cases.py`

save_history error paths:
- [ ] `test_save_history_no_records_skips` - Empty records -> no file write
- [ ] `test_save_history_io_error` - Mock save_json to return False -> logged
- [ ] `test_save_history_appends_to_existing` - Existing history gets new session appended

profile_action decorator:
- [ ] `test_profile_action_inactive_no_record` - Profiler inactive -> function runs, no record
- [ ] `test_profile_action_active_records` - Profiler active -> record created
- [ ] `test_profile_action_exception_still_records` - Function raises -> duration still recorded

profile_block context manager:
- [ ] `test_profile_block_inactive_no_record` - Inactive -> no recording
- [ ] `test_profile_block_active_records` - Active -> records duration

**Estimated tests: ~8**

---

### Task 4.4: Validation Boundary Tests (TCG-FND-014) [Simple]
**File:** `tests/unit/core/test_validation_edge_cases.py` (NEW)
**Source:** `game/core/validation.py` (184 LOC)
**Existing:** `tests/unit/core/test_validation.py`
**Tests:** `pytest tests/unit/core/test_validation_edge_cases.py`

ValidationResult edge cases:
- [ ] `test_init_with_none_errors_defaults_to_list` - errors=None -> []
- [ ] `test_init_with_none_warnings_defaults_to_list` - warnings=None -> []
- [ ] `test_message_property_empty_errors` - No errors -> ""
- [ ] `test_message_property_first_error` - Returns errors[0]
- [ ] `test_add_error_with_error_code_enum` - ErrorCode enum converted to string value
- [ ] `test_add_error_second_code_ignored` - First code wins, second add_error code skipped
- [ ] `test_merge_valid_into_invalid` - Valid merged into invalid stays invalid
- [ ] `test_merge_invalid_into_valid` - Invalid merged into valid becomes invalid
- [ ] `test_create_factory_empty_message` - create(True, "") -> no errors in list

validation_result convenience function:
- [ ] `test_validation_result_with_message` - Creates result with message in errors
- [ ] `test_validation_result_no_message` - Creates valid result with empty errors

**Estimated tests: ~11**

---

### Task 4.5: Error Codes Enum Coverage (TCG-FND-015) [Simple]
**File:** `tests/unit/core/test_error_codes_coverage.py` (NEW)
**Source:** `game/core/error_codes.py` (145 LOC)
**Existing:** `tests/unit/core/test_error_codes.py`
**Tests:** `pytest tests/unit/core/test_error_codes_coverage.py`

- [ ] `test_all_error_codes_unique_values` - No duplicate .value among all members
- [ ] `test_all_codes_follow_naming_convention` - Each value matches X### pattern (letter + 3 digits)
- [ ] `test_validation_codes_start_with_v` - V001-V099 pattern
- [ ] `test_state_codes_start_with_s` - S001-S099 pattern
- [ ] `test_resource_codes_start_with_r` - R001-R099 pattern
- [ ] `test_persistence_codes_start_with_p` - P001-P099 pattern
- [ ] `test_formula_codes_start_with_f` - F001-F099 pattern
- [ ] `test_component_codes_start_with_c` - C001-C099 pattern

**Estimated tests: ~8**

---

### Task 4.6: JSON Utils Edge Cases (TCG-FND-016) [Simple]
**File:** `tests/unit/core/test_json_utils_edge_cases.py` (NEW)
**Source:** `game/core/json_utils.py` (144 LOC)
**Existing:** `tests/unit/core/test_json_utils.py`
**Tests:** `pytest tests/unit/core/test_json_utils_edge_cases.py`

load_json error paths:
- [ ] `test_load_json_file_not_found_returns_default` - Missing file -> default
- [ ] `test_load_json_invalid_json_returns_default` - Malformed JSON -> default
- [ ] `test_load_json_io_error_returns_default` - Permission error -> default
- [ ] `test_load_json_custom_default` - Custom default value returned on error

save_json error paths:
- [ ] `test_save_json_io_error_returns_false` - Permission error -> False
- [ ] `test_save_json_type_error_returns_false` - Non-serializable object -> False
- [ ] `test_save_json_creates_parent_dirs` - Parent directories created

load_json_required:
- [ ] `test_load_json_required_missing_raises_file_not_found` - Raises FileNotFoundError
- [ ] `test_load_json_required_invalid_raises_decode_error` - Raises json.JSONDecodeError

**Estimated tests: ~9**

---

### Task 4.7: Configuration Edge Cases (TCG-FND-017) [Simple]
**File:** `tests/unit/core/test_config_edge_cases.py` (NEW)
**Source:** `game/core/config.py` (500+ LOC)
**Existing:** `tests/unit/core/test_config.py`
**Tests:** `pytest tests/unit/core/test_config_edge_cases.py`

DisplayConfig:
- [ ] `test_default_resolution_tuple` - Returns (3840, 2160)
- [ ] `test_windowed_resolution_tuple` - Returns (2560, 1600)
- [ ] `test_test_resolution_tuple` - Returns (1440, 900)

AIConfig boundary values:
- [ ] `test_min_spacing_positive` - MIN_SPACING > 0
- [ ] `test_flee_distance_greater_than_orbit` - FLEE_DISTANCE > DEFAULT_ORBIT_DISTANCE
- [ ] `test_formation_throttle_0_to_1` - FORMATION_ENGINE_THROTTLE in (0, 1]

PhysicsConfig:
- [ ] `test_tick_rate_positive` - TICK_RATE > 0
- [ ] `test_spatial_grid_cell_size_positive` - SPATIAL_GRID_CELL_SIZE > 0

**Estimated tests: ~8**

---

### Task 4.8: AI Interfaces Adapter Coverage (TCG-FND-018) [Simple]
**File:** `tests/unit/ai/test_controllable_adapter.py` (NEW or EXPAND)
**Source:** `game/ai/interfaces/controllable.py` (200+ LOC)
**Existing:** `tests/unit/ai/controllable_interface/` tests
**Tests:** `pytest tests/unit/ai/test_controllable_adapter.py`

Note: First check existing tests in `tests/unit/ai/controllable_interface/`. If comprehensive, mark as already-covered.

IControllable abstract contract:
- [ ] `test_cannot_instantiate_icontrollable` - TypeError on ABC instantiation
- [ ] `test_all_abstract_methods_present` - Check method names via __abstractmethods__
- [ ] `test_concrete_subclass_must_implement_all` - Partial impl raises TypeError
- [ ] `test_mock_implementation_satisfies_interface` - Full mock impl instantiates

**Estimated tests: ~4**

---

### Task 4.9: Research Tracker Serialization Edge Cases (TCG-FND-019) [Simple]
**File:** `tests/unit/research/test_research_tracker_edge_cases.py` (NEW)
**Source:** `game/research/data/research_tracker.py` (180+ LOC)
**Existing:** `tests/unit/research/test_research_tracker.py`
**Tests:** `pytest tests/unit/research/test_research_tracker_edge_cases.py`

NodeState serialization:
- [ ] `test_node_state_roundtrip` - from_dict(to_dict()) preserves all fields
- [ ] `test_node_state_from_dict_defaults` - Missing keys use defaults (0, 0.0, 0)
- [ ] `test_node_state_zero_rp` - rp_allocation=0 serializes correctly
- [ ] `test_node_state_max_chance` - current_chance=0.95 preserved

ResearchTracker serialization:
- [ ] `test_tracker_roundtrip_empty_states` - Empty node_states dict preserved
- [ ] `test_tracker_roundtrip_with_states` - Multiple node states preserved
- [ ] `test_session_seed_consistency` - Same seed produces same sequence

**Estimated tests: ~7**

---

### Task 4.10: Engine Physics Floating Point (TCG-FND-020) [Simple]
**File:** `tests/unit/systems/test_physics_edge_cases.py` (NEW)
**Source:** `game/engine/physics.py` (250+ LOC)
**Existing:** `tests/unit/systems/test_physics.py`
**Tests:** `pytest tests/unit/systems/test_physics_edge_cases.py`

- [ ] `test_zero_velocity_stays_zero` - No force -> velocity remains 0
- [ ] `test_very_small_velocity_not_lost` - 1e-10 velocity preserved after update
- [ ] `test_large_force_velocity_reasonable` - Very large force doesn't produce infinity
- [ ] `test_zero_mass_handling` - Division by zero protected (or documented behavior)
- [ ] `test_drag_reduces_velocity` - After many ticks, velocity approaches 0

**Estimated tests: ~5**

---

### Task 4.11: Spatial Grid Query Edge Cases (TCG-FND-021) [Simple]
**File:** `tests/unit/systems/test_spatial_edge_cases.py` (NEW)
**Source:** `game/engine/spatial.py` (36 LOC)
**Existing:** `tests/unit/systems/test_spatial.py`, `tests/unit/systems/test_spatial_extended.py`
**Tests:** `pytest tests/unit/systems/test_spatial_edge_cases.py`

- [ ] `test_query_radius_at_cell_boundary` - Object exactly on cell boundary found
- [ ] `test_query_negative_coordinates` - Objects at negative positions found
- [ ] `test_query_empty_grid` - Empty grid returns []
- [ ] `test_query_radius_zero` - radius=0 returns objects in same cell only
- [ ] `test_insert_and_query_many_objects` - 100+ objects handled correctly

**Estimated tests: ~5**

---

## Simulation MINOR Tasks

### Task 4.12: Marker Ability UI Output (TCG-SIM-010) [Simple]
**File:** `tests/unit/components/abilities/test_markers_ui.py` (NEW)
**Source:** `game/simulation/components/abilities/markers.py` (91 LOC)
**Existing:** Will be created in Phase 2 Task 2.7 (markers tests). This task adds UI-specific tests.
**Tests:** `pytest tests/unit/components/abilities/test_markers_ui.py`

Note: Depends on Phase 2 Task 2.7 completing first. If markers tests already cover get_ui_rows(), skip this.

- [ ] `test_vehicle_launch_ui_rows_format` - get_ui_rows() returns formatted capacity/cycle text
- [ ] `test_command_control_ui_rows` - Returns command status text
- [ ] `test_structural_integrity_ui_rows` - Returns integrity info text

**Estimated tests: ~3**

---

### Task 4.13: Component Health Manager Edge Cases (TCG-SIM-011) [Simple]
**File:** `tests/unit/components/test_component_health_edge_cases.py` (NEW)
**Source:** `game/simulation/components/component_health_manager.py`
**Existing:** `tests/unit/components/test_component_health_manager.py`
**Tests:** `pytest tests/unit/components/test_component_health_edge_cases.py`

- [ ] `test_take_damage_zero_hp_component` - Damage to 0-HP component returns True (destroyed)
- [ ] `test_heal_past_max_hp` - Healing capped at max HP
- [ ] `test_damage_threshold_50_percent` - Component at exactly 50% HP gets DAMAGED status
- [ ] `test_damage_below_threshold_not_damaged` - Component at 51% HP stays operational

**Estimated tests: ~4**

---

### Task 4.14: Resource Manager Edge Cases (TCG-SIM-012) [Simple]
**File:** `tests/unit/simulation/systems/test_resource_manager_edge_cases.py` (NEW)
**Source:** `game/simulation/systems/resource_manager.py`
**Existing:** Check `tests/unit/simulation/systems/` for existing resource tests
**Tests:** `pytest tests/unit/simulation/systems/test_resource_manager_edge_cases.py`

- [ ] `test_consume_more_than_available` - Returns False or clamps to 0
- [ ] `test_regen_capped_at_max` - Regeneration doesn't exceed max_value
- [ ] `test_register_storage_additive` - Multiple register_storage calls sum up
- [ ] `test_set_value_at_max` - set_value(max) preserves exact value
- [ ] `test_reset_stats_preserves_current` - reset_stats zeroes max but keeps current

**Estimated tests: ~5**

---

### Task 4.15: Ability Aggregator Layer Scope (TCG-SIM-013) [Simple]
**File:** `tests/unit/entities/test_ability_aggregator_scope.py` (NEW)
**Source:** `game/simulation/entities/ability_aggregator.py`
**Existing:** `tests/unit/entities/test_ability_aggregator_layers.py`
**Tests:** `pytest tests/unit/entities/test_ability_aggregator_scope.py`

- [ ] `test_combat_layer_only_combat_abilities` - COMBAT layer filters non-combat
- [ ] `test_strategic_layer_only_strategic_abilities` - STRATEGIC layer filters combat
- [ ] `test_both_layer_abilities_in_combat` - BOTH-layer abilities included in combat
- [ ] `test_both_layer_abilities_in_strategic` - BOTH-layer abilities included in strategic
- [ ] `test_scope_filtering_sector` - SECTOR scope abilities filtered correctly

**Estimated tests: ~5**

---

### Task 4.16: Combat Endurance Calculation (TCG-SIM-014) [Simple]
**File:** `tests/unit/combat/test_combat_endurance_edge_cases.py` (NEW)
**Source:** `game/simulation/entities/combat_endurance.py`
**Existing:** `tests/unit/combat/test_combat_endurance.py`
**Tests:** `pytest tests/unit/combat/test_combat_endurance_edge_cases.py`

- [ ] `test_crew_shortage_reduces_endurance` - Low crew -> lower endurance
- [ ] `test_fuel_shortage_reduces_endurance` - Low fuel -> lower endurance
- [ ] `test_simultaneous_shortages_combined` - Multiple shortages compound
- [ ] `test_full_resources_max_endurance` - All resources full -> max endurance

**Estimated tests: ~4**

---

### Task 4.17: Hit/Miss Resolution Edge Cases (TCG-SIM-015) [Medium]
**File:** `tests/unit/combat/test_targeting_edge_cases.py` (NEW)
**Source:** `game/simulation/combat/targeting_system.py` + `game/simulation/combat/damage_calculator.py`
**Existing:** Check existing targeting/damage tests
**Tests:** `pytest tests/unit/combat/test_targeting_edge_cases.py`

- [ ] `test_zero_defense_score` - 0 defense -> higher hit chance
- [ ] `test_maximum_range_accuracy_penalty` - At max range -> minimum accuracy
- [ ] `test_point_blank_range_bonus` - Very close range -> accuracy bonus
- [ ] `test_evasion_stacking` - Multiple evasion sources combine correctly

**Estimated tests: ~4**

---

### Task 4.18: Ship Formation Positioning (TCG-SIM-016) [Simple]
**File:** `tests/unit/entities/test_ship_formation_edge_cases.py` (NEW)
**Source:** `game/simulation/entities/ship_formation.py`
**Existing:** `tests/unit/entities/test_ship_formation.py`
**Tests:** `pytest tests/unit/entities/test_ship_formation_edge_cases.py`

- [ ] `test_empty_formation_no_crash` - 0 ships -> empty offsets
- [ ] `test_single_ship_formation` - 1 ship -> offset at center
- [ ] `test_large_formation_all_unique_positions` - 20 ships -> no overlapping offsets

**Estimated tests: ~3**

---

### Task 4.19: Projectile Physics Edge Cases (TCG-SIM-017) [Medium]
**File:** `tests/unit/entities/test_projectile_edge_cases.py` (NEW)
**Source:** `game/simulation/entities/projectile.py` + `game/simulation/projectile_manager.py`
**Existing:** Check existing projectile tests
**Tests:** `pytest tests/unit/entities/test_projectile_edge_cases.py`

- [ ] `test_very_fast_projectile_ccd` - Fast projectile doesn't phase through target
- [ ] `test_stationary_target_hit` - Projectile hits stationary target at any speed
- [ ] `test_projectile_lifetime_expiry` - Expired projectile removed

**Estimated tests: ~3**

---

### Task 4.20: Ship Stats Phase Ordering (TCG-SIM-018) [Medium]
**File:** `tests/unit/simulation/systems/test_ship_stats_phase_ordering.py` (NEW)
**Source:** `game/simulation/entities/ship_stats.py`
**Existing:** `tests/unit/entities/test_ship_stats.py`, `tests/unit/simulation/systems/test_ship_stats_calculator_phases.py`
**Tests:** `pytest tests/unit/simulation/systems/test_ship_stats_phase_ordering.py`

Note: Check existing phase tests first. If `test_ship_stats_calculator_phases.py` already verifies ordering, mark as covered.

- [ ] `test_phase_1_resets_before_aggregation` - Phase 1 zeroes stats before recalc
- [ ] `test_phase_2_uses_phase_1_crew_count` - Crew deactivation uses correct count
- [ ] `test_phase_3_only_active_components` - Inactive components excluded
- [ ] `test_phase_5_uses_final_mass` - Physics uses post-modification mass

**Estimated tests: ~4**

---

## Strategy MINOR Tasks

### Task 4.21: Fleet Navigation Service Pure Unit Tests (TCG-STR-009) [Medium]
**File:** `tests/unit/strategy/fleet_navigation/test_navigation_pure.py` (NEW)
**Source:** `game/strategy/services/fleet_navigation_service.py` (100+ LOC)
**Existing:** `tests/unit/strategy/fleet_navigation/test_data_structures.py`, `test_destination_path.py`, `test_projection.py`
**Tests:** `pytest tests/unit/strategy/fleet_navigation/test_navigation_pure.py`

Note: Check existing tests first. Existing files test data structures, destination/path, and projection. Focus on gaps.

NavigationState:
- [ ] `test_navigation_state_frozen` - Frozen dataclass cannot be modified
- [ ] `test_navigation_state_from_fleet_correctness` - All fields populated from fleet

NavigationStep:
- [ ] `test_navigation_step_creation` - next_hex, remaining_movement, warp_used stored
- [ ] `test_navigation_step_no_movement` - remaining=0 step valid

**Estimated tests: ~4**

---

### Task 4.22: Pathfinding Intercept Edge Cases (TCG-STR-010) [Medium]
**File:** `tests/unit/strategy/pathfinding/test_intercept_edge_cases.py` (NEW)
**Source:** `game/strategy/data/pathfinding.py` (447 LOC)
**Existing:** Check existing `test_hybrid_and_intercept.py`
**Tests:** `pytest tests/unit/strategy/pathfinding/test_intercept_edge_cases.py`

- [ ] `test_intercept_faster_chaser` - Chaser faster than target -> intercept found
- [ ] `test_intercept_slower_chaser` - Chaser slower -> no intercept or delayed
- [ ] `test_intercept_same_speed` - Equal speed -> trailing intercept

**Estimated tests: ~3**

---

### Task 4.23: Conflict Resolution Core Logic (TCG-STR-011) [Medium]
**File:** `tests/unit/strategy/conflict_resolution/test_conflict_core.py` (NEW)
**Source:** `game/strategy/engine/conflict_resolution_engine.py` (150+ LOC)
**Existing:** Check for `tests/unit/strategy/conflict_resolution/`
**Tests:** `pytest tests/unit/strategy/conflict_resolution/test_conflict_core.py`

Note: If conflict resolution tests already exist in the directory, expand rather than create new.

- [ ] `test_no_conflicts_returns_zero` - No contested hexes -> combats_resolved=0
- [ ] `test_two_empires_same_hex_triggers_combat` - Contested hex detected
- [ ] `test_three_empires_same_hex` - Multi-empire conflict handled
- [ ] `test_fleet_destroyed_in_result` - Destroyed fleet ID in fleets_destroyed list

**Estimated tests: ~4**

---

### Task 4.24: Galaxy Layout Scaling (TCG-STR-012) [Simple]
**File:** `tests/unit/strategy/generation/test_layout_scaling.py` (NEW)
**Source:** `game/strategy/generation/loaders/` (GalaxyLayoutsLoader)
**Existing:** `tests/unit/strategy/generation/test_astrophysics.py`
**Tests:** `pytest tests/unit/strategy/generation/test_layout_scaling.py`

- [ ] `test_scale_layout_preserves_positions` - Position fields unchanged by scaling
- [ ] `test_scale_layout_scales_sigma` - sigma field scaled by factor
- [ ] `test_scale_layout_scales_radius` - radius field scaled by factor

**Estimated tests: ~3**

---

### Task 4.25: Build Queue Source Error Paths (TCG-STR-013) [Simple]
**File:** `tests/unit/strategy/data/test_build_queue_source_errors.py` (NEW)
**Source:** `game/strategy/data/build_queue_source.py` (289 LOC)
**Existing:** `tests/unit/strategy/data/test_build_queue_source.py`
**Tests:** `pytest tests/unit/strategy/data/test_build_queue_source_errors.py`

- [ ] `test_load_production_rates_missing_file` - Returns {} on missing file
- [ ] `test_load_production_rates_caching` - Second call uses cache
- [ ] `test_collect_queues_no_shipyards` - No shipyard facilities -> empty list
- [ ] `test_collect_queues_missing_facility_data` - Graceful handling of malformed data

**Estimated tests: ~4**

---

### Task 4.26: Simulation Adapter Edge Cases (TCG-STR-014) [Simple]
**File:** `tests/unit/strategy/adapters/test_simulation_adapter_edge_cases.py` (NEW)
**Source:** `game/strategy/adapters/simulation_adapter.py`
**Existing:** `tests/unit/strategy/adapters/test_simulation_adapter.py`
**Tests:** `pytest tests/unit/strategy/adapters/test_simulation_adapter_edge_cases.py`

- [ ] `test_resolve_empty_survivors` - Empty survivor list -> all ships destroyed
- [ ] `test_resolve_null_ship_state` - NULL ship state in survivors handled
- [ ] `test_registries_passed_to_battle_engine` - Registries forwarded correctly

**Estimated tests: ~3**

---

### Task 4.27: Ship Display Formatter Edge Cases (TCG-STR-015) [Simple]
**File:** `tests/unit/strategy/test_ship_display_formatter_edge_cases.py` (NEW)
**Source:** `game/strategy/data/ship_display_formatter.py` (111 LOC)
**Existing:** `tests/unit/strategy/test_ship_display_formatter.py`
**Tests:** `pytest tests/unit/strategy/test_ship_display_formatter_edge_cases.py`

- [ ] `test_display_id_with_null_serial` - serial=None -> returns None
- [ ] `test_status_text_destroyed` - is_alive=False -> "DESTROYED"
- [ ] `test_resource_percentage_zero_max` - max_storage=0 -> no division by zero
- [ ] `test_hp_display_zero_max` - max_hp=0 -> safe display

**Estimated tests: ~4**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] All new tests pass: `pytest tests/unit/ -v --tb=short`
- [ ] Full test suite still passes: `pytest tests/ -n 12`
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to project audit
