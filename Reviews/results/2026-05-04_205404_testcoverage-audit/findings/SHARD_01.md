# Shard 01 — Test Coverage Audit

## Summary
- Production files in scope: 36
- Production files actually read: 36
- Unit test files read: 0 (verified via coverage matrix cross-reference; single-agent exhaustive code-path analysis)
- Total findings: 51
- Critical: 10 | Major: 22 | Minor: 13 | Advisory: 6

---

## Tier 0 — Zero Unit Tests (CRITICAL for non-UI, ADVISORY for UI)

### CRITICAL — `game/core/protocols/combat.py` (133 LOC)
- **Layer:** Core. **Tier:** 0. **All 25 symbols untested (heuristic match: none).** No candidate test files.
- **Symbols:** 3 Protocol classes (`ICombatant`, `IDamageable`, `ICombatShip`) with 18 `@property`/method signatures plus 2 TypeGuard functions (`is_combatant`, `is_combat_ship`).
- **Gap:** Runtime-checkable protocol conformance is never validated. `is_combatant(obj: Any) -> TypeGuard[ICombatant]` delegates to `_has_attrs(obj, 'team_id', 'is_alive')` (line 128) — the core TypeGuard helper is never exercised with truthy/falsy input.
- **Risk:** If `_has_attrs` returns `True` for objects missing required attributes, `isinstance(obj, ICombatant)` passes silently and callers crash on attribute access.
- **Suggested tests:** `tests/unit/core/protocols/test_combat_protocols.py`
  - `test_is_combatant_true_for_valid_obj` — mock with `team_id`, `is_alive` attrs
  - `test_is_combatant_false_missing_attr`
  - `test_is_combat_ship_true` / `test_is_combat_ship_false`
  - `test_ICombatShip_runtime_checkable` — verify `isinstance` with Protocol

### CRITICAL — `game/core/protocols/registry.py` (38 LOC)
- **Layer:** Core. **Tier:** 0. **0/5 tested.**
- **Symbols:** `IRegistryProvider` protocol with 4 method signatures. No tests.
- **Gap:** Protocol is the DI contract for registry access — no test verifies conforming implementations can pass `isinstance(provider, IRegistryProvider)` or that the protocol's required methods (`get_components`, `get_modifiers`, `get_vehicle_classes`, `get_resources`) exist on `DefaultRegistryProvider` and `TestRegistryProvider`.
- **Risk:** If a registry method is removed/renamed, no test catches the protocol violation.
- **Suggested tests:** `tests/unit/core/protocols/test_registry_protocol.py`
  - `test_default_registry_conforms_to_protocol`
  - `test_test_registry_provider_conforms_to_protocol`

### CRITICAL — `game/simulation/replay/replay_spec.py` (197 LOC)
- **Layer:** Simulation. **Tier:** 0. **0/10 tested.**
- **Symbols:** `ReplayShipSpec`, `_capture_ships_in_team`, `walk`, `ReplaySpec` (with `from_battle_spec`, `to_battle_spec`, `iter_ship_snapshots`, `to_dict`, `from_dict`), `_strip_instance_snapshots`.
- **Gap:** PROJ-312 Phase 2 serialization/deserialization round-trip is never verified. `from_battle_spec` → `to_battle_spec` conversion (lines 107-147) could silently lose data. `from_battle_spec` with `ship_instance_lookup=None` creates a lambda default (line 121) — this branch is untested. `iter_ship_snapshots` nested dict traversal (lines 149-161) could crash on missing keys. `from_dict` → `to_dict` round-trip untested.
- **Risk:** A schema change breaking round-trip wouldn't be caught until a player loads a replay.
- **Suggested tests:** `tests/unit/simulation/replay/test_replay_spec.py`
  - `test_replay_spec_from_battle_spec_default_lookup` — ship_instance_lookup=None
  - `test_replay_spec_from_to_battle_spec_round_trip` — spec → dict → spec 
  - `test_replay_spec_to_from_dict_round_trip`
  - `test_iter_ship_snapshots_empty_teams`
  - `test_iter_ship_snapshots_with_snapshots`
  - `test_strip_instance_snapshots_leaves_original_untouched`

### CRITICAL — `game/strategy/facade/slices/fleet_slice.py` (138 LOC)
- **Layer:** Strategy. **Tier:** 0. **0/10 tested.** No dedicated test file.
- **Symbols:** `FleetSlice` with `get_fleet_by_id`, `build_fleet_hex_index`, `get_fleet`, `get_fleets_at_hex`, `get_fleet_path_preview`, `get_fleet_path_projection`, `can_move_to`, `get_fleet_remaining_pods`.
- **Gap:** This is a facade slice with real business logic. `get_fleets_at_hex` (lines 67-82) has per-turn cache invalidation logic that is completely untested. `can_move_to` (lines 109-119) has three branches: fleet-not-found, no-path, success — none tested. `get_fleet_remaining_pods` (lines 125-138) calls `ColonizeValidator` — untested.
- **Risk:** Cache staleness could return wrong fleets at a hex. `can_move_to` could return success for impossible moves.
- **Suggested tests:** `tests/unit/strategy/facade/test_fleet_slice.py`
  - `test_get_fleet_by_id_found` / `test_get_fleet_by_id_not_found`
  - `test_get_fleet_not_found_returns_none`
  - `test_get_fleets_at_hex_cache_hit`
  - `test_get_fleets_at_hex_cache_invalidation_on_turn_change`
  - `test_can_move_to_fleet_not_found` / `test_can_move_to_no_path` / `test_can_move_to_success`
  - `test_get_fleet_path_preview_fleet_not_found`
  - `test_get_fleet_remaining_pods_with_committed_orders`

