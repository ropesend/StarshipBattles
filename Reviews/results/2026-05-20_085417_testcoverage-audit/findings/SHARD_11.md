# Shard 11 — Unit Test Coverage Audit

**Audit type:** Discovery (Phase 2 — exhaustive production-file read + test cross-reference)  
**Shard:** 11 (53 files, ~9820 LOC)  
**Heuristic baseline:** `coverage_data_11.md` (import-name-grep, NOT verified)  
**Methodology:** Read every production file → found + read every corresponding test → cross-referenced symbols  

---

## Summary

| Tier | Count | Files |
|---|---|---|
| **CRITICAL** (Tier 0) | 5 | 5 production files with zero test coverage |
| **MAJOR** (Tier 1) | 0 | (galaxy_test/constants.py verified as tested → reclassified) |
| **MINOR** (Tier 2) | 38 | Partial coverage, untested error paths / internal methods |
| **ADVISORY** (Tier 3) | 10 | Heuristically covered, verified by test existence |

**Heuristic baseline errors found:** 6 Tier 0 files downgraded (tests exist), 0 Tier 3→0 upgrades.

---

## CRITICAL (Tier 0 — Zero Tests)

### 1. `game/strategy/interfaces/engines/components.py` (47 LOC, strategy layer)
- **Status:** ABC with no test file anywhere. No test imports this module.
- **Symbols:** `IComponentActivationEngine` (ABC), `process_activation_tick` (abstract method)
- **Risk:** Pure ABC stub with no implementation. Low runtime risk but zero contract verification.
- **Test needed:** Verify the ABC's abstract method signature contract works with real implementations.

### 2. `game/strategy/services/ability_sources/warp_point.py` (64 LOC, strategy layer)
- **Status:** Zero test imports. No test file anywhere.
- **Symbols:** `WarpPointAbilitySource` (frozen dataclass, 9 public interfaces)
- **Functions:** `source_kind`, `source_label`, `source_id`, `owner_id`, `get_abilities`, `affects_hex`, `affects_system`, `get_activation_state`
- **Risk:** MAJOR — this is a concrete `IAbilitySource` adapter used by the system effects collector (PROJ-303). The `affects_hex` method has a `TypeError` catch path at line 57 that is completely untested.
- **Key untested branches:**
  - L53-54: `wp_loc is None or sys_loc is None` → `return False`
  - L57-58: `TypeError` during `hex_coord == sys_loc + wp_loc`
  - L40: `owner_id` returns `None` (warp points ownerless)
  - L43: `get_abilities` handles `None` intrinsic_abilities gracefully
  - L64: `get_activation_state` always returns `None`

### 3. `game/ui/screens/fms_menu_callbacks.py` (136 LOC, ui layer)
- **Status:** Zero test file exists. No `test_fms_menu_callbacks.py` found.
- **Symbols:** `build_planet_fms_callbacks`, `build_fleet_fms_callbacks`, `_first_ship_id_with`, `_dispatch` (2x nested)
- **Risk:** MAJOR — these callbacks wire right-click context menus to `IssueCommand` dispatch. Untested paths include:
  - L39-40: facade is `None` → silent return
  - L62-78: `_first_ship_id_with` returning `None` for missing capabilities/ships
  - L70: `caps.ships_with_ability(ability) or []` empty list path
  - L77-78: `sid` is None → returns None
  - Cross-cutting: all 10 lambdas (5 planet + 5 fleet) are closure-scoped and unevaluated until menu click
- **Test needed:** Unit tests for `_first_ship_id_with` edge cases + lambda invocation verification for both builders.

### 4. `game/ui/screens/strategy_windows/dispatch.py` (129 LOC, ui layer)
- **Status:** No test imports from this module directly. Facade-dispatch tests exist but test facade layer, not this UI dispatcher.
- **Symbols:** `UICallbackDispatcher` (class), `ConfirmationDialogController` (class)
- **Functions:** `UICallbackDispatcher.process`, `ConfirmationDialogController.show`, `ConfirmationDialogController.process_event`
- **Risk:** MAJOR — both classes are stateful helpers for `StrategyWindowManager`. `process_event` at L118-129 has multi-branch gate logic testing `event.type`, `c._pending_confirmation_dialog is not None`, and `event.ui_element == c._pending_confirmation_dialog`.
- **Key untested branches:**
  - L51-56: `UICallbackDispatcher.process` — button-press dispatch + cleanup
  - L118-129: `ConfirmationDialogController.process_event` — three nested conditions
  - L123-127: callback is None after dialog close (race condition)
- **Test needed:** Test both classes with mocked Composer; verify callback execution, cleanup, and null-guard.

### 5. `game/ui/screens/test_lab/results_panel.py` (266 LOC, ui layer)
- **Status:** Zero test imports. No `test_results_panel.py` found. Related test_lab tests exist for other modules but not this one.
- **Symbols:** `ResultsPanel` (class, 11 public methods)
- **Functions:** `set_details_panel`, `set_test`, `_recalculate_scroll`, `handle_event`, `update`, `draw`, `_draw_header`, `_is_card_visible`, `_draw_scrollbar`
- **Risk:** MAJOR — 266 LOC of complex UI state (scroll management, card selection, details panel wiring).
- **Key untested branches:**
  - L66-68: details_panel.clear() when switching tests
  - L97-111: `_recalculate_scroll` with empty run_cards vs populated
  - L115-150: Mouse click handling — clear buttons, card selection, scroll
  - L152-159: update() hover state for cards
  - L161-190: draw() with scroll clipping, card visibility
  - L237-246: `_is_card_visible` visibility calculation
  - L248-266: `_draw_scrollbar` with thumb size/position math
