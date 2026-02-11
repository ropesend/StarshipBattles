# Phase 1: Foundation Layer - CRITICAL + MAJOR

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-110 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Add unit tests for all Foundation layer CRITICAL and MAJOR coverage gaps (TCG-FND-001 through TCG-FND-010). Expected: ~100 new tests.

---

## Tasks

### Task 1.1: Hex Math Unit Tests (TCG-FND-001) [Medium]
**File:** `tests/unit/core/test_hex_math.py` (NEW)
**Source:** `game/core/hex_math.py` (250 LOC, 8 public functions + HexCoord class)
**Existing:** Integration tests only at `tests/integration/strategy/test_hex_math_strategy.py`
**Tests:** `pytest tests/unit/core/test_hex_math.py`

HexCoord class:
- [ ] `test_init_calculates_s_coordinate` - Verify s = -q - r for various inputs
- [ ] `test_init_negative_coords` - HexCoord(-5, -3) should have s=8
- [ ] `test_init_large_coords` - HexCoord(10000, -5000) maintains invariant
- [ ] `test_eq_identical_coords` - HexCoord(1,2) == HexCoord(1,2)
- [ ] `test_eq_different_coords` - HexCoord(1,2) != HexCoord(2,1)
- [ ] `test_eq_non_hexcoord` - HexCoord(1,2) != (1,2) returns False
- [ ] `test_hash_same_coords` - Two equal HexCoords have same hash
- [ ] `test_hash_usable_as_dict_key` - Can use HexCoord as dict key
- [ ] `test_hash_usable_in_set` - Can add/lookup HexCoord in set
- [ ] `test_repr_format` - repr returns "HexCoord(q, r)"
- [ ] `test_add_two_hexcoords` - (1,0) + (0,1) = (1,1)
- [ ] `test_add_returns_notimplemented` - HexCoord + int returns NotImplemented
- [ ] `test_sub_two_hexcoords` - (3,2) - (1,1) = (2,1)
- [ ] `test_sub_returns_notimplemented` - HexCoord - int returns NotImplemented
- [ ] `test_neighbors_returns_6` - center.neighbors() has exactly 6 elements
- [ ] `test_neighbors_are_adjacent` - All neighbors are distance 1 from center
- [ ] `test_neighbors_off_center` - Neighbors of (5,3) are correct

hex_distance:
- [ ] `test_distance_same_coord` - distance(a, a) == 0
- [ ] `test_distance_adjacent` - distance to neighbor == 1
- [ ] `test_distance_symmetric` - distance(a,b) == distance(b,a)
- [ ] `test_distance_known_value` - distance((0,0), (2,3)) == 5
- [ ] `test_distance_negative_coords` - distance((-3,2), (3,-2)) works correctly

hex_ring:
- [ ] `test_ring_radius_0` - Returns [HexCoord(0,0)]
- [ ] `test_ring_radius_1` - Returns exactly 6 hexes, all at distance 1
- [ ] `test_ring_radius_3` - Returns exactly 18 hexes (6*3), all at distance 3
- [ ] `test_ring_no_duplicates` - No duplicate coordinates in ring

hex_lerp:
- [ ] `test_lerp_t0_returns_start` - hex_lerp(a, b, 0) == a
- [ ] `test_lerp_t1_returns_end` - hex_lerp(a, b, 1) == b
- [ ] `test_lerp_t05_returns_midpoint` - hex_lerp((0,0), (4,0), 0.5) == (2,0)
- [ ] `test_lerp_same_start_end` - hex_lerp(a, a, 0.5) == a

hex_linedraw:
- [ ] `test_linedraw_same_point` - Returns [a] when a == b
- [ ] `test_linedraw_adjacent` - Returns [a, b] for adjacent hexes
- [ ] `test_linedraw_length` - Line from (0,0) to (3,0) has 4 points (N+1)
- [ ] `test_linedraw_all_adjacent` - Each consecutive pair is adjacent

hex_to_pixel / pixel_to_hex:
- [ ] `test_to_pixel_origin` - (0,0) -> (0, 0)
- [ ] `test_to_pixel_known_value` - (1,0) with size=10 -> (15, 8.66)
- [ ] `test_pixel_roundtrip` - pixel_to_hex(hex_to_pixel(h, s), s) == h for various h
- [ ] `test_pixel_to_hex_rounding` - Fractional pixels round to nearest hex

