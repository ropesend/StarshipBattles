# PROJ-336 Phase 1 — Per-file characterization tests

**Status:** Pending
**Goal:** Add unit-test characterization for the four strategy services per the
master-plan philosophy: pin behavior, do not fix bugs, do not refactor production.

## Task 1.1: `test_fleet_navigation_gaps.py` (gap-fill only — Decision D-001) [Medium]

**Production file:** `game/strategy/services/fleet_navigation_service.py` (759 LOC)
**New test file:** `tests/unit/strategy/services/test_fleet_navigation_gaps.py`
**Existing tests to NOT modify:** entire `tests/unit/strategy/fleet_navigation/` tree + the two existing files in `tests/unit/strategy/services/test_fleet_navigation_*.py`.

Behaviors to pin (estimate 6-8 tests):

- [ ] `test_resolve_warp_exit_returns_none_when_warp_point_hex_not_in_index` — `_resolve_warp_exit` early-return path 1.
- [ ] `test_resolve_warp_exit_returns_none_when_local_warp_point_not_found_in_source_system` — early-return path 2.
- [ ] `test_resolve_warp_exit_returns_none_when_destination_system_does_not_exist` — early-return path 3.
- [ ] `test_resolve_warp_exit_falls_back_to_destination_system_center_when_no_reciprocal_warp_point` — fallback branch.
- [ ] `test_consume_ticks_crosses_turn_boundary_when_moves_left_exhausted` — pure static method; pin off-by-one.
- [ ] `test_consume_ticks_stops_at_max_turns_even_with_remaining_ticks` — termination condition.
- [ ] `test_project_path_returns_empty_when_fleet_id_already_in_projection_guard` — re-entrancy guard observable behavior (use `_get_projection_stack().add(fleet.id)` then call `project_path`).
- [ ] `test_calculate_fleet_next_hex_pops_invalid_move_to_fleet_target_before_compute` — pins the early-pop branch in the mutation bridge.

## Task 1.2: `test_system_destroyer.py` (full characterization) [Medium]

**Production file:** `game/strategy/services/system_destroyer.py` (179 LOC)
**New test file:** `tests/unit/strategy/services/test_system_destroyer.py`

Behaviors to pin (estimate 11-13 tests):

`collect_system_contents`:
- [ ] `test_collect_snapshots_planets_and_stars_from_system`
- [ ] `test_collect_includes_fleet_strictly_inside_radius` (fleet at distance 49 included)
- [ ] `test_collect_excludes_fleet_at_exact_radius_boundary` (fleet at distance 50 excluded — `<`, not `<=`)
- [ ] `test_collect_excludes_fleet_outside_radius`
- [ ] `test_collect_with_empty_empires_returns_zero_fleets`
- [ ] `test_collect_with_empire_having_no_fleets_returns_zero_fleets`
- [ ] `test_collect_with_custom_radius_kwarg_overrides_default` (e.g. radius=10)
- [ ] `test_collect_returns_frozen_plan` (pin `dataclasses.FrozenInstanceError` on `plan.planets = ()`)

`destroy_system`:
- [ ] `test_destroy_removes_planets_from_owner_empire_colonies_and_unregisters`
- [ ] `test_destroy_skips_colony_removal_when_planet_owner_id_is_none`
- [ ] `test_destroy_calls_remove_fleet_with_event_bus_passthrough` (verify event_bus arg)
- [ ] `test_destroy_clears_system_stars_when_remove_stars_true`
- [ ] `test_destroy_leaves_system_stars_intact_when_remove_stars_false_and_reports_zero_stars_removed`
- [ ] `test_destroy_collects_ship_names_into_result` (and skips ships missing `.name`)

## Task 1.3: `test_fleet_cargo_projector.py` (full characterization) [Small]

**Production file:** `game/strategy/services/fleet_cargo_projector.py` (64 LOC)
**New test file:** `tests/unit/strategy/services/test_fleet_cargo_projector.py`

Behaviors to pin (estimate 9-11 tests):

- [ ] `test_returns_current_when_order_queue_empty`
- [ ] `test_load_with_explicit_amount_adds_to_projected`
- [ ] `test_load_with_zero_amount_fills_to_capacity`
- [ ] `test_load_clamps_to_capacity_when_amount_exceeds_remaining`
- [ ] `test_unload_with_explicit_amount_subtracts_from_projected`
- [ ] `test_unload_with_zero_amount_drains_to_zero`
- [ ] `test_unload_clamps_to_zero_when_amount_exceeds_projected`
- [ ] `test_skips_orders_whose_target_is_not_a_dict` (e.g. fleet-target order)
- [ ] `test_skips_orders_with_mismatching_cargo_type`
- [ ] `test_skips_orders_with_unrecognized_direction` (e.g. `'sideways'`)
- [ ] `test_multiple_orders_for_same_cargo_type_compose_cumulatively` (load 1000 then unload 400 → +600)
- [ ] `test_only_TRANSFER_LOAD_POPULATION_UNLOAD_POPULATION_order_types_are_processed` (e.g. MOVE order ignored)

## Task 1.4: `test_stabilizer_registry.py` (full characterization) [Small]

**Production file:** `game/strategy/services/stabilizer_registry.py` (119 LOC)
**New test file:** `tests/unit/strategy/services/test_stabilizer_registry.py`

Per Decision D-005, mock `find_abilities_in_scope` for these tests.

Behaviors to pin (estimate 9-11 tests):

- [ ] `test_returns_none_when_reference_planet_is_none` (short-circuit before order_type check — D-007)
- [ ] `test_returns_none_when_order_type_not_in_any_spec_blocks` (e.g. OrderType.MOVE)
- [ ] `test_returns_none_when_no_empire_has_active_stabilizer`
- [ ] `test_returns_none_when_empires_iterable_is_empty`
- [ ] `test_returns_geologic_spec_for_implode_planet_when_active`
- [ ] `test_returns_stellar_spec_for_stellerate_star_when_active`
- [ ] `test_returns_stellar_spec_for_create_dyson_sphere_when_active`
- [ ] `test_returns_warpfield_spec_for_open_warp_point_when_active`
- [ ] `test_first_empire_with_match_wins_over_later_empire` (pin empire-iteration order)
- [ ] `test_calls_find_abilities_in_scope_with_require_active_true` (capture kwargs)
- [ ] `test_passes_component_registry_through_to_scanner_unchanged` (None and a sentinel)
- [ ] `test_geologic_scope_iteration_order_planet_then_sector_then_system` (assert call order on the mock — pins the spec.scopes contract)

## Phase Completion

- [ ] All four task files exist + green.
- [ ] `python Tools/lint_test_files.py` passes.
- [ ] Commits land per-file: `test(336): characterize <service_name>`.
- [ ] Any "looks like a bug" finding recorded in `decisions.md` as a D-NNN
      observation entry.
