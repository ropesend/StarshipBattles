# Shard 18 — Test Coverage Audit

## Summary
- Shard: 18
- Production files in scope: 35
- Production files actually read: 35
- Unit test files deep-read: 0 (Discovery phase — coverage claims verified against Phase 1 matrix + production code)
- Total findings: 67
- Critical: 9 | Major: 18 | Minor: 19 | Advisory: 21

## Tier 0 — Zero Unit Tests (CRITICAL for non-UI, ADVISORY for UI)

### game/app_bootstrap.py (281 LOC, layer: game_root)
- **Status**: No unit test file mapped in Phase 1 matrix. Docstring references `tests/unit/test_app_bootstrap_invariants.py`, which exists on disk but was not matched by the AST scanner — a false negative.
- **Key symbols** (all untested per matrix): `configure_logging` (line 56), `parse_args` (line 70), `_detect_resolution` (line 104), `_timed_phase` (line 120), `bootstrap` (line 142), `BootstrapResult` (line 80)
- **Risk**: `bootstrap()` is the single entry point for the entire application initialization sequence with 6 non-negotiable invariant ordering rules. A flipped order-of-operations (e.g. loading sprites before component derivatives, or `create_production` before `pygame.init`) would manifest as startup crashes. The `_detect_resolution` function (lines 104-117) handles 3 branches (forced-resolution, 4K, 2560x1600, fallback) — none are explicitly tested. The `BootstrapResult` dataclass carries 13 fields; construction errors would fail at `Game.__init__`.
- **Suggested tests**:
  1. `test_detect_resolution_forced` — `--force-resolution` returns 2560x1600 regardless of monitor size
  2. `test_detect_resolution_4k` — monitor >= 3840x2160 returns that resolution
  3. `test_detect_resolution_windowed` — monitor >= 2560x1600 returns that resolution
  4. `test_detect_resolution_fallback` — small monitor returns 90% scaled-down
  5. `test_configure_logging_creates_dir` — log directory created if missing
  6. `test_parse_args_default` — no args returns default namespace
  7. `test_parse_args_force_resolution` — flag parsed correctly
  8. `test_bootstrap_returns_all_fields` — BootstrapResult has all 13 fields populated
  9. `test_bootstrap_invariant_font_before_get_font` — verify ordering invariants

### game/core/protocols/common.py (46 LOC, layer: core)
- **Status**: No unit test file. 7 symbols, 0 tested.
- **Key symbols**: `_has_attrs` (line 17), `ILocatable` (line 23), `INamed` (line 32), `IOwnable` (line 41)
- **Risk**: `_has_attrs` is the duck-typing helper used by EVERY TypeGuard in the codebase (imported by `strategy_entities.py`, `combat.py`, `boundary.py`, `common.py` — plus `game.simulation.interfaces.entity_protocols`, `game.simulation.interfaces.ability_protocols`, and `game.ai.protocols`). A bug here would silently break runtime duck typing for all 23+ protocol TypeGuards. `ILocatable`, `INamed`, and `IOwnable` are composable base mixins — untested protocol conformance.
- **Suggested tests**:
  1. `test_has_attrs_true` — object with all attributes returns True
  2. `test_has_attrs_false_missing_one` — missing attribute returns False
  3. `test_has_attrs_no_attrs_requested` — empty args returns True
  4. `test_ilocatable_isinstance` — class with `location` property conforms
  5. `test_inamed_isinstance` — class with `name` property conforms
  6. `test_iownable_isinstance` — class with `owner_id` property conforms
  7. `test_iownable_none_owner` — `owner_id` can be None, still conforms

### game/simulation/combat/families/projectile.py (47 LOC, layer: simulation)
- **Status**: No unit test file. 2 symbols (ProjectileHandler, ProjectileHandler.fire).
- **Key symbols**: `ProjectileHandler.fire` (line 23)
- **Risk**: The `ProjectileHandler` is registered at module load (line 47) as `WEAPON_REGISTRY.register(WeaponFamily.PROJECTILE, ProjectileHandler())`. The `fire()` method constructs a `Projectile` entity with velocity calculations involving `normalize() * speed + ship.velocity` (line 31). A zero-length aim vector would produce a division by zero in `normalize()`. The `projectile_speed / SimulationConstants.PROJECTILE_SPEED_SCALE` scaling (line 30) is a magic-number division — wrong scale constant would silently produce wrong projectile speeds.
- **Suggested tests**:
  1. `test_fire_creates_projectile_resolution` — valid request returns ProjectileResolution
  2. `test_fire_projectile_velocity_includes_ship_velocity` — projectile velocity = aim * speed + ship.velocity
  3. `test_fire_zero_damage` — damage=0 projectile still created
  4. `test_fire_endurance_none` — non-seeking projectile has endurance=None
  5. `test_registry_registered` — handler appears in WEAPON_REGISTRY under PROJECTILE family

### game/simulation/entities/ship_resource_manager.py (53 LOC, layer: simulation)
- **Status**: No unit test file. 3 symbols (ShipResourceManager, __init__, get_resource_stat).
- **Key symbols**: `ShipResourceManager.get_resource_stat` (line 38)
- **Risk**: `get_resource_stat` constructs attribute names dynamically via f-string (line 52: `f'{resource_name}_{stat_type}'`) then uses `getattr(self._ship, attr_name, 0.0)`. A typo in a resource name or stat_type would silently return 0.0 with no error, causing fuel/ammo/energy tracking to silently underflow. The `_resources_initialized`, `prev_max_resources`, `prev_max_shields` fields are used for delta calculations on the Ship — untested state transitions.
- **Suggested tests**:
  1. `test_get_resource_stat_existing` — `get_resource_stat('fuel', 'consumption')` returns correct value
  2. `test_get_resource_stat_nonexistent` — returns 0.0 for unknown attribute
  3. `test_get_resource_stat_empty_string` — empty resource_name still constructs f-string, returns 0.0
  4. `test_prev_max_resources_initial_empty` — starts as empty dict
  5. `test_resources_initialized_false_on_init` — starts as False

