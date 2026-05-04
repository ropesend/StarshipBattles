# PROJ-334 Phase 1 — Characterization tests for gap-list

**Status:** Pending (Phase 0 must complete first)
**Goal:** Add new tests for every Uncovered / Partial row in `findings/coverage_gap_audit.md`.

> All test names use the convention from `decisions.md` D-007: encode behavior in active voice. NO `test_basic_*` / `test_edge_*` / `test_misc_*`.

## Task 1A: `pathfinding.py` gap-fill tests

> Final list confirmed by Phase 0 audit. Below is the candidate list assuming each row is uncovered after audit; remove rows the audit shows as already-covered.

### `find_path_deep_space`
- [ ] `test_find_path_deep_space_returns_single_hex_when_start_equals_end`
- [ ] `test_find_path_deep_space_path_is_symmetric_for_reversed_endpoints`

### `find_path_interstellar`
- [ ] `test_find_path_interstellar_returns_start_only_when_target_equals_source`
- [ ] `test_find_path_interstellar_returns_none_when_target_in_disconnected_subgraph`
- [ ] `test_find_path_interstellar_returns_two_systems_for_direct_neighbor`
- [ ] `test_find_path_interstellar_chooses_lower_distance_route_when_two_paths_exist`
- [ ] `test_find_path_interstellar_path_starts_with_source_and_ends_with_target`

### `get_system_at_hex` / `find_nearest_system`
- [ ] `test_get_system_at_hex_uses_o1_fast_path_for_exact_match`
- [ ] `test_get_system_at_hex_returns_none_when_no_system_within_radius`
- [ ] `test_get_system_at_hex_returns_nearest_when_multiple_in_radius`
- [ ] `test_find_nearest_system_returns_none_for_empty_galaxy`

### `find_hybrid_path`
- [ ] `test_find_hybrid_path_falls_back_to_deep_space_when_fleet_cannot_warp`
- [ ] `test_find_hybrid_path_can_warp_param_overrides_fleet_capability`
- [ ] `test_find_hybrid_path_uses_deep_space_when_start_and_end_in_same_system`
- [ ] `test_find_hybrid_path_falls_back_to_deep_space_when_systems_are_disconnected`
- [ ] `test_find_hybrid_path_appends_system_global_location_when_reciprocal_warp_point_missing`

### `calculate_intercept_point`
- [ ] `test_calculate_intercept_point_returns_target_location_when_chaser_speed_is_zero`
- [ ] `test_calculate_intercept_point_returns_target_location_when_chaser_speed_is_negative`
- [ ] `test_calculate_intercept_point_returns_target_path_endpoint_when_no_intercept_possible`
- [ ] `test_calculate_intercept_point_early_exits_on_perfect_synchronization`
- [ ] `test_calculate_intercept_point_handles_navigationstate_chaser_with_id_minus_one`

### `strip_start_hex` (already heavily tested per `test_strip_start_hex.py`)
- [ ] _Confirm coverage in audit; expect zero gaps. Skip if all rows covered._

## Task 1B: `galaxy_system_generator.py` characterization tests

> NEW file: `tests/unit/strategy/data/test_galaxy_system_generator.py`.
> Hand-rolled fakes per D-005; no `unittest.mock`.

### Determinism contract (the load-bearing pair per task brief)
- [ ] `test_generate_systems_with_seed_42_produces_canonical_5_system_galaxy` — pin sorted `[(name, global_location)]` representation as inline golden. Galaxy radius 2000, count 5, min_dist 100.
- [ ] `test_generate_systems_with_seed_42_is_reproducible_across_two_runs` — same seed, two GalaxySystemGenerator instances → same output.
- [ ] `test_generate_systems_with_different_seeds_produces_different_galaxies` — seed=42 vs seed=43 → outputs differ.
- [ ] `test_generate_systems_seed_zero_is_valid` — seed=0 produces deterministic output.
- [ ] `test_generate_systems_with_seed_2_pow_32_minus_1_is_valid` — boundary seed.

### Dual-RNG seed derivation (the determinism-protecting design)
- [ ] `test_generate_systems_storm_rng_does_not_perturb_placement_stream` — same placement_strategy + same parent RNG seed produce identical placements regardless of whether storm generation runs.
- [ ] `test_generate_systems_intrinsic_rolls_use_separate_rng_from_placement` — verify by injecting fake placement_strategy that records its rng and asserting child stream isolation.

### Saturation / failure counter
- [ ] `test_generate_systems_returns_fewer_than_count_when_galaxy_saturated`
- [ ] `test_generate_systems_stops_after_10_consecutive_placement_failures`
- [ ] `test_generate_systems_resets_failure_counter_on_successful_placement`

### Parameter behavior
- [ ] `test_generate_systems_count_zero_returns_empty_list_and_does_not_mutate_galaxy`
- [ ] `test_generate_systems_count_one_skips_min_dist_check`
- [ ] `test_generate_systems_uses_random_placement_strategy_when_none_provided`
- [ ] `test_generate_systems_uses_default_storm_blueprint_when_storm_gen_present_and_config_none`
- [ ] `test_generate_systems_does_not_use_default_storm_config_when_storm_gen_is_none`

### `generate_planets` / `generate_storms`
- [ ] `test_generate_planets_returns_early_when_system_has_no_stars`
- [ ] `test_generate_planets_sorts_by_orbit_distance_then_negative_mass`
- [ ] `test_generate_planets_registers_each_planet_with_galaxy`
- [ ] `test_generate_storms_is_noop_when_storm_generator_is_none`

### Module-level helpers (only those not covered by `test_intrinsic_rng_determinism.py`)
- [ ] `test_load_json_or_empty_returns_empty_dict_when_path_missing`
- [ ] `test_load_json_or_empty_narrows_to_dict_key_when_provided`
- [ ] `test_apply_intrinsic_abilities_is_idempotent_when_entity_has_existing_abilities`
- [ ] `test_apply_intrinsic_abilities_is_noop_when_types_data_empty`
- [ ] `test_apply_system_archetype_is_idempotent_when_archetype_pre_set`
- [ ] `test_apply_system_archetype_skips_void_archetype_key`
- [ ] `test_apply_system_archetype_is_noop_when_random_exceeds_chance`

## Verification

- [ ] All listed tests added (minus rows the Phase 0 audit confirmed already-covered).
- [ ] `pytest tests/unit/strategy/pathfinding/ -x -q` green.
- [ ] `pytest tests/unit/strategy/data/test_galaxy_system_generator.py -x -q` green.
- [ ] `python Tools/test_sharded/test_sharded.py` green.
- [ ] `python Tools/lint_test_files.py` 0 violations.
- [ ] `decisions.md` D-Observations table populated with any oddities surfaced during testing.

## Phase Completion

- [ ] All Task 1A and 1B items checked.
- [ ] Per D-009, commits land in this order:
  1. `docs(334): coverage gap audit`
  2. `test(334): characterize GalaxySystemGenerator`
  3. `test(334): pathfinding gap-fill — basic_paths`
  4. `test(334): pathfinding gap-fill — edge_cases`
  5. `test(334): pathfinding gap-fill — hybrid_and_intercept`
- [ ] `Projects/projects_index.md` PROJ-334 → Awaiting Verification.