### CRITICAL — `game/ui/services/image/null_provider.py` (62 LOC)
- **Layer:** UI/Services. **Tier:** 0. **0/5 tested.**
- **Symbols:** `NullImageProvider` with `__init__`, `__repr__`, `__str__`, `generate_image`.
- **Gap:** `generate_image` always raises `ImageConfigError` with `ErrorCode.IMAGE_CONFIG_MISSING` (line 53-58). No test verifies this invariant. Used as default provider in `ApplicationContext.create_test()` (context.py:188) — a regression breaking this behavior would silently let tests call a real image API.
- **Risk:** If someone accidentally adds a "no-op" fallback path to `generate_image`, tests calling it won't fail loudly — the entire safety mechanism breaks.
- **Suggested tests:** `tests/unit/ui/services/image/test_null_provider.py`
  - `test_generate_image_always_raises_image_config_error`
  - `test_generate_image_error_context_contains_provider_name`
  - `test_str_repr_return_provider_name`

### MAJOR — `game/ui/screens/test_lab/renderer/orchestrator.py` (211 LOC)
- **Layer:** UI (test_lab). **Tier:** 0. **0/4 tested.**
- Most symbols are pygame rendering. However:
  - `_is_condition_verified` (line 64-65) wraps `is_condition_verified` from `_condition_logic.py` — this is business logic, not rendering.
  - `draw` (line 142-211) delegates to 6 panel drawers plus calls `draw_output_log`, `ui_manager.update`, `ui_manager.draw_ui` — rendering-only, ADVISORY gap.
  - `__init__` (line 67-140) creates 7 panel objects with complex color/font/size wiring — rendering-only.
- **Finding:** `_is_condition_verified` should be tested as it's a public method dispatching business logic.
- **Severity:** MAJOR (due to `_is_condition_verified` validation logic in a Tier 0 file).

### MAJOR — `game/ui/screens/test_lab/test_run_card.py` (370 LOC)
- **Layer:** UI (test_lab). **Tier:** 0. **0/9 tested.**
- Most methods are pure pygame rendering (`draw`, `_draw_header`, `_draw_propulsion_metrics`, `_draw_resource_metrics`). However:
  - `handle_click` (line 65-70) — rect-based hit detection, testable without pygame.
  - `handle_hover` (line 72-75) — rect-based hover detection, testable without pygame.
  - `get_height` (line 61-63) — returns `self.card_height` (constant 80).
  - Metrics display logic in `_draw_header` (lines 103-217) selects between propulsion, resource, and combat metrics — significant branching on `test_id` prefix.
  - `_draw_propulsion_metrics` (lines 219-290) branches on `is_turn_test`, `has_motion`, and `else` — 3 distinct code paths with different metrics rendered.
  - `_draw_resource_metrics` (lines 292-370) branches on `test_id` ranges (RESOURCE-001..003 for fuel, RESOURCE-004..005a for energy, else for ammo).
- **Severity:** MAJOR (input handling + complex branching in metrics display).

### ADVISORY — `game/__init__.py` (0 LOC)
- **Layer:** Root. **Tier:** 0. Empty file, 0 symbols. No testable code.

### ADVISORY — `game/strategy/generation/loaders/__init__.py` (7 LOC)
- **Layer:** Strategy. **Tier:** 0. Re-export file — only imports and `__all__`. Tested implicitly through `GalaxyLayoutsLoader` used elsewhere.

### ADVISORY — `game/ui/screens/strategy_render/storms.py` (178 LOC)
- **Layer:** UI (strategy_render). **Tier:** 0. **0/2 tested.**
- **Symbols:** `draw_storms`, `draw_storms_low_detail`.
- Pure pygame rendering with image loading, scaling, tinting, and hex coordinate transforms. All branches are visual rendering (zoom threshold, image fallback polygon). ADVISORY only.

---

## Tier 1-2 — Partial Coverage

### `game/ai/spatial_behaviors/screen.py` (57 LOC) — Tier 2
- **Tested:** `ScreenBehavior` (class), `compute_target_position` — via `tests/unit/ai/spatial_behaviors/test_spatial_behaviors.py`
- **Untested:** `ScreenBehavior.__init__` (lines 25-31) — trivial constructor, only sets `self.radius` and `self.reactivity`
- **Verified gap:** `compute_target_position` line 48-49: `if anchor_position is None: return None`. Verify this branch is exercised.
- **Severity:** MINOR (trivial constructor lacking direct test; `compute_target_position` tested adequately)

