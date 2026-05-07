# PROJ-334 Phase 0 — Coverage Gap Audit

**Generated:** 2026-05-04
**Source files audited:**
- `game/strategy/data/pathfinding.py` (503 LOC)
- `game/strategy/data/galaxy_system_generator.py` (354 LOC)

**Existing tests audited:**
- `tests/unit/strategy/pathfinding/test_basic_paths.py`
- `tests/unit/strategy/pathfinding/test_edge_cases.py`
- `tests/unit/strategy/pathfinding/test_hybrid_and_intercept.py`
- `tests/unit/strategy/pathfinding/test_intercept_recursion.py`
- `tests/unit/strategy/pathfinding/test_strip_start_hex.py`
- `tests/unit/strategy/data/test_intrinsic_rng_determinism.py`

Status legend: **Covered** = behavior pinned by an existing test. **Partial** = surface tested but the specific edge case is missing. **Uncovered** = no existing test exercises this behavior.

---

## Pathfinding coverage matrix

| Symbol / behavior | Status | Existing test(s) | Gap | Phase 1 test name |
|---|---|---|---|---|
| `strip_start_hex` — None path | Covered | `TestStripStartHex.test_none_path_returns_none` | — | (skip) |
| `strip_start_hex` — empty path | Covered | `TestStripStartHex.test_empty_path_returns_empty` | — | (skip) |
| `strip_start_hex` — match removes head | Covered | `TestStripStartHex.test_strips_matching_start_hex` | — | (skip) |
| `strip_start_hex` — no match preserves | Covered | `TestStripStartHex.test_preserves_path_when_start_differs` | — | (skip) |
| `strip_start_hex` — single-element match → [] | Covered | `TestStripStartHex.test_single_element_matching_returns_empty` | — | (skip) |
| `strip_start_hex` — tuple type preserved | Covered | `TestStripStartHex.test_works_with_tuple_path` | — | (skip) |
| `strip_start_hex` — list type preserved | Covered | `TestStripStartHex.test_preserves_list_type` | — | (skip) |
| `find_path_deep_space` — start == end | Covered | `TestDeepSpacePath.test_same_location_returns_single_hex` | — | (skip) |
| `find_path_deep_space` — adjacent | Covered | `TestDeepSpacePath.test_adjacent_hex_returns_two_points` | — | (skip) |
| `find_path_deep_space` — long path correctness | Covered | `TestPathfindingEdgeCases.test_very_long_path` | — | (skip) |
| `find_path_deep_space` — symmetric for reversed endpoints | **Uncovered** | — | No test asserts `len(deep_space(a,b)) == len(deep_space(b,a))` and identical reversed | `test_find_path_deep_space_path_is_symmetric_for_reversed_endpoints` |
| `find_path_interstellar` — same source/target | Covered | `TestInterstellarPath.test_same_system_returns_single_system` | — | (skip) |
| `find_path_interstellar` — direct neighbor | Covered | `TestInterstellarPath.test_adjacent_systems_path` | — | (skip) |
| `find_path_interstellar` — multi-hop | Covered | `TestInterstellarPath.test_multi_hop_path` | — | (skip) |
| `find_path_interstellar` — disconnected → None | Covered | `TestInterstellarPath.test_disconnected_systems_returns_none` + `TestPathfindingEdgeCases.test_galaxy_with_no_warp_points` | — | (skip) |
| `find_path_interstellar` — path order start→end | Covered | `TestInterstellarPath.test_path_order_is_correct` | — | (skip) |
| `find_path_interstellar` — chooses lower-cost route under two-path graph | **Uncovered** | None — fixture is a linear A-B-C graph; no diamond | A* cost-optimality is not exercised | `test_find_path_interstellar_chooses_lower_distance_route_when_two_paths_exist` |
| `get_system_at_hex` — exact match (O(1) fast path) | Covered | `TestSystemLocation.test_get_system_at_exact_location` | — | (skip) |
| `get_system_at_hex` — within radius | Covered | `TestSystemLocation.test_get_system_at_hex_nearby` | — | (skip) |
| `get_system_at_hex` — outside radius → None | Covered | `TestSystemLocation.test_get_system_at_hex_outside_radius` | — | (skip) |
| `get_system_at_hex` — closest of multiple | Covered | `TestSystemLocation.test_get_system_chooses_closest` | — | (skip) |
| `find_nearest_system` — ignores radius | Covered | `TestSystemLocation.test_find_nearest_system_always_finds_one` | — | (skip) |
| `find_nearest_system` — closest wins | Covered | `TestSystemLocation.test_find_nearest_system_chooses_closest` | — | (skip) |
| `find_nearest_system` — empty galaxy → None | Covered | `TestSystemLocation.test_find_nearest_system_empty_galaxy` | — | (skip) |
| `find_hybrid_path` — same system → deep-space | Covered | `TestHybridPath.test_same_system_uses_deep_space` | — | (skip) |
| `find_hybrid_path` — empty galaxy → deep-space | Covered | `TestPathfindingEdgeCases.test_empty_galaxy_systems` | — | (skip) |
| `find_hybrid_path` — fleet cannot warp → deep-space | Partial | `TestHybridPath.test_fleet_without_warp_uses_direct` | Asserts endpoints but not that path skips warp arrivals | `test_find_hybrid_path_falls_back_to_deep_space_when_fleet_cannot_warp` |
| `find_hybrid_path` — `can_warp` param overrides fleet | **Uncovered** | — | `can_warp` parameter never tested in isolation | `test_find_hybrid_path_can_warp_param_overrides_fleet_capability` |
| `find_hybrid_path` — interstellar disconnected → falls back to deep-space | **Uncovered** | — | Fallback branch when `find_path_interstellar` returns None mid-stitch is unexercised | `test_find_hybrid_path_falls_back_to_deep_space_when_systems_are_disconnected` |
| `find_hybrid_path` — missing reciprocal warp point → uses next_sys global location | **Uncovered** | — | Lines 280–285 (data-error branch) untested | `test_find_hybrid_path_appends_system_global_location_when_reciprocal_warp_point_missing` |
| `find_hybrid_path` — fleet=None defaults to warp-capable | Covered | `TestHybridPath.test_no_fleet_defaults_to_warp` | — | (skip) |
| `project_fleet_path` — delegates to service | Covered | `TestFleetPathProjection.test_delegates_to_navigation_service` | — | (skip) |
| `project_fleet_path` — passes `max_turns` | Covered | `TestFleetPathProjection.test_passes_max_turns_parameter` | — | (skip) |
| `calculate_intercept_point` — chaser speed 0 → target.location | Covered | `TestInterceptCalculation.test_zero_chaser_speed_returns_target_location` | — | (skip) |
| `calculate_intercept_point` — chaser speed negative → target.location | Covered | `TestPathfindingEdgeCases.test_negative_speed_fleet` | — | (skip) |
| `calculate_intercept_point` — empty target_path fallback | Partial | `TestInterceptCalculation.test_stationary_target_returns_current_location` | Stationary case covered, but "no intercept possible & target_path non-empty → returns last hex" is **Uncovered** | `test_calculate_intercept_point_returns_target_path_endpoint_when_no_intercept_possible` |
| `calculate_intercept_point` — early-exit on synchronization | **Uncovered** | — | Early-exit branch (`abs(chaser_turns - target_turn) < 0.1`) never asserted | `test_calculate_intercept_point_early_exits_on_perfect_synchronization` |
| `calculate_intercept_point` — accepts NavigationState | Covered | `TestInterceptCalculation.test_accepts_navigation_state_as_chaser` | — | (skip) |
| `calculate_intercept_point` — NavigationState gets id=-1 in proxy | Partial | Indirect via accepts-NavigationState | Specifically pinning the id=-1 logging-leak observation requires its own test | `test_calculate_intercept_point_uses_id_minus_one_for_navigationstate_chaser` |
| Cyclic intercept recursion guard | Covered | `TestMutualInterceptDoesNotRecurse.*` (4 tests) | — | (skip) |

