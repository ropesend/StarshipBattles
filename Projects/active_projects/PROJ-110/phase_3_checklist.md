# Phase 3: Strategy Layer - CRITICAL + MAJOR

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-110 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Add unit tests for all Strategy layer CRITICAL and MAJOR coverage gaps (TCG-STR-001 through TCG-STR-008). Expected: ~90 new tests.

---

## Tasks

### Task 3.1: Radiation Physics Unit Tests (TCG-STR-001) [Simple]
**File:** `tests/unit/strategy/data/test_radiation_physics.py` (NEW)
**Source:** `game/strategy/data/physics.py` (57 LOC)
**Existing:** Integration test `tests/integration/strategy/test_radiation.py`
**Tests:** `pytest tests/unit/strategy/data/test_radiation_physics.py`

SectorEnvironment:
- [ ] `test_sector_environment_init` - Stores local_hex and system
- [ ] `test_sector_environment_calculate_radiation_delegates` - Calls calculate_incident_radiation

calculate_incident_radiation:
- [ ] `test_single_star_at_same_hex` - Distance clamped to 1.0, full intensity
- [ ] `test_single_star_distance_2` - Falloff = 1/2^2.1, spectrum scaled
- [ ] `test_single_star_distance_5` - Falloff = 1/5^2.1
- [ ] `test_two_stars_sum_contributions` - Total = star1_contribution + star2_contribution
- [ ] `test_zero_distance_clamped` - Star at same hex as target gets r=1.0
- [ ] `test_all_spectrum_bands_scaled` - All 9 bands get falloff applied
- [ ] `test_empty_stars_list` - Returns zero spectrum (all bands 0)

**Estimated tests: ~9**

---

### Task 3.2: Strategy Session Facade Unit Tests (TCG-STR-002) [Complex]
**File:** `tests/unit/strategy/facade/test_strategy_session_facade.py` (NEW)
**Source:** `game/strategy/facade/strategy_session_facade.py` (451 LOC)
**Existing:** `tests/integration/strategy/facade/test_facade_init.py` (basic delegation tests)
**Tests:** `pytest tests/unit/strategy/facade/test_strategy_session_facade.py`

Note: All tests use Mock GameSession. Focus on facade logic, not session internals.

Fleet queries:
- [ ] `test_get_fleet_found` - Returns FleetInfo DTO when fleet exists
- [ ] `test_get_fleet_not_found` - Returns None when fleet not in any empire
- [ ] `test_get_fleets_at_hex_multiple` - Returns list of FleetInfo for fleets at hex
- [ ] `test_get_fleets_at_hex_empty` - Returns [] when no fleets at hex
- [ ] `test_get_fleet_path_preview_found` - Delegates to session.preview_fleet_path
- [ ] `test_get_fleet_path_preview_not_found` - Returns None for unknown fleet
- [ ] `test_get_fleet_path_projection_found` - Delegates to session.get_fleet_path_projection
- [ ] `test_get_fleet_path_projection_not_found` - Returns [] for unknown fleet

System queries:
- [ ] `test_get_all_systems` - Returns SystemInfo list from galaxy.systems
- [ ] `test_get_system_at_hex_found` - Returns SystemInfo for hex with system
- [ ] `test_get_system_at_hex_not_found` - Returns None for empty hex

Planet queries:
- [ ] `test_get_planet_found` - Returns PlanetInfo DTO
- [ ] `test_get_planet_not_found` - Returns None for unknown planet_id
- [ ] `test_get_planets_at_hex_found` - Returns PlanetInfo list for system at hex
- [ ] `test_get_planets_at_hex_no_system` - Returns [] when no system at hex

Empire queries:
- [ ] `test_get_all_empires` - Returns EmpireInfo list
- [ ] `test_get_empire_found` - Returns EmpireInfo for valid ID
- [ ] `test_get_empire_not_found` - Returns None for unknown ID
- [ ] `test_get_empire_colonies` - Returns ColonySummary list
- [ ] `test_get_empire_colonies_not_found` - Returns [] for unknown empire
- [ ] `test_get_empire_fleets` - Returns FleetSummary list
- [ ] `test_get_empire_fleets_not_found` - Returns [] for unknown empire

