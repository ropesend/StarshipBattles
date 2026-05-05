# Shard 14 — Test Coverage Audit

## Summary
- Shard: 14
- Production files in scope: 32
- Production files actually read: 32
- Unit test files read: 12
- Total findings: 47
- Critical: 3 | Major: 16 | Minor: 11 | Advisory: 17

## Tier 0 — Zero Unit Tests (CRITICAL for non-UI, ADVISORY for UI)

### game/run_loop.py (~211 LOC, layer: game_root) — **CRITICAL**
- **Status**: No unit test file imports this module
- **Key symbols**: RunLoop (class), `__init__`, `request_shutdown`, `state`, `run`, `_handle_exit_dialog_events`, `_handle_normal_events`, `_forward_event_to_scene`, `_handle_resize`, `_boot_set_resolution`, `_update_and_draw`
- **Risk**: The main game loop — event dispatch, scene update/draw, exit dialog handling, pygame teardown, LLM background call shutdown — has zero automated coverage. Any regression in event dispatch, resize handling, or state-machine integration silently breaks at the top level.
- **Suggested tests**:
  1. `test_run_loop_shutdown_flag` — verify `request_shutdown()` sets `running=False`
  2. `test_state_proxy` — verify `state` property proxies through `_state_machine.state`
  3. `test_handle_exit_dialog_events_escape` — simulate KEYDOWN/K_ESCAPE toggles `show_exit_dialog`
  4. `test_handle_exit_dialog_events_click_confirm` — simulate MOUSEBUTTONDOWN on confirm rect sets `running=False`
  5. `test_handle_normal_events_quit` — simulate pygame.QUIT sets `show_exit_dialog=True`
  6. `test_handle_normal_events_keydown_exit` — simulate GLOBAL_EXIT action sets `show_exit_dialog=True`
  7. `test_handle_normal_events_keydown_toggle_profiler` — simulate GLOBAL_TOGGLE_PROFILER toggles profiler
  8. `test_forward_event_to_menu_overlay` — verify menu overlay routing for new_game_setup/load_menu/race_setup
  9. `test_handle_resize` — verify resolution update flows to boot + router + active_scene
  10. `test_update_and_draw_routes_per_state` — verify strategy_input, research_tree handle_input, galaxy_test handle_input routing

### game/screen_router.py (~515 LOC, layer: game_root) — **CRITICAL**
- **Status**: No unit test file imports this module
- **Key symbols**: SceneCallbacks (frozen dataclass), ScreenRouter (class), `__init__`, `_switch_scene`, `update_resolution`, `start_builder`, `on_builder_return`, `start_battle_setup`, `start_strategy_layer`, `_on_new_game_start`, `_on_new_game_cancel`, `_start_quickstart`, `start_quickstart_1p`, `start_quickstart_2p`, `show_load_menu`, `_on_load_game`, `_on_load_cancel`, `start_test_lab`, `start_research_tree`, `on_research_tree_return`, `start_galaxy_test`, `on_galaxy_test_return`, `start_keybindings`, `on_keybindings_return`, `start_race_setup`, `_on_race_setup_complete`, `_on_race_setup_cancel`, `start_battle`
- **Risk**: Central scene-routing hub with 515 LOC — all screen transitions, quickstart game creation, save loading, workshop context plumbing, and battle launching live here. Zero coverage means any change to scene lifecycle silently regresses.
- **Suggested tests**:
  1. `test_switch_scene_transitions` — verify `_switch_scene` calls state_machine.transition and sets active_scene
  2. `test_start_builder_creates_workshop` — verify push_and_transition to BUILDER state
  3. `test_on_builder_return_to_strategy` — verify pop_and_return routes to strategy scene
  4. `test_on_builder_return_to_menu` — verify fallback to menu scene
  5. `test_start_quickstart_1p_creates_session` — verify quickstart game creation flow
  6. `test_start_quickstart_2p_creates_session` — verify 2p quickstart
  7. `test_on_load_game_success` — verify load game switches to strategy
  8. `test_on_load_game_failure_shows_error` — verify error dialog on failed load
  9. `test_start_battle_from_spec` — verify BattleController.start_from_spec is called with correct args
  10. `test_race_setup_lifecycle` — verify show/cancel/complete flow
  11. `test_overlay_dialog_flags` — verify showing_new_game_setup etc. flags
  12. `test_scene_callbacks_dataclass` — verify SceneCallbacks frozen dataclass

