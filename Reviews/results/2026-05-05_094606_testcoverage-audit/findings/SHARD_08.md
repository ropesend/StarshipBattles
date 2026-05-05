# Shard 08 — Test Coverage Audit

## Summary
- Shard: 08
- Production files in scope: 38
- Production files actually read: 38
- Unit test files read: 28+ (across coverage matrix entries)
- Total findings: 47
- Critical: 4 | Major: 16 | Minor: 14 | Advisory: 13

## Tier 0 — Zero Unit Tests (CRITICAL for non-UI, ADVISORY for UI)

### game/core/protocols/ui.py (~112 LOC, layer: core)
- **Status**: No unit test file imports this module. Tier 0.
- **Key symbols**: `IScene` (Protocol), `ICamera` (Protocol), `is_camera` (TypeGuard)
- **Risk**: These protocols define the abstraction boundary between UI and core layers. IScene is used by every screen class; ICamera is used by research and strategy rendering. Untested protocol conformance means implementors could drift without detection.
- **Suggested tests**:
  1. `test_iscene_protocol` — Verify that Screen classes satisfy IScene (has handle_event, update, draw, handle_resize)
  2. `test_icamera_protocol` — Verify Camera satisfies ICamera (has width, height, zoom, world_to_screen, screen_to_world)
  3. `test_is_camera_typeguard` — Test the TypeGuard with Camera and non-Camera objects

### game/strategy/data/planet_gen.py (~604 LOC, layer: strategy)
- **Status**: No unit test file imports this module (TIER 0 per Phase 1). Zero test coverage.
- **Key symbols**: `PlanetGenerator`, `generate_system_bodies`, `_generate_orbital_slots`, `_generate_moons`, `_create_planet_objects`, `_determine_type`, `_generate_resources`, `_generate_surface_flags`, `_generate_mass_constrained`, `_collect_star_exclusion_zones`
- **Risk**: This is ~600 LOC of planet generation logic with no tests. It drives galaxy generation for new games. Bugs in mass distribution, type classification, or resource generation would silently produce broken game worlds. Classification logic (_determine_type) has 30+ branches with no coverage. Resource generation has complex logarithmic scaling formulas.
- **Suggested tests**:
  1. `test_determine_type_gas_giant` — mass > gas_giant_min → JOVIAN
  2. `test_determine_type_ice_giant` — mass between giant_min and gas_giant_min → ICE_GIANT
  3. `test_determine_type_chthonian` — hot giant with low pressure → CHTHONIAN
  4. `test_determine_type_continental` — moderate water, temp, pressure → CONTINENTAL
  5. `test_determine_type_pelagic` — high water → PELAGIC
  6. `test_determine_type_magma` — extreme heat → MAGMA
  7. `test_generate_mass_constrained_small_bias` — verify log-normal distribution within bounds
  8. `test_generate_mass_constrained_fallback` — when gauss misses, falls back to uniform
  9. `test_generate_resources_scaling` — verify Earth-mass baseline produces expected quantities
  10. `test_collect_star_exclusion_zones` — secondary stars create exclusion hex zones
  11. `test_generate_moons_chance` — moon chance scales with primary mass
  12. `test_generate_system_bodies_with_blueprint` — blueprint planet_count respected
  13. `test_generate_system_bodies_zero_planets` — 0 planet count returns empty dict

### game/ui/screens/test_lab/test_executor.py (~N LOC, layer: ui)
- **Status**: Per Phase 1, no candidate test files import this module. Very likely TIER 0.
- **Risk**: Test executor handles test lifecycle in Combat Lab. Core functionality tested only via Combat Lab integration tests.
- **Note**: This file manages running Combat Lab tests. Business logic (scenario execution, result collection) should be testable.
- **Severity**: ADVISORY (UI) with MAJOR note — contains testable orchestration logic.

### game/ui/widgets/panel_factory.py (~N LOC, layer: ui)
- **Status**: Factory class per Pattern #15. UI construction. Per Phase 1, likely TIER 0 or 1.
- **Risk**: Panel factory creates panel instances — fallback/error paths untested.
- **Severity**: ADVISORY (UI widget factory)

## Tier 1-2 — Partial Coverage

### game/ai/target_evaluator.py (~331 LOC, layer: ai)

#### [MAJOR] `TargetEvaluator._eval_distance_rule` — Untested
- **Location**: target_evaluator.py:41-78
- **Issue**: Phase 1 reports no heuristic match for this method. Despite having 6 test files importing the module, distance rule evaluation appears untested directly. The `evaluate` method tests may exercise it indirectly.
- **Untested path**: nearest vs farthest vs distance type dispatch; cached vs uncached distance paths
- **Suggested test**: `test_distance_nearest_with_weight` — nearest target with weight > 0 returns negative-weighted distance