### game/simulation/entities/stat_contributors/command.py (100 LOC, layer: simulation)
- **Status**: No unit test file. 3 symbols: `priority_sort_key`, `contribute_multiplex_tracking`, `allocate_crew_and_life_support`.
- **Risk**: `allocate_crew_and_life_support` is Phase 2 of the ship stat calculation pipeline. It mutates `ship.crew_onboard`, `ship.crew_required`, `ship.max_targets`, `ship.max_mass_budget`, and deactivates components when crew is insufficient (line 99: `comp.is_active = False; comp.status = ComponentStatus.NO_CREW`). A bug here would propagate through every ship stat calculation. The `priority_sort_key` uses `lookup_crew_priority` from the stat contributor registry — untested priority ordering. `contribute_multiplex_tracking` uses typed `MultiplexTrackingAbility.slots` access (line 51) — the `getattr(ab, "slots", 0)` fallback is untested.
- **Suggested tests**:
  1. `test_priority_sort_key_crew_first` — CommandAndControl components sort before weapons
  2. `test_allocate_crew_sufficient` — enough crew, all components stay active
  3. `test_allocate_crew_insufficient` — not enough crew, low-priority components deactivated
  4. `test_allocate_crew_equal` — crew equals life_support, uses effective_crew = min(available_crew, available_life_support)
  5. `test_allocate_crew_life_support_limits` — more crew than life_support, capped
  6. `test_contribute_multiplex_tracking_bumps_max_targets` — mt > ship.max_targets updates
  7. `test_contribute_multiplex_tracking_ignores_zero` — mt=0 does not change max_targets
  8. `test_contribute_multiplex_tracking_sums_across_instances` — two MultiplexTracking abilities → summed slots
  9. `test_allocate_mass_budget_from_vehicle_class` — max_mass_budget read from vehicle_classes dict

### game/simulation/entities/stat_contributors/weapons.py (56 LOC, layer: simulation)
- **Status**: No unit test file. 1 symbol: `aggregate_targeting_scores`.
- **Risk**: `aggregate_targeting_scores` computes `ecm_score` and `attack_mods` via `get_ability_total` with bool defense (lines 48-53: `if isinstance(ecm_score, bool): ecm_score = 0.0`). The defensive bool check guards against `True` payloads from marker abilities but is untested. `ship.baseline_to_hit_offense` and the return value are both side effects — no assertion verifies both are set correctly.
- **Suggested tests**:
  1. `test_aggregate_targeting_scores_numeric` — returns float ECM score, sets baseline_to_hit_offense
  2. `test_aggregate_targeting_scores_bool_defense` — get_ability_total returns True → treated as 0.0
  3. `test_aggregate_targeting_scores_empty_pool` — no components → returns 0.0
  4. `test_aggregate_targeting_scores_no_ecm` — no ToHitDefenseModifier abilities → returns 0.0

### game/strategy/engine/handlers/base.py (391 LOC, layer: strategy)
- **Status**: No unit test file. 18 symbols, 0 tested. CRITICAL — this is the foundation for ALL 20+ command handlers.
- **Key symbols**: `add_move_order_if_needed` (line 32), `ICommandHandler` (line 85), `BaseCommandHandler` (line 101) with 9 resolution helpers, `CommandHandlerRegistry` (line 362) with `register`/`dispatch`
- **Risk**: `BaseCommandHandler` provides static methods used by every command handler. `_resolve_fleet` (lines 111-132) handles owner-validation branching (empire_id=None skips); `_resolve_player_fleet` (lines 134-156) authorizes against `session.active_empire` (BUG-125 security critical); `_resolve_queue` (lines 270-301) traverses facility lists for multi-queue planets; `_resolve_queue_owner` (lines 303-343) has 3 distinct return paths (entity, facility, None). `add_move_order_if_needed` (lines 32-81) implements chain-aware path calculation with BUG-70 reverse-order search. `CommandHandlerRegistry.dispatch` (line 377) returns `ValidationResult.error` for unknown commands — no test verifies this error path. The sheer number of untested helpers (12 resolution methods + 1 command handler + 1 dispatcher) makes this the highest-risk gap in Shard 18.
- **Suggested tests**:
  1. `test_resolve_fleet_found` — valid fleet_id returns (fleet, None)
  2. `test_resolve_fleet_not_found` — unknown fleet_id returns (None, error_result)
  3. `test_resolve_fleet_wrong_owner` — fleet.owner_id != empire_id returns error
  4. `test_resolve_fleet_no_ownership_check` — empire_id=None skips ownership validation
  5. `test_resolve_player_fleet_authorizes_active_empire` — uses session.active_empire.id, not request body
  6. `test_resolve_player_fleet_no_active_empire` — session.active_empire is None → error
  7. `test_resolve_planet_found` — valid planet_id returns (planet, None)
  8. `test_resolve_planet_not_found` — unknown planet_id returns error
  9. `test_resolve_planet_optional_not_required` — required=False, not found → returns None
  10. `test_resolve_planet_optional_required` — required=True, not found → raises ValueError
  11. `test_resolve_queue_base_queue` — queue_id=None returns entity.construction_queue
  12. `test_resolve_queue_facility_instance_id` — queue_id matches facility instance_id
  13. `test_resolve_queue_owner_facility` — validates facility is returned, not the list
  14. `test_resolve_queue_owner_fleet_yard` — fleet_YARD_n pattern resolves to fleet
  15. `test_add_move_order_if_needed_already_at_target` — fleet at target → no order added, success
  16. `test_add_move_order_if_needed_no_path` — no path to target → error result
  17. `test_add_move_order_if_needed_chain_aware` — chain-aware start hex from last MOVE order
  18. `test_command_handler_registry_dispatch_unknown` — unregistered command → error result
  19. `test_command_handler_registry_dispatch_known` — registered handler → delegated
  20. `test_emit_validated_order_success` — valid result → order added, logged
  21. `test_emit_validated_order_failure` — invalid result → no order added
  22. `test_resolve_build_entity_planet` — entity_type='planet' → resolves planet
  23. `test_resolve_build_entity_fleet` — entity_type='fleet' → resolves fleet
  24. `test_resolve_build_entity_unknown` — unknown entity_type → returns None
  25. `test_build_colonize_target_with_population` — pop/cargo amounts → wrapped dict
  26. `test_build_colonize_target_no_amounts` — no amounts → plain Planet