Game state queries:
- [ ] `test_get_turn_number` - Returns session.turn_number
- [ ] `test_get_human_player_ids` - Returns list of human player empire IDs

Validation queries:
- [ ] `test_can_colonize_fleet_not_found` - Returns invalid result
- [ ] `test_can_colonize_planet_not_found` - Returns invalid result
- [ ] `test_can_colonize_delegates_to_turn_engine` - Valid fleet/planet delegates
- [ ] `test_can_move_to_fleet_not_found` - Returns invalid result
- [ ] `test_can_move_to_no_path` - Returns invalid when no path exists
- [ ] `test_can_move_to_valid_path` - Returns valid when path exists

Event queries:
- [ ] `test_get_turn_events_current_turn` - Delegates with current turn number
- [ ] `test_get_turn_events_specific_turn` - Delegates with specified turn
- [ ] `test_get_all_events` - Returns all events as dicts
- [ ] `test_get_events_by_category` - Filters by category

**Estimated tests: ~33**

---

### Task 3.3: Galaxy Placement and Region Classifier (TCG-STR-003) [Complex]
**File:** `tests/unit/strategy/generation/test_region_classifier.py` (NEW)
**Source:** `game/strategy/generation/region_classifier.py` (281 LOC)
**Existing:** Placement strategies tested in `test_placement_strategies.py`, but NO region classifier tests
**Tests:** `pytest tests/unit/strategy/generation/test_region_classifier.py`

RegionInfo:
- [ ] `test_region_info_dataclass` - region_id, region_type, name accessible

RegionClassifier init:
- [ ] `test_spiral_layout_detected` - _has_spiral=True for spiral_arm primitive
- [ ] `test_cluster_layout_detected` - _has_clusters=True for multiple radial primitives
- [ ] `test_empty_primitives_no_regions` - No primitives -> empty regions

Region building:
- [ ] `test_spiral_regions_include_arms` - Arms 0..N-1 as 'arm' regions
- [ ] `test_spiral_regions_include_core` - Core added when radial primitive present
- [ ] `test_cluster_regions_count` - One region per cluster center
- [ ] `test_ring_layout_regions` - Ring + Core regions

Spiral classification:
- [ ] `test_classify_origin_as_core` - (0,0) in spiral galaxy classified as core
- [ ] `test_classify_arm_point` - Point on arm returns correct arm index
- [ ] `test_classify_different_arms_different_ids` - Symmetric points get different arm IDs
- [ ] `test_classify_near_origin_fallback` - Very close to center returns core

Cluster classification:
- [ ] `test_classify_near_cluster_center` - Point near center gets that cluster ID
- [ ] `test_classify_equidistant_clusters` - Deterministic tie-breaking

Region neighbors:
- [ ] `test_spiral_adjacent_arms_are_neighbors` - Arm 0 neighbors Arm 1
- [ ] `test_spiral_arms_wrap_around` - Last arm neighbors first arm
- [ ] `test_spiral_core_neighbors_all_arms` - Core neighbors every arm
- [ ] `test_cluster_top3_neighbors` - Each cluster has up to 3 nearest neighbors
- [ ] `test_empty_regions_empty_neighbors` - No regions -> empty dict

Properties:
- [ ] `test_regions_property` - Returns list of RegionInfo
- [ ] `test_region_count_property` - Returns correct count
- [ ] `test_classify_no_regions_returns_0` - Default return when no regions

**Estimated tests: ~22**

---

### Task 3.4: Stars Module Unit Tests (TCG-STR-004) [Medium]
**File:** `tests/unit/strategy/data/test_stars.py` (NEW)
**Source:** `game/strategy/data/stars.py` (561 LOC)
**Tests:** `pytest tests/unit/strategy/data/test_stars.py`

Spectrum:
- [ ] `test_spectrum_init_all_bands` - All 9 bands stored
- [ ] `test_spectrum_get_total_output` - Sum of all bands
- [ ] `test_spectrum_to_dict` - Dict has all 9 band keys
- [ ] `test_spectrum_from_dict` - Reconstructs from dict
- [ ] `test_spectrum_serialization_roundtrip` - from_dict(to_dict()) preserves values

