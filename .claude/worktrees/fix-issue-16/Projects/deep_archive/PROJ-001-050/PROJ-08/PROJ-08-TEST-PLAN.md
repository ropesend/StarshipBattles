# PROJ-08 Test Plan: Data-Driven Resource System

This document lists all tests that should be created to verify the PROJ-08 refactor is fully implemented and working correctly.

**Total Tests Required: 243**
**Total Tests Implemented: 271** (exceeds target with additional coverage)

---

## Implementation Progress Checklist

**Last Updated:** 2026-01-22
**Status:** ✅ COMPLETE

### Summary

| Section | Tests | Implemented | Passing | Owner | Status |
|---------|-------|-------------|---------|-------|--------|
| 1. Resource Registry | 39 | 39 | 39 | Agent | ✅ Complete |
| 2. ShipStatsService | 31 | 53 | 53 | Agent | ✅ Complete |
| 3. ShipInstance | 71 | 71 | 71 | Agent | ✅ Complete |
| 4. Fleet | 42 | 73 | 73 | Agent | ✅ Complete |
| 5. TurnEngine | 22 | 27 | 27 | Agent | ✅ Complete |
| 6. Integration | 8 | 8 | 8 | Agent | ✅ Complete |
| 7. Fixtures | - | ✓ | - | Agent | ✅ Complete |
| **TOTAL** | **243** | **271** | **271** | | **✅ COMPLETE** |

### Test Files Created/Modified

- `tests/unit/core/test_resources_registry.py` (NEW) - 39 tests
- `tests/unit/strategy/test_ship_stats_service.py` (MODIFIED) - 31 new tests added
- `tests/unit/strategy/test_ship_instance_proj08.py` (NEW) - 71 tests
- `tests/unit/strategy/test_fleet.py` (MODIFIED) - 42 new tests added
- `tests/strategy/test_turn_engine.py` (MODIFIED) - 22 new tests added
- `tests/integration/test_resource_system.py` (NEW) - 8 tests
- `tests/unit/strategy/conftest.py` (NEW) - Common fixtures

---

### Section 1: Resource Registry Tests (39 tests) ✅

**File:** `tests/unit/core/test_resources_registry.py` (NEW)

- [x] **1.1 Happy Path** (5 tests) ✅
  - [x] 1.1.1 `test_load_resources_basic_happy_path`
  - [x] 1.1.2 `test_load_resources_uses_default_path`
  - [x] 1.1.3 `test_load_resources_with_custom_filepath`
  - [x] 1.1.4 `test_load_resources_preserves_all_fields`
  - [x] 1.1.5 `test_load_resources_handles_absolute_path`

- [x] **1.2 Error Handling** (5 tests) ✅
  - [x] 1.2.1 `test_load_resources_missing_file_uses_defaults`
  - [x] 1.2.2 `test_load_resources_missing_file_abs_path_fallback`
  - [x] 1.2.3 `test_load_resources_malformed_json_uses_defaults`
  - [x] 1.2.4 `test_load_resources_invalid_json_exception_handling`
  - [x] 1.2.5 `test_load_resources_empty_file_uses_defaults`

- [x] **1.3 Edge Cases** (9 tests) ✅
  - [x] 1.3.1 `test_load_resources_empty_resources_array`
  - [x] 1.3.2 `test_load_resources_missing_resources_key_silent_failure` ⚠️ BUG DOC
  - [x] 1.3.3 `test_load_resources_null_resources_value`
  - [x] 1.3.4 `test_load_resources_resources_not_array`
  - [x] 1.3.5 `test_load_resources_resource_missing_id_field`
  - [x] 1.3.6 `test_load_resources_resource_null_id`
  - [x] 1.3.7 `test_load_resources_resource_empty_string_id`
  - [x] 1.3.8 `test_load_resources_duplicate_ids_last_wins`
  - [x] 1.3.9 `test_load_resources_duplicate_ids_warning`

- [x] **1.4 Data Accumulation Bug** (4 tests) ⚠️ CRITICAL ✅
  - [x] 1.4.1 `test_load_resources_multiple_calls_accumulate_data` ⚠️ BUG DOC
  - [x] 1.4.2 `test_load_resources_reload_should_replace_not_accumulate`
  - [x] 1.4.3 `test_load_resources_partial_reload_leaves_old_data`
  - [x] 1.4.4 `test_registry_resources_clear_between_loads`

- [x] **1.5 Registry Integration** (5 tests) ✅
  - [x] 1.5.1 `test_get_resource_registry_returns_correct_dict`
  - [x] 1.5.2 `test_get_resource_registry_empty_after_clear`
  - [x] 1.5.3 `test_resource_registry_keyed_by_id`
  - [x] 1.5.4 `test_registry_manager_resources_initialization`
  - [x] 1.5.5 `test_registry_manager_freeze_prevents_load`

- [x] **1.6 Logging** (3 tests) ✅
  - [x] 1.6.1 `test_load_resources_logs_success_info`
  - [x] 1.6.2 `test_load_resources_logs_missing_file_warning`
  - [x] 1.6.3 `test_load_resources_logs_parse_failure_warning`

- [x] **1.7 Thread Safety** (2 tests) ✅
  - [x] 1.7.1 `test_load_resources_thread_safe_singleton_access`
  - [x] 1.7.2 `test_registry_manager_singleton_shared_resources`

- [x] **1.8 Fixture Integration** (2 tests) ✅
  - [x] 1.8.1 `test_reset_game_state_clears_resources`
  - [x] 1.8.2 `test_load_resources_from_real_data_directory`

- [x] **1.9 Exception Scenarios** (4 tests) ✅
  - [x] 1.9.1 `test_load_resources_file_permission_denied`
  - [x] 1.9.2 `test_load_resources_path_encoding_issues`
  - [x] 1.9.3 `test_load_resources_very_large_json_file`
  - [x] 1.9.4 `test_load_resources_deeply_nested_json`

---

### Section 2: ShipStatsService Tests (31 tests) ✅

**File:** `tests/unit/strategy/test_ship_stats_service.py` (ADD TO EXISTING)

- [x] **2.1 Generic Dict Accumulators** (5 tests) ✅
  - [x] 2.1.1 `test_resource_storage_generic_dict_structure`
  - [x] 2.1.2 `test_resource_consumption_per_hex_generic_dict`
  - [x] 2.1.3 `test_resource_consumption_per_turn_generic_dict`
  - [x] 2.1.4 `test_warp_resource_costs_generic_dict`
  - [x] 2.1.5 `test_multiple_custom_resources_accumulate`

- [x] **2.2 Component Toggles** (8 tests) ✅
  - [x] 2.2.1 `test_toggled_off_component_mass_still_counted`
  - [x] 2.2.2 `test_toggled_off_component_no_hp_contribution`
  - [x] 2.2.3 `test_toggled_off_component_no_strategic_movement`
  - [x] 2.2.4 `test_toggled_off_warp_drive_no_warp_capability`
  - [x] 2.2.5 `test_toggled_off_resource_storage_not_counted`
  - [x] 2.2.6 `test_mixed_enabled_disabled_components`
  - [x] 2.2.7 `test_missing_toggle_defaults_to_enabled`
  - [x] 2.2.8 `test_toggled_off_custom_resource_consumption_not_counted`

