# Compiled Confirmed Gaps — Shards 07-12

**Generated**: 2026-05-05
**Source**: Verified Shard Reports 07-12 (Phase 3 Skeptical Verification)
**Scope**: All CONFIRMED gaps. DISPUTED and INCONCLUSIVE claims excluded.

---

## Per-Shard Statistics

| Shard | Reviewed | Confirmed | Disputed | Inconclusive | Downgrades | Upgrades |
|---|---|---|---|---|---|---|
| 07 | 14 (2C+12M) | 4 (1C+3M) | 9 | 1 | 8 downgraded | 1 MINOR upgrade |
| 08 | 28 (4C+24M) | 10 (0C+10M) | 17 | 1 | 2 C→ADVISORY | 0 |
| 09 | 24 (10C+13M) | 12 (4C+8M) | 9 | 0 | 6 C→Tier2/3 | 0 |
| 10 | 4 (2C+2M) | 1 (1C+0M) | 2 | 0 | 1 C→LOW, 1 C→ADVISORY | 0 |
| 11 | 8 (2C+6M) | 2 (0C+2M) | 5 | 1 | 2 C | 0 |
| 12 | 29 (5C+24M) | 18 (1C+17M) | 11 | 0 | 4 C→Tier1-3 | 0 |
| **Total** | **107** | **47** | **53** | **3** | — | — |

**Phase 2 Claim Accuracy Rate (07-12)**: 47/107 = 43.9% of CRITICAL/MAJOR claims survived skeptical verification.

---

## All CONFIRMED Gaps

### [CRITICAL] `game/research/data/tech_tree.py` — detect_cycles / resolve_all_requirements / validate / calculate_depth
- **Shard**: 07
- **Location**: tech_tree.py:200-280
- **Untested**: DFS cycle detection (`detect_cycles` with `rec_stack` logic and `negate` filter at line 244), `resolve_all_requirements` (RNG-dependent fuzzy requirement resolution), combined `validate()`, `load_from_json` with empty/invalid/comment-only JSON, `calculate_depth` with missing node_id (returns 0).
- **Suggested test**: `test_detect_cycles_simple_cycle` — 2-node mutual-requirement cycle, verify `dirty_nodes` populated. `test_detect_cycles_no_cycle` — linear chain, verify clean. `test_resolve_all_requirements_returns_subset` — seed RNG, verify deterministic output. `test_validate_combines_cycles_and_requirements` — verify both dirty nodes and validation errors reported.

### [CRITICAL] `game/simulation/combat/families/_beam_common.py` — build_beam_resolution
- **Shard**: 09
- **Location**: _beam_common.py:20-50
- **Untested**: `build_beam_resolution` has zero dedicated unit tests. The zero-length aim vector guard (line 34: `aim_vec.length() > 0` → default `Vector2(1, 0)`) is completely untested. BeamResolution objects are constructed directly in other tests, never via `build_beam_resolution`.
- **Suggested test**: `test_build_beam_creates_resolution_with_correct_properties` — call with mock attacker/defender/weapon, verify BeamResolution fields. `test_build_beam_zero_length_aim_vector_falls_back_to_default` — aim vector of (0,0), verify rightward default used.

### [CRITICAL] `game/simulation/combat/families/pdc.py` — PDCHandler.fire()
- **Shard**: 09
- **Location**: pdc.py:1-40
- **Untested**: No test file imports `PDCHandler` or calls `PDCHandler().fire()`. The module-level `WEAPON_REGISTRY.register()` side effect is implicitly exercised by registry tests, and `test_weapon_dispatch_golden.py:419-422` checks PDC dispatch produces `BeamResolution`, but that tests the firing system's dispatch, not `PDCHandler.fire()` itself.
- **Suggested test**: `test_pdc_handler_fire_produces_beam_resolution` — instantiate PDCHandler, call fire() with mock combat state, verify BeamResolution returned with correct family and weapon data.