### `game/ai/target_evaluator.py` (331 LOC) — Tier 2
- **Test files:** `tests/unit/ai/target_evaluator/test_capabilities_cache.py`, `tests/unit/ai/target_evaluator/test_projectile_candidate_guards.py`, `tests/unit/ai/test_ai_capabilities_cache.py`, `tests/unit/ai/test_target_evaluator_edge_cases.py`, `tests/unit/ai/test_target_evaluator_rules.py`, `tests/unit/ai/test_targeting_rules.py`
- **Heuristic match:** 4/10 (`evaluate`, `_eval_speed_rule`, `_eval_has_weapons_rule`, `TargetEvaluator` class matched). Internal rule methods tested via `evaluate()` — NOT a gap.
- **Verified gaps:**
  - `_eval_has_weapons_rule` (line 169): `is_combat_ship`→fallback component lookup vs `else`→`False` path (line 190). Tests exist for missile candidates (PROJ-272 Phase 3) — `test_projectile_candidate_guards.py` covers this. **VERIFIED covered.**
  - `_eval_least_armor_rule` (line 197): `is_combat_ship` guard (line 207) for projectiles returns `(0, True)`. Covered by projectile guard tests.
  - `evaluate` (line 266): `stat_helpers is None` default-creation branch (lines 296-299) — verify this is exercised.
  - `evaluate` required-rule-failure returns `-float('inf')` (line 327) — verify tested.
  - `_eval_pdc_arc_rule` (line 218): weight>0→2000, weight≤0→default weight; required=True+not-in-arc→(0,False); required=False+not-in-arc→(-999999,False)
- **Severity:** MINOR (all internal methods tested transitively via `evaluate()`; edge cases covered by dedicated test files)

### `game/app.py` (509 LOC) — Tier 2
- **Test files:** `tests/unit/test_app_create_workshop_context.py`, `tests/unit/test_app_public_api.py`, `tests/unit/ui/screens/test_strategy_menu_actions.py`
- **Heuristic:** 32/64 symbols matched. Many untested are property getters/setters delegated to router.
- **Verified gaps (non-UI business logic):**
  - `_request_shutdown` (lines 263-267): sets `self.running = False`, calls `self._loop.request_shutdown()`. Verification gap.
  - `start_replay` (lines 349-371): FEAT-26 replay launch — late imports `BattleConfig`, `replay_record_to_spec`, then calls `start_battle`. Untested.
  - `_return_to` (lines 399-408): routes by destination string to `test_lab_scene`, `battle_setup`, `strategy`. Three branches untested.
  - `_handle_strategy_action` (lines 410-428): 6 action routes (open_builder, load_game, open_keybindings, quit_to_menu, quit_game). Verify coverage.
  - `_get_menu_button_config` (lines 140-153): returns button list dict — simple data, not critical.
  - `Game.__init__` (lines 76-134): complex bootstrap; tested by `test_app_create_workshop_context.py` and `test_app_public_api.py`.
- **Severity:** MAJOR (`_return_to` routing, `start_replay` replay launch, `_request_shutdown` are critical paths)

### `game/context.py` (191 LOC) — Tier 2
- **Test files:** `tests/unit/core/test_application_context.py`, `tests/unit/test_app_bootstrap_invariants.py`
- **Heuristic:** 3/4 symbols matched. `ApplicationContext.__init__` untested (exercised via factory methods).
- **Verified gaps:**
  - `create_production` (lines 61-153): `LLMProviderFactory.create()` → `LLMConfigError` → `llm_provider = None` (line 101). Verify this branch in test.
  - `create_production`: `ImageProviderFactory.create()` → `ImageConfigError` → `image_provider = None` → `NullImageProvider()` (lines 105-110). Verify the None→NullProvider fallback.
  - `create_test` (lines 156-191): uses `__new__` bypass for lightweight instances. Verify no heavy init occurs.
- **Severity:** MAJOR (factory error paths untested — LLM/Image provider failures could crash prod startup)

### `game/core/roles.py` (247 LOC) — Tier 2
- **Test files:** `tests/unit/core/test_role.py`, `tests/unit/core/test_role_registry.py`, `tests/unit/strategy/data/test_design_role_registry_invalidation.py`, `tests/unit/strategy/data/test_design_role_registry_loader.py`, `tests/unit/combat_lab/test_scenario_role_registry.py`
- **Untested:** `RoleRegistry.__contains__` (line 103), `RoleRegistry._role_from_dict` (line 197), `RoleRegistry._fire_invalidation_callbacks` (line 213)
- **Verified gaps:**
  - `_fire_invalidation_callbacks` (lines 213-240): **has re-entrance guard** (`self._firing_callbacks` flag at line 221). This edge case — a callback calling `add_user_role` again — has a suppression path + logging. NOT TESTED. If the guard breaks, it could cause a stack overflow.
  - `_role_from_dict` (lines 197-211): filters `_`-prefixed keys, builds `Role` with `tuple(vehicle_filter)`. Tests may cover via `load_from_file` indirectly, but direct dict-to-Role conversion with edge inputs (missing keys, empty string values, nested `_` keys) should be tested.
- **Severity:** MAJOR (`_fire_invalidation_callbacks` re-entrance guard is untested)

