# Shard 09 — Test Coverage Audit

## Summary
- Shard: 09
- Production files in scope: 47
- Production files actually read: 47
- Unit test files read: 17
- Total findings: 51
- Critical: 10 | Major: 15 | Minor: 11 | Advisory: 15

## Tier 0 — Zero Unit Tests (CRITICAL for non-UI, ADVISORY for UI)

### game/ai/protocols.py (~125 LOC, layer: ai)
- **Status**: No unit test file imports this module
- **Key symbols**: `IGridEntity`, `IProjectile`, `IComponentHealth`, `is_grid_entity`, `is_projectile`, `is_component_health`
- **Risk**: TypeGuard functions and Protocols used across the AI layer for duck-typing. If these protocols or TypeGuards break (e.g., `_has_attrs` import changes), AI targeting/combat silently degrades.
- **Suggested tests**:
  1. `test_is_grid_entity` — verify TypeGuard returns True for objects with `position` + `team_id`, False for objects missing them
  2. `test_is_projectile` — verify TypeGuard returns True for objects with `position` + `type`, False for non-projectiles
  3. `test_is_component_health` — verify TypeGuard for `current_hp` attribute
  4. `test_protocol_runtime_checkable` — verify `isinstance` compatibility with `@runtime_checkable` Protocol instances

### game/core/component_state.py (~102 LOC, layer: core)
- **Status**: No unit test file imports this module
- **Key symbols**: `ComponentState`, `ComponentInstanceView`, `component_state_key`
- **Risk**: `ComponentState` is the authoritative per-component HP persistence container between battles (PROJ-269). `to_dict`/`from_dict` errors would corrupt save files. `__post_init__` float coercion untested.
- **Suggested tests**:
  1. `test_component_state_key_format` — verify key format `"{id}#{index}"`
  2. `test_component_state_to_dict` — verify all fields survive round-trip
  3. `test_component_state_from_dict` — verify reconstruction with defaults for missing `max_hp`, `is_active`
  4. `test_component_state_post_init_coerces_int_to_float` — verify int inputs become float
  5. `test_component_state_is_damaged` — boundary: max_hp=0 (no damage), current < max (damaged), current >= max (not damaged)
  6. `test_component_instance_view_construction` — verify read-only snapshot construction

### game/simulation/combat/families/_beam_common.py (~44 LOC, layer: simulation)
- **Status**: No unit test file imports this module
- **Key symbols**: `build_beam_resolution`
- **Risk**: Shared construction helper used by both `BeamHandler` and `PDCHandler` (PROJ-359). If this function breaks, both beam and PDC weapon families fail. Zero-length aim vector branch (line 34) untested.
- **Suggested tests**:
  1. `test_build_beam_resolution_constructs_correctly` — verify all `BeamResolution` fields populated from `AttackRequest`
  2. `test_build_beam_resolution_zero_aim_vector` — verify direction defaults to Vector2(1,0) when aim_vec is zero-length

### game/simulation/combat/families/pdc.py (~45 LOC, layer: simulation)
- **Status**: No unit test file imports this module
- **Key symbols**: `PDCHandler`, `PDCHandler.fire`
- **Risk**: PDC weapon family handler (PROJ-359). Untested fire() method means all PDC weapon resolution is untested. Shared dependency on `_beam_common.build_beam_resolution` means the delegation chain has zero unit coverage.
- **Suggested tests**:
  1. `test_pdc_handler_fire_returns_beam_resolution` — verify `PDCHandler().fire(request)` returns AttackResolution
  2. `test_pdc_handler_registered_in_registry` — verify `WEAPON_REGISTRY` contains PDC family handler

### game/simulation/entities/stat_contributors/launch.py (~55 LOC, layer: simulation)
- **Status**: No unit test file imports this module
- **Key symbols**: `contribute_vehicle_launch`
- **Risk**: Hangar capacity, fighter wave size, and launch cycle stat aggregation (PROJ-360). Missing coverage means fighter/carrier mechanics have zero direct unit tests for the stat contributor. Guards against missing `VehicleLaunch` ability (line 45) untested. Boundary conditions on `max_launch_mass`, `cycle_time` comparison (lines 56, 60) untested.
- **Suggested tests**:
  1. `test_contribute_vehicle_launch_adds_capacity` — verify fighter_capacity incremented from VehicleStorage abilities
  2. `test_contribute_vehicle_launch_skips_without_vehicle_launch` — verify no-op when VehicleLaunch missing
  3. `test_contribute_vehicle_launch_tracks_max_mass` — verify fighter_size_cap is max across components
  4. `test_contribute_vehicle_launch_tracks_longest_cycle` — verify launch_cycle is max across components