- [x] **2.3 Trigger Types** (7 tests) ✅
  - [x] 2.3.1 `test_trigger_strategic_per_hex_accumulates_correctly`
  - [x] 2.3.2 `test_trigger_per_turn_accumulates_correctly`
  - [x] 2.3.3 `test_trigger_warp_jump_accumulates_correctly`
  - [x] 2.3.4 `test_different_triggers_dont_cross_buckets`
  - [x] 2.3.5 `test_trigger_per_turn_degrades_with_damage`
  - [x] 2.3.6 `test_trigger_warp_jump_requires_full_hp`
  - [x] 2.3.7 `test_trigger_unknown_type_ignored`

- [x] **2.4 Custom Resources** (5 tests) ✅
  - [x] 2.4.1 `test_custom_resource_type_in_storage`
  - [x] 2.4.2 `test_custom_resource_per_hex_consumption`
  - [x] 2.4.3 `test_custom_resource_per_turn_consumption`
  - [x] 2.4.4 `test_custom_resource_warp_costs`
  - [x] 2.4.5 `test_many_different_custom_resources_coexist`

- [x] **2.5 Bug Documentation** (3 tests) ✅
  - [x] 2.5.1 `test_empty_resource_type_creates_empty_string_key_bug` ⚠️ BUG DOC
  - [x] 2.5.2 `test_empty_resource_type_in_consumption_ignored`
  - [x] 2.5.3 `test_none_resource_type_handled_safely`

- [x] **2.6 Integration** (3 tests) ✅
  - [x] 2.6.1 `test_damaged_toggled_component_full_mass_partial_stats`
  - [x] 2.6.2 `test_all_resource_types_in_one_component`
  - [x] 2.6.3 `test_fallback_handles_new_generic_fields`

---

### Section 3: ShipInstance Tests (71 tests) ✅

**File:** `tests/unit/strategy/test_ship_instance_proj08.py` (NEW)

- [x] **3.1 Component Toggles Field** (2 tests) ✅
  - [x] 3.1.1 `test_component_toggles_field_initialized_empty`
  - [x] 3.1.2 `test_component_toggles_field_default_factory`

- [x] **3.2 set_component_enabled** (5 tests) ✅
  - [x] 3.2.1 `test_set_component_enabled_enable`
  - [x] 3.2.2 `test_set_component_enabled_disable`
  - [x] 3.2.3 `test_set_component_enabled_multiple_components`
  - [x] 3.2.4 `test_set_component_enabled_overwrites_existing`
  - [x] 3.2.5 `test_set_component_enabled_invalidates_cache`

- [x] **3.3 is_component_enabled** (4 tests) ✅
  - [x] 3.3.1 `test_is_component_enabled_default_true`
  - [x] 3.3.2 `test_is_component_enabled_explicitly_true`
  - [x] 3.3.3 `test_is_component_enabled_explicitly_false`
  - [x] 3.3.4 `test_is_component_enabled_after_set`

- [x] **3.4 get_resource_capacity** (5 tests) ✅
  - [x] 3.4.1 `test_get_resource_capacity_fuel`
  - [x] 3.4.2 `test_get_resource_capacity_energy`
  - [x] 3.4.3 `test_get_resource_capacity_custom_resource`
  - [x] 3.4.4 `test_get_resource_capacity_unknown_resource`
  - [x] 3.4.5 `test_get_resource_capacity_zero_capacity`

- [x] **3.5 get_current_resource** (4 tests) ✅
  - [x] 3.5.1 `test_get_current_resource_returns_default_when_full`
  - [x] 3.5.2 `test_get_current_resource_returns_current_when_partial`
  - [x] 3.5.3 `test_get_current_resource_with_all_types`
  - [x] 3.5.4 `test_get_current_resource_custom_resource`

- [x] **3.6 consume_resource** (7 tests) ✅
  - [x] 3.6.1 `test_consume_resource_success`
  - [x] 3.6.2 `test_consume_resource_insufficient_fails`
  - [x] 3.6.3 `test_consume_resource_exact_amount`
  - [x] 3.6.4 `test_consume_resource_zero_amount`
  - [x] 3.6.5 `test_consume_resource_multiple_types`
  - [x] 3.6.6 `test_consume_resource_custom_type`
  - [x] 3.6.7 `test_consume_resource_when_not_tracked`

- [x] **3.7 get_all_resource_costs_per_hex** (4 tests) ✅
  - [x] 3.7.1 `test_get_all_resource_costs_per_hex_empty`
  - [x] 3.7.2 `test_get_all_resource_costs_per_hex_fuel_only`
  - [x] 3.7.3 `test_get_all_resource_costs_per_hex_multiple_resources`
  - [x] 3.7.4 `test_get_all_resource_costs_per_hex_custom_resource`

- [x] **3.8 get_all_resource_costs_per_turn** (4 tests) ✅
  - [x] 3.8.1 `test_get_all_resource_costs_per_turn_empty`
  - [x] 3.8.2 `test_get_all_resource_costs_per_turn_single_resource`
  - [x] 3.8.3 `test_get_all_resource_costs_per_turn_multiple_resources`
  - [x] 3.8.4 `test_get_all_resource_costs_per_turn_custom_resource`

- [x] **3.9 get_warp_resource_costs** (5 tests) ✅
  - [x] 3.9.1 `test_get_warp_resource_costs_empty`
  - [x] 3.9.2 `test_get_warp_resource_costs_energy_only`
  - [x] 3.9.3 `test_get_warp_resource_costs_fuel_and_energy`
  - [x] 3.9.4 `test_get_warp_resource_costs_custom_resource`
  - [x] 3.9.5 `test_get_warp_resource_costs_damaged_warp_drive`

- [x] **3.10 Cache Invalidation** (3 tests) ✅
  - [x] 3.10.1 `test_cache_invalidation_on_set_component_enabled`
  - [x] 3.10.2 `test_cache_recalculated_after_toggle`
  - [x] 3.10.3 `test_cache_not_invalidated_on_other_changes`

- [x] **3.11 Serialization - to_dict** (3 tests) ✅
  - [x] 3.11.1 `test_to_dict_includes_component_toggles_empty`
  - [x] 3.11.2 `test_to_dict_includes_component_toggles_with_values`
  - [x] 3.11.3 `test_to_dict_preserves_all_toggle_states`

- [x] **3.12 Serialization - from_dict** (4 tests) ✅
  - [x] 3.12.1 `test_from_dict_restores_component_toggles_empty`
  - [x] 3.12.2 `test_from_dict_restores_component_toggles_with_values`
  - [x] 3.12.3 `test_from_dict_missing_component_toggles_defaults_to_empty`
  - [x] 3.12.4 `test_from_dict_then_to_dict_round_trip`