#### [MAJOR] `TargetEvaluator._eval_mass_rule` — Untested
- **Location**: target_evaluator.py:81-110
- **Issue**: No direct tests. Mass-based targeting (largest, smallest, strongest, weakest) untested.
- **Untested path**: mass type routing; weight vs factor path; negative factor for smallest/weakest
- **Suggested test**: `test_mass_largest_with_weight` — largest target with weight > 0 returns mass * weight

#### [MAJOR] `TargetEvaluator._eval_damage_rule` — Untested
- **Location**: target_evaluator.py:137-166
- **Issue**: most_damaged and least_damaged rules untested. HP percentage math (multiplying by 100 when weight > 0) has no coverage.
- **Suggested test**: `test_damage_most_damaged` — ship with 0.5 HP% gets negative-weighted score when weight > 0

#### [MAJOR] `TargetEvaluator._eval_least_armor_rule` — Untested
- **Location**: target_evaluator.py:197-215
- **Issue**: Armor scoring untested. Non-ship candidate fallback path (returns 0) untested.
- **Untested path**: `is_combat_ship == False` path returns (0, True); Component.current_hp sum
- **Suggested test**: `test_least_armor_projectile` — non-combat-ship (projectile) returns (0, True)

#### [MAJOR] `TargetEvaluator._eval_pdc_arc_rule` — Untested
- **Location**: target_evaluator.py:218-238
- **Issue**: PDC arc rule has multiple branches: not-missile pass-through, in-arc positive score, required-but-not-in-arc (returns match=False), strong penalty for non-required miss
- **Suggested test**: `test_pdc_arc_missile_in_arc` — missile in PDC arc returns weighted score

#### [MAJOR] `TargetEvaluator._eval_capability_rule` — Untested
- **Location**: target_evaluator.py:241-263
- **Issue**: Router function dispatches to has_weapons, least_armor, pdc_arc. Each path should be tested via evaluate() with appropriate rules.
- **Suggested test**: `test_capability_rule_has_weapons` — rule type='has_weapons' dispatches correctly

#### [MINOR] `TargetEvaluator.evaluate` — Missing stat_helpers=None path
- **Location**: target_evaluator.py:266-331
- **Issue**: evaluate() is tested but the `stat_helpers is None` path (lines 295-299) which uses default helpers is likely untested.
- **Suggested test**: `test_evaluate_no_stat_helpers` — call evaluate without stat_helpers, verify defaults are used

### game/assets/asset_manager.py (~350 LOC, layer: assets)

#### [MAJOR] `AssetManager.load_star_image` — Untested
- **Location**: asset_manager.py:132-158
- **Issue**: Star image loading with resolution fallback chain completely untested. Fallback logic (try each resolution, return missing texture on all fail) has no coverage.
- **Suggested test**: `test_load_star_image_resolution_fallback` — all resolutions fail → returns missing texture

#### [MAJOR] `AssetManager.get_star_core_info` — Untested
- **Location**: asset_manager.py:160-176
- **Issue**: Star core metadata lookup with default fallback dict untested.
- **Suggested test**: `test_get_star_core_info_known` — known star returns metadata; unknown star returns defaults

#### [MAJOR] `AssetManager.get_star_asset_key_for_type` — Untested
- **Location**: asset_manager.py:178-191
- **Issue**: Star type to asset key mapping from manifest.
- **Suggested test**: `test_get_star_asset_key_for_type` — verify MAIN_SEQUENCE → 'yellow' mapping

#### [MINOR] `AssetManager.__init__` — Indirect only
- **Location**: asset_manager.py:31-37
- **Issue**: Constructor is exercised by tests that create AssetManager instances, but `_load_star_metadata` error path (missing file warning) not tested directly.

#### [MINOR] `AssetManager.clear` — Untested
- **Location**: asset_manager.py:48-52
- **Issue**: Cache clearing for test isolation. Never called in tests (tests create fresh instances instead).
- **Note**: Low priority since tests use set_default_asset_manager with fresh instances.

### game/core/registry.py (~470 LOC, layer: core)

#### [MINOR] `GameRegistries.__post_init__` — Untested edge case
- **Location**: registry.py:86-90
- **Issue**: The `resource_catalog is None` guard (auto-creates empty ResourceCatalog) is not directly tested. Tests typically pass explicit resource_catalog.
- **Suggested test**: `test_game_registries_default_resource_catalog` — create GameRegistries without resource_catalog, verify empty catalog is auto-created