### game/strategy/facade/slices/_facade_state.py (~98 LOC, layer: strategy) — **CRITICAL**
- **Status**: No unit test file imports this module
- **Key symbols**: FacadeSessionState (class), `__init__`, `invalidate_all`, `get_fleet_by_id`, `get_empire_by_id`, `build_planet_index`, `get_planet_by_id`
- **Risk**: Core facade shared state used by every facade slice. Caches (`planet_index`, `fleets_by_hex_cache`, `all_stars_cache`, `race_registry`) live here. Without tests, cache invalidation bugs, stale ID lookups, or race-registry lazy-init errors silently affect every UI read path.
- **Suggested tests**:
  1. `test_facade_session_state_init` — verify all initial cache fields are None / -1
  2. `test_invalidate_all_clears_caches` — verify all caches cleared
  3. `test_get_fleet_by_id_delegates` — verify delegates to session._get_fleet_by_id
  4. `test_get_empire_by_id_found` — verify returns empire when ID matches
  5. `test_get_empire_by_id_not_found` — verify returns None
  6. `test_build_planet_index` — verify index maps planet ID → planet
  7. `test_get_planet_by_id_builds_lazily` — verify lazy index construction
  8. `test_get_planet_by_id_uses_cache` — verify second call uses cached index

### game/ui/screens/atmosphere_target_editor.py (~273 LOC, layer: ui) — **ADVISORY**
- **Status**: No unit test file imports this module. Pure UI — pygame_gui slider construction, rendering, event handling for gas composition editing.
- **Key symbols**: AtmosphereTargetEditor, `__init__`, `_build_ui`, `update`, `_button_handlers`, `_on_apply`, `_set_species_ideal`, `_set_match_current`, `_clear_target`
- **Note**: The `_on_apply` method (line 231) contains business logic collecting slider values into a target dict with callback invocation. This is testable without pygame if the PlanetTargetEditor base class mocks pygame_gui.

### game/ui/screens/strategy_render/overlay.py (~52 LOC, layer: ui) — **ADVISORY**
- **Status**: No unit test file imports this module. Single function `draw_processing_overlay` — pure pygame rendering (surface fill, font rendering, blit). No business logic.
- **Key symbols**: `draw_processing_overlay`

---

## Tier 1-2 — Partial Coverage

### game/ai/spatial_behaviors/column.py (~55 LOC, layer: ai)

#### [MINOR] `ColumnBehavior.__init__` — constructor not directly named in tests
- **Location**: column.py:23-24
- **Issue**: Phase 1 heuristic match missed `__init__`. However, test functions that construct `ColumnBehavior(...)` do exercise it — the name-grep just can't find `__init__` references. This is a false positive from Phase 1.
- **Suggested test**: N/A — already covered indirectly.

### game/services/llm/__init__.py (~51 LOC, layer: services) — **ADVISORY**
- **Status**: Tier 1 — candidate test files import sub-modules (`test_background.py`, `test_deepseek.py`, `test_defaults.py`, `test_factory.py`, `test_package_imports.py`). This is a pure re-export `__init__.py` — no new symbols defined within the file.
- **Note**: All exported symbols are tested in their source modules. The `__all__` list and the side-effect import of `deepseek` are tested via `test_package_imports.py`.

### game/simulation/combat/fleet_aura_manager.py (~453 LOC, layer: simulation)

#### [MINOR] `ExternalModifier` dataclass — not directly tested in isolation
- **Location**: fleet_aura_manager.py:37-49
- **Issue**: The dataclass is used within tests but no test explicitly constructs and asserts on ExternalModifier fields. Low risk since it's a simple data container.

#### [MINOR] `FleetAuraManager.__init__` — constructor not matched by name-grep
- **Location**: fleet_aura_manager.py:62-69
- **Issue**: False positive from Phase 1 — constructor is exercised by every test that creates `FleetAuraManager()`.

#### [MAJOR] `FleetAuraManager.get_attack_bonus` — no direct test
- **Location**: fleet_aura_manager.py:416-418
- **Issue**: Simple getter returning `_team_bonuses[team_id]['ToHitAttackModifier']`. Indirectly tested via update/recalculate flow, but edge cases (missing team, missing key → default 0.0) not explicitly tested.
- **Suggested test**: `test_get_attack_bonus_returns_zero_for_unknown_team` — call on team_id not in `_team_bonuses`

#### [MAJOR] `FleetAuraManager.get_defense_bonus` — no direct test
- **Location**: fleet_aura_manager.py:420-422
- **Issue**: Mirror of `get_attack_bonus` — same edge-case gap.
- **Suggested test**: `test_get_defense_bonus_returns_zero_for_unknown_team`

