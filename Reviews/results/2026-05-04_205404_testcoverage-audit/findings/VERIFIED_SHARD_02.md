# Shard 02 — Verified Test Coverage Audit Report

## Summary

| Metric | Count |
|--------|-------|
| Claims reviewed (CRITICAL + MAJOR) | 16 (2 CRITICAL + 14 MAJOR) |
| MINOR/ADVISORY spot-checked | 6 |
| **CONFIRMED** (gap stands) | 10 |
| **PARTIALLY DISPUTED** (some sub-claims wrong, core gap valid) | 3 |
| **DISPUTED** (gap is tested) | 2 |
| **INCONCLUSIVE** | 1 |
| Severity downgrades | 3 (CRITICAL→MAJOR, MAJOR→MINOR ×2) |
| Severity upgrades | 0 |
| Discovery agent errors | 8 |

---

## CONFIRMED Gaps (per file)

### CRITICAL: `game/ui/screens/builder/stat_rows_dynamic.py` (504 LOC)
**Verified status: CONFIRMED — CRITICAL**

Zero tests. No indirect imports in any test file. All 14 functions are pure data-transformation logic producing `StatDefinition` dataclasses — no pygame rendering. The file contains complex conditional branching:

| Function | Lines | Branches Untested |
|----------|-------|-------------------|
| `_get_constant_consumption` | 18-31 | Empty layers, missing components, missing ability_instances, TypeError/AttributeError catch |
| `_get_max_endurance` | 34-45 | Zero max_usage (returns inf), invalid types, division by zero |
| `_discover_resources` | 48-71 | Empty ship, sort-key ordering edge cases |
| `_build_resource_rows` | 74-155 | 7 conditional row outputs, all branches |
| `get_logistics_rows` | 158-164 | Delegates to _build_resource_rows |
| `get_construction_rows` | 167-186 | All 5 resource types |
| `_get_strategic_abilities` | 191-232 | Harvesters, storage, planetary_yard, space_shipyard, staging_capacity |
| `get_strategic_rows` | 235-302 | Harvester rows, storage rows, planetary yard, space shipyard (bonus/max_mass/rates), staging capacity |
| `has_strategic_abilities` | 305-312 | All true/false combinations |
| `get_cargo_rows` | 317-348 | Cargo, pod storage, colony types |
| `has_cargo_abilities` | 351-360 | All branch combinations |
| `get_planetary_engineering_rows` | 379-402 | AtmosphereModifier, WaterModifier |
| `get_planetary_defense_rows` | 405-438 | 7 activatable abilities with scope labels |
| `get_strategic_modifier_rows` | 443-476 | Shield, damage, build rate, harvest boost with scope |
| `get_superweapon_rows` | 481-503 | Superweapon count rows |

**Suggested tests:** ~30+ unit tests covering each function with edge cases (empty ship, missing resources, zero rates, TypeError handling).

---

### MAJOR: `game/simulation/battle_config.py` (70 LOC)
**Verified status: CONFIRMED — MAJOR**

- `_default_end_condition()` (line 28-30): Module-level factory — never directly called in tests. Only exercised via `field(default_factory=_default_end_condition)` on the `BattleConfig` dataclass. The test `test_default_end_condition_is_team_eliminated` checks the dataclass default but does NOT invoke the function directly, test late-import path, or verify the return type independently.
- Replay fields (lines 68-69): `replay_mode`, `replay_id`, `captured_telemetry_level` — completely untested. No test constructs `BattleConfig(replay_mode=True)` or verifies any replay-related behavior on `BattleConfig`. The `replay_id` field tested elsewhere refers to `BattleResult.replay_id` / `BattleOutcome.replay_id`, not `BattleConfig.replay_id`.

**Suggested tests:** `test_default_end_condition_callable_returns_team_eliminated`, `test_replay_mode_default_false`, `test_replay_id_default_none`.

---

### MAJOR: `game/simulation/components/abilities/resources.py` (234 LOC)
**Verified status: CONFIRMED — MAJOR**

- `ResourceConsumption._get_resource_registry()` (lines 51-64): Never directly tested. Never called in isolation. Test files only exercise the public `update()`/`check_and_consume()` which call it internally. The `resources` arg being passed (line 60-61) and the `component.ship.resources is None` fallback (line 64) are untested.
- `ResourceConsumption.update()` edge case (lines 82-84): The branch where `registry.get_resource(self.resource_type)` returns `None` (resource type not found in registry) when `self.amount > 0` is untested. Tested starvation case uses an existing resource type that's exhausted, not the case where the resource type doesn't exist in the registry at all.
- `ResourceGeneration.get_ui_rows()` (lines 226-231): Non-energy resource type color, rate=0.0 formatting, negative rate formatting — all untested.