#### [MINOR] `RegistryManager.unfrozen` — Context manager paths
- **Location**: registry.py:172-185
- **Issue**: The `unfrozen()` context manager restores prior freeze state. Exception path (finally clause) likely covered through indirect test but not explicitly verified.
- **Note**: Low priority — heavily used by Combat Lab runner and test fixtures.

#### [MINOR] `freeze_registry` — Module-level wrapper
- **Location**: registry.py:311-317
- **Issue**: Simple wrapper around RegistryManager.freeze(). Likely exercised indirectly through test setup.

### game/simulation/combat/combat_events.py (~164 LOC, layer: simulation)

#### [MINOR] `CombatEventBus.unsubscribe` — Untested
- **Location**: combat_events.py:135-139
- **Issue**: Unsubscribe path (removing a registered callback) not tested. No-op when callback not found.
- **Suggested test**: `test_unsubscribe_registered_callback` — subscribe then unsubscribe; verify callback not called on emit

#### [MINOR] `CombatEventBus.emit` — Subscriber exception path
- **Location**: combat_events.py:142-163
- **Issue**: The broad except clause (line 161) catching subscriber exceptions is unlikely to be explicitly tested.
- **Note**: This is an intentional broad catch for robustness; formal testing of exception swallowing is low priority.

### game/strategy/adapters/simulation_adapter.py (~490 LOC, layer: strategy)

#### [MAJOR] `SimulationBattleResolver._resolve_seed` — Seed RNG creation path
- **Location**: simulation_adapter.py:330-336
- **Issue**: The lazy creation of `_seed_rng` (lines 333-335) when seed is None. The `random.Random()` instance is used for implicit seeding — this path is exercised in production but may not have deterministic test coverage.
- **Suggested test**: `test_resolve_seed_random_fallback` — verify that no-seed calls produce different seeds

#### [MINOR] `SimulationBattleResolver._build_capture_context` — Fallback paths
- **Location**: simulation_adapter.py:367-446
- **Issue**: Multiple fallback paths for missing fleet metadata (unknown empire, missing location, missing owner). The `ship_instance_lookup` closure's broad except (line 435) path.
- **Note**: These are defensive paths; coverage via integration tests.

#### [MINOR] `_resolve_registries` — Fallback to global provider
- **Location**: simulation_adapter.py:39-52
- **Issue**: The None → get_default_registry_provider() fallback path. Tests typically pass explicit registries.

### game/strategy/combat/post_battle_hook.py (~221 LOC, layer: strategy)

#### [MAJOR] `_prune_empty_fleets` — Exception paths
- **Location**: post_battle_hook.py:200-218
- **Issue**: Multiple branch paths: empire not in empires dict (returns), no `fleets` attribute on empire (returns), fleet not in empire_fleets during removal (ValueError caught). Only the happy path tested.
- **Suggested test**: `test_prune_empty_fleets_empire_not_found` — empire missing from mapping → no-op

#### [MAJOR] `apply_outcome_to_fleets` — Orphan outcome entry
- **Location**: post_battle_hook.py:72-81
- **Issue**: Missing ShipInstance lookup path (logged warning, skipped) not tested. Unknown ShipStatus (line 129-132) not tested.
- **Suggested test**: `test_apply_outcome_orphan_ship` — ship_outcome with non-existent instance_id → logged and skipped

#### [MINOR] `_apply_survivor_outcome` — outcome_max_hp <= 0 fallback
- **Location**: post_battle_hook.py:166-170
- **Issue**: Defensive fallback when outcome reports max_hp <= 0 (uses prior_max_hp). Untested edge case.
- **Suggested test**: `test_survivor_outcome_zero_max_hp` — outcome reports max_hp=0.0 → falls back to prior snapshot

### game/strategy/data/component_activation_state.py (~156 LOC, layer: strategy)

#### [MAJOR] `ComponentActivationState.tick` — DEACTIVATING phase
- **Location**: component_activation_state.py:59-67
- **Issue**: ACTIVATING phase tested, DEACTIVATING phase transition likely also tested indirectly, but the `energy_drain_rate = 0.0` reset on completion (line 65) is a specific behavior to verify.
- **Suggested test**: `test_deactivating_complete_resets_energy_drain` — verify energy_drain_rate set to 0 on DEACTIVATING completion

#### [MINOR] `ComponentActivationState.start_activating` — ValueError on wrong phase
- **Location**: component_activation_state.py:77-81
- **Issue**: ValueError raised when not in INACTIVE phase. Should be verified.