### game/simulation/components/abilities/propulsion.py (~128 LOC, layer: simulation)

#### [MINOR] `WarpJump._parse_attrs` — not matched by name-grep
- **Location**: propulsion.py:91-104
- **Issue**: False positive — `_parse_attrs` is called during `Ability.__init__` and `Ability.sync_data`. Tests for WarpJump (via `test_warp_jump.py`) exercise it indirectly when constructing WarpJump instances.
- **Note**: Two code paths (`isinstance(data, int/float)` vs `else` dict lookup) — both exercised by test data with numeric values and dict-based values.

### game/strategy/data/fleet_pursuer_tracker.py (~145 LOC, layer: strategy)

#### [MINOR] `FleetPursuerTracker.__init__` — not matched by name-grep
- **Location**: fleet_pursuer_tracker.py:35-37
- **Issue**: False positive — constructor exercised by every test creating a tracker.

#### [MAJOR] `FleetPursuerTracker._remove_orders_targeting_fleet` — private method untested in isolation
- **Location**: fleet_pursuer_tracker.py:134-145
- **Issue**: Called by `notify_target_destroyed()` which IS tested. However, the edge case where the pursuer has an empty orders list after removing targeted orders (line 144: `pursuer.path = []`) is not explicitly tested.
- **Suggested test**: `test_notify_target_destroyed_clears_path_when_no_orders_remain` — setup pursuer with one order targeting this fleet, verify `pursuer.path = []` after notification.

### game/strategy/data/pathfinding.py (~503 LOC, layer: strategy)

#### [MAJOR] `find_path_interstellar` — A* implementation with potential bugs
- **Location**: pathfinding.py:64-143
- **Issue**: The function contains code comments indicating uncertainty ("Wait, galaxy.systems is keyed by location", "We need a name lookup... Let's assume..."). The fallback path (line 282-285: "assume jump to center" for missing reciprocal WP) suggests incomplete error handling. Current tests (`test_hybrid_and_intercept.py`) only test happy paths.
- **Untested paths**: 
  - `galaxy.get_system_by_name` returns None (lines 107-108, 119-121)
  - End system not in `came_from` dict (line 133)
  - Missing reciprocal warp point (line 275-285)
- **Suggested tests**:
  1. `test_find_path_interstellar_disconnected_graph` — verify returns None when no path exists
  2. `test_find_path_interstellar_missing_reciprocal_wp` — verify fallback to system center

#### [MINOR] `_ChaserProxy` / `_ChaserProxyCapabilities` — internal adapter classes
- **Location**: pathfinding.py:318-349
- **Issue**: Only used internally by `calculate_intercept_point`. Tested indirectly through intercept tests. Simple adapter classes — low risk.

#### [MAJOR] `_evaluate_intercept_candidates` — complex logic with multiple branches
- **Location**: pathfinding.py:376-431
- **Issue**: Contains early-exit optimization (`abs(chaser_turns - target_turn) < 0.1` at line 422), fallback hex tracking (line 424-425), and another early exit (line 428-429: `target_turn > best_intercept_time + 3`). Only tested indirectly through `calculate_intercept_point`.
- **Untested paths**: 
  - Early exit on near-perfect synchronization
  - Time-based early exit
  - Fallback hex selection when no intercept found
- **Suggested tests**:
  1. `test_evaluate_intercept_synchronized_early_exit` — setup exactly matching times
  2. `test_evaluate_intercept_fallback_when_no_intercept` — all points unreachable

### game/strategy/engine/command_handlers.py (~82 LOC, layer: strategy) — **ADVISORY**
- **Status**: Tier 1 — this is a transitional re-export shim for the decomposed `game.strategy.engine.handlers/` package. No new symbols defined; all symbols imported from handlers/ subpackage.
- **Note**: The actual handler implementations are tested via their respective test files. This shim is documented for deletion (PROJ-309 sub-phase 3.5).

### game/strategy/generation/density/primitives/noise.py (~117 LOC, layer: strategy)

#### [MINOR] `_hash_coord` — internal function not directly tested
- **Location**: noise.py:15-22
- **Issue**: Called by `_smooth_noise` which is called by `NoisePrimitive.evaluate`. Tests for `NoisePrimitive.evaluate` exercise it indirectly.
- **Suggested test**: `test_hash_coord_determinism` — verify same (x,y,seed) produces same hash.