**Suggested tests:** `test_get_resource_registry_passed_resource_arg`, `test_get_resource_registry_ship_resources_none`, `test_constant_update_resource_type_not_found`, `test_generation_ui_rows_fuel_type_color`.

---

### MAJOR: `game/simulation/components/abilities/weapons.py` (386 LOC)
**Verified status: CONFIRMED — MAJOR**

- `_parse_formula_field()` (lines 17-40): Module-level helper with zero direct tests. Verified indirectly via `WeaponAbility.__init__` and `sync_data` (e.g. `test_damage_formula_stored`, `test_formula_negative_clamped_to_zero`). Untested paths: `raw is None` → returns `(default, None)` (line 40), `raw is 0` — falsy but valid numeric value (line 38 handles this correctly via `raw is not None`), formula with context variables, negative formula result clamping.
- `_get_raw_field()` (lines 80-94): Module-level helper with zero direct tests. The `fallback_key` path (line 92-93) is untested. Tested indirectly but never called with explicit `fallback_key` and empty primary key. The `data` being non-dict with empty component data is also untested.
- `BeamWeaponAbility.calculate_hit_chance()` OverflowError path (lines 328-329): The `except OverflowError` branch is **dead code in practice** — the clamps at line 326 (`max(-20.0, min(20.0, net_score))`) prevent `math.exp` from ever overflowing. The explicit handler is unreachable. This is a code hygiene issue, not a coverage gap.
- `SeekerWeaponAbility.check_firing_solution()` (lines 383-386): Overrides parent to skip arc check. The exact override behaviour contract (omni-directional seeker always passes arc check; only range matters) is not independently verified.

**Suggested tests:** `test_parse_formula_field_none_returns_default`, `test_parse_formula_field_zero_returns_zero`, `test_get_raw_field_fallback_key_used`, `test_seeker_firing_solution_no_arc_restriction`.

---

### MAJOR: `game/strategy/engine/planet_energy_engine.py` (302 LOC)
**Verified status: CONFIRMED — MAJOR**

Strong integration test coverage for `process_energy_tick` and `_process_planet`. However, multiple helpers have zero direct tests:

- `get_shield_info()` (lines 40-50): Module-level helper. Zero direct tests.
- `get_activatable_ability_info()` (lines 53-66): Module-level helper. Zero direct tests.
- `_extract_abilities()` (lines 69-75): Late-import delegation (to `component_inspector`). Zero direct tests.
- `_is_ability_active()` (lines 91-99): The `isinstance(active_dict, dict)` False path (line 98 — returns False when `planet.active_abilities` is not a dict) is untested.
- `PlanetEnergyEngine._get_facility_fingerprint()` (lines 158-162): Produces `(instance_id, is_operational)` tuple for cache keying. Never tested in isolation.
- `PlanetEnergyEngine._compute_activation_drain()` (lines 257-269): Iterates facility → component_states → ComponentActivationState. The branches: non-operational facility skip (line 261), non-dict state_data skip (line 264), `is_draining_energy` False path (line 267-268) are untested.
- `PlanetEnergyEngine._cancel_all_draining_components()` (lines 271-301): Multi-component cancellation, `event_bus=None` path (line 288), and `ability_name` falsy branch are only partially tested.

**Suggested tests:** `test_get_shield_info_returns_none_for_non_shield`, `test_is_ability_active_non_dict_fallback`, `test_compute_activation_drain_non_operational_skip`, `test_cancel_all_draining_multi_component`.

---

### MAJOR: `game/strategy/engine/water_engine.py` (87 LOC)
**Verified status: CONFIRMED — MAJOR**

All test fixtures use `_make_water_facility()` which creates dict-form WaterModifier. The list-form branch and other gaps are untested:

- `_process_colony` list-form `isinstance(wm_data, list)` branch (lines 57-59): CONFIRMED untested. All test facilities produce `"WaterModifier": {"modification_rate": rate}` (dict), never `[{"modification_rate": rate1}, {"modification_rate": rate2}]` (list).
- `_extract_water_modifier()` (lines 80-87): Tested only indirectly through `_process_colony`. The `isinstance(data, (dict, list))` return vs None return, and the Dict|list type boundary are not independently verified.
- `WaterEngine.__init__(registries=None)`: All 8 tests use `WaterEngine()` with default None. The `registries` parameter with non-None value is never tested.