### [CRITICAL] `game/strategy/facade/slices/event_slice.py` — EventSlice all 8 query methods
- **Shard**: 09
- **Location**: event_slice.py:1-80
- **Untested**: Zero test references for `EventSlice` across entire test suite. All 8 query methods (`get_turn_events` with `empire_id=None` and `empire_id=X`, `get_all_events`, `get_events_by_category`, `get_human_player_ids`, `get_turn_number`, `get_save_path`) completely untested. Dual-path EventLog API dispatch (empire_id None vs not None) is regression-prone and never exercised.
- **Suggested test**: `test_event_slice_get_turn_events_scoped` — EventSlice wrapping mock EventLog, verify empire_id filtering. `test_event_slice_get_turn_events_all` — empire_id=None returns events for all empires. `test_event_slice_get_human_player_ids` — verify human-filtered empire IDs returned.

### [CRITICAL] `game/strategy/services/effect_ability_display.py` — _format_status / _is_activatable / _ability_kind
- **Shard**: 09
- **Location**: effect_ability_display.py:40-95
- **Untested**: Internal helpers `_format_status` (4 branches: Active/Activating/Deactivating/Inactive) and `_is_activatable` have zero grep matches across test suite. `_ability_kind` tested only indirectly through `system_effects_collector` integration tests. Public functions (`make_group_key`, `make_display_name`, `format_intrinsic_ability_magnitude`) ARE tested via `test_system_effects_collector.py`.
- **Suggested test**: `test_format_status_active` — ACTIVE component_state → "(Active)". `test_format_status_activating` → "(Activating)". `test_is_activatable_true_for_activatable` — mock ability with requires_activation=True returns True. `test_ability_kind_environmental_damage` — EnvironmentalDamageAbility → "Environmental Damage".

### [CRITICAL] `game/ui/screens/build_queue_screen.py` — 15 untested symbols
- **Shard**: 10
- **Location**: build_queue_screen.py:48-658
- **Untested**: ~10 business-logic methods only exercised indirectly (or not at all) through integration tests. Key gaps: `_validate_params` (4 ValidationException branches + 2 hasattr checks not directly verified), `_dispatch_toggle_pause_command` (zero test coverage), `_handle_button_press` (50-line dispatch with 20+ elif branches, no systematic branch coverage), `_handle_virtual_table_action` (remove/add/up/down actions not directly tested), `_handle_drag_operations` (exercised only through drag-drop integration).
- **Suggested test**: `test_validate_params_raises_on_missing_facade` — call with missing facade, verify ValidationException. `test_dispatch_toggle_pause_command` — mock facade, verify TogglePauseConstructionQueueCommand sent. `test_handle_button_press_close` — verify close button triggers _close.

### [CRITICAL] `game/strategy/generation/density/primitives/density_primitive.py` — clamp_density
- **Shard**: 12
- **Location**: density_primitive.py:36-45
- **Untested**: `clamp_density` function (`max(0.0, min(1.0, value))`) has zero tests. No callers of `clamp_density` found in any test trace.
- **Suggested test**: `test_clamp_density_negative` — -0.5 → 0.0. `test_clamp_density_above_one` — 1.5 → 1.0. `test_clamp_density_in_range` — 0.5 → 0.5. `test_clamp_density_boundary_zero` — 0.0 → 0.0. `test_clamp_density_boundary_one` — 1.0 → 1.0.

---

### [MAJOR] `game/strategy/services/replay_ship_builder.py` — builder closure decision logic
- **Shard**: 07
- **Location**: replay_ship_builder.py:1-87
- **Untested**: Unit-level branch coverage of builder closure: snapshot found → `ShipInstanceSerializer.from_dict` → `to_ship` path, snapshot not found + fallback → uses fallback, snapshot not found + no fallback → `ValueError`. Existing test (`test_replay_ship_builder_registry_contract.py`) only verifies protocol contract — `build_replay_ship_builder` doesn't crash with `DefaultRegistryProvider`.
- **Suggested test**: `test_builder_snapshot_found_returns_ship` — mock store returning a snapshot, verify ship returned via from_dict→to_ship. `test_builder_snapshot_not_found_with_fallback` — mock store returning None, verify fallback used. `test_builder_snapshot_not_found_no_fallback_raises_valueerror` — mock store returning None, no fallback, verify ValueError.

