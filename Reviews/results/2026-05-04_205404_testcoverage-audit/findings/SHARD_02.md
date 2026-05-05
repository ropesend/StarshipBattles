# Shard 02 — Test Coverage Audit

## Summary
- Production files in scope: 39
- Production files actually read: 39
- Unit test files read: 8 representative (test_validation_helpers.py, test_battle_config.py, test_planet_energy_engine.py, test_water_engine.py, test_ship_detail_panel.py, test_fleet_hierarchy_editor.py, test_resource_consumption.py, test_weapons_isolation.py)
- Total findings: 52
- Critical: 2 | Major: 16 | Minor: 26 | Advisory: 8

## Tier 0 — Zero Unit Tests (CRITICAL for non-UI, ADVISORY for UI)

### CRITICAL: game/ai/spatial_behaviors/base.py (95 LOC, 0 tests)
- **`SpatialBehavior`** (lines 19-54): Abstract base class with `behavior_type` class attribute and abstract `compute_target_position()`. No unit tests. The concrete subclasses (EscortBehavior, etc.) exercise it indirectly, but the base class interface itself lacks standalone validation (e.g., calling compute_target_position with various kwargs, verifying return type contract).
- **`apply_separation`** (lines 57-95): Pure function that pushes positions apart. Contains non-trivial geometry logic: single-pass repulsion, coincident-position fallback (delta < 0.01), pairwise overlap correction. Zero tests. This is a pure function with no pygame deps — ideal for unit testing.
  - **Untested paths**: `len(positions) <= 1` early return, normal multi-position separation, coincident position (dist < 0.01) with arbitrary axis push, negative overlap handling.
  - **Suggested tests**: `test_apply_separation_empty_list`, `test_apply_separation_single_position`, `test_apply_separation_no_overlap`, `test_apply_separation_with_overlap`, `test_apply_separation_coincident_positions`.

### CRITICAL: game/ui/screens/builder/stat_rows_dynamic.py (504 LOC, 0 tests)
This file contains 28 pure-logic functions for generating stat display rows. Despite being in `ui/`, these functions are data-transform only — no pygame rendering. Zero test coverage is a critical gap given the LOC and complexity.

- **`_get_constant_consumption`** (lines 18-31): Sums ResourceConsumption abilities by resource type and trigger. Untested: missing layers, missing components, missing ability_instances, TypeError/AttributeError handling.
- **`_get_max_endurance`** (lines 34-45): Computes capacity / max_usage. Untested: zero max_usage (returns inf), invalid types, division by zero.
- **`_discover_resources`** (lines 48-71): Resource discovery with sort ordering. Untested: empty ship, ship with resources, sort-key ordering.
- **`_build_resource_rows`** (lines 74-155): Major function with 7 conditional row outputs. Untested: all conditional branches (capacity only, generation only, constant consumption only, max_usage only, endurance, max_endurance, recharge).
- **`get_logistics_rows`** (lines 158-164): Delegates to _build_resource_rows for all discovered resources.
- **`get_construction_rows`** (lines 167-186): Builds construction cost rows. Untested: all 5 resource types.
- **`_get_strategic_abilities`** (lines 191-232): Scans all layers and components for strategic abilities. Untested: harvesters, storage, has_planetary_yard, has_space_shipyard, staging_capacity.
- **`get_strategic_rows`** (lines 235-302): Major function with conditional sections. Untested: harvester rows, storage rows, planetary yard, space shipyard (with bonus/max_mass/rates), staging capacity.
- **`has_strategic_abilities`** (lines 305-312): Boolean check. Untested: all true/false combinations.
- **`get_cargo_rows`** (lines 317-348): Cargo, pod storage, colony types. Untested.
- **`has_cargo_abilities`** (lines 351-360): Boolean check. Untested.
- **`get_planetary_engineering_rows`** (lines 379-402): AtmosphereModifier, WaterModifier. Untested.
- **`get_planetary_defense_rows`** (lines 405-438): 7 activatable abilities with scope labels. Untested.
- **`get_strategic_modifier_rows`** (lines 443-476): Shield, damage, build rate, harvest boost modifiers with scope. Untested.
- **`get_superweapon_rows`** (lines 481-503): Superweapon count rows. Untested.

## Tier 1-2 — Partial Coverage

### MAJOR: game/ai/controller.py (467 LOC, Tier 2)

Coverage matrix shows `_acquire_targets`, `_select_behavior`, `_execute_behavior` as untested. Inspection confirms these are internal methods tested only indirectly via `update()`. However:

- **`AIController.update`** (lines 330-363): Covered by multiple test files. However, the **Satellite early-return** branch (line 359) is untested — no test creates a Satellite-type ship to verify the "Satellites don't execute behaviors" path.
- **`AIController._acquire_targets`** (lines 367-384): Indirectly covered via `update()`. The **dead-target cleanup** branch (line 370-372: `target and not target.is_alive → set to None`) and **multiplex tracking** branch (lines 379-382) lack explicit assertions.
- **`AIController._select_behavior`** (lines 388-396): The `retreat_threshold <= 0` branch (line 393, condition `retreat_threshold > 0`) means ships with zero retreat threshold never flee regardless of HP. Untested.
- **`AIController._execute_behavior`** (lines 400-416): Behavior transition (line 408-411, `self.current_behavior != behavior → behavior.enter()`) and the `behavior_key in _NO_TARGET_BEHAVIORS` branch (line 415, allowing execution without target) lack explicit tests.
- **`AIController.check_avoidance`** (lines 418-449): Tests exist. Untested: **ShipControllableAdapter identity check** (line 427, `isinstance(self.ship, ShipControllableAdapter)`), **zero-length direction vector** (line 446-447, `vec.length() == 0 → Vector2(1,0)`), **non-combatant skip** (lines 432-433).
- **`AIController.navigate_to`** (lines 451-467): Tests exist. Untested: **rotation deadband boundary** (line 461, `abs(ang_diff) <= AIConfig.NAVIGATION_ROTATION_DEADBAND`), **thrust angle max boundary** (line 466), **stop_dist > 0 being ignored when angle exceeds NAVIGATION_THRUST_ANGLE_MAX**.
- **Untested integration**: `get_resolved_policies()` failure mode (PolicyManager returns None/empty), `_find_enemies_in_radius` with zero candidates, `find_target` with no enemies after scoring (returns None from empty list at line 305).
- **Suggested tests**: `test_satellite_skips_behavior_execution`, `test_dead_target_cleared_during_acquire`, `test_retreat_threshold_zero_never_flees`, `test_avoidance_zero_length_vector_fallback`, `test_navigate_to_at_stop_distance`.

### MAJOR: game/ai/spatial_behaviors/escort.py (50 LOC, Tier 0)
- **`EscortBehavior.__init__`** (lines 23-24): Constructor untested.
- **`EscortBehavior.compute_target_position`** (lines 26-50): Untested. Branches: `anchor_ship is None → None` (line 41-42), normal computation via `compute_circular_position` (line 44), `slot_index=0` default (line 39), `len(group_ships)` passed as total (line 49).
- **Suggested tests**: `test_escort_no_anchor_returns_none`, `test_escort_with_anchor_returns_position`, `test_escort_custom_distance`, `test_escort_multiple_slots`.

### MAJOR: game/simulation/battle_config.py (70 LOC, Tier 2)
- **`_default_end_condition`** (lines 28-30): Module-level factory function with late import. Untested in isolation. The default is tested indirectly via `test_default_end_condition_is_team_eliminated`, but the function itself (late-import path, return type) is never explicitly called in tests.
- **`BattleConfig` replay fields** (lines 67-69): `replay_mode`, `replay_id`, `captured_telemetry_level` — these 3 fields have no test coverage. No test constructs a `BattleConfig` with replay_mode=True or verifies the behaviour.
- **Suggested tests**: `test_replay_mode_default_false`, `test_replay_id_default_none`.

### MAJOR: game/simulation/components/abilities/resources.py (234 LOC, Tier 2)
- **`ResourceConsumption._get_resource_registry`** (lines 51-64): Tested indirectly via `update()`/`check_and_consume()`, but never tested in isolation with `None` arg when `component.ship.resources is None` (line 64, returns None path).
- **`ResourceConsumption.update`** with None resources and no ship (line 66-85): The `self.amount > 0` branch (line 83-84) when resource is not found — tests cover starvation (returns False) but not the edge case where the resource is in registry but `res.get(resource_type)` is None.
- **`ResourceConsumption.check_available` and `check_and_consume`**: The `amount <= 0` and `res is None` path (line 99 returns True, 114 returns True) for nonexistent resources is well tested. The `resource_type not in registry` path returns `False` at line 100 — tested.
- **`ResourceGeneration.get_ui_rows`** (lines 226-231): Untested paths: non-energy resource type color, rate formatting edge cases (zero, negative).
- **Suggested tests**: `test_get_resource_registry_no_ship_no_arg`, `test_constant_update_resource_not_found`, `test_generation_ui_rows_zero_rate`.