#### [MINOR] `ComponentActivationState.from_dict` — Backward compat path
- **Location**: component_activation_state.py:144-156
- **Issue**: Old format `{'active': True/False}` deserialization path. Backward compat could rot.
- **Suggested test**: `test_from_dict_old_format_active` — `{'active': True}` → ACTIVE phase

### game/strategy/data/galaxy_spatial_index.py (~192 LOC, layer: strategy)

#### [MAJOR] `GalaxySpatialIndex.get_system_at_location` — Multiple return paths
- **Location**: galaxy_spatial_index.py:108-143
- **Issue**: Four distinct lookup paths (direct system, planet, zone, warp point). Tests likely cover the happy path but not all four branches with None fallthrough.
- **Suggested test**: `test_get_system_at_warp_point` — location at a warp point returns correct system

#### [MINOR] `GalaxySpatialIndex.get_system_of_object` — Non-location objects
- **Location**: galaxy_spatial_index.py:52-53
- **Issue**: Objects without `location` attribute return None. Untested guard.

### game/strategy/engine/atmosphere_engine.py (~147 LOC, layer: strategy)

#### [MAJOR] `AtmosphereEngine.process_atmosphere` — Full processing pipeline
- **Location**: atmosphere_engine.py:40-51
- **Issue**: The main pipeline includes validation, per-colony processing, facility iteration. Unit tests likely cover tick-level validation but the full atmosphere modification math (mass-to-Pa conversion, proportional distribution, overshoot guard) may not be directly tested.
- **Suggested test**: `test_process_atmosphere_proportional_distribution` — multiple gases, verify proportional allocation
- **Suggested test**: `test_process_atmosphere_no_overshoot` — allocation would overshoot target → clamped to exact delta

#### [MAJOR] `AtmosphereEngine._extract_atmo_modifier` — List data path
- **Location**: atmosphere_engine.py:140-147
- **Issue**: Returns None for non-dict/non-list data. The `isinstance(data, list)` branch (lines 72-73) summing multiple entries is a distinct code path.
- **Suggested test**: `test_extract_atmo_modifier_list` — list-typed modifier data summed correctly

### game/strategy/engine/command_handlers.py (~82 LOC, layer: strategy)

#### [ADVISORY] Re-export shim — No new logic
- **Location**: command_handlers.py:1-82
- **Issue**: This is a pure re-export shim (`__init__.py`-style). All symbols are imported from `game.strategy.engine.handlers/`. Listed as ADVISORY / LOW_PRIORITY — the actual handler code lives in the handlers subpackage and has separate coverage.
- **Note**: Transitional shim per PROJ-309. Should be tracked as documentation debt rather than coverage gap.

### game/strategy/engine/game_session.py (~454 LOC, layer: strategy)

#### [MAJOR] `GameSession.from_dict` — Multiple error recovery paths
- **Location**: game_session.py:331-454
- **Issue**: Large deserialization method with 10+ sequential steps. Multiple PersistenceException raise paths (missing config, galaxy, empire keys). Pursuer tracker rebuild (lines 442-448) conditional on order types.
- **Untested paths**: Corrupt data error paths, pursuer tracker rebuild for MOVETO_FLEET/JOIN_FLEET orders
- **Suggested test**: `test_from_dict_missing_config` — 'config' key missing raises PersistenceException

#### [MINOR] `GameSession.handle_command` — Non-ISSUE_ORDER command
- **Location**: game_session.py:282-284
- **Issue**: The branch where `command.type != ISSUE_ORDER` returns None. Untested.

### game/strategy/engine/turn_phase_registry.py (~297 LOC, layer: strategy)

#### [MAJOR] `DEFAULT_TICK_PHASE_LIST` — Golden test coverage
- **Location**: turn_phase_registry.py:174-297
- **Issue**: The 15-phase descriptor list is pinned by `test_default_tick_phase_list.py` (golden order test per docstring). However, the individual hook functions (`_log_turn_start_tick_1`, `_log_after_construction_tick_1`, `_accumulate_env_events`, `_capture_move_queue`, `_derive_moved_fleet_ids`) MAY lack direct unit tests.
- **Suggested test**: `test_capture_move_queue` — verify move_queue and pre_movement_locations are populated
- **Suggested test**: `test_derive_moved_fleet_ids` — verify moved_fleet_ids contains fleet whose location changed

#### [MINOR] `_resolve_planet_modifier_effects` — Late import path
- **Location**: turn_phase_registry.py:152-164
- **Issue**: Late import of PlanetModifierEffectEngine inside resolver. Import failure path untested.