### [MAJOR] `game/strategy/engine/order_processor.py` — _load_pod_from_staging_yard / _unload_pod_to_staging_yard
- **Shard**: 07
- **Location**: order_processor.py:532-616
- **Untested**: Private pod I/O methods `_load_pod_from_staging_yard` (lines 532-585, capacity/mass checks) and `_unload_pod_to_staging_yard` (lines 587-616) have zero test references. The colonize and instant-orders paths are well-tested, but pod staging yard interaction is untested.
- **Suggested test**: `test_load_pod_from_staging_yard_success` — mock staging yard with available pod, verify loaded and removed from yard. `test_load_pod_from_staging_yard_capacity_exceeded` — pod mass exceeds capacity, verify ValueError or skip. `test_unload_pod_to_staging_yard` — verify pod transferred to staging yard with cargo update.

### [MAJOR] `game/strategy/services/action_time_resolver.py` — ACTIVATE_ABILITY / DEACTIVATE_ABILITY paths
- **Shard**: 07
- **Location**: action_time_resolver.py:140-185
- **Untested**: `ACTIVATE_ABILITY` with `ability_name=''` in target dict (returns 1), `ACTIVATE_ABILITY`/`DEACTIVATE_ABILITY` with planet facility filtering, `_find_planet_ability_time` with `facility_id` filter (lines 151-155), `_extract_time` with non-dict `ability_data` (lines 181-183). Movement-order shortcut and unknown-type default ARE tested.
- **Suggested test**: `test_activate_ability_empty_ability_name_returns_1` — target with ability_name='', verify default 1. `test_find_planet_ability_time_with_facility_id_filter` — planet with multiple facilities, verify only matching facility used. `test_extract_time_non_dict_ability_data` — ability_data=5, verify correct extraction.

### [MAJOR] `game/simulation/components/abilities/markers.py` — RequiresCommandAndControl.update()
- **Shard**: 07 (upgraded from discovery MINOR)
- **Location**: markers.py:87-104
- **Untested**: `RequiresCommandAndControl.update()` with 6-branch logic: `comp is None`, `comp.ship is None`, layer iteration, `is_active` check, self-skip, `has_ability` check. All other marker abilities well-tested in `test_markers.py` (336 lines).
- **Suggested test**: `test_requires_command_and_control_update_self_disable` — component on ship without C&C ability, verify self-disabled. `test_requires_command_and_control_update_ship_has_cc` — component on ship with C&C ability active, verify not disabled.

### [MAJOR] `game/assets/asset_manager.py` — Star image loading and metadata
- **Shard**: 08
- **Location**: asset_manager.py:132-158, 160-176, 178-191
- **Untested**: `load_star_image` (resolution fallback chain), `get_star_core_info` (metadata lookup with known and unknown star types), `get_star_asset_key_for_type` (star-type-to-asset-key mapping). Existing tests only cover `load_image`/`load_group`/`load_external_image` and planet image resolution.
- **Suggested test**: `test_load_star_image_resolution_fallback` — mock all resolutions to fail, verify missing texture returned. `test_get_star_core_info_known_star` — MAIN_SEQUENCE returns metadata dict. `test_get_star_asset_key_for_type` — WHITE_DWARF → 'white'.

### [MAJOR] `game/strategy/adapters/simulation_adapter.py` — _resolve_seed lazy RNG creation
- **Shard**: 08
- **Location**: simulation_adapter.py:330-336
- **Untested**: `_resolve_seed` lazy creation of `_seed_rng` via `random.Random()` when `seed` is `None`. Zero test references across entire test suite. Exercised in production combat but has no deterministic test.
- **Suggested test**: `test_resolve_seed_random_fallback` — call with seed=None multiple times, verify different results (non-deterministic RNG used). `test_resolve_seed_explicit_seed` — verify deterministic output for same seed.