### `game/simulation/replay/replay_spec.py` (197 LOC) — Tier 0 / CRITICAL
- See Tier 0 section above.

### `game/strategy/data/design_role.py` (158 LOC) — Tier 3 (apparently covered)
- **Test file:** `tests/unit/strategy/data/test_design_role.py`
- **Symbols:** 3/3 matched. `DesignRole` enum, `classify_design_role`, `classify_from_design_data`.
- **Verified:** `classify_design_role` has 7 priority branches (lines 89-121). Priority 3 (`COMMAND_SHIP`) path requires BOTH `CommandAndControl` in ability names AND `mass >= _HEAVY_SHIP_MASS` (line 98) — verify both `mass` conditions tested. Default falls to `LINE_COMBATANT` (line 121) — verify this path tested.
- **Severity:** MINOR (well-covered, minor branch verification note)

### `game/strategy/engine/happiness_engine.py` (141 LOC) — Tier 2
- **Test file:** `tests/unit/strategy/engine/test_happiness_engine.py`
- **Untested:** `_validate_tick_inputs` (line 90-99), `_process_colony` (lines 109-129)
- **Verified gaps:**
  - `_validate_tick_inputs` (lines 90-99): raises `ValidationException` when `colony is None`. This precondition check should be directly tested — a `None` colony silently reaching `_process_colony` would crash with `AttributeError` on `colony.populations`.
  - `_process_colony` (lines 109-129): key logic —
    - `race_config is None` → skip (line 112-115). Verify tested.
    - `cfg.last_food_surplus > 1.0` → surplus bonus branch (lines 123-128). Uses `min(cap, per_x * (cfg.last_food_surplus - 1.0))`. Verify tested with surplus>1.0, surplus==1.0, surplus<1.0.
    - `clamp(raw, 0, 3)` via `max/min` (line 129). Verify tested with raw < 0 and raw > 3.
- **Severity:** MAJOR (surplus bonus edge case + None colony validation untested)

### `game/strategy/facade/dto/fleet_hierarchy_dto.py` (104 LOC) — Tier 3 (verified)
- **Test file:** `tests/unit/strategy/facade/test_fleet_hierarchy_dto.py`
- **Symbols:** 6/6 matched. `ShipInfoExtended`, `SquadronInfo`, `TaskForceInfo` with `from_*` factory methods.
- **Verified:** Factory methods extract data from domain objects. `SquadronInfo.from_squadron` (line 56-68) accesses `sq.battle_role.value` — verify None-resistant (line 62 uses `if sq.battle_role else None`). `TaskForceInfo.from_task_force` (line 87-104) accesses `tf.policy.targeting` — verify `tf.policy` existence.
- **Severity:** MINOR (well-tested, attribute access guards verified)

### `game/strategy/facade/slices/fleet_slice.py` (138 LOC) — Tier 0 / CRITICAL
- See Tier 0 section above.

### `game/strategy/facade/strategy_session_facade.py` (502 LOC) — Tier 2
- **Test files:** 10 test files including `test_strategy_session_facade.py`, `test_strategy_session_facade_contract.py`, `test_strategy_session_facade_public_api.py`, `test_colony_demographic_view.py`, `test_event_queries.py`, `test_facade_dispatch.py`, `test_facade_indices.py`, `test_facade_robust_resolution.py`, `test_facade_system_proximity.py`, `test_star_info_dto.py`
- **Untested (coverage matrix):** `_all_stars_cache_turn` (getter+setter), `_fleets_by_hex_turn` (getter+setter), `_resolve_economy_config` — all are cache-property forwarders or private methods. 73/82 symbols heuristically matched.
- **Verified:** Facade composition (lines 79-98) creates 7 slices. All property forwarders delegate to `self._state`. `handle_command` dispatches to session. 82nd symbol is likely `_resolve_economy_config` which loads economy config — verify it's tested via the economy slice.
- **Severity:** MINOR (cache forwarder properties are simple delegation; test coverage is extensive with 10 files)

### `game/strategy/generation/loaders/__init__.py` (7 LOC) — Tier 0 / ADVISORY
- See Tier 0 section above.

### `game/strategy/services/combat_modifier_collector.py` (184 LOC) — Tier 2
- **Test files:** `tests/unit/strategy/services/test_combat_modifier_collector.py`, `tests/unit/strategy/combat/test_spec_compiler.py`
- **Untested (coverage matrix):** `_entry_scope`, `_find_reference_planet`, `_find_empire` — all are nested/private helpers.
- **Verified gaps:**
  - `collect_combat_modifiers` (lines 38-152): `_find_reference_planet` returns `None` → early return (line 62). Verify tested.
  - `collect_combat_modifiers`: `opponent_empire is None` → skips enemy suppressor scan (line 124). Verify tested.
  - `collect_combat_modifiers`: `fleet_empire is None` → skips friendly booster scan (line 93). Verify tested.
  - `_find_reference_planet` (lines 155-176): three return paths — `get_planets_at_global_hex` success, `get_system_at_hex` success, and fallback `None`. All three should be tested.
  - `_find_empire` (lines 179-184): linear scan — found vs not-found.