### game/strategy/engine/turn_state_snapshot.py (~134 LOC, layer: strategy)

#### [MAJOR] `TurnStateSnapshot.dump_crash_snapshot` — Write failure path
- **Location**: turn_state_snapshot.py:102-134
- **Issue**: Crash snapshot writing with OSError/TypeError handling (line 133). The error path (disk full, permission denied) is untested.
- **Suggested test**: `test_dump_crash_snapshot_os_error` — mock open to raise OSError → logged error, no crash

#### [MINOR] `TurnStateSnapshot.capture` — Serialization failure
- **Location**: turn_state_snapshot.py:53-61
- **Issue**: The `except Exception` path wrapping in PersistenceException. Logic is straightforward but untested for raise path.

### game/strategy/events/event_log.py (~188 LOC, layer: strategy)

#### [MAJOR] `EventLog.get_events_for_turn` — empire_id scoping
- **Location**: event_log.py:95-113
- **Issue**: Two distinct code paths: empire_id is None (no filter) vs empire_id scoped. GLOBAL_EVENT_EMPIRE_ID broadcast logic.
- **Suggested test**: `test_get_events_for_turn_with_empire_id` — filters by empire and includes global events

#### [MAJOR] `EventLog.get_events_by_category` — empire_id + category branch
- **Location**: event_log.py:115-142
- **Issue**: Four branches (all+no_filter, category+no_filter, all+empire, category+empire). Enum coercion branch (line 131).
- **Suggested test**: `test_get_events_by_category_with_empire` — category filter + empire scope

#### [MINOR] `Event.from_dict` — require_keys validation
- **Location**: event_log.py:62-67
- **Issue**: `require_keys` raises PersistenceException on missing keys. Untested error path.

### game/strategy/facade/dto/fleet_dto.py (~235 LOC, layer: strategy)

#### [MAJOR] `FleetInfo.from_fleet` — Multiple order type branches
- **Location**: fleet_dto.py:103-219
- **Issue**: Order description logic has 6 branches (MOVE/COLONIZE, MOVE_TO_FLEET/JOIN_FLEET, BUILD, TRANSFER with dict direction, fallback "Transfer"). Dict target with planet object, HexCoord target, Planet target. Transfer order with load vs unload direction.
- **Untested paths**: TRANSFER order target description, MOVE_TO_FLEET with fleet target, BUILD order display
- **Suggested test**: `test_from_fleet_transfer_load_order` — TRANSFER load order produces correct description
- **Suggested test**: `test_from_fleet_build_order` — BUILD order description shows queue count

#### [MINOR] `FleetInfo._aggregate_carried_items` — Unknown item field
- **Location**: fleet_dto.py:222-235
- **Issue**: getattr defaults (Unknown, unknown, 0.0) for missing fields. Key collision aggregation.

### game/strategy/generation/density/primitives/linear.py (~86 LOC, layer: strategy)

#### [MAJOR] `LinearPrimitive.evaluate` — Multiple spatial branches
- **Location**: linear.py:37-86
- **Issue**: Four distinct spatial zones: inside bar (perpendicular only), past bar end (combined distance), width <= 0 guard, parallel_clamped to bar ends. Gaussian falloff with width==0 edge case.
- **Suggested test**: `test_evaluate_on_bar_center` — point at center returns peak_density
- **Suggested test**: `test_evaluate_past_bar_end` — point beyond bar end gets combined distance falloff
- **Suggested test**: `test_evaluate_zero_width` — width=0 returns peak_density for proximal points, 0 otherwise

### game/ui/components/table/header.py (~146 LOC, layer: ui)

#### [ADVISORY] `TableHeader.rebuild` — pygame_gui widget construction
- **Location**: header.py:53-117
- **Issue**: Pure pygame_gui widget construction and layout. ADVISORY — UI rendering code.
- **Note**: `check_presses` method (lines 119-140) has testable button press checking logic but is UI-rendering-dependent.

### game/ui/panels/design_report_panel.py (~200 LOC, layer: ui)

#### [ADVISORY] `DesignReportPanel` — pygame_gui widget layout
- **Location**: design_report_panel.py:24-200
- **Issue**: UI panel construction and layout. ADVISORY for rendering parts.
- **Note**: `update_design` delegates to `DesignStatsPanel` which has separate test coverage. The `_update_portrait` image loading/transformation could benefit from unit testing the image scaling logic.

### game/ui/panels/race_description_panel.py (~418 LOC, layer: ui)