### [MAJOR] `game/strategy/combat/post_battle_hook.py` — Orphan outcome + _prune_empty_fleets exception paths
- **Shard**: 08
- **Location**: post_battle_hook.py:72-81, 129-132, 200-218
- **Untested**: Orphan outcome entry path (`apply_outcome_to_fleets` when no `ShipInstance` matches `instance_id`), unknown `ShipStatus` warning path (line 129-132), `_prune_empty_fleets` exception branches (empire not in empires dict → continue, no `fleets` attribute → continue, `ValueError` during removal). Happy paths are thoroughly covered (514-line test file).
- **Suggested test**: `test_apply_outcome_orphan_ship` — outcome with non-existent instance_id → logged and skipped. `test_prune_empty_fleets_empire_not_in_dict` — fleet's empire missing from empires dict, verify no crash.

### [MAJOR] `game/strategy/engine/game_session.py` — from_dict error recovery paths
- **Shard**: 08
- **Location**: game_session.py:331-454
- **Untested**: `from_dict` `PersistenceException` raise paths (missing config key, missing galaxy key, missing empire key), pursuer tracker rebuild conditional on `MOVE_TO_FLEET`/`JOIN_FLEET` order types (lines 442-448). Happy-path round-trip IS tested.
- **Suggested test**: `test_from_dict_missing_config` — dict with 'config' key missing → raises PersistenceException. `test_from_dict_missing_galaxy` — dict missing 'galaxy' → raises PersistenceException.

### [MAJOR] `game/strategy/engine/turn_phase_registry.py` — Hook functions
- **Shard**: 08
- **Location**: turn_phase_registry.py:129-149
- **Untested**: Individual hook functions `_capture_move_queue` and `_derive_moved_fleet_ids` lack dedicated unit tests. Exercised only through integration (TurnEngine.process_turn goldentest). The golden order test verifies 15-phase descriptor list ordering but not individual hook behavior.
- **Suggested test**: `test_capture_move_queue_populates_move_queue_and_pre_locations` — mock fleet with MOVE orders, verify move_queue and pre_locations populated.

### [MAJOR] `game/strategy/facade/dto/fleet_dto.py` — FleetInfo.from_fleet order-type branches
- **Shard**: 08
- **Location**: fleet_dto.py:103-219
- **Untested**: 4 of 6 order-type branches in `FleetInfo.from_fleet`: BUILD (shows queue count), TRANSFER load/unload descriptions, COLONIZE with Planet target, and MOVE/COLONIZE with dict target. Only MOVE (HexCoord) and JOIN_FLEET are tested.
- **Suggested test**: `test_from_fleet_build_order` — BUILD order shows queue count. `test_from_fleet_transfer_load_order` — TRANSFER load order description. `test_from_fleet_colonize_planet_target` — COLONIZE with Planet target.

### [MAJOR] `game/ui/screens/atmosphere_target_editor.py` — _set_species_ideal
- **Shard**: 08
- **Location**: atmosphere_target_editor.py:244-260
- **Untested**: `_set_species_ideal` has zero test references. PROJ-283 gas factor setpoint resolution from race config preferences is untested business logic in a UI file.
- **Suggested test**: `test_set_species_ideal_resolves_setpoints` — mock race_config with species preferences, verify slider values set to correct gas pressures.