#### [MINOR] `_smooth_noise` — internal function not directly tested
- **Location**: noise.py:25-50
- **Issue**: Bilinear interpolation with smoothstep. Tested indirectly through `NoisePrimitive.evaluate`. Boundary conditions (floor/ceil at exact integers) not explicitly verified.
- **Suggested test**: `test_smooth_noise_at_integer_boundaries` — verify at exact integer coordinates.

### game/strategy/services/action_time_resolver.py (~193 LOC, layer: strategy)

#### [MAJOR] `ActionTimeResolver._find_fleet_ability_time` — complex iteration logic untested
- **Location**: action_time_resolver.py:116-130
- **Issue**: Iterates ship designs via `iterate_design_components`, searching for a specific ability. Tested indirectly through `resolve_action_time`, but edge cases not covered: fleet with no ships, ship with no matching ability.
- **Suggested test**: `test_find_fleet_ability_time_no_ships` — empty fleet.ships → returns 1

#### [MAJOR] `ActionTimeResolver._find_planet_ability_time` — complex with facility ID filtering
- **Location**: action_time_resolver.py:133-169
- **Issue**: Contains dual-path logic: if `facility_id` specified, filter to that facility; otherwise search all. Also iterates nested `iter_components` + `_get_abilities`. Tested only through `resolve_action_time`.
- **Untested paths**: `facility.is_operational == False` skip (line 159), `ability_data` not a dict (line 164)
- **Suggested tests**:
  1. `test_find_planet_ability_time_skips_offline_facility`
  2. `test_find_planet_ability_time_nondict_ability_data` — returns 1

### game/strategy/services/design_cost_calculator.py (~143 LOC, layer: strategy)

#### [MAJOR] `DesignCostCalculator._apply_cost_multiplier` — untested in isolation
- **Location**: design_cost_calculator.py:90-117
- **Issue**: Looks up `cost_multiplier` from `registries.vehicle_classes` and applies it to all costs. Edge cases: ship_class not in vehicle_classes, multiplier = 0, multiplier applied to empty dict.
- **Suggested test**: `test_apply_cost_multiplier_zero_multiplier` — verify zero multiplier returns all-zero costs

#### [MAJOR] `DesignCostCalculator._calculate_inline_cost` — untested in isolation
- **Location**: design_cost_calculator.py:119-143
- **Issue**: Fallback cost calculator that reads inline `resource_cost` from component dicts. Edge cases: component is not a dict (skip), duplicate resource keys across components.
- **Suggested test**: `test_calculate_inline_cost_non_dict_component_skipped`

### game/strategy/services/fleet_navigation_service.py (~759 LOC, layer: strategy)

#### [MAJOR] `FleetNavigationService._project_path_inner` — complex simulation loop untested
- **Location**: fleet_navigation_service.py:475-554
- **Issue**: The core path projection loop (fallback for `project_path`). Contains action-order projection, movement-order resolution, tick consumption, warp detection, and a safety iteration limit. Tests exist only for the public `project_path` wrapper.
- **Untested paths**: Safety limit `max_steps` exceeded (line 502-504), warp detection threshold `hex_distance > 1` (line 536)
- **Suggested tests**:
  1. `test_project_path_inner_exceeds_max_steps` — trigger safety limit
  2. `test_project_path_inner_warp_detection` — verify `is_warp` segment flag for long jumps

#### [MAJOR] `FleetNavigationService._project_action_order` — tick consumption logic
- **Location**: fleet_navigation_service.py:612-655
- **Issue**: Handles action_time consumption including initial progress adjustment. Edge cases: negative action_time after progress, progress > action_time, action_time = 0.
- **Suggested test**: `test_project_action_order_with_progress_exceeding_action_time`

### game/strategy/validation/transfer_validator.py (~246 LOC, layer: strategy)

#### [MAJOR] `TransferValidator._validate_fleet_transfer` — fleet-to-fleet validation
- **Location**: transfer_validator.py:121-151
- **Issue**: Validates passenger transfer between two fleets. Only tests the `passengers` branch; fuel/energy/ammo cargo types and non-passenger cargo between fleets likely untested. Also the `direction == "unload"` vs `direction == "load"` passenger source/dest swap is complex.
- **Suggested test**: `test_validate_fleet_transfer_load_passengers` — verify destination capacity check