#### [ADVISORY] `RaceDescriptionPanel` — UI widget construction
- **Location**: race_description_panel.py:39-418
- **Issue**: Large UI panel with complex LLM generation widget state machine. ADVISORY for rendering.
- **Note**: Contains significant business logic:
  - `update_char_counts` — text validation (testable)
  - `update_config` — config mutation with MAX_LENGTH truncation (testable)
  - `set_state` / `_apply_field_state` — state machine with 5 FieldStatus branches (should be MAJOR tested)
  - `_tick_field_label` — elapsed time display logic (testable)
- **Upgrade to MAJOR for** `_apply_field_state`: 5 distinct UI states (IDLE, RUNNING, DONE, ERROR, CANCELLED) with widget show/hide/enable/disable and text syncing. This is testable business logic in a UI file.

#### [MAJOR] `RaceDescriptionPanel._apply_field_state` — State machine logic
- **Location**: race_description_panel.py:358-418
- **Issue**: 5-branch state machine with widget visibility, enable/disable, and text sync. Not tested as a unit.
- **Suggested test**: `test_apply_field_state_idle` — verify btn_generate shown/enabled, other buttons hidden
- **Suggested test**: `test_apply_field_state_running` — verify btn_generate disabled, btn_cancel shown, text box disabled
- **Suggested test**: `test_apply_field_state_done` — verify text synced from race_config to text box

### game/ui/panels/race_theme_gallery.py (~191 LOC, layer: ui)

#### [ADVISORY] `RaceThemeGallery` — UI gallery widget
- **Location**: race_theme_gallery.py:26-191
- **Issue**: Gallery panel extending BaseGallery. ADVISORY for rendering.
- **Note**: `_discover_assets` caching logic and theme manager integration are testable but render-dependent.

### game/ui/screens/atmosphere_target_editor.py (~273 LOC, layer: ui)

#### [ADVISORY] `AtmosphereTargetEditor` — UI window for atmosphere editing
- **Location**: atmosphere_target_editor.py:46-273
- **Issue**: Full UI window with sliders. ADVISORY for rendering.
- **Note**: Contains testable business logic:
  - `_set_species_ideal` — gas factor setpoint resolution (should be MAJOR)
  - `_on_apply` — target dict construction from slider values (testable)
  - Gas composition math (ALL_GASES, GAS_DISPLAY mappings)

#### [MAJOR] `AtmosphereTargetEditor._set_species_ideal` — Species preference resolution
- **Location**: atmosphere_target_editor.py:244-260
- **Issue**: Reads species preferences, resolves gas factor setpoints to slider values. PROJ-283 logic.
- **Suggested test**: `test_set_species_ideal_resolves_setpoints` — mock race_config preferences, verify slider values set

### game/ui/screens/builder/modifier_config.py (~99 LOC, layer: ui)

#### [ADVISORY] Configuration data — No logic
- **Location**: modifier_config.py:1-99
- **Issue**: Pure configuration dictionary (MODIFIER_UI_CONFIG and DEFAULT_CONFIG). No functions or methods to test. ADVISORY — data-only file.
- **Note**: These configs drive `modifier_row.py` and `modifier_logic.py` which should be tested.

### game/ui/screens/new_game_setup_ui_builder.py (~41 LOC, layer: ui)

#### [ADVISORY] Thin test seam
- **Location**: new_game_setup_ui_builder.py:25-41
- **Issue**: Thin seam class that delegates to screen._create_ui(). Part of PROJ-328 compositional construction pattern. Only has a build() method that calls screen._create_ui().
- **Note**: This is a DI seam for testing. The null/mock variants in tests/fixtures/ provide test coverage.

### game/ui/screens/planet_abilities_controller.py (~250 LOC, layer: ui)

#### [ADVISORY] UI controller with testable business logic
- **Location**: planet_abilities_controller.py:36-250
- **Issue**: Controller for PlanetAbilitiesWindow (PROJ-329C). Contains:
  - `scan_abilities` — data-driven ability discovery (testable)
  - `_humanize_ability_name` — CamelCase to display name (testable, pure function)
  - `compute_environment_editors` — facility scanning for env abilities (testable)
  - Toggle dispatching to IssuePlanetOrderCommand
- **Note**: Controller follows pattern of not importing pygame. Business logic should be unit-testable.

#### [MAJOR] `PlanetAbilitiesController.scan_abilities` — Data-driven discovery
- **Location**: planet_abilities_controller.py:~80-150
- **Issue**: Core discovery logic scanning facilities for toggleable abilities. Data-driven (no hardcoded type lists per conventions 6.5). Should have unit test coverage.
- **Suggested test**: `test_scan_abilities_discovers_activation_time` — component with activation_time → listed as toggleable
- **Suggested test**: `test_scan_abilities_excludes_no_activation_time` — component without activation_time → excluded