### [MAJOR] `game/simulation/systems/tick_phase.py` — 6 concrete phase classes
- **Shard**: 09
- **Location**: tick_phase.py:1-100
- **Untested**: 6 concrete phase classes (`RebuildGridPhase`, `AIAndShipUpdatePhase`, `BoundaryEnforcementPhase`, `AttackProcessingPhase`, `RammingPhase`, `ProjectileUpdatePhase`) never instantiated or tested directly. Only `ITickPhase` protocol and `TickPhaseRegistry` tested via `MockPhase`. `create_default_phases` also untested.
- **Suggested test**: `test_create_default_phases_returns_ordered_list` — verify 6 phases returned in correct execution order. `test_rebuild_grid_phase_returns_rebuild_step` — instantiate RebuildGridPhase, verify execute returns correct TickStep.

### [MAJOR] `game/strategy/data/habitability_factors.py` — _make_scalar_extractor / _make_gas_extractor / _build_gas_factors
- **Shard**: 09
- **Location**: habitability_factors.py:120-145, 148-175, 300-340
- **Untested**: Factory functions `_make_scalar_extractor` (None-guard, float coercion at lines 132-135) and `_make_gas_extractor` (atmosphere None guard, `.get(formula, 0.0)` fallback, float coercion) have no dedicated unit tests. `_build_gas_factors` builds 10 gas HabitabilityFactor entries — O2/N2 special-cased defaults (21kPa/5kPa for O2, 79kPa/20kPa for N2) have no boundary tests. Registry-level tests exercise generated extractors but not factory-internal logic.
- **Suggested test**: `test_make_scalar_extractor_handles_none_species` — species with None scalar field returns 0.0. `test_make_gas_extractor_defaults_missing_gas` — species with no O2 preference returns 0.0. `test_build_gas_factors_o2_special_defaults` — verify O2 default ideal=21kPa, tolerance=5kPa.

### [MAJOR] `game/strategy/generation/density/primitives/noise.py` — _hash_coord / _smooth_noise
- **Shard**: 09
- **Location**: noise.py:18-50
- **Untested**: `_hash_coord` (bit-manipulation: XOR, multiply, right-shift at lines 18-22) and `_smooth_noise` (smoothstep interpolation, bilinear interpolation, integer/fractional-coordinate decomposition at lines 28-50) have no standalone unit tests. Tested only through `NoisePrimitive.evaluate()` integration.
- **Suggested test**: `test_hash_coord_deterministic` — same coordinates/shift → same hash. `test_hash_coord_different_coords_different_hash` — verify avalanche effect. `test_smooth_noise_returns_between_0_and_1` — verify output range.

### [MAJOR] `game/ui/screens/setup_screen.py` — _get_ship_factory
- **Shard**: 09
- **Location**: setup_screen.py:60-80
- **Untested**: Module-level lazy singleton factory getter `_get_ship_factory` has zero test references. Uses global mutable state (`global _ship_factory`), `get_default_registry_provider()`, and `GameRegistries` construction.
- **Suggested test**: `test_get_ship_factory_returns_singleton` — two calls return same instance. `test_get_ship_factory_creates_with_correct_registries` — verify factory wraps default registry provider.

### [MAJOR] `game/simulation/components/abilities/harvester.py` — _parse_attrs dict/non-dict branches + StagingYardAbility / PlanetaryYardAbility
- **Shard**: 09
- **Location**: harvester.py:80-130
- **Untested**: All 4 `_parse_attrs` dict/non-dict branches in `ResourceHarvesterAbility`, `LocalStorageAbility`, `StagingYardAbility`, and `SpaceShipyardAbility` untested. `StagingYardAbility` non-dict branch (`float(data)` coercion at line 104) and `PlanetaryYardAbility.__init__` override (line 123) untested.
- **Suggested test**: `test_staging_yard_parse_attrs_float_coercion` — data=5.0, verify self.capacity=5.0. `test_resource_harvester_parse_attrs_dict_branch` — dict with rate and resource_id. `test_planetary_yard_init_override` — verify PlanetaryYardAbility.__init__ correctly sets yard-specific fields.

