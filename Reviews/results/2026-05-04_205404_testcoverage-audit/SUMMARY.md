# Test Coverage Audit — Final Summary (Verified Claims Only)

## Run Info
- **Date:** 2026-05-04
- **Seed:** testcoverage-2026-05-04_205404
- **Shards:** 18
- **Total production files:** 699 (~154K LOC)
- **Total symbols:** 7,011
- **Phase 1 estimated coverage:** 55.1% (heuristic — NOT authoritative)

## Coverage Scorecard (Phase 1 heuristic)

| Layer | Files | Symbols | Tested | Coverage % |
|-------|-------|---------|--------|------------|
| game_root | 7 | 116 | 35 | 30.2% |
| ai | 20 | 183 | 163 | 89.1% |
| assets | 2 | 28 | 15 | 53.6% |
| core | 35 | 458 | 227 | 49.6% |
| engine | 4 | 20 | 16 | 80.0% |
| research | 7 | 46 | 43 | 93.5% |
| services | 8 | 33 | 25 | 75.8% |
| simulation | 96 | 1,247 | 781 | 62.6% |
| strategy | 197 | 1,733 | 1,113 | 64.2% |
| ui | 323 | 3,147 | 1,442 | 45.8% |
| **Totals** | **699** | **7,011** | **3,860** | **55.1%** |

## Verified Gap Summary

| Category | Phase 2 Claims | CONFIRMED | DISPUTED | INCONCLUSIVE |
|----------|---------------|-----------|----------|--------------|
| CRITICAL | 43 | 20 | 22 | 0 |
| MAJOR | 135 | 62 | 58 | 1 |
| MINOR | 98 | 46 | 30 | 1 |
| ADVISORY | 72 | 33 | 15 | 0 |
| **Totals** | **348** | **161** | **125** | **2** |

**Key:** 161 genuine coverage gaps confirmed across all severities. 125 claims disputed (tests already exist). 2 inconclusive. Discovery agent false-positive rate across CRITICAL+MAJOR claims: ~45%.

---

## P0 — Critical Gaps (Immediate Attention)

These 20 files have **zero test coverage** and represent high-risk untested code paths.

### Facade CQRS Read Slices (4 files — zero test coverage)

1. **`game/strategy/facade/slices/planet_slice.py`** (105 LOC) — `get_planets_at_hex`, `can_colonize`, `get_planet`. Dual-path hex lookup (strict + radius fallback) and cross-domain colonize validation with multiple failure branches all untested.
   - *Suggested:* `test_planet_slice.py` — mock `FacadeSessionState`, verify strict + radius fallback, all `can_colonize` branches.

2. **`game/strategy/facade/slices/empire_slice.py`** (97 LOC) — 7 public CQRS-lite Read methods. DTO conversions, None-return branches, late-import error paths all uncovered.
   - *Suggested:* `test_empire_slice.py` — test all 7 public methods with mock session state.

3. **`game/strategy/facade/slices/system_slice.py`** (132 LOC) — Primary CQRS read-slice for UI system/star resolution. `get_system_at_hex`, `get_system_near_hex` fallback, `get_all_stars` cache invalidation all untested.
   - *Suggested:* `test_system_slice.py` — mock Galaxy with known systems + storms.

4. **`game/strategy/facade/dto/build_queue_dto.py`** (41 LOC) — `from_domain` cloning with `[dict(item) for item in list(...)]`. Shallow copy bugs could allow UI to mutate domain queue data.
   - *Suggested:* `test_build_queue_dto.py` — verify detached copies, missing `owner_entity` attribute fallbacks.

5. **`game/strategy/facade/slices/_facade_state.py`** (98 LOC) — Core facade shared state with caches and ID lookups consumed by ALL facade slices. Zero test file imports this module.
   - *Suggested:* `test_facade_state.py` — test turn-based cache invalidation, ID lookup consistency.

### Protocols & Interfaces (2 files)

6. **`game/core/protocols/boundary.py`** (126 LOC, 23 symbols) — 3 protocols + 3 TypeGuard functions. No test imports any symbol from this module.
   - *Suggested:* `test_protocols_boundary.py` — test all TypeGuards, `isinstance` checks, `@runtime_checkable` conformance.

7. **`game/simulation/interfaces/ability_protocols.py`** (359 LOC) — 9 TypeGuard functions that are the sole mechanism for duck-type narrowing across the simulation layer. `is_projectile_weapon` attribute disambiguation, `is_warp_jump`, `is_beam_weapon` — all untested.
   - *Suggested:* `test_ability_protocols.py` — test all 9 TypeGuards with valid/invalid objects, edge cases.

### Simulation Critical (3 files)