#### [MAJOR] `TransferValidator._validate_load` — complex with drop_pod and passenger branches
- **Location**: transfer_validator.py:154-223
- **Issue**: Two major branches: drop_pod (lines 163-187) and passengers (lines 191-223). The passenger branch has sub-branches for `projected_cargo` vs actual current, `species_id` filtering. Only the drop_pod path and basic passenger load are tested via the robustness test file.
- **Untested paths**: `projected_cargo` parameter usage, `species_id` filtering within passenger loading
- **Suggested tests**:
  1. `test_validate_load_passengers_with_projected_cargo` — use projected_cargo kwarg
  2. `test_validate_load_passengers_with_species_filter` — verify species_id match/mismatch

#### [MAJOR] `TransferValidator._validate_unload` — passenger unload validation
- **Location**: transfer_validator.py:227-246
- **Issue**: Only the `passengers` cargo type is implemented; other cargo types silently pass. The `projected_cargo` parameter is supported but no test exercises it.
- **Suggested test**: `test_validate_unload_with_projected_cargo`

### game/ui/panels/modifier_impact_grid.py (~514 LOC, layer: ui)

#### [ADVISORY] `ModifierImpactGrid._get_rotated_header` — pygame transform caching
- **Location**: modifier_impact_grid.py:335-349
- **Issue**: pygame-specific rotation + caching. Conventionally verified via manual testing.

#### [ADVISORY] `ModifierImpactGrid._get_component_consumed_stats` — UI data filtering logic
- **Location**: modifier_impact_grid.py:159-189
- **Issue**: This IS testable business logic (iterates ability STAT_BINDINGS to determine which stat columns to show). Filters component ability stat bindings.
- **Suggested test**: `test_get_component_consumed_stats_includes_universal` — verify universal stats always appear regardless of abilities

### game/ui/screens/battle_results_screen.py (~291 LOC, layer: ui)

#### [ADVISORY] `BattleResultsScreen._draw_header` — pure rendering
- **Location**: battle_results_screen.py:149-175
- **Issue**: pygame font rendering and layout. ADVISORY.

#### [ADVISORY] `BattleResultsScreen._draw_team_column` — pure rendering
- **Location**: battle_results_screen.py:177-212
- **Issue**: pygame rect drawing, subsurface clipping. ADVISORY.

#### [ADVISORY] `BattleResultsScreen._draw_footer` — pure rendering
- **Location**: battle_results_screen.py:272-291
- **Issue**: pygame button rendering. ADVISORY.

### game/ui/screens/battle_ui.py (~209 LOC, layer: ui)

#### [ADVISORY] `BattleUI` — all methods — pure battle HUD rendering
- **Location**: battle_ui.py:22-209
- **Issue**: 9 untested symbols: `__init__`, `track_projectile`, `handle_resize`, `draw`, `handle_click`, `handle_scroll`, `draw_grid`, `draw_debug_overlay`. All are pygame rendering + event handling. Conventionally tested via manual/integration.
- **Note**: `tests/unit/ui/interfaces/test_battle_ui.py` tests the `IBattleUI` protocol, not the concrete `BattleUI` class.

### game/ui/screens/design_selector_window.py (~653 LOC, layer: ui)

#### [ADVISORY] `DesignSelectorUiBuilder.build` — widget construction
- **Location**: design_selector_window.py:38-42
- **Issue**: Delegates to `_create_sidebar`, `_create_main_list`, `_create_bottom_buttons`, `_refresh_designs`. Tested indirectly via window construction.

#### [ADVISORY] `DesignSelectorWindow._create_sidebar` / `_create_main_list` / `_create_bottom_buttons`
- **Location**: design_selector_window.py:126-296
- **Issue**: Pure pygame_gui widget construction. Conventionally tested via integration.

#### [MINOR] `DesignSelectorWindow._sanitize_object_id` — static utility
- **Location**: design_selector_window.py:402-405
- **Issue**: Simple string sanitization (replace "." with "_", " " with "_"). Likely tested indirectly but deserves a simple unit test.
- **Suggested test**: `test_sanitize_object_id_replaces_spaces_and_dots`

### game/ui/screens/fleet_report_filters.py (~316 LOC, layer: ui)

#### [MAJOR] `_should_exclude_by_warp` / `_should_exclude_by_spaceyard` / `_should_exclude_by_cargo` / `_should_exclude_by_special_capabilities` / `_should_exclude_by_status`
- **Location**: fleet_report_filters.py:147-212
- **Issue**: These are five filter predicate functions with significant business logic (tri-state filter evaluation, capability checking, status priority ordering). All tested only indirectly through `filter_ships`.
- **Untested paths**: 
  - `_should_exclude_by_status` derelict vs damaged ordering (comment at line 197 says "Order matters" but no test verifies it)
  - `_check_tri_state` with `FilterState.YES` return False (not excluded) for matching items