### [MAJOR] `game/ui/screens/strategy_click_dispatcher.py` — 12 mode-specific click handlers
- **Shard**: 09 (partially confirmed)
- **Location**: strategy_click_dispatcher.py:120-400
- **Untested**: 12 of 14 mode-specific handlers untested: `_handle_join_mode_click`, `_handle_colonize_mode_click`, `_handle_transfer_mode_click`, `_handle_edit_move_click`, `_handle_drop_cargo_mode_click`, `_handle_load_cargo_mode_click`, `_handle_warp_target_click`, `_handle_implode_planet_click`, `_handle_stellerate_star_click`, `_handle_open_warp_click`, `_handle_close_warp_click`, `_handle_dyson_sphere_click`. BUG-93 path (move failure → SELECT reset, line 121) also untested. `_hit_test_planets`, `_resolve_click_target`, `_handle_picking`, and `dispatch_click` routing have integration coverage.
- **Suggested test**: `test_handle_colonize_mode_click_valid_planet` — verify COLONIZE order created. `test_handle_warp_target_click_invalid_location` — verify error or no-op.

### [MAJOR] `game/ui/screens/transfer_view_model.py` — 11 ViewModel methods
- **Shard**: 09 (partially confirmed)
- **Location**: transfer_view_model.py:1-200
- **Untested**: 11 methods untested: `set_pending_zero`, `clear_all_pending`, `reset_pending`, `format_pending`, `toggle_filter_empty`, `set_sources`, `select_source` (with side effects of target rebinding), `select_target`, `target_labels`, `source_labels`, `get_amounts`, `_build_pod_rows`, `visible_rows`. Only `apply_arrow`, `apply_max`, `build_row_data` are directly tested.
- **Suggested test**: `test_set_pending_zero_resets_row` — call with species row, verify pending set to 0. `test_select_source_rebinds_target` — select source, verify target and filter updated.

### [MAJOR] `game/strategy/engine/harvesting_engine.py` — _get_harvest_booster_mult
- **Shard**: 11
- **Location**: harvesting_engine.py:388-419
- **Untested**: `_get_harvest_booster_mult` has zero grep matches across entire test suite. Contains late-import chain for `find_abilities_in_scope` and `aggregate_multipliers`, iterates over 4 scopes (planet/sector/system/empire), aggregates results via two-phase stacking. Existing harvesting tests cover `process_harvesting_tick`, `recalculate_storage`, per-tick harvesting, depletion, and storage overflow but never call this method.
- **Suggested test**: `test_get_harvest_booster_mult_aggregates_across_scopes` — mock 4 scopes with different multipliers, verify aggregation. `test_get_harvest_booster_mult_no_boosters_returns_1` — empty scopes return 1.0.

### [MAJOR] `game/strategy/engine/fleet_movement_engine.py` — _filter_jump_past_collisions untested branches
- **Shard**: 11 (partially confirmed)
- **Location**: fleet_movement_engine.py:300-350
- **Untested**: Larger fleet drops path (`ships_a > ships_b` → drop fleet_a at line 324-325), `JOIN_FLEET` order type matching (line 301), non-pursuit order pass-through (`order_a.type not in _PURSUIT → continue` at line 306), `isinstance(fleet_b, Fleet)` guard (line 309), multiple overlaps / `drop_ids` with multiple fleet pairs. One test exists for tie-breaking (equal ships, smaller ID dropped) but no other paths.
- **Suggested test**: `test_filter_jump_past_drops_larger_fleet` — fleet_a with 5 ships, fleet_b with 3, verify fleet_a dropped. `test_filter_jump_past_join_fleet_order` — JOIN_FLEET order triggers collision detection. `test_filter_jump_past_non_pursuit_passes_through` — MOVE order not filtered. `test_filter_jump_past_target_not_fleet_passes_through` — target is None or non-Fleet.