hex_to_dict / hex_from_dict:
- [ ] `test_to_dict_format` - Returns {'q': q, 'r': r}
- [ ] `test_from_dict_creates_hexcoord` - Creates correct HexCoord
- [ ] `test_serialization_roundtrip` - hex_from_dict(hex_to_dict(h)) == h

**Estimated tests: ~35**

---

### Task 1.2: AI Behaviors Unit Tests (TCG-FND-002) [Complex]
**File:** `tests/unit/ai/test_behavior_units.py` (NEW)
**Source:** `game/ai/behaviors.py` (514 LOC, 13 behavior classes)
**Existing:** Scattered tests in `test_ai_behaviors.py`, `test_advanced_behaviors.py` - check for overlap
**Tests:** `pytest tests/unit/ai/test_behavior_units.py`

Setup: Create mock controller fixture with:
- `controller.ship.get_position()` -> Vector2
- `controller.ship.get_weapon_range()` -> float
- `controller.ship.get_rotation()` -> float
- `controller.navigate_to(pos, stop_dist, precise)` -> None
- `controller.check_avoidance()` -> Optional[Vector2]
- `controller.get_engage_distance_multiplier(policy)` -> float

AIBehavior base:
- [ ] `test_base_init_stores_controller` - controller accessible
- [ ] `test_base_enter_is_noop` - enter() does not raise
- [ ] `test_base_update_raises_not_implemented` - update() raises NotImplementedError

RamBehavior:
- [ ] `test_ram_navigates_to_target_position` - navigate_to called with target.position, stop_dist=0
- [ ] `test_ram_precise_is_false` - precise=False in navigate_to call

FleeBehavior:
- [ ] `test_flee_moves_away_from_target` - Navigates to position opposite target
- [ ] `test_flee_fire_while_retreating_default_false` - set_trigger_pulled(False)
- [ ] `test_flee_fire_while_retreating_true` - set_trigger_pulled(True) when strategy says so
- [ ] `test_flee_zero_distance_uses_default_vector` - When at same position as target, uses Vector2(1,0)

KiteBehavior:
- [ ] `test_kite_closes_in_when_too_far` - navigate_to with target position
- [ ] `test_kite_backs_off_when_too_close` - navigate_to away from target
- [ ] `test_kite_min_spacing_enforced` - opt_dist >= MIN_SPACING
- [ ] `test_kite_collision_avoidance_overrides` - When check_avoidance returns pos, navigates there
- [ ] `test_kite_collision_avoidance_disabled` - When avoid_collisions=False, skips check
- [ ] `test_kite_zero_distance_uses_default_vector` - Same position fallback

AttackRunBehavior:
- [ ] `test_attack_run_init_state_approach` - Initial state is 'approach'
- [ ] `test_attack_run_enter_resets_state` - enter() resets to 'approach', timer=0
- [ ] `test_attack_run_approach_navigates_to_target` - Approach phase navigates toward target
- [ ] `test_attack_run_transitions_to_retreat` - When close enough, switches to retreat
- [ ] `test_attack_run_retreat_flees_away` - Retreat phase moves away from target
- [ ] `test_attack_run_retreat_timer_decrements` - Timer decreases by TICK_DURATION each update
- [ ] `test_attack_run_transitions_back_to_approach` - After timer and distance, returns to approach
- [ ] `test_attack_run_custom_distances` - Strategy dict overrides approach/retreat distances

FormationBehavior:
- [ ] `test_formation_dead_master_exits_formation` - ship.set_in_formation(False) when master dead
- [ ] `test_formation_derelict_master_exits` - Same for derelict master
- [ ] `test_formation_no_master_exits` - Same for None master
- [ ] `test_formation_in_range_matches_rotation` - In drift zone: snaps to master angle
- [ ] `test_formation_out_of_range_navigates` - Out of drift zone: navigates to predicted position
- [ ] `test_formation_fixed_rotation_mode` - Offset doesn't rotate with master