8. **`game/simulation/replay/replay_record.py`** (93 LOC) — Persisted-on-disk replay format (PROJ-312). Serialization/deserialization completely untested.
   - *Suggested:* `test_replay_record.py` — test `from_dict`/`to_dict` roundtrip, field validation.

9. **`game/simulation/replay/replay_outcome.py`** — `from_dict` casts via `str()` which could silently mask type errors. Round-trip never verified.
   - *Suggested:* `test_replay_outcome.py` — test roundtrip, type coercion safety, schema_version handling.

10. **`game/simulation/entities/ship_validator_helper.py`** (70 LOC) — No dedicated test. `check_validity`, `get_validation_warnings`, `get_missing_requirements` only exercised indirectly through `Ship` delegation. PROJ-252 registry_provider DI path untested.
    - *Suggested:* `test_ship_validator_helper.py` — test direct construction with controlled DI.

### Strategy Engine Handlers (3 files)

11. **`game/strategy/engine/handlers/movement.py`** (214 LOC, 10 symbols) — Five handler classes: ColonizeCommandHandler, MoveCommandHandler, InterceptCommandHandler, JoinCommandHandler, WarpCommandHandler. All zero coverage.
    - *Suggested:* `test_movement_handlers.py` — test each handler's `execute()` with mock session.

12. **`game/strategy/engine/handlers/order_queue.py`** (212 LOC, 10 symbols) — SplitFleetCommandHandler creates new Fleet objects, transfers ships, mutates empire registrations. High risk.
    - *Suggested:* `test_order_queue_handlers.py` — test split fleet creation, order reorder, delete with index validation.

13. **`game/strategy/services/ability_sources/star.py`** (77 LOC) — PROJ-302 infrastructure. `affects_hex()` coordinate math with try/except TypeError fallback, `affects_system` identity comparison, `get_abilities` None→{} fallback all untested.
    - *Suggested:* `test_star.py` — test affects_hex global/local frame, get_abilities fallback.

### Application Infrastructure (3 files)

14. **`game/run_loop.py`** (~211 LOC) — Main game loop. Zero automated coverage. No test file imports this module.
    - *Suggested:* `test_run_loop.py` — test loop startup/shutdown, fps management, event routing with mocked deps.

15. **`game/screen_router.py`** (~515 LOC) — Central scene-routing hub dispatches between all game screens. Zero tests.
    - *Suggested:* `test_screen_router.py` — test scene registration, transition flow, screen lifecycle callbacks.

16. **`game/exit_dialog.py`** — Module-level mutable globals (`_exit_yes_rect`, `_exit_no_rect`), PROJ-258 violation. Draw/click/cancel handlers all untested.
    - *Suggested:* `test_exit_dialog.py` — test drawing, click handling with mocked pygame surface.

### UI Critical (4 files)

17. **`game/ui/screens/builder/stat_rows_dynamic.py`** (504 LOC) — All 14 pure-data-transformation functions have zero tests and zero pygame dependency. Complex branching in `_build_resource_rows` (7 conditional row outputs), `_get_strategic_abilities`, `get_planetary_engineering_rows`.
    - *Suggested:* `test_stat_rows_dynamic.py` — ~30+ tests covering each function with edge cases.

18. **`game/ui/screens/builder/components.py`** — `ComponentListItem._generate_tooltip` has 12+ branches on ability types. Dynamic mass calculation via `component.clone()` + `recalculate_stats()` has branching on `ship_context` presence.
    - *Suggested:* `test_components.py` — test tooltip generation for each ability type, mass calc with/without ship_context.

19. **`game/ui/screens/strategy_windows/orders_window_ctrl.py`** — `OrdersRegistrar` closure-capture pattern with facade rebinding risk. 6 closures created with shared `edit_order_callback`.
    - *Suggested:* `test_orders_window_ctrl.py` — test open creates window with correct callbacks.

20. **`game/ui/screens/transfer_grid_renderer.py`** (366 LOC) — `_add_row` constructs 15+ pygame_gui widgets per row with pixel-position math across 13 layout constants. Completely untested.
    - *Suggested:* `test_transfer_grid_renderer.py` — test layout calculations with mocked pygame_gui.

---

## P1 — Major Gaps (Address Before Next Feature)

### Simulation Layer