**Pathfinding gap totals:** 23 Covered, 3 Partial, 7 Uncovered → **8 new tests** (one Partial — fleet-cannot-warp — already provides minimal pin so we add the stricter assertion as a NEW test rather than mutating existing).

---

## Galaxy system generator coverage matrix

| Symbol / behavior | Status | Existing test(s) | Gap | Phase 1 test name |
|---|---|---|---|---|
| `_apply_planet_intrinsic_abilities` — seeded determinism | Covered | `test_planet_intrinsic_rolls_deterministic_with_seeded_rng` | — | (skip) |
| `_apply_star_intrinsic_abilities` — seeded determinism | Covered | `test_star_intrinsic_rolls_deterministic_with_seeded_rng` | — | (skip) |
| `_apply_system_archetype` — seeded determinism | Covered | `test_system_archetype_rolls_deterministic_with_seeded_rng` | — | (skip) |
| `_apply_*_intrinsic_abilities` — different seeds differ | Covered | `test_different_seeds_produce_different_rolls` | — | (skip) |
| `_apply_intrinsic_abilities` — idempotent on pre-set abilities | **Uncovered** | — | Lines 268–269 skip-branch unexercised | `test_apply_intrinsic_abilities_is_idempotent_when_entity_has_existing_abilities` |
| `_apply_intrinsic_abilities` — no-op when types_data empty | **Uncovered** | — | Lines 263–264 unexercised | `test_apply_intrinsic_abilities_is_noop_when_types_data_empty` |
| `_apply_system_archetype` — idempotent when archetype pre-set | **Uncovered** | — | Lines 341–342 unexercised | `test_apply_system_archetype_is_idempotent_when_archetype_pre_set` |
| `_apply_system_archetype` — skips `void` key | **Uncovered** | — | Lines 347–349 unexercised | `test_apply_system_archetype_skips_void_archetype_key` |
| `_apply_system_archetype` — no-op when rng.random() > chance | **Uncovered** | — | Line 343 unexercised | `test_apply_system_archetype_is_noop_when_random_exceeds_chance` |
| `_load_json_or_empty` — missing path → {} | **Uncovered** | — | Helper untested | `test_load_json_or_empty_returns_empty_dict_when_path_missing` |
| `_load_json_or_empty` — narrows to dict_key | **Uncovered** | — | Helper untested | `test_load_json_or_empty_narrows_to_dict_key_when_provided` |
| `GalaxySystemGenerator.generate_planets` — early-return on no stars | **Uncovered** | — | Line 67–68 unexercised | `test_generate_planets_returns_early_when_system_has_no_stars` |
| `GalaxySystemGenerator.generate_planets` — sorts by orbit_distance, -mass | **Uncovered** | — | Line 73 unexercised | `test_generate_planets_sorts_by_orbit_distance_then_negative_mass` |
| `GalaxySystemGenerator.generate_planets` — registers each planet | **Uncovered** | — | Lines 80–82 unexercised | `test_generate_planets_registers_each_planet_with_galaxy` |
| `GalaxySystemGenerator.generate_storms` — no-op when storm_gen=None | **Uncovered** | — | Lines 97–98 unexercised | `test_generate_storms_is_noop_when_storm_generator_is_none` |
| `GalaxySystemGenerator.generate_storms` — assigns storms when storm_gen present | **Uncovered** | — | Lines 100–101 unexercised | `test_generate_storms_assigns_storms_when_storm_generator_present` |
| `GalaxySystemGenerator.generate_systems` — golden determinism (seed=42) | **Uncovered** | — | Master plan load-bearing | `test_generate_systems_with_seed_42_produces_canonical_galaxy` |
| `GalaxySystemGenerator.generate_systems` — same seed reproducible | **Uncovered** | — | — | `test_generate_systems_with_seed_42_is_reproducible_across_two_runs` |
| `GalaxySystemGenerator.generate_systems` — different seeds differ | **Uncovered** | — | Sanity check | `test_generate_systems_with_different_seeds_produces_different_galaxies` |
| `GalaxySystemGenerator.generate_systems` — count=0 returns [] | **Uncovered** | — | Loop never enters | `test_generate_systems_count_zero_returns_empty_list_and_does_not_mutate_galaxy` |
| `GalaxySystemGenerator.generate_systems` — saturation: stops after 10 failures | **Uncovered** | — | Lines 181–186 unexercised | `test_generate_systems_stops_after_max_consecutive_placement_failures` |
| `GalaxySystemGenerator.generate_systems` — failure counter resets on success | **Uncovered** | — | Line 189 unexercised | `test_generate_systems_resets_failure_counter_on_successful_placement` |
| `GalaxySystemGenerator.generate_systems` — saturated returns < count | **Uncovered** | — | — | `test_generate_systems_returns_fewer_than_count_when_galaxy_saturated` |
| `GalaxySystemGenerator.generate_systems` — uses RandomPlacementStrategy default | **Uncovered** | — | Line 134 unexercised | `test_generate_systems_uses_random_placement_strategy_when_none_provided` |
| `GalaxySystemGenerator.generate_systems` — default storm config when storm_gen present | **Uncovered** | — | Lines 137–143 unexercised | `test_generate_systems_uses_default_storm_blueprint_when_storm_gen_present_and_config_none` |
| `GalaxySystemGenerator.generate_systems` — no default storm config when storm_gen=None | **Uncovered** | — | Branch unexercised | `test_generate_systems_does_not_use_default_storm_config_when_storm_gen_is_none` |
| `GalaxySystemGenerator.generate_systems` — dual-RNG: storm/intrinsic seeds derived | **Uncovered** | — | Lines 162–169 unexercised | `test_generate_systems_derives_storm_and_intrinsic_seeds_from_parent_rng` |
| `GalaxySystemGenerator.generate_systems` — rng=None still runs | **Uncovered** | — | Else-branch unexercised | `test_generate_systems_with_rng_none_completes_without_error` |
| `GalaxySystemGenerator.__init__` | Implicitly covered | All `generate_*` tests construct one | — | (skip) |

