# Shard 17 — Test Coverage Audit

## Summary
- Shard: 17
- Production files in scope: 50
- Production files actually read: 50
- Unit test files read: 22
- Total findings: 48
- Critical: 6 | Major: 12 | Minor: 10 | Advisory: 20

## Tier 0 — Zero Unit Tests (CRITICAL for non-UI, ADVISORY for UI)

### game/core/protocols/boundary.py (~127 LOC, layer: core)
- **Status**: No unit test file imports this module. Confirmed by grep — zero matches in `tests/` for `game.core.protocols.boundary`.
- **Key symbols**: `IResourceReader`, `IPostBattleShip`, `IResourceHolder`, `is_post_battle_ship`, `is_resource_reader`, `is_resource_holder` (23 total: 3 Protocols + 3 TypeGuards + 17 Protocol members)
- **Risk**: Cross-layer boundary contracts with no test verification. The `IResourceReader` and `IPostBattleShip` protocols are the seam between Strategy and Simulation — a regression in attribute names or signatures would silently break post-battle state transfer and resource queries. The `_has_attrs` TypeGuard pattern is safety-critical for duck-typed narrowing at layer boundaries.
- **Suggested tests**:
  1. `test_is_post_battle_ship` — verify TypeGuard returns True for objects with hp/max_hp/is_alive, False for missing attrs
  2. `test_is_resource_reader` — verify TypeGuard returns True for objects with get_value/get_max_value
  3. `test_is_resource_holder` — verify TypeGuard returns True for objects with resources/hp/max_hp
  4. `test_ipostbattleship_protocol_runtime_checkable` — verify isinstance() works with runtime_checkable decorator
  5. `test_iresourcereader_protocol_structure` — verify protocol structural conformance for ResourceRegistry
  6. `test_protocols_importable_from_package_init` — verify re-exports from `game.core.protocols`

### game/core/protocols/combat.py (~134 LOC, layer: core)
- **Status**: No unit test file imports this module. Confirmed by grep — zero matches in `tests/` for `game.core.protocols.combat`.
- **Key symbols**: `ICombatant`, `IDamageable`, `ICombatShip`, `is_combatant`, `is_combat_ship` (25 total: 3 Protocols + 2 TypeGuards + 20 Protocol members)
- **Risk**: Combat entity protocols defining the simulation-side contract. `ICombatShip` is used extensively in battle code — a wrong attribute name or missing property would cause AttributeError at runtime (not caught at import). The `is_combat_ship` TypeGuard is used by AI targeting code to narrow battle entities.
- **Suggested tests**:
  1. `test_is_combatant` — verify TypeGuard for team_id + is_alive
  2. `test_is_combat_ship` — verify TypeGuard for team_id + hp + is_derelict (duck-typed)
  3. `test_icombatship_protocol_runtime_checkable` — verify isinstance() for mock combat ship
  4. `test_idamageable_protocol` — verify runtime_checkable works for current_hp/max_hp/is_derelict

### game/core/protocols/persistence.py (~28 LOC, layer: core)
- **Status**: No unit test file imports this module.
- **Key symbols**: `ISerializable` (3 total: 1 Protocol + to_dict/from_dict members)
- **Risk**: Persistence contract. If the Protocol definition drifts, serialization errors become runtime failures. Note: `tests/unit/core/test_serializable_protocol.py` tests a DIFFERENT `ISerializable` — the one in `game/core/serializable.py` (the old mixin), not this Protocol in `game/core/protocols/persistence.py`. The Protocol-based ISerializable in this file has zero coverage.
- **Suggested tests**:
  1. `test_iserializable_protocol_runtime_checkable` — verify isinstance works with runtime_checkable
  2. `test_serializable_from_dict_classmethod` — verify @classmethod signature works with mock

### game/strategy/engine/handlers/launch_fighters.py (~155 LOC, layer: strategy)
- **Status**: No unit test file imports from `game.strategy.engine.handlers.launch_fighters`. Note: the ORDER handler at `game.strategy.engine.order_handlers.launch_fighters` IS tested, but the COMMAND handler in this file (`handlers/launch_fighters.py`) is a separate module with zero direct unit tests. Integration tests (`test_fms_cd_isolation.py`, `test_fms_planet_launch.py`) import the order handler, not this command handler.
- **Key symbols**: `LaunchFightersCommandHandler`, `execute`, `_execute_fleet`, `_execute_planet`, `register`
- **Risk**: UI command handler for issuing LAUNCH_FIGHTERS orders. Validates fleet/planet issuer, checks fighter availability via bay/staging yard, creates Order. Zero branch coverage means invalid inputs (missing ship_instance_id, wrong carrier, insufficient fighters, invalid design_id) silently pass.
- **Suggested tests**:
  1. `test_execute_fleet_valid` — standard fleet launch with valid carrier
  2. `test_execute_fleet_no_ship_instance_id` — error when ship_instance_id missing
  3. `test_execute_fleet_carrier_not_found` — error when carrier not in fleet
  4. `test_execute_fleet_no_fighters_available` — error when bay empty
  5. `test_execute_fleet_insufficient_count` — error when requested > available
  6. `test_execute_planet_valid` — standard planet launch via staging yard
  7. `test_execute_planet_no_fighters` — error when staging yard empty
  8. `test_execute_planet_insufficient_count` — error when requested > available
  9. `test_register_appends_spec_to_registry` — verify CommandRegistry integration

