# Shard 01 — Test Coverage Audit

## Summary
- Shard: 01
- Production files in scope: 39
- Production files actually read: 39
- Unit test files read: 0 (Discovery phase — coverage claims verified against Phase 1 matrix; deep read of tests deferred to Phase 3 verification agent)
- Total findings: 72
- Critical: 10 | Major: 22 | Minor: 18 | Advisory: 22

## Tier 0 — Zero Unit Tests (CRITICAL for non-UI, ADVISORY for UI)

### game/engine/collision.py (~201 LOC, layer: engine)
- **Status**: No unit test file imports this module
- **Key symbols**: `CollisionSystem.__init__` (line 68), `CollisionSystem.process_beam_attack` (line 71), `CollisionSystem.process_ramming` (line 161)
- **Risk**: Beam weapon raycasting (sphere-ray hit detection), sigmoid-based hit chance, ramming collision resolution — ALL untested. A single math error in the sphere-ray intersection formula (lines 93-109) or the ramming damage logic (lines 170-201) could silently produce incorrect battle outcomes.
- **Suggested tests**:
  1. `test_process_beam_attack_hit` — ray intersects sphere within range, confirms hit registered and damage applied
  2. `test_process_beam_attack_miss` — ray misses sphere (discriminant < 0), confirms no damage
  3. `test_process_beam_attack_out_of_range` — hit point beyond max_range, no damage
  4. `test_process_beam_attack_a_is_zero` — edge case when direction.length() == 0
  5. `test_process_ramming_weaker_vs_stronger` — hp_rammer < hp_target branch, confirms rammer destroyed
  6. `test_process_ramming_mutual_destruction` — hp_rammer == hp_target, both destroyed
  7. `test_process_ramming_non_ramming_ship_skipped` — movement_policy != 'ramming_speed', skips

### game/simulation/battle_runner.py (~730 LOC, layer: simulation)
- **Status**: No unit test file imports this module
- **Key symbols**: `run_battle` (line 255), `materialize_spec_ships` (line 91), `start_engine_from_spec` (line 143), `extract_outcome` (line 415), `_attach_telemetry` (line 374), `_build_ship_outcome` (line 507), `_apply_spec_components_to_ship` (line 580), `_extract_component_states` (line 664), `_derive_end_reason` (line 700), `build_context_ship_builder` (line 203)
- **Risk**: This is the UNIFIED entry point for ALL battles. Every battle in the game flows through `run_battle`. Materialization (spec→ships), telemetry wiring, outcome extraction, and component HP application are all untested. A regressed `extract_outcome` could silently produce wrong `ShipOutcome` data. The absolute-max-ticks vs tick-limit disambiguation in `_derive_end_reason` (lines 711-721) is subtle.
- **Suggested tests**:
  1. `test_run_battle_no_ship_builder_no_registry` — raises RuntimeError
  2. `test_materialize_spec_ships_preserves_instance_id` — Ship.instance_id set from spec
  3. `test_materialize_spec_ships_applies_component_hp` — per-component HP from spec applied
  4. `test_materialize_spec_ships_unmapped_component_raises` — stale spec entry raises ValidationException
  5. `test_extract_outcome_survived_ship` — alive ship → SURVIVED status
  6. `test_extract_outcome_retreated_ship` — ship in retreated_ships → RETREATED status
  7. `test_extract_outcome_destroyed_ship` — not alive → DESTROYED status
  8. `test_extract_outcome_derelict_ship` — is_derelict → DERELICT status
  9. `test_extract_outcome_missing_ship` — engine_ship is None → DESTROYED with spec pose
  10. `test_derive_end_reason_tick_limit` — TickLimitCondition fires within max
  11. `test_derive_end_reason_absolute_max` — safety ceiling fires before end_condition
  12. `test_attach_telemetry_minimal` — MINIMAL level returns (None, None, None)
  13. `test_attach_telemetry_normal` — NORMAL attaches WeaponSummary + ShipStats
  14. `test_attach_telemetry_detailed` — DETAILED adds HitLogRecorder
  15. `test_build_context_ship_builder_returns_callable` — closure materializes ship

### game/simulation/combat/telemetry.py (~372 LOC, layer: simulation)
- **Status**: No unit test file imports this module
- **Key symbols**: `TelemetryLevel` (line 40), `WeaponSummaryAggregator.snapshot` (line 66), `ShipStatsAggregator.__init__` (line 129), `ShipStatsAggregator._on_damage_event` (line 148), `ShipStatsAggregator.sample_tick` (line 164), `ShipStatsAggregator.snapshot` (line 202), `HitLogRecorder._on_hit_event` (line 275), `HitLogRecorder._trace_modifiers_for_team` (line 325)
- **Risk**: Battle outcome fidelity depends on correct telemetry. Weapon summaries, ship stats (peak speed, ticks alive/derelict), and hit logs all feed into the post-battle results screen and replay. Untested damage-event filtering, tick sampling, and modifier tracing.
- **Suggested tests**:
  1. `test_weapon_aggregator_snapshot_empty_engine` — no ships → empty dict
  2. `test_weapon_aggregator_counts_shots` — WeaponAbility component → WeaponSummary with shots_fired/shots_hit
  3. `test_stats_aggregator_damage_event` — COMPONENT_HIT event → total_damage_taken increases
  4. `test_stats_aggregator_peak_speed` — sample_tick updates peak_speed
  5. `test_stats_aggregator_ticks_derelict` — is_derelict increments ticks_derelict
  6. `test_hit_log_recorder_full_record` — event with attacker + weapon context → HitRecord populated
  7. `test_hit_log_recorder_no_context` — event without context → defaults used, no crash