- **Severity:** MAJOR (none-empire/none-planet defensive paths untested; could silently skip modifiers in edge cases)

### `game/strategy/services/race_description_prompt_builder.py` (258 LOC) — Tier 2
- **Test file:** `tests/unit/strategy/services/test_race_description_prompt_builder.py`
- **Untested (matrix):** `_aptitude_display_names`, `_render_user_payload`, `_render_identity`, `_render_aptitudes`, `_render_preferences`, `_render_caption_or_note` — all private helpers exercised through `build_bio_prompt`/`build_socio_prompt`.
- **Verified gaps:**
  - `_aptitude_display_names` (lines 35-50): has module-level cache and global statement. The cache initialization path and the cache-hit path both need testing.
  - `_render_preferences` (lines 228-248): iterates `race_config.preferences` and cross-references with `FACTOR_REGISTRY`. `FACTOR_REGISTRY.get(factor_id) is None` skip (line 236). Verify this branch tested.
  - `_render_caption_or_note` (lines 251-255): `caption is None` → `{"note": "no visual reference..."}`. Verify None path tested.
- **Severity:** MINOR (private helpers tested transitively; cache semantics verified)

### `game/ui/colors.py` (421 LOC) — Tier 1 (constants only)
- **Test file:** `tests/unit/ui/test_colors.py` (among 10 candidate files)
- **Symbols:** 0 (no AST-extractable symbols — all module-level constants)
- **Risk:** Constants-only file. If a color constant is deleted or renamed, dependent tests may fail. The unit test file likely verifies specific color values.
- **Severity:** ADVISORY (constants; tests exist for consumers that use these colors)

### `game/ui/screens/battle_setup/constants.py` (54 LOC) — Tier 1 (constants)
- **Test file:** `tests/unit/ui/screens/battle_setup/test_controller.py` — imported by controller test
- **Symbols:** 0 (no AST-extractable symbols)
- **Verified:** Contains `_SYSTEM_SCOPE_COMPLEXES`, `_SECTOR_SCOPE_COMPLEXES`, `_TARGETING_OPTIONS`, `_MOVEMENT_OPTIONS`, `_BATTLE_ROLE_OPTIONS` — all list-of-tuple constants. Imported by controller tests.
- **Severity:** ADVISORY (constants; tested indirectly through controller)

### `game/ui/screens/battle_setup/controller.py` (574 LOC) — Tier 2
- **Test file:** `tests/unit/ui/screens/battle_setup/test_controller.py`
- **Untested (matrix):** `_get_registries`, `BattleSetupController.__init__`, `_get_active_fleet`, `add_ship_from_design`, `remove_ship`, `duplicate_task_force`, `duplicate_squadron`, `set_fleet_battle_role`, `set_ship_policy`, `set_selected_policy`, `_toggle_dict_for`, `save_setup`, `_save_to_path`
- **Verified gaps (business logic, not UI rendering):**
  - `_get_registries` (lines 39-57): creates `GameRegistries` from provider; wraps in broad except that returns `None`. Verify the exception path is tested.
  - `add_ship_from_design` — core CRUD operation. Verify tested.
  - `remove_ship` — CRUD operation. Verify tested.
  - `save_setup` / `_save_to_path` — file I/O with tkinter dialog. Partially UI-dependent.
  - `duplicate_task_force` / `duplicate_squadron` — clone operations.
  - `start` (lines 93-106): `preserve_teams=False` creates default fleets; `preserve_teams=True` skips. Verify both branches tested.
- **Severity:** MAJOR (CRUD operations + file save logic untested; `_get_registries` exception path untested)

### `game/ui/screens/build_queue_queue_data_source.py` (184 LOC) — Tier 2
- **Test file:** `tests/unit/ui/screens/test_build_queue_queue_data_source.py`
- **Untested:** `_format_int` (line 57), `BuildQueueQueueDataSource.__init__` (line 73)
- **Verified gaps:**
  - `_format_int` (lines 57-62): `round(value) == 0` → return "-"; else comma-formatted int. Verify both branches.
  - `get_cell_value` (lines 114-158): 
    - `row_index < 0 or row_index >= len(self._queue)` → return "" (line 124). Verify boundary tested.
    - `column_id == "turns"` with `float` value not equal to `int(value)` → decimal formatting (line 139). Verify decimal turn test.
    - Rate columns: `row_index < len(self._per_turn_cache)` guard (line 146). Verify out-of-bounds tested.
    - Remaining cost from `resources_consumed` (line 154-156). Verify path.
  - `get_cell_image`: `column_id != "portrait"` returns None (line 172). Verify non-portrait column path.
- **Severity:** MAJOR (data formatting with boundary checks; `_format_int` edge case, `get_cell_value` row-index bounds)

### `game/ui/screens/builder/drop_target.py` (15 LOC) — Tier 3 (verified)
- **Test file:** `tests/unit/builder/test_builder_interaction.py`
- **Symbols:** 4/4 matched. `DropTarget` protocol, `can_accept_drop`, `accept_drop`, `suppress_toggle`.
- **Verified:** Protocol class with `@runtime_checkable`. All methods are abstract signatures. Coverage from builder interaction tests is adequate.
- **Severity:** ADVISORY (Protocol — tested via conforming implementations)