### game/simulation/entities/stat_contributors/movement.py (~68 LOC, layer: simulation)
- **Status**: No unit test file imports this module
- **Key symbols**: `contribute_combat_propulsion`, `contribute_strategic_movement`, `contribute_warp_jump`, `contribute_maneuvering_thruster`
- **Risk**: Four per-ability movement stat contributors (PROJ-360). Thrust, strategic movement, warp tonnage, and maneuver stats all without direct unit tests. Warp tonnage max comparison (line 63) untested.
- **Suggested tests**:
  1. `test_contribute_combat_propulsion_sums_thrust` — verify acc.thrust accumulates
  2. `test_contribute_strategic_movement_sums_points` — verify acc.strategic_movement accumulates
  3. `test_contribute_warp_jump_tracks_max_tonnage` — verify acc.warp_max_tonnage is max across components
  4. `test_contribute_maneuvering_thruster_sums_turn` — verify acc.turn_speed and acc.maneuver_points accumulate

### game/strategy/facade/slices/event_slice.py (~96 LOC, layer: strategy)
- **Status**: No unit test file imports this module
- **Key symbols**: `EventSlice`, 8 methods
- **Risk**: Event slice is the facade's event-log read surface (PROJ-309). All 8 query methods untested. Event filtering by empire_id uses two different `EventLog` API paths depending on whether `empire_id is None` — regression-prone.
- **Suggested tests**:
  1. `test_get_turn_events_default_turn` — verify returns current-turn events when turn=None
  2. `test_get_turn_events_with_empire_scope` — verify events filtered by empire_id path
  3. `test_get_all_events` — verify returns all events
  4. `test_get_events_by_category` — verify category filtering
  5. `test_get_human_player_ids` — verify returns session's human player list
  6. `test_get_save_path_returns_none_for_unsaved` — verify None for new games

### game/strategy/services/ability_sources/planet_intrinsic.py (~91 LOC, layer: strategy)
- **Status**: No unit test file imports this module
- **Key symbols**: `PlanetIntrinsicAbilitySource`, 9 methods
- **Risk**: Planet intrinsic ability adapter (PROJ-301). Multi-hex body logic (`radius_hexes > 0` branch, line 71) completely untested. `affects_hex` with TypeGuard coercion failing (line 83-84) untested. `source_id` fallback path (line 38) untested.
- **Suggested tests**:
  1. `test_affects_hex_single_hex_planet` — verify standard planet center match
  2. `test_affects_hex_multi_hex_planet` — verify multi-hex body projection
  3. `test_affects_hex_no_location_returns_false` — verify graceful None handling
  4. `test_source_id_uses_name_fallback_when_id_is_neg1` — verify fallback path
  5. `test_source_label_includes_planet_type` — verify formatting
  6. `test_get_abilities_returns_empty_dict_for_missing` — verify None/empty guard

### game/strategy/services/effect_ability_display.py (~168 LOC, layer: strategy)
- **Status**: No unit test file imports this module
- **Key symbols**: `_ability_kind`, `_format_status`, `_is_activatable`, `make_group_key`, `make_display_name`, `format_intrinsic_ability_magnitude`
- **Risk**: Central display-formatting module for effect abilities (PROJ-362). Consumed by `system_effects_collector`, planet list per-effect columns, and system tree panel effects. Incorrect grouping keys or display names would corrupt all three UI surfaces. Complex branching in `make_group_key` (EnvironmentalDamage fallback, quality improvement fallback) and `format_intrinsic_ability_magnitude` (rate vs multiplier, identity-value suppression) untested.
- **Suggested tests**:
  1. `test_make_group_key_uses_field_value` — verify `"ResourceHarvestBooster:metals"` grouping
  2. `test_make_group_key_environmental_damage_fallback` — verify `"EnvironmentalDamage:environmental"` default
  3. `test_make_display_name_explicit_from_metadata` — verify explicit display_name wins
  4. `test_make_display_name_derived_from_resource_type` — verify "Metals Harvest Boost" derivation
  5. `test_format_intrinsic_ability_magnitude_rate` — verify rate formatting
  6. `test_format_intrinsic_ability_magnitude_multiplier_suppresses_identity` — verify `x1.00` returns ""
  7. `test_format_status_active_deactivating_countdown` — verify countdown formatting
  8. `test_is_activatable_with_activation_time` — verify detection

### game/strategy/validation/superweapon_validator.py (~270 LOC, layer: strategy)
- **Status**: No unit test file imports this module
- **Key symbols**: `SuperweaponValidator`, 11 methods
- **Risk**: All 7 superweapon validation methods completely untested. Fleet-level destroy-planet, stellerate-star, open/close-warp-point, create-dyson-sphere, and self-destruct validators. Each has complex branching: ability checks, location checks, warp point duplicate checks, multi-ship self-destruct validation. Critical for preventing invalid superweapon orders.
- **Suggested tests**:
  1. `test_validate_implode_planet_null_target` — verify error for None planet
  2. `test_validate_implode_planet_missing_ability` — verify error when no DestroyPlanet
  3. `test_validate_implode_planet_success` — verify success path
  4. `test_validate_stellerate_star_no_stars_in_system` — verify error for starless system
  5. `test_validate_open_warp_point_duplicate_warp` — verify error for existing warp link
  6. `test_validate_open_warp_point_invalid_target_system` — verify error for nonexistent target
  7. `test_validate_close_warp_point_fleet_not_at_warp_point` — verify location check
  8. `test_validate_self_destruct_empty_ship_list` — verify error for empty list
  9. `test_validate_self_destruct_ship_not_in_fleet` — verify ship existence check
  10. `test_validate_self_destruct_missing_ability` — verify ability check
  11. `test_validate_self_destruct_success` — verify success path