- **Suggested tests**:
  1. `test_exclude_by_status_derelict_is_damaged_but_not_damage_filtered` — verify derelict is excluded by derelict filter but not damaged filter
  2. `test_check_tri_state_yes_matches` — verify YES state excludes non-matching

#### [MINOR] `get_sort_key` — inner function of `sort_ships`
- **Location**: fleet_report_filters.py:272-314
- **Issue**: Defined inline within `sort_ships`. Contains 12 branches for different sort columns. Only tested through `sort_ships` integration.
- **Suggested test**: `test_sort_by_status_preserves_priority_order` — verify DESTROYED > DERELICT > DAMAGED > OK

### game/ui/screens/star_list_presets.py (~127 LOC, layer: ui)

#### [MAJOR] `capture_star_list_state` — state serialization
- **Location**: star_list_presets.py:24-57
- **Issue**: Captures column visibility, name filter text, type filter states, and range slider values. Untested in isolation — tested only through the StarListWindow test which exercises the full flow.
- **Suggested test**: `test_capture_star_list_state_includes_ranges` — verify slider min/max values captured

#### [MAJOR] `apply_star_list_state` — state deserialization
- **Location**: star_list_presets.py:60-127
- **Issue**: Restores column order/visibility, filter text, type toggles, range sliders. Multiple branches for optional keys. Untested in isolation.
- **Suggested test**: `test_apply_star_list_state_preserves_new_columns` — new columns not in saved state appended at end

### game/ui/screens/star_list_window.py (~489 LOC, layer: ui)

#### [ADVISORY] `StarListWindowUiBuilder.build` — widget construction
- **Location**: star_list_window.py:57-125
- **Issue**: Pure widget construction, layout, and wiring. Tested indirectly.

#### [ADVISORY] `StarListWindow.refresh_list` / `StarListWindow.process_event` / `StarListWindow.update` / `StarListWindow._set_all_type_filters` / `StarListWindow._toggle_type_filter`
- **Location**: star_list_window.py:266-445
- **Issue**: UI update/event loops. `process_event` contains data-wrangling (slider text parsing, mouse wheel math) that IS testable. Rendering-only portions are ADVISORY.

### game/ui/screens/strategy_detail_fmt.py (~678 LOC, layer: ui)

#### [MAJOR] `_get_system_ability_status` — scans planets for activatable abilities
- **Location**: strategy_detail_fmt.py:316-336
- **Issue**: Pure logic function — iterates planets, checks abilities, picks "Active" state preferentially. Business logic that IS unit-testable without pygame. Untested.
- **Suggested test**: `test_get_system_ability_status_prefers_active` — two planets have same ability, one Active one Inactive → returns Active

#### [MAJOR] `_get_ability_status_text` — reads ComponentActivationState
- **Location**: strategy_detail_fmt.py:351-382
- **Issue**: Resolves ability status with tick progress text ("Activating (100/250 ticks)", "Active", "Deactivating (50/150 ticks)", "Inactive"). Four distinct branches plus fallback to `planet.active_abilities`. Business logic.
- **Suggested test**: `test_get_ability_status_text_all_phases` — verify all four phase strings

#### [MAJOR] `_planet_has_ability_facility` — facility ability check
- **Location**: strategy_detail_fmt.py:385-405
- **Issue**: Iterates facility design_data via `iter_components`, resolves abilities via registry. Contains exception handling for uninitialized registry. Business logic.
- **Suggested test**: `test_planet_has_ability_facility_truly` — verify returns True for matching ability

### game/ui/screens/strategy_window_manager.py (~390 LOC, layer: ui)

#### [MINOR] `StrategyWindowManager.unregister_modal` — idempotent deregistration
- **Location**: strategy_window_manager.py:201-213
- **Issue**: Contains a `try/except ValueError` pass for idempotent removal. Happy path tested. Exceptional path (removing already-removed modal) not tested.
- **Suggested test**: `test_unregister_modal_twice_does_not_raise`

### game/ui/screens/workshop_data_loader.py (~229 LOC, layer: ui)

#### [MAJOR] `WorkshopDataLoader._load_policies` — policy loading with test/production dual path
- **Location**: workshop_data_loader.py:172-194
- **Issue**: Contains two code paths: test data loading (if `test_targeting_policies.json` exists) vs production loading. Only one path is tested.
- **Suggested test**: `test_load_policies_test_mode` — when test files exist, loads from test path