Star:
- [ ] `test_star_init` - All attributes stored
- [ ] `test_star_to_dict` - Includes all fields, star_type as string, color as list
- [ ] `test_star_from_dict` - Reconstructs Star with correct types
- [ ] `test_star_serialization_roundtrip` - from_dict(to_dict()) preserves all fields
- [ ] `test_star_location_default_origin` - Default location is HexCoord(0,0)

StarGenerator:
- [ ] `test_generate_mass_in_range` - Mass between 0.1 and 100.0 (seeded)
- [ ] `test_generate_mass_companion_less_than_primary` - Companion mass < primary
- [ ] `test_determine_type_returns_valid_type` - Returns StarType enum member
- [ ] `test_determine_type_low_mass_red_dwarf` - mass < 0.5 -> RED_DWARF
- [ ] `test_kelvin_to_rgb_hot_star` - High temp gives blue-white RGB
- [ ] `test_kelvin_to_rgb_cool_star` - Low temp gives red RGB
- [ ] `test_map_radius_small_star` - Small radius maps to 1-3 hexes
- [ ] `test_map_radius_compact_remnant` - Neutron/black hole maps to 0.5
- [ ] `test_generate_spectrum_has_9_bands` - All bands populated
- [ ] `test_generate_system_stars_single` - Most common: returns 1 star (seeded)
- [ ] `test_generate_system_stars_from_blueprint` - Blueprint controls count and mass range

**Estimated tests: ~21**

---

### Task 3.5: Planet Naming Unit Tests (TCG-STR-005) [Simple]
**File:** `tests/unit/strategy/data/test_planet_naming.py` (NEW)
**Source:** `game/strategy/data/planet_naming.py` (87 LOC)
**Tests:** `pytest tests/unit/strategy/data/test_planet_naming.py`

to_roman:
- [ ] `test_to_roman_1` - 1 -> "I"
- [ ] `test_to_roman_4` - 4 -> "IV"
- [ ] `test_to_roman_5` - 5 -> "V"
- [ ] `test_to_roman_9` - 9 -> "IX"
- [ ] `test_to_roman_10` - 10 -> "X"
- [ ] `test_to_roman_14` - 14 -> "XIV"
- [ ] `test_to_roman_39` - 39 -> "XXXIX" (max supported)
- [ ] `test_to_roman_parametrized` - Parametrize 1-39 with known values

assign_body_names:
- [ ] `test_assign_single_planet` - "SystemName I"
- [ ] `test_assign_multiple_planets_different_locations` - "I", "II", "III" by distance
- [ ] `test_assign_moons_at_same_location` - Primary gets "I", moons get "Ia", "Ib"
- [ ] `test_assign_sorts_by_mass` - Heaviest at location is primary
- [ ] `test_assign_sorts_locations_by_distance` - Closer to center gets lower numeral
- [ ] `test_assign_empty_bodies_list` - No crash on empty list

**Estimated tests: ~14**

---

### Task 3.6: Engine Interfaces Contract Tests (TCG-STR-006) [Medium]
**File:** `tests/unit/strategy/interfaces/test_engines_contracts.py` (NEW or EXPAND)
**Source:** `game/strategy/interfaces/engines.py` (471 LOC)
**Existing:** Check `tests/unit/strategy/interfaces/test_engine_interfaces.py` first
**Tests:** `pytest tests/unit/strategy/interfaces/test_engines_contracts.py`

Note: Must first check if `test_engine_interfaces.py` already covers this. If so, mark TCG-STR-006 as already-covered and skip.