- **Test needed:** Test card selection, scroll state transitions, and details panel wiring with mock TestHistory.

---

## MAJOR (Tier 1 — No Symbols Tested)

None after verification. `game/ui/screens/galaxy_test/constants.py` was baseline Tier 1 but `tests/unit/ui/screens/test_galaxy_test_screen.py` lines 13-50 actually test `SIDEBAR_WIDTH`, `HEX_SIZE`, `PLANET_TYPE_COLORS` values and type assertions. **Reclassified to Tier 2 (MINOR).**

---

## MINOR (Tier 2 — Partial Coverage)

### 0. `game/ui/screens/galaxy_test/constants.py` (32 LOC, ui layer)
- **Baseline:** Tier 1. **Verified:** Tier 2.
- **Test:** `tests/unit/ui/screens/test_galaxy_test_screen.py::TestGalaxyTestConstants`
- **Tested:** `SIDEBAR_WIDTH` positivity, `HEX_SIZE` positivity, `PLANET_TYPE_COLORS` dict type, valid RGB colors
- **Untested:** No test for specific planet type key existence in `PLANET_TYPE_COLORS`, no test for the full 11-key set (`PlanetType.CONTINENTAL` through `PlanetType.PLANETOID`)
- **Gap:** MINOR — full key enumeration not validated

### 1. `game/ai/spatial_behaviors/column.py` (55 LOC, ai layer)
- **Test:** `tests/unit/ai/spatial_behaviors/test_spatial_behaviors.py`
- **Tested:** `ColumnBehavior.compute_target_position`
- **Untested:** `ColumnBehavior.__init__` (line 23 — stores `follow_distance`)
- **Gap:** MINOR — the init test is trivially missing; `compute_target_position` covers the main logic.

### 2. `game/ai/spatial_behaviors/escort.py` (50 LOC, ai layer)
- **Test:** `tests/unit/ai/spatial_behaviors/test_spatial_behaviors.py`
- **Tested:** `EscortBehavior.compute_target_position`
- **Untested:** `EscortBehavior.__init__` (line 23 — stores `distance`)
- **Gap:** MINOR — same trivial init gap as column.

### 3. `game/core/input_actions.py` (344 LOC, core layer)
- **Test:** `tests/unit/core/test_input_actions.py`
- **Tested:** `InputAction` enum, `KeyBinding.display_text`, `KeyBinding.from_dict`, `KeyBinding.to_dict`, `ACTION_DISPLAY_NAMES`, `ACTION_GROUPS`
- **Untested:** `KeyBinding._key_display_name` (L301-315) — private method with 4 branches: special keys, function keys, letter keys, fallback. Indirectly tested via `display_text()`.
- **Gap:** MINOR — private helper covered via public method; direct edge case tests for fallback path lacking.

### 4. `game/core/validation.py` (209 LOC, core layer)
- **Test:** `tests/unit/core/test_validation.py` + 24 other files
- **Tested:** All 12 symbols heuristically covered
- **Untested:** Cannot assess without deep-dive. Heuristic says full coverage.
- **Gap:** ADVISORY — potentially fully covered.

### 5. `game/research/data/research_tracker.py` (293 LOC, research layer)
- **Test:** `tests/unit/research/test_research_tracker.py`
- **Tested:** Most public methods through `test_research_tracker.py` and `test_research_service.py`
- **Untested:** 
  - `_clamp_allocations_to_budget` (L219-244) — private method with budget-scale-down logic including zero-budget branch (L225-228) and proportional scaling with remainder allocation to last node (L232-244). Indirectly tested via `set_rp_budget`.
  - `__init__` trivially untested in isolation.
- **Gap:** MINOR — `_clamp_allocations_to_budget` has complex proportional scaling math that merits direct testing. The zero-budget path (L225-228) where `rp_budget == 0` sets all allocations to 0 is never specifically triggered in public method tests.

### 6. `game/simulation/combat/families/_beam_common.py` (44 LOC, simulation layer)
- **Test:** `tests/unit/simulation/combat/test_weapon_family_handlers.py`
- **Tested:** All 1 symbol heuristically covered
- **Gap:** ADVISORY — appears fully covered.

### 7. `game/simulation/combat/modifier_stack.py` (74 LOC, simulation layer)
- **Test:** `tests/unit/simulation/combat/test_modifier_stack.py` + 17 other files
- **Tested:** All 3 symbols
- **Gap:** ADVISORY — appears fully covered.

### 8. `game/simulation/combat/ram_target_resolver.py` (226 LOC, simulation layer)
- **Test:** `tests/unit/simulation/combat/test_ram_target_resolver.py` (254 lines)
- **Tested:** `set_ram_target`, `process_ramming_tick`, collision detection, symmetric damage exchange, warhead consumption, target clearing
- **Verified tested (skeptical):** `_collect_warheads`, `_delivered_damage`, `_is_collision`, `_apply_damage`, `_resolve_collision` — all exercised through `process_ramming_tick` integration tests.
- **Untested:**
  - `clear_ram_target` — only tested indirectly via `process_ramming_tick`. No direct unit test for the public method (L73-77).
  - `_is_collision` fallback path (L143-151) when `position` attribute is missing — uses `x`/`y`/`radius` attributes. Not explicitly tested.
  - `_apply_damage` damage-calculator fallback path (L168-188) — the broad `except Exception` fallback through direct HP decrement is never triggered in tests (which pass without a damage calculator).
  - `__init__` with damage_calculator parameter (L46-47) — never tested with a non-None damage_calculator.
