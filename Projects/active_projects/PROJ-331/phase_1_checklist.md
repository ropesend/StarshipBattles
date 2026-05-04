# PROJ-331 — Per-File Characterization Test Plans

> Format: each phase lists the new tests to create. SPECIFIC test names — every line is one behavior pinned by one test.

## §1 — `battle_state.py` characterization gaps (16 tests)

**New file:** `tests/unit/simulation/test_battle_state_live_object_bridges.py`

### `ComponentState.from_component` (1)
- [ ] `test_from_component_extracts_id_hp_layer_and_serializes_modifiers` — Build `Mock` Component with two modifiers; assert returned `ComponentState` has correct id/hp/active/layer/modifiers and modifier dicts have `id` + `value` keys (not Modifier objects).

### `ShipState.from_ship` (3)
- [ ] `test_from_ship_generates_uuid_when_ship_id_not_provided` — Pass `ship_id=None`; assert returned `ship_id` matches UUID4 regex.
- [ ] `test_from_ship_uses_provided_ship_id` — Pass `ship_id="my-id"`; assert returned `ship_id == "my-id"`.
- [ ] `test_from_ship_resolves_current_target_to_target_name` — Set `ship.current_target = Mock(name="enemy-ship")`; assert `current_target_id == "enemy-ship"`.

### `ShipState.to_ship` (3)
- [ ] `test_to_ship_raises_validation_exception_when_registries_is_none` — Call with `registries=None`; assert `ValidationException` with `MISSING_DEPENDENCY` code.
- [ ] `test_to_ship_skips_unknown_layer_with_warning` — Provide a `ShipState` with components in layer name `"BOGUS"`; assert log warning and Ship constructed without that layer's components.
- [ ] `test_to_ship_applies_modifiers_before_damage_state` — Provide ComponentState with modifier + `current_hp=5, max_hp=10`; assert (mocked) Component's `add_modifier` is called BEFORE `current_hp` assignment (sequence assertion).

### `ProjectileState.from_projectile` (2)
- [ ] `test_from_projectile_resolves_owner_and_target_via_ship_id_map` — Pass projectile with owner+target Ship mocks and a `ship_id_map={"owner_id": "battle_owner_id", "target_id": "battle_target_id"}`; assert resulting state's `owner_ship_id == "battle_owner_id"` and `target_ship_id == "battle_target_id"`.
- [ ] `test_from_projectile_extracts_enum_type_value` — Set `proj.type = AttackType.MISSILE` (Enum); assert resulting state's `projectile_type` is the enum's `.value`, not its repr.

### `ProjectileState.to_projectile` (1)
- [ ] `test_to_projectile_resolves_owner_and_target_via_ship_lookup` — Construct ProjectileState with owner+target ids; pass `ship_lookup={...}`; assert resulting Projectile is constructed with the looked-up Ship instances (or None when id missing from lookup).

### `BattleState.capture_from_engine` (3)
- [ ] `test_capture_from_engine_generates_battle_id_when_not_provided` — Pass `battle_id=None`; assert returned state's `battle_id` matches UUID4 regex.
- [ ] `test_capture_from_engine_reuses_existing_ship_id_map_entries` — Pass a pre-populated `ship_id_map={"engine_id": "preserved_id"}`; assert resulting `BattleState.ships` contains key `"preserved_id"` (not `"engine_id"`).
- [ ] `test_capture_from_engine_serializes_only_alive_projectiles` — Mock engine with 3 projectiles (2 alive, 1 dead); assert `len(state.projectiles) == 2`.

### `BattleState` query methods (4)
- [ ] `test_get_ships_by_team_returns_only_matching_team_id` — Build state with mixed-team ships; assert filtered list correct.
- [ ] `test_get_surviving_ships_excludes_escaped_and_dead` — Build state with 4 ships covering (alive-not-escaped, alive-escaped, dead-not-escaped, dead-escaped); assert only the (alive-not-escaped) is returned.
- [ ] `test_get_escaped_ships_returns_only_retreat_status_escaped` — Build state with mixed retreat statuses; assert filter correct.
- [ ] `test_get_destroyed_ships_excludes_escaped_dead_ships` — Build state with both `is_alive=False, retreat_status=None` and `is_alive=False, retreat_status="escaped"`; assert only the first is returned.