### game/ui/research/research_renderer.py (~324 LOC, layer: ui)
- **Status**: No unit test file imports this module — ADVISORY (pygame rendering)
- **Key symbols**: `ResearchRenderer`, 9 methods
- **Risk**: All tech tree rendering. 324 LOC of pygame drawing code: dependency lines, dashed lines for negated requirements, node rectangles with status colors, text, and lighting effects. Conventionally tested via integration/manual testing.
- **Note**: `_is_visible` (viewport culling, line 312) contains testable logic beyond pure rendering — coordinate comparison math. Could be factored out and unit tested separately.

### game/ui/screens/strategy_screen_assets.py (~88 LOC, layer: ui)
- **Status**: No unit test file imports this module — ADVISORY (UI helpers)
- **Key symbols**: `focus_on_player_home`, `load_assets`, `get_object_asset`
- **Risk**: Asset loading and camera-focus helpers (PROJ-330). `focus_on_player_home` has testable logic (finding home colony system, hex-to-pixel conversion). `get_object_asset` has complex branching (star/planet/warp/fleet type dispatch) that could be tested with mock objects.
- **Note**: `get_object_asset` has 7 conditional branches (star, planet with optional rotation, warp, fleet) — these are testable business logic, not pure rendering. A mock AssetManager pattern would allow unit testing.

### game/ui/screens/strategy_windows/move_choice_dialog.py (~94 LOC, layer: ui)
- **Status**: No unit test file imports this module — ADVISORY (UI dialog)
- **Key symbols**: `MoveChoiceWindow`, `MoveChoiceDialog`, `MoveChoiceDialog.show`
- **Risk**: UI dialog that prompts move-vs-intercept choice. The `show()` method performs coordinates math (centering, button layout) and callback wiring. The `MoveChoiceWindow` extends `StrategyModalWindow` (which IS tested via `test_strategy_modal_window.py`), but the `MoveChoiceDialog` registrar layer is not directly tested.
- **Note**: `show()` also contains ordering risk via `pygame_gui` callback lambda wire-up (line 93-94) — lambdas capture closures that need to be tracked.

### game/ui/screens/strategy_windows/transfer_dialogs.py (~79 LOC, layer: ui)
- **Status**: No unit test file imports this module — ADVISORY (UI dialog)
- **Key symbols**: `TransferDialogRegistrar`, 3 methods
- **Risk**: Transfer dialog opening logic. Both `open()` and `open_quick()` use late imports and construct dialog windows. The existing-slot guard (`if c.transfer_dialog is not None`, line 32) is a potential resource leak point (kill-then-replace).
- **Note**: The `open_quick` method branches on `direction` parameter ('unload'/'load') — this is testable business logic that chooses between CargoQuickDialog and TransferDialog.

### game/ui/screens/test_lab/details/resource_outcomes.py (~294 LOC, layer: ui)
- **Status**: No unit test file imports this module — ADVISORY (UI rendering)
- **Key symbols**: `is_resource_test`, `draw_resource_outcomes`, 3 helper renderers
- **Risk**: 294 LOC of pygame rendering for resource test outcomes (PROJ-309). Three sub-renderers (fuel/energy/ammo) dispatched by test_id prefix matching. `is_resource_test()` is simple non-rendering logic. The rendering code has tolerance-check branching (line 117) and velocity-status display logic (line 130-138) that mixes computation with rendering.
- **Note**: `is_resource_test` (line 18-21) is pure testable logic — string prefix check on `run_record.metrics['test_id']`. Could be extracted and unit tested.

## Tier 1-2 — Partial Coverage

### game/simulation/services/design_loader.py (~136 LOC, layer: simulation)

#### [MINOR] `SimulationDesignLoader.__init__` — Missing None-guard test
- **Location**: design_loader.py:45-58
- **Issue**: Constructor validates registries is not None and raises `ValidationException`, but this path is untested per Phase 1. The rest of the class (load methods) is tested.
- **Suggested test**: `test_init_with_none_registries_raises`

### game/simulation/systems/tick_phase.py (~201 LOC, layer: simulation)

#### [MAJOR] `RebuildGridPhase` — Class name not matched by tests
- **Location**: tick_phase.py:87-100
- **Issue**: Phase 1 reports `RebuildGridPhase` (and 4 other phase classes) as untested. The test file only tests the `TickPhaseRegistry` protocol via `MockPhase`, not the concrete phase implementations.
- **Untested path**: The 6 concrete phase classes (`RebuildGridPhase`, `AIAndShipUpdatePhase`, `BoundaryEnforcementPhase`, `AttackProcessingPhase`, `RammingPhase`, `ProjectileUpdatePhase`) each call specific engine methods — none of these method-call chains are directly verified.
- **Suggested test**: `test_create_default_phases_includes_boundary_enforcement` — verify `BoundaryEnforcementPhase` is registered at priority 250; `test_default_phases_priority_order` — verify all 6 phases in correct order