### game/ui/screens/planet_list_filter_manager.py (~148 LOC, layer: ui)

#### [ADVISORY] Filter state management — testable logic
- **Location**: planet_list_filter_manager.py:34-148
- **Issue**: Filter state management with type/owner/range/effects filters. No pygame imports (independently testable per docstring). ADVISORY for UI layer but has concrete, testable filter logic.
- **Note**: `compute_planet_effect_keys`, `apply_filters`, range slider extraction, and effect filtering are testable pure logic operations.

### game/ui/screens/settings_window.py (~109 LOC, layer: ui)

#### [ADVISORY] Settings UI window
- **Location**: settings_window.py:14-109
- **Issue**: Pure UI window with sliders for game settings. ADVISORY for rendering. Reads/writes GameSettings (which has its own tests).
- **Note**: Slider value change handling could benefit from integration tests.

### game/ui/screens/strategy_event_router.py (~506 LOC, layer: ui)

#### [ADVISORY] Event routing for strategy UI
- **Location**: strategy_event_router.py:25-506
- **Issue**: Large event router (~500 LOC) handling pygame_gui events for StrategyUI. ADVISORY for event handling code. Significant file size — could benefit from decomposition but that's a design concern, not coverage.
- **Note**: Contains `has_modal_open`, `handle_ui_button_pressed`, click handling, and window management logic. Complex event routing is inherently hard to unit test.

### game/ui/screens/strategy_ui_action_router.py (~97 LOC, layer: ui)

#### [ADVISORY] UI action routing
- **Location**: strategy_ui_action_router.py:20-97
- **Issue**: Routes zoom/button/cycle actions. Delegates to camera_nav and other UI components. ADVISORY for UI routing.
- **Note**: The if/elif chain dispatch could be tested by mocking camera_nav and verifying correct method is called per action.

### game/ui/screens/strategy_windows/planet_abilities_ctrl.py

#### [ADVISORY] Strategy window controller
- **Note**: Similar to planet_abilities_controller.py. UI window controller with testable logic. ADVISORY for UI layer.

### game/ui/screens/test_lab/details/panel.py

#### [ADVISORY] Test Lab detail panel
- **Note**: Test Lab UI detail rendering. ADVISORY for pygame rendering code. May contain testable formatting/calculation helpers.

### game/ui/screens/workshop_event_router.py