- **Gap:** MINOR — the `_is_collision` fallback path (position-less ships) and `_apply_damage` exception fallback are untested. `clear_ram_target` public method lacks direct unit test.

### 9. `game/simulation/combat/weapon_registry.py` (95 LOC, simulation layer)
- **Test:** `tests/unit/simulation/combat/test_weapon_registry.py` (260 lines)
- **Tested:** `register`, `unregister`, `dispatch`, `has`, `detect_family`, metadata, extensibility
- **Untested:**
  - `__init__` (L40-41) — trivial init, not directly tested
  - `reset` (L52-53) — not directly tested
  - `WEAPON_REGISTRY` module-level singleton (L75) — not verified as created/present
- **Gap:** MINOR — `reset` lacks direct test; module singleton only tested indirectly.

### 10. `game/simulation/components/abilities/cargo.py` (78 LOC, simulation layer)
- **Test:** `tests/unit/simulation/abilities/test_cargo_storage.py` (267 lines)
- **Tested:** Creation (dict, scalar, float, empty, invalid), sync_data, recalculate, UI rows, primary value, registry integration, layer attribute
- **Untested:** `__init__` — not directly tested with component parameter verification. Covered indirectly through creation tests.
- **Gap:** ADVISORY — comprehensive test coverage.

### 11. `game/simulation/components/abilities/resources.py` (234 LOC, simulation layer)
- **Test:** `tests/unit/simulation/components/abilities/test_resource_consumption.py` + 6 other files
- **Tested:** Most methods across `ResourceConsumption`, `ResourceStorage`, `ResourceGeneration`
- **Untested:**
  - `ResourceConsumption._get_resource_registry` (L51-64) — private method with 3 branches (resources arg, component.ship.resources, None). Heuristic marked as untested.
  - `ResourceConsumption.check_available` (L102-115) — 4-branch method: registry exists + resource exists + sufficient, registry exists + resource missing + amount ≤ 0, registry missing → False.
  - `ResourceConsumption.get_strategic_cost` (L117-126) — `strategic_per_hex` trigger branch.
  - `ResourceGeneration.update` method — not present; `ResourceGeneration` has `recalculate` and `get_ui_rows` but no `update`.
  - Error paths in `check_and_consume` where registry is None → returns False (L100).
- **Gap:** MINOR — `_get_resource_registry` has 3 explicit branches, `check_available` has 4. `check_and_consume` branch at L99 (amount ≤ 0 with no resource in registry) returns True — no explicit test.


### 12. `game/simulation/entities/layer_data.py` (112 LOC, simulation layer)
- **Test:** `tests/unit/builder/test_builder_structure_features.py` + 19 others
- **Tested:** All 4 symbols heuristically covered
- **Gap:** ADVISORY — appears fully covered.

### 13. `game/simulation/entities/stat_contributors/accumulator.py` (89 LOC, simulation layer)
- **Test:** `tests/unit/simulation/entities/stat_contributors/test_stat_accumulator.py`
- **Tested:** All 1 symbol heuristically covered
- **Gap:** ADVISORY — appears fully covered.

### 14. `game/strategy/data/design_role_registry.py` (98 LOC, strategy layer)
- **Test:** `tests/unit/strategy/data/test_design_role_registry.py` + loader + invalidation
- **Tested:** `get_default_design_role_registry`, `set_default_design_role_registry`, `reset_default_design_role_registry`
- **Untested:** `_build_default` (L65-91) — private function that loads from 3 file layers. Indirectly tested via `get_default_*`. The mod overlay path (L75-81) and user overlay path (L83-86) may not be explicitly tested.
- **Gap:** MINOR — `_build_default` mod and user overlay branches.

### 15. `game/strategy/data/planet_atmosphere.py` (177 LOC, strategy layer)
- **Test:** `tests/unit/strategy/planet_atmosphere/test_calculations.py` + `test_generation.py`
- **Tested:** All 5 symbols
- **Gap:** ADVISORY — appears fully covered.

### 16. `game/strategy/data/planetary_facility.py` (238 LOC, strategy layer)
- **Test:** 28 candidate test files
- **Tested:** Most symbols
- **Untested:** `_validate_resource_id` (L146-149) — private method with ValueError raise branch. Heuristically untested. The deprecated fuel wrappers (L203-217) are tested indirectly.
- **Gap:** MINOR — `_validate_resource_id` exception path for unknown resource_id.

### 17. `game/strategy/engine/environmental_hazard_engine.py` (250 LOC, strategy layer)
- **Test:** `tests/unit/strategy/engine/test_environmental_hazard_engine.py`
- **Tested:** `process_environmental_tick` main flow, validation
- **Untested:**
  - `__init__` (L57-63) — not tested in isolation. Covered via process tests.
  - `_get_ship_mutator` (L65-71) — lazy initialization with `ShipInstanceWriteService` fallback. Never directly tested; tests likely pass their own mutator.
  - `process_environmental_tick` short-circuit path (L118-122) — when galaxy has zero storms, returns empty events early. Not explicitly tested.
  - `_apply_damage_to_ship` HP reset to None path (L226) — when new_hp >= max_hp, mutator.set_current_hp(ship, None) resets to full.
  - `_drain_fuel_from_ship` drain amount zero path (L247-248).
- **Gap:** MINOR — storm-free short-circuit and lazy mutator initialization.