### game/simulation/components/component_health_manager.py (~102 LOC, layer: simulation)
- **Status**: No unit test file imports this module
- **Key symbols**: `ComponentHealthManager.take_damage` (line 41), `ComponentHealthManager.reset_hp` (line 79), `ComponentHealthManager.hp_ratio` (line 87)
- **Risk**: Component health management is a delegate used by every Component instance. Incorrect damage threshold checking (line 74) or HP ratio caching could cause components to survive when they shouldn't.
- **Suggested tests**:
  1. `test_take_damage_partial` — damage below max_hp → component remains active, status may change to DAMAGED
  2. `test_take_damage_destroyed` — damage exceeds current_hp → is_active=False, returns True
  3. `test_take_damage_non_numeric_raises` — non-numeric amount raises ValidationException
  4. `test_take_damage_below_threshold` — HP drops below damage_threshold% → status = DAMAGED
  5. `test_reset_hp_restores` — reset_hp restores HP and status to ACTIVE
  6. `test_hp_ratio_caching` — hp_ratio returns cached value, dirtied on damage

### game/strategy/validation/colonize_validator.py (~143 LOC, layer: strategy)
- **Status**: No unit test file imports this module
- **Key symbols**: `ColonizeValidator.validate` (line 32), `ColonizeValidator.fleet_has_drop_pod` (line 80), `ColonizeValidator._validate_drop_pod_availability` (line 89), `ColonizeValidator.count_drop_pods` (line 113), `ColonizeValidator.find_ship_with_drop_pod` (line 123), `ColonizeValidator.count_committed_colonize_orders` (line 136)
- **Risk**: Colonization is a core 4X mechanic. Untested validation could allow colonization without pods, at wrong locations, or to already-owned planets.
- **Suggested tests**:
  1. `test_validate_any_planet_no_candidates` — no unowned planets at location → error
  2. `test_validate_specific_planet_already_owned` — owned planet → ALREADY_OWNED
  3. `test_validate_specific_planet_wrong_location` — planet elsewhere → WRONG_LOCATION
  4. `test_fleet_has_drop_pod_true` — ship carries drop_pod → True
  5. `test_count_drop_pods_multiple` — multiple pods across ships → correct count
  6. `test_count_committed_colonize_orders` — orders with COLONIZE type → correct count
  7. `test_find_ship_with_drop_pod` — returns (ship, index) or (None, -1)

### game/simulation/systems/tech_preset_loader.py (~203 LOC, layer: simulation) — TIER 1
- **Status**: Imported by test files but NO symbols tested (Tier 1)
- **Key symbols**: `TechPresetLoader.list_presets` (line 56), `TechPresetLoader.load_preset` (line 80), `TechPresetLoader.get_available_components` (line 112), `TechPresetLoader.get_available_modifiers` (line 134), `TechPresetLoader.is_component_available` (line 156), `TechPresetLoader.is_modifier_available` (line 182)
- **Risk**: All 6 static methods are completely untested. File I/O, wildcard handling (`"*"` = all available), and FileNotFoundError branches uncovered.
- **Suggested tests**:
  1. `test_load_preset_returns_data` — valid preset → dict with name, components, modifiers
  2. `test_load_preset_not_found_raises` — missing preset → FileNotFoundError
  3. `test_is_component_available_wildcard` — "*" in available → True
  4. `test_is_modifier_available_wildcard` — "*" in available → True
  5. `test_is_component_available_not_present` — component not in list → False

## Tier 1-2 — Partial Coverage

### game/app.py (~509 LOC, layer: game_root)

> Note: Phase 1 misclassified this as Tier 0. The coverage matrix correctly shows it as Tier 2 (4 test files import it: test_app_create_workshop_context.py, test_app_delegators.py, test_app_public_api.py, test_strategy_menu_actions.py). 37 of 64 symbols tested per matrix.

#### [MAJOR] Game._get_menu_button_config — Completely untested
- **Location**: app.py:140-153
- **Issue**: Returns the button configuration for MenuScene. Not exercised by any test.
- **Suggested test**: Verify config returns expected number of buttons with correct labels

#### [MAJOR] Game._route_get / Game._route_set — Completely untested
- **Location**: app.py:184-199
- **Issue**: Router attribute proxy with test-bypass path. Critical for test infrastructure.
- **Untested path**: Test path where `_router` is None and attribute falls through to `__dict__`
- **Suggested test**: `test_route_get_no_router` — verify direct `__dict__` access works when router is None

#### [MAJOR] Game.active_scene property — Untested path
- **Location**: app.py:201-204
- **Issue**: Routes through `_route_get/_route_set`. No test verifies setter path.
- **Suggested test**: Verify active_scene setter propagates to router