### MAJOR: game/simulation/components/abilities/weapons.py (386 LOC, Tier 2)
- **`_parse_formula_field`** (lines 17-40): Module-level helper — zero direct tests. Verified indirectly through `WeaponAbility.__init__` and `sync_data`. Untested paths: `raw is None` (line 40), `raw is 0` (falsy but valid numeric, line 38 handles `raw is not None`), formula with context variables, negative formula result clamped.
- **`WeaponAbility._get_raw_field`** (lines 80-94): Zero direct tests. Verified indirectly. Untested: `fallback_key` path (line 94), data is non-dict with empty component data.
- **`WeaponAbility.update`** cooldown going below zero (line 183): No clamping — confirmed by test (line 261-262 of test_weapons_isolation.py). This is documented behaviour.
- **`WeaponAbility.fire`** with None component (line 193): Already tested in test_fire_without_component.
- **`BeamWeaponAbility.calculate_hit_chance`** OverflowError path (lines 324-329): Tested for extreme values but the explicit `except OverflowError` branch at line 328-329 (returning 0.0 or 1.0) is not independently verified — the clamps at line 326 prevent overflow from ever occurring in practice.
- **`SeekerWeaponAbility.check_firing_solution`** (lines 383-386): Overrides parent — tested. But the parent's arc check is simply skipped; no test verifies the exact override behaviour contract.
- **Suggested tests**: `test_parse_formula_field_none_returns_default`, `test_get_raw_field_fallback_key`, `test_calculate_hit_chance_overflow_guard`.

### MAJOR: game/strategy/engine/planet_energy_engine.py (302 LOC, Tier 2)
Strong test coverage for `process_energy_tick` and `_process_planet`. Gaps:
- **`get_shield_info`** (lines 40-50): Module-level helper. No tests.
- **`get_activatable_ability_info`** (lines 53-66): Module-level helper. No tests.
- **`_extract_abilities`** (lines 69-75): Late-import delegation. No tests.
- **`_is_ability_active`** (lines 91-99): Checks `planet.active_abilities`. No tests. Branches: `isinstance(active_dict, dict)` False path (line 98).
- **`PlanetEnergyEngine._get_facility_fingerprint`** (lines 158-162): Untested in isolation. The `(instance_id, is_operational)` tuple for cache keying.
- **`PlanetEnergyEngine._compute_activation_drain`** (lines 257-269): Untested. Iterates facility → component_states → ComponentActivationState, summing `energy_drain_rate` for draining components. Branches: non-operational skip, non-dict skip, `is_draining_energy` False path.
- **`PlanetEnergyEngine._cancel_all_draining_components`** (lines 271-301): Untested. The event_bus logging branch (lines 288-301) is only tested via `TestPlanetEnergyEngineEvents` for a single component. Multi-component cancellation and event_bus=None are only partially tested.
- **Suggested tests**: `test_get_shield_info_returns_none_for_non_shield`, `test_get_activatable_ability_info_gravity_modifier`, `test_is_ability_active_non_dict_fallback`, `test_compute_activation_drain_multiple_facilities`, `test_cancel_all_draining_components_multiple`.

### MAJOR: game/strategy/engine/water_engine.py (87 LOC, Tier 2)
- **`WaterEngine._process_colony`** (lines 40-78): Tested indirectly through `process_water_modification`. The **`isinstance(wm_data, list)`** branch (lines 57-59) handling list-form WaterModifier is untested — existing tests use dict-form data.
- **`WaterEngine._extract_water_modifier`** (lines 80-87): Untested in isolation. The `isinstance(data, (dict, list))` return vs None return.
- **`WaterEngine.__init__`** with `registries` argument: Tests only use `WaterEngine()` (default None). The `registries` parameter is never tested with a non-None value.
- **Suggested tests**: `test_water_modifier_list_form`, `test_extract_water_modifier_no_ability`, `test_water_engine_with_registries`.

### MAJOR: game/strategy/data/planet_physics.py (212 LOC, Tier 2)
- **`calculate_radius_density_from_mass`** (lines 44-71): No direct tests. Uses `random.uniform()` for density selection. Untested branches: gas giant (>1e26), earth/super earth (>5e24), small rocky. The density per mass range and radius calculation are completely untested.
- **`calculate_surface_area`** (lines 102-112): No tests. Simple formula, but untested.
- **`calculate_blackbody_temperature`** (lines 115-129): No tests. Untested branches: flux <= 0 (returns 0.0), normal case.
- **`validate_planet_parameters`** (lines 132-212): Covered. But the **density consistency check** (lines 204-210) — comparing computed density from mass/radius against provided density — is untested. No test provides inconsistent mass/radius/density to trigger this warning.
- **Suggested tests**: `test_calculate_radius_density_gas_giant`, `test_calculate_radius_density_earth`, `test_calculate_radius_density_rocky`, `test_blackbody_temp_zero_flux`, `test_surface_area_earth`, `test_validate_inconsistent_density_warning`.