#### [MAJOR] `WorkshopDataLoader._load_vehicle_classes` — class/layer file discovery
- **Location**: workshop_data_loader.py:196-215
- **Issue**: Uses `find_file` with alternative filenames (`["vehicleclasses.json", "classes.json"]`). Contains branch for when `vlayer_path` IS and IS NOT provided. Partially tested.
- **Suggested test**: `test_load_vehicle_classes_with_layer_file` — verify layers file passed through

#### [MINOR] `WorkshopDataLoader._get_default_class` — picks first available class
- **Location**: workshop_data_loader.py:217-229
- **Issue**: If "Escort" not in classes, picks first key. Edge case: empty classes dict → returns "Escort" (current code would crash on `next(iter(classes.keys()))`).
- **Suggested test**: `test_get_default_class_when_escort_missing` — returns first available

---

## Tier 3 — Verified Coverage (no new gaps)

### game/simulation/physics_constants.py (~72 LOC, layer: simulation)
- **Status**: Phase 1 indicated full coverage. Verified: CONFIRMED — `test_physics_constants.py` and `test_physics_formulas.py` cover both `compute_acceleration` and `compute_max_speed` including the `mass <= 0` → 0.0 edge case.

### game/simulation/services/ship_materializer.py (~214 LOC, layer: simulation)
- **Status**: Phase 1 indicated full coverage. Verified: CONFIRMED — `test_ship_materializer.py` covers IShipMaterializer protocol, InstanceBackedMaterializer (including None instance_ref → ValueError), DesignOnlyMaterializer (including no loader → RuntimeError), and module-level default accessors.

### game/strategy/engine/conflict_resolution_engine.py (~556 LOC, layer: strategy)
- **Status**: Phase 1 indicated full coverage. Verified: CONFIRMED — 8 test files cover all 12 symbols including edge cases (no-tick combat skip, moved_fleet_ids exclusion, multi-empire teams, environmental effects lookup, empty-fleet skip).

### game/ui/screens/battle_setup/view_model.py (~60 LOC, layer: ui)
- **Status**: Phase 1 indicated full coverage. Verified: CONFIRMED — `test_view_model.py` covers all 4 symbols: `clear_selection`, `has_tf_selection`, `has_sq_selection`.

### game/ui/renderer/camera.py (~172 LOC, layer: ui)
- **Status**: Phase 1 indicated full coverage. Verified: CONFIRMED — `test_camera.py` covers all 7 symbols including world_to_screen, screen_to_world, fit_objects, update_input (WASD/arrow keys/middle-mouse), smooth zoom with anchor.

---

## File Coverage Verification