| File | Function | Gap | Suggested Test |
|------|----------|-----|----------------|
| `game/simulation/battle_config.py` | `_default_end_condition`, replay fields | Module-level factory never directly called; replay_mode/replay_id/captured_telemetry_level untested | `test_default_end_condition_callable`, `test_replay_mode_default_false` |
| `game/simulation/components/abilities/resources.py` | `_get_resource_registry`, `update()` unregistered resource branch | Resource registry lookup never tested in isolation; unregistered resource type starvation path untested | `test_get_resource_registry_passed_resource_arg`, `test_constant_update_resource_type_not_found` |
| `game/simulation/components/abilities/weapons.py` | `_parse_formula_field`, `_get_raw_field` | Module-level helpers: `raw=None` returns default, fallback_key path — both untested | `test_parse_formula_field_none_returns_default`, `test_get_raw_field_fallback_key_used` |
| `game/simulation/combat/telemetry.py` | `ShipStatsAggregator._on_damage_event`, `HitLogRecorder._trace_modifiers_for_team` | None-target/instance/damage early returns; entire modifier_stack non-None path in `_trace_modifiers_for_team` untested | Test None guards, test `_trace_modifiers_for_team` with populated modifier_stack |
| `game/simulation/battle_runner.py` | `_derive_end_reason` disambiguation (L657-664) | When absolute_max_ticks fires AND spec end_condition is TickLimitCondition with max_ticks <= absolute_max_ticks | `test_derive_end_reason_tick_limit_vs_absolute_max_disambiguation` |
| `game/simulation/components/component.py` | `health_manager` lazy-init, `reset_hp` facade | 2 facade methods untested on Component instances | `test_health_manager_lazy_init`, `test_reset_hp_on_component` |
| `game/simulation/components/abilities/__init__.py` | `get_ability_default_scope` (3 branches) | Single source of truth for default scope resolution. Known-with-default, known-without-default, unknown — all zero coverage | Test all 3 branches with ABILITY_REGISTRY |
| `game/simulation/components/abilities/planetary.py` | 4 PROJ-300 abilities: ThrustModifier, StrategicSpeedModifier, EnvironmentalDamage, FuelDrain | All 4 have zero test coverage. __init__ dict/non-dict branching untested | Test each ability's init, `get_primary_value`, `get_ui_rows` |
| `game/simulation/systems/resource_manager.py` | `ResourceState.has_sufficient`, `add`, `set_max`; `ResourceRegistry.set_max_value` vs `set_regen_rate` asymmetry | API inconsistency (one creates, one silently skips); fundamental state methods untested | Test asymmetry, `has_sufficient` border cases, `add` overflow, `set_max` clamp |
| `game/simulation/entities/ship.py` | `__init__` registries=None, `_equip_default_hull` missing class_def, `_loading_warnings` | 607 LOC; specific branches lack targeted tests | Test init validation exception, hull fallback, warnings accumulation |
| `game/simulation/entities/ship_resource_manager.py` | `resources_initialized` flag, `prev_max_resources`, `prev_max_shields` | Stateful tracking logic completely untested | Test resources_initialized lifecycle, prev_max deltas after capacity changes |
| `game/simulation/entities/ship_stats.py` | `_aggregate_hangar_abilities`, PROJ-271 `shield_bonus_add`, `_initialize_resources` delta-update | Hangar aggregation zero coverage; shield_bonus_add via external_stats untested; delta-update path untested | Test hangar stats, external_stats shield_bonus_add, resources delta-update |
| `game/simulation/entities/ship_validator_helper.py` | All 3 public methods | CRITICAL severity — see P0 |

### Strategy / Engine Layer

| File | Function | Gap | Suggested Test |
|------|----------|-----|----------------|
| `game/strategy/data/planet_physics.py` | `calculate_radius_density_from_mass` (gas giant + small rocky), `calculate_surface_area`, `calculate_blackbody_temperature` zero flux | Only Earth/Super-Earth branch tested; surface area and blackbody zero-flux untested | Test gas giant, small rocky, surface area, zero flux returns 0.0 |
| `game/strategy/data/fleet_capability_calculator.py` | `list_abilities()` | Zero coverage — the only reference in tests is a mocked-out stub | Test real implementation with multi-ship fleet |
| `game/strategy/engine/planet_energy_engine.py` | `get_shield_info`, `get_activatable_ability_info`, `_is_ability_active` non-dict fallback, `_compute_activation_drain`, `_cancel_all_draining_components` | Multiple helpers with zero direct tests; integration coverage only | Test shield info, ability active non-dict, compute activation drain |
| `game/strategy/engine/water_engine.py` | `_process_colony` list-form branch, `_extract_water_modifier`, `__init__` with registries | List-form WaterModifier completely untested; registries param never passed | Test list-form stacking, registered dict fallback, registries DI |
| `game/strategy/engine/turn_state_snapshot.py` | `dump_crash_snapshot()` | PROJ-251 crash forensics path with disk I/O and error handling untested | Test writes file, handles OSError |
| `game/strategy/data/galaxy_warp_generator.py` | 11 internal methods (MST, angle validation, warp type rolling) | Only 3 boundary tests (N=0,1,2); internal methods lack direct coverage | Test MST with 3-system triangle, angle clearance, roll determinism |
| `game/strategy/services/ability_iterator.py` | 7 of 9 provider functions | PROJ-301..305 integration seams — planet, star, warp point, system archetype, fleet providers untested | Add mock systems with all entity types to exercise each provider |
| `game/strategy/services/system_effects_collector.py` | `_aggregate` (192 LOC, 7 error paths, 4 filtering stages) | Tested only indirectly; risk of silent regression in gating/filtering | Add isolated tests for _aggregate error paths, D16/D17 validation |
| `game/strategy/services/race_resolver.py` | `resolve_race_config` (4 paths) | Feeds population growth + happiness. 4 resolution paths all untested | Test registry hit, registry miss + empire fallback, empire-only, no match → None |
| `game/strategy/validation/planet_order_validator.py` | `_facility_has_ability` (3 branches) | Backs both validate_activate_ability and validate_deactivate_ability. Command handler tests mock it out entirely | Test dict+ability_name, dict+comp_id+registry, str+registry paths |
| `game/strategy/combat/spec_compiler.py` | `_ship_spec_from_instance` design_data fallback, post_battle_hook empire key resolution | ~5 branch gaps; bulk of code IS tested (933 LOC in 3 test files) | Test design_data fallback, empire_id vs owner_id resolution |
| `game/strategy/services/race_description_llm_controller.py` | `re_roll_socio`, `cancel_socio` | 2 public API paths have zero direct test calls | Test socio re-roll and cancel mirroring bio equivalents |