### [MAJOR] `game/core/constants.py` — LayerDefaults
- **Shard**: 12
- **Location**: constants.py:40-44
- **Untested**: `LayerDefaults` constants `CORE_RADIUS_PCT`, `INNER_RADIUS_PCT`, `OUTER_RADIUS_PCT` completely untested. Test file (`test_constants.py`, 26 lines) tests only `EARTH_MASS` and `ResourceCatalog`.
- **Suggested test**: `test_layer_defaults_core_radius_pct` — verify CORE_RADIUS_PCT value. `test_layer_defaults_radii_sum_to_1` — verify CORE + INNER + OUTER = 1.0.

### [MAJOR] `game/simulation/combat/attack_contract.py` — WeaponFamilyMetadata / FAMILY_METADATA
- **Shard**: 12
- **Location**: attack_contract.py:155-190
- **Untested**: `WeaponFamilyMetadata` and `FAMILY_METADATA` module-level dict untested. Two test functions reference PDC targeting behavior but test the targeting system, not the metadata values themselves. No test directly verifies `FAMILY_METADATA[WeaponFamily.PDC].targets_missiles == True` or defaults for non-PDC families.
- **Suggested test**: `test_pdc_metadata_targets_missiles` — verify FAMILY_METADATA[WeaponFamily.PDC].targets_missiles is True. `test_beam_metadata_does_not_target_missiles` — verify non-PDC families default to targets_missiles=False.

### [MAJOR] `game/simulation/components/abilities/base.py` — Ability._parse_attrs / StaticValueAbility._parse_attrs / SimpleMultiplierAbility._parse_attrs
- **Shard**: 12
- **Location**: base.py:98-115, 459-465, 511-517
- **Untested**: Base no-op `_parse_attrs` never tested directly. `StaticValueAbility._parse_attrs` data format handling (float, int, bool) not explicitly verified. `SimpleMultiplierAbility._parse_attrs` setattr-based attribute population not directly tested. All three exercised indirectly through concrete subclass instantiation via `__init__` but the specific `_parse_attrs` behavior is never pinned.
- **Suggested test**: `test_base_parse_attrs_is_noop` — call base Ability._parse_attrs, verify no error, no mutation. `test_static_value_parse_attrs_float` — pass float data, verify attribute set. `test_simple_multiplier_parse_attrs_sets_multiplier` — pass dict with multiplier, verify attribute.

### [MAJOR] `game/strategy/data/galaxy_system_generator.py` — _load_planet_types / _load_star_types / _load_system_archetypes
- **Shard**: 12
- **Location**: galaxy_system_generator.py:240-245, 293-299, 319-324
- **Untested**: Module-level cache functions `_load_planet_types`, `_load_star_types`, `_load_system_archetypes` untested. Cache-miss/JSON-load branches and cache-hit paths not explicitly verified. `_apply_system_archetype` is imported by tests but uses hand-rolled fakes bypassing the real cache path.
- **Suggested test**: `test_load_planet_types_cache_miss_loads_json` — patch json.load, verify data loaded from file. `test_load_planet_types_cache_hit_returns_cached` — second call returns same object without re-reading file. `test_load_star_types_returns_dict` — verify structure.

### [MAJOR] `game/strategy/engine/production_spawner.py` — __init__ / _resolve_planet_location
- **Shard**: 12
- **Location**: production_spawner.py:34-42, 84-107
- **Untested**: Constructor's registration logic with explicit args never tested (only defaults). `_resolve_planet_location` branches untested: galaxy=None, no parent system, planet.location=None. Happy path indirectly covered through `spawn_completed_item` but error/edge branches completely untested.
- **Suggested test**: `test_production_spawner_init_with_explicit_registries` — pass custom registries and event_bus, verify stored. `test_resolve_planet_location_galaxy_none` — galaxy=None, verify None returned or raises. `test_resolve_planet_location_no_parent_system` — planet with no system, verify graceful handling.