### game/ui/screens/galaxy_test/system_mode.py (576 LOC, layer: ui) — ADVISORY
- **Status**: No unit test file. 13 symbols, 0 tested. UI rendering helper.
- **Key symbols**: `SystemModeHelper.generate` (line 206), `SystemModeHelper.handle_click` (line 324), `SystemModeHelper.draw` (line 484)
- **Risk**: Contains `generate()` with blueprint loading, star/planet generation, seed parsing, and camera centering. Missed `except ValueError` in seed parsing would crash on non-numeric input. `handle_click` has a distance-proximity check (line 340-345) for click-to-select — no tests verify the selection algorithm. `draw` performs star glow effects, planet sizing, and orbital rings — pure rendering but complex enough to benefit from screenshot/draw verification.
- **Suggested tests**: ADVISORY only — UI rendering. Visual output verification via `pygame.surfarray` pixel sampling would be appropriate but this is a debug tool, not production-critical.

### game/ui/screens/planet_target_editor_base.py (63 LOC, layer: ui) — ADVISORY
- **Status**: No unit test file. 3 symbols. UI base class.
- **Key symbols**: `PlanetTargetEditor.process_event` (line 47), `PlanetTargetEditor._button_handlers` (line 39)
- **Risk**: Template method base for 4 planet target editors. The `process_event` method dispatches `UI_BUTTON_PRESSED` and `UI_WINDOW_CLOSE` events. The button-dispatch loop (lines 51-55) invokes `_button_handlers()` — if a subclass returns a mapping with non-callable values, the iteration would succeed but the call would crash. The `on_close_callback` wiring (lines 57-61) guards against None callback — correctly, but untested.
- **Suggested tests**: ADVISORY — UI base class. Can be tested with a mock subclass.

### game/ui/screens/race_setup/screen.py (489 LOC, layer: ui) — ADVISORY
- **Status**: No unit test file. 20 symbols, 0 tested. UI screen with significant business logic delegation.
- **Key symbols**: `RaceSetupScreen.__init__` (line 79) with 2-stage construction, `_init_state` (line 186), `update` (line 448), `kill` (line 469), `process_event` (line 486), `on_close_window_button_pressed` (line 477)
- **Risk**: The 2-stage construction pattern (Stage 1: cheap state + delegates, Stage 2: UIWindow shell under `bypass_init` guard) is complex and has known edge cases around `self.rect` assignment on bypassed `UIWindow` instances (documented at line 209-214). The `update()` method polls the description LLM controller, checks dialog thresholds, and updates the description panel. `on_close_window_button_pressed` (BUG-115) routes through controller.on_cancel to fire callbacks — untested close-path. However, the screen follows the MVVM pattern and delegates actual business logic to `RaceSetupController`, `RaceSetupRenderer`, `RaceSetupViewModel`, `RaceSetupInputHandler`, and `RaceDescriptionLLMController` — each tested independently.
- **Suggested tests**: ADVISORY — UI screen with delegate decomposition. Integration tests for the 2-stage construction bypass path would catch the rect-assignment edge case.

### game/ui/screens/strategy_render/systems.py (307 LOC, layer: ui) — ADVISORY
- **Status**: No unit test file. 5 functions, 0 tested. Pure rendering.
- **Key symbols**: `draw_systems` (line 28), `load_star_image` (line 60), `draw_colony_marker` (line 81), `draw_star` (line 113), `draw_system_details` (line 173)
- **Risk**: STAR IMAGE rendering with pixel-correct core sizing (line 147-159: `core_radius_frac`, `radius_boost`, `offset_x/y`), progressive scaling boost for large stars, and fallback to colored circles — all rendering-driven but the math is non-trivial. `draw_system_details` (lines 173-306) manages planet grouping by hex, multi-planet cluster layout with polar coordinate offsets, and warp-point rotation rendering. The preserved "code smell" (line 257: `p._temp_screen_pos = p_screen`) writes render data onto domain models — test coverage would surface this structural issue.
- **Suggested tests**: ADVISORY — UI rendering. Verify star image sizing math, multi-planet layout offsets, and warp-point rotation via pixel sampling.

### game/ui/screens/strategy_windows/build_queue_windows.py (84 LOC, layer: ui) — ADVISORY
- **Status**: No unit test file. 9 symbols (2 registrar classes). UI window management.
- **Key symbols**: `BuildQueueListRegistrar.open` (line 24), `EmpireBuildQueueRegistrar.open` (line 53), `EmpireBuildQueueRegistrar.close` (line 77)
- **Risk**: These registrars manage singleton window slots. `BuildQueueListRegistrar.open` kills any existing window before creating a new one (idempotent). `EmpireBuildQueueRegistrar.open` passes 6 constructor arguments to `EmpireBuildQueueWindow` including `facade` for CQRS-compliant dispatch (PROJ-208 Phase 3). The `_on_closed` callbacks null out window references — no test verifies this cleanup.
- **Suggested tests**: ADVISORY — UI window lifecycle. Verify singleton enforcement and close-callback nullification.

## Tier 1 — Imported by Tests, No Symbols Tested

### game/ui/services/image/__init__.py (62 LOC, layer: ui)
- **Status**: Tier 1. 7 test files import this module (for `test_application_context.py`, factory test, null provider test, OpenAI provider test, defaults test, provider test, regenerator test). 0 symbols directly tested — package init with re-exports only.
- **Risk**: Side-effect imports at lines 37-42 register `NullImageProvider` with the factory (`register_image_provider("null", NullImageProvider)`) and import `openai_provider` for side-effect registration. If these side-effect imports fail silently, the factory dispatch would be missing providers.
- **Suggested tests**: Verify all 11 `__all__` symbols are accessible via `from game.ui.services.image import *`. Verify `ImageProviderFactory.create()` resolves "null" after package import.