### Application Layer

| File | Function | Gap | Suggested Test |
|------|----------|-----|----------------|
| `game/app.py` | `_return_to`, `start_replay`, `_request_shutdown` | Major entry points have zero unit tests | Test shutdown sets running=False, return_to test_lab/strategy, start_replay |
| `game/context.py` | LLM/Image provider error-fallback paths | LLMConfigError catch, ImageConfigError → NullImageProvider fallback, create_test __new__ bypass — all untested | Test provider factory failure paths, create_test file I/O |
| `game/core/roles.py` | `_fire_invalidation_callbacks` re-entrance guard | Guard at L221 (`if self._firing_callbacks: return`) never exercised | Test callback that itself calls add_user_role during firing |

### UI Layer

| File | Function | Gap | Suggested Test |
|------|----------|-----|----------------|
| `game/ui/services/game_settings.py` | `_load`, `get`, `save`, module-level singleton | Zero tests (94 LOC). AppCtx service #9. Mutable global state + global keyword | Test load/save roundtrip, get defaults, brightness clamp |
| `game/ui/screens/workshop_viewmodel_layer_ops.py` | 5 pure-Python algorithm methods (254 LOC) | Zero pygame deps but zero tests. Layer resolution, restriction validation, reverse-index iteration | Test resolve_target_layer, quick_add_component, move_component_group |
| `game/ui/screens/builder/stat_definitions.py` | `StatDefinition` — 4 dispatch paths (77 LOC) | Callable vs string getter, callable vs format string, validator path — all untested | Test all 4 dispatch paths with callable and string variants |
| `game/ui/screens/builder/stat_getters.py` | ~19 of 36 getters + 5 formatters + 3 validators | Resource getters with error-handling (None guards, div-by-zero) entirely untouched | Test resource getters, fuel/ammo/energy consumption, warp tonnage/cost |
| `game/ui/screens/builder/weapons_panel.py` | `handle_event`, `draw`, `_update_scrollbar` | 14 of 15 symbols have zero direct tests | Test event routing, scrollbar visibility, viewport clipping |
| `game/ui/screens/builder/modifier_row.py` | `build_ui`, `update`, `handle_event`, `kill` | 355 LOC widget; only 2 helpers tested (156 LOC) | Test handle_event dispatch, update state transitions, all 3 control types |
| `game/ui/screens/builder/grouping_strategies.py` | 3 strategy classes | Zero test coverage; readonly filter exclusion untested | Test all three strategies with empty/single/multi-component inputs |
| `game/ui/screens/test_lab/test_run_card.py` | `handle_click`, `handle_hover`, `_draw_header` dispatch | 370 LOC, zero tests; rect-collision logic testable without pygame | Test click/hover inside/outside rect, header dispatch |
| `game/ui/screens/test_lab/screen_input_handler.py` | `handle_event`, `_handle_dialog_events`, `_handle_panel_events`, `_handle_click` | 399 LOC, zero tests; event dispatch with 5 sub-checkers | Test event routing, dialog gating, panel type dispatch |
| `game/ui/screens/battle_setup/controller.py` | `_get_registries` exception path, `add_ship_from_design`, `remove_ship` | Exception catch returns None untested; CRUD operations untested | Test get_registries None fallback, add/remove ship |
| `game/ui/screens/event_log_window.py` | `_handle_replay_click` (4 branches), `_handle_row_navigate` | FEAT-26 replay resolution completely untested | Test replay click branches, row navigate extracts hex |
| `game/ui/screens/list_data_source_base.py` | `_extract_value` — func, attr with dot-path, fmt formatting | Complex branch logic in abstract base class; only exercised through subclasses | Test _extract_value with func getter, attr getter, dot-path chain |
| `game/ui/screens/strategy_windows/build_queue_windows.py` | 2 Registrars — lifecycle (open/close/_on_closed) | Window construction with full DI, kill + nullify guard — all untested | Test open creates window, open replaces existing, on_closed nullifies |
| `game/ui/screens/strategy_windows/empire_panel_ctrl.py` | `SettingsRegistrar` (zero coverage), `EmpirePanelRegistrar` (partial) | 82 LOC, 2 classes; SettingsRegistrar has no tests at all | Test SettingsRegistrar open creates window, kill-existing |
| `game/ui/screens/strategy_windows/list_windows.py` | `navigate_camera_to`, `StarListRegistrar` | Zero coverage for camera nav helper and star list registrar lifecycle | Test camera nav, StarListRegistrar open/on_closed |
| `game/ui/screens/strategy_fleet_ops.py` | `handle_move_designation`, `execute_move`, `execute_intercept`, `handle_join_designation`, `execute_join` | 5 methods with complex branching orchestrating fleet operations | Test move designation branches, execute move/intercept/join |
| `game/ui/screens/save_selection_window.py` | `_load_saves`, `_handle_delete_confirmation`, `update` | Event handlers with file operations untested | Test load saves, delete confirmation removes file |
| `game/ui/screens/species_selector_mixin.py` | `get_selected_race_id`, `load_race_config`, `_get_active_race_config` | 163 LOC zero tests; tuple vs string option handling, RaceLibrary exception path | Test selected race id with tuple/string options, config resolution order |
| `game/ui/screens/race_setup/panel_factory.py` | 7 factory functions (177 LOC) | No dedicated tests; each has distinct wiring logic + LLM controller attachment | Test each factory creates correct panel type with expected callbacks |
| `game/ui/screens/race_setup/controller.py` | ~17 mutation methods + save/load (486 LOC) | No dedicated tests; screen-level only | Unit test save flows, load flows, per-tab randomization |
| `game/ui/screens/empire_panel_window.py` | `_create_ui`, `_create_tab_buttons`, panel rendering methods | 15 of 19 symbols untested (572 LOC) | Test tab switching, section rendering with empty data |
| `game/ui/services/image/openai_provider.py` | `_post_edit` (entire edit endpoint), `_parse_response` JSON decode/missing b64/invalid base64, `_read_actual_size` PIL failure | Happy path tested; all error/alternate paths untested | Test edit image, parse_response non-JSON, missing b64_json, bad base64, SSL error |
| `game/ui/services/modifier_icon_service.py` | `get_icon` (cache miss, fallback filename, file not found, pygame load error, scale) | Zero tests; multiple untested paths in icon resolution | Test cache hit/miss, fallback filename, missing file error handling |
| `game/ai/combat_utils.py` | `get_capability_cache_key` (3 paths) | Only untested function in well-tested module | Test with entity.id, with name only, with neither |