- [x] **3.13 Clone Preservation** (4 tests) ✅
  - [x] 3.13.1 `test_clone_preserves_component_toggles_empty`
  - [x] 3.13.2 `test_clone_preserves_component_toggles_with_values`
  - [x] 3.13.3 `test_clone_toggles_are_independent_copies`
  - [x] 3.13.4 `test_clone_preserves_new_instance_id`

- [x] **3.14 Stats Integration** (2 tests) ✅
  - [x] 3.14.1 `test_component_toggles_passed_to_stats_calculation`
  - [x] 3.14.2 `test_disabled_component_affects_stats`

- [x] **3.15 Resource Method Interactions** (3 tests) ✅
  - [x] 3.15.1 `test_get_resource_capacity_with_disabled_component`
  - [x] 3.15.2 `test_consume_resource_tracks_in_resource_levels`
  - [x] 3.15.3 `test_get_all_resource_costs_multiple_calls_consistent`

- [x] **3.16 Backward Compatibility** (4 tests) ✅
  - [x] 3.16.1 `test_legacy_methods_still_work_get_current_fuel`
  - [x] 3.16.2 `test_legacy_methods_still_work_consume_fuel`
  - [x] 3.16.3 `test_legacy_methods_still_work_get_current_energy`
  - [x] 3.16.4 `test_legacy_methods_still_work_consume_energy`

- [x] **3.17 Edge Cases** (4 tests) ✅
  - [x] 3.17.1 `test_consume_resource_negative_amount`
  - [x] 3.17.2 `test_get_resource_capacity_empty_stats`
  - [x] 3.17.3 `test_component_toggles_with_nonexistent_component`
  - [x] 3.17.4 `test_get_all_resource_costs_when_stats_missing_field`

---

### Section 4: Fleet Tests (42 tests) ✅

**File:** `tests/unit/strategy/test_fleet.py` (ADD TO EXISTING)

- [x] **4.1 Movement Resource Methods** (16 tests) ✅
  - [x] 4.1.1 `test_movement_resource_costs_single_ship`
  - [x] 4.1.2 `test_movement_resource_costs_multiple_ships`
  - [x] 4.1.3 `test_movement_resource_costs_mixed_resource_types`
  - [x] 4.1.4 `test_movement_resource_costs_empty_fleet`
  - [x] 4.1.5 `test_movement_resource_costs_legacy_string_ships_only`
  - [x] 4.1.6 `test_has_resources_for_movement_sufficient_all_ships`
  - [x] 4.1.7 `test_has_resources_for_movement_insufficient_fuel_one_ship`
  - [x] 4.1.8 `test_has_resources_for_movement_insufficient_energy_one_ship`
  - [x] 4.1.9 `test_has_resources_for_movement_zero_cost_resources`
  - [x] 4.1.10 `test_has_resources_for_movement_empty_fleet`
  - [x] 4.1.11 `test_consume_movement_resources_success_single_hex`
  - [x] 4.1.12 `test_consume_movement_resources_success_multiple_hexes`
  - [x] 4.1.13 `test_consume_movement_resources_failure_atomicity`
  - [x] 4.1.14 `test_consume_movement_resources_atomicity_multi_resource`
  - [x] 4.1.15 `test_consume_movement_resources_zero_cost_resources`
  - [x] 4.1.16 `test_consume_movement_resources_empty_fleet`

- [x] **4.2 Warp Resource Methods** (15 tests) ✅
  - [x] 4.2.1 `test_warp_resource_costs_single_ship`
  - [x] 4.2.2 `test_warp_resource_costs_multiple_ships`
  - [x] 4.2.3 `test_warp_resource_costs_mixed_resource_types`
  - [x] 4.2.4 `test_warp_resource_costs_empty_fleet`
  - [x] 4.2.5 `test_warp_resource_costs_legacy_string_ships_only`
  - [x] 4.2.6 `test_has_resources_for_warp_sufficient_all_ships`
  - [x] 4.2.7 `test_has_resources_for_warp_insufficient_energy_one_ship`
  - [x] 4.2.8 `test_has_resources_for_warp_insufficient_fuel_one_ship`
  - [x] 4.2.9 `test_has_resources_for_warp_zero_cost_resources`
  - [x] 4.2.10 `test_has_resources_for_warp_empty_fleet`
  - [x] 4.2.11 `test_consume_warp_resources_success_all_ships`
  - [x] 4.2.12 `test_consume_warp_resources_failure_atomicity`
  - [x] 4.2.13 `test_consume_warp_resources_atomicity_multi_resource`
  - [x] 4.2.14 `test_consume_warp_resources_zero_cost_resources`
  - [x] 4.2.15 `test_consume_warp_resources_empty_fleet`

- [x] **4.3 Backward Compatibility** (4 tests) ✅
  - [x] 4.3.1 `test_backward_compat_has_energy_for_warp_wrapper`
  - [x] 4.3.2 `test_backward_compat_consume_warp_energy_wrapper`
  - [x] 4.3.3 `test_backward_compat_consume_fleet_fuel_wrapper`
  - [x] 4.3.4 `test_backward_compat_legacy_warp_methods_still_work`

- [x] **4.4 Edge Cases** (7 tests) ✅
  - [x] 4.4.1 `test_destroyed_ships_excluded_from_movement_calculation`
  - [x] 4.4.2 `test_derelict_ships_excluded_from_warp_calculation`
  - [x] 4.4.3 `test_mixed_destroyed_and_combat_capable_ships`
  - [x] 4.4.4 `test_very_large_fleet`
  - [x] 4.4.5 `test_ships_with_no_resource_costs`
  - [x] 4.4.6 `test_floating_point_precision_in_resource_consumption`
  - [x] 4.4.7 `test_warp_capability_check_integration`

---

### Section 5: TurnEngine Tests (22 tests) ✅

**File:** `tests/strategy/test_turn_engine.py` (ADD TO EXISTING)

- [x] **5.1 Per-Turn Resource Consumption** (5 tests) ✅
  - [x] 5.1.1 `test_per_turn_resource_consumption_single_ship`
  - [x] 5.1.2 `test_per_turn_resource_consumption_multiple_resources`
  - [x] 5.1.3 `test_per_turn_resource_consumption_multiple_ships_in_fleet`
  - [x] 5.1.4 `test_per_turn_consumption_non_combat_ships_skipped`
  - [x] 5.1.5 `test_per_turn_consumption_zero_cost_components_ignored`

- [x] **5.2 Resource Depletion** (3 tests) ✅
  - [x] 5.2.1 `test_resource_depletion_during_tick_returns_false`
  - [x] 5.2.2 `test_resource_depletion_triggers_auto_disable`
  - [x] 5.2.3 `test_no_auto_disable_for_non_per_turn_resources`