#### [MINOR] `create_default_phases` — Phase 1 reports untested
- **Location**: tick_phase.py:183-201
- **Issue**: Factory function for creating default phase registry. Not directly tested; exercised only through BattleEngine integration.
- **Suggested test**: `test_create_default_phases_returns_six_phases` — verify length and ordering

### game/strategy/data/empire.py (~387 LOC, layer: strategy)

#### [MINOR] `Empire.add_colony` — Phase 1 reports untested
- **Location**: empire.py:56-59
- **Issue**: Method not directly called in unit tests. Heuristic match failed. However, this is a 3-line method (append + set owner_id) exercised indirectly through broader colony setup in integration tests.
- **Suggested test**: `test_add_colony_sets_owner` — verify planet.owner_id is set

### game/strategy/data/habitability_factors.py (~384 LOC, layer: strategy)

#### [MAJOR] `_make_scalar_extractor` — Factory function untested
- **Location**: habitability_factors.py:129-137
- **Issue**: Factory that creates extractor functions for habitability scalar axes. The returned `extract` function reads `planet.<attr>` with None-guard and type coercion. If the generated extractor malfunctions, all 7 scalar habitability scores break.
- **Suggested test**: `test_make_scalar_extractor_returns_float` — verify generated extractor returns float; `test_make_scalar_extractor_returns_none_for_missing_attr` — verify None guard

#### [MAJOR] `_make_gas_extractor` — Factory function untested
- **Location**: habitability_factors.py:140-151
- **Issue**: Factory that creates extractor functions for 10 atmospheric gas axes. Same risk profile as `_make_scalar_extractor` — if broken, all gas habitability scores fail.
- **Suggested test**: `test_make_gas_extractor_returns_partial_pressure` — verify returns 0.0 for missing gas

#### [MAJOR] `_build_gas_factors` — Function untested
- **Location**: habitability_factors.py:311+ (read from full file)
- **Issue**: Builds the 10 atmospheric gas `HabitabilityFactor` entries. If gas factors are misconfigured, the species setup UI and habitability formula produce wrong results.
- **Suggested test**: `test_build_gas_factors_has_ten_gases` — verify count; `test_gas_factors_have_correct_weights` — verify weight ~0.15 each

### game/strategy/engine/planet_modifier_effect_engine.py (~96 LOC, layer: strategy)

#### [MAJOR] Planet modifier effect methods — Mostly untested
- **Location**: planet_modifier_effect_engine.py:33-96
- **Issue**: Phase 1 reports only `process_modifier_effects_tick` as tested. All private helper methods (`_process_planet`, `_process_gravity`, `_process_radiation`, `_has_active_ability`) are untested. The gravity apply/revert logic (lines 60-68) and radiation shield logic (lines 77-83) have complex state-transition branching.
- **Untested paths**:
  - Gravity apply: active modifier + gravity_target is set → stores original, sets target (line 63-64)
  - Gravity revert: no active modifier + original stored → restores, clears original (line 67-68)
  - Radiation: active shield → sets shielding to target (line 78)
  - Radiation revert: inactive shield + current > 0 → sets to 0 (line 82-83)
  - MagicMock guard: isinstance checks for non-numeric gravity values (lines 53-55)
- **Suggested tests**:
  1. `test_process_gravity_applies_target` — verify gravity apply branch
  2. `test_process_gravity_reverts_when_inactive` — verify revert branch
  3. `test_process_gravity_guard_against_magicmock` — verify non-numeric values bypassed
  4. `test_process_radiation_applies_shielding` — verify shielding set
  5. `test_process_radiation_reverts_to_zero` — verify revert path
  6. `test_has_active_ability_non_operational_facility` — verify skip

### game/strategy/generation/density/primitives/noise.py (~117 LOC, layer: strategy)

#### [MAJOR] `_hash_coord` — Internal hash function untested
- **Location**: noise.py:15-22
- **Issue**: Coordinate-hashing function used by `_smooth_noise`. Hash collision or bit-manipulation rot could produce zero density everywhere without detection.
- **Suggested test**: `test_hash_coord_deterministic` — verify same inputs produce same output; `test_hash_coord_distributes` — verify different coordinates produce different hashes

#### [MAJOR] `_smooth_noise` — Noise generation function untested
- **Location**: noise.py:25-50
- **Issue**: Core value-noise function with smoothstep interpolation. Integer-coordinate, fractional-part, bilinear interpolation — all logic paths untested. Returns stable values but correctness depends on math.
- **Suggested test**: `test_smooth_noise_in_expected_range` — verify outputs in [0,1]; `test_smooth_noise_deterministic` — verify same seed produces same noise

### game/ui/panels/race_portrait_gallery.py (~153 LOC, layer: ui)