### [MAJOR] `game/strategy/engine/superweapon_order_processor.py` — _finalize_superweapon / execute_superweapon / _stabilizer_target_label
- **Shard**: 12
- **Location**: superweapon_order_processor.py:65-135, 137-319, 321-335
- **Untested**: `_finalize_superweapon` — consume_ship=True path and fleet-empty removal (`empire.remove_fleet`) not verified. `execute_superweapon` — CLOSE_WARP_POINT legacy back-compat path and several stop-early error paths not specifically verified. `_stabilizer_target_label` — zero test references.
- **Suggested test**: `test_finalize_superweapon_consumes_ship` — superweapon with consume_ship=True, verify ship removed from fleet. `test_execute_superweapon_close_warp_legacy_string` — plain string target, verify compatibility path works. `test_stabilizer_target_label_formats_correctly` — verify label formatting with planet/star names.

### [MAJOR] `game/strategy/systems/save_game_service.py` — set_replay_store / get_replay_store / notification functions
- **Shard**: 12
- **Location**: save_game_service.py:33-61
- **Untested**: Module-level `set_replay_store`/`get_replay_store` getter/setter pair untested. `_notify_replay_store_save_or_load` and `_notify_replay_store_save_deleted` notification functions untested (branch on None store, exception swallowing not verified).
- **Suggested test**: `test_set_and_get_replay_store` — set a mock store, verify get returns it. `test_notify_save_or_load_none_store_noop` — None store, verify no crash. `test_notify_save_or_load_calls_store` — valid store, verify callback invoked.

### [MAJOR] `game/ui/screens/builder/stat_getters.py` — 21 untested symbols
- **Shard**: 12
- **Location**: stat_getters.py:1-200
- **Untested**: `fmt_multiply`, `fmt_decimal`, `get_mass_display`, `get_crew_required`, `get_crew_capacity`, `get_life_support`, `get_max_targets`, `get_armor_hp`, `get_maneuver_points`, `get_strategic_speed`, `get_fuel_consumption`, `get_ammo_consumption`, `get_energy_consumption`, `get_warp_tonnage`, `get_warp_cost`, `get_passenger_capacity`, `has_superweapons`, `mass_unit_func`. 11 symbols ARE tested (fmt_time, fmt_score, fmt_targeting, fmt_yes_no, fmt_text, mass_validator, crew_validator, life_support_validator, and several resource getters).
- **Suggested test**: `test_fmt_multiply_formats_with_x_suffix` — multiply=2.5, verify "2.5x". `test_fmt_decimal_rounds` — verify precision. `test_get_mass_display_with_tonnage` — mock component with mass_tonnage, verify display string. `test_get_crew_required_sums_crew` — multiple crew-consuming abilities, verify sum.

---

## Cross-Shard Patterns

1. **Phase 1 false negatives dominant**: Across all 6 shards, the most common agent error was Phase 1's name-based import-grep heuristic missing test files. Test files that exercise production code through indirect patterns (registry lookups, factory functions, package `__init__.py` re-exports) were systematically missed. This produced 27 false CRITICAL claims across shards 07-12.

2. **Search directory errors**: Phase 2 agents searched wrong directories (e.g., `tests/unit/engine/` instead of `tests/unit/systems/`, `tests/unit/strategy/engine/` instead of `tests/unit/strategy/consumable_management_engine/`), missing entire test subdirectories.

3. **Content blindness**: Even when Phase 2 agents correctly identified test files, they sometimes failed to read or analyze the content (e.g., `test_build_queue_helpers.py` listed but reported as "zero tests" for a function it contains 14 dedicated tests for).

4. **Genuine gaps concentrate in**: factory-internal logic (tests only exercises through registry/public API, never isolates the factory), private method error paths, superweapon edge cases, UI business logic, and module-level caches/singletons.

5. **Best-tested modules (falsely reported)**: `weapons.py` (1828 lines of tests), `fleet_aura_manager.py` (1804 lines across 7 files), `target_evaluator.py` (1592 lines), `planet_gen.py` (812 lines), `build_queue_source.py` (930 lines), `game_initializer.py` (646 lines), `quickstart_builder.py` (442 lines) — all had substantial to excellent coverage but were reported as major gaps.