- [x] **5.3 Auto-Disable Logic** (6 tests) ✅
  - [x] 5.3.1 `test_auto_disable_finds_components_with_per_turn_trigger`
  - [x] 5.3.2 `test_auto_disable_multiple_components_same_resource`
  - [x] 5.3.3 `test_auto_disable_skips_unregistered_components`
  - [x] 5.3.4 `test_auto_disable_handles_layer_formats`
  - [x] 5.3.5 `test_auto_disable_invalidates_stats_cache`
  - [x] 5.3.6 `test_auto_disable_logs_info_message`

- [x] **5.4 Full Turn Integration** (3 tests) ✅
  - [x] 5.4.1 `test_full_turn_depletes_per_turn_resources_completely`
  - [x] 5.4.2 `test_full_turn_does_not_overconsume_resources`
  - [x] 5.4.3 `test_per_turn_and_movement_resources_both_consumed`

- [x] **5.5 Movement Gating** (3 tests) ✅
  - [x] 5.5.1 `test_movement_requires_generic_resources`
  - [x] 5.5.2 `test_generic_movement_resource_consumption`
  - [x] 5.5.3 `test_warp_uses_generic_methods`

- [x] **5.6 Component Toggle Integration** (2 tests) ✅
  - [x] 5.6.1 `test_disabled_component_not_consumed_per_turn`
  - [x] 5.6.2 `test_auto_disabled_component_reenabled_via_manual_toggle`

---

### Section 6: Integration Tests (8 tests) ✅

**File:** `tests/integration/test_resource_system.py` (NEW)

- [x] 6.1 `test_custom_resource_type_full_pipeline`
- [x] 6.2 `test_per_turn_consumption_across_full_turn`
- [x] 6.3 `test_auto_disable_component_chain_on_resource_depletion`
- [x] 6.4 `test_warp_jump_uses_resource_consumption_trigger`
- [x] 6.5 `test_movement_with_multi_resource_consumption`
- [x] 6.6 `test_backward_compat_load_old_save_without_component_toggles`
- [x] 6.7 `test_component_toggle_affects_movement_and_warp`
- [x] 6.8 `test_fleet_mixed_legacy_and_new_ship_instances`

---

### Section 7: Common Fixtures ✅

**File:** `tests/unit/strategy/conftest.py` (NEW)

- [x] `reset_resource_registry` fixture
- [x] `temp_resources_json` fixture
- [x] `custom_resource_registry` fixture
- [x] `ship_with_per_turn_component` fixture
- [x] `fleet_with_resource_ships` fixture
- [x] `mock_component_registry` fixture
- [x] `make_design_data` fixture
- [x] `ship_stats_with_custom_resources` fixture

---

## Agent Assignment Log

| Agent | Section(s) Assigned | Date Started | Date Completed | Notes |
|-------|---------------------|--------------|----------------|-------|
| ac7f8dd | Section 1: Resource Registry | 2026-01-22 | 2026-01-22 | 39/39 tests passing |
| af28267 | Section 2: ShipStatsService | 2026-01-22 | 2026-01-22 | 31+ tests added, 53 total passing |
| a44f573 | Section 3: ShipInstance | 2026-01-22 | 2026-01-22 | 71/71 tests passing |
| a8255be | Section 4: Fleet | 2026-01-22 | 2026-01-22 | 42+ tests added, 73 total passing |
| ac4868b | Section 5: TurnEngine | 2026-01-22 | 2026-01-22 | 22+ tests added, 27 total passing |
| a706ce4 | Section 6: Integration | 2026-01-22 | 2026-01-22 | 8/8 tests passing |
| Main | Section 7: Fixtures | 2026-01-22 | 2026-01-22 | All fixtures created |

---

## Table of Contents