#### [ADVISORY] `_discover_assets` — Asset discovery with pygame loading
- **Location**: portrait_gallery.py:100-132
- **Issue**: Pygame image loading and scaling in asset discovery loop. Conventionally tested via integration. However, the `os.scandir` + filtering logic (lines 117-118) and sort (line 129) are testable business logic mixed with rendering.

#### [ADVISORY] `_update_preview` — UI preview with pygame rendering
- **Location**: portrait_gallery.py:134-152
- **Issue**: Pygame UIElement construction for portrait preview. ADVISORY as pure rendering. However, the surface scaling math (line 146) is testable.

### game/ui/research/research_scene.py (~401 LOC, layer: ui)

#### [MINOR] `ResearchTreeScene._calculate_layout` — Layout computation untested
- **Location**: research_scene.py:149-164
- **Issue**: Node position calculation based on tree depth and alphabetical sorting. Pure math logic — testable with mock TechTree. Phase 1 flagged this as untested.
- **Suggested test**: `test_calculate_layout_assigns_positions` — verify node positions assigned by depth and alphabetical order

### game/ui/screens/menu_scene.py (~109 LOC, layer: ui)

#### [ADVISORY] `MenuScene._create_buttons` — UI button construction
- **Location**: menu_scene.py:60-79
- **Issue**: Pygame_gui button creation from config. Conventionally tested via integration. However, the coordinate math (centering, Y-spacing) is testable business logic.

### game/ui/screens/race_setup/renderer.py (~234 LOC, layer: ui)

#### [ADVISORY] `RaceSetupRenderer.close_save_update_dialog` — UI widget cleanup
- **Location**: renderer.py:131-138
- **Issue**: Kill-and-clear pattern for UI widgets. Simple 6-line method. Low risk.

#### [ADVISORY] `RaceSetupRenderer.close_llm_dialog` — UI widget cleanup
- **Location**: renderer.py:182-187
- **Issue**: Same pattern as above. ADVISORY.

#### [ADVISORY] `RaceSetupRenderer.close_llm_error_popup` — UI widget cleanup
- **Location**: renderer.py:222-226
- **Issue**: Same pattern as above. ADVISORY.

### game/ui/screens/setup_screen.py (~314 LOC, layer: ui)

#### [MAJOR] `_get_ship_factory` — Module-level factory getter untested
- **Location**: setup_screen.py:51-65
- **Issue**: Lazy singleton factory getter. Uses global state, registry provider. `GameRegistries` construction from provider in this helper is a critical DI path. If broken, all battle setup breaks.
- **Suggested test**: `test_get_ship_factory_creates_once` — verify singleton behavior; `test_get_ship_factory_returns_valid_factory` — verify factory works

#### [MINOR] `BattleSetupScreen.get_team_display_groups` — Display logic untested
- **Location**: setup_screen.py:155-167
- **Issue**: Team display grouping for UI. Contains callback generation logic. MINOR — UI display method.

#### [ADVISORY] `BattleSetupScreen._handle_action_buttons` — UI rendering
- **Location**: setup_screen.py:228-240
- **Issue**: Action button rendering and hit testing. ADVISORY as UI rendering.

### game/ui/screens/strategy_click_dispatcher.py (~593 LOC, layer: ui)

#### [MAJOR] 16 mode-click handlers — Mostly untested
- **Location**: click_dispatcher.py:69-323 (dispatch + 16 handlers)
- **Issue**: Only `_hit_test_planets`, `_resolve_click_target`, and `_handle_picking` have heuristic matches. The 13 mode-specific click handlers (MOVE, JOIN, COLONIZE, TRANSFER, EDIT_MOVE, DROP_CARGO, LOAD_CARGO, WARP_TARGET, and 5 superweapon modes, SELECT) are all untested. These are high-branching UI dispatch methods.
- **Untested paths**: All fleet ops delegation calls, planet prompt flows, right-click cancel flows, error-recovery flows (BUG-93: `input_mode` reset on move failure, line 121-122)
- **Suggested tests**:
  1. `test_dispatch_click_routes_to_correct_handler` — verify mode → handler mapping
  2. `test_move_mode_right_click_cancels` — verify SELECT mode reset
  3. `test_move_mode_move_designation_failure_resets_input_mode` — verify BUG-93 fix
  4. `test_colonize_mode_single_planet_bypasses_prompt` — verify single-planet shortcut
  5. `test_colonize_mode_multiple_planets_prompts` — verify prompt flow

### game/ui/screens/strategy_window_manager.py (~390 LOC, layer: ui)

#### [MINOR] `StrategyWindowManager.unregister_modal` — Modal list management
- **Location**: window_manager.py:201-213
- **Issue**: Removes modal from live list with ValueError guard. Simple list operation, tested indirectly through `StrategyModalWindow.kill()`.

#### [MINOR] `StrategyWindowManager._open_planet_editor` — Editor dispatch
- **Location**: window_manager.py:300-306
- **Issue**: Placeholder for future planet editor. MINOR — not yet implemented.