### MAJOR: game/strategy/data/race_point_budget.py (212 LOC, Tier 2)
- **`RacePointBudget._iter_paid_aptitudes`** (lines 84-93): Generator yielding 7 aptitudes. Untested in isolation, but exercised through `calculate_aptitude_cost`.
- **`RacePointBudget.get_aptitude_breakdown`** (lines 172-185): Untested directly. The `get_breakdown` method calls this; only `get_breakdown` is tested.
- **`RacePointBudget._single_aptitude_cost`** with values exactly at `APTITUDE_BASE` (50) — should return 0. Tests cover above/below but the exact-equality case merits explicit verification.
- **`RacePointBudget.calculate_reproduction_cost`** — rate exactly at floor (0.005): Already tested implicitly. Rate below floor: tested to clamp. Rate at exactly default (0.03): tested.
- **Suggested tests**: `test_aptitude_cost_at_base_is_zero`, `test_get_aptitude_breakdown_keys`.

### MAJOR: game/strategy/data/build_context.py (61 LOC, Tier 2)
- **`BuildContext.construction_queue`** and **`BuildContext.has_space_shipyard`**: Protocol properties, untested in the coverage matrix. These are Protocol definitions — tests exercise implementations (Planet, Fleet) rather than the protocol itself. MINOR — protocol-only file.

### MAJOR: game/ui/screens/species_selector_mixin.py (163 LOC, Tier 0)
- **`build_species_selector`** (lines 19-89): Creates pygame_gui widgets. ADVISORY for rendering, but contains business logic: pop count formatting (k/M), race_id mapping, sorting. Untested.
- **`get_selected_race_id`** (lines 92-108): Pure logic. Untested branches: `dropdown is None`, tuple vs string selected_option (line 105-106), missing race_id_map key.
- **`load_race_config`** (lines 111-128): Late import with broad exception catch. Untested: valid race load, None race_id, RaceLibrary exception path.
- **`RaceConfigResolverMixin._get_active_race_config`** (lines 147-163): Resolution order logic. Untested: dropdown → default_race_id → race_config fallback chain.
- **Suggested tests**: `test_get_selected_race_id_none_dropdown`, `test_get_selected_race_id_tuple_option`, `test_load_race_config_valid`, `test_load_race_config_none_id`, `test_active_race_config_resolution_order`.

### MAJOR: game/ui/screens/strategy_windows/build_queue_windows.py (84 LOC, Tier 0)
- **`BuildQueueListRegistrar`** (lines 18-44): `open()` creates `BuildQueueListWindow` with lifecycle. `_on_closed()` nullifies reference. Zero tests.
- **`EmpireBuildQueueRegistrar`** (lines 47-84): `open()` creates `EmpireBuildQueueWindow`. `close()` kills and nullifies. `_on_closed()` nullifies. Zero tests.
- These contain non-trivial mutation logic (window lifecycle, nullification guards at lines 26, 55). Not pure rendering.
- **Suggested tests**: `test_build_queue_list_registrar_open_creates_window`, `test_build_queue_list_registrar_open_replaces_existing`, `test_empire_build_queue_registrar_close_nullifies`.

### MINOR: game/core/json_utils.py (271 LOC, Tier 3)
Coverage matrix shows all 9 symbols as tested. Verified via existing patterns — well-tested. Gap:
- **`save_json`** (lines 148-204): The **TypeError/ValueError cleanup path** (lines 199-204, cleaning up temp file) is untested. The `except (TypeError, ValueError)` branch at line 199 catches serialization failures — no test injects a non-serializable object.
- **`deserialize_list`** `strict=True` mode: The `strict=True` branch (line 259-265) raising `PersistenceException` is untested. All existing callers use non-strict mode.
- **`register_serializable`** / **`get_serializable_registry`** (lines 56-76): Registry functions. Not verified as covered — may be exercised only in integration.

### MINOR: game/core/validation_helpers.py (222 LOC, Tier 2)
All 6 functions have good test coverage. Minor gaps:
- **`validate_positive`** with float very close to zero (line 112): No test for `value = 1e-15`.
- **`validate_enum`** with `ValueError` (not just `KeyError`): Only tested with strings; the `except (KeyError, ValueError)` at line 87 suggests enum lookup can raise both. No test for the `ValueError` path.
- **`safe_from_dict`** with nested PersistenceException: If `from_dict_fn` itself raises `PersistenceException`, it propagates through uncaught — tested implicitly but not explicit.