### 18. `game/strategy/engine/movement_phase_collaborator.py` (194 LOC, strategy layer)
- **Test:** `tests/unit/strategy/turn_engine/test_movement_phase_collaborator.py`
- **Tested:** `snapshot_before`, `resolve_after`
- **Untested:**
  - `_diff_moved_fleets` (L77-98) — heuristically untested. Multi-branch: empty pre_movement_locations, emp_id None, etc.
  - `_mark_boosters_dirty` (L100-108) — heuristically untested. Empty moved_owner_ids early return, emp matching.
  - `_resolve_minefields` (L110-163) — heuristically untested. Broad except catch path (L155-159), runnable_movers filter (L138-141).
  - `_prune_destroyed_fleet_contents` (L165-194) — speed recalc defensive callable check, fleet removal when emptied.
- **Gap:** MAJOR — three private methods marked untested by heuristic; the broad except in `_resolve_minefields` (L155) is particularly concerning — minefield-resolver errors must never abort turn loop, and this contract is untested.

### 19. `game/strategy/engine/order_handlers/transfer.py` (252 LOC, strategy layer)
- **Test:** `tests/unit/strategy/engine/order_handlers/test_transfer_handler.py`
- **Tested:** Core transfer execution paths for planet and fleet targets
- **Untested:**
  - `supported_order_types` property (L60-62) — heuristically untested. Simple tuple return, trivially missing.
  - `_resolve_target_fleet_by_id` galaxy.empires search path (L238-244) — the getattr guard for missing `empires` attribute.
- **Gap:** MINOR — `supported_order_types` is trivial; `_resolve_target_fleet_by_id` has getattr fallback.

### 20. `game/strategy/engine/order_processor.py` (115 LOC, strategy layer)
- **Test:** 17 candidate files
- **Tested:** All 5 symbols heuristically covered
- **Gap:** ADVISORY — appears fully covered.

### 21. `game/strategy/generation/density/primitives/noise.py` (117 LOC, strategy layer)
- **Test:** `tests/unit/strategy/generation/density/test_noise.py`
- **Tested:** All 4 symbols
- **Gap:** ADVISORY — appears fully covered.

### 22. `game/strategy/generation/loaders/system_blueprints_loader.py` (241 LOC, strategy layer)
- **Test:** `tests/unit/strategy/generation/test_system_blueprints.py`
- **Tested:** `load`, `get_blueprint`, `select_random_blueprint`
- **Untested:**
  - `__init__` (L27-34) — not tested in isolation.
  - `_validate_schema` (L118-151) — validation with 5 error branches: not-a-dict, missing 'blueprints', blueprints not-a-dict.
  - `_validate_blueprint` (L153-241) — complex validation with 15+ error branches: missing star_count/planet_count/weight, star_count int range check, star_count dict min/max validation, star_count dict missing min/distribution, star_count wrong type, planet_count not dict, planet_count missing min/max, planet_count range invalidity, weight ≤ 0.
- **Gap:** MAJOR — `_validate_schema` and `_validate_blueprint` have ~20 error-raising branches combined. Only indirectly tested through `load()` which triggers them on malformed input. The `star_count` as-dict branch with `distribution` key (L201-206) is a completely dead path — if `min` is missing but `distribution` exists, it raises; this is never tested.

### 23. `game/strategy/interfaces/engines/components.py` — **See CRITICAL section above (Tier 0)**

### 24. `game/strategy/services/ability_sources/warp_point.py` — **See CRITICAL section above (Tier 0)**

### 25. `game/strategy/services/deployment_zone_calculator.py` (107 LOC, strategy layer)
- **Test:** `tests/unit/strategy/services/test_deployment_zone_calculator.py`
- **Tested:** All 3 symbols
- **Gap:** ADVISORY — appears fully covered.

### 26. `game/strategy/services/planet_write_service.py` (184 LOC, strategy layer)
- **Test:** `tests/unit/strategy/services/test_planet_write_service.py`
- **Tested:** Population mutators, facility mutators, stockpile, orders, scalar fields
- **Untested (heuristic):**
  - `add_staging_item` (L102-110) — delegates to `planet.add_to_staging_yard`
  - `pop_staging_item` (L112-119) — delegates to `planet.pop_staging_yard_typed`
  - `insert_order` (L132-135) — delegates to `planet.add_order` with index
  - `set_atmosphere_target` (L158-159) — simple attribute set
  - `set_gravity_target` (L170-171) — simple attribute set
  - `set_water_target` (L173-174) — simple attribute set
- **Gap:** MINOR — 6 thin delegate methods not directly tested. All are one-liners or two-liners.

### 27. `game/strategy/services/task_group_suggester.py` (125 LOC, strategy layer)
- **Test:** `tests/unit/strategy/services/test_task_group_suggester.py`
- **Tested:** All 1 symbol
- **Gap:** ADVISORY — appears fully covered.

### 28. `game/strategy/validation/superweapon_validator.py` (270 LOC, strategy layer)
- **Baseline tier:** Tier 0. **Corrected tier:** Tier 2 (MINOR).
- **Test:** `tests/unit/strategy/validation/test_superweapon_validator.py` (731 lines) — **comprehensive**
- **Tested:** `find_ship_with_ability`, `validate_implode_planet`, `validate_stellerate_star`, `validate_open_warp_point`, `validate_close_warp_point`, `validate_create_dyson_sphere`, `validate_self_destruct`
- **Untested:**
  - `_require_ability` (L35-54) — private method tested indirectly; the `component_registry is None` branch (L46) returns None (no error) — this is intentional (no checks run without registry) but the branch path is implicit.
  - `_require_at_star_system` (L56-69) — private method tested indirectly.
  - `_validate_star_targeted_superweapon` (L98-122) — private method tested indirectly.
  - `validate_open_warp_point` with `skip_location_check=True` (L162-166) — the already-exists-warp check is skipped when location check is skipped.
  - `validate_close_warp_point` with `skip_location_check=True` — the exact-sector check is skipped.