OrbitBehavior:
- [ ] `test_orbit_no_target_returns_early` - No action when target is None
- [ ] `test_orbit_zero_distance_returns_early` - No action when at same position
- [ ] `test_orbit_too_close_adds_outward_component` - Move outward when too close
- [ ] `test_orbit_too_far_adds_inward_component` - Move inward when too far
- [ ] `test_orbit_in_range_pure_tangent` - Pure tangent movement at correct distance

Test behaviors (light coverage):
- [ ] `test_do_nothing_disables_firing` - set_trigger_pulled(False)
- [ ] `test_stationary_fire_does_nothing` - No navigation calls
- [ ] `test_straight_line_thrusts_forward` - thrust_forward called
- [ ] `test_rotate_only_rotates` - rotate(direction) called, no thrust
- [ ] `test_erratic_changes_direction` - Direction changes over time

**Estimated tests: ~35**

---

### Task 1.3: Resource Loading Error Paths (TCG-FND-003) [Medium]
**File:** `tests/unit/core/test_resources.py` (NEW)
**Source:** `game/core/resources.py` (143 LOC)
**Tests:** `pytest tests/unit/core/test_resources.py`

_get_default_resources:
- [ ] `test_default_resources_has_fuel_energy_ammo` - Returns dict with all 3 resource types

_resolve_resource_path:
- [ ] `test_resolve_existing_file` - Returns path when file exists at given location
- [ ] `test_resolve_absolute_fallback` - Tries absolute path when relative fails
- [ ] `test_resolve_nonexistent_returns_none` - Returns None when file doesn't exist

load_resources_data (success + error paths):
- [ ] `test_load_resources_data_success` - Parses valid JSON into dict keyed by ID
- [ ] `test_load_resources_data_file_not_found` - Returns defaults on FileNotFoundError
- [ ] `test_load_resources_data_invalid_json` - Returns defaults on JSONDecodeError
- [ ] `test_load_resources_data_permission_error` - Returns defaults on PermissionError
- [ ] `test_load_resources_data_malformed_data` - Returns defaults on TypeError
- [ ] `test_load_resources_data_no_file_returns_defaults` - Returns defaults when path resolves to None
- [ ] `test_load_resources_data_empty_resources_list` - Returns empty dict for empty resources array

load_resources (registry integration):
- [ ] `test_load_resources_updates_registry` - Registry populated on success
- [ ] `test_load_resources_file_not_found_uses_defaults` - Registry gets defaults
- [ ] `test_load_resources_invalid_json_uses_defaults` - Registry gets defaults
- [ ] `test_load_resources_missing_file_uses_defaults` - Unresolvable path uses defaults

**Estimated tests: ~14**

---

### Task 1.4: Input Mapper Coverage Gaps (TCG-FND-004) [Medium]
**File:** `tests/unit/core/test_input_mapper.py` (EXPAND existing)
**Source:** `game/core/input_mapper.py` (379 LOC)
**Tests:** `pytest tests/unit/core/test_input_mapper.py`

Conflict detection:
- [ ] `test_get_conflicts_same_key_overlapping_context` - Fleet/strategy contexts conflict
- [ ] `test_get_conflicts_same_key_nonoverlapping_context` - build_queue/transfer don't conflict
- [ ] `test_get_conflicts_global_overlaps_everything` - Global context conflicts with all
- [ ] `test_get_conflicts_no_conflicts_for_different_keys` - Different keys never conflict
- [ ] `test_get_conflicts_with_modifiers` - Same key, same modifiers = conflict

Context overlap:
- [ ] `test_contexts_overlap_global_always_true` - global overlaps with any context
- [ ] `test_contexts_overlap_fleet_strategy` - fleet and strategy overlap
- [ ] `test_contexts_overlap_build_queue_isolated` - build_queue doesn't overlap fleet
- [ ] `test_contexts_overlap_none_context_always_true` - None context treated as overlap
- [ ] `test_contexts_overlap_same_context` - fleet overlaps with itself