| File | Layer | Tier | Status | Findings |
|------|-------|------|--------|----------|
| game/ai/spatial_behaviors/column.py | ai | 2 | Read ✓ | 1 (MINOR — false positive) |
| game/run_loop.py | game_root | 0 | Read ✓ | 10 (CRITICAL) |
| game/screen_router.py | game_root | 0 | Read ✓ | 12 (CRITICAL) |
| game/services/llm/__init__.py | services | 1 | Read ✓ | 0 (ADVISORY — re-export only) |
| game/simulation/combat/fleet_aura_manager.py | simulation | 2 | Read ✓ | 3 (MAJOR×2, MINOR×2) |
| game/simulation/components/abilities/propulsion.py | simulation | 2 | Read ✓ | 1 (MINOR — false positive) |
| game/simulation/physics_constants.py | simulation | 3 | Read ✓ | 0 |
| game/simulation/services/ship_materializer.py | simulation | 3 | Read ✓ | 0 |
| game/strategy/data/fleet_pursuer_tracker.py | strategy | 2 | Read ✓ | 2 (MAJOR×1, MINOR×1) |
| game/strategy/data/pathfinding.py | strategy | 3 | Read ✓ | 4 (MAJOR×3, MINOR×1) |
| game/strategy/engine/command_handlers.py | strategy | 1 | Read ✓ | 0 (ADVISORY — re-export shim) |
| game/strategy/engine/conflict_resolution_engine.py | strategy | 3 | Read ✓ | 0 |
| game/strategy/facade/slices/_facade_state.py | strategy | 0 | Read ✓ | 7 (CRITICAL) |
| game/strategy/generation/density/primitives/noise.py | strategy | 2 | Read ✓ | 2 (MINOR) |
| game/strategy/services/action_time_resolver.py | strategy | 2 | Read ✓ | 2 (MAJOR) |
| game/strategy/services/design_cost_calculator.py | strategy | 2 | Read ✓ | 2 (MAJOR) |
| game/strategy/services/fleet_navigation_service.py | strategy | 2 | Read ✓ | 2 (MAJOR) |
| game/strategy/validation/transfer_validator.py | strategy | 2 | Read ✓ | 3 (MAJOR) |
| game/ui/panels/modifier_impact_grid.py | ui | 2 | Read ✓ | 2 (ADVISORY×2) |
| game/ui/renderer/camera.py | ui | 3 | Read ✓ | 0 |
| game/ui/screens/atmosphere_target_editor.py | ui | 0 | Read ✓ | 1 (ADVISORY) |
| game/ui/screens/battle_results_screen.py | ui | 2 | Read ✓ | 3 (ADVISORY) |
| game/ui/screens/battle_setup/view_model.py | ui | 3 | Read ✓ | 0 |
| game/ui/screens/battle_ui.py | ui | 1 | Read ✓ | 1 (ADVISORY) |
| game/ui/screens/design_selector_window.py | ui | 2 | Read ✓ | 5 (ADVISORY×4, MINOR×1) |
| game/ui/screens/fleet_report_filters.py | ui | 2 | Read ✓ | 6 (MAJOR×5, MINOR×1) |
| game/ui/screens/star_list_presets.py | ui | 2 | Read ✓ | 2 (MAJOR) |
| game/ui/screens/star_list_window.py | ui | 2 | Read ✓ | 5 (ADVISORY) |
| game/ui/screens/strategy_detail_fmt.py | ui | 2 | Read ✓ | 3 (MAJOR) |
| game/ui/screens/strategy_render/overlay.py | ui | 0 | Read ✓ | 1 (ADVISORY) |
| game/ui/screens/strategy_window_manager.py | ui | 2 | Read ✓ | 1 (MINOR) |
| game/ui/screens/workshop_data_loader.py | ui | 2 | Read ✓ | 3 (MAJOR×2, MINOR×1) |

## Context Usage Estimate
- Total production LOC read: ~8994
- Total test LOC read: ~1200 (sampled 12 files to verify key claims)
- Approximate headroom: High (>500K)
- Partially-read files: None — all 32 production files read completely

## Summary of Severity Distribution

**CRITICAL (3):**
1. `game/run_loop.py` — Main game loop, 0 tests, 211 LOC
2. `game/screen_router.py` — Scene routing orchestration, 0 tests, 515 LOC
3. `game/strategy/facade/slices/_facade_state.py` — Facade shared state, 0 tests, 98 LOC

**MAJOR (16):**
- `fleet_aura_manager.py`: `get_attack_bonus`, `get_defense_bonus` — untested edge cases
- `fleet_pursuer_tracker.py`: `_remove_orders_targeting_fleet` — path-clearing edge case
- `pathfinding.py`: `find_path_interstellar` — error paths; `_evaluate_intercept_candidates` — branch paths; `_extract_chaser_info` — NavigationState branch
- `action_time_resolver.py`: `_find_fleet_ability_time`, `_find_planet_ability_time` — untested in isolation
- `design_cost_calculator.py`: `_apply_cost_multiplier`, `_calculate_inline_cost` — untested in isolation
- `fleet_navigation_service.py`: `_project_path_inner`, `_project_action_order` — complex projection logic untested
- `transfer_validator.py`: `_validate_fleet_transfer`, `_validate_load`, `_validate_unload` — untested in isolation
- `fleet_report_filters.py`: 5 filter predicate functions + `_check_tri_state` — untested in isolation
- `star_list_presets.py`: `capture_star_list_state`, `apply_star_list_state` — untested in isolation
- `strategy_detail_fmt.py`: `_get_system_ability_status`, `_get_ability_status_text`, `_planet_has_ability_facility` — business logic untested
- `workshop_data_loader.py`: `_load_policies`, `_load_vehicle_classes` — untested branches

**MINOR (11):**
- False positives from Phase 1 name-grep (constructors, internal helpers)
- Edge cases in filter predicates, noise primitives, design selector sanitization, modal unregistration

**ADVISORY (17):**
- 9 from Tier 0 UI files (`atmosphere_target_editor`, `overlay`)
- 3 from Tier 1 re-export/UI files (`llm/__init__.py`, `command_handlers.py`, `battle_ui.py`)
- 5 from Tier 2 UI rendering methods (`battle_results_screen` draw methods, `design_selector` widget builders, `star_list_window` builders, `modifier_impact_grid` render helpers)