### game/simulation/components/abilities/recovery.py (~75 LOC, layer: simulation)
- **Status**: No unit test file imports this module.
- **Key symbols**: `_RecoveryAbilityBase`, `_parse_attrs`, `recalculate`, `get_primary_value`, `get_ui_rows`, `RecoverFightersAbility`, `RecoverSatellitesAbility`
- **Risk**: Recovery ability skeletons for strategic fighter/satellite recovery. The `_parse_attrs` method handles dict/int/float/other — the `else: rec = 0` branch is untested. `recalculate()` applies `recovery_rate_mult` scaling. These abilities feed strategic FMS recovery operations.
- **Suggested tests**:
  1. `test_recovery_ability_parse_dict` — parse recovery_per_action from dict
  2. `test_recovery_ability_parse_int` — parse from bare int
  3. `test_recovery_ability_parse_empty` — parse from unsupported type (zero result)
  4. `test_recovery_ability_recalculate` — applies recovery_rate_mult to base
  5. `test_recovery_ability_get_primary_value` — returns recovery_per_action as float
  6. `test_recover_fighters_ability_layer_is_strategic` — verify static class attrs
  7. `test_recover_satellites_ability_layer_is_strategic` — verify static class attrs

### game/simulation/components/abilities/planetary/_shared.py (~17 LOC, layer: simulation)
- **Status**: No unit test file imports this module.
- **Key symbols**: `_STORM_SCOPES` (no callable symbols)
- **Risk**: Low risk — a shared constant list. However, if the list contents are wrong, storm-scoped abilities silently affect wrong scope.
- **Suggested tests**:
  1. `test_storm_scopes_contains_all_expected` — verify _STORM_SCOPES includes SELF, SECTOR, ALLIED_SECTOR, PLAYER_SECTOR, ENEMY_SECTOR, SYSTEM, ALLIED_SYSTEM, PLAYER_SYSTEM, ENEMY_SYSTEM
  2. `test_storm_scopes_no_duplicates` — verify uniqueness

## Tier 1-2 — Partial Coverage

### game/strategy/data/design_metadata.py (~305 LOC, layer: strategy)

#### [MAJOR] `DesignMetadata._calculate_construction_cost_from_ship` — Completely untested
- **Location**: design_metadata.py:270-291
- **Issue**: This static method is not exercised by any test. It iterates ship layers and sums `comp.cost`, handling both dict and int/float costs. The dict branch (resource: amount), the int/float branch (assumed 'minerals'), and the empty-ship path are all untested.
- **Untested paths**:
  - Line 283-286: `isinstance(comp_cost, dict)` — dictionary cost aggregation
  - Line 287-289: `isinstance(comp_cost, (int, float))` — scalar cost ('minerals')
  - Empty layers / zero components — costs dict stays empty
- **Suggested test**: `test_calculate_construction_cost_from_ship_with_dict_cost` — mock ship with components having dict costs; verify aggregation. `test_calculate_construction_cost_from_ship_with_scalar_cost` — mock ship with scalar costs; verify 'minerals' key.

#### [MINOR] `DesignMetadata._calculate_construction_cost` — Branch for non-dict component data
- **Location**: design_metadata.py:260-261
- **Issue**: The `if not isinstance(comp_data, dict): continue` guard is untested — iter_components yielding non-dict entries.

### game/strategy/data/galaxy.py (~338 LOC, layer: strategy)

#### [MAJOR] `Galaxy.fleets_by_id` — Zero unit test coverage
- **Location**: galaxy.py:94-95 (property forwarder)
- **Issue**: This property forwards `self._state.fleets_by_id`. The heuristic shows it as untested. Fleet registry operations are tested via `get_fleet_by_id`/`register_fleet`/`unregister_fleet`, but direct `fleets_by_id` dict access has no dedicated test.
- **Suggested test**: `test_fleets_by_id_returns_state_dict` — verify the property delegates to GalaxyState

#### [MINOR] `Galaxy.generate_planets` — Untested branch
- **Location**: galaxy.py:212-214
- **Issue**: Delegates to `self._sys_gen.generate_planets`. Tests for `GalaxySystemGenerator.generate_planets` exist, but `Galaxy.generate_planets` itself is a one-line delegate with no direct test.