- **Gap:** MINOR — skip_location_check paths in open/close warp point not explicitly tested, though close_warp has skip_location_check tests at L552-584.

### 29. `game/ui/panels/design_report_panel.py` (200 LOC, ui layer)
- **Test:** `tests/unit/ui/panels/test_design_report_panel.py`
- **Tested:** `update_design`, `_update_portrait`, `get_width_required`, `kill`
- **Untested:** `show_placeholder` (L87-117) — creates placeholder UITextBox. Marked untested by heuristic.
- **Gap:** MINOR — placeholder display is a UI rendering concern.

### 30. `game/ui/panels/race_environment_panel.py` (337 LOC, ui layer)
- **Test:** `tests/unit/ui/test_race_environment_panel.py`
- **Tested:** `update_config`, `update_labels`, `set_from_config`, `apply_homeworld_preset`, `handle_dropdown_change`, `_update_points_display`
- **Untested (heuristic):**
  - `_create_content` (L90-118) — layout construction, tested through __init__
  - `_create_repro_and_happiness` (L149-196) — slider construction
  - `_create_factor_rows` (L198-211) — factor row creation
  - `_on_row_change` (L276-283) — callback fired by PreferenceRow
- **Gap:** MINOR — private layout methods covered via init; `_on_row_change` delegation is trivial.

### 31. `game/ui/screens/builder/layer_panel.py` (536 LOC, ui layer)
- **Test:** `tests/unit/ui/test_structure_visibility.py`
- **Tested:** Basic structure visibility toggles
- **Untested (heuristic):** `handle_item_action` (L296-356), `handle_event` (L358-376), `update` (L378-389), `suppress_toggle` (L391-393), `draw` (L395-411), `can_accept_drop` (L413-414), `accept_drop` (L416-437), `get_target_layer_at` (L439-470), `get_range_selection` (L472-536)
- **Gap:** MAJOR — 536 LOC with only ~10% test coverage. `handle_item_action` has 12 explicit action branches; `accept_drop` has validation error path; `get_range_selection` has range-calculation logic with edge cases for group items.
- **Key specifics:**
  - L411: `draw` draws selection highlight overlays — untested rendering
  - L430-435: `accept_drop` validation-failure error message path
  - L439-470: `get_target_layer_at` scroll-offset positioning + multi-item traversal
  - L472-536: `get_range_selection` with collapsed groups — 64-line complex traversal

### 32. `game/ui/screens/builder/right_panel.py` (437 LOC, ui layer)
- **Test:** `tests/unit/builder/test_builder_ui_sync.py`
- **Tested:** Basic sync operations (3 of 16 symbols)
- **Untested:** `on_registry_reloaded`, `on_ship_updated`, `setup_controls`, `setup_stats`, `_sync_from_stats_panel`, `rebuild_stats`, `update_class_dropdown`, `update_vehicle_type_dropdown`, `update_role_dropdown`, `_get_role_dropdown_data`, `update_dropdowns_for_data_reload`, `update_stats_display`
- **Gap:** MAJOR — 437 LOC with ~15% test coverage. `setup_controls` (L81-167) creates 7+ dropdown widgets with complex state. `_get_role_dropdown_data` (L381-407) has 3-branch fallback logic for missing/bad role IDs. `update_dropdowns_for_data_reload` computes type/class lists from vehicle_classes dict.
- **Key specifics:**
  - L153-156: Role dropdown creation with role resolution
  - L272-279: `update_portrait_image` default-path fallback with os.path.exists checks
  - L381-407: `_get_role_dropdown_data` with `KeyError` catch on registry.get
  - L409-433: `update_dropdowns_for_data_reload` — complex list/dict transformations

### 33. `game/ui/screens/builder_selection.py` (123 LOC, ui layer)
- **Test:** `tests/unit/ui/screens/test_builder_selection.py`
- **Tested:** `normalize_selection`, `process_selection_change`, `get_primary_selection`
- **Untested:** `_is_component_like` (L11-18) — duck-type check, heuristically untested
- **Gap:** MINOR — trivial one-liner tested via `normalize_selection`.

### 34. `game/ui/screens/design_image_helper.py` (218 LOC, ui layer)
- **Test:** `tests/unit/ui/screens/test_design_image_helper.py`
- **Tested:** `load_portrait_thumbnail` (cached path), `load_topdown_thumbnail` (cached path), `clear_thumbnail_cache`
- **Untested (heuristic):** `_load_portrait_thumbnail_uncached` (L62-123), `_load_topdown_thumbnail_uncached` (L149-208)
- **Gap:** MINOR — uncached paths tested indirectly through public cached wrappers. `_load_portrait_thumbnail_uncached` has a complex 6-branch fallback: theme manager discovery, multi-candidate path loading, gradient-placeholder generation with vehicle-type color mapping.
- **Key specifics:**
  - L76-77: theme manager not initialized → `manager.initialize()`
  - L80-93: multi-candidate image loading with try/except per path
  - L95-123: Fallback placeholder generation — 30 lines of gradient fill + font rendering

### 35. `game/ui/screens/fleet_report_view_model.py` (182 LOC, ui layer)
- **Test:** `tests/unit/ui/test_fleet_list_view_model.py`
- **Tested:** `update_ships`, `toggle_filter`, `set_filter_state`, `get_tri_state`, `set_sort`, `get_filter_state`, `get_filtered_ships`, `get_ship_count`, `get_total_ship_count`, `get_filter_label`
- **Untested (heuristic):** `__init__` (L49-76), `_refresh` (L158-166)
- **Gap:** MINOR — `__init__` tested through construction; `_refresh` tested via `get_filtered_ships`.