#### [MINOR] `StrategyWindowManager._on_star_list_closed` / `_on_settings_closed` — Closure callbacks
- **Location**: window_manager.py:368, 386
- **Issue**: Simple slot-nulling closure callbacks. MINOR — trivial cleanup methods.

### game/ui/screens/transfer_view_model.py (~322 LOC, layer: ui)

#### [MAJOR] 14 ViewModel methods — Mostly untested
- **Location**: transfer_view_model.py:68-322
- **Issue**: Phase 1 reports only `apply_arrow`, `apply_max`, `build_row_data` as heuristically matched. 14 methods report as untested: `__init__`, `set_pending_zero`, `clear_all_pending`, `reset_pending`, `get_pending`, `format_pending`, `toggle_filter_empty`, `set_sources`, `select_source`, `select_target`, `target_labels`, `source_labels`, `get_amounts`, `_build_pod_rows`, `visible_rows`. The test file only tests 3 methods (`apply_arrow`, `apply_max`, `build_row_data`).
- **Untested paths**: Source/target selection state management, pending-transfer display formatting, filter-empty toggling, pod row construction, visibility filtering.
- **Suggested tests**:
  1. `test_format_pending_max_load` — verify "Load Max" display
  2. `test_format_pending_max_drop` — verify "Drop Max" display
  3. `test_toggle_filter_empty_flips_state` — verify toggle
  4. `test_reset_pending_clears_all` — verify clear behavior
  5. `test_visible_rows_filters_when_filter_empty_true` — verify visibility
  6. `test_select_source_and_target_labels` — verify dropdown label generation

### game/ui/services/battle_ui_service.py (~299 LOC, layer: ui)

#### [MINOR] `BattleUIService.__init__` — Trivial constructor
- **Location**: battle_ui_service.py:59-65
- **Issue**: Simple assignment. MINOR.

#### [MINOR] `BattleUIService._convert_component` — Internal converter
- **Location**: battle_ui_service.py:218-245
- **Issue**: Converts simulation Component to ComponentDTO. Tested indirectly through `get_ships()` which calls `_convert_ship()` which calls `_convert_component()`. MINOR — indirect coverage.

#### [MINOR] `BattleUIService._convert_beam` — Internal converter
- **Location**: battle_ui_service.py:283-299
- **Issue**: Converts beam records to BeamDTO. Same indirect coverage pattern. MINOR.

### game/simulation/components/abilities/harvester.py (~181 LOC, layer: simulation)

#### [MAJOR] `_parse_attrs` methods — Parsing logic untested
- **Location**: harvester.py:16-22, 57-64, 100-104, 138-146
- **Issue**: Four `_parse_attrs` methods for `ResourceHarvesterAbility`, `LocalStorageAbility`, `StagingYardAbility`, and `SpaceShipyardAbility` are untested. These parse ability data from `dict` or `Any`, with fallback defaults. The dict/data-non-dict branching (isinstance check) on each is untested.
- **Suggested tests**:
  1. `test_resource_harvester_parse_dict` — verify fields extracted from dict
  2. `test_resource_harvester_parse_non_dict` — verify fallback defaults
  3. `test_local_storage_parse_dict` — verify capacity extraction
  4. `test_space_shipyard_parse_dict_includes_production_rates` — verify optional field

#### [MAJOR] `StagingYardAbility` — Entire class untested
- **Location**: harvester.py:91-110
- **Issue**: Class itself not heuristically matched by Phase 1. Non-dict parsing branch (line 104) untested: `float(data)` coercion path.
- **Suggested test**: `test_staging_yard_parse_non_dict_capacity` — verify float coercion

#### [MAJOR] `PlanetaryYardAbility` — Entire class untested
- **Location**: harvester.py:113-130
- **Issue**: Class itself not heuristically matched. Has custom `__init__` (line 123) that overrides base Ability.
- **Suggested test**: `test_planetary_yard_get_primary_value` — verify returns 1.0

### game/core/formula_evaluator.py (~413 LOC, layer: core)

#### [MINOR] `_eval_node` — Internal AST evaluator
- **Location**: formula_evaluator.py:81-181
- **Issue**: Phase 1 reports `_eval_node` as untested. However, this function is the core recursive AST walker — it IS comprehensively tested through `FormulaEvaluator.evaluate()` which calls it. The heuristic mismatch is because test files call `evaluate()` not `_eval_node()` directly.
- **Note**: 14 AST node types handled. `ast.Compare` (line 153) and `ast.IfExp` (line 168) are less commonly exercised paths. The test suite covers the main evaluate path but may not cover all AST node types individually.

### game/core/paths.py (~197 LOC, layer: core)

#### [MINOR] `_find_project_root` — Module-level root discovery
- **Location**: paths.py:21-40
- **Issue**: Phase 1 reports untested. However, this runs at module import — it's implicitly tested every time any test runs. MINOR.
- **Suggested test**: `test_project_root_found` — verify returns valid path with game/ and data/ subdirectories