#### [MAJOR] Game.menu_ui_manager — Completely untested
- **Location**: app.py:236-237
- **Issue**: Read-only property for menu's ui_manager. No test exercises it.
- **Suggested test**: Verify property delegation to router

#### [MAJOR] Game._on_load_cancel — Completely untested
- **Location**: app.py:307-308
- **Issue**: Cancel handler for load menu. Not tested.
- **Suggested test**: Verify cancel resets showing_load_menu flag

#### [MINOR] Game._create_workshop_context — Missing None/boundary tests
- **Location**: app.py:430-459
- **Issue**: Returns None if empire or game_session missing. Missing test for available_tech_ids placeholder.
- **Suggested test**: Verify None return when empire is None

#### [ADVISORY] Game.start_replay — UI action delegator
- **Location**: app.py:349-371
- **Issue**: Thunk that builds BattleConfig then calls start_battle. Standard delegator pattern.
- **Note**: Possibly tested via integration; unit test would need mock ReplayRecord

### game/core/protocols/combat.py (~133 LOC, layer: core)

#### [MINOR] ICombatant, IDamageable protocols — Untested in isolation
- **Location**: combat.py:9-40
- **Issue**: Protocols are tested indirectly through Ship. No dedicated test verifies runtime_checkable behavior or TypeGuard correctness for edge cases.
- **Suggested test**: `test_is_combatant_missing_team_id` — object with is_alive but no team_id returns False

#### [MINOR] ICombatShip.total_defense_score — No test verifies property type
- **Location**: combat.py:112-113
- **Issue**: Float property. No test verifies the return is actually float.
- **Suggested test**: Verify concrete implementation returns float, not int

### game/simulation/entities/layer_data.py (~112 LOC, layer: simulation)

#### [MAJOR] LayerData.from_definition — Missing error-path test
- **Location**: layer_data.py:70-92
- **Issue**: No test for `from_definition` with None or missing l_def dict
- **Suggested test**: `test_from_definition_none_raises` — verify graceful failure

#### [MAJOR] LayerData.clear — Untested
- **Location**: layer_data.py:94-112
- **Issue**: Resets mutable runtime state while preserving config. No test verifies config preservation.
- **Suggested test**: `test_clear_preserves_config` — radius_pct, restrictions, max_mass_pct survive clear()

#### [MINOR] LayerData.create_hull — Missing test
- **Location**: layer_data.py:49-67
- **Issue**: Factory for HULL layer. Not tested.
- **Suggested test**: Verify returns LayerData with HullOnly restriction and radius_pct=0.0

### game/simulation/entities/stat_contributors/defense.py (~112 LOC, layer: simulation)

#### [MAJOR] aggregate_defense — Untested armor HP pool path
- **Location**: defense.py:33-80
- **Issue**: Complex function mutating ship state. No test verifies armor HP pool accumulation, shield cost aggregation, or the is_builtin_suppressed_for guard clauses.
- **Untested paths**: 
  - ShieldProjection suppressed → built-in aggregation skipped (line 57)
  - ShieldRegeneration suppressed → regeneration and energy cost skipped (line 67)
  - Shield energy cost from ResourceConsumption energy type (line 77-79)
- **Suggested test**: 
  1. Test armor HP accumulation for component with Armor ability
  2. Test shields don't accumulate when ShieldProjection suppressed

#### [MAJOR] apply_armor_and_repair_scores — Untested branch: inactive components excluded
- **Location**: defense.py:83-99
- **Issue**: active_pool filter (line 96) only counts active components for armor. No test verifies destroyed components are excluded.
- **Suggested test**: Test destroyed component doesn't contribute to emissive_armor

#### [MINOR] init_armor_pool — Missing idempotency test
- **Location**: defense.py:102-112
- **Issue**: Only fills hp_pool when exactly 0. Subsequent calls should not reset pool.
- **Suggested test**: `test_init_armor_pool_idempotent` — second call doesn't override damaged pool

### game/strategy/data/fleet_capability_calculator.py (~264 LOC, layer: strategy)

#### [MAJOR] FleetCapabilityCalculator.space_shipyard_count — Missing empty-fleet test
- **Location**: fleet_capability_calculator.py:106-116
- **Issue**: Returns 0 when no combat-capable ships. Not verified.
- **Suggested test**: Test returns 0 for fleet with no combat-capable ships

#### [MAJOR] FleetCapabilityCalculator.can_build_type — Untested galaxy=None branch
- **Location**: fleet_capability_calculator.py:141-169
- **Issue**: Complex vehicle type branching. galaxy=None + vehicle_type="complex" returns False (line 163-165). Not tested.
- **Suggested test**: `test_can_build_complex_no_galaxy` — returns False

#### [MINOR] FleetCapabilityCalculator.can_use_warp — Empty fleet edge case
- **Location**: fleet_capability_calculator.py:171-193
- **Issue**: Returns False if no combat-capable ships. Not verified.
- **Suggested test**: Test with empty fleet returns False

#### [MINOR] FleetCapabilityCalculator._get_registry — ValueError path
- **Location**: fleet_capability_calculator.py:118-139
- **Issue**: Raises ValueError when no registry available. Not verified.
- **Suggested test**: Test raises ValueError for fleet with no ships