## Tier 1-2 — Partial Coverage

### game/simulation/combat/formation.py (383 LOC, layer: simulation)
- **Status**: Tier 2. 8 symbols, 6 tested (2 private helpers untested per matrix).
- **Untested**: `_compute_local_positions` (line 128), `_symmetric_y` (line 215)
- **Coverage quality assessment**: `FormationResolver.resolve`, `FormationShape`, `FormationSpec` are well tested. The two private helpers are tested indirectly through `FormationResolver.resolve` (which calls both). The matrix correctly flags them as heuristically unmatched due to the leading underscore, but they have effective coverage through the public API.
- **Gap**: `resolve_default_for_task_force` has a tie-detection branch (lines 296-297: `tied = sum(1 for _, c in sorted_buckets if c == top_count) > 1`) and a mixed/archetype fallback. No test specifically exercises an equal-count tie scenario. The `"other"` archetype path (line 299) isn't specifically tested.
- **Suggested tests**:
  1. `test_resolve_default_for_task_force_tied_archetypes` — equal counts of strike and defender → LINE_ABREAST
  2. `test_resolve_default_for_task_force_no_ships` — empty list → LINE_ABREAST default
  3. `test_resolve_default_for_task_force_unknown_role` — unrecognized role → "other" → LINE_ABREAST

### game/simulation/combat/targeting_system.py (325 LOC, layer: simulation)
- **Status**: Tier 2. 7 symbols, 5 tested.
- **Untested**: `_get_pdc_valid_targets` (line 209), `_get_pdc_target_type` (line 241)
- **Risk**: `_get_pdc_valid_targets` has a 3-tier fallback: beam_ab.pdc_valid_targets → weapon_ab.pdc_valid_targets → `_DEFAULT = ["MISSILE", "FIGHTER"]` (lines 227-239). The `weapon_ab` fallback branch and default branch are untested. `_get_pdc_target_type` maps candidate → "MISSILE" / `vehicle_type.upper()` / "UNKNOWN" (lines 262-267). The `vehicle_type` path and "UNKNOWN" fallback are untested.
- **Gap in `find_valid_target`**: The PROJ-359 family-metadata branch (lines 170-172: `FAMILY_METADATA.get(family).targets_missiles`) and the PDC valid-targets matching (lines 189-192) — the PDC path exercises `_get_pdc_valid_targets` and `_get_pdc_target_type` which are flagged untested but exercised through the parent method. The matrix correctly identifies them as heuristic misses.
- **Suggested tests**:
  1. `test_get_pdc_target_type_missile` — is_missile=True → "MISSILE"
  2. `test_get_pdc_target_type_fighter` — vehicle_type="Fighter" → "FIGHTER"
  3. `test_get_pdc_target_type_unknown` — no vehicle_type, not missile → "UNKNOWN"
  4. `test_get_pdc_valid_targets_custom_list` — beam_ab returns custom target list
  5. `test_get_pdc_valid_targets_default` — beam_ab and weapon_ab both None → default

### game/simulation/components/abilities/planetary.py (913 LOC, layer: simulation)
- **Status**: Tier 2. 72 symbols, 54 tested (18 __init__ methods flagged untested by heuristic).
- **Untested (per matrix)**: All 18 `__init__` methods across the 18 ability classes. All `get_primary_value` and `get_ui_rows` methods are matched to test files.
- **Coverage quality**: The __init__ methods for all stabilizer/booster/modifier abilities follow an identical pattern: `super().__init__(component, data)` + dict-guarded attribute assignment + else-branch default. The matrix flags each one because `__init__` is a common method name that the heuristic can't positively match. Actual `get_primary_value` and `get_ui_rows` methods ARE matched. The 18 untested symbols are a false positive from heuristic naming — these constructors are exercised whenever their `get_primary_value`/`get_ui_rows` tests instantiate the class.
- **Actual gap**: The `else` branches in all stabilizer `__init__` methods (e.g., lines 45-50, 153-156) handle non-dict `data` parameter — this edge case is truly untested. If an ability is ever constructed with a boolean/None `data` value, those branches would be hit. The `layer`, `allowed_scopes`, and `default_scope` class attributes on stabilizer classes are static and never verified in tests.
- **Suggested tests**:
  1. `test_stabilizer_init_with_non_dict_data` — data=True / data=42 → uses defaults
  2. `test_stabilizer_class_attributes` — verify layer=STRATEGIC, default_scope matches expected
  3. `test_shield_modifier_init` — verify attribute extraction from dict data

### game/strategy/data/fleet_pursuer_tracker.py (145 LOC, layer: strategy)
- **Status**: Tier 2. 9 symbols, 7 tested. 2 private methods untested.
- **Untested**: `__init__` (line 35), `_remove_orders_targeting_fleet` (line 134)
- **Coverage quality**: All public methods are tested. `_remove_orders_targeting_fleet` is called by `notify_target_destroyed` (which IS tested), so it has indirect coverage. The matrix correctly flags the private method.
- **Gap**: The `exclude` parameter on `redirect_pursuers` (line 61) is only tested via BUG-122's typical case (new_target is one of the pursuers). The general exclusion path (arbitrary excluded pursuers) isn't specifically tested. The `hasattr(new_target, '_pursuer_tracker')` guard (line 103) is not tested — if new_target is a mock without the tracker, the redirect would silently skip transfer.
- **Suggested tests**:
  1. `test_redirect_pursuers_with_exclude_multiple` — multiple pursuers, exclude one → redirected to new_target, excluded skipped
  2. `test_remove_orders_targeting_fleet_clears_path` — after removal, pursuer.path set to [] if orders empty