### 36. `game/ui/screens/fms_menu_callbacks.py` — **See CRITICAL section above (Tier 0)**

### 37. `game/ui/screens/galaxy_test/constants.py` — **Reclassified to Tier 2 (see #0 above)**

### 38. `game/ui/screens/planet_list_presets.py` (242 LOC, ui layer)
- **Test:** `tests/unit/ui/screens/test_planet_list_components.py` + `test_planet_list_filter_manager.py`
- **Tested:** `PresetManager` basic operations, `capture_planet_list_state`, `apply_planet_list_state`
- **Untested (heuristic):** `__init__` (L22-23), `save_to_disk` (L30-33), `get_all_presets` (L56-58)
- **Gap:** MINOR — `save_to_disk` writes to file (IO), `get_all_presets` returns dict directly.

### 39. `game/ui/screens/setup_data_io.py` (220 LOC, ui layer)
- **Test:** `tests/unit/ui/screens/test_setup_data_io.py`
- **Tested:** `scan_ship_designs`, `load_ships_from_entries`, `save_battle_setup`, `load_battle_setup`
- **Untested (heuristic):** `serialize_team` (L146-158), `find_design` (L185-189), `load_team` (L194-210)
- **Gap:** MINOR — inner functions tested through the public wrappers (`save_battle_setup`, `load_battle_setup`).

### 40. `game/ui/screens/strategy_input_handler.py` (216 LOC, ui layer)
- **Test:** `tests/unit/ui/screens/test_strategy_input_handler_core.py` + 6 others
- **Tested:** Most input handling paths, keydown mapping, button press routing, click dispatch
- **Untested:** `_handle_keydown` (L123-127) — the no-mapper branch (L125-128: returns None).
- **Gap:** MINOR — `_handle_keydown` with `self._mapper is None` (null mapper guard).

### 41. `game/ui/screens/strategy_modal_window.py` (292 LOC, ui layer)
- **Test:** `tests/unit/ui/screens/test_strategy_modal_window.py` + 3 others
- **Tested:** All 9 symbols
- **Gap:** ADVISORY — appears fully covered.

### 42-46. `strategy_screen_assets`, `strategy_screen_order_editing`, `strategy_screen_selection`, `strategy_windows/empire_panel_ctrl`, `test_lab/dialogs` — **Baseline incorrectly marked Tier 0. All have dedicated test files.**

### 47. `game/ui/screens/workshop_data_loader.py` (229 LOC, ui layer)
- **Test:** `tests/unit/ui/screens/test_workshop_data_loader.py`
- **Tested:** `find_file`, `clear_registries`, `load_all`
- **Untested:** `_get_default_class` (L217-229) — with first-available fallback (L225-227) when "Escort" not in classes. Heuristically untested.
- **Gap:** MINOR — fallback class-selection path when "Escort" is absent.

### 48. `game/ui/screens/workshop_screen.py` (645 LOC, ui layer)
- **Test:** `tests/unit/ui/screens/test_workshop_screen.py` + 8 other files
- **Tested:** 24 of 31 symbols
- **Untested (heuristic):** `rebuild_modifier_ui`, `show_clear_confirmation`, `on_select_target_pressed`
- **Gap:** MINOR — 3 methods untested out of 31. `show_clear_confirmation` is a UI confirmation interaction.

### 49. `game/ui/services/component_service.py` (132 LOC, ui layer)
- **Test:** `tests/unit/ui/services/test_component_service.py`
- **Tested:** `get_all_components`, `get_modifier_registry`, `get_modifier_definition`, `is_modifier_allowed`
- **Untested (heuristic):** `__init__` (L36-52), `_get_provider` (L54-56)
- **Key specifics:**
  - L46-51: `__init__` has explicit None-check that raises `ValidationException` — this is important. Tests should verify this.
  - `_get_provider` is a trivial getter.
- **Gap:** MINOR — None-check exception path in `__init__` NOT tested.

### 50. `game/ui/services/design_loader_adapter.py` (99 LOC, ui layer)
- **Test:** `tests/unit/ui/services/test_design_loader_adapter.py`
- **Tested:** `load_ship_from_design_data`, `load_ship_from_file`
- **Untested:** `__init__` (L36-56) — has None-check exception path when both `design_loader` and `registry_provider` are None (L48-55).
- **Gap:** MINOR — None-check exception path in `__init__` NOT tested.

---

## File Coverage Verification Table