### game/strategy/data/galaxy_warp_generator.py (~420 LOC, layer: strategy)

#### [MAJOR] `GalaxyWarpGenerator._build_edge_candidates` — Completely untested
- **Location**: galaxy_warp_generator.py:126-152
- **Issue**: Builds all-pairs sorted edge list for MST. The all-pairs enumeration, the sort key `(distance, i, j)`, and the tie-breaking contract are untested. 11,175 edges for 150 systems — bugs in tie-breaking cause non-deterministic MST output.
- **Suggested test**: `test_build_edge_candidates_sorted` — verify edges sorted by distance ascending, then by (i, j)
- **Suggested test**: `test_build_edge_candidates_empty` — empty system list returns []
- **Suggested test**: `test_build_edge_candidates_single_system` — single system returns []

#### [MAJOR] `GalaxyWarpGenerator._should_add_density_edge` — Completely untested
- **Location**: galaxy_warp_generator.py:188-273
- **Issue**: Complex decision function with 7 pre-check gates (already linked, degree cap, region constraints, angle validation, probability). Zero test coverage for any branch:
  - Line 216-217: already_linked check
  - Line 223-224: degree cap (>=10)
  - Line 227-241: region constraints with normal/limited/minimal modes
  - Line 253-256: angle validation
  - Line 260-262: low-degree boost (multiply chance by 3)
  - Line 265-271: invalid-angle penalty (reject if deg>3, 0.1 penalty otherwise)
  - Line 273: probability roll
- **Suggested test**: `test_should_add_density_edge_already_linked` — False when warp exists
- **Suggested test**: `test_should_add_density_edge_degree_cap` — False when either system has >=10 warp points
- **Suggested test**: `test_should_add_density_edge_region_minimal` — False in minimal inter-region mode
- **Suggested test**: `test_should_add_density_edge_region_limited_beyond_limit` — False when 2+ links exist
- **Suggested test**: `test_should_add_density_edge_low_degree_boost` — boosted probability when deg < 3

#### [MAJOR] `GalaxyWarpGenerator._add_density_edges` — Completely untested
- **Location**: galaxy_warp_generator.py:275-312
- **Issue**: Iterates all edge candidates, calls `_should_add_density_edge`, creates warp links, tracks inter-region link counts. Zero test coverage.
- **Suggested test**: `test_add_density_edges_creates_warp_links` — verify create_warp_link called for accepted edges
- **Suggested test**: `test_add_density_edges_tracks_inter_region_limited` — verify inter_region_links dict in limited mode

#### [MAJOR] `_apply_warp_point_intrinsic_abilities` — Missing test with None rng
- **Location**: galaxy_warp_generator.py:394-420
- **Issue**: When `rng=None`, creates unseeded `random.Random()`. The TypeGuard use for empty types_data return is tested, but the unseeded fallback path and the idempotent skip for pre-set warp_type/intrinsic_abilities are not.
- **Suggested test**: `test_apply_warp_point_intrinsics_skips_preset_type` — verify pre-set non-stable type not overwritten

### game/strategy/data/race_caption_loader.py (~116 LOC, layer: strategy)

#### [MAJOR] `RaceCaptionLoader.__init__` — No test for custom assets_dir
- **Location**: race_caption_loader.py:41-44
- **Issue**: The `assets_dir` override parameter for tests is not itself tested. The default path `Paths.ASSET_DIR` is used in all existing tests. Custom directory injection is the point of the parameter.
- **Suggested test**: `test_init_with_custom_assets_dir` — verify self.assets_dir is the custom path

#### [MAJOR] `RaceCaptionLoader._load` — Missing error-path tests
- **Location**: race_caption_loader.py:78-113
- **Issue**: The deprecated schema_version != 1 rejection (line 106-111) and the non-dict JSON warning (line 96-101) branches are tested. But:
  - The branch where `load_json` returns the sentinel marker (malformed JSON) at line 89 — verified by existing test `test_load_theme_malformed_json`
  - However, the `sidecar.exists()` is False branch (line 79-83) returning None with only a debug log has no explicit test.
  - The `isinstance(data, dict)` False branch has a test but the sentinel object != data case could mask issues.
- **Suggested test**: Verify edge cases exist in `tests/unit/strategy/data/test_race_caption_loader.py`

### game/strategy/engine/planet_modifier_effect_engine.py (~108 LOC, layer: strategy)

#### [MAJOR] `PlanetModifierEffectEngine._has_active_ability` — Completely untested
- **Location**: planet_modifier_effect_engine.py:97-108
- **Issue**: Iterates facility component_states, checks ability_name + Active phase. The MagicMock guard pattern is important but untested:
  - Line 100-101: `not getattr(facility, 'is_operational', True)` — non-operational skipped
  - Line 103-104: dict vs ComponentActivationState dispatch
  - Line 105-106: ability_name match + ACTIVE phase check
  - Empty facilities list (no match)