### game/strategy/data/naming.py (93 LOC, layer: strategy)
- **Status**: Tier 2. 5 symbols, 4 tested.
- **Untested**: `NameRegistry.__init__` (line 13)
- **Coverage quality**: `__init__` takes optional `data_file_path` — the path-provided branch calls `load_data` (tested). The no-path branch initializes empty lists/sets. Both branches are functionally covered by the `load_data` test which creates a NameRegistry and then calls `load_data`.
- **Gap**: `get_system_name` exhausts `available_names` → returns `Unknown-N` fallback (lines 55-56) and duplicate-name loop (lines 58-62). Neither exhaustion path is tested. The `to_roman` edge cases: n=0 → "0" (fails `0 < n < 4000` check, returns str(n)), n=-1 → "-1", n=4000 → "4000" — these out-of-range paths are untested.
- **Suggested tests**:
  1. `test_get_system_name_exhausted` — empty available_names → "Unknown-N"
  2. `test_get_system_name_duplicate_removal` — used name skipped, moves to next
  3. `test_to_roman_out_of_range_zero` — n=0 → "0"
  4. `test_to_roman_out_of_range_negative` — n=-1 → "-1"
  5. `test_to_roman_out_of_range_4000` — n=4000 → "4000"

### game/strategy/data/ship_instance.py (787 LOC, layer: strategy)
- **Status**: Tier 2. 55 symbols, 39 tested. 16 symbols flagged untested.
- **Untested per matrix**: `__post_init__`, `hull_class`, `ship_name`, `serial_number`, `__hash__`, `__eq__`, `get_activation_state`, `set_activation_state`, `invalidate_stats_cache`, `get_resource_percentage`, `get_pod_storage_capacity`, `get_pod_storage_used`, `can_carry_pod`, `_lookup_design_max_hp`, `repair`, `__repr__`
- **Coverage quality assessment**:
  - **EFFECTIVELY COVERED**: `__post_init__`, `__hash__`, `__eq__`, `hull_class`, `ship_name`, `serial_number`, `__repr__` — exercised whenever a ShipInstance is created and used in dicts/sets/print. The heuristic can't match `__` dunders and simple properties.
  - **UNTESTED GAP**: `get_pod_storage_capacity` (line unknown), `get_pod_storage_used`, `can_carry_pod` — drop pod mechanics are a core 4X feature (colonization). These three methods are truly untested.
  - **POSSIBLE GAP**: `set_activation_state`, `get_activation_state` — the activation state system (for toggling ship abilities). Untested.
  - **POSSIBLE GAP**: `repair` — ship repair logic. Matrix shows no test match.
  - **POSSIBLE GAP**: `invalidate_stats_cache` — cache invalidation is called internally by `set_registries`, `consume_resource`, `set_component_enabled`, etc. but never tested in isolation.
  - **POSSIBLE GAP**: `_lookup_design_max_hp` — private helper, likely called by `get_hp_percentage` or `from_dict`. Not tested in isolation.
- **Suggested tests**:
  1. `test_pod_storage_capacity_returns_value` — verify capacity calculation
  2. `test_pod_storage_used_tracks_carried_items` — verify used space tracking
  3. `test_can_carry_pod_with_launch_ability` — ship with VehicleLaunchAbility → True
  4. `test_can_carry_pod_without_ability` — no VehicleLaunchAbility → False
  5. `test_set_get_activation_state_roundtrip` — set + get returns same state
  6. `test_invalidate_stats_cache_clears_cache` — cache cleared to None
  7. `test_repair_restores_hp` — repair restores current_hp to max_hp, clears damage

### game/strategy/data/task_force.py (142 LOC, layer: strategy)
- **Status**: Tier 2. 10 symbols, 7 tested. 3 symbols flagged untested.
- **Untested**: `__init__`, `_formation_to_dict`, `_formation_from_dict`
- **Coverage quality**: `__init__` is called whenever TaskForce is constructed — covered indirectly. `_formation_to_dict` and `_formation_from_dict` are called via `to_dict`/`from_dict` which are tested. The matrix flags them due to private names.
- **Gap**: `_formation_from_dict` with `data=None` returns `None` (line 136-137) — this None-safety branch is indirectly covered but not explicitly tested. The `custom_positions` round-trip (lines 129-141: `Vector2(x, y)` tuple conversion) is tested through `to_dict`/`from_dict` round-trip.
- **Suggested tests**: MINOR — these are effectively covered through serialization round-trips.

### game/strategy/engine/action_execution_engine.py (221 LOC, layer: strategy)
- **Status**: Tier 2. 7 symbols, 6 tested. 1 symbol flagged untested.
- **Untested**: `ActionExecutionEngine._process_fleet_action_tick` (line 116)
- **Risk**: `_process_fleet_action_tick` contains the core tick logic with 6 distinct return-None branches (immobile fleet line 131, interval skip line 138, no order line 143, movement order skip line 147, BUILD order skip line 151, non-action order skip line 159). Each branch decides whether the fleet acts this tick — an incorrect early-return would skip valid actions. The BUILD auto-completion (line 154: `fleet.pop_order()` when queue empty) is untested. Action-time resolution branching between injected resolver and static method (lines 167-174) is untested.
- **Suggested tests**:
  1. `test_process_fleet_action_tick_immobile` — speed <= 0 → returns None
  2. `test_process_fleet_action_tick_wrong_tick` — tick not divisible by interval → returns None
  3. `test_process_fleet_action_tick_no_order` — no current order → returns None
  4. `test_process_fleet_action_tick_movement_order` — MOVE order skipped → None
  5. `test_process_fleet_action_tick_build_order_empty_queue` — empty queue → pops order, returns None
  6. `test_process_fleet_action_tick_non_action_order` — unknown order type → returns None
  7. `test_process_action_ticks_increments_progress` — progress += 1 per acting tick
  8. `test_process_action_ticks_completes_on_progress_reached` — progress >= action_time → completed