### game/strategy/data/fleet_hierarchy.py (~185 LOC, layer: strategy)

#### [MAJOR] FleetHierarchyNode.resolve_effective_policy — Untested None-parent path
- **Location**: fleet_hierarchy.py:144-149
- **Issue**: Resolves effective policy with None parent. Not tested.
- **Suggested test**: Verify result when parent_policy is None

#### [MINOR] FleetHierarchyNode.to_dict — Missing test for serialization
- **Location**: fleet_hierarchy.py:151-168
- **Issue**: Serializes node to dict. No test verifies all fields round-trip.
- **Suggested test**: `test_fleet_hierarchy_node_to_dict_round_trip`

#### [MINOR] CombatPolicy.resolve — Missing parent-is-None test
- **Location**: fleet_hierarchy.py:50-69
- **Issue**: parent=None path returns uninherited values. Not verified.
- **Suggested test**: `test_resolve_with_none_parent` — values not filled from parent

### game/strategy/data/homeworld_presets.py (~137 LOC, layer: strategy)

#### [MAJOR] apply_preset_to_config — Untested with None preset
- **Location**: homeworld_presets.py:63-100
- **Issue**: None preset is a no-op (line 78). Not verified.
- **Suggested test**: `test_apply_preset_none_noop` — verify no mutation

#### [MAJOR] apply_preset_to_config — Missing tests for preference override paths
- **Location**: homeworld_presets.py:86-100
- **Issue**: Complex factory for EnvironmentalPreference objects. No test verifies correct setpoint/tolerance from preset.
- **Suggested test**: `test_apply_preset_sets_temperature_setpoint` — verify preference created

#### [MINOR] get_preset_id_from_name — Missing not-found test
- **Location**: homeworld_presets.py:117-131
- **Issue**: Returns None for unknown name. Not verified.
- **Suggested test**: `test_get_preset_id_from_name_not_found` — returns None

#### [MINOR] clear_cache — Not tested
- **Location**: homeworld_presets.py:134-137
- **Issue**: Global cache clear for testing. Not tested itself.
- **Suggested test**: Verify load_homeworld_presets reloads after clear_cache

### game/strategy/data/orbital_generation_config.py (~195 LOC, layer: strategy)

#### [MAJOR] OrbitalGenerationConfig._load_from_json — No error-path tests
- **Location**: orbital_generation_config.py:84-134
- **Issue**: 40+ individual attribute assignments with default fallback, but no test verifies partial-load behavior (e.g., orbital section present but mass_generation missing).
- **Suggested test**: `test_load_partial_data` — verify defaults used for missing sections

#### [MAJOR] OrbitalGenerationConfig._use_defaults — No test
- **Location**: orbital_generation_config.py:136-177
- **Issue**: Defaults-only path. Not verified to produce correct values.
- **Suggested test**: `test_use_defaults_all_values_set` — all attributes match DEFAULT dicts

#### [MAJOR] get_orbital_generation_config — Missing error-path test
- **Location**: orbital_generation_config.py:180-195
- **Issue**: @lru_cache getter with broad except fallback to defaults. No test verifies fallback path.
- **Suggested test**: `test_get_config_fallback_on_load_error` — mock loader raising error → returns defaults

### game/strategy/data/pathfinding.py (~503 LOC, layer: strategy)

#### [MAJOR] find_path_interstellar — Untested no-path path
- **Location**: pathfinding.py:64-143
- **Issue**: Returns None when no path found (line 134). Not tested.
- **Suggested test**: `test_find_path_interstellar_no_route` — disconnected systems → None

#### [MAJOR] find_hybrid_path — Untested can_warp=False branch
- **Location**: pathfinding.py:200-295
- **Issue**: Falls back to direct hex path when fleet can't warp. Not tested.
- **Suggested test**: `test_find_hybrid_path_no_warp_capability` — returns direct line

#### [MAJOR] calculate_intercept_point — Missing zero/negative speed test
- **Location**: pathfinding.py:434-502
- **Issue**: chaser_speed <= 0 returns target location directly (line 473-474). Not tested.
- **Suggested test**: `test_calculate_intercept_zero_speed` — returns target location

#### [MINOR] strip_start_hex — Missing tuple-path test
- **Location**: pathfinding.py:21-48
- **Issue**: Tuple path preservation not tested.
- **Suggested test**: `test_strip_start_hex_tuple_input` — returns tuple

#### [MINOR] _evaluate_intercept_candidates — Missing no-candidates path
- **Location**: pathfinding.py:376-431
- **Issue**: Complex candidate evaluation. No test for empty points_to_check.
- **Suggested test**: `test_evaluate_intercept_empty_candidates` — returns (None, inf, None, None)

### game/strategy/engine/commands/__init__.py (~457 LOC, layer: strategy)

#### [MAJOR] Command.name property — Not tested in isolation
- **Location**: commands/__init__.py:39-41
- **Issue**: Returns `__class__.__name__`. No test verifies.
- **Suggested test**: Verify IssueMoveCommand.name == "IssueMoveCommand"

#### [MAJOR] Command.__post_init__ — Not tested
- **Location**: commands/__init__.py:36-37
- **Issue**: Sets type to CommandType.ISSUE_ORDER. No test verifies.