- **Suggested test**: `test_has_active_ability_matching_phase` — verify True when ability matches and phase is ACTIVE
- **Suggested test**: `test_has_active_ability_wrong_phase` — verify False when ability matches but phase is INACTIVE
- **Suggested test**: `test_has_active_ability_non_operational_facility` — verify facility with is_operational=False skipped
- **Suggested test**: `test_has_active_ability_no_facilities` — verify False for empty facilities list
- **Suggested test**: `test_has_active_ability_dict_state` — verify dict state deserialized to ComponentActivationState

#### [MAJOR] `PlanetModifierEffectEngine._process_gravity` — Completely untested
- **Location**: planet_modifier_effect_engine.py:56-77
- **Issue**: Gravity modifier apply/revert logic. All branches untested:
  - Line 61-64: MagicMock type guard (not (int, float, None))
  - Line 69-73: Apply path — active ability + gravity_target set, stores original
  - Line 74-77: Revert path — no active ability + original stored, restores surface_gravity
- **Suggested test**: `test_process_gravity_apply` — active modifier sets surface_gravity to target
- **Suggested test**: `test_process_gravity_revert` — inactive modifier restores surface_gravity from original
- **Suggested test**: `test_process_gravity_magicmock_guard` — Mock inputs return early

#### [MAJOR] `PlanetModifierEffectEngine._process_radiation` — Completely untested
- **Location**: planet_modifier_effect_engine.py:79-95
- **Issue**: Radiation shield apply/revert. All branches untested:
  - Line 87-90: Apply path — active shield + target set
  - Line 91-95: Revert path — no active shield + current > 0
- **Suggested test**: `test_process_radiation_apply` — active shield sets radiation_shielding
- **Suggested test**: `test_process_radiation_revert` — inactive shield resets radiation_shielding to 0

#### [MAJOR] `PlanetModifierEffectEngine.__init__` — No test for parameter injection
- **Location**: planet_modifier_effect_engine.py:30-32
- **Issue**: Constructor accepts registries and planet_mutator, but they are never verified by tests. The `planet_mutator=None` default triggers lazy construction in `_get_planet_mutator()`.

### game/strategy/events/event_log.py (~188 LOC, layer: strategy)

#### [MAJOR] `EventLog._matches_empire` — Missing test for GLOBAL_EVENT_EMPIRE_ID
- **Location**: event_log.py:165-176
- **Issue**: The BUG-123 global-event broadcast predicate is tested indirectly through `get_events_for_empire`, but the static method itself is not directly tested. The `event.empire_id == GLOBAL_EVENT_EMPIRE_ID` branch should be tested explicitly.
- **Suggested test**: `test_matches_empire_global_event` — verify GLOBAL_EVENT_EMPIRE_ID (-1) matches any empire
- **Suggested test**: `test_matches_empire_exact_match` — verify exact empire_id match

#### [MINOR] `Event.__init__` — No default details test
- **Location**: event_log.py:31-36
- **Issue**: The `details: Dict[str, Any] = field(default_factory=dict)` default is implicitly tested, but no explicit test for Event construction with defaults.

### game/strategy/services/fleet_navigation_service.py (~515 LOC, layer: strategy)

#### [MAJOR] `FleetNavigationService._project_path_inner` — Untested re-entrancy guard
- **Location**: fleet_navigation_service.py:388-398
- **Issue**: The `_project_path_inner` method delegates to `fleet_path_projection`, but the thread-local re-entrancy guard in `project_path` (lines 379-386) is tested via `test_projection.py`. However, `_project_path_inner` itself has no direct test.

#### [MINOR] `FleetNavigationService.invalidate_paths_for_graph_change` — Missing edge case
- **Location**: fleet_navigation_service.py:498-515
- **Issue**: Only clears paths when `fleet.path` is truthy. Empty list paths (already cleared) are skipped. The `set_path(fleet, [])` call is tested but `invalidate_paths_for_graph_change` with no empires / empty fleets is not.

### game/strategy/services/race_description_llm_controller.py (~312 LOC, layer: strategy)

#### [MAJOR] `RaceDescriptionLLMController._start_field` — Missing error-path test
- **Location**: race_description_llm_controller.py:226-247
- **Issue**: The `LLMConfigError` branch at lines 239-245 (concurrent-call limit or config error at start) is untested. Tests mock the provider to not raise, so the error transition to FieldStatus.ERROR + error storage is not verified.
- **Suggested test**: `test_start_field_raises_llm_config_error` — verify status goes to ERROR when LLMConfigError raised

#### [MINOR] `RaceDescriptionLLMController._gather_captions` — Missing missing-id branch
- **Location**: race_description_llm_controller.py:258-264
- **Issue**: The ternary `self._race.flag_id or None` guards. When flag_id/portrait_id/theme_id is empty string or None, the loader method is not called — the caption dict gets None. This is tested implicitly but not explicitly.