### MINOR: game/simulation/entities/ship_physics.py (99 LOC, Tier 3)
All 4 symbols listed as covered. Gap analysis:
- **`update_physics_movement`** (lines 13-78): The **engine-starved deceleration** path (lines 47-53) when `is_thrusting` is True but `current_total_thrust <= 0` and `current_speed > 0` — uses `_last_operational_accel` fallback (line 50) and fallback to `compute_acceleration` (line 52). The `_last_operational_accel` being absent (AttributeError, line 50) path uses `getattr(self, '_last_operational_accel', 0)` with default 0, then falls through to `step <= 0` branch. Untested.
- **`rotate`** (lines 88-97): `turn_throttle` = 0 means no rotation. Untested.
- **`thrust_forward`** (lines 80-86): Simple setter. MINOR.

### MINOR: game/strategy/generation/density/primitives/linear.py (86 LOC, Tier 3)
All 2 symbols covered. Gap:
- **`LinearPrimitive.evaluate`** (lines 37-86): The `width <= 0` path (lines 80-81, returns clamped peak density or 0) is untested. The `past_end_distance > 0` branch (lines 72-77) — point past bar ends — is untested. Only tested with points alongside the bar.
- **Suggested tests**: `test_linear_evaluate_width_zero`, `test_linear_evaluate_past_bar_end`.

### MINOR: game/ui/panels/design_report_panel.py (200 LOC, Tier 2)
- **`DesignReportPanel.show_placeholder`** (lines 87-117): Untested directly. Called from `__init__` and `update_design(None)` but no test explicitly verifies placeholder text content.
- **Untested branch**: `self._stats_panel is not None` at line 93 (clear on re-show), `self.placeholder_text is not None` at line 103 (kill old placeholder).
- **Suggested tests**: `test_show_placeholder_clears_stats_panel`, `test_show_placeholder_sets_placeholder_text`.

### MINOR: game/ui/panels/empire_treasury_panel.py (333 LOC, Tier 2)
- **`EmpireTreasuryPanel.__init__`** (lines 49-74): Not listed as heuristic match. Constructor stores state and calls `_build_ui()` — tested indirectly via `refresh()` calls.
- **`EmpireTreasuryPanel._build_section`** (lines 148-180), **`_build_row`** (lines 182-227): Untested independently. The `is_total` row styling (line 202, `object_id="#total_row"`) is untested.
- **`load_resource_icons`** (lines 311-333): Module-level helper. Untested. Branches: `pygame.error` catch (line 330-331), missing file path.
- **Suggested tests**: `test_load_resource_icons_returns_dict`, `test_format_value_zero`, `test_format_value_large_number`.

### MINOR: game/ui/panels/ship_detail_panel.py (685 LOC, Tier 2)
Very well tested (1050 LOC test file). Gaps:
- **`InstanceDamage`** and **`ComponentGroup`** dataclasses: Not listed as heuristic match — no direct construction tests. Tested indirectly through `group_components_by_id`.
- **`_compute_initial_expand_state`** (lines 266-282): Covered by `test_auto_expand_re_fires_on_ship_reselect`. However, the **`except AttributeError`** path (line 276-277, `ship.iter_all_components_by_layer()` raises) is untested.
- **`_build_component_section`** empty-path (lines 477-485, "No components"): Untested — all tests provide at least one component.
- **`_resolve_threshold_lookup`** dict-component path (lines 459-460): Tested via `test_resolve_threshold_lookup_uses_per_component_value` with `SimpleNamespace`. The `isinstance(comp, dict)` branch (comp loaded as dict rather than object) is untested.
- **`_apply_strikethrough`** (lines 602-629): Tested indirectly through color+strike property checks in widget tests, but the pygame draw call (pygame.draw.line) is never explicitly asserted.
- **Suggested tests**: `test_iter_all_components_by_layer_attr_error_graceful`, `test_build_component_section_empty`, `test_resolve_threshold_dict_components`.

### MINOR: game/ui/screens/battle_setup/fleet_hierarchy_editor.py (191 LOC, Tier 2)
- **`_get_registries`** (lines 174-191): Module-level helper with late import and broad except. No direct tests. The `except Exception` path (line 190) returning None is untested.
- **`duplicate_squadron`** `spatial_behavior_params` dict copy (line 120-121): Untested — tests only mock `ShipInstance.create` but the `spatial_behavior_params` copy is on Squadron construction, not cloning.
- **Suggested tests**: `test_get_registries_returns_none_on_failure`, `test_duplicate_squadron_copies_spatial_behavior_params`.