Modifier handling:
- [ ] `test_extract_modifiers_ctrl` - KMOD_CTRL -> frozenset({"ctrl"})
- [ ] `test_extract_modifiers_shift` - KMOD_SHIFT -> frozenset({"shift"})
- [ ] `test_extract_modifiers_alt` - KMOD_ALT -> frozenset({"alt"})
- [ ] `test_extract_modifiers_multiple` - KMOD_CTRL|KMOD_SHIFT -> frozenset({"ctrl", "shift"})
- [ ] `test_extract_modifiers_none` - 0 -> frozenset()

Lookup table:
- [ ] `test_build_lookup_multiple_actions_same_key` - Multiple actions indexed correctly
- [ ] `test_resolve_returns_first_matching_context` - Context filter picks correct action

**Estimated tests: ~17**

---

### Task 1.5: Paths Module Unit Tests (TCG-FND-005) [Medium]
**File:** `tests/unit/core/test_paths.py` (NEW)
**Source:** `game/core/paths.py` (134 LOC)
**Tests:** `pytest tests/unit/core/test_paths.py`

Path constants:
- [ ] `test_root_dir_exists` - Paths.ROOT_DIR is a real directory
- [ ] `test_data_dir_exists` - Paths.DATA_DIR is a real directory
- [ ] `test_asset_dir_exists` - Paths.ASSET_DIR is a real directory
- [ ] `test_game_dir_exists` - Paths.GAME_DIR is a real directory
- [ ] `test_data_dir_is_under_root` - DATA_DIR starts with ROOT_DIR
- [ ] `test_core_data_files_defined` - COMPONENTS_FILE, MODIFIERS_FILE etc. are non-empty strings
- [ ] `test_components_file_exists` - Paths.COMPONENTS_FILE is a real file

Pathlib accessors:
- [ ] `test_get_root_returns_path` - Returns pathlib.Path
- [ ] `test_get_data_dir_returns_path` - Returns pathlib.Path under root
- [ ] `test_get_assets_dir_returns_path` - Returns pathlib.Path
- [ ] `test_get_output_dir_returns_path` - Returns pathlib.Path
- [ ] `test_get_saves_dir_returns_path` - Returns pathlib.Path

**Estimated tests: ~12**

---

### Task 1.6: Screenshot Manager Unit Tests (TCG-FND-006) [Medium]
**File:** `tests/unit/core/test_screenshot_manager.py` (NEW)
**Source:** `game/core/screenshot_manager.py` (219 LOC)
**Tests:** `pytest tests/unit/core/test_screenshot_manager.py`

Note: All tests must mock pygame and use ScreenshotManager.reset() in teardown.

Singleton:
- [ ] `test_instance_returns_same_object` - Two calls return same instance
- [ ] `test_direct_init_raises_after_instance` - RuntimeError on second __init__
- [ ] `test_reset_allows_new_instance` - After reset(), instance() creates new

Capture (mocked):
- [ ] `test_capture_disabled_does_nothing` - No file ops when enabled=False
- [ ] `test_capture_no_surface_logs_warning` - Logs warning when surface is None
- [ ] `test_capture_with_label_includes_label` - Filename contains label
- [ ] `test_capture_region_clips_to_surface` - Region clipped to surface bounds
- [ ] `test_capture_region_outside_surface_logs_warning` - Zero-size clip logs warning
- [ ] `test_capture_io_error_handled` - pygame.error caught, no crash

Clipboard (mocked):
- [ ] `test_clipboard_tkinter_success` - Tkinter path works
- [ ] `test_clipboard_tkinter_failure_falls_back` - On Tkinter error, tries clip
- [ ] `test_clipboard_windows_fallback` - subprocess.run with clip called

**Estimated tests: ~12**

---

### Task 1.7: AI Controller Coverage Expansion (TCG-FND-007) [Medium]
**File:** `tests/unit/ai/test_ai_controller_unit.py` (NEW)
**Source:** `game/ai/controller.py` (480 LOC)
**Tests:** `pytest tests/unit/ai/test_ai_controller_unit.py`