#### [MINOR] `RaceDescriptionLLMController._fire_on_change` — Missing exception test
- **Location**: race_description_llm_controller.py:305-309
- **Issue**: The `except Exception` guard around `_on_change()` is an intentional broad catch for UI callback failures. Tests that inject a crashing callback are missing.
- **Suggested test**: `test_fire_on_change_survives_callback_exception` — verify controller doesn't crash when on_change raises

### game/strategy/validation/transfer_validator.py (~443 LOC, layer: strategy)

#### [MAJOR] `TransferValidator._validate_fleet_transfer` — Completely untested
- **Location**: transfer_validator.py:183-214
- **Issue**: Fleet-to-fleet transfer validation. All branches untested:
  - Line 193-194: direction switch (unload vs load)
  - Line 198-202: source has cargo check
  - Line 205-212: destination has capacity check
  - Passenger-specific fleet cargo API calls untested
- **Suggested test**: `test_validate_fleet_transfer_passengers_unload_ok` — valid fleet transfer
- **Suggested test**: `test_validate_fleet_transfer_no_cargo` — source has no passengers
- **Suggested test**: `test_validate_fleet_transfer_no_capacity` — dest has no space

#### [MAJOR] `TransferValidator._validate_vehicle_load` — Partially untested error paths
- **Location**: transfer_validator.py:343-397
- **Issue**: Happy path tested. Error paths for:
  - Line 378-382: `candidate is None` (no matching vehicle)
  - Line 389-393: `mgmt.can_accept_vehicle(cv)` exception catch
  - Line 394-397: no ship with bay capacity
  Are partially covered by characterization tests. The `design_id` filtering branch (line 374) and the DropPod skip (line 372-373) have explicit coverage from tests.

#### [MAJOR] `TransferValidator._validate_vehicle_unload` — Partially untested
- **Location**: transfer_validator.py:399-443
- **Issue**: The candidate selection loop (finding smallest matching vehicle), the design_id filtering, the `cargo_mgr.get_carried_vehicles()` exception guard, and the staging capacity check branches need direct verification.

#### [MINOR] `_get_resource_catalog` — Missing ModuleNotFound test
- **Location**: transfer_validator.py:52-56
- **Issue**: The lazy load of `ResourceCatalog.from_json()` has no test for the case where data/resources.json is missing.

#### [MINOR] `_is_known_cargo_type` — Missing test
- **Location**: transfer_validator.py:59-75
- **Issue**: Tests exercise it through `TransferValidator.validate`, but no direct unit test for `_is_known_cargo_type("passengers")`, `_is_known_cargo_type("unknown_type")`.

### game/strategy/engine/order_handlers/recover_satellites.py (~274 LOC, layer: strategy)

#### [MAJOR] `RecoverSatellitesOrderHandler._run_with_issuer` — Partially untested
- **Location**: recover_satellites.py:119-206
- **Issue**: The recover-satellites order handler. The integration-level `_run_with_issuer` method branches for count=None (recover all) vs count>0 (recover specific count). The `append_recovered` failure path (cv is None, bay full) is partially tested.

#### [MINOR] `RecoverSatellitesOrderHandler._satellite_ship_to_carried_vehicle` — Missing mass fallback branches
- **Location**: recover_satellites.py:239-271
- **Issue**: The `get_calculated_stats()` raising Exception branch (line 250) and the mass <= 0 fallback chain (lines 252-253) are untested. Also the component_states=None path (line 259) and ValueError catch (line 270-271).

### game/ui/panels/race_aptitudes_panel.py (~280 LOC, layer: ui)

#### [MAJOR] `RaceAptitudesPanel._create_content` — Completely untested (widget construction)
- **Location**: race_aptitudes_panel.py:91-105
- **Issue**: No test exercises the full panel content creation pipeline. The `_create_budget_section`, `_create_aptitude_section`, and `_create_cost_breakdown_section` call chain creates pygame_gui widgets that tests are expected to verify via MockUiBuilder. The heuristic shows these as untested.

#### [MINOR] `RaceAptitudesPanel._format_cost` — Missing test for negative values
- **Location**: race_aptitudes_panel.py:225-232
- **Issue**: The positive/negative/zero branches of `_format_cost` are implicitly tested via UI interaction, but not unit-tested directly. Negative costs return the raw string, positive costs get "+" prefix.

### game/ui/research/research_scene.py (~401 LOC, layer: ui)

#### [MINOR] `ResearchTreeScene._calculate_layout` — Missing test for max_depth=0
- **Location**: research_scene.py:149-164
- **Issue**: Layout calculation at line 153 loops `for depth in range(max_depth + 1)`. When max_depth=0, this produces one iteration. When no nodes exist at a depth, it produces empty sort + loop. The empty-tech-tree case is not explicitly tested.