#### [ADVISORY] Workshop event routing
- **Note**: Event routing between workshop UI components (Pattern #10: Event Bus). ADVISORY for UI event handling. The tested EventBus infrastructure provides test coverage for the pub/sub mechanism.

### game/ui/widgets/panel_factory.py

#### [ADVISORY] Panel factory (Pattern #15)
- **Note**: Factory class for creating UI panels. ADVISORY for widget instantiation. May contain fallback/default logic that warrants unit testing for factory correctness.

## Tier 3 — Verified Coverage (no new gaps)

### game/simulation/entities/ship_physics.py (~99 LOC, layer: simulation)
- **Status**: Phase 1 indicated Tier 3 full coverage (4/4 symbols tested). Verified: CONFIRMED — `ShipPhysicsMixin`, `update_physics_movement`, `thrust_forward`, `rotate` all have direct tests in `tests/unit/simulation/entities/test_ship_physics.py` and `tests/unit/systems/test_physics.py`.
- **Minor note**: `rotate` method's `direction` parameter with negative values and boundary rotation (angle %= 360 wrapping) should be verified in tests.

### game/simulation/interfaces/__init__.py (~128 LOC, layer: simulation)
- **Status**: Re-export only (`__init__.py` that re-exports from ability_protocols, component_protocols, entity_protocols, ai_controller). All symbols come from tested sub-modules.
- **Note**: Listed as LOW_PRIORITY / ADVISORY. The sub-modules have extensive test coverage.

### game/strategy/combat/__init__.py (~6 LOC, layer: strategy)
- **Status**: Package docstring only. No callable symbols. ADVISORY / LOW_PRIORITY.

## File Coverage Verification

| File | Layer | Tier | Status | Findings |
|------|-------|------|--------|----------|
| game/ai/target_evaluator.py | ai | 2 | Read ✓ | 7 (6 Major, 1 Minor) |
| game/assets/asset_manager.py | assets | 2 | Read ✓ | 5 (2 Major, 3 Minor) |
| game/core/protocols/ui.py | core | 0 | Read ✓ | 1 (Critical) |
| game/core/registry.py | core | 2 | Read ✓ | 3 (3 Minor) |
| game/simulation/combat/combat_events.py | simulation | 2 | Read ✓ | 2 (2 Minor) |
| game/simulation/entities/ship_physics.py | simulation | 3 | Read ✓ | 0 (Verified) |
| game/simulation/interfaces/__init__.py | simulation | 1 | Read ✓ | 0 (Advisory — re-exports) |
| game/strategy/adapters/simulation_adapter.py | strategy | 2 | Read ✓ | 3 (1 Major, 2 Minor) |
| game/strategy/combat/__init__.py | strategy | 0 | Read ✓ | 0 (Advisory — docstring) |
| game/strategy/combat/post_battle_hook.py | strategy | 2 | Read ✓ | 3 (2 Major, 1 Minor) |
| game/strategy/data/component_activation_state.py | strategy | 2 | Read ✓ | 3 (1 Major, 2 Minor) |
| game/strategy/data/galaxy_spatial_index.py | strategy | 2 | Read ✓ | 2 (1 Major, 1 Minor) |
| game/strategy/data/planet_gen.py | strategy | 0 | Read ✓ | 1 (Critical) |
| game/strategy/engine/atmosphere_engine.py | strategy | 2 | Read ✓ | 2 (2 Major) |
| game/strategy/engine/command_handlers.py | strategy | 1 | Read ✓ | 0 (Advisory — shim) |
| game/strategy/engine/game_session.py | strategy | 2 | Read ✓ | 2 (1 Major, 1 Minor) |
| game/strategy/engine/turn_phase_registry.py | strategy | 2 | Read ✓ | 2 (1 Major, 1 Minor) |
| game/strategy/engine/turn_state_snapshot.py | strategy | 2 | Read ✓ | 2 (1 Major, 1 Minor) |
| game/strategy/events/event_log.py | strategy | 2 | Read ✓ | 3 (2 Major, 1 Minor) |
| game/strategy/facade/dto/fleet_dto.py | strategy | 2 | Read ✓ | 2 (1 Major, 1 Minor) |
| game/strategy/generation/density/primitives/linear.py | strategy | 2 | Read ✓ | 1 (Major) |
| game/ui/components/table/header.py | ui | 2 | Read ✓ | 1 (Advisory) |
| game/ui/panels/design_report_panel.py | ui | 2 | Read ✓ | 1 (Advisory) |
| game/ui/panels/race_description_panel.py | ui | 2 | Read ✓ | 2 (1 Major, 1 Advisory) |
| game/ui/panels/race_theme_gallery.py | ui | 1 | Read ✓ | 1 (Advisory) |
| game/ui/screens/atmosphere_target_editor.py | ui | 2 | Read ✓ | 2 (1 Major, 1 Advisory) |
| game/ui/screens/builder/modifier_config.py | ui | 0 | Read ✓ | 0 (Advisory — config data) |
| game/ui/screens/new_game_setup_ui_builder.py | ui | 0 | Read ✓ | 0 (Advisory — test seam) |
| game/ui/screens/planet_abilities_controller.py | ui | 2 | Read ✓ | 2 (1 Major, 1 Advisory) |
| game/ui/screens/planet_list_filter_manager.py | ui | 2 | Read ✓ | 1 (Advisory) |
| game/ui/screens/settings_window.py | ui | 2 | Read ✓ | 1 (Advisory) |
| game/ui/screens/strategy_event_router.py | ui | 2 | Read ✓ | 1 (Advisory) |
| game/ui/screens/strategy_ui_action_router.py | ui | 2 | Read ✓ | 1 (Advisory) |
| game/ui/screens/strategy_windows/planet_abilities_ctrl.py | ui | 2 | Read ✓ | 1 (Advisory) |
| game/ui/screens/test_lab/details/panel.py | ui | 2 | Read ✓ | 1 (Advisory) |
| game/ui/screens/test_lab/test_executor.py | ui | 0 | Read ✓ | 1 (Advisory) |
| game/ui/screens/workshop_event_router.py | ui | 2 | Read ✓ | 1 (Advisory) |
| game/ui/widgets/panel_factory.py | ui | 0 | Read ✓ | 1 (Advisory) |

## Context Usage Estimate
- Total production LOC read: ~8700
- Total test LOC read: ~1500 (sampled from coverage entries)
- Approximate headroom: Medium (200-500K)
- Partially-read files (if any): None — all 38 files read`