- [ ] `test_get_engage_distance_max_range` - 'max_range' returns 1.0
- [ ] `test_get_engage_distance_ram` - 'ram' returns 0.0
- [ ] `test_get_engage_distance_numeric` - 0.8 returns 0.8
- [ ] `test_get_engage_distance_default` - Unknown string returns 1.0
- [ ] `test_behavior_selection_formation` - In formation -> 'formation' behavior
- [ ] `test_behavior_selection_flee` - HP below threshold -> 'flee' behavior
- [ ] `test_behavior_selection_policy` - Normal HP -> policy behavior (kite/ram/etc)
- [ ] `test_satellite_exception_no_movement` - Vehicle type 'Satellite' skips movement
- [ ] `test_dead_ship_no_action` - update() returns early for dead ship
- [ ] `test_find_target_returns_highest_scored` - Multiple enemies, returns best
- [ ] `test_find_target_no_enemies_returns_none` - Empty grid returns None

**Estimated tests: ~11**

---

### Task 1.8: Strategy Manager Error Paths (TCG-FND-008) [Medium]
**File:** `tests/unit/ai/test_strategy_manager_singleton.py` (EXPAND existing)
**Source:** `game/ai/strategy_manager.py` (159 LOC)
**Tests:** `pytest tests/unit/ai/test_strategy_manager_singleton.py`

- [ ] `test_resolve_strategy_missing_id_returns_default` - Unknown ID returns default strategy
- [ ] `test_get_targeting_policy_missing_returns_default` - Unknown ID returns default targeting
- [ ] `test_get_movement_policy_missing_returns_default` - Unknown ID returns default movement
- [ ] `test_resolve_strategy_assembles_all_parts` - Returned dict has 'definition', 'targeting', 'movement'
- [ ] `test_clear_resets_loaded_flag` - After clear(), ensure_loaded reloads
- [ ] `test_ensure_loaded_only_loads_once` - Second call is no-op
- [ ] `test_load_data_missing_files_returns_empty` - Missing JSON files -> empty policies

**Estimated tests: ~7**

---

### Task 1.9: Target Evaluator Edge Cases (TCG-FND-009) [Medium]
**File:** `tests/unit/ai/test_target_evaluator_edge_cases.py` (NEW)
**Source:** `game/ai/target_evaluator.py` (500+ LOC)
**Tests:** `pytest tests/unit/ai/test_target_evaluator_edge_cases.py`

- [ ] `test_evaluate_zero_weight_rule_ignored` - Rule with weight=0 contributes nothing
- [ ] `test_evaluate_required_flag_rejects_target` - Required rule with 0 score returns -inf
- [ ] `test_evaluate_empty_rules_returns_zero` - No rules returns base score 0
- [ ] `test_safe_distance_none_position` - Graceful fallback when position is None
- [ ] `test_distance_cache_used_when_provided` - Pre-computed distances used, not recalculated

**Estimated tests: ~5**

---

### Task 1.10: Research Service Edge Cases (TCG-FND-010) [Medium]
**File:** `tests/unit/research/test_research_service.py` (EXPAND existing)
**Source:** `game/research/systems/research_service.py` (231 LOC)
**Tests:** `pytest tests/unit/research/test_research_service.py`

- [ ] `test_process_turn_locked_node_decay` - Locked nodes decay chance but no progress
- [ ] `test_process_turn_max_chance_capped_at_95` - current_chance never exceeds 0.95
- [ ] `test_process_turn_zero_allocation_only_decays` - No RP -> only decay event
- [ ] `test_process_turn_breakthrough_resets_chance` - After breakthrough, chance = 0
- [ ] `test_process_turn_tech_levels_updated_mid_turn` - Breakthrough updates tech_levels for subsequent nodes
- [ ] `test_calculate_added_chance_zero_rp` - Returns 0.0
- [ ] `test_calculate_added_chance_positive_rp` - Returns volatility * ln(1+rp)
- [ ] `test_estimate_turns_zero_rp_returns_inf` - No investment -> infinite turns
- [ ] `test_estimate_turns_net_gain_zero_returns_inf` - Decay >= gain -> infinite

**Estimated tests: ~9**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] All new tests pass: `pytest tests/unit/core/test_hex_math.py tests/unit/ai/test_behavior_units.py tests/unit/core/test_resources.py tests/unit/core/test_paths.py tests/unit/core/test_screenshot_manager.py tests/unit/ai/test_ai_controller_unit.py tests/unit/ai/test_target_evaluator_edge_cases.py -v`
- [ ] Full test suite still passes: `pytest tests/ -n 12`
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