1. [Resource Registry Tests](#1-resource-registry-tests) - 39 tests
2. [ShipStatsService Tests](#2-shipstatsservice-tests) - 31 tests
3. [ShipInstance Tests](#3-shipinstance-tests) - 71 tests
4. [Fleet Tests](#4-fleet-tests) - 42 tests
5. [TurnEngine Tests](#5-turnengine-tests) - 22 tests
6. [Integration Tests](#6-integration-tests) - 8 tests
7. [Test Fixtures](#7-common-fixtures)

---

## 1. Resource Registry Tests

**File:** `tests/unit/core/test_resources_registry.py` (NEW)

**Total: 39 tests**

### Group 1: Happy Path (5 tests)

| # | Test Name | Description |
|---|-----------|-------------|
| 1.1 | `test_load_resources_basic_happy_path` | Normal loading of valid resources from JSON file |
| 1.2 | `test_load_resources_uses_default_path` | Function finds and loads from default `data/resources.json` |
| 1.3 | `test_load_resources_with_custom_filepath` | Function accepts custom filepath parameter |
| 1.4 | `test_load_resources_preserves_all_fields` | All fields from resource definitions are preserved |
| 1.5 | `test_load_resources_handles_absolute_path` | Function works with absolute paths |

### Group 2: Error Handling (5 tests)

| # | Test Name | Description |
|---|-----------|-------------|
| 2.1 | `test_load_resources_missing_file_uses_defaults` | Missing file falls back to hardcoded defaults |
| 2.2 | `test_load_resources_missing_file_abs_path_fallback` | Attempts absolute path resolution before defaults |
| 2.3 | `test_load_resources_malformed_json_uses_defaults` | Invalid JSON syntax triggers defaults |
| 2.4 | `test_load_resources_invalid_json_exception_handling` | All exceptions caught gracefully |
| 2.5 | `test_load_resources_empty_file_uses_defaults` | Empty JSON object triggers defaults |

### Group 3: Edge Cases (9 tests)

| # | Test Name | Description |
|---|-----------|-------------|
| 3.1 | `test_load_resources_empty_resources_array` | JSON with empty resources array handled |
| 3.2 | `test_load_resources_missing_resources_key_silent_failure` | **BUG DOC**: Missing key silently results in empty registry |
| 3.3 | `test_load_resources_null_resources_value` | Null value handled correctly |
| 3.4 | `test_load_resources_resources_not_array` | Non-array value caught |
| 3.5 | `test_load_resources_resource_missing_id_field` | Resources without 'id' skipped |
| 3.6 | `test_load_resources_resource_null_id` | Null id skipped |
| 3.7 | `test_load_resources_resource_empty_string_id` | Empty string id skipped |
| 3.8 | `test_load_resources_duplicate_ids_last_wins` | Last definition overwrites |
| 3.9 | `test_load_resources_duplicate_ids_warning` | Silent overwrite documented |

### Group 4: Data Accumulation Bug (4 tests)

| # | Test Name | Description |
|---|-----------|-------------|
| 4.1 | `test_load_resources_multiple_calls_accumulate_data` | **BUG DOC**: Multiple calls accumulate instead of replace |
| 4.2 | `test_load_resources_reload_should_replace_not_accumulate` | Expected behavior after bug fix |
| 4.3 | `test_load_resources_partial_reload_leaves_old_data` | Data persistence issue |
| 4.4 | `test_registry_resources_clear_between_loads` | Registry cleared before each load |

### Group 5: Registry Integration (5 tests)

| # | Test Name | Description |
|---|-----------|-------------|
| 5.1 | `test_get_resource_registry_returns_correct_dict` | Utility function returns registry dict |
| 5.2 | `test_get_resource_registry_empty_after_clear` | Reflects state after clear |
| 5.3 | `test_resource_registry_keyed_by_id` | Resources indexed by id field |
| 5.4 | `test_registry_manager_resources_initialization` | Initializes empty dict |
| 5.5 | `test_registry_manager_freeze_prevents_load` | Frozen registry behavior |

### Group 6: Logging (3 tests)

| # | Test Name | Description |
|---|-----------|-------------|
| 6.1 | `test_load_resources_logs_success_info` | Success logs info message |
| 6.2 | `test_load_resources_logs_missing_file_warning` | Missing file triggers warning |
| 6.3 | `test_load_resources_logs_parse_failure_warning` | Parse error triggers warning |

### Group 7: Thread Safety (2 tests)

| # | Test Name | Description |
|---|-----------|-------------|
| 7.1 | `test_load_resources_thread_safe_singleton_access` | Multi-threaded access safe |
| 7.2 | `test_registry_manager_singleton_shared_resources` | Same instance across calls |

### Group 8: Fixture Integration (2 tests)

| # | Test Name | Description |
|---|-----------|-------------|
| 8.1 | `test_reset_game_state_clears_resources` | Fixture clears resources between tests |
| 8.2 | `test_load_resources_from_real_data_directory` | Works with actual file |

### Group 9: Exception Scenarios (4 tests)

| # | Test Name | Description |
|---|-----------|-------------|
| 9.1 | `test_load_resources_file_permission_denied` | Permission errors caught |
| 9.2 | `test_load_resources_path_encoding_issues` | Non-UTF8 handled gracefully |
| 9.3 | `test_load_resources_very_large_json_file` | Large files don't cause issues |
| 9.4 | `test_load_resources_deeply_nested_json` | Nested fields preserved |

---

## 2. ShipStatsService Tests

**File:** `tests/unit/strategy/test_ship_stats_service.py` (ADD TO EXISTING)

**Total: 31 tests**

### Group 1: Generic Dict Accumulators (5 tests)

| # | Test Name | Description |
|---|-----------|-------------|
| 1.1 | `test_resource_storage_generic_dict_structure` | `resource_storage` supports any resource type |
| 1.2 | `test_resource_consumption_per_hex_generic_dict` | Accumulates with `strategic_per_hex` trigger |
| 1.3 | `test_resource_consumption_per_turn_generic_dict` | Accumulates with `per_turn` trigger |
| 1.4 | `test_warp_resource_costs_generic_dict` | Supports any resource with `warp_jump` trigger |
| 1.5 | `test_multiple_custom_resources_accumulate` | Multiple custom resources coexist |

### Group 2: Component Toggles (8 tests)

| # | Test Name | Description |
|---|-----------|-------------|
| 2.1 | `test_toggled_off_component_mass_still_counted` | Disabled components contribute mass only |
| 2.2 | `test_toggled_off_component_no_hp_contribution` | Disabled components don't contribute HP |
| 2.3 | `test_toggled_off_component_no_strategic_movement` | Disabled engines don't contribute movement |
| 2.4 | `test_toggled_off_warp_drive_no_warp_capability` | Disabled warp drives give zero tonnage |
| 2.5 | `test_toggled_off_resource_storage_not_counted` | Disabled storage doesn't add capacity |
| 2.6 | `test_mixed_enabled_disabled_components` | Mix of enabled/disabled works correctly |
| 2.7 | `test_missing_toggle_defaults_to_enabled` | Missing toggles default to True |
| 2.8 | `test_toggled_off_custom_resource_consumption_not_counted` | Disabled custom consumption ignored |

### Group 3: Trigger Types (7 tests)

| # | Test Name | Description |
|---|-----------|-------------|
| 3.1 | `test_trigger_strategic_per_hex_accumulates_correctly` | Per-hex trigger goes to correct dict |
| 3.2 | `test_trigger_per_turn_accumulates_correctly` | Per-turn trigger goes to correct dict |
| 3.3 | `test_trigger_warp_jump_accumulates_correctly` | Warp trigger goes to correct dict |
| 3.4 | `test_different_triggers_dont_cross_buckets` | Same resource, different triggers, separate dicts |
| 3.5 | `test_trigger_per_turn_degrades_with_damage` | Damaged components reduce consumption |
| 3.6 | `test_trigger_warp_jump_requires_full_hp` | Warp costs zero when damaged |
| 3.7 | `test_trigger_unknown_type_ignored` | Unknown triggers safely ignored |

### Group 4: Custom Resources (5 tests)

| # | Test Name | Description |
|---|-----------|-------------|
| 4.1 | `test_custom_resource_type_in_storage` | Arbitrary resource in storage works |
| 4.2 | `test_custom_resource_per_hex_consumption` | Custom resource per-hex works |
| 4.3 | `test_custom_resource_per_turn_consumption` | Custom resource per-turn works |
| 4.4 | `test_custom_resource_warp_costs` | Custom resource warp costs work |
| 4.5 | `test_many_different_custom_resources_coexist` | 5+ custom resources work together |

### Group 5: Bug Documentation (3 tests)

| # | Test Name | Description |
|---|-----------|-------------|
| 5.1 | `test_empty_resource_type_creates_empty_string_key_bug` | **BUG DOC**: Empty resource creates '' key |
| 5.2 | `test_empty_resource_type_in_consumption_ignored` | Empty resource_type should be ignored |
| 5.3 | `test_none_resource_type_handled_safely` | None/missing resource_type safe |

### Group 6: Integration (3 tests)

| # | Test Name | Description |
|---|-----------|-------------|
| 6.1 | `test_damaged_toggled_component_full_mass_partial_stats` | Damaged AND toggled off combination |
| 6.2 | `test_all_resource_types_in_one_component` | Component with multiple resource abilities |
| 6.3 | `test_fallback_handles_new_generic_fields` | Fallback returns generic dict fields |

---

## 3. ShipInstance Tests

**File:** `tests/unit/strategy/test_ship_instance_proj08.py` (NEW)

**Total: 71 tests**

### Group 1: Component Toggles Field (2 tests)

| # | Test Name | Description |
|---|-----------|-------------|
| 1.1 | `test_component_toggles_field_initialized_empty` | Initializes with empty dict |
| 1.2 | `test_component_toggles_field_default_factory` | Multiple instances don't share dict |

### Group 2: set_component_enabled (5 tests)

| # | Test Name | Description |
|---|-----------|-------------|
| 2.1 | `test_set_component_enabled_enable` | Enabling stores True |
| 2.2 | `test_set_component_enabled_disable` | Disabling stores False |
| 2.3 | `test_set_component_enabled_multiple_components` | Multiple components independently |
| 2.4 | `test_set_component_enabled_overwrites_existing` | Setting twice overwrites |
| 2.5 | `test_set_component_enabled_invalidates_cache` | Changing toggle clears cache |

### Group 3: is_component_enabled (4 tests)

| # | Test Name | Description |
|---|-----------|-------------|
| 3.1 | `test_is_component_enabled_default_true` | Missing toggles default to True |
| 3.2 | `test_is_component_enabled_explicitly_true` | Retrieves explicitly True |
| 3.3 | `test_is_component_enabled_explicitly_false` | Retrieves explicitly False |
| 3.4 | `test_is_component_enabled_after_set` | Reflects set_component_enabled |

### Group 4: get_resource_capacity (5 tests)

| # | Test Name | Description |
|---|-----------|-------------|
| 4.1 | `test_get_resource_capacity_fuel` | Retrieves fuel capacity |
| 4.2 | `test_get_resource_capacity_energy` | Retrieves energy capacity |
| 4.3 | `test_get_resource_capacity_custom_resource` | Works with arbitrary resources |
| 4.4 | `test_get_resource_capacity_unknown_resource` | Returns 0 for unknown |
| 4.5 | `test_get_resource_capacity_zero_capacity` | Returns 0 when empty |

### Group 5: get_current_resource (4 tests)

| # | Test Name | Description |
|---|-----------|-------------|
| 5.1 | `test_get_current_resource_returns_default_when_full` | Returns max when not in levels |
| 5.2 | `test_get_current_resource_returns_current_when_partial` | Returns actual level when tracked |
| 5.3 | `test_get_current_resource_with_all_types` | Works for fuel, energy, ammo |
| 5.4 | `test_get_current_resource_custom_resource` | Works with custom resources |

### Group 6: consume_resource (7 tests)

| # | Test Name | Description |
|---|-----------|-------------|
| 6.1 | `test_consume_resource_success` | Consumes when sufficient |
| 6.2 | `test_consume_resource_insufficient_fails` | Returns False when insufficient |
| 6.3 | `test_consume_resource_exact_amount` | Can consume exactly remaining |
| 6.4 | `test_consume_resource_zero_amount` | Zero consumption always succeeds |
| 6.5 | `test_consume_resource_multiple_types` | Different types consumed independently |
| 6.6 | `test_consume_resource_custom_type` | Works with custom resources |
| 6.7 | `test_consume_resource_when_not_tracked` | Uses max capacity as starting point |

### Group 7: get_all_resource_costs_per_hex (4 tests)

| # | Test Name | Description |
|---|-----------|-------------|
| 7.1 | `test_get_all_resource_costs_per_hex_empty` | Returns empty dict when no costs |
| 7.2 | `test_get_all_resource_costs_per_hex_fuel_only` | Returns single resource dict |
| 7.3 | `test_get_all_resource_costs_per_hex_multiple_resources` | Returns multiple resource dict |
| 7.4 | `test_get_all_resource_costs_per_hex_custom_resource` | Works with custom resources |

### Group 8: get_all_resource_costs_per_turn (4 tests)

| # | Test Name | Description |
|---|-----------|-------------|
| 8.1 | `test_get_all_resource_costs_per_turn_empty` | Returns empty dict when no costs |
| 8.2 | `test_get_all_resource_costs_per_turn_single_resource` | Returns single per-turn cost |
| 8.3 | `test_get_all_resource_costs_per_turn_multiple_resources` | Returns multiple per-turn costs |
| 8.4 | `test_get_all_resource_costs_per_turn_custom_resource` | Works with custom resources |

### Group 9: get_warp_resource_costs (5 tests)

| # | Test Name | Description |
|---|-----------|-------------|
| 9.1 | `test_get_warp_resource_costs_empty` | Returns empty when no warp |
| 9.2 | `test_get_warp_resource_costs_energy_only` | Returns energy warp cost |
| 9.3 | `test_get_warp_resource_costs_fuel_and_energy` | Returns both fuel and energy |
| 9.4 | `test_get_warp_resource_costs_custom_resource` | Works with custom resources |
| 9.5 | `test_get_warp_resource_costs_damaged_warp_drive` | Returns zero when damaged |

### Group 10: Cache Invalidation (3 tests)

| # | Test Name | Description |
|---|-----------|-------------|
| 10.1 | `test_cache_invalidation_on_set_component_enabled` | Cache cleared on toggle |
| 10.2 | `test_cache_recalculated_after_toggle` | Stats recalculated on next access |
| 10.3 | `test_cache_not_invalidated_on_other_changes` | Cache not invalidated by other methods |

### Group 11: Serialization - to_dict (3 tests)

| # | Test Name | Description |
|---|-----------|-------------|
| 11.1 | `test_to_dict_includes_component_toggles_empty` | Serializes empty toggles |
| 11.2 | `test_to_dict_includes_component_toggles_with_values` | Serializes toggles with values |
| 11.3 | `test_to_dict_preserves_all_toggle_states` | All states preserved exactly |

### Group 12: Serialization - from_dict (4 tests)

| # | Test Name | Description |
|---|-----------|-------------|
| 12.1 | `test_from_dict_restores_component_toggles_empty` | Deserializes empty toggles |
| 12.2 | `test_from_dict_restores_component_toggles_with_values` | Deserializes toggles with values |
| 12.3 | `test_from_dict_missing_component_toggles_defaults_to_empty` | Old saves without toggles work |
| 12.4 | `test_from_dict_then_to_dict_round_trip` | Round-trip serialization correct |

### Group 13: Clone Preservation (4 tests)

| # | Test Name | Description |
|---|-----------|-------------|
| 13.1 | `test_clone_preserves_component_toggles_empty` | Clone has empty toggles |
| 13.2 | `test_clone_preserves_component_toggles_with_values` | Clone copies all toggles |
| 13.3 | `test_clone_toggles_are_independent_copies` | Modifying clone doesn't affect original |
| 13.4 | `test_clone_preserves_new_instance_id` | Clone gets new ID but same toggles |

### Group 14: Stats Integration (2 tests)

| # | Test Name | Description |
|---|-----------|-------------|
| 14.1 | `test_component_toggles_passed_to_stats_calculation` | Toggles passed to ShipStatsService |
| 14.2 | `test_disabled_component_affects_stats` | Disabling component changes returned stats |

### Group 15: Resource Method Interactions (3 tests)

| # | Test Name | Description |
|---|-----------|-------------|
| 15.1 | `test_get_resource_capacity_with_disabled_component` | Disabling affects capacity |
| 15.2 | `test_consume_resource_tracks_in_resource_levels` | consume_resource updates dict |
| 15.3 | `test_get_all_resource_costs_multiple_calls_consistent` | Multiple calls return same values |

### Group 16: Backward Compatibility (4 tests)

| # | Test Name | Description |
|---|-----------|-------------|
| 16.1 | `test_legacy_methods_still_work_get_current_fuel` | get_current_fuel() works |
| 16.2 | `test_legacy_methods_still_work_consume_fuel` | consume_fuel() works |
| 16.3 | `test_legacy_methods_still_work_get_current_energy` | get_current_energy() works |
| 16.4 | `test_legacy_methods_still_work_consume_energy` | consume_energy() works |

### Group 17: Edge Cases (4 tests)

| # | Test Name | Description |
|---|-----------|-------------|
| 17.1 | `test_consume_resource_negative_amount` | Negative amount handled safely |
| 17.2 | `test_get_resource_capacity_empty_stats` | Returns 0 when stats empty |
| 17.3 | `test_component_toggles_with_nonexistent_component` | Can toggle components not in design |
| 17.4 | `test_get_all_resource_costs_when_stats_missing_field` | Returns empty dict when field missing |

---

## 4. Fleet Tests

**File:** `tests/unit/strategy/test_fleet.py` (ADD TO EXISTING)

**Total: 42 tests**

### Group 1: Movement Resource Methods (16 tests)

| # | Test Name | Description |
|---|-----------|-------------|
| 1.1 | `test_movement_resource_costs_single_ship` | `get_movement_resource_costs()` single ship |
| 1.2 | `test_movement_resource_costs_multiple_ships` | Sums costs from multiple ships |
| 1.3 | `test_movement_resource_costs_mixed_resource_types` | Different resources from different ships |
| 1.4 | `test_movement_resource_costs_empty_fleet` | Empty fleet returns empty dict |
| 1.5 | `test_movement_resource_costs_legacy_string_ships_only` | String ships return empty dict |
| 1.6 | `test_has_resources_for_movement_sufficient_all_ships` | Returns True when all ships have enough |
| 1.7 | `test_has_resources_for_movement_insufficient_fuel_one_ship` | Returns False when one ship lacks fuel |
| 1.8 | `test_has_resources_for_movement_insufficient_energy_one_ship` | Returns False when one ship lacks energy |
| 1.9 | `test_has_resources_for_movement_zero_cost_resources` | Ignores zero-cost resources |
| 1.10 | `test_has_resources_for_movement_empty_fleet` | Returns True for empty fleet |
| 1.11 | `test_consume_movement_resources_success_single_hex` | Consumes 1 hex correctly |
| 1.12 | `test_consume_movement_resources_success_multiple_hexes` | Multiplies cost by hexes |
| 1.13 | `test_consume_movement_resources_failure_atomicity` | Atomic - no consumption if any ship fails |
| 1.14 | `test_consume_movement_resources_atomicity_multi_resource` | Atomic across multiple resource types |
| 1.15 | `test_consume_movement_resources_zero_cost_resources` | Zero-cost not consumed |
| 1.16 | `test_consume_movement_resources_empty_fleet` | Returns True for empty fleet |

### Group 2: Warp Resource Methods (15 tests)

| # | Test Name | Description |
|---|-----------|-------------|
| 2.1 | `test_warp_resource_costs_single_ship` | `get_warp_resource_costs()` single ship |
| 2.2 | `test_warp_resource_costs_multiple_ships` | Sums warp costs from multiple ships |
| 2.3 | `test_warp_resource_costs_mixed_resource_types` | Different warp resources |
| 2.4 | `test_warp_resource_costs_empty_fleet` | Empty fleet returns empty dict |
| 2.5 | `test_warp_resource_costs_legacy_string_ships_only` | String ships return empty dict |
| 2.6 | `test_has_resources_for_warp_sufficient_all_ships` | Returns True when all ships have enough |
| 2.7 | `test_has_resources_for_warp_insufficient_energy_one_ship` | Returns False when one lacks energy |
| 2.8 | `test_has_resources_for_warp_insufficient_fuel_one_ship` | Returns False when one lacks fuel |
| 2.9 | `test_has_resources_for_warp_zero_cost_resources` | Ignores zero-cost |
| 2.10 | `test_has_resources_for_warp_empty_fleet` | Returns True for empty fleet |
| 2.11 | `test_consume_warp_resources_success_all_ships` | Consumes from all ships |
| 2.12 | `test_consume_warp_resources_failure_atomicity` | Atomic operation |
| 2.13 | `test_consume_warp_resources_atomicity_multi_resource` | Atomic across multiple resources |
| 2.14 | `test_consume_warp_resources_zero_cost_resources` | Zero-cost not consumed |
| 2.15 | `test_consume_warp_resources_empty_fleet` | Returns True for empty fleet |

### Group 3: Backward Compatibility (4 tests)

| # | Test Name | Description |
|---|-----------|-------------|
| 3.1 | `test_backward_compat_has_energy_for_warp_wrapper` | `has_energy_for_warp()` wraps correctly |
| 3.2 | `test_backward_compat_consume_warp_energy_wrapper` | `consume_warp_energy()` wraps correctly |
| 3.3 | `test_backward_compat_consume_fleet_fuel_wrapper` | `consume_fleet_fuel()` works |
| 3.4 | `test_backward_compat_legacy_warp_methods_still_work` | `get_warp_energy_cost()` etc. work |

### Group 4: Edge Cases (7 tests)

| # | Test Name | Description |
|---|-----------|-------------|
| 4.1 | `test_destroyed_ships_excluded_from_movement_calculation` | Destroyed ships ignored |
| 4.2 | `test_derelict_ships_excluded_from_warp_calculation` | Derelict ships ignored |
| 4.3 | `test_mixed_destroyed_and_combat_capable_ships` | Correctly filters mixed ships |
| 4.4 | `test_very_large_fleet` | 15+ ships performs correctly |
| 4.5 | `test_ships_with_no_resource_costs` | Empty cost dicts don't break aggregation |
| 4.6 | `test_floating_point_precision_in_resource_consumption` | Handles floating point values |
| 4.7 | `test_warp_capability_check_integration` | `can_use_warp()` integration |

---

## 5. TurnEngine Tests

**File:** `tests/strategy/test_turn_engine.py` (ADD TO EXISTING)

**Total: 22 tests**

### Group 1: Per-Turn Resource Consumption (5 tests)

| # | Test Name | Description |
|---|-----------|-------------|
| 1.1 | `test_per_turn_resource_consumption_single_ship` | Single ship depletes resource over 100 ticks |
| 1.2 | `test_per_turn_resource_consumption_multiple_resources` | Multiple resources deplete independently |
| 1.3 | `test_per_turn_resource_consumption_multiple_ships_in_fleet` | Each ship consumes independently |
| 1.4 | `test_per_turn_consumption_non_combat_ships_skipped` | Non-combat ships not processed |
| 1.5 | `test_per_turn_consumption_zero_cost_components_ignored` | Zero cost components skipped |

### Group 2: Resource Depletion (3 tests)

| # | Test Name | Description |
|---|-----------|-------------|
| 2.1 | `test_resource_depletion_during_tick_returns_false` | `consume_resource()` returns False when insufficient |
| 2.2 | `test_resource_depletion_triggers_auto_disable` | Auto-disable called on depletion |
| 2.3 | `test_no_auto_disable_for_non_per_turn_resources` | Only per_turn trigger components disabled |

### Group 3: Auto-Disable Logic (6 tests)

| # | Test Name | Description |
|---|-----------|-------------|
| 3.1 | `test_auto_disable_finds_components_with_per_turn_trigger` | Identifies and disables correct components |
| 3.2 | `test_auto_disable_multiple_components_same_resource` | All matching components disabled |
| 3.3 | `test_auto_disable_skips_unregistered_components` | Handles missing component gracefully |
| 3.4 | `test_auto_disable_handles_layer_formats` | Handles both list and dict layer formats |
| 3.5 | `test_auto_disable_invalidates_stats_cache` | Cache invalidated after disable |
| 3.6 | `test_auto_disable_logs_info_message` | Logs info when disabling |

### Group 4: Full Turn Integration (3 tests)

| # | Test Name | Description |
|---|-----------|-------------|
| 4.1 | `test_full_turn_depletes_per_turn_resources_completely` | 100 ticks depletes budget |
| 4.2 | `test_full_turn_does_not_overconsume_resources` | Resources can't go negative |
| 4.3 | `test_per_turn_and_movement_resources_both_consumed` | Both consumption types coexist |

### Group 5: Movement Gating (3 tests)

| # | Test Name | Description |
|---|-----------|-------------|
| 5.1 | `test_movement_requires_generic_resources` | Movement blocked if lacking any resource |
| 5.2 | `test_generic_movement_resource_consumption` | Consumes via `consume_movement_resources()` |
| 5.3 | `test_warp_uses_generic_methods` | Warp uses generic has/consume methods |

### Group 6: Component Toggle Integration (2 tests)

| # | Test Name | Description |
|---|-----------|-------------|
| 6.1 | `test_disabled_component_not_consumed_per_turn` | Disabled components don't consume |
| 6.2 | `test_auto_disabled_component_reenabled_via_manual_toggle` | Player can re-enable after auto-disable |

---

## 6. Integration Tests

**File:** `tests/integration/test_resource_system.py` (NEW)

**Total: 8 tests**

| # | Test Name | Description |
|---|-----------|-------------|
| 1 | `test_custom_resource_type_full_pipeline` | JSON → component → ship → fleet end-to-end |
| 2 | `test_per_turn_consumption_across_full_turn` | 100-tick depletion correct |
| 3 | `test_auto_disable_component_chain_on_resource_depletion` | Depletion → disable → stats recalc chain |
| 4 | `test_warp_jump_uses_resource_consumption_trigger` | Warp uses `trigger: 'warp_jump'` not legacy field |
| 5 | `test_movement_with_multi_resource_consumption` | Fuel + custom resource movement works |
| 6 | `test_backward_compat_load_old_save_without_component_toggles` | Old saves load correctly |
| 7 | `test_component_toggle_affects_movement_and_warp` | Toggle engine/warp affects capabilities |
| 8 | `test_fleet_mixed_legacy_and_new_ship_instances` | Mixed string/ShipInstance fleet works |

---

## 7. Common Fixtures

### Resource Registry Fixtures

```python
@pytest.fixture
def reset_resource_registry():
    """Clear and reset resource registry between tests."""
    RegistryManager.instance().resources.clear()
    yield
    RegistryManager.instance().resources.clear()

@pytest.fixture
def temp_resources_json(tmp_path):
    """Create temporary resources.json for testing."""
    def _create(resources_list):
        filepath = tmp_path / "resources.json"
        data = {"resources": [{"id": r} for r in resources_list]}
        filepath.write_text(json.dumps(data))
        return str(filepath)
    return _create

@pytest.fixture
def custom_resource_registry(reset_resource_registry, temp_resources_json):
    """Registry with custom 'glag' resource."""
    filepath = temp_resources_json(["fuel", "energy", "ammo", "glag"])
    load_resources(filepath)
    return RegistryManager.instance()
```

### Ship/Fleet Fixtures

```python
@pytest.fixture
def ship_with_per_turn_component():
    """ShipInstance with a per-turn energy consumption component."""
    design_data = {
        'layers': {
            'systems': [{'id': 'test_sensor_array'}]
        }
    }
    # Mock component in registry with per_turn trigger
    return ShipInstance(design_data=design_data, ...)

@pytest.fixture
def fleet_with_resource_ships(ship_with_per_turn_component):
    """Fleet containing ships with various resource consumption patterns."""
    fleet = Fleet(...)
    fleet.add_ship(ship_with_per_turn_component)
    return fleet

@pytest.fixture
def mock_component_registry():
    """Mock component registry with test components."""
    components = {
        'test_sensor_array': MockComponent(
            id='test_sensor_array',
            abilities={
                'ResourceConsumption': [
                    {'resource': 'energy', 'amount': 100, 'trigger': 'per_turn'}
                ]
            }
        )
    }
    with patch('game.core.registry.get_component_registry', return_value=components):
        yield components
```

### Stats/Design Fixtures

```python
@pytest.fixture
def make_design_data():
    """Factory for creating design_data with components."""
    def _make(components_by_layer: dict) -> dict:
        layers = {}
        for layer_name, comp_ids in components_by_layer.items():
            layers[layer_name] = [{'id': cid} for cid in comp_ids]
        return {'layers': layers}
    return _make

@pytest.fixture
def ship_stats_with_custom_resources():
    """Mock stats with custom resource types."""
    return {
        'max_hp': 100,
        'mass': 500,
        'resource_storage': {'fuel': 500, 'energy': 300, 'glag': 100},
        'resource_consumption_per_hex': {'fuel': 10, 'glag': 5},
        'resource_consumption_per_turn': {'energy': 50},
        'warp_resource_costs': {'energy': 1000},
        'strategic_movement': 100,
        'warp_max_tonnage': 5000,
        # Legacy fields
        'max_fuel': 500,
        'max_energy': 300,
        'max_ammo': 0,
        'strategic_fuel_per_hex': 10,
        'warp_energy_cost': 1000,
        'warp_fuel_cost': 0,
    }
```

---

## Implementation Priority

### Phase 1: Critical Path (Week 1)
1. Resource Registry Tests (Group 4: Data Accumulation Bug)
2. ShipStatsService Tests (Group 2: Component Toggles, Group 3: Trigger Types)
3. TurnEngine Tests (Group 1: Per-Turn Consumption, Group 3: Auto-Disable)

### Phase 2: Core Functionality (Week 2)
1. ShipInstance Tests (Groups 4-9: Resource Methods)
2. Fleet Tests (Groups 1-2: Movement and Warp Methods)
3. Integration Tests (Tests 1-5)

### Phase 3: Edge Cases & Compatibility (Week 3)
1. All remaining unit tests
2. Integration Tests (Tests 6-8)
3. Edge case and error handling tests

---

## Notes

- All tests should use the `reset_game_state` fixture to ensure isolation
- Mock component registry for unit tests, use real registry for integration tests
- Test both success and failure paths for all resource operations
- Verify cache invalidation explicitly in relevant tests
- Document any tests that expose bugs (prefix with "BUG DOC")