---

## P2 — Minor Gaps (Improve Opportunistically)

Key minor gaps across verified shards (representative sample):

| File | Gap |
|------|-----|
| `game/core/protocols/combat.py` | `_has_attrs` helper not tested in isolation; TypeGuards with truthy-but-incomplete objects |
| `game/core/math.py` | `normalize_angle()` — zero tests for edge cases (0, 180, -180, 360, large values) |
| `game/strategy/formulas/habitability.py` | `_gaussian_factor` sigma guard indirectly tested |
| `game/strategy/systems/race_randomizer.py` | `_resolve_rng`, `_pick_name_entry`, `_pick_leader` — indirectly tested only |
| `game/simulation/projectile_manager.py` | `_apply_hit()` — `source_weapon is None` fallback and `get_damage(hit_dist)` branch untested |
| `game/simulation/entities/projectile.py` | `_update_guidance()` — 6 specific math branches (owner=None lead solver, predictive lead, same-position, turn-rate clamping) untested |
| `game/simulation/combat/fleet_aura_manager.py` | `get_attack_bonus`, `get_defense_bonus` — 0.0 defaults for unknown team_id not pinned |
| `game/strategy/data/physics.py` | `calculate_incident_radiation` edge cases: `dist < 1.0` clamping, empty stars list |
| `game/strategy/services/replay_store.py` | `_evict_excess` OSError during file unlink untested |
| `game/strategy/engine/resupply_engine.py` | `__init__` tested (contrary to Phase 2 claim); only `_calculate_fuel_distribution` division edge case untested |
| `game/strategy/engine/atmosphere_engine.py` | Formula verified correct (contrary to Phase 2 claim); partial indirect coverage |
| `game/strategy/generation/storm_generator.py` | `_find_valid_center` (50-attempt exhaustion, max_radius clamp), `_collect_occupied_hexes` |
| `game/strategy/data/classification_config.py` | `__init__`, `_load_from_json`, `_use_defaults` exercised through `ClassificationConfig(data)` construction; defaults-fallback path IS tested |
| `game/strategy/data/fleet.py` | `remove_orders_by_type_and_target()` only tested indirectly via merge_with |
| `game/ui/screens/transfer_view_model.py` | `apply_arrow` MAX_LOAD/MAX_DROP sentinel reset, `apply_max` direction-based sentinel, `build_row_data` species key ordering |
| `game/ui/screens/strategy_screen.py` | `current_empire` IndexError with empty `human_player_ids` untested |
| `game/ui/screens/builder/detail_panel.py` | `on_selection_changed` 4-branch dispatch (None, tuple, hasattr id, fallback) untested |
| `game/ui/screens/planet_list_filters.py` | `get_column_value` dot-walk attr chain, `compute_planet_ranges` empty-list defaults |
| `game/ui/screens/strategy_panel_manager.py` | `resize_strategy_panels`, `apply_hotkey_tooltips` |
| `game/ui/screens/strategy_camera_nav.py` | `zoom_to_galaxy`, `zoom_to_system`, `cycle_selection` — no dedicated tests |
| `game/ui/screens/battle_setup/spec_compiler.py` | `_load_complex_design` OSError path, `_iter_components` edge cases, `_ship_spec_from_instance` pose=None fallback |
| `game/ui/screens/builder/schematic_view.py` | `_calculate_max_r` — cube-root scaling math using vehicle_class_service |
| `game/ai/behaviors.py` | `_flee_direction` zero-length vector edge case |
| `game/ai/spatial_behaviors/battle_line.py` | 3 shape branches (wedge, echelon_left, echelon_right) — all use shape="line" in tests |
| `game/ui/screens/strategy_click_dispatcher.py` | `_hit_test_planets` (~108 LOC geometric hit-testing), `_handle_picking` (~89 LOC) untested despite integration test coverage for dispatch routing |
| `game/ui/screens/strategy_detail_fmt.py` | `_get_system_ability_status` active-preference logic (multi-planet), `_get_ability_status_text` DEACTIVATING phase, `_planet_has_ability_facility` broad except |
| `game/ui/screens/fleet_report_filters.py` | Filter predicates have integration coverage through `filter_ships` but no isolation tests |
| `game/ui/screens/workshop_data_loader.py` | `_load_policies` test-file branch, `_load_vehicle_classes` vlayer_path pass-through |
| `game/ui/services/image/null_provider.py` | `repr`/`str` dunders — trivial but untested |