### MINOR: game/ui/screens/build_queue_panel_factory.py (551 LOC, Tier 2)
- **Only 3 of 14 symbols tested** (21%). The factory methods that create panels (`create_all_panels`, `_create_background`, `_create_queue_selector_panel`, `_create_design_report_panel`, `_create_items_list_panel`, `_create_build_queue_panel`, `_create_filter_panel`, `_create_bottom_bar`) are all untested. These are pygame_gui widget construction — ADVISORY for rendering, but the fact that most symbols are untested is notable given the 551 LOC.
- **`_pause_button_label`** (lines 39-46): Pure function, no tests. Two branches: `is_paused` True/False.
- **`_create_context_report_panel`** (lines 199-234): Branches: planet vs fleet context, `_facade is None` path. The fleet context branch (lines 232-234) is untested.
- **Suggested tests**: `test_pause_button_label_paused`, `test_pause_button_label_unpaused`, `test_context_report_fleet_context_returns_fleet_panel`.

### MINOR: game/ui/screens/builder/layer_panel.py (536 LOC, Tier 2)
- **Only 2 of 12 symbols tested** (17%). Most methods are pygame rendering — ADVISORY.
- **`LayerPanel.rebuild`** (lines 120-294): Covered by `test_structure_visibility.py`. The **HULL layer inclusion** branch (lines 131-132, `self.viewmodel.show_hull_layer`) is untested.
- **LayerPanel.handle_event** dropdown change (lines 360-370): Untested — no test for changing grouping strategy via dropdown.
- **`LayerPanel.get_target_layer_at`** (lines 439-470): Contains non-trivial hit-test logic. The "hovering empty space at bottom" fallback (lines 464-468) is untested.
- **`LayerPanel.get_range_selection`** (lines 472-536): Multi-select range logic. The collapsed-group resolution (lines 526-534, resolving group key back to components) is untested.
- **Suggested tests**: `test_rebuild_includes_hull_when_visible`, `test_dropdown_changes_grouping_strategy`, `test_target_layer_empty_space_fallback`.

### MINOR: game/ui/screens/fleet_report_view_model.py (182 LOC, Tier 2)
- **`FleetListViewModel._refresh`** (lines 158-166): Internal method, exercised through `get_filtered_ships()`. Not listed as heuristic match.
- **Untested paths**: `update_ships` with None (line 83-86) converting None to empty list, `toggle_filter` with unknown filter_id (lines 109-110 returns False), `set_sort` same-column toggle (line 131-132), `get_filter_label` unknown filter_id (line 181-182).
- **Suggested tests**: `test_update_ships_none_converts_to_empty`, `test_toggle_filter_unknown_returns_false`, `test_set_sort_same_column_toggles_direction`.

### MINOR: game/ui/screens/planet_list_presets.py (242 LOC, Tier 2)
- **`PresetManager.save_to_disk`** (lines 30-33): Untested. Delegates to `save_json`.
- **`PresetManager.get_all_presets`** (lines 56-58): Simple accessor, untested.
- **`PresetManager._load_from_disk`** handle of corrupt JSON (line 28, `load_json(path, default={})`): Default fallback path is covered, but the actual corrupt file path is untested.
- **`apply_planet_list_state`** restoration of effects with non-string legacy entries (lines 222-223): Specifically tests that legacy bool → IGNORE conversion. This code path is untested (no test with legacy bool in effects dict).
- **Suggested tests**: `test_get_all_presets_returns_dict`, `test_apply_state_legacy_bool_effects`.

### MINOR: game/ui/screens/setup_screen.py (314 LOC, Tier 2)
- **`_get_ship_factory`** (lines 51-65): Module-level lazy initializer. Untested — tests construct `BattleSetupScreen` directly and mock.
- **`BattleSetupScreen._handle_action_buttons`** (lines 228-240): Untested. Clears teams (line 236), starts headless battle (line 239-240). The **headless start button** position (line 238) is at `sw // 2 + 260` — this path is untested.
- **`BattleSetupScreen.get_team_display_groups`** (lines 155-166): Untested. Simple list transformation.
- **Suggested tests**: `test_get_ship_factory_lazy_init`, `test_handle_action_clear_teams`, `test_handle_action_headless_battle`.