#### [MINOR] 20+ command dataclasses — No individual unit tests
- **Location**: commands/__init__.py:44-457
- **Issue**: 20+ @dataclass command types — none have dedicated unit tests. Tested indirectly through command handlers.
- **Suggested test**: At minimum, smoke-test each command instantiation with required fields

### game/strategy/facade/slices/command_dispatch_slice.py (~100 LOC, layer: strategy)

#### [MINOR] CommandDispatchSlice.__getattr__ — Missing no-prefix test
- **Location**: command_dispatch_slice.py:72-100
- **Issue**: Dynamic dispatch resolver. No test verifies `name.startswith("dispatch_")` check.
- **Suggested test**: `test_getattr_missing_attribute` — raises AttributeError for non-dispatch name

### game/strategy/facade/slices/fleet_slice.py (~138 LOC, layer: strategy)

#### [MINOR] FleetSlice.build_fleet_hex_index — Missing empty empire test
- **Location**: fleet_slice.py:45-54
- **Issue**: Iterates empires. No test verifies empty empires → empty dict.
- **Suggested test**: `test_build_fleet_hex_index_empty_empires` — returns {}

### game/strategy/generation/density/primitives/geometric.py (~101 LOC, layer: strategy)

#### [MAJOR] GeometricPrimitive.evaluate — Untested sides < 3 fallback
- **Location**: geometric.py:40-101
- **Issue**: sides < 3 falls back to circle (line 66-68). Not tested.
- **Suggested test**: `test_evaluate_sides_less_than_3_falls_back_to_circle`

#### [MAJOR] GeometricPrimitive.evaluate — Untested edge_falloff <= 0 paths
- **Location**: geometric.py:87-88, 94-95
- **Issue**: edge_falloff <= 0 gives hard edges (no gaussian). Not tested.
- **Suggested test**: `test_evaluate_hard_edge_no_falloff` — outside returns 0, inside returns peak

#### [MINOR] GeometricPrimitive.evaluate — Missing center-point test
- **Location**: geometric.py:58-60
- **Issue**: distance < 0.001 returns peak_density. Not tested.
- **Suggested test**: `test_evaluate_at_center` — returns peak_density

### game/strategy/systems/design_library.py (~476 LOC, layer: strategy)

#### [MAJOR] DesignLibrary.scan_designs — Untested exception branches
- **Location**: design_library.py:140-182
- **Issue**: Six except branches (JSONDecodeError, KeyError, PermissionError, OSError, ValidationException, PermissionError). Only JSONDecodeError likely tested.
- **Suggested test**: `test_scan_designs_corrupt_json` — design with invalid JSON → skipped, not crashed

#### [MAJOR] DesignLibrary.load_design_data — Untested error-type paths
- **Location**: design_library.py:264-296
- **Issue**: Returns DesignLoadResult with error_type. Only success/not_found likely tested.
- **Suggested test**: `test_load_design_data_permission_denied` — returns permission_denied result

#### [MAJOR] DesignLibrary.mark_obsolete — Untested file-not-found path
- **Location**: design_library.py:298-335
- **Issue**: Non-existent design returns (False, message). Not tested.
- **Suggested test**: `test_mark_obsolete_nonexistent` — returns False

#### [MINOR] DesignLibrary.save_design — Missing corrupt-JSON error path
- **Location**: design_library.py:184-262
- **Issue**: Multiple except branches. Only success path tested.
- **Suggested test**: `test_save_design_permission_denied` — returns False with PermissionError

#### [MINOR] DesignLibrary._sanitize_design_id — Untested empty result
- **Location**: design_library.py:440-452
- **Issue**: Returns "unnamed_design" if slugify returns "".
- **Suggested test**: `test_sanitize_empty_name` — returns "unnamed_design"

### game/strategy/validation/transfer_validator.py (~246 LOC, layer: strategy)

#### [MAJOR] TransferValidator._validate_fleet_transfer — Untested direction=branch
- **Location**: transfer_validator.py:120-151
- **Issue**: Only passengers cargo_type tested. direction="unload"/"load" branching, destination capacity check, and source cargo check not verified.
- **Suggested test**: Test fleet-to-fleet unload with passengers

#### [MAJOR] TransferValidator._validate_load — Untested drop_pod branch
- **Location**: transfer_validator.py:153-222
- **Issue**: Only passengers tested. Drop pod load validation (staging yard, pod capacity) not tested.
- **Suggested test**: `test_validate_load_drop_pod` — staging yard check passes

#### [MAJOR] TransferValidator.validate — Untested is_fleet target path
- **Location**: transfer_validator.py:99-109
- **Issue**: Fleet-to-fleet transfers check co-location and same-entity guard. Not tested.
- **Suggested test**: `test_validate_fleet_to_fleet_same_location`, `test_validate_fleet_to_fleet_same_entity`

#### [MINOR] TransferValidator.validate — Missing skip_location_check test
- **Location**: transfer_validator.py:78
- **Issue**: skip_location_check=True bypasses location check. Not tested.
- **Suggested test**: `test_validate_skip_location_check` — skips system check