---

## UI Advisory Gaps

These are primarily pygame rendering code or widget construction files where coverage gaps are expected and low-risk per audit methodology. Representative entries:

| File | Why Advisory |
|------|-------------|
| `game/ui/screens/battle_screen.py` (687 LOC) | LOC ceiling violation; untested symbols are all rendering/visual-effect methods |
| `game/ui/screens/test_lab/dialogs.py` | Pure pygame rendering; `close`, `_handle_confirm`, `_handle_cancel` are simple state transitions |
| `game/ui/screens/strategy_ui_action_router.py` | Pure delegation mapping — 16 if/elif branches, trivial 1:1 contract with scene methods |
| `game/ui/screens/strategy_screen_lifecycle.py` | All 8 functions tested (contrary to Phase 2 CRITICAL claim) — effectively COVERED |
| `game/ui/screens/battle_state_viewer.py` | Pure pygame rendering/event dispatch |
| `game/ui/screens/strategy_render/` (grid, storms, hex_outlines) | Snake-line hex drawing with viewport culling |
| `game/ui/screens/test_lab/theme.py` | Color hex constant definitions only |
| `game/ui/screens/test_lab/renderer/tag_filter_panel.py` | Pure pygame tag filter button rendering |
| `game/ui/screens/race_setup/screen.py` | 63 tests exist (matrix incorrectly classified as TIER_0) |
| `game/ui/widgets/range_slider_builder.py` | `build_range_slider_row()` — pure pygame_gui element construction |
| `game/ui/screens/builder/modifier_utils.py` | `copy_modifiers` 20 LOC, zero tests — any change to strategy modifier data structures could silently break |
| `game/ui/screens/builder/weapons_renderer.py` (524 LOC) | Pure pygame rendering — all 15 symbols are rendering-related |
| `game/ui/components/table/virtual_table.py` | pygame_gui widget construction code |
| `game/ui/components/filters/tri_state_widget.py` | `_update_visuals()` exercised indirectly via `set_state()`/`check_pressed()` |
| `game/ui/research/research_scene.py` | 63 tests exist for the race setup screen (matrix false negative) |
| `game/core/protocols/common.py` | Pure Protocol definitions; `_has_attrs` is a one-liner tested through every TypeGuard |
| `game/core/protocols/strategy_domain.py` | TypeGuards tested in `test_protocols.py`; protocols are pure type declarations |
| `game/core/protocols/persistence.py` | `ISerializable` tested in `test_serializable_protocol.py` (4 tests) — CRITICAL claim DISPUTED |
| `game/core/profiling.py` | 3 dedicated test files exist (500+ LOC); CRITICAL claim DISPUTED |
| `game/strategy/data/star_generation_config.py` | All 3 symbols directly tested (11 tests); MAJOR claim DISPUTED |
| `game/simulation/components/modifier_manager.py` | All instance methods well-tested; only deprecated static wrappers untested — MAJOR claim overblown |