**Generator gap totals:** 4 Covered (intrinsic determinism), 23 Uncovered → **23 new tests** (cluster heavily; many share fakes).

---

## Phase 1 plan summary

- **Pathfinding gap-fill:** 8 new tests across `test_basic_paths.py` (1), `test_edge_cases.py` (3), `test_hybrid_and_intercept.py` (4).
- **Galaxy system generator green-field:** 23 new tests in `tests/unit/strategy/data/test_galaxy_system_generator.py` (NEW file).
- **Total new tests:** 31 (slightly above the 24–30 estimate; helper coverage came in higher than projected).

## D-Observations surfaced during audit

| ID | File:Line | Observation |
|---|---|---|
| O-001 | `pathfinding.py:91-99` | `current_sys` first assigned at line 91 then immediately overwritten at line 106. Lines 91–99 are dead code with stale planning comments. Documented; not fixed (D-006). |
| O-002 | `pathfinding.py:128` | A* uses `hex_distance` for both G-cost (`new_cost`) and H-cost (heuristic). Heuristic is admissible (≤ true cost on warp-graph) but not consistent with the G-cost — overweights heuristic vs. typical A*. Documented; not fixed. |
| O-003 | `pathfinding.py:365` | `_extract_chaser_info` returns `id=-1` for `NavigationState` chasers. This `-1` leaks into the debug log at line 470. Documented; not fixed. |
| O-004 | `galaxy_system_generator.py:177` | `placement_strategy.sample_location` is called with the **parent** `rng` (not `intrinsic_rng` / `storm_rng`). Comment at lines 158–161 claims "preserves determinism of system placement"; actual implementation does preserve it because the parent RNG drives placement directly. The dual-RNG split is therefore correctly isolated to the *post-placement* storm + intrinsic streams. No bug; observation pinned by `test_generate_systems_derives_storm_and_intrinsic_seeds_from_parent_rng`. |