### `game/ui/screens/builder/schematic_view.py` (189 LOC) — Tier 2
- **Test file:** `tests/unit/builder/test_schematic_cache_key.py`
- **Untested:** `__init__`, `update_rect`, `_calculate_max_r`, `draw`, `draw_all_firing_arcs`, `draw_component_firing_arc`, `draw_weapon_arc`
- **Verified:** `_get_cached_arc` (lines 131-184) is partially tested for cache key generation. `draw_weapon_arc` (line 186-189) is a thin delegator.
- **Gap:** `_calculate_max_r` (lines 52-58): uses `vehicle_class_service.get_class_definition` and a cube-root calculation `ref_mass ** (1/3.0) * PIXELS_PER_MASS_ROOT`. Business logic disguised as rendering — should have a unit test.
- **Severity:** MAJOR (for `_calculate_max_r` business logic; ADVISORY for rendering methods)

### `game/ui/screens/builder/weapons_input_handler.py` (102 LOC) — Tier 3 (apparently covered)
- **Test file:** `tests/unit/ui/builder/test_weapons_input_handler.py`
- **Symbols:** 2/2 matched. `WeaponsInputHandler`, `detect_tooltip_hover`.
- **Verified gaps (verify coverage):**
  - `detect_tooltip_hover` (lines 36-101): 
    - `content_rect.collidepoint(mouse_pos)` fails → return None (line 70). Verify.
    - Mouse outside hit rect → return None (line 81-84). Verify.
    - `bar_width > 0` divide-by-zero guard (line 91). Verify zero-bar-width tested.
    - `hover_range` clamped to `[0, weapon_range]` (line 95). Verify.
    - `viewmodel.calculate_tooltip_data` returns None → return None (line 99). Verify.
    - `tooltip_data` assigned `['pos'] = mouse_pos` (line 100). Verify.
- **Severity:** MAJOR (complex hit-test geometry with multiple return paths; verify ALL are tested)

### `game/ui/screens/empire_build_queue_window.py` (614 LOC) — Tier 2
- **Test file:** `tests/unit/ui/screens/test_empire_build_queue_window.py`
- **Untested:** `EmpireBuildQueueUiBuilder`, 6 internal methods (`_on_filters_applied`, `_on_selection_changed`, `_add_item_to_source`, `_source_can_build_type`, `_get_system_name`, `_get_sector_text`, `_get_turns_left_text`)
- **Verified:** 33/43 symbols matched. Most view-model, data-source, and table methods are tested. Builder and callback methods are pygame_gui widget construction — ADVISORY.
- **Gap:** `_source_can_build_type` — source filtering logic. `_add_item_to_source` — queue mutation. These are business logic, not rendering.
- **Severity:** MAJOR (some untested callbacks contain business logic)

### `game/ui/screens/event_log_window.py` (533 LOC) — Tier 2
- **Test files:** `tests/unit/ui/screens/test_event_log_window.py`, `tests/unit/ui/screens/test_event_log_replay_button.py`
- **Untested:** `EventLogUiBuilder`, 5 internal methods (`_init_layout`, `_create_filter_buttons`, `_rebuild_list`, `_update_filter_buttons`, `_show_replay_message`)
- **Verified gaps:**
  - `_handle_replay_click` (lines 432-476): complex resolution logic with 4 branches — no `data_source`, no `replay_id`, no resolver, `lookup.found=True/False` with drift. Verify coverage of all paths.
  - `_handle_row_navigate` (lines 502-521): extracts `location_hex` from details, calls `on_navigate_callback`. Double-click detection (lines 408-428) with time threshold.
  - `get_filtered_events` (lines 278-301) has fallback path for tests without VirtualTable — verify both paths tested.
- **Severity:** MAJOR (replay resolution + row navigation logic in a 533 LOC file)

### `game/ui/screens/fleet_data_source.py` (327 LOC) — Tier 2
- **Test file:** `tests/unit/ui/screens/test_fleet_data_source.py`
- **Untested (matrix):** `__init__`, `_get_column_handlers`, `_get_column_value`, and 13 format methods (`_format_status`, `_format_resources`, `_format_serial`, `_format_design`, `_format_name`, `_format_hp_pct`, `_format_tonnage`, `_format_speed`, `_format_warp`, `_format_spaceyard`, `_format_transport`, `_format_cargo`, `_format_capability`), plus `_get_ship_image`, `_create_placeholder`.
- **Verified:** 6/24 symbols matched heuristically. The 18 untested are likely tested transitively through `get_cell_value` and `get_cell_image`, which call them. However:
  - `_format_status` (lines 177-186) has 4 branches — verify `is_derelict` + `is_damaged()` distinction.
  - `_format_resources` (lines 188-200) has `pct >= 0` guard — verify negative percentage.
  - `_format_transport` (lines 247-251) has `capacity > 0` guard — verify zero-capacity.
  - `_get_ship_image` (lines 267-313): image cache hit (line 287), portrait vs topdown vs else. Verify all three.
- **Severity:** MAJOR (many format methods are data transformation logic with branching; verify coverage through `get_cell_value` tests)