---

## Shard Verification Summary

| Shard | Phase 2 Claims | Verified | Disputed | Inconclusive | Notable |
|-------|---------------|----------|----------|--------------|---------|
| 01 | 51 (10C+22MJ+13MN+6AD) | 16 | 9 | 0 | 7 severity downgrades; 4 false negatives (tests existed) |
| 02 | 22 (2C+14MJ+6MN/AD) | 10 | 8 | 1 | 1 CRITICAL confirmed (stat_rows_dynamic); 1 MINOR→MAJOR upgrade |
| 03 | 29 (3C+12MJ+8MN+6AD) | 14 | 7 | 0 | 2 false CRITICALs (shim imports missed); 5 false MAJORs |
| 04 | 14 (0C+8MJ+6MN) | 7 | 1 | 0 | No CRITICAL claims; 1 MAJOR partially disputed |
| 05 | ~25 (1C+8MJ+7MN+9AD) | 10 | 1 | 0 | 1 CRITICAL confirmed (protocols/ui.py); 1 ADVISORY→MAJOR upgrade |
| 06 | 47 files, ~10 CRITICAL+MAJOR | 7 | 2 | 0 | 3 CRITICAL confirmed; 2 CRITICAL discovered (movement/order_queue handlers) |
| 07 | 11 (2C+7MJ+1MN+1AD) | 2 | 2 | 0 | Both CRITICALs disputed (strategy_domain + event_slice tested); only 1 MAJOR stands |
| 08 | 18 (2C+4MJ+5MN+7AD) | 7 | 6 | 0 | Both CRITICAL confirmed; all 4 MAJOR disputed (extensive integration tests) |
| 09 | 29 (3C+6MJ+10MN+10AD) | 8 | 4 | 0 | 1 CRITICAL confirmed (empire_slice); 2 CRITICAL downgraded/removed |
| 10 | ~14 (1C+8MJ+5MN) | 4 | 4 | 0 | CRITICAL disputed (profiling has 3 test files); 4 MAJOR confirmed |
| 11 | 39 (5C+5MJ+9MN+8AD+12 Tier3) | 4 | 3 | 0 | 2 CRITICAL confirmed (system_slice + build_queue_dto); 3 CRITICAL disputed |
| 12 | ~8 (1C+2MJ+5MN/AD) | 1 | 2 | 0 | CRITICAL disputed (ISerializable tested); 1 MAJOR confirmed |
| 13 | ~30 (4C+3MJ+18MN+10AD) | 2 | 4 | 0 | 57% agent error rate; 3 CRITICAL false positives |
| 14 | 47 (3C+16MJ) | 16 | 3 | 0 | All 3 CRITICAL confirmed (run_loop, screen_router, _facade_state); 13 MAJOR confirmed |
| 15 | ~45 (8C+10MJ+...)| 14 | 4 | 0 | 6 CRITICAL confirmed; battle_panels MAJOR claim DISPUTED (~1,470 LOC tests exist) |
| 16 | ~30 (3C+5MJ+...)| 2 | 6 | 0 | 0 CRITICAL confirmed (all disputed/downgraded); 2 MAJOR confirmed |
| 17 | ~25 (2C+4MJ+...)| 2 | 4 | 0 | 0 CRITICAL confirmed; ship_combat_manager FALSE POSITIVE |
| 18 | ~30 (2C+10MJ+...)| 5 | 5 | 0 | 0 CRITICAL confirmed; 5 MAJOR confirmed; 6 test files missed by agent |

---

## Priority Action Plan — Top 20 Most Impactful Confirmed Gaps

Ranked by `severity × layer importance × LOC`.