**Suggested tests:** `test_water_modifier_list_form_stacks_rates`, `test_extract_water_modifier_returns_none_for_no_ability`, `test_water_engine_with_registries_passed_in`.

---

### MAJOR: `game/strategy/data/planet_physics.py` (212 LOC)
**Verified status: PARTIALLY CONFIRMED — MAJOR** (see Disputed sub-claim below)

Unit test file (`test_planet_physics.py`) only covers `validate_planet_parameters`, `calculate_escape_velocity`, and `calculate_surface_gravity`. Integration test (`test_planet_physics.py`) tests `calculate_radius_density_from_mass` once with `MASS_EARTH`. Remaining gaps:

- `calculate_radius_density_from_mass()` (lines 44-71): The integration test only covers the Earth/Super-Earth branch (`mass > 5e24`). The gas giant branch (`mass > 1e26`) and small rocky branch (`mass <= 5e24`) are untested. The `random.uniform()` calls make deterministic testing difficult but not impossible (mock `random.uniform`).
- `calculate_surface_area()` (lines 102-112): CONFIRMED untested. Simple `4πr²` formula.
- `calculate_blackbody_temperature()` (lines 115-129): CONFIRMED untested. Untested branch: `flux_wm2 <= 0` → returns `0.0` (line 127-128).
- Density consistency check in `validate_planet_parameters` (lines 204-210): CONFIRMED untested. No test provides mass/radius/density where `|expected_density - provided_density| / max(expected_density, 1) > 0.1` to trigger the warning.

**Suggested tests:** `test_calculate_radius_density_gas_giant`, `test_calculate_radius_density_small_rocky`, `test_surface_area_earth`, `test_blackbody_temp_zero_flux_returns_zero`, `test_validate_inconsistent_density_produces_warning`.

---

### MAJOR: `game/ui/screens/species_selector_mixin.py` (163 LOC)
**Verified status: CONFIRMED — MAJOR**

Zero tests. No indirect imports found in any test file (grep returned nothing). The file contains business logic beyond rendering:

- `build_species_selector()`: Population formatting (k/M suffixes), race_id mapping, sort ordering
- `get_selected_race_id()`: Tuple vs string selected_option handling (pygame_gui version compatibility), dropdown=None path, missing race_id_map key
- `load_race_config()`: Valid race load, None race_id, RaceLibrary exception path (broad `except Exception`)
- `RaceConfigResolverMixin._get_active_race_config()`: Resolution order logic (dropdown → default_race_id → race_config)

**Suggested tests:** `test_get_selected_race_id_none_dropdown`, `test_get_selected_race_id_tuple_option`, `test_load_race_config_valid`, `test_load_race_config_none_id_returns_none`, `test_active_race_config_resolution_order`.

---

### MAJOR: `game/ui/screens/strategy_windows/build_queue_windows.py` (84 LOC)
**Verified status: CONFIRMED — MAJOR**

Grep found `BuildQueueListWindow` and `EmpireBuildQueueWindow` patched in `test_sub_window_hotkeys.py` and `test_strategy_window_manager.py`, but only as mocked dependencies — the `BuildQueueListRegistrar` and `EmpireBuildQueueRegistrar` lifecycle logic (open/close/_on_closed) is never tested:

- `BuildQueueListRegistrar.open()` (lines 24-41): Creates window, replaces existing, passes callback. Untested.
- `BuildQueueListRegistrar._on_closed()` (line 43-44): Nullifies reference. Untested.
- `EmpireBuildQueueRegistrar.open()` (lines 53-75): Creates empire window with full dependency injection. Untested.
- `EmpireBuildQueueRegistrar.close()` (lines 77-81): Kill + nullify guard. Untested.
- `EmpireBuildQueueRegistrar._on_closed()` (line 83-84): Nullifies reference. Untested.

**Suggested tests:** `test_build_queue_list_registrar_open_creates_window`, `test_build_queue_list_registrar_open_replaces_existing`, `test_on_closed_nullifies_window_reference`, `test_empire_build_queue_close_nullifies`.

---

## DISPUTED & INCONCLUSIVE Claims