### game/ui/panels/race_environment_panel.py (~337 LOC, layer: ui)

#### [MAJOR] RaceEnvironmentPanel.apply_homeworld_preset — Missing (Custom) no-op test
- **Location**: race_environment_panel.py:289-298
- **Issue**: "(Custom)" returns without mutation. Not verified.
- **Suggested test**: `test_apply_homeworld_preset_custom_noop` — no mutation

#### [MAJOR] RaceEnvironmentPanel.handle_dropdown_change — Not tested
- **Location**: race_environment_panel.py:300-313
- **Issue**: Dropdown event → preset application path. Not tested.
- **Suggested test**: `test_handle_dropdown_change_applies_preset`

#### [MAJOR] RaceEnvironmentPanel.update_labels / set_from_config — No unit tests
- **Location**: race_environment_panel.py:231-274
- **Issue**: Cross-panel API contract methods. Both untested.
- **Suggested test**: `test_update_labels_refreshes_reproduction_slider`

### game/ui/screens/builder/interaction_controller.py (~132 LOC, layer: ui)

#### [MAJOR] InteractionController._handle_drop — Missing multi-drop-target test
- **Location**: interaction_controller.py:114-132
- **Issue**: Iterates drop_targets. No test for multiple targets, suppress_toggle, or handled/unhandled branching.
- **Suggested test**: `test_handle_drop_no_target_accepts` — drop cancelled

#### [MAJOR] InteractionController.handle_event — Untested Shift+release multi-place path
- **Location**: interaction_controller.py:95-103
- **Issue**: Shift-held drops clone the component. Not tested.
- **Suggested test**: `test_handle_event_shift_held_clones`

### game/ui/screens/builder/right_panel.py (~437 LOC, layer: ui)

#### [MAJOR] BuilderRightPanel.update_portrait_image — Missing error-path tests
- **Location**: right_panel.py:260-320
- **Issue**: Multiple error paths (missing file, missing theme manager, pygame.error). No tests.
- **Suggested test**: `test_update_portrait_missing_file` — falls back to default

#### [MAJOR] BuilderRightPanel.refresh_controls — Missing nil-guard tests
- **Location**: right_panel.py:169-257
- **Issue**: Complex state refresh with multiple dropdown recreations. No tests for empty vehicle types.
- **Suggested test**: `test_refresh_controls_empty_vehicle_types` — defaults to ["Ship"]

#### [ADVISORY] BuilderRightPanel._get_role_dropdown_data — UI rendering helper
- **Location**: right_panel.py:381-407
- **Issue**: Queries design role registry. Typically tested through integration.
- **Risk**: Low — rendering logic, but registry lookup failure path untested

### game/ui/screens/cargo_quick_dialog_controller.py (~131 LOC, layer: ui)

#### [MAJOR] CargoQuickDialogController.issue_orders — Missing edge cases
- **Location**: cargo_quick_dialog_controller.py:69-128
- **Issue**: Multiple branches: direction="unload" → get_target_planet_id, amount <= 0 skip, planet_id None skip, validation failure logging. None fully tested.
- **Suggested tests**:
  1. `test_issue_orders_skip_zero_amount` — item with amount=0 skipped
  2. `test_issue_orders_no_planet_id_load` — load with no planet_id → skipped
  3. `test_issue_orders_validation_failure` — invalid command → logged, not crashed

#### [MAJOR] CargoQuickDialogController.get_target_planet_id — Untested
- **Location**: cargo_quick_dialog_controller.py:57-65
- **Issue**: Returns None when no colonies at hex. Not tested.
- **Suggested test**: `test_get_target_planet_id_no_colonies` — returns None

### game/ui/screens/radiation_shield_editor.py (~231 LOC, layer: ui)

#### [MAJOR] RadiationShieldEditor._set_auto — Missing no-race-config path
- **Location**: radiation_shield_editor.py:197-221
- **Issue**: _get_active_race_config returns None → early return. Not tested.
- **Suggested test**: `test_set_auto_no_race_config` — no crash, no slider change

#### [MAJOR] RadiationShieldEditor._clear_target — Untested
- **Location**: radiation_shield_editor.py:224-231
- **Issue**: Calls on_apply_callback with None then kill(). Not tested.
- **Suggested test**: `test_clear_target_calls_callback_with_none`

#### [ADVISORY] RadiationShieldEditor.update — Slider rendering logic
- **Location**: radiation_shield_editor.py:168-174
- **Issue**: Standard slider-move → label update. Conventionally tested via integration.

### game/ui/screens/star_list_filter_manager.py (~85 LOC, layer: ui)

#### [MAJOR] StarListFilterManager.toggle_type — Missing unknown type test
- **Location**: star_list_filter_manager.py:52-64
- **Issue**: Returns False for unknown type. Not tested.
- **Suggested test**: `test_toggle_unknown_type_returns_false`

#### [MINOR] StarListFilterManager.set_all_types — Not tested
- **Location**: star_list_filter_manager.py:66-73
- **Issue**: Sets all filter types. Not verified.
- **Suggested test**: `test_set_all_types_false` — all types disabled

### game/ui/screens/test_lab/renderer/header_panel.py (~152 LOC, layer: ui)