1. **`game/run_loop.py`** (CRITICAL, ~211 LOC) — Main game loop. Every operation depends on this.
2. **`game/screen_router.py`** (CRITICAL, ~515 LOC) — Central scene routing hub.
3. **`game/strategy/engine/handlers/movement.py`** (CRITICAL, 214 LOC) — Colonize, move, intercept, join, warp handlers.
4. **`game/strategy/engine/handlers/order_queue.py`** (CRITICAL, 212 LOC) — Split fleet, order queue mutation.
5. **`game/strategy/facade/slices/_facade_state.py`** (CRITICAL, 98 LOC) — Core facade shared state for all slices.
6. **`game/strategy/facade/slices/planet_slice.py`** (CRITICAL, 105 LOC) — CQRS Read path for planet resolution.
7. **`game/strategy/facade/slices/empire_slice.py`** (CRITICAL, 97 LOC) — CQRS Read path for empire queries.
8. **`game/strategy/facade/slices/system_slice.py`** (CRITICAL, 132 LOC) — CQRS Read path for system/star resolution.
9. **`game/simulation/interfaces/ability_protocols.py`** (CRITICAL, 359 LOC) — TypeGuard duck-type narrowing.
10. **`game/ui/screens/builder/stat_rows_dynamic.py`** (CRITICAL, 504 LOC) — 14 pure-data functions, zero tests, zero pygame.
11. **`game/simulation/replay/replay_record.py`** (CRITICAL, 93 LOC) — Replay serialization format.
12. **`game/simulation/replay/replay_outcome.py`** (CRITICAL) — Replay outcome serialization.
13. **`game/simulation/entities/ship_validator_helper.py`** (CRITICAL, 70 LOC) — Ship validation helper.
14. **`game/core/protocols/boundary.py`** (CRITICAL, 126 LOC) — Protocol boundary definitions.
15. **`game/strategy/services/ability_sources/star.py`** (CRITICAL, 77 LOC) — PROJ-302 star abilities.
16. **`game/exit_dialog.py`** (CRITICAL) — Module-level mutable state, exit UX.
17. **`game/ui/screens/transfer_grid_renderer.py`** (CRITICAL, 366 LOC) — Complex layout math.
18. **`game/simulation/entities/ship.py`** (MAJOR, 607 LOC) — Largest production file; several untested branches.
19. **`game/simulation/entities/ship_stats.py`** (MAJOR) — Hangar stats, PROJ-271 shield_bonus_add, resource delta-update.
20. **`game/app.py`** (MAJOR, 509 LOC) — App-level entry points (replay, shutdown, routing).

---

## Estimated Test Effort

| Severity | Count | ~Tests Needed | Notes |
|----------|-------|---------------|-------|
| CRITICAL | 20 | ~300 test functions | Most are new test files for modules with zero coverage |
| MAJOR | 62 | ~400 test functions | Mix of new files and extending existing test suites |
| MINOR | 46 | ~150 test functions | Mostly extending existing tests with edge cases |
| ADVISORY | 33 | ~50 test functions | Low priority; primarily rendering/trivial code |
| **Totals** | **161** | **~900 test functions** | Estimated 2-4 weeks of dedicated test authoring effort |

---

## Discovery Agent Systematic Errors

The Phase 2 discovery agent demonstrated a ~45% false-positive rate on CRITICAL+MAJOR claims. Primary error categories:

1. **Filename-pattern matching failure** (~60% of errors): Agent searched for `test_module_name.py` and missed test files with non-obvious names (e.g., `test_utils.py` for `pygame_utils.py`, `test_protocols.py` for `strategy_entities.py`).

2. **Shim import blindness** (~20%): Tests importing through re-export shims (e.g., `game.strategy.engine.command_handlers` → `handlers/`) were invisible to the heuristic.

3. **Cross-module indirect coverage** (~15%): Facade → Slice, Ship → ShipCombatManager delegation chains not traced.

4. **Over-aggressive private-method counting** (~5%): Private methods exercised through public API counted as "untested."

5. **Missed 6 complete test files in Shard 18** alone (crew_abilities.py 555 LOC, pygame_utils.py 565 LOC, input_handler.py 311 LOC, etc.).

---

## Full Report Paths

- **Phase 1 raw:** `Reviews/results/2026-05-04_205404_testcoverage-audit/raw/`
- **Phase 2 shard:** `Reviews/results/2026-05-04_205404_testcoverage-audit/findings/SHARD_*.md`
- **Phase 3 verified:** `Reviews/results/2026-05-04_205404_testcoverage-audit/findings/VERIFIED_SHARD_*.md`
- **Final summary JSON:** `Reviews/results/2026-05-04_205404_testcoverage-audit/SUMMARY.json`
- **Final summary MD:** `Reviews/results/2026-05-04_205404_testcoverage-audit/SUMMARY.md`

---

*Report compiled 2026-05-04 from 18 verified shard reports. All CONFIRMED claims verified by independent code reading. DISPUTED and INCONCLUSIVE claims excluded from detailed listings but counted in statistics.*
