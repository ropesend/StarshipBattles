# PROJ-341 — Per-file characterization checklist

Each section is an in-scope file. Each row is a concrete test function name and the production-code line range it pins. All test names follow the existing project convention `test_<noun>_<behavior>` and read as plain English assertions.

Total target: ~43 tests.

---

## §1 — `game/strategy/engine/environmental_hazard_engine.py`

**Test file:** `tests/unit/strategy/engine/test_environmental_hazard_engine.py`
**Status:** Pending. Green-field — zero existing tests.

### 1.1 — `process_environmental_tick` happy path

- [ ] `test_process_environmental_tick_returns_event_when_storm_deals_damage` — pins lines 71-167. One fleet, one ship, single `EnvironmentalDamage` row with `aggregate_value=100.0`. Asserts one event with `damage_dealt == 1.0` (100/100), `tick == 5`.
- [ ] `test_process_environmental_tick_returns_event_when_storm_drains_fuel` — pins lines 140-143. One fleet, one ship, single `FuelDrain` row with `aggregate_value=200.0`. Asserts `fuel_drained == 2.0` and `ship.consume_resource("fuel", 2.0)` was called once.
- [ ] `test_process_environmental_tick_aggregates_damage_across_multiple_sources` — pins lines 119-120. Two `EnvironmentalDamage` rows with `aggregate_value=50.0` and `aggregate_value=30.0`. Asserts total per-tick damage == 0.8.
- [ ] `test_process_environmental_tick_distributes_damage_evenly_across_combat_ships` — pins lines 135-138. Three combat ships, `damage_per_turn=300`. Asserts each ship took `pytest.approx(1.0)` damage (300/100/3).
- [ ] `test_process_environmental_tick_drains_fuel_per_ship_without_dividing` — pins lines 140-143 + observation OBS-003. Three combat ships, `fuel_per_turn=300`. Asserts each ship had `consume_resource("fuel", 3.0)` called, total `fuel_drained == 9.0`.

### 1.2 — `process_environmental_tick` source-label resolution

- [ ] `test_process_environmental_tick_uses_first_provider_source_label` — pins lines 145-157. Damage row provider has `source_label='Ion Storm Alpha'`. Asserts event `storm_name == 'Ion Storm Alpha'`.
- [ ] `test_process_environmental_tick_falls_back_to_unknown_hazard_when_no_label` — pins lines 145-157. Provider list has no `source_label`. Asserts event `storm_name == 'Unknown Hazard'`.

### 1.3 — `process_environmental_tick` skip / continue paths

- [ ] `test_process_environmental_tick_returns_no_event_when_galaxy_has_no_get_system_at_location` — pins lines 99 + 103-104. Galaxy mock has no `get_system_at_location` attribute; asserts empty event list.
- [ ] `test_process_environmental_tick_returns_no_event_when_fleet_not_in_a_system` — pins lines 105-107. `get_system_at_location` returns None. Asserts empty event list.
- [ ] `test_process_environmental_tick_returns_no_event_when_no_effects_at_hex` — pins lines 116-117. `collect_sector_effects` returns empty list.
- [ ] `test_process_environmental_tick_returns_no_event_when_aggregate_values_are_zero` — pins lines 122-123 + observation OBS-002. Effect rows present but aggregate <= 0.
- [ ] `test_process_environmental_tick_returns_no_event_when_fleet_has_no_combat_ships` — pins lines 125-127. `fleet.get_combat_capable_ships()` returns `[]`.

### 1.4 — `_validate_tick_inputs`

- [ ] `test_validate_tick_inputs_raises_validation_exception_when_fleet_location_is_none` — pins lines 60-69. One fleet with `location=None`. Asserts `ValidationException` with context dict containing `empire_id` and `fleet_id`.
- [ ] `test_validate_tick_inputs_does_not_raise_for_valid_fleets` — pins lines 60-69. Implicit via 1.1 happy path; explicit assertion that calling with all-valid empires returns None and does not raise.

### 1.5 — `_apply_damage_to_ship`

- [ ] `test_apply_damage_to_ship_reduces_current_hp_by_damage_amount` — pins lines 169-201. Ship at 100 HP, damage 25 → `current_hp == 75`. Returns 25.
- [ ] `test_apply_damage_to_ship_marks_ship_dead_when_hp_reaches_zero` — pins lines 198-199. Ship at 10 HP, damage 50 → `current_hp == 0`, `is_alive == False`, returns 10 (clamped).
- [ ] `test_apply_damage_to_ship_resets_current_hp_to_none_when_damage_is_zero_at_full_hp` — pins observation OBS-001 (the dead `else` branch at line 195). Ship at full HP (`current_hp is None`, `max_hp=100`), damage=0 → `ship.current_hp` reset to None, returns 0.