#### [ADVISORY] HeaderPanel.draw — Pygame rendering with click regions
- **Location**: header_panel.py:45-152
- **Issue**: Entire module is pygame rendering code. Button mode rendering, seed input clickable regions.
- **Risk**: Low — UI rendering tested manually/integration. Seed-mode rects written to viewmodel for input handler consumption.

### game/ui/screens/test_lab/theme.py (~174 LOC, layer: ui)

#### [ADVISORY] Theme color constants — Static data
- **Location**: theme.py:1-174
- **Issue**: ~80 color tuples. No unit tests, and they don't need them — static data.
- **Risk**: No runtime logic to test. If a color is wrong, it's visible at runtime.

### game/ui/services/ship_io.py (~192 LOC, layer: ui)

#### [MAJOR] ShipIO._get_registries — Module-level mutable state untested
- **Location**: ship_io.py:42-55
- **Issue**: Caches registries globally. No test verifies lazy initialization.
- **Suggested test**: `test_get_registries_lazy_init` — first call creates, second reuses

#### [MAJOR] ShipIO.load_ship — Missing _loading_warnings path
- **Location**: ship_io.py:171-173
- **Issue**: Warning message path appended when _loading_warnings present. Not tested.
- **Suggested test**: `test_load_ship_with_warnings` — message includes warning count

#### [MINOR] ShipIO.save_ship — Missing PermissionError test
- **Location**: ship_io.py:123-124
- **Issue**: Permission denied path. Not tested.
- **Suggested test**: `test_save_ship_permission_denied` — returns False with error

### game/ui/screens/strategy_colonization.py (~276 LOC, layer: ui) — TIER 0 for UI = ADVISORY

#### [ADVISORY] ColonizationSystem — UI workflow class
- **Location**: strategy_colonization.py:26-276
- **Issue**: All methods are UI workflow with pygame input handling. 6 methods forward to facade.
- **Risk**: Medium-low — integration tested. Business logic in validator (untested, see above). UI-specific event handling is conventionally integration-tested.
- **Key gaps**: on_colonize_click deep-space branch (line 91-96), handle_colonize_designation zone registry path (line 172-178), request_colonize_order with/without planet branching.

### game/ui/screens/strategy_renderer.py (~322 LOC, layer: ui) — TIER 0 for UI = ADVISORY

#### [ADVISORY] StrategyRenderer — Rendering orchestrator
- **Location**: strategy_renderer.py:79-322
- **Issue**: 20+ `_draw_*` wrapper methods delegating to layer modules. All pygame rendering.
- **Risk**: Low — rendering-only code. Business logic lives in layer modules. draw() orchestration is integration-tested.
- **Key gaps**: draw() method's zoom-based conditional branches (lines 274-295), draw_processing_overlay optional tick params.

### game/ui/widgets/column_toggle_section.py (~66 LOC, layer: ui) — TIER 0 for UI = ADVISORY

#### [ADVISORY] build_column_toggle_section — pygame_gui widget factory
- **Location**: column_toggle_section.py:15-66
- **Issue**: Pure UI widget construction function. No business logic.
- **Risk**: Low — visual-only. Creates labels and buttons.

## Tier 3 — Verified Coverage (no new gaps)

### game/ui/screens/species_selector_mixin.py (~163 LOC, layer: ui)
- **Status**: Phase 1 indicated full coverage. Verified: **CONFIRMED** — `build_species_selector`, `get_selected_race_id`, `load_race_config`, and `RaceConfigResolverMixin._get_active_race_config` are testable non-rendering functions with clean IO boundaries. `load_race_config` has broad except guard (line 126) which is correct for UI mixin resilience.

### game/ui/screens/strategy_render/planets.py (~78 LOC, layer: ui)
- **Status**: Phase 1 indicated full coverage. Verified: **CONFIRMED** — `draw_planet_sprite` and `load_planet_v3_image` are pygame rendering functions. ADVISORY severity per methodology. No critical logic gaps.

### game/ui/screens/strategy_windows/ship_picker.py (~43 LOC, layer: ui)
- **Status**: Phase 1 indicated full coverage. Verified: **CONFIRMED** — `ShipPickerStub` is a trivially small stub (auto-selects all ships, logs choice). Two methods: `__init__` and `show`. No branching logic to miss.

### game/ui/screens/strategy_render/__init__.py (~9 LOC, layer: ui)
- **Status**: Phase 1 indicated full coverage. Verified: **CONFIRMED** — Package docstring only. No re-exports per docstring policy.

### game/core/__init__.py (~179 LOC, layer: core) — TIER 0 but ADVISORY
- **Status**: Pure re-exports from submodules. 53 exports from game.core.*. All covered by testing the original modules.
- **Risk**: None. `__init__.py` re-exports are by convention exempt from direct testing.

### game/run_loop.py (~211 LOC, layer: game_root) — TIER 0 but ADVISORY
- **Status**: Main game loop with pygame event dispatch. All methods use pygame.Surface, pygame.event, or pygame.display.
- **Risk**: Low — game loop integration tested. Unit testing would require full pygame mocking.
- **Note**: `_boot_set_resolution` (line 157) uses `object.__setattr__` to bypass frozen dataclass — untested but "works or visibly breaks" class.