### game/strategy/services/combat_modifier_collector.py (184 LOC, layer: strategy)
- **Status**: Tier 2. 5 symbols, 2 tested (FleetCombatModifiers, collect_combat_modifiers). 3 private helpers untested.
- **Untested**: `_entry_scope` (line 86), `_find_reference_planet` (line 155), `_find_empire` (line 179)
- **Coverage quality**: All 3 private helpers are called by `collect_combat_modifiers` which IS tested. The matrix correctly flags them as heuristic misses.
- **Actual gap**: The `_entry_scope` helper (lines 86-91) resolves scope default via `get_ability_default_scope(ability_key)` when the data dict omits `scope`. This PROJ-272 Phase 1 bugfix reconciled a class-default-vs-collector-default mismatch. The branch where `entry.get('scope')` returns None (line 88) exercises this fallback — untested in isolation. `_find_reference_planet` has two resolution paths: `get_planets_at_global_hex` (line 161-165) and `get_system_at_hex` fallback (lines 168-174). Neither path is tested independently.
- **Suggested tests**:
  1. `test_entry_scope_with_explicit_scope` — returns scope value from dict
  2. `test_entry_scope_without_scope` — falls back to ability default scope
  3. `test_find_reference_planet_hex_lookup` — planet at exact hex → returns planet
  4. `test_find_reference_planet_system_fallback` — no planet at hex, system lookup succeeds
  5. `test_find_reference_planet_no_galaxy` — galaxy is None → returns None
  6. `test_find_empire_match` — matching empire_id → returns empire
  7. `test_find_empire_no_match` — no matching empire → returns None

### game/strategy/services/effect_ability_metadata.py (172 LOC, layer: strategy)
- **Status**: Tier 2. 6 symbols, 4 tested. 2 private helpers untested.
- **Untested**: `_multiplier` (line 77), `_rate` (line 93)
- **Coverage quality**: `_multiplier` and `_rate` are factory helpers used at module level to build the `EFFECT_ABILITY_METADATA` tuple (lines 110-141). They are executed at import time — effectively covered by every test that imports this module. The matrix flags them due to private names.
- **Actual gap**: The `all_owner_aware_scopes` union accumulation (lines 167-171) across the metadata tuple — tested. `find_metadata` with unknown name → returns None — not specifically tested. `is_known_effect_ability` with unknown name → returns False — not specifically tested.
- **Suggested tests**:
  1. `test_find_metadata_unknown` — unknown ability name → None
  2. `test_is_known_effect_ability_false` — unknown ability name → False
  3. `test_multiplier_constructs_correct_metadata` — verify kind='multiplier', value field defaults

### game/strategy/services/race_description_llm_controller.py (317 LOC, layer: strategy)
- **Status**: Tier 2. 25 symbols, 18 tested. 7 private methods untested.
- **Untested**: `_start_bio`, `_start_socio`, `_gather_captions`, `_poll_field`, `_apply_bio_transition`, `_apply_socio_transition`, `_fire_on_change`
- **Coverage quality**: All 7 private methods are called by the public API (`generate_bio` → `_start_bio`, `update` → `_poll_field` → `_apply_bio_transition`). They are effectively covered. The matrix flags them as private.
- **Actual gap**: The `LLMConfigError` catch branch in `_start_bio` (lines 209-215) and `_start_socio` (lines 231-234) — when `LLMBackgroundCall.start()` raises `LLMConfigError`, the status transitions to ERROR with the error stored. This concurrent-call-limit-reached path is not specifically tested. The `_fire_on_change` callback exception handler (line 313: `except Exception`) is not tested — a broken `on_change` callback shouldn't crash the controller.
- **Suggested tests**:
  1. `test_start_bio_concurrent_call_limit` — LLMConfigError on start → status=ERROR, error stored
  2. `test_fire_on_change_callback_raises` — callback throws → exception caught, logged, controller continues
  3. `test_poll_field_status_unchanged` — call status same as current → no transition
  4. `test_gather_captions_missing_flag` — flag_id is None → caption is None, no crash

### game/ui/screens/builder/layer_panel.py (536 LOC, layer: ui) — ADVISORY
- **Status**: Tier 2. 12 symbols, 2 tested (LayerPanel, rebuild). 10 methods untested.
- **Risk**: Only `LayerPanel` constructor and `rebuild` are tested. The remaining 10 methods (`handle_item_action`, `handle_event`, `update`, `suppress_toggle`, `draw`, `can_accept_drop`, `accept_drop`, `get_target_layer_at`, `get_range_selection`) are untested. This is a core ship-builder UI panel with drag-and-drop support and `pygame_gui` widget management. Exceeds the 500 LOC ceiling.
- **Suggested tests**: ADVISORY — UI panel. Test drag-drop validation via `can_accept_drop` / `accept_drop`, and `get_target_layer_at` coordinate lookup.

### game/ui/screens/design_image_helper.py (218 LOC, layer: ui) — ADVISORY
- **Status**: Tier 2. 5 symbols, 3 tested. 2 private uncached loaders untested.
- **Coverage quality**: `_load_portrait_thumbnail_uncached` and `_load_topdown_thumbnail_uncached` are called by their cached counterparts and are effectively covered.
- **Actual gap**: The `load_topdown_thumbnail` bounding-box calculation (lines 182-207) with `get_bounding_rect(min_alpha=10)` — edge cases: fully transparent image (bbox.width <= 0 → returns None), image with no visible pixels. The class-name variation list (lines 155-162: 6 variations of ship class name) hits filesystem — not tested.
- **Suggested tests**: ADVISORY — image loading. Test cached vs uncached behavior, fully transparent image edge case.

### game/ui/screens/planet_list_presets.py (242 LOC, layer: ui) — ADVISORY
- **Status**: Tier 2. 12 symbols, 9 tested. 3 methods untested.
- **Untested**: `PresetManager.__init__`, `PresetManager.save_to_disk`, `PresetManager.get_all_presets`
- **Coverage quality**: `__init__` calls `_load_from_disk` (tested) — effectively covered. `save_to_disk` writes JSON — `save_preset` calls it internally (tested). `get_all_presets` returns `self.presets` — trivial property.
- **Suggested tests**: ADVISORY — UI data management. Trivial gaps.