### 1.6 — `_drain_fuel_from_ship`

- [ ] `test_drain_fuel_from_ship_caps_at_current_fuel` — pins lines 213-219. Ship has 5 fuel, drain request 20 → returns 5, `consume_resource("fuel", 5)` called.

**Section §1 total: 17 tests.**

---

## §2 — `game/strategy/engine/superweapon_order_processor.py`

**Test file:** `tests/unit/strategy/engine/test_superweapon_order_processor_gaps.py`
**Status:** Pending. Existing file `test_superweapon_order_processor.py` already covers (do NOT duplicate):
- Happy paths for all 6 superweapons (planet removed, stars removed, warp points created/removed, ships specified-removed).
- Ship-not-consumed for the 5 non-suicide weapons.
- Event logging shape for IMPLODE_PLANET and SHIPS_SELF_DESTRUCTED.
- "No ability ship cancels order" for IMPLODE_PLANET, OPEN_WARP_POINT, CREATE_DYSON_SPHERE.
- Enemy-colony cleanup for IMPLODE_PLANET and CREATE_DYSON_SPHERE.
- Dyson-Sphere zone radius (5 hex clearing, radius_hexes=6) and race_config plumbing.
- CLOSE_WARP_POINT wrong-sector rejection.
- Fleet-not-consumed when ship preserved.

### 2.1 — Stabilizer-blocking cancellation paths (all five non-self-destruct weapons)

- [ ] `test_implode_planet_cancels_when_stabilizer_blocks` — pins lines 166-175. Patches `find_blocking_stabilizer` to return a `MagicMock(ability_name='ChronoStabilizer')`. Asserts `success=False`, `ChronoStabilizer` in message, order popped, `unregister_planet` not called.
- [ ] `test_stellerate_star_cancels_when_stabilizer_blocks` — pins lines 247-259. Asserts no `system_destroyer` invocation, `fleet_consumed=False` (the fleet survives because the cancel happens before the suicide effect).
- [ ] `test_open_warp_point_cancels_when_stabilizer_blocks` — pins lines 334-346. Asserts no warp points added to either system.
- [ ] `test_close_warp_point_cancels_when_stabilizer_blocks` — pins lines 450-462. Asserts `galaxy.remove_warp_link` not called.
- [ ] `test_create_dyson_sphere_cancels_when_stabilizer_blocks` — pins lines 543-555. Asserts no planets unregistered, stars not cleared, no Dyson registered.

### 2.2 — `process_open_warp_point` far-end geometry

- [ ] `test_open_warp_point_far_end_placed_on_axis_for_axial_pairing` — pins lines 376-384. Source at (10,10), target at (40,10). `direction_q=-30, direction_r=0, dist=30`, far_q=round(-30/30*6)=-6, far_r=0. Asserts target system's added warp point is at `HexCoord(-6, 0)`.
- [ ] `test_open_warp_point_far_end_uses_chebyshev_normalisation_for_diagonal_pairing` — pins line 380 (the `max(abs(q), abs(r), 1)` Chebyshev-style normalisation). Source at (50,50), target at (10,10). `direction_q=40, direction_r=40, dist=40`, far_q=round(40/40*6)=6, far_r=6. Asserts far-end at `HexCoord(6, 6)`.

### 2.3 — `process_close_warp_point` legacy back-compat

- [ ] `test_close_warp_point_accepts_legacy_string_target_without_sector_check` — pins lines 436-438 + observation OBS-005. Order target is plain string `'Beta'` (not a dict). Asserts `remove_warp_link` called regardless of fleet hex; no sector-mismatch error.

### 2.4 — `process_close_warp_point` precondition errors not yet pinned

- [ ] `test_close_warp_point_returns_failure_when_destination_id_is_empty_string` — pins lines 440-442. Order target is dict with `destination_id=''`. Asserts no `remove_warp_link` call, `success=False`, order popped.
- [ ] `test_close_warp_point_returns_failure_when_fleet_not_at_a_system` — pins lines 445-448. `get_system_at_hex` returns None. Asserts `success=False` with "not at a star system" message.

### 2.5 — Empty-fleet cleanup (SG-003) for fleet-consuming superweapons

- [ ] `test_self_destruct_removes_empty_fleet_from_empire` — pins lines 706-710. Fleet has one ship, target list contains it. Asserts `empire.remove_fleet(fleet, event_bus=...)` called, `fleet_consumed=True`.
- [ ] `test_self_destruct_does_not_remove_fleet_when_ships_remain` — pins line 706. Fleet has two ships; only one targeted. Asserts `empire.remove_fleet` NOT called, `fleet_consumed=False`.
- [ ] `test_self_destruct_returns_failure_when_target_is_empty_list` — pins lines 678-680. `order.target = []`. Asserts `success=False` with "No ships specified" message.
- [ ] `test_self_destruct_returns_failure_when_target_is_not_a_list` — pins lines 678-680. `order.target = "not-a-list"`. Asserts `success=False`.