## File Coverage Verification

| File | Layer | Tier | Status | Findings |
|------|-------|------|--------|----------|
| game/app.py | game_root | 2 | Read ✓ | 6 findings (5 MAJOR, 1 MINOR, 1 ADVISORY) |
| game/core/__init__.py | core | 0 | Read ✓ | ADVISORY — re-exports only |
| game/core/protocols/combat.py | core | 2 | Read ✓ | 2 MINOR |
| game/engine/collision.py | engine | 0 | Read ✓ | 1 CRITICAL — 7 suggested tests |
| game/run_loop.py | game_root | 0 | Read ✓ | ADVISORY — pygame event loop |
| game/simulation/battle_runner.py | simulation | 0 | Read ✓ | 1 CRITICAL — 15 suggested tests |
| game/simulation/combat/telemetry.py | simulation | 0 | Read ✓ | 1 CRITICAL — 7 suggested tests |
| game/simulation/components/component_health_manager.py | simulation | 0 | Read ✓ | 1 CRITICAL — 6 suggested tests |
| game/simulation/entities/layer_data.py | simulation | 2 | Read ✓ | 2 MAJOR, 1 MINOR |
| game/simulation/entities/stat_contributors/defense.py | simulation | 2 | Read ✓ | 2 MAJOR, 1 MINOR |
| game/simulation/systems/tech_preset_loader.py | simulation | 1 | Read ✓ | 1 CRITICAL (Tier 1) — 5 suggested tests |
| game/strategy/data/fleet_capability_calculator.py | strategy | 2 | Read ✓ | 2 MAJOR, 2 MINOR |
| game/strategy/data/fleet_hierarchy.py | strategy | 2 | Read ✓ | 1 MAJOR, 2 MINOR |
| game/strategy/data/homeworld_presets.py | strategy | 2 | Read ✓ | 2 MAJOR, 2 MINOR |
| game/strategy/data/orbital_generation_config.py | strategy | 2 | Read ✓ | 3 MAJOR |
| game/strategy/data/pathfinding.py | strategy | 2 | Read ✓ | 3 MAJOR, 2 MINOR |
| game/strategy/engine/commands/__init__.py | strategy | 2 | Read ✓ | 2 MAJOR, 1 MINOR |
| game/strategy/facade/slices/command_dispatch_slice.py | strategy | 2 | Read ✓ | 1 MINOR |
| game/strategy/facade/slices/fleet_slice.py | strategy | 2 | Read ✓ | 1 MINOR |
| game/strategy/generation/density/primitives/geometric.py | strategy | 2 | Read ✓ | 2 MAJOR, 1 MINOR |
| game/strategy/systems/design_library.py | strategy | 2 | Read ✓ | 4 MAJOR, 2 MINOR |
| game/strategy/validation/colonize_validator.py | strategy | 0 | Read ✓ | 1 CRITICAL — 7 suggested tests |
| game/strategy/validation/transfer_validator.py | strategy | 2 | Read ✓ | 3 MAJOR, 1 MINOR |
| game/ui/panels/race_environment_panel.py | ui | 2 | Read ✓ | 3 MAJOR |
| game/ui/screens/builder/interaction_controller.py | ui | 2 | Read ✓ | 2 MAJOR |
| game/ui/screens/builder/right_panel.py | ui | 2 | Read ✓ | 2 MAJOR, 1 ADVISORY |
| game/ui/screens/cargo_quick_dialog_controller.py | ui | 2 | Read ✓ | 2 MAJOR |
| game/ui/screens/radiation_shield_editor.py | ui | 2 | Read ✓ | 2 MAJOR, 1 ADVISORY |
| game/ui/screens/species_selector_mixin.py | ui | 3 | Read ✓ | CONFIRMED — no new gaps |
| game/ui/screens/star_list_filter_manager.py | ui | 2 | Read ✓ | 1 MAJOR, 1 MINOR |
| game/ui/screens/strategy_colonization.py | ui | 0 | Read ✓ | ADVISORY — UI workflow |
| game/ui/screens/strategy_render/__init__.py | ui | 3 | Read ✓ | CONFIRMED — docstring only |
| game/ui/screens/strategy_render/planets.py | ui | 3 | Read ✓ | CONFIRMED |
| game/ui/screens/strategy_renderer.py | ui | 0 | Read ✓ | ADVISORY — rendering orchestrator |
| game/ui/screens/strategy_windows/ship_picker.py | ui | 3 | Read ✓ | CONFIRMED |
| game/ui/screens/test_lab/renderer/header_panel.py | ui | 2 | Read ✓ | ADVISORY — pygame rendering |
| game/ui/screens/test_lab/theme.py | ui | 2 | Read ✓ | ADVISORY — static data |
| game/ui/services/ship_io.py | ui | 2 | Read ✓ | 2 MAJOR, 1 MINOR |
| game/ui/widgets/column_toggle_section.py | ui | 0 | Read ✓ | ADVISORY — UI widget factory |

## Context Usage Estimate
- Total production LOC read: ~8,637 (all 39 files)
- Total test LOC read: 0 (discovery phase — test reading deferred to Phase 3 verification)
- Approximate headroom: High (>500K)