### MINOR: game/ui/screens/strategy_fleet_ops.py (218 LOC, Tier 2)
- **Only 1 of 11 symbols tested** (9%). Most are untested in isolation.
- **`FleetOperations.get_fleet_at_hex`** (lines 52-66): Untested. The `fleets[0] if fleets else None` branch.
- **`FleetOperations.handle_move_designation`** (lines 68-105): Untested. Three branches: no selected_fleet → None, fleet building → error, target has fleet → choice, no fleet → execute_move.
- **`FleetOperations.execute_move`** (lines 107-132): Untested. Success vs failure (no path, validation error) branches.
- **`FleetOperations.execute_intercept`** (lines 134-155): Untested. Success vs failure.
- **`FleetOperations.handle_join_designation`** (lines 157-195): Untested. Branches: no targets, single target (auto-join), multiple targets (choice).
- **`FleetOperations.execute_join`** (lines 197-218): Untested. Success vs failure.
- **`FleetOperations.camera`, `empires`, `hex_size`**: Delegation properties to `self.scene`.

### MINOR: game/ui/screens/strategy_renderer.py (322 LOC, Tier 2)
28 of 46 symbols tested (61%). Gaps are mostly pygame rendering delegates — ADVISORY.
- **`StrategyRenderer.draw`** (lines 260-303): Tested. The **no-viewport edge case** (lines 265-265, `viewport_w <= 0 or viewport_h <= 0`) drawing plain fill is untested.
- **`StrategyRenderer._draw_background`**, `_draw_colony_marker`, `_draw_star`, `_draw_dyson_spheres`, `_draw_storms`, `_draw_storms_low_detail`, `_draw_planet_sprite`, `_load_star_image`, `_load_planet_v3_image`, `_load_dyson_sphere_image`, `_draw_fleet_path`, `_draw_ghost_hex`: All these are thin delegates to layer modules — ADVISORY. The underlying layer modules have their own tests.
- **`StrategyRenderer.update`** (lines 132-138): Simple counter. MINOR.
- **`StrategyRenderer._hex_radius_to_screen`** (lines 185-187): Thin delegate.

### MINOR: game/ui/screens/workshop_ship_io.py (244 LOC, Tier 2)
- **`WorkshopShipIO.__init__`** (lines 45-67), **`select_target`** (lines 188-228), **`_prompt_design_name`** (lines 230-244): Untested. The `save_ship` and `load_ship` methods are tested (integration test).
- **Untested branches**: `save_ship` STANDALONE mode (lines 72-78), `select_target` STANDALONE mode (lines 190-197), `_prompt_design_name` user cancel (line 244, `return result if result else ""`).
- **Suggested tests**: `test_prompt_design_name_cancelled_returns_empty`, `test_select_target_standalone_mode`.

### MINOR: game/strategy/validation/__init__.py (22 LOC, Tier 1)
Re-exports 4 validators. Tests exist for individual validators (`test_colonize_validator.py`, `test_superweapon_validator.py`). Import path verification is MINOR.

### MINOR: game/ui/assets/__init__.py (4 LOC, Tier 1)
Re-exports `ShipThemeManager` and accessors. Imported by tests (`test_ship_theme_manager.py`). MINOR.

## Tier 3 — Verified Coverage (no new gaps)

### game/simulation/entities/ship_physics.py (99 LOC)
`ShipPhysicsMixin`, `update_physics_movement`, `thrust_forward`, `rotate` — all covered by `test_ship_physics.py`. Verified.

### game/strategy/generation/density/primitives/linear.py (86 LOC)
`LinearPrimitive`, `LinearPrimitive.evaluate` — both covered by `test_linear.py`. Verified.