### 2.6 — Dyson-Sphere fallback atmosphere when race_config is missing

- [ ] `test_create_dyson_sphere_uses_default_atmosphere_when_empire_has_no_race_config` — pins lines 609-613 (the fallback branch). `empire.race_config = None`. Asserts created Dyson has `surface_gravity == 9.81`, `surface_temperature == 288.0`, `surface_water == 0.3`, atmosphere has `O2: 21000.0` and `N2: 79000.0`.

### 2.7 — `_get_reference_planet`

- [ ] `test_get_reference_planet_returns_first_planet_in_system` — pins lines 756-771 + observation OBS-006. System has two planets at different hexes. Asserts the returned planet is `system.planets[0]`, not the closer one.

**Section §2 total: 16 tests.**

---

## §3 — `game/strategy/engine/action_execution_engine.py`

**Test file:** `tests/unit/strategy/engine/test_action_execution_engine_gaps.py`
**Status:** Pending. Existing file `test_action_execution_engine.py` already covers (do NOT duplicate):
- Speed → tick interval (5/20/100, immobile).
- Progress accumulation, action_time-1 immediate completion, multi-tick completion.
- MOVE / MOVE_TO_FLEET / WARP filtered out.
- BUILD with empty queue auto-pop; BUILD with non-empty queue skipped.
- Fleet consumption flag.
- Iteration safety (single fleet-removal mid-iteration).
- ActionTickResult shape.
- Multi-empire processing.
- Parametrized "all action order types" sweep.

### 3.1 — `_validate_tick_inputs`

- [ ] `test_validate_tick_inputs_raises_validation_exception_when_fleet_location_is_none` — pins lines 70-79. One fleet with `location=None`. Asserts `ValidationException` raised before any progress accumulation. After raise, `order.execution_progress` is still 0.
- [ ] `test_validate_tick_inputs_does_not_raise_for_valid_empires` — pins lines 70-79. Sanity test: explicit no-raise on a valid input.
- [ ] `test_process_action_ticks_does_not_mutate_state_when_validate_raises` — pins line 102 (validate-before-mutate ordering). Two empires; second has a None-location fleet. Asserts the first empire's fleets are NOT progress-incremented before the exception.

### 3.2 — `ActionTimeResolver`-injection constructor path

- [ ] `test_engine_accepts_injected_action_time_resolver` — pins lines 56-68. Passes a custom resolver instance to constructor. (Note: implementation always reads from the static `ActionTimeResolver` class even when an instance is injected — pin **that** behavior. Document as observation if the injected resolver is unused.)
- [ ] `test_engine_defaults_to_none_action_time_resolver_when_omitted` — pins line 67. Construct with `order_processor` only; assert `engine._action_time_resolver is None`.

### 3.3 — Order-popping responsibility lives with the order processor

- [ ] `test_engine_does_not_pop_order_when_action_completes` — pins observation OBS-007 + lines 170-184. Mock processor returns False and does NOT pop the order. After tick 20 (action_time=1, progress hits 1), assert `fleet.get_current_order()` is still the same Order instance — engine itself did not pop.
- [ ] `test_engine_does_not_pop_order_for_in_progress_action` — pins lines 185-194. Mock with `action_time=3`. After tick 20 (progress=1), assert order is still active and processor was not called.

### 3.4 — `_execute_action` kwarg threading

- [ ] `test_execute_action_forwards_component_registry_and_all_empires_to_processor` — pins lines 196-215. Pass distinctive `component_registry=sentinel_registry` and `all_empires=[other_empire]`. Assert `processor.execute_action_order` was called with those exact values via kwargs (`component_registry=sentinel_registry, empires=[other_empire]`).
- [ ] `test_execute_action_forwards_none_kwargs_when_caller_omits_them` — pins lines 209-215. Call `process_action_ticks` without `component_registry` or `all_empires`. Assert processor received `component_registry=None, empires=None`.

### 3.5 — Iteration safety with multiple consumed fleets

- [ ] `test_process_action_ticks_handles_multiple_consumed_fleets_in_same_empire` — pins line 107 (`list(empire.fleets)` copy). Empire has three fleets, processor consumes all three. Asserts all three results returned, no `IndexError` or `ValueError`, `empire.fleets` is empty after.

**Section §3 total: 10 tests.**

---

## Grand total

| Phase | Tests |
|---|---:|
| §1 environmental_hazard_engine | 17 |
| §2 superweapon_order_processor (gap-fill) | 16 |
| §3 action_execution_engine (gap-fill) | 10 |
| **Total** | **43** |