### `BattleResults` query methods (2)
- [ ] `test_get_team_survivors_filters_surviving_ships_by_team_id` — Build results with mixed-team surviving_ships list; assert filter.
- [ ] `test_get_team_losses_filters_destroyed_ships_by_team_id` — Build results with mixed-team destroyed_ships list; assert filter.

## §2 — `battle_controller.py` characterization gaps (12 tests across 2 files)

### §2a — Edits to `tests/unit/simulation/battle_controller/test_state.py` (4 new tests)

- [ ] `test_load_state_restores_alive_projectiles_only` — Mock state with 3 projectiles (2 alive, 1 dead); assert `engine.projectiles` ends with 2 entries (each from `proj_state.to_projectile(ship_lookup)`).
- [ ] `test_load_state_resolves_projectile_owner_via_ship_id_map` — Mock state with 1 alive projectile owning ship "save_id_1"; mock ship_id_map mapping engine ship to "save_id_1"; assert `to_projectile` called with `ship_lookup` containing the engine ship.
- [ ] `test_require_registries_returns_none_for_empty_state_when_registries_unset` — Call `_require_registries_for_state_restore(state_count=0)` with `controller._registries=None`; assert returns `None` (no raise).
- [ ] `test_require_registries_raises_validation_exception_for_nonempty_state_when_registries_unset` — Call `_require_registries_for_state_restore(state_count=3)` with `controller._registries=None`; assert `ValidationException` with `MISSING_DEPENDENCY` code.

### §2b — New file `tests/unit/simulation/battle_controller/test_start_from_spec.py` (8 tests)

- [ ] `test_start_from_spec_raises_runtimeerror_when_no_ship_builder_and_no_registry_provider` — Call `start_from_spec(spec, ai_factory=Mock())` with both args None; assert RuntimeError with PROJ-252 message fragment.
- [ ] `test_start_from_spec_uses_explicit_ship_builder_when_provided` — Patch `start_engine_from_spec`; pass `ship_builder=Mock()`; assert `start_engine_from_spec` was called with that exact builder (not `build_context_ship_builder` output).
- [ ] `test_start_from_spec_falls_back_to_context_builder_when_registry_provider_supplied` — Patch `build_context_ship_builder`; pass `registry_provider=Mock()`, `ship_builder=None`; assert `build_context_ship_builder` called with that registry_provider.
- [ ] `test_start_from_spec_constructs_default_battleconfig_when_config_none` — Patch `start_engine_from_spec`; call without `config`; assert `controller._config.seed == spec.seed` and `controller._config.absolute_max_ticks == spec.absolute_max_ticks`.
- [ ] `test_start_from_spec_uses_provided_battleconfig_when_supplied` — Pass explicit `BattleConfig`; assert `controller._config is that_config`.
- [ ] `test_start_from_spec_constructs_unbounded_region_when_spec_has_no_boundary` — Set `spec.boundary = None`; patch `start_engine_from_spec`; assert `controller._retreat_manager.boundary` is an `UnboundedRegion`.
- [ ] `test_start_from_spec_uses_spec_boundary_when_present` — Set `spec.boundary = RectBoundary(...)`; assert `controller._retreat_manager.boundary is spec.boundary`.
- [ ] `test_start_from_spec_populates_ship_id_map_from_engine_ships` — Mock engine with 3 ships; assert `controller._ship_id_map` has 3 entries (one per ship.id, mapping to itself).

## §3 — `conflict_resolution_engine.py` characterization gaps (13 tests)

**New file:** `tests/unit/strategy/conflict_resolution/test_logging_and_lookups.py`