| # | Original Severity | Module | Claim | Verdict | Reason |
|---|-------------------|--------|-------|---------|--------|
| 1 | **CRITICAL** | `game/ai/spatial_behaviors/base.py` | `apply_separation` untested (0 tests) | **DISPUTED** | Has 5 tests in `tests/unit/ai/spatial_behaviors/test_anti_clumping.py` covering: empty list, single position, normal separation force, far-apart unchanged, and coincident positions. |
| 2 | **CRITICAL** | `game/ai/spatial_behaviors/base.py` | `SpatialBehavior` base class untested (0 tests) | **DISPUTED** | Has 3 tests in `tests/unit/ai/spatial_behaviors/test_spatial_behaviors.py`: importability, `compute_target_position` attribute, and `behavior_type` attribute. Tests are thin (attribute checks only) but present. |
| 3 | MAJOR | `game/ai/controller.py` | `check_avoidance` gaps: ShipControllableAdapter, zero-length vector, non-combatant skip | **DISPUTED** | All 3 are explicitly tested: `test_avoidance_skips_self_via_adapter` (line 463), `test_avoidance_handles_zero_distance` (line 569), `test_avoidance_skips_non_combatants` (line 503). |
| 4 | MAJOR | `game/ai/controller.py` | `navigate_to` rotation deadband and thrust angle untested | **DISPUTED** | Rotation deadband tested: `test_navigate_no_rotation_within_5_degrees` (line 662). Thrust angle tested: `test_navigate_thrusts_within_30_degrees` (line 681) + `test_navigate_no_thrust_outside_30_degrees` (line 698). Stop distance tested: `test_navigate_stops_at_stop_distance` (line 753). |
| 5 | MAJOR | `game/ai/controller.py` | Satellite early-return branch untested | **DISPUTED** | `test_satellite_exception_no_movement` (line 139) creates a Satellite-type ship and verifies `current_behavior is None` after `update()`. |
| 6 | MAJOR | `game/ai/spatial_behaviors/escort.py` | `compute_target_position` "fully untested" | **PARTIALLY DISPUTED** | The main path IS tested (`test_escort_positions_near_anchor`, line 230). The `anchor_ship is None → None` branch (line 41-42) is genuinely untested. |
| 7 | MAJOR | `game/strategy/data/planet_physics.py` | `calculate_radius_density_from_mass` "completely untested" | **PARTIALLY DISPUTED** | Tested in integration test `tests/integration/strategy/test_planet_physics.py:20` with `MASS_EARTH`. However, only the Earth/Super-Earth branch is covered; gas giant and small rocky branches remain untested. |
| 8 | MAJOR | `game/strategy/data/race_point_budget.py` | Multiple claimed untested methods | **PARTIALLY DISPUTED** | `get_aptitude_breakdown` is called by `get_breakdown` which IS tested. `_iter_paid_aptitudes` is exercised through `calculate_aptitude_cost`. File has 27 tests in `test_race_point_budget_v2.py`. The specific untested edge (aptitude at exact base=50) is very minor. |

---

## Discovery Agent Errors

1. **Missed entire test file `test_anti_clumping.py`** — The Phase 2 agent claimed `apply_separation` (lines 57-95 of `base.py`) was untested, but this file contains 5 dedicated tests. This is the most impactful error, leading to a false CRITICAL classification.

2. **Missed 5 existing tests in `test_ai_controller_unit.py`** — The agent claimed `check_avoidance` gaps (ShipControllableAdapter, zero-length direction, non-combatant skip) and `navigate_to` gaps (rotation deadband, thrust angle, stop distance) were untested. All were already tested.

3. **Missed `test_satellite_exception_no_movement` test** — The agent claimed the Satellite early-return in `update()` was untested. It is tested at line 139 of `test_ai_controller_unit.py`.

4. **Overstated `EscortBehavior.compute_target_position` gap** — The agent said "untested" but the test file has `test_escort_positions_near_anchor` which exercises this method. Only the `anchor_ship=None` branch is untested.

5. **Overstated `calculate_radius_density_from_mass` gap** — Agent claimed "completely untested" but the integration test `tests/integration/strategy/test_planet_physics.py` tests it (albeit only the Earth branch).

6. **Overstated `race_point_budget.py` gaps** — Agent claimed MAJOR severity for a file with 27 tests. The remaining untested paths (aptitude exact at base, aptitude breakdown direct call) are very minor.

7. **Missed tests for `SpatialBehavior` base class** — Agent claimed 0 tests for `base.py`, but `test_spatial_behaviors.py` has 3 tests for the base class (existence, `compute_target_position` attribute, `behavior_type` attribute).