#### [MINOR] `Paths.get_planets_v3_dir` / `Paths.get_stars_dir` — Getter methods
- **Location**: paths.py:183, 187
- **Issue**: Phase 1 reports heuristic mismatch. These are simple pathlib getters. MINOR.

## Tier 3 — Verified Coverage (no new gaps)

### game/ai/ai_factory.py (~123 LOC, layer: ai)
- **Status**: Phase 1 indicated full coverage. Verified: CONFIRMED — all 6 symbols covered by `test_ai_factory.py` (165 LOC, 8 tests). Tests cover: create_for_ship, create_for_ships, set_grid, set_rng, error paths (missing grid/rng), adapter wrapping, and BattleEngine integration.
- **Minor note**: Missing RNG error path (line 103-108) not directly tested but covered by integration test that sets up grid without RNG.

### game/core/paths.py (~197 LOC, layer: core)
- **Status**: Phase 1 indicated Tier 2. Verified: PARTIAL — found 3 MINOR untested symbols (see above).

### game/simulation/physics_constants.py (~72 LOC, layer: simulation)
- **Status**: Phase 1 indicated full coverage. Verified: CONFIRMED — `compute_acceleration` and `compute_max_speed` tested via dedicated test files. Both formulas have zero-mass boundary guards tested. Constants K_SPEED, K_THRUST, K_TURN are implicitly verified by formula tests.

### game/strategy/engine/planet_command_handlers.py (~220 LOC, layer: strategy)
- **Status**: Phase 1 indicated full coverage. Verified: CONFIRMED — `test_planet_command_handlers.py` (548 LOC) exhaustively tests all 14 handler methods. Coverage includes: planet-not-found, wrong-owner, unknown-order-type, missing-ability-name, unsupported-order-type, validation errors, and success paths for issue/clear/delete/set-target commands.

### game/strategy/generation/density/primitives/spiral_arm.py (~103 LOC, layer: strategy)
- **Status**: Phase 1 indicated full coverage. Verified: CONFIRMED — dedicated test file covers `SpiralArmPrimitive.evaluate()`. Branch coverage on pitch_angle near zero (line 68-70), arm_width <= 0 (line 97-98), and distance < 1.0 center case (line 57-59).

### game/strategy/systems/race_randomizer.py (~446 LOC, layer: strategy)
- **Status**: Phase 1 indicated full coverage. Verified: CONFIRMED — `test_race_randomizer.py` covers all 12 public/private methods including budget-aware aptitude randomization with FEAT-12 constraints.

### game/ui/components/table/selection.py (~138 LOC, layer: ui)
- **Status**: Phase 1 indicated full coverage. Verified: CONFIRMED — `test_selection.py` covers `SingleSelect`, `MultiSelect`, `NoSelect` with click handling, Ctrl-toggling, get/clear/set operations, and "cannot remove last" guard.

### game/ui/screens/strategy_modal_window.py (~160 LOC, layer: ui)
- **Status**: Phase 1 indicated full coverage. Verified: CONFIRMED — `test_strategy_modal_window.py` covers construction, `__init_subclass__` auto-registration, `kill()` deregistration, bypass_init escape hatch, and `window_manager=None` path. Pattern #31 validation confirmed.

### game/ui/utils/portraits.py (~105 LOC, layer: ui)
- **Status**: Phase 1 indicated full coverage. Verified: CONFIRMED — `test_portraits.py` covers `get_ship_class_color` (known classes, unknown class, None input) and `create_placeholder_portrait` (gradient, text shadow, subtitle, border).

### game/simulation/__init__.py (~130 LOC, layer: simulation)
- **Status**: LOW_PRIORITY — `__init__.py` re-export file. Symbols tested via their original module tests. Tier 1 classification is correct.

### game/simulation/replay/__init__.py (~80 LOC, layer: simulation)
- **Status**: LOW_PRIORITY — `__init__.py` re-export file. Imports 3 test files. Symbols tested via their original module tests.

### game/strategy/__init__.py (~79 LOC, layer: strategy)
- **Status**: LOW_PRIORITY — `__init__.py` re-export file. Symbols tested via their original module tests.

### game/strategy/adapters/__init__.py (~10 LOC, layer: strategy)
- **Status**: LOW_PRIORITY — `__init__.py` re-export file. Single export.

### game/strategy/services/ability_sources/__init__.py (~42 LOC, layer: strategy)
- **Status**: LOW_PRIORITY — `__init__.py` re-export file. Imports 10 test files. Symbols tested via their original module tests.

## File Coverage Verification