Abstract method presence:
- [ ] `test_imovement_engine_has_collect_movements` - Abstract method exists
- [ ] `test_imovement_engine_has_apply_movements` - Abstract method exists
- [ ] `test_imovement_engine_has_calculate_next_hex` - Abstract method exists
- [ ] `test_iproduction_engine_has_process_construction_tick` - Abstract method exists
- [ ] `test_iproduction_engine_has_process_production` - Abstract method exists
- [ ] `test_iproduction_engine_has_process_fleet_production` - Abstract method exists
- [ ] `test_iorder_processor_has_process_instant_orders` - Abstract method exists
- [ ] `test_iorder_processor_has_process_end_turn_orders` - Abstract method exists
- [ ] `test_iconflict_engine_has_resolve_all_conflicts` - Abstract method exists
- [ ] `test_iresource_engine_has_process_per_turn_consumption` - Abstract method exists
- [ ] `test_ipopulation_engine_has_process_population_growth` - Abstract method exists
- [ ] `test_iresupply_engine_has_process_fuel_generation` - Abstract method exists
- [ ] `test_iresupply_engine_has_process_fleet_resupply` - Abstract method exists

Cannot instantiate:
- [ ] `test_cannot_instantiate_abstract_movement_engine` - TypeError on ABC instantiation
- [ ] `test_cannot_instantiate_abstract_production_engine` - TypeError
- [ ] `test_cannot_instantiate_abstract_conflict_engine` - TypeError

**Estimated tests: ~16**

---

### Task 3.7: QuickstartBuilder Unit Tests (TCG-STR-007) [Medium]
**File:** `tests/unit/strategy/test_quickstart_builder.py` (NEW)
**Source:** `game/strategy/quickstart_builder.py` (299 LOC)
**Tests:** `pytest tests/unit/strategy/test_quickstart_builder.py`

Fixture path functions:
- [ ] `test_get_quickstart_fixtures_dir_returns_path` - Returns Path object
- [ ] `test_get_quickstart_races_dir_under_fixtures` - Is subdir of fixtures
- [ ] `test_get_quickstart_designs_dir_under_fixtures` - Is subdir of fixtures

QuickstartBuilder.load_test_race:
- [ ] `test_load_test_race_valid_file` - Returns RaceConfig when file exists
- [ ] `test_load_test_race_missing_file` - Returns None when file doesn't exist
- [ ] `test_load_test_race_invalid_json` - Returns None on parse failure

QuickstartBuilder.build_1p_config:
- [ ] `test_build_1p_returns_game_config` - Returns GameConfig instance
- [ ] `test_build_1p_single_player` - Has exactly 1 player
- [ ] `test_build_1p_player_is_human` - Player has is_human=True
- [ ] `test_build_1p_custom_prefix` - save_name starts with custom prefix
- [ ] `test_build_1p_default_parameters` - galaxy_radius=8000, system_count=100

QuickstartBuilder.build_2p_config:
- [ ] `test_build_2p_has_two_players` - Has exactly 2 players
- [ ] `test_build_2p_both_human` - Both players have is_human=True

**Estimated tests: ~13**

---

### Task 3.8: Configuration Classes Tests (TCG-STR-008) [Simple]
**File:** `tests/unit/strategy/data/test_classification_config.py` (NEW)
**Source:** `game/strategy/data/classification_config.py` (145 LOC)
**Tests:** `pytest tests/unit/strategy/data/test_classification_config.py`

Note: Also check `race_point_budget.py` and `homeworld_presets.py` for existing tests.

ClassificationConfig defaults:
- [ ] `test_init_no_data_uses_defaults` - ClassificationConfig(None) uses hardcoded values
- [ ] `test_default_dwarf_max` - dwarf_max == 2.0e23
- [ ] `test_default_ice_dwarf_max_temp` - ice_dwarf_max == 170
- [ ] `test_default_vacuum_pressure` - vacuum == 500
- [ ] `test_default_arid_water` - arid == 0.20

ClassificationConfig from JSON:
- [ ] `test_init_with_json_data` - Loads thresholds from classification dict
- [ ] `test_json_overrides_defaults` - JSON values take precedence
- [ ] `test_partial_json_falls_back_to_defaults` - Missing keys use defaults
- [ ] `test_no_classification_key_uses_defaults` - Data without 'classification' key -> defaults

get_classification_config:
- [ ] `test_cached_config_returns_instance` - Returns ClassificationConfig
- [ ] `test_cached_config_fallback_on_error` - Returns default config on load error

**Estimated tests: ~11**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] All new tests pass: `pytest tests/unit/strategy/ -v --tb=short`
- [ ] Full test suite still passes: `pytest tests/ -n 12`
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