### `_validate_tick_inputs` (2)
- [ ] `test_validate_tick_inputs_raises_validation_exception_when_fleet_has_none_location` — Build empires with one fleet `location=None`; call `resolve_all_conflicts(empires, tick=20)`; assert `ValidationException` with `empire_id`/`fleet_id` in context.
- [ ] `test_validate_tick_inputs_passes_when_all_fleets_have_locations` — Build empires with all fleets locationed; call `resolve_all_conflicts`; assert no raise (returns `ConflictResult`).

### `resolve_all_conflicts` short-circuit (1)
- [ ] `test_resolve_all_conflicts_returns_zero_combats_when_tick_is_none` — Pass `tick=None`; assert `ConflictResult(combats_resolved=0, fleets_destroyed=[])` and `_resolve_conflicts` not invoked.

### `_log_combat_result` (4)
- [ ] `test_log_combat_result_skips_emission_when_event_bus_is_none` — Engine with `event_bus=None`; call `_resolve_combat_at_hex` with mock resolver; assert no emission attempt happens (no AttributeError).
- [ ] `test_log_combat_result_extracts_unique_storm_names_from_sector_effects` — Pass `environmental_effects=[{"providers": [{"source_kind": "storm", "source_label": "Ion Storm"}]}, {"providers": [{"source_kind": "storm", "source_label": "Ion Storm"}, {"source_kind": "storm", "source_label": "Plasma"}]}]`; assert event payload's `storm_names == ["Ion Storm", "Plasma"]` (deduped, in encounter order).
- [ ] `test_log_combat_result_uses_min_owner_id_as_empire_id` — Two fleets with `owner_id=5` and `owner_id=2`; assert event payload's `empire_id == 2`.
- [ ] `test_log_combat_result_threads_replay_unavailable_reason_from_battle_result` — Resolver returns `BattleResult(... replay_unavailable_reason="sole_survivor")`; assert event payload's `replay_unavailable_reason == "sole_survivor"`.

### `_lookup_environmental_effects` (2)
- [ ] `test_lookup_environmental_effects_returns_none_when_galaxy_is_none` — Engine with `_galaxy=None`; call `_lookup_environmental_effects(location)`; assert returns None.
- [ ] `test_lookup_environmental_effects_returns_none_when_galaxy_lacks_get_system_at_location` — Engine with `_galaxy = Mock(spec=[])` (no `get_system_at_location` attr); assert returns None.

### `_collect_team_modifiers` (1)
- [ ] `test_collect_team_modifiers_returns_none_and_logs_when_collector_raises` — Monkeypatch `collect_combat_modifiers` to raise; call `_collect_team_modifiers(...)`; assert returns None and a warning is logged.

### Multi-fleet ordering determinism (1)
- [ ] `test_resolve_combat_at_hex_orders_fleets_by_empire_id_then_fleet_id` — Build occupants with empires `[emp_5, emp_2]` each with 2 fleets `[fleet_99, fleet_3]`; capture `resolver.resolve_battle` `fleets` arg order; assert order is `[emp2/fleet3, emp2/fleet99, emp5/fleet3, emp5/fleet99]`.

### Sole-survivor / no-ships (2)
- [ ] `test_resolve_combat_at_hex_skips_when_no_fleet_has_any_ships` — All occupant fleets have empty `ships=[]`; call `_resolve_combat_at_hex`; assert `resolver.resolve_battle` NOT called and INFO log emitted.
- [ ] `test_resolve_combat_at_hex_returns_when_only_one_empire_present` — Occupants from a single empire; call `_resolve_combat_at_hex`; assert resolver not called (early return on `len(fleets_by_empire) < 2`).

## Phase Completion Criteria

- [ ] All 41 tests written and green.
- [ ] `python Tools/lint_test_files.py` reports 0 violations.
- [ ] Per-file commits (4 commits): one each for the 3 new files + 1 for the test_state.py edits.
- [ ] Full sharded suite green.
- [ ] `Projects/projects_index.md` updated.