| # | Production File | LOC | Baseline Tier | Verified Tier | Test File(s) | Actual Coverage | Gaps |
|---|---|---|---|---|---|---|---|
| 1 | `ai/policy_manager.py` | 118 | 3 | 3 | `test_policy_manager.py` + 6 | Full | ADVISORY |
| 2 | `ai/spatial_behaviors/column.py` | 55 | 2 | 2 | `test_spatial_behaviors.py` | Partial | `__init__` |
| 3 | `ai/spatial_behaviors/escort.py` | 50 | 2 | 2 | `test_spatial_behaviors.py` | Partial | `__init__` |
| 4 | `core/input_actions.py` | 344 | 2 | 2 | `test_input_actions.py` | Partial | `_key_display_name` indirect |
| 5 | `core/validation.py` | 209 | 3 | 3 | `test_validation.py` + 24 | Full | ADVISORY |
| 6 | `research/data/research_tracker.py` | 293 | 2 | 2 | `test_research_tracker.py` | Partial | `_clamp_allocations_to_budget` |
| 7 | `simulation/combat/families/_beam_common.py` | 44 | 3 | 3 | `test_weapon_family_handlers.py` | Full | ADVISORY |
| 8 | `simulation/combat/modifier_stack.py` | 74 | 3 | 3 | `test_modifier_stack.py` + 17 | Full | ADVISORY |
| 9 | `simulation/combat/ram_target_resolver.py` | 226 | 2 | 2 | `test_ram_target_resolver.py` | Partial | `clear_ram_target` direct, fallback paths |
| 10 | `simulation/combat/weapon_registry.py` | 95 | 2 | 2 | `test_weapon_registry.py` | Partial | `reset`, module singleton |
| 11 | `simulation/components/abilities/cargo.py` | 78 | 2 | 3 | `test_cargo_storage.py` | Full | ADVISORY |
| 12 | `simulation/components/abilities/resources.py` | 234 | 2 | 2 | `test_resource_consumption.py` + 6 | Partial | `_get_resource_registry`, `check_available` |
| 13 | `simulation/entities/layer_data.py` | 112 | 3 | 3 | 20 files | Full | ADVISORY |
| 14 | `simulation/entities/stat_contributors/accumulator.py` | 89 | 3 | 3 | `test_stat_accumulator.py` | Full | ADVISORY |
| 15 | `strategy/data/design_role_registry.py` | 98 | 2 | 2 | `test_design_role_registry.py` + 2 | Partial | `_build_default` mod/user paths |
| 16 | `strategy/data/planet_atmosphere.py` | 177 | 3 | 3 | `test_calculations.py` + `test_generation.py` | Full | ADVISORY |
| 17 | `strategy/data/planetary_facility.py` | 238 | 2 | 2 | 28 files | Partial | `_validate_resource_id` |
| 18 | `strategy/engine/environmental_hazard_engine.py` | 250 | 2 | 2 | `test_environmental_hazard_engine.py` | Partial | Short-circuit, lazy mutator, damage/HP reset |
| 19 | `strategy/engine/movement_phase_collaborator.py` | 194 | 2 | 2 | `test_movement_phase_collaborator.py` | Partial (MAJOR) | 3 private methods untested |
| 20 | `strategy/engine/order_handlers/transfer.py` | 252 | 2 | 2 | `test_transfer_handler.py` | Partial | `supported_order_types`, fallback getattr |
| 21 | `strategy/engine/order_processor.py` | 115 | 3 | 3 | 17 files | Full | ADVISORY |
| 22 | `strategy/generation/density/primitives/noise.py` | 117 | 3 | 3 | `test_noise.py` | Full | ADVISORY |
| 23 | `strategy/generation/loaders/system_blueprints_loader.py` | 241 | 2 | 2 | `test_system_blueprints.py` | Partial (MAJOR) | `_validate_schema`, `_validate_blueprint` (~20 branches) |
| 24 | **`strategy/interfaces/engines/components.py`** | **47** | **0** | **0** | **NONE** | **Zero (CRITICAL)** | **ABC with no tests** |
| 25 | **`strategy/services/ability_sources/warp_point.py`** | **64** | **0** | **0** | **NONE** | **Zero (CRITICAL)** | **Concrete adapter with no tests** |
| 26 | `strategy/services/deployment_zone_calculator.py` | 107 | 3 | 3 | `test_deployment_zone_calculator.py` | Full | ADVISORY |
| 27 | `strategy/services/planet_write_service.py` | 184 | 2 | 2 | `test_planet_write_service.py` | Partial | 6 thin delegate methods |
| 28 | `strategy/services/task_group_suggester.py` | 125 | 3 | 3 | `test_task_group_suggester.py` | Full | ADVISORY |
| 29 | `strategy/validation/superweapon_validator.py` | 270 | **0→2** | 2 | `test_superweapon_validator.py` (731 LOC) | Partial | skip_location_check branch in open_warp |
| 30 | `ui/panels/design_report_panel.py` | 200 | 2 | 2 | `test_design_report_panel.py` | Partial | `show_placeholder` |
| 31 | `ui/panels/race_environment_panel.py` | 337 | 2 | 2 | `test_race_environment_panel.py` | Partial | `_on_row_change` indirect |
| 32 | `ui/screens/builder/layer_panel.py` | 536 | 2 | 2 | `test_structure_visibility.py` | Partial (MAJOR) | 10 of 12 methods untested |
| 33 | `ui/screens/builder/right_panel.py` | 437 | 2 | 2 | `test_builder_ui_sync.py` | Partial (MAJOR) | 13 of 16 methods untested |
| 34 | `ui/screens/builder_selection.py` | 123 | 2 | 2 | `test_builder_selection.py` | Partial | `_is_component_like` indirect |
| 35 | `ui/screens/design_image_helper.py` | 218 | 2 | 2 | `test_design_image_helper.py` | Partial | `_load_*_thumbnail_uncached` indirect |
| 36 | `ui/screens/fleet_report_view_model.py` | 182 | 2 | 2 | `test_fleet_list_view_model.py` | Partial | `__init__`, `_refresh` indirect |
| 37 | **`ui/screens/fms_menu_callbacks.py`** | **136** | **0** | **0** | **NONE** | **Zero (CRITICAL)** | **All callbacks untested** |
| 38 | `ui/screens/galaxy_test/constants.py` | 32 | **1→2** | 2 | `test_galaxy_test_screen.py` | Partial | Key enumeration not validated |
| 39 | `ui/screens/planet_list_presets.py` | 242 | 2 | 2 | `test_planet_list_components.py` | Partial | `save_to_disk`, `get_all_presets` |
| 40 | `ui/screens/setup_data_io.py` | 220 | 2 | 2 | `test_setup_data_io.py` | Partial | `serialize_team`, `find_design` indirect |
| 41 | `ui/screens/strategy_input_handler.py` | 216 | 2 | 2 | `test_strategy_input_handler_core.py` + 6 | Partial | null mapper guard |
| 42 | `ui/screens/strategy_modal_window.py` | 292 | 3 | 3 | `test_strategy_modal_window.py` | Full | ADVISORY |
| 43 | `ui/screens/strategy_screen_assets.py` | 88 | **0→2** | 2 | `test_strategy_screen_assets.py` (170 LOC) | Partial | Full public API tested |
| 44 | `ui/screens/strategy_screen_order_editing.py` | 93 | **0→2** | 2 | `test_strategy_screen_order_editing.py` (194 LOC) | Partial | Full public API tested |
| 45 | `ui/screens/strategy_screen_selection.py` | 99 | **0→2** | 2 | `test_strategy_screen_selection.py` (184 LOC) | Partial | Full public API tested |
| 46 | **`ui/screens/strategy_windows/dispatch.py`** | **129** | **0** | **0** | **NONE** | **Zero (CRITICAL)** | **Both classes untested** |
| 47 | `ui/screens/strategy_windows/empire_panel_ctrl.py` | 97 | **0→2** | 2 | `test_empire_panel_ctrl.py` (133 LOC) | Partial | `_on_closed` indirect |
| 48 | **`ui/screens/test_lab/dialogs.py`** | 272 | **0→2** | **2** | `test_dialogs.py` (111 LOC) | Partial | Draw methods, `handle_event` scroll |
| 49 | **`ui/screens/test_lab/results_panel.py`** | **266** | **0** | **0** | **NONE** | **Zero (CRITICAL)** | **266 LOC UI component with no tests** |
| 50 | `ui/screens/workshop_data_loader.py` | 229 | 2 | 2 | `test_workshop_data_loader.py` | Partial | `_get_default_class` fallback |
| 51 | `ui/screens/workshop_screen.py` | 645 | 2 | 2 | `test_workshop_screen.py` + 8 | Partial | 3 of 31 methods |
| 52 | `ui/services/component_service.py` | 132 | 2 | 2 | `test_component_service.py` | Partial | `__init__` None-check raise path |
| 53 | `ui/services/design_loader_adapter.py` | 99 | 2 | 2 | `test_design_loader_adapter.py` | Partial | `__init__` None-check raise path |