8. **Underscored `check_avoidance` test coverage** — Specific tests for `ShipControllableAdapter` unwrapping (lines 463-485 in test file) were completely overlooked.

---

## Severity Downgrades

| Module | Original | Downgraded To | Reason |
|--------|----------|---------------|--------|
| `game/ai/spatial_behaviors/base.py` | CRITICAL | MAJOR | `apply_separation` has 5 tests; `SpatialBehavior` base has 3 tests. Original claim of "0 tests" was incorrect. However, the base class tests are thin (attribute checks only) and there are gaps in `apply_separation` edge cases (coincident positions with >2 ships, overlapping overlap corrections). Retain downgraded severity. |
| `game/ai/controller.py` | MAJOR | MINOR | 6 of 8 claimed untested branches are already tested. Remaining gaps: dead-target cleanup, `retreat_threshold=0`, behavior transition, PolicyManager failure modes. These are narrow edge cases. |
| `game/strategy/data/race_point_budget.py` | MAJOR | MINOR | File has 27 tests in `test_race_point_budget_v2.py`. Remaining untested paths (`_single_aptitude_cost` at exact base=50, `get_aptitude_breakdown` direct call, `_iter_paid_aptitudes` isolation) are trivial and well-covered by the existing indirect tests. |

---

## MINOR/ADVISORY Spot-Check Results

| Original Severity | Module | Claim | Verification | Action |
|-------------------|--------|-------|-------------|--------|
| MINOR | `game/ai/spatial_behaviors/escort.py` | `anchor_ship is None → None` branch untested | CONFIRMED — none of the 2 tests pass `anchor_ship=None` | No change |
| MINOR | `game/simulation/components/abilities/resources.py` | `_get_resource_registry` untested in isolation | CONFIRMED — no test calls it directly; only exercised through `update()`/`check_and_consume()` | No change |
| ADVISORY | `game/ui/screens/builder/modifier_utils.py` | `copy_modifiers` 20 LOC, 0 tests | CONFIRMED — pure function, zero tests. Value: any change to strategy modifier data structures could silently break ship copying. | No change (ADVISORY appropriate) |
| ADVISORY | `game/ui/screens/builder/weapons_renderer.py` | 524 LOC pygame rendering, 0 tests | CONFIRMED — imports `pygame.draw`, `pygame.Surface`. All 15 symbols are rendering-related. | No change (ADVISORY appropriate — pure rendering) |
| MINOR | `game/ui/screens/strategy_fleet_ops.py` | 10 of 11 symbols untested | CONFIRMED — `FleetOperations` delegates to `self.scene` for `camera`, `empires`, `hex_size`. Only `handle_designation_request` is covered (indirectly via response). The methods `handle_move_designation`, `execute_move`, `execute_intercept`, `handle_join_designation`, `execute_join` have complex branching logic that is untested. | **UPGRADE to MAJOR** — contains non-trivial mutation logic (movement, interception, joining) with multiple branching paths |
| MINOR | `game/ui/screens/planet_list_presets.py` | `apply_planet_list_state` legacy bool effects untested | CONFIRMED — no test passes legacy bool values in effects dict. The conversion path at lines 222-223 is untested. | No change |

### Upgrade: `game/ui/screens/strategy_fleet_ops.py` — MINOR → MAJOR

The file contains 4 methods with significant business logic and branching that are completely untested:
- `handle_move_designation()` (68-105): 4 branches (no selected_fleet, fleet building error, target has fleet → choice, no fleet → execute)
- `execute_move()` (107-132): Success vs failure branches
- `execute_intercept()` (134-155): Success vs failure branches
- `handle_join_designation()` (157-195): 4 branches (no targets, single target, multiple targets → choice)
- `execute_join()` (197-218): Success vs failure branches

These are not rendering delegates — they orchestrate strategy-level fleet operations with complex state transitions.

---

## Final Tally

| Severity | Count | Files |
|----------|-------|-------|
| CRITICAL | 1 | `stat_rows_dynamic.py` |
| MAJOR | 9 | `battle_config.py`, `resources.py`, `weapons.py`, `planet_energy_engine.py`, `water_engine.py`, `planet_physics.py`, `species_selector_mixin.py`, `build_queue_windows.py`, `strategy_fleet_ops.py` (upgraded from MINOR) |
| MINOR | 3 | `spatial_behaviors/base.py` (downgraded from CRITICAL), `controller.py` (downgraded from MAJOR), `race_point_budget.py` (downgraded from MAJOR) |
| DISPUTED (no remaining gap) | 0 | — |