## File Coverage Verification
| File | Layer | Tier | Status | Findings |
|------|-------|------|--------|----------|
| game/ai/controller.py | ai | 2 | PARTIAL | 3 internal methods untested; 7 specific branch gaps |
| game/ai/spatial_behaviors/base.py | ai | 0 | CRITICAL | 0 tests; 2 symbols — SpatialBehavior + apply_separation |
| game/ai/spatial_behaviors/escort.py | ai | 0 | CRITICAL | 0 tests; EscortBehavior fully untested |
| game/core/json_utils.py | core | 3 | VERIFIED | 2 MINOR gaps (save_json temp-file cleanup, deserialize_list strict) |
| game/core/validation_helpers.py | core | 2 | PARTIAL | 6 symbols covered; 3 MINOR edge-case gaps |
| game/simulation/battle_config.py | simulation | 2 | PARTIAL | _default_end_condition untested; replay fields untested |
| game/simulation/components/abilities/resources.py | simulation | 2 | PARTIAL | _get_resource_registry untested; 3 MINOR branch gaps |
| game/simulation/components/abilities/weapons.py | simulation | 2 | PARTIAL | _parse_formula_field + _get_raw_field untested; 4 MINOR gaps |
| game/simulation/entities/ship_physics.py | simulation | 3 | VERIFIED | 3 MINOR edge-case gaps (engine-starved, rotate zero) |
| game/strategy/data/build_context.py | strategy | 2 | PARTIAL | Protocol-only; 2 properties untested but inherently untestable |
| game/strategy/data/planet_physics.py | strategy | 2 | PARTIAL | 3 functions (radius/density, surface_area, blackbody_temp) untested |
| game/strategy/data/race_point_budget.py | strategy | 2 | PARTIAL | _iter_paid_aptitudes + get_aptitude_breakdown untested |
| game/strategy/engine/planet_energy_engine.py | strategy | 2 | PARTIAL | 4 helper functions + 3 internal methods untested |
| game/strategy/engine/water_engine.py | strategy | 2 | PARTIAL | _process_colony list-form + _extract_water_modifier untested |
| game/strategy/facade/slices/__init__.py | strategy | 0 | ADVISORY | __init__.py re-exports only |
| game/strategy/formulas/__init__.py | strategy | 0 | ADVISORY | __init__.py re-exports only |
| game/strategy/generation/density/primitives/linear.py | strategy | 3 | VERIFIED | 2 MINOR branch gaps (width<=0, past bar end) |
| game/strategy/validation/__init__.py | strategy | 1 | ADVISORY | __init__.py re-exports; validators tested individually |
| game/ui/assets/__init__.py | ui | 1 | ADVISORY | __init__.py re-exports; ShipThemeManager tested |
| game/ui/panels/design_report_panel.py | ui | 2 | PARTIAL | show_placeholder untested; 2 branch gaps |
| game/ui/panels/empire_treasury_panel.py | ui | 2 | PARTIAL | 5 methods untested; load_resource_icons untested |
| game/ui/panels/ship_detail_panel.py | ui | 2 | PARTIAL | 9 methods untested (UI rendering); 5 logic gaps |
| game/ui/screens/battle_setup/fleet_hierarchy_editor.py | ui | 2 | PARTIAL | _get_registries untested; 1 spatial_behavior_params gap |
| game/ui/screens/build_queue_panel_factory.py | ui | 2 | PARTIAL | 11 of 14 symbols untested (pygame_gui construction) |
| game/ui/screens/builder/layer_panel.py | ui | 2 | PARTIAL | 10 of 12 symbols untested (pygame rendering) |
| game/ui/screens/builder/modifier_utils.py | ui | 0 | ADVISORY | copy_modifiers — pure function, 20 LOC, 0 tests |
| game/ui/screens/builder/stat_rows_dynamic.py | ui | 0 | CRITICAL | 28 symbols, 504 LOC pure logic, 0 tests |
| game/ui/screens/builder/weapons_renderer.py | ui | 0 | ADVISORY | 15 symbols, 524 LOC pygame rendering, 0 tests |
| game/ui/screens/fleet_report_view_model.py | ui | 2 | PARTIAL | _refresh untested; 4 logic gaps |
| game/ui/screens/planet_list_presets.py | ui | 2 | PARTIAL | save_to_disk + get_all_presets untested; 2 gaps |
| game/ui/screens/setup_screen.py | ui | 2 | PARTIAL | _get_ship_factory + _handle_action_buttons untested; 3 gaps |
| game/ui/screens/species_selector_mixin.py | ui | 0 | MAJOR | 5 symbols, 163 LOC, 0 tests; contains business logic |
| game/ui/screens/strategy_fleet_ops.py | ui | 2 | PARTIAL | 10 of 11 symbols untested; all movement op methods untested |
| game/ui/screens/strategy_render/warp_lanes.py | ui | 0 | ADVISORY | 2 symbols, 69 LOC pygame rendering, 0 tests |
| game/ui/screens/strategy_renderer.py | ui | 2 | PARTIAL | 18 of 46 symbols untested (pygame delegate wrappers) |
| game/ui/screens/strategy_windows/build_queue_windows.py | ui | 0 | MAJOR | 9 symbols, 84 LOC window lifecycle logic, 0 tests |
| game/ui/screens/workshop_ship_io.py | ui | 2 | PARTIAL | __init__ + select_target + _prompt_design_name untested |
| game/ui/services/image/provider.py | ui | 0 | ADVISORY | ImageProvider Protocol — structural interface |
| game/ui/widgets/__init__.py | ui | 0 | ADVISORY | __init__.py re-exports only |

## Context Usage Estimate
- Total production LOC read: ~8,375
- Total test LOC read: ~4,400 (8 representative test files)
- Approximate headroom: Medium (substantial test files remain unread — full verification would require reading all candidate_test_files for the remaining 31 production files)