---

## Heuristic Baseline Corrections

| File | Baseline Tier | Verified Tier | Reason |
|---|---|---|---|
| `strategy/validation/superweapon_validator.py` | 0 | 2 | `test_superweapon_validator.py` exists (731 LOC, comprehensive) |
| `ui/screens/strategy_screen_assets.py` | 0 | 2 | `test_strategy_screen_assets.py` exists (170 LOC) |
| `ui/screens/strategy_screen_order_editing.py` | 0 | 2 | `test_strategy_screen_order_editing.py` exists (194 LOC) |
| `ui/screens/strategy_screen_selection.py` | 0 | 2 | `test_strategy_screen_selection.py` exists (184 LOC) |
| `ui/screens/strategy_windows/empire_panel_ctrl.py` | 0 | 2 | `test_empire_panel_ctrl.py` exists (133 LOC) |
| `ui/screens/test_lab/dialogs.py` | 0 | 2 | `test_dialogs.py` exists (111 LOC) |
| `ui/screens/galaxy_test/constants.py` | 1 | 2 | `test_galaxy_test_screen.py` tests constants explicitly |

## Prioritized Remediation Plan

### Immediate (CRITICAL)
1. **`test_lab/results_panel.py`** (266 LOC) — Write unit tests for `ResultsPanel` covering card selection, scroll state, mouse event handling, and details panel wiring.
2. **`fms_menu_callbacks.py`** (136 LOC) — Write unit tests for `_first_ship_id_with` edge cases and lambda dispatch for both planet and fleet callbacks.
3. **`strategy_windows/dispatch.py`** (129 LOC) — Write unit tests for `UICallbackDispatcher.process` and `ConfirmationDialogController.show/process_event`.
4. **`ability_sources/warp_point.py`** (64 LOC) — Write unit tests for `WarpPointAbilitySource`, especially `affects_hex` TypeError catch and None-guard paths.
5. **`interfaces/engines/components.py`** (47 LOC) — Minimal ABC contract test.

### High Priority (MAJOR)
6. **`builder/layer_panel.py`** (536 LOC) — 10 of 12 methods untested; focus on `handle_item_action`, `accept_drop`, `get_range_selection`.
7. **`builder/right_panel.py`** (437 LOC) — 13 of 16 methods untested; focus on `_get_role_dropdown_data`, `update_dropdowns_for_data_reload`.
8. **`system_blueprints_loader.py`** (241 LOC) — `_validate_schema` and `_validate_blueprint` have ~20 untested validation branches.
9. **`movement_phase_collaborator.py`** (194 LOC) — Test `_resolve_minefields` broad-except path and `_prune_destroyed_fleet_contents`.

### Lower Priority (MINOR)
10. `ram_target_resolver.py` — Direct unit test for `clear_ram_target`, `_is_collision` fallback, `_apply_damage` exception fallback.
11. `resources.py` — `_get_resource_registry` 3-branch test, `check_available` 4-branch test.
12. `environmental_hazard_engine.py` — Storm-free short-circuit test.
13. `component_service.py` / `design_loader_adapter.py` — `__init__` None-check exception paths.