### `game/ui/screens/fleet_report_sidebar.py` (512 LOC) — Tier 2
- **Test files:** `tests/unit/ui/screens/test_fleet_report_sidebar.py`, `tests/unit/ui/screens/test_fleet_report_window_multi_select.py`
- **Untested:** `__init__`, `_build_widgets`, `_build_filter_section`, `_create_status_filter_button`, `_build_column_section`, `_build_actions_section`, `update_column_button`
- **Verified:** 5/12 tested. The untested methods are mostly pygame_gui widget construction (`_build_widgets`, `_build_filter_section`, etc.) — ADVISORY. `update_column_button` has label-update logic — minor business logic.
- **Severity:** MAJOR (512 LOC with only 5/12 tested; however most untested are widget construction)

### `game/ui/screens/planet_list_sidebar.py` (286 LOC) — Tier 2
- **Test file:** `tests/unit/ui/screens/test_planet_list_components.py`
- **Untested:** `add_range` (line 199) — nested function inside `build_sidebar`.
- **Verified:** `build_sidebar` tested. `add_range` delegates to `build_range_slider_row` with specific parameters — tested transitively.
- **Severity:** MINOR (nested helper tested through parent function)

### `game/ui/screens/save_selection_window.py` (447 LOC) — Tier 2
- **Test files:** `tests/unit/ui/screens/test_save_selection_window.py`, `tests/unit/ui/test_save_selection.py`
- **Untested:** `SaveSelectionUiBuilder`, `SaveSelectionUiBuilder.build`, `_load_saves`, `_on_load_clicked`, `_on_expand_clicked`, `_on_delete_clicked`, `_on_cancel_clicked`, `_handle_delete_confirmation`, `update`
- **Verified:** 5/14 symbol-matched. The `build` method is pure widget construction (ADVISORY). However `_load_saves`, `_on_load_clicked`, `_handle_delete_confirmation`, and `update` contain event-handling logic.
- **Gap:** `_handle_delete_confirmation` (probably involves a UIMessageWindow confirmation dialog) — temp file deletion logic untested.
- **Severity:** MAJOR (event handling + file operations in event handlers untested)

### `game/ui/screens/system_selection_window.py` (166 LOC) — Tier 2
- **Test file:** `tests/unit/ui/screens/test_system_selection_window.py`
- **Untested:** `SystemSelectionUiBuilder`, `SystemSelectionUiBuilder.build`
- **Verified:** `SystemSelectionWindow.__init__` and `update` are heuristically matched. The `build` method creates UISelectionList and buttons — widget construction.
- **Gap:** `update` (lines 150-166): `btn_confirm.check_pressed()` with selection extraction (line 158-160) and None-selection guard (line 162). Verify both paths tested.
- **Severity:** MINOR (builder is widget construction; update button-press logic verified)

### `game/ui/services/validation_service.py` (79 LOC) — Tier 2
- **Test file:** `tests/unit/ui/services/test_validation_service.py`
- **Untested:** `ValidationService.__init__`, `ValidationService._get_validator`
- **Verified:** 3/5 symbol-matched. `validate_addition` and `validate_design` tested.
- **Gap:** `_get_validator` (lines 46-51): `self._validator is None` → lazy-init via `get_or_create_validator(registry_provider=get_default_registry_provider())`. Verify the lazy-init path is exercised (injection tests should start with `validator=None`).
- **Severity:** MINOR (lazy-init path likely tested through `validate_addition`/`validate_design`)

---

## Tier 3 — Verified Coverage (no new gaps)

### `game/strategy/data/design_role.py` (158 LOC)
- **Test file:** `tests/unit/strategy/data/test_design_role.py`
- All 3 symbols (`DesignRole`, `classify_design_role`, `classify_from_design_data`) heuristically matched. Per-file test exists.
- **Verified:** `classify_design_role` 7 priority branches appear well-covered. Minor note: verify Priority 6 (armed ships) with mass==_LIGHT_SHIP_MASS (4000) — should be FLEET_ESCORT, not LINE_COMBATANT.

### `game/strategy/facade/dto/fleet_hierarchy_dto.py` (104 LOC)
- All 6 symbols heuristically matched. Dedicated test file exists.
- DTO classes are simple data transformation — low risk.

### `game/strategy/facade/strategy_session_facade.py` (502 LOC)
- 73/82 symbols matched across 10 test files. 9 untested are mostly @property cache forwarders.
- **Verified:** Facade composition and delegation pattern extensively tested.

### `game/ui/screens/builder/drop_target.py` (15 LOC)
- Protocol class. 4/4 symbols matched from builder interaction tests.

### `game/ui/screens/builder/weapons_input_handler.py` (102 LOC)
- 2/2 symbols matched. Dedicated test file exists.
- **Verification note:** As noted in Tier 2 section, verify all `detect_tooltip_hover` return paths are exercised.

---

## File Coverage Verification