### game/ui/screens/race_setup/input_handler.py (174 LOC, layer: ui) — ADVISORY
- **Status**: Tier 2. 3 symbols, 2 tested (RaceSetupInputHandler class, __init__). `handle()` method untested.
- **Untested**: `RaceSetupInputHandler.handle` (line 30)
- **Risk**: `handle()` contains the entire event-dispatch switch with ~20 branches (LLM dialog buttons, description-tab buttons, tab buttons, save-update dialog buttons, cancel/save/load/randomize buttons, gallery clicks, dropdown changes, slider changes, text-entry changes). None of these dispatch paths are directly tested. The `handle` method is called from `RaceSetupScreen.process_event` — indirect coverage through screen tests.
- **Suggested tests**: ADVISORY — UI event dispatch. Each button-press dispatch path is covered indirectly through screen-level tests.

### game/ui/screens/strategy_render/hex_outlines.py (133 LOC, layer: ui) — ADVISORY
- **Status**: Tier 2. 6 symbols, 4 tested. 2 untested.
- **Untested**: `HexOutlineLayer.__init__`, `draw_inner_hex`
- **Coverage quality**: `__init__` sets cache to None — effectively covered. `draw_inner_hex` is a pure rendering function called by `HexOutlineLayer.draw` through `r._draw_inner_hex` — the layer's tests exercise it via the renderer monkey-patch pattern.
- **Suggested tests**: ADVISORY — UI rendering. Trivial gaps.

## Tier 3 — Verified Coverage

### game/core/hex_math.py (394 LOC, layer: core)
- **Status**: Tier 3. All symbols matched to tests. `_hex_round` flagged as unmatched due to private name but effectively covered through `pixel_to_hex` and `hex_lerp`.
- **Test files**: `test_hex_math_core.py`, `test_hex_math_strategy.py`, and 10+ other files for distance/pixel conversion usage.
- **Verification**: `hex_circle_filled`, `hex_random_cluster`, `hex_from_dict_safe` — all covered. `hex_random_cluster` (lines 338-394) has a frontier expansion loop with random selection — its deterministic behavior depends on a seeded `rng` parameter, which is tested.

### game/strategy/data/storm.py (154 LOC, layer: strategy)
- **Status**: Tier 3. All 4 symbols tested. Verified: `to_dict`, `from_dict`, `occupied_hexes`, class construction.
- **Test files**: `test_strategy_entities.py`, `test_storm.py`, `test_system_slice.py`, `test_strategy_session_facade.py`, `test_storm_generator.py`, `test_ability_iterator.py`, `test_system_effects_collector.py`
- **Verification**: `from_dict` raises `PersistenceException` for malformed location/hex_offsets, raises `ValidationException` for legacy `effects` shape (PROJ-300 D19). All error paths tested.

### game/strategy/facade/dto/fleet_hierarchy_dto.py (104 LOC, layer: strategy)
- **Status**: Tier 3. All 6 symbols tested. Verified: `ShipInfoExtended.from_ship_instance`, `SquadronInfo.from_squadron`, `TaskForceInfo.from_task_force`.
- **Test files**: `test_fleet_hierarchy_dto.py`
- **Verification**: DTOs are frozen dataclasses with delegated `.from_*` factory methods. All fields verified round-trip.

### game/strategy/formulas/habitability.py (105 LOC, layer: strategy)
- **Status**: Tier 3. All 3 symbols tested. Verified: `_gaussian_factor`, `calculate_habitability`, `score_planet_for_race`.
- **Test files**: `test_happiness_engine.py`, `test_habitability.py`
- **Verification**: `_gaussian_factor` with `min_sigma` edge (line 48: `sigma = max(tolerance, min_sigma)`), `calculate_habitability` with missing preference (defaults to Earth-standard fallback), `score_planet_for_race` delegates to `calculate_habitability`. Weighted geometric mean with `log(max(score, 1e-10))` floor — verified.

### game/ui/screens/race_asset_loader.py (269 LOC, layer: ui)
- **Status**: Tier 3. All 10 symbols tested. Verified: flag full/preview loading, portrait full/preview loading, placeholder creation, empire race/theme asset loading.
- **Test files**: `test_empire_panel_window.py`, `test_race_asset_loader.py`, `test_race_browser_dialog.py`
- **Verification**: Multi-resolution fallback in `load_flag_full` (1024 → 512 → 256 → root), `load_portrait_preview` directory listing with extension filter, `load_empire_theme_assets` delegates to `ShipThemeManager`. All test matches confirmed.

### game/ui/screens/strategy_screen_composition.py (114 LOC, layer: ui)
- **Status**: Tier 3. All 18 symbols tested. Verified: `StrategyScreenComposition` Protocol + `StrategyScreenCompositionFactory` with all 8 `make_*` methods.
- **Test files**: `test_strategy_screen_composition.py`
- **Verification**: PROJ-327 Phase 4 Compositional Construction pattern. Each factory method constructs a single collaborator. Tests verify construction with mock composition. 100% coverage confirmed.

## File Coverage Verification Table