| File | Layer | Tier | Status | Findings |
|------|-------|------|--------|----------|
| game/ai/ai_factory.py | ai | 3 | Read ✓ | 0 |
| game/ai/protocols.py | ai | 0 | Read ✓ | 4 (CRITICAL) |
| game/ai/spatial_behaviors/base.py | ai | 0 | Read ✓ | 1 (CRITICAL) |
| game/core/component_state.py | core | 0 | Read ✓ | 6 (CRITICAL) |
| game/core/formula_evaluator.py | core | 2 | Read ✓ | 1 (MINOR) |
| game/core/paths.py | core | 2 | Read ✓ | 3 (MINOR) |
| game/simulation/__init__.py | simulation | 1 | Read ✓ | 0 (LOW_PRIORITY) |
| game/simulation/combat/families/_beam_common.py | simulation | 0 | Read ✓ | 2 (CRITICAL) |
| game/simulation/combat/families/pdc.py | simulation | 0 | Read ✓ | 2 (CRITICAL) |
| game/simulation/components/abilities/harvester.py | simulation | 2 | Read ✓ | 6 (MAJOR) |
| game/simulation/entities/stat_contributors/launch.py | simulation | 0 | Read ✓ | 4 (CRITICAL) |
| game/simulation/entities/stat_contributors/movement.py | simulation | 0 | Read ✓ | 4 (CRITICAL) |
| game/simulation/physics_constants.py | simulation | 3 | Read ✓ | 0 |
| game/simulation/replay/__init__.py | simulation | 1 | Read ✓ | 0 (LOW_PRIORITY) |
| game/simulation/services/design_loader.py | simulation | 2 | Read ✓ | 1 (MINOR) |
| game/simulation/systems/tick_phase.py | simulation | 2 | Read ✓ | 2 (MAJOR + MINOR) |
| game/strategy/__init__.py | strategy | 0 | Read ✓ | 0 (LOW_PRIORITY) |
| game/strategy/adapters/__init__.py | strategy | 0 | Read ✓ | 0 (LOW_PRIORITY) |
| game/strategy/data/empire.py | strategy | 2 | Read ✓ | 1 (MINOR) |
| game/strategy/data/habitability_factors.py | strategy | 2 | Read ✓ | 3 (MAJOR) |
| game/strategy/engine/planet_command_handlers.py | strategy | 3 | Read ✓ | 0 |
| game/strategy/engine/planet_modifier_effect_engine.py | strategy | 2 | Read ✓ | 5 (MAJOR) |
| game/strategy/facade/slices/event_slice.py | strategy | 0 | Read ✓ | 6 (CRITICAL) |
| game/strategy/generation/density/primitives/noise.py | strategy | 2 | Read ✓ | 2 (MAJOR) |
| game/strategy/generation/density/primitives/spiral_arm.py | strategy | 3 | Read ✓ | 0 |
| game/strategy/services/ability_sources/__init__.py | strategy | 1 | Read ✓ | 0 (LOW_PRIORITY) |
| game/strategy/services/ability_sources/planet_intrinsic.py | strategy | 0 | Read ✓ | 6 (CRITICAL) |
| game/strategy/services/effect_ability_display.py | strategy | 0 | Read ✓ | 8 (CRITICAL) |
| game/strategy/systems/race_randomizer.py | strategy | 3 | Read ✓ | 0 |
| game/strategy/validation/superweapon_validator.py | strategy | 0 | Read ✓ | 11 (CRITICAL) |
| game/ui/components/table/selection.py | ui | 3 | Read ✓ | 0 |
| game/ui/panels/race_portrait_gallery.py | ui | 2 | Read ✓ | 2 (ADVISORY) |
| game/ui/research/research_renderer.py | ui | 0 | Read ✓ | 1 (ADVISORY + NOTE) |
| game/ui/research/research_scene.py | ui | 2 | Read ✓ | 1 (MINOR) |
| game/ui/screens/menu_scene.py | ui | 2 | Read ✓ | 1 (ADVISORY) |
| game/ui/screens/race_setup/renderer.py | ui | 2 | Read ✓ | 3 (ADVISORY) |
| game/ui/screens/setup_screen.py | ui | 2 | Read ✓ | 3 (MAJOR + MINOR + ADVISORY) |
| game/ui/screens/strategy_click_dispatcher.py | ui | 2 | Read ✓ | 5 (MAJOR) |
| game/ui/screens/strategy_modal_window.py | ui | 3 | Read ✓ | 0 |
| game/ui/screens/strategy_screen_assets.py | ui | 0 | Read ✓ | 1 (ADVISORY + NOTE) |
| game/ui/screens/strategy_window_manager.py | ui | 2 | Read ✓ | 4 (MINOR) |
| game/ui/screens/strategy_windows/move_choice_dialog.py | ui | 0 | Read ✓ | 1 (ADVISORY) |
| game/ui/screens/strategy_windows/transfer_dialogs.py | ui | 0 | Read ✓ | 1 (ADVISORY) |
| game/ui/screens/test_lab/details/resource_outcomes.py | ui | 0 | Read ✓ | 1 (ADVISORY + NOTE) |
| game/ui/screens/transfer_view_model.py | ui | 2 | Read ✓ | 6 (MAJOR) |
| game/ui/services/battle_ui_service.py | ui | 2 | Read ✓ | 3 (MINOR) |
| game/ui/utils/portraits.py | ui | 3 | Read ✓ | 0 |

## Context Usage Estimate
- Total production LOC read: ~8,673
- Total test LOC read: ~2,500
- Approximate headroom: High (>500K)
- Partially-read files (if any): None — all 47 files read completely