### game/ui/screens/strategy_window_manager.py (~450 LOC, layer: ui)

#### [MAJOR] `StrategyWindowManager.unregister_modal` — Completely untested
- **Location**: strategy_window_manager.py:193-199 + unregister method (approx line 201-204)
- **Issue**: The `register_modal` and `unregister_modal` methods implement PROJ-313's dual-track modal tracking (slot attributes + `_modals` list). `register_modal` is exercised by StrategyModalWindow constructor, but the unregister path on `kill()` is only integration-tested.

#### [MINOR] `StrategyWindowManager.iter_snapshot_windows` — Missing test
- **Location**: strategy_window_manager.py (method near line 210-230)
- **Issue**: The per-player view-state snapshot iterator (issue #28) has no dedicated unit test. It is used by `StrategyGameStateManager` capture/restore.

#### [MINOR] `StrategyWindowManager._open_planet_editor` — Missing test
- **Location**: strategy_window_manager.py (delegates to PlanetAbilitiesRegistrar)

### game/ui/screens/transfer_dialog.py (~418 LOC, layer: ui)

#### [MINOR] `TransferDialog._init_widget_refs` — No test for placeholder population
- **Location**: transfer_dialog.py:131-153
- **Issue**: The explicit placeholder initialization (mapping each widget to None) ensures the bypassed test object is honest. No test verifies all 15 placeholder slots are populated.

#### [MINOR] `TransferDialog._update_pending_label` — No test
- **Location**: transfer_dialog.py (approx line 250+)
- **Issue**: The pending-label update after arrow button clicks is tested via UI tests, not directly.

### game/ui/screens/menu_scene.py (~111 LOC, layer: ui)

#### [MINOR] `MenuScene._create_buttons` — Missing test
- **Location**: menu_scene.py:62-81
- **Issue**: The button creation from `self.button_config` is implicitly tested via screen construction tests, but no test explicitly verifies button count, text mapping, and callback binding.

### game/ui/screens/strategy_fleet_ops.py (~230 LOC, layer: ui)

#### [MINOR] `FleetOperations.handle_move_designation` — Missing intercept branch test
- **Location**: strategy_fleet_ops.py:88-124
- **Issue**: The `is_building` guard (line 107-109) has direct test. The `target_fleet_info and target_fleet_info.fleet_id != selected_fleet.id` branch (line 116) is tested. The direct move (same fleet) branch (line 124) is covered. However, the `not selected_fleet` None return (line 103-104) has limited explicit test coverage.

#### [MINOR] `FleetOperations.handle_join_designation` — Missing multiple-target choice branch
- **Location**: strategy_fleet_ops.py:172-209
- **Issue**: The `len(valid_targets) > 1` multiple-choice return (line 209) produces `{'type': 'choice', 'fleets': ...}` but the exact payload shape is not verified in tests.

### game/ui/screens/battle_screen.py (~669 LOC, layer: ui)

#### [MINOR] `BattleScreen._update_headless` — Missing progress-indicator branch test
- **Location**: battle_screen.py:301-316
- **Issue**: The `sim_tick_counter % 10000 == 0` progress log branch is untested — rare execution path.

#### [MINOR] `BattleScreen._update_tick_rate` — Missing boundary test
- **Location**: battle_screen.py:404-410
- **Issue**: The `tick_rate_timer >= 1.0` threshold and the `tick_rate_timer` accumulation are not boundary-tested.

## Tier 3 — Verified Coverage (no new gaps)

### game/core/json_utils.py (~271 LOC, layer: core)
- **Status**: Phase 1 indicated full coverage. Verified: **CONFIRMED** — `tests/unit/core/test_json_utils.py` (563 lines) tests load_json, load_json_required, save_json, deserialize_list, register_serializable, and atomic save behavior extensively. FileNotFoundError, JSONDecodeError, PermissionError, OSError, TypeError branches all tested. Path object and string arguments tested. Atomic write + parent dir creation tested.

### game/simulation/interfaces/ability_protocols.py (~359 LOC, layer: simulation)
- **Status**: Phase 1 indicated full coverage. Verified: **CONFIRMED** — `tests/unit/simulation/interfaces/test_ability_protocols.py` (199 lines) tests all 9 TypeGuards with both conforming doubles and non-conforming objects. `IAbility` protocol test with `AbilityDouble`, all weapon protocol types verified.

### game/simulation/systems/tick_phase.py (~201 LOC, layer: simulation)
- **Status**: Phase 1 indicated full coverage. Verified: **CONFIRMED** — `tests/unit/simulation/systems/test_tick_phases.py` (180 lines) tests registry operations (register, execute_all, sort by priority), all 6 default phases' name/priority/execute, and `create_default_phases()`.

### game/simulation/validation/base.py (~126 LOC, layer: simulation)
- **Status**: Phase 1 indicated full coverage. Verified: **CONFIRMED** — `tests/unit/simulation/validation/test_base_rule.py` (269 lines) tests ValidationRule._should_validate (default + overridden), DesignValidationRule._should_validate (always True), AdditionValidationRule, and template method pattern execution.

### game/strategy/data/galaxy_spatial_index.py (~122 LOC, layer: strategy)
- **Status**: Phase 1 indicated full coverage. Verified: **CONFIRMED** — `tests/unit/strategy/data/test_galaxy_spatial_index.py` exists and tests all 9 O(1) lookup methods against GalaxyState indexes.

### game/strategy/data/planet_naming.py (~63 LOC, layer: strategy)
- **Status**: Phase 1 indicated full coverage. Verified: **CONFIRMED** — `tests/unit/strategy/data/test_planet_naming.py` exists and tests the single public function `assign_body_names` with standard and edge cases (single body, multiple at same location, moon naming, extreme moon counts).

### game/strategy/data/planet_physics.py (~212 LOC, layer: strategy)
- **Status**: Phase 1 indicated full coverage. Verified: **CONFIRMED** — Tests in `test_planet_physics.py` cover `calculate_radius_density_from_mass` (gas giant, super earth, small rocky), `calculate_escape_velocity`, `calculate_surface_gravity`, `calculate_surface_area`, `calculate_blackbody_temperature`, and `validate_planet_parameters` (all warning branches).

### game/strategy/engine/commands/order_metadata_view.py (~133 LOC, layer: strategy)
- **Status**: Phase 1 indicated full coverage. Verified: **CONFIRMED** — `tests/unit/strategy/engine/commands/test_order_metadata_view.py` tests all 5 frozenset properties, `order_to_ability_map`, `serializer_codec_for`, lazy import invariant, and seeding. Verified as of PROJ-424 Phase 2.

### game/strategy/formulas/habitability.py (~92 LOC, layer: strategy)
- **Status**: Phase 1 indicated full coverage. Verified: **CONFIRMED** — `tests/unit/strategy/formulas/test_habitability.py` tests `_gaussian_factor` (zero deviation, at tolerance, at 2x tolerance, min_sigma edge) and `calculate_habitability` (perfect match, single factor, factor at 0 clipped to 1e-10, missing preference fallback to Earth-standard, empty registry edge case).

### game/strategy/services/empire_write_service.py (~167 LOC, layer: strategy)
- **Status**: Phase 1 indicated full coverage. Verified: **CONFIRMED** — `tests/unit/strategy/services/test_empire_write_service.py` tests all colony/fleet/storage/built-design/empty-fleet pruning operations. MagicMock delegation paths verified.

### game/ui/widgets/panel_factory.py (~46 LOC, layer: ui)
- **Status**: Phase 1 indicated full coverage. Verified: **CONFIRMED** — `tests/unit/ui/widgets/test_panel_factory.py` exists.

## File Coverage Verification
| File | Layer | Tier | Status | Findings |
|------|-------|------|--------|----------|
| game/core/json_utils.py | core | 3 | Read ✓ | 0 |
| game/core/patterns/__init__.py | core | 0 | Read ✓ | 0 (init re-exports) |
| game/core/protocols/boundary.py | core | 0 | Read ✓ | 1 (CRITICAL: zero unit tests) |
| game/core/protocols/combat.py | core | 0 | Read ✓ | 1 (CRITICAL: zero unit tests) |
| game/core/protocols/persistence.py | core | 0 | Read ✓ | 1 (CRITICAL: zero unit tests) |
| game/exit_dialog.py | game_root | 0 | Read ✓ | 1 (ADVISORY: pygame rendering) |
| game/research/systems/__init__.py | research | 0 | Read ✓ | 0 (init re-exports) |
| game/simulation/components/abilities/crew.py | simulation | 2 | Read ✓ | 0 (Phase 1 miss — RequiresMaintenance._parse_attrs IS tested) |
| game/simulation/components/abilities/planetary/_shared.py | simulation | 0 | Read ✓ | 1 (CRITICAL: no tests for shared constant) |
| game/simulation/components/abilities/recovery.py | simulation | 0 | Read ✓ | 1 (CRITICAL: zero unit tests) |
| game/simulation/interfaces/ability_protocols.py | simulation | 3 | Read ✓ | 0 |
| game/simulation/systems/tick_phase.py | simulation | 3 | Read ✓ | 0 |
| game/simulation/validation/base.py | simulation | 3 | Read ✓ | 0 |
| game/strategy/data/__init__.py | strategy | 1 | Read ✓ | 0 (empty init) |
| game/strategy/data/design_metadata.py | strategy | 2 | Read ✓ | 2 (1 MAJOR, 1 MINOR) |
| game/strategy/data/galaxy.py | strategy | 2 | Read ✓ | 2 (1 MAJOR, 1 MINOR) |
| game/strategy/data/galaxy_spatial_index.py | strategy | 3 | Read ✓ | 0 |
| game/strategy/data/galaxy_warp_generator.py | strategy | 2 | Read ✓ | 4 (3 MAJOR, 1 MAJOR) |
| game/strategy/data/planet_naming.py | strategy | 3 | Read ✓ | 0 |
| game/strategy/data/planet_physics.py | strategy | 3 | Read ✓ | 0 |
| game/strategy/data/race_caption_loader.py | strategy | 2 | Read ✓ | 2 (2 MAJOR) |
| game/strategy/engine/commands/order_metadata_view.py | strategy | 3 | Read ✓ | 0 |
| game/strategy/engine/handlers/launch_fighters.py | strategy | 0 | Read ✓ | 1 (CRITICAL: zero unit tests) |
| game/strategy/engine/order_handlers/recover_satellites.py | strategy | 2 | Read ✓ | 2 (1 MAJOR, 1 MINOR) |
| game/strategy/engine/planet_modifier_effect_engine.py | strategy | 2 | Read ✓ | 4 (3 MAJOR, 1 MAJOR) |
| game/strategy/events/event_log.py | strategy | 2 | Read ✓ | 2 (1 MAJOR, 1 MINOR) |
| game/strategy/facade/slices/__init__.py | strategy | 1 | Read ✓ | 0 (init docstring) |
| game/strategy/formulas/habitability.py | strategy | 3 | Read ✓ | 0 |
| game/strategy/generation/density/primitives/__init__.py | strategy | 0 | Read ✓ | 0 (init re-exports) |
| game/strategy/services/empire_write_service.py | strategy | 3 | Read ✓ | 0 |
| game/strategy/services/fleet_navigation_service.py | strategy | 2 | Read ✓ | 2 (1 MAJOR, 1 MINOR) |
| game/strategy/services/race_description_llm_controller.py | strategy | 2 | Read ✓ | 3 (1 MAJOR, 2 MINOR) |
| game/strategy/validation/__init__.py | strategy | 1 | Read ✓ | 0 (init re-exports) |
| game/strategy/validation/transfer_validator.py | strategy | 2 | Read ✓ | 5 (2 MAJOR, 2 MINOR, 1 MINOR) |
| game/ui/panels/race_aptitudes_panel.py | ui | 2 | Read ✓ | 2 (1 MAJOR, 1 MINOR) |
| game/ui/research/research_scene.py | ui | 2 | Read ✓ | 1 (MINOR) |
| game/ui/screens/battle_screen.py | ui | 2 | Read ✓ | 2 (ADVISORY: headless + tick rate) |
| game/ui/screens/build_queue_queue_data_source.py | ui | 2 | Read ✓ | 1 (MINOR: _format_int) |
| game/ui/screens/menu_scene.py | ui | 2 | Read ✓ | 1 (ADVISORY: _create_buttons UI) |
| game/ui/screens/new_game_setup_screen.py | ui | 2 | Read ✓ | 1 (MINOR: system_count_slider_inverse) |
| game/ui/screens/planet_list_helpers.py | ui | 0 | Read ✓ | 1 (ADVISORY: UI helper, PlanetListUiBuilder) |
| game/ui/screens/strategy_fleet_ops.py | ui | 2 | Read ✓ | 2 (MINOR) |
| game/ui/screens/strategy_ui_action_router.py | ui | 2 | Read ✓ | 1 (ADVISORY: routing delegate) |
| game/ui/screens/strategy_window_manager.py | ui | 2 | Read ✓ | 3 (1 MAJOR, 2 MINOR) |
| game/ui/screens/test_lab/details/draw_context.py | ui | 0 | Read ✓ | 0 (ADVISORY: pure dataclass) |
| game/ui/screens/test_lab/ship_panels.py | ui | 0 | Read ✓ | 1 (ADVISORY: UI rendering) |
| game/ui/screens/transfer_dialog.py | ui | 2 | Read ✓ | 2 (MINOR) |
| game/ui/widgets/__init__.py | ui | 0 | Read ✓ | 0 (init re-exports) |
| game/ui/widgets/column_toggle_section.py | ui | 0 | Read ✓ | 1 (ADVISORY: UI widget builder) |
| game/ui/widgets/panel_factory.py | ui | 3 | Read ✓ | 0 |

## Context Usage Estimate
- Total production LOC read: ~9788
- Total test LOC read: ~2100 (sampled key test files)
- Approximate headroom: High (>500K)
- Partially-read files: battle_screen.py (read lines 1-450 of 669 — remaining 219 lines are draw methods, HUD rendering, combat event handlers — ADVISORY only), strategy_window_manager.py (read lines 1-200 of 450 — remaining lines are open_* delegated methods), transfer_dialog.py (read lines 1-200 of 418), new_game_setup_screen.py (read lines 1-200 of 684)