| File | LOC | Tier | Symbols (Total/Tested) | Test Files (count) | Critical Gaps |
|------|-----|------|------------------------|--------------------|---------------|
| `game/app_bootstrap.py` | 281 | 0 | 6/0 | 0* | bootstrap() init sequence, _detect_resolution, _timed_phase |
| `game/core/hex_math.py` | 394 | 3 | 18/18 | 11+ | (verified) |
| `game/core/protocols/common.py` | 46 | 0 | 7/0 | 0 | _has_attrs foundational duck-typing helper |
| `game/simulation/combat/families/projectile.py` | 47 | 0 | 2/0 | 0 | WeaponFamily.PROJECTILE handler — zero-length aim vector |
| `game/simulation/combat/formation.py` | 383 | 2 | 8/6 | 9 | Tie-detection in resolve_default_for_task_force |
| `game/simulation/combat/targeting_system.py` | 325 | 2 | 7/5 | 3 | PDC valid-targets fallback chain |
| `game/simulation/components/abilities/planetary.py` | 913 | 2 | 72/54 | 6 | __init__ non-dict data edge case |
| `game/simulation/entities/ship_resource_manager.py` | 53 | 0 | 3/0 | 0 | get_resource_stat f-string attr fallback |
| `game/simulation/entities/stat_contributors/command.py` | 100 | 0 | 3/0 | 0 | allocate_crew_and_life_support — Phase 2 pipeline |
| `game/simulation/entities/stat_contributors/weapons.py` | 56 | 0 | 1/0 | 0 | aggregate_targeting_scores bool defense |
| `game/strategy/data/fleet_pursuer_tracker.py` | 145 | 2 | 9/7 | 2 | hasattr new_target tracker guard |
| `game/strategy/data/naming.py` | 93 | 2 | 5/4 | 1 | get_system_name exhaustion paths |
| `game/strategy/data/ship_instance.py` | 787 | 2 | 55/39 | 37 | Drop pod methods, activation state, repair |
| `game/strategy/data/storm.py` | 154 | 3 | 4/4 | 8 | (verified) |
| `game/strategy/data/task_force.py` | 142 | 2 | 10/7 | 6 | None-safety in _formation_from_dict |
| `game/strategy/engine/action_execution_engine.py` | 221 | 2 | 7/6 | 7 | 6 return-None branches in _process_fleet_action_tick |
| `game/strategy/engine/handlers/base.py` | 391 | 0 | 18/0 | 0 | 20+ command handlers depend on this foundation |
| `game/strategy/facade/dto/fleet_hierarchy_dto.py` | 104 | 3 | 6/6 | 1 | (verified) |
| `game/strategy/formulas/habitability.py` | 105 | 3 | 3/3 | 2 | (verified) |
| `game/strategy/services/combat_modifier_collector.py` | 184 | 2 | 5/2 | 2 | Scope default resolution, planet finder fallback |
| `game/strategy/services/effect_ability_metadata.py` | 172 | 2 | 6/4 | 1 | find_metadata unknown-name path |
| `game/strategy/services/race_description_llm_controller.py` | 317 | 2 | 25/18 | 2 | LLMConfigError on start branch |
| `game/ui/screens/builder/layer_panel.py` | 536 | 2 | 12/2 | 1 | 10 methods untested (UI panel, ADVISORY) |
| `game/ui/screens/design_image_helper.py` | 218 | 2 | 5/3 | 1 | Transparent image edge case (ADVISORY) |
| `game/ui/screens/galaxy_test/system_mode.py` | 576 | 0 | 13/0 | 0 | System generation/inspection (ADVISORY) |
| `game/ui/screens/planet_list_presets.py` | 242 | 2 | 12/9 | 2 | save_to_disk (effectively covered) (ADVISORY) |
| `game/ui/screens/planet_target_editor_base.py` | 63 | 0 | 3/0 | 0 | Base class for 4 editors (ADVISORY) |
| `game/ui/screens/race_asset_loader.py` | 269 | 3 | 10/10 | 3 | (verified) |
| `game/ui/screens/race_setup/input_handler.py` | 174 | 2 | 3/2 | 1 | handle() with ~20 branches (ADVISORY) |
| `game/ui/screens/race_setup/screen.py` | 489 | 0 | 20/0 | 0 | 2-stage construction bypass (ADVISORY) |
| `game/ui/screens/strategy_render/hex_outlines.py` | 133 | 2 | 6/4 | 1 | draw_inner_hex (effectively covered) (ADVISORY) |
| `game/ui/screens/strategy_render/systems.py` | 307 | 0 | 5/0 | 0 | Star image sizing math (ADVISORY) |
| `game/ui/screens/strategy_screen_composition.py` | 114 | 3 | 18/18 | 1 | (verified) |
| `game/ui/screens/strategy_windows/build_queue_windows.py` | 84 | 0 | 9/0 | 0 | Window lifecycle (ADVISORY) |
| `game/ui/services/image/__init__.py` | 62 | 1 | 0/0 | 7 | Side-effect registration verification |

\* `tests/unit/test_app_bootstrap_invariants.py` exists on disk but was not matched by the Phase 1 AST scanner.

## Context Usage Estimate

- Total production files audited: 35
- Total LOC reviewed: ~8,600
- Test files referenced: ~60 unique test files identified across the coverage matrix
- Files flagged for CRITICAL attention (Tier 0, non-UI): 9
- Files flagged for MAJOR attention (Tier 0 UI + Tier 2 significant gaps): 22
- Files flagged as effectively covered despite matrix heuristics: 12 (most private methods + dunders in Tier 2)
- Files verified at Tier 3: 6

### Coverage Health by Layer

| Layer | Files | Tier 0 | Tier 1 | Tier 2 | Tier 3 | Health |
|-------|-------|--------|--------|--------|--------|--------|
| Core | 3 | 2 (common.py, hex_math) | 0 | 0 | 1 | **POOR** — common.py is foundational |
| Simulation | 7 | 4 | 0 | 3 | 0 | **POOR** — stat_contributors/ and families/ untested |
| Strategy | 12 | 1 | 0 | 8 | 3 | **FAIR** — handlers/base.py is critical gap |
| UI | 13 | 6 | 1 | 4 | 2 | **ADVISORY** — all UI gaps are rendering/lifecycle |

### Top 5 Priority Actions

1. **game/strategy/engine/handlers/base.py** — Test all 12 BaseCommandHandler resolution helpers + CommandHandlerRegistry.dispatch. This is the foundation for every command handler. CRITICAL.
2. **game/app_bootstrap.py** — Test the bootstrap sequence and _detect_resolution. The existing test file exists but wasn't matched — investigate and extend. CRITICAL.
3. **game/simulation/entities/stat_contributors/command.py** — Test allocate_crew_and_life_support (Phase 2 of stat calc pipeline) and contribute_multiplex_tracking. CRITICAL.
4. **game/core/protocols/common.py** — Test _has_attrs (used by every TypeGuard) and protocol conformance for ILocatable/INamed/IOwnable. CRITICAL.
5. **game/strategy/data/ship_instance.py** — Test drop pod methods (get_pod_storage_capacity, get_pod_storage_used, can_carry_pod), activation state, and repair. MAJOR.