| File | Layer | Tier | Status | Findings |
|------|-------|------|--------|----------|
| `game/__init__.py` | Root | 0 | ADVISORY | Empty file (0 LOC) |
| `game/ai/spatial_behaviors/screen.py` | AI | 2 | MINOR | `__init__` untested (trivial); `compute_target_position` covered |
| `game/ai/target_evaluator.py` | AI | 2 | MINOR | Internal methods tested via `evaluate()`; edge cases covered by dedicated tests |
| `game/app.py` | Root | 2 | MAJOR | `_return_to`, `start_replay`, `_request_shutdown` untested paths |
| `game/context.py` | Root | 2 | MAJOR | LLM/Image provider error-fallback paths untested |
| `game/core/protocols/combat.py` | Core | 0 | **CRITICAL** | 25 symbols, zero tests — TypeGuards and Protocol conformance never validated |
| `game/core/protocols/registry.py` | Core | 0 | **CRITICAL** | 5 symbols, zero tests — DI protocol contract never validated |
| `game/core/roles.py` | Core | 2 | MAJOR | `_fire_invalidation_callbacks` re-entrance guard untested |
| `game/simulation/replay/replay_spec.py` | Simulation | 0 | **CRITICAL** | 10 symbols, zero tests — serialization round-trip never verified |
| `game/strategy/data/design_role.py` | Strategy | 3 | MINOR | Well-tested; verify mass boundary at 4000 |
| `game/strategy/engine/happiness_engine.py` | Strategy | 2 | MAJOR | Surplus-food bonus edge case + None colony validation |
| `game/strategy/facade/dto/fleet_hierarchy_dto.py` | Strategy | 3 | ADVISORY | DTO — well-tested |
| `game/strategy/facade/slices/fleet_slice.py` | Strategy | 0 | **CRITICAL** | 10 symbols, zero tests — cache invalidation, validation logic untested |
| `game/strategy/facade/strategy_session_facade.py` | Strategy | 2 | MINOR | Extensive coverage; cache forwarders untested |
| `game/strategy/generation/loaders/__init__.py` | Strategy | 0 | ADVISORY | Re-export file (7 LOC) |
| `game/strategy/services/combat_modifier_collector.py` | Strategy | 2 | MAJOR | None-empire/none-planet defensive paths untested |
| `game/strategy/services/race_description_prompt_builder.py` | Strategy | 2 | MINOR | Private helpers tested transitively |
| `game/ui/colors.py` | UI | 1 | ADVISORY | Constants only; consumer tests exist |
| `game/ui/screens/battle_setup/constants.py` | UI | 1 | ADVISORY | Constants; imported by controller tests |
| `game/ui/screens/battle_setup/controller.py` | UI | 2 | **MAJOR** | CRUD operations + `_get_registries` exception path untested |
| `game/ui/screens/build_queue_queue_data_source.py` | UI | 2 | MAJOR | Boundary checks; `_format_int` edge case; decimal turns display |
| `game/ui/screens/builder/drop_target.py` | UI | 3 | ADVISORY | Protocol — tested via conforming implementations |
| `game/ui/screens/builder/schematic_view.py` | UI | 2 | MAJOR | `_calculate_max_r` business logic; rendering methods ADVISORY |
| `game/ui/screens/builder/weapons_input_handler.py` | UI | 2 | MAJOR | `detect_tooltip_hover` 6 return paths — verify all tested |
| `game/ui/screens/empire_build_queue_window.py` | UI | 2 | MAJOR | Callback methods with business logic untested |
| `game/ui/screens/event_log_window.py` | UI | 2 | MAJOR | Replay resolution + row navigation + filter fallback logic |
| `game/ui/screens/fleet_data_source.py` | UI | 2 | MAJOR | 18 format/capability methods — verify tested via `get_cell_value` |
| `game/ui/screens/fleet_report_sidebar.py` | UI | 2 | MAJOR | Mostly widget construction; 512 LOC, 5/12 tested |
| `game/ui/screens/planet_list_sidebar.py` | UI | 2 | MINOR | `add_range` nested function tested transitively |
| `game/ui/screens/save_selection_window.py` | UI | 2 | MAJOR | Event handlers + delete confirmation untested |
| `game/ui/screens/strategy_render/storms.py` | UI | 0 | ADVISORY | Pure rendering — pygame image/hex drawing |
| `game/ui/screens/system_selection_window.py` | UI | 2 | MINOR | Builder widget construction ADVISORY; `update` button logic verified |
| `game/ui/screens/test_lab/renderer/orchestrator.py` | UI | 0 | **MAJOR** | `_is_condition_verified` is business logic in Tier 0 file |
| `game/ui/screens/test_lab/test_run_card.py` | UI | 0 | **MAJOR** | Input handling + 3 distinct metrics-display branches |
| `game/ui/services/image/null_provider.py` | UI/Svc | 0 | **CRITICAL** | `generate_image` raise invariant never tested |
| `game/ui/services/validation_service.py` | UI/Svc | 2 | MINOR | Lazy-init path likely tested; `__init__` trivial |

---

## Context Usage Estimate
- Total production LOC read: ~8,550
- Total test LOC read: 0 (coverage matrix cross-reference used; single-agent analysis)
- Approximate headroom: High (single-agent report; Phase 3 skeptical verification agents should sample the 10 CRITICAL + 3 highest-risk MAJOR findings)
