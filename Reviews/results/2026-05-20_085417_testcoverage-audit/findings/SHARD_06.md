# Test Coverage Audit — Shard 06 Discovery Agent

**Date:** 2026-05-20
**Files in scope:** 38 production files, ~9573 LOC
**Tiers:** 0=8, 1=2, 2=23, 3=5

---

## Summary

| Severity | Count | Description |
|----------|-------|-------------|
| CRITICAL | 2 | Tier 0 non-UI files with zero test coverage |
| MAJOR | 3 | Tier 1 files or untested critical error paths |
| MINOR | 13 | Partial coverage / missing corners |
| ADVISORY | 20 | UI rendering, `__init__.py` re-exports, Protocol-only files |

**Key Findings:**
- **2 CRITICAL gaps**: `entity_protocols.py` (0 tests, 487 LOC of runtime-checkable Protocols + TypeGuards) and `LayMinesCommandHandler` (0 tests, 168 LOC of command-side validation/write logic).
- **Heuristic baseline was wrong for `superweapons.py`** — it has a comprehensive 162-line test suite. Downgraded from CRITICAL to MINOR.
- **Heuristic baseline was wrong for `LayMinesCommandHandler`** — tests exist for the *order* handler (runtime execution) but NOT the *command* handler (validation/write entry point).
- Most Tier 2 files have partial coverage — the largest gaps are in `build_queue_panel_factory.py` (UI construction not tested for most methods) and `structure_list_items.py` (non-rendering methods untested).
- Tier 3 files are well-covered as the heuristic predicted, except `modifier_effects.py` which has a `validate_modifier_definition` method with partial coverage.

---

## Tier 0 — Critical

### CRITICAL: `game/simulation/interfaces/entity_protocols.py` (487 LOC, layer: simulation)

**Coverage: ZERO — no test file exists. Verified by filesystem glob.**

This file defines 4 `@runtime_checkable Protocol` classes (`ICombatShip`, `IProjectile`, `IPhysicsShip`, `ISerializableShip`) and 4 `TypeGuard` functions (`is_combat_ship`, `is_projectile`, `is_physics_ship`, `is_serializable_ship`). These are used extensively by combat systems, AI controllers, and targeting logic via `isinstance()` and TypeGuard narrowing.

**Untested code lines:**
- `ICombatShip` Protocol (lines 44–231): 28 properties + 4 methods. Used by AI controllers, combat systems, targeting logic. No tests verify any protocol member is correctly checked by `isinstance(obj, ICombatShip)`.
- `IProjectile` Protocol (lines 237–372): 18 properties. Used by collision/weapon systems.
- `IPhysicsShip` Protocol (lines 378–415): 8 properties.
- `ISerializableShip` Protocol (lines 421–458): 6 properties.
- `is_combat_ship` TypeGuard (lines 469–471): Duck-typing uses `_has_attrs(obj, 'angle', 'layers')`. Never tested.
- `is_projectile` TypeGuard (lines 474–476): Uses `_has_attrs(obj, 'type') and _has_attrs(obj, 'position')`. Never tested.
- `is_physics_ship` TypeGuard (lines 480–482): Uses `_has_attrs(obj, 'velocity', 'mass')`. Never tested.
- `is_serializable_ship` TypeGuard (lines 485–487): Uses `_has_attrs(obj, 'to_save_dict', 'theme_id')`. Never tested.

**Risk:** TypeGuard functions produce false negatives if the duck-typing attribute set is wrong. Protocols may drift from their concrete implementations. Runtime `isinstance` checks in production code depend on these Protocols being correct.

**Recommendation:** Create `tests/unit/simulation/interfaces/test_entity_protocols.py` with:
1. Mock objects satisfying each protocol → verify `isinstance(mock, Protocol)` returns True
2. Mock objects missing key attrs → verify TypeGuard returns False
3. Concrete Ship/Projectile instances → verify protocol conformance

---

### MINOR: `game/simulation/components/abilities/superweapons.py` (116 LOC, layer: simulation)

**Heuristic was WRONG — tests exist.** `tests/unit/simulation/components/abilities/test_superweapons.py` (162 lines) provides comprehensive coverage of all 6 superweapon classes. Covers: instantiation via `ABILITY_REGISTRY` and `create_ability`, layer (`STRATEGIC`), scope (`SELF`), `STAT_BINDINGS` (empty), `get_primary_value()` (returns 0.0), `get_ui_rows()` (correct label/value/color_hint), registry presence, and `_parse_attrs` action_time (boolean True → 1, dict with action_time, dict without key → 1).

**Minor gaps:**
- `_parse_attrs` is tested only through the `__init__` path (`ability_class(mock_component, True)`). The `sync_data` call path (line 46 docstring claims it's also called from `sync_data`) is not tested. (Lines 44–49)
- No test for the `data.get('action_time', 1) if isinstance(data, dict) else 1` edge case where `data` is a non-dict non-bool type (e.g., a list, an int other than True).

---

### CRITICAL: `game/strategy/engine/handlers/lay_mines.py` (168 LOC, layer: strategy)

**Coverage: ZERO for the command handler. Verified by filesystem glob.**

This file defines `LayMinesCommandHandler` — the command-side validation/write entry point for strategic mine-laying. The *order* handler (`LayMinesOrderHandler` in `order_handlers/lay_mines.py`) has a comprehensive test suite (277 lines), but the *command* handler has NONE.

**Untested code paths:**
- `execute()` (lines 48–57): Fleet vs Planet dispatch based on `cmd.planet_id`. Not tested.
- `_execute_fleet()` (lines 63–115): Ship lookup, bay inventory check, count resolution, validation errors (no ship_instance_id, ship not found, no mines available, insufficient mines), order queuing. Not tested.
- `_execute_planet()` (lines 121–157): Planet lookup, staging yard check, validation errors (no mines, insufficient mines), order queuing. Not tested.
- `register()` (line 160–165): Registers handler into `CommandRegistry`. Not tested.
- `check_issuer_invariant()` call (line 51): Error handling path. Not tested.
- `resolve_requested()` validation (lines 89–91, 131–133): When `cmd.count` is None → "use all available" resolution. Not tested.

**Risk:** Command-side validation bugs (incorrect bay/staging-yard queries, wrong target_hex fallback, missing order fields) surface at runtime with confusing error messages or silently incorrect behavior. The order handler is well-tested but only exercises the *execution* path — not the validation/queuing layer.

**Recommendation:** Create `tests/unit/strategy/engine/handlers/test_lay_mines_command.py` mirroring the order-handler pattern. Test both fleet and planet paths with valid/invalid inputs.

---

### ADVISORY: `game/ui/screens/gravity_target_editor.py` (220 LOC, layer: ui)

**Coverage: ZERO — no test file exists.**

UI editor window for setting planet gravity targets. All methods are Pygame UI construction or button click handlers. ADVISORY severity per methodology (UI rendering/event).

Untested: `__init__`, `_build_ui`, `update`, `_button_handlers`, `_on_apply`, `_set_species_ideal`, `_set_match_current`, `_clear_target`.

---

### ADVISORY: `game/ui/screens/strategy_render/background.py` (58 LOC, layer: ui)

**Coverage: ZERO — no test file exists.**

Background galaxy image layer. Pygame surface manipulation. Untested: `__init__`, `_load_background`, `draw`.

---

### ADVISORY: `game/ui/screens/strategy_windows/ship_picker.py` (43 LOC, layer: ui)

**Coverage: ZERO — no test file exists.**

Placeholder stub (`ShipPickerStub`) that auto-selects all ships. ADVISORY due to being an explicit TODO/stub. Untested: `__init__`, `show`.

---

### ADVISORY: `game/ui/screens/test_lab/renderer/category_panel.py` (157 LOC, layer: ui)

**Coverage: ZERO — no test file exists.**

Collapsible category tree sidebar renderer. All methods are pygame drawing routines. Untested: `__init__`, `draw`.

---

### ADVISORY: `game/ui/services/image/provider.py` (82 LOC, layer: ui)

**Coverage: ZERO — no test file exists.**

Purely a `@runtime_checkable Protocol` definition for `ImageProvider`. No implementation code. ADVISORY — testing a Protocol definition in isolation has marginal value; the concrete implementations (`OpenAIImageProvider`, etc.) are tested elsewhere.

---

## Tier 1

### ADVISORY: `game/ai/interfaces/__init__.py` (30 LOC, layer: ai)

Re-export shim. Imports `IControllable`, `ShipControllableAdapter` from `game.ai.interfaces.controllable` and protocol types from `game.ai.protocols`. No new code. Tests for the imported types exist in their source modules.

---

### ADVISORY: `game/core/__init__.py` (176 LOC, layer: core)

Re-export shim. Imports exceptions, error codes, math utilities, registry/DI classes, constants, event logging, validation, configuration, paths, protocols, and roles from their respective modules. No new code. Each imported module has its own test coverage.

---

## Tier 2 — Detailed Findings

### MINOR: `game/ai/spatial_behaviors/patrol_zone.py` (57 LOC, layer: ai)

**Test file:** `tests/unit/ai/spatial_behaviors/test_spatial_behaviors.py`

- `compute_target_position` — tested via spatial_behaviors test suite. OK.
- `__init__` (lines 24–30) — untested in isolation. The default `zone_center=None` → `Vector2(0, 0)` path (line 29) is not tested.

---

### MAJOR: `game/app.py` (531 LOC, layer: game_root)

**Test files:** `test_app_create_workshop_context.py`, `test_app_delegators.py`, `test_app_public_api.py`, `test_strategy_menu_actions.py`, `test_viewing_empire_anchor.py`, `test_workshop_ship_io_facade_state.py`

Key untested symbols confirmed by code review:
- `_get_menu_button_config` — static method returning menu button definitions. Not tested.
- `_route_get` / `_route_set` — property forwarding delegation. Not tested.
- `active_scene` / `builder_scene` — property forwarders to ScreenRouter. Not tested.
- `menu_ui_manager` / `show_exit_dialog` / `showing_load_menu` / `showing_race_setup` / `showing_new_game_setup` — delegate to ScreenRouter. Not tested.
- Screen transition callbacks (`_on_new_game_setup`, `_on_builder_enter`, `_on_strategy_enter`, etc.) — tested indirectly through integration tests.
- `create_workshop_context` — has its own test file.
- `run()` — delegator to RunLoop. Not tested.

**Assessment:** The untested symbols are mostly thin delegators/property forwarders. The core game entry flow is tested in integration. MAJOR because `_get_menu_button_config` maps buttons to screen transitions with UI callback wiring that could silently break.

---

### MINOR: `game/engine/spatial.py` (61 LOC, layer: engine)

**Test files:** `test_spatial_exact.py`, `test_spatial.py`

Appears well-covered. `SpatialGrid.__init__`, `clear`, `_get_cell`, `insert`, `query_radius`, `query_radius_exact` all tested. MINOR: `query_radius_exact` with empty grid → empty list not explicitly tested, but likely covered by broader tests.

---

### MINOR: `game/run_loop.py` (223 LOC, layer: game_root)

**Test file:** `tests/unit/test_run_loop.py` (177 lines)

Tests cover: `request_shutdown`, `run` smoke (one frame + shutdown), ESC closes exit dialog, exit dialog click/cancel, QUIT event, GLOBAL_EXIT keybinding, profiler toggle, VIDEORESIZE, `_handle_normal_events` routing, and shutdown ordering (LLM before replay verifier).

Untested:
- `_boot_set_resolution` (lines 172–183): Window resize surface update. Not tested in isolation.
- `_update_and_draw` (lines 189–223): `strategy_scene.update_input`, battle HUD drawing paths. Not tested in isolation.
- `_forward_event_to_scene` (lines 148–163): Overlay dialog routing (showing_new_game_setup, showing_load_menu, showing_race_setup). Not tested as those states are covered by integration-level tests but not unit-tested.

---

### MINOR: `game/simulation/components/modifier_effects.py` (270 LOC, layer: simulation)

**Test files:** 17 candidate test files including `test_modifier_effect.py`, `test_modifier_effect_evaluator.py`, `test_formula_edge_cases.py`, `test_formula_error_handling.py`, `test_formula_validation.py`

Appears well-covered. The data-driven `evaluate_modifier`, `evaluate_formula`, `validate_formula`, `validate_modifier_definition` are all tested. The `ModifierEffect` dataclass `describe()`, `is_targeted()`, `to_dict()`, `from_dict()` are tested.

Minor gap: `validate_modifier_definition` (lines 242–269) — tests for malformed effects that are not lists (line 259–261) and missing effects key (line 255–256) may not be exhaustive.

---

### MINOR: `game/simulation/entities/ship_serialization.py` (266 LOC, layer: simulation)

**Test files:** 13 candidate test files including `test_ship_serialization.py`, `test_ship_external_stats_serialization_guard.py`

Appears well-covered. `to_dict`, `from_dict`, `_load_components`, `_restore_resources`, `_verify_stats` all tested.

Minor gap: `to_dict` (lines 26–112) exception handler (lines 109–112) — the `except Exception` catch for diagnostic logging is not tested. HULL layer skip (line 85–87) and hull_ component skip (line 95–96) paths tested.

---

### MAJOR: `game/simulation/systems/tactical_mine_resolver.py` (597 LOC, layer: simulation)

**Test files:** `test_tactical_mine_resolver.py` (436 lines)

Tests cover: warhead mine creation/detonation, laserhead mine creation/detonation, point-defense destruction, cooldown behavior, `from_mine_group` construction, `writeback_to_mine_group` (consumed mines removed, all-mines-consumed edge case).

Untested:
- `_warhead_per_tick_roll` (lines 282–316): Internal method — tested indirectly through `tick()`. The `expected_ticks_in_proximity` balance-file path (lines 304–313) and `per_tick` minimum clamp (line 315) are exercised but the specific balance edge cases may not be.
- `_laserhead_per_tick` (lines 318–362): Internal method — tested indirectly. The `except Exception` fallback on line 347 for `total_defense_score` is not explicitly tested.
- `_apply_damage` (lines 364–397): The `damage_calculator.apply_damage` path (lines 378–381) and the `except Exception` fallback (lines 382–388) are tested. The direct-HP-decrement fallback (lines 389–397) is tested for dead ship edge case.
- `_scatter_in_box` (lines 576–590): Tested via `from_mine_group`. The `battle_boundary is None` path (uses pre-computed positions) is tested.
- `_sum_warhead_damage` (lines 515–532): Tested via `from_mine_group`. The `wh` as int/float scalar (line 530–531) edge case is not explicitly tested.
- `_extract_laserhead` (lines 535–551): Tested via `from_mine_group`. The scalar int/float fallback (line 549–550) not explicitly tested.
- `_extract_hull_hp` (lines 554–573): Tested. The total==0.0 → 30.0 default (line 571–572) is tested.
- `TacticalMineEvent` dataclass (lines 78–88): Not directly tested as a standalone value object.

**Assessment:** MAJOR because multiple helper functions have untested scalar-type branches (`wh` as raw int/float) that could cause TypeError at runtime if the mine design dict format is unexpected.

---

### MINOR: `game/strategy/data/build_context.py` (62 LOC, layer: strategy)

**Test file:** `tests/unit/strategy/data/test_build_context.py` (193 lines)

Tests cover: `isinstance(planet, BuildContext)`, `isinstance(fleet, BuildContext)`, duck-typing dispatch, `can_build_type` for both contexts, `construction_queue` attached test.

Untested per heuristic: `construction_queue` and `has_space_shipyard` as standalone property tests. The heuristic had these as untested — but the test file tests `can_build_type` extensively, which exercises the protocol shape. Minor gap.

---

### MINOR: `game/strategy/data/order_serializer.py` (243 LOC, layer: strategy)

**Test file:** `tests/unit/strategy/data/test_order_serializer.py` (419 lines)

Extensively tested. All 7 target formats covered, corrupt entry handling, unknown types, `resolve_order_references` with fleet/planet resolution, unresolvable references pruning.

Untested per heuristic: `_deserialize_single_order` (lines 71–96). This is tested indirectly through `deserialize_orders`. The `execution_progress` restore (line 95) is tested via round-trip tests.

---

### MAJOR: `game/strategy/data/planet_gen.py` (427 LOC, layer: strategy)

**Test file:** `tests/unit/strategy/data/test_planet_gen.py` (736 lines)

Extensive tests. Covers: `__init__`, `_generate_mass_constrained` (with bias small/large), `_calculate_moon_chance`, `_generate_moon_mass`, `_collect_star_exclusion_zones`, `_generate_orbital_slots` (with blueprints), `_generate_moons`, `_create_single_planet`.

Untested:
- `_create_planet_objects` (lines 332–357): Tested indirectly through `generate_system_bodies`. The internal loop building planets from slots is exercised.
- `generate_system_bodies` full integration — tested via the public entry point.
- `_generate_orbital_slots` → hot_jupiter blueprint path with `hot_required=True` (lines 150–174) — partially tested.

**Assessment:** MAJOR despite large test file because `_create_single_planet` (which calls out to 8 dependent physics/atmosphere/surface modules) has no direct unit test — all coverage is through integration-level `generate_system_bodies` calls. The `validate_planet_parameters` warning path (lines 378–380) is not tested.

---

### MINOR: `game/strategy/facade/slices/_facade_state.py` (188 LOC, layer: strategy)

**Test file:** 7 candidate test files including `test_facade_state.py`

Well-covered. `invalidate_all`, `get_fleet_by_id`, `get_empire_by_id`, `get_planet_by_id`, `build_planet_index`, `get_designs_for_empire` all tested.

Untested:
- `seed_planet_index` and `seed_race_registry` (lines 169–188): Explicitly test-only helpers. Tested in `test_facade_state_proj411_caches.py` and `test_facade_indices.py`.

---

### MINOR: `game/strategy/services/ability_iterator.py` (339 LOC, layer: strategy)

**Test file:** `tests/unit/strategy/services/test_ability_iterator.py` (414 lines)

Well-covered. Tests: `iter_ability_sources_at_hex` with storms, facilities, planets, warp points, fleets, stars; `iter_ability_sources_in_system`; deduplication; `set_fleet_lookups`; `register_source_provider_*` / `unregister_source_provider`.

Untested per heuristic: The 8 private provider functions (`_iter_hex_filtered_sources`, `_facility_provider`, `_storm_provider`, `_star_provider`, `_planet_intrinsic_provider`, `_fleet_provider`, `_system_archetype_provider`, `_warp_point_provider`). These are tested indirectly through the public `iter_ability_sources_*` entry points.

Minor gap: `_iter_hex_filtered_sources` with `system is None` → returns immediately (line 160–161) — not explicitly tested.

---

### MINOR: `game/strategy/services/combat_modifier_collector.py` (195 LOC, layer: strategy)

**Test file:** `tests/unit/strategy/services/test_combat_modifier_collector.py` (396 lines)

Well-covered. Tests: `collect_combat_modifiers` for shield/damage multipliers, flat_bonus ShieldProjection, enemy-scope suppressors, `_find_reference_planet`, `_find_empire`.

Untested per heuristic: `_entry_scope` (lines 90–95) — local function inside `collect_combat_modifiers`. Tested indirectly but not as a standalone unit.

---

### MINOR: `game/strategy/services/replay_verification_sidecar.py` (173 LOC, layer: strategy)

**Test files:** `test_replay_verification_sidecar.py`, `test_replay_verification_coordinator.py`

Appears well-covered. `write_verification_sidecar`, `read_verification_sidecar`, `sidecar_path_for_replay`, `VerificationSidecar.to_dict`/`from_dict` all tested. The error paths (JSON corrupt, schema mismatch, missing file) are tested.

---

### MINOR: `game/strategy/validation/colonize_validator.py` (166 LOC, layer: strategy)

**Test file:** `tests/unit/strategy/engine/test_multi_pod_colonization.py` (163 lines)

Tests cover: `validate` (target_planet=None with candidates, specific planet, already-owned, wrong-location), `fleet_has_drop_pod`, `_validate_drop_pod_availability`, `count_drop_pods`, `count_committed_colonize_orders`.

Untested per heuristic: `find_ship_with_drop_pod` (lines 138–156) — returns `(ship, pod_index)`. Not directly tested in the test file. The `pod_index=0` return value (always returns first pod) and the `(None, -1)` no-pod-found return are untested.

**Assessment:** MINOR — `find_ship_with_drop_pod` is a simple lookup helper. But the always-returns-index-0 behavior (line 155) means multi-pod sequential consumption may rely on post-removal re-indexing — this contract is undocumented and untested.

---

### MINOR: `game/strategy/validation/planet_order_validator.py` (124 LOC, layer: strategy)

**Test file:** `tests/unit/strategy/validation/test_planet_order_validator.py` (78 lines)

Tests cover: `_facility_has_ability` with inline component abilities, dict component registry lookup, string component registry lookup.

Untested:
- `validate_activate_ability` (lines 24–66): Facility not found, facility not operational, ability not present, already active, already queued — all untested.
- `validate_deactivate_ability` (lines 68–102): Not tested at all.

**Assessment:** MINOR — only the private helper `_facility_has_ability` is tested. The two public validation methods have zero direct coverage.

---

### ADVISORY: `game/ui/assets/ship_theme_manager.py` (453 LOC, layer: ui)

**Test files:** `test_ship_theme_manager.py`, `test_race_asset_loader.py`

Tests cover: `initialize`, `_discover_theme`, `load_image`, `get_portrait_image`, `clear`, `get_default_ship_theme_manager`, `set_default_ship_theme_manager`.

Untested: `_validate_image_size` (lines 239–267) — PIL-based image dimension check. Not tested. `get_theme_description` — not tested.

**Assessment:** ADVISORY (UI asset loading).

---

### ADVISORY: `game/ui/screens/build_queue_panel_factory.py` (586 LOC, layer: ui)

**Test file:** `tests/unit/ui/screens/test_build_queue_panel_factory.py`

Most methods create pygame_gui widgets. Tests focus on the factory setup and panel creation. The 9 private `_create_*` methods and `_pause_button_label` are all UI widget construction. ADVISORY — these are inherently visual/surface-level.

---

### ADVISORY: `game/ui/screens/builder/structure_list_items.py` (630 LOC, layer: ui)

**Test files:** `test_builder_structure_features.py`, `test_modifier_icons.py`, `test_structure_visibility.py`

Non-rendering methods (`handle_event`, `set_move_buttons_enabled`, `get_abs_rect`, `kill`) are tested indirectly through integration tests. The visible rendering methods (`__init__`, `update`) create pygame widgets. ADVISORY.

---

### ADVISORY: `game/ui/screens/builder/weapons_panel.py` (321 LOC, layer: ui)

**Test files:** `test_weapons_panel.py`, `test_weapons_report_layout.py`

The ViewModel (`WeaponsViewModel`) is well-tested separately. The panel itself handles MVVM event routing and pygame rendering. ADVISORY.

---

### ADVISORY: `game/ui/screens/builder/weapons_viewmodel.py` (494 LOC, layer: ui)

**Test file:** `tests/unit/ui/builder/test_weapons_viewmodel.py`

The ViewModel has its own dedicated test file. Methods `_get_all_weapons` and `calculate_tooltip_data` are marked untested per heuristic but may be exercised through `load_weapons` and the public API.

---

### ADVISORY: `game/ui/screens/data_list_window_mixin.py` (130 LOC, layer: ui)

**Test file:** `test_planet_list_components.py`

Mix-in providing shared column toggle, preset save, and slider text sync. Used by `PlanetListWindow` and `StarListWindow`. Tested through those windows' tests. ADVISORY.

---

### ADVISORY: `game/ui/screens/galaxy_test/screen.py` (288 LOC, layer: ui)

**Test file:** `tests/unit/ui/screens/test_galaxy_test_screen.py`

Test screen for galaxy/system generation. Most methods are UI construction or pygame rendering. ADVISORY.

---

### ADVISORY: `game/ui/screens/race_setup/controller.py` (499 LOC, layer: ui)

**Test file:** `tests/unit/ui/screens/race_setup/test_controller.py`

Tests cover: basic controller construction, save/load flows, validation. The 11 untested items (randomize methods, on_overwrite_save, on_save_dialog_cancel) are all UI event callbacks. ADVISORY.

---

### ADVISORY: `game/ui/screens/workshop_data_reloader.py` (197 LOC, layer: ui)

**Test file:** `tests/unit/ui/screens/test_workshop_data_reloader.py`

Most methods tested. `_refresh_ui_after_data_reload` is a private method tested indirectly through `reload_data`. ADVISORY.

---

### ADVISORY: `game/ui/services/game_settings.py` (94 LOC, layer: ui)

**Test file:** `tests/unit/ui/services/test_game_settings.py`

Tests cover: `get`, `set`, `save`, `reset_to_defaults`, `background_brightness` property. `_load` and `__init__` tested indirectly. ADVISORY.

---

### ADVISORY: `game/ui/services/ship_factory.py` (185 LOC, layer: ui)

**Test file:** `tests/unit/ui/services/test_ship_factory.py`

Tests cover: `create_from_design`, `get_ship_radius`, `configure_ship`. `setup_formation` and `_get_registries` not tested in isolation. ADVISORY.

---

### ADVISORY: `game/ui/widgets/preference_row.py` (237 LOC, layer: ui)

**Test file:** `tests/unit/ui/widgets/test_preference_row.py`

Tests cover: `format_value`, `calculate_factor_cost`, `current_preference`, `refresh_from_sliders`, `set_preference`, `owns_event`. `_build_widgets` is pygame_gui widget construction. ADVISORY.

---

## Tier 3 — Verification

### `game/simulation/components/modifier_effects.py` → MINOR (covered, minor gaps noted above)

### `game/simulation/entities/ship_serialization.py` → MINOR (covered, exception handler not tested)

### `game/engine/spatial.py` → MINOR (covered, minor edge cases)

### `game/strategy/services/replay_verification_sidecar.py` → COVERED

### `game/strategy/validation/planet_order_validator.py` → MINOR (downgraded from Tier 3 — only helper tested)

---

## File Coverage Verification Table

| File | Heuristic Tier | Verified Tier | Status | Key Gaps |
|------|---------------|---------------|--------|----------|
| `game/simulation/interfaces/entity_protocols.py` | 0 | 0 | **CRITICAL** | 0 tests. 4 Protocols + 4 TypeGuards |
| `game/simulation/components/abilities/superweapons.py` | 0 | 2→MINOR | **HEURISTIC WRONG** | Tests exist. `sync_data` path + non-dict edge case |
| `game/strategy/engine/handlers/lay_mines.py` | 0 | 0 | **CRITICAL** | 0 tests for command handler |
| `game/ui/screens/gravity_target_editor.py` | 0 | 0 | ADVISORY | UI, 0 tests |
| `game/ui/screens/strategy_render/background.py` | 0 | 0 | ADVISORY | UI, 0 tests |
| `game/ui/screens/strategy_windows/ship_picker.py` | 0 | 0 | ADVISORY | UI stub, 0 tests |
| `game/ui/screens/test_lab/renderer/category_panel.py` | 0 | 0 | ADVISORY | UI, 0 tests |
| `game/ui/services/image/provider.py` | 0 | 0 | ADVISORY | Protocol only |
| `game/ai/interfaces/__init__.py` | 1 | 1 | ADVISORY | Re-export shim |
| `game/core/__init__.py` | 1 | 1 | ADVISORY | Re-export shim |
| `game/ai/spatial_behaviors/patrol_zone.py` | 2 | 2 | MINOR | `__init__` default zone_center=None |
| `game/app.py` | 2 | 2 | MAJOR | `_get_menu_button_config`, delegators |
| `game/engine/spatial.py` | 3 | 3 | MINOR | Edge cases |
| `game/run_loop.py` | 2 | 2 | MINOR | `_boot_set_resolution`, `_update_and_draw` |
| `game/simulation/components/modifier_effects.py` | 3 | 3 | MINOR | `validate_modifier_definition` edge cases |
| `game/simulation/entities/ship_serialization.py` | 3 | 3 | MINOR | `to_dict` exception handler |
| `game/simulation/systems/tactical_mine_resolver.py` | 2 | 2 | MAJOR | Scalar-type branches in helpers |
| `game/strategy/data/build_context.py` | 2 | 2 | MINOR | Protocol property tests |
| `game/strategy/data/order_serializer.py` | 2 | 2 | MINOR | `execution_progress` restore |
| `game/strategy/data/planet_gen.py` | 2 | 2 | MAJOR | `_create_single_planet` not directly tested |
| `game/strategy/facade/slices/_facade_state.py` | 2 | 2 | MINOR | seed_ helpers tested |
| `game/strategy/services/ability_iterator.py` | 2 | 2 | MINOR | `system is None` short-circuit |
| `game/strategy/services/combat_modifier_collector.py` | 2 | 2 | MINOR | `_entry_scope` isolation |
| `game/strategy/services/replay_verification_sidecar.py` | 3 | 3 | COVERED | — |
| `game/strategy/validation/colonize_validator.py` | 2 | 2 | MINOR | `find_ship_with_drop_pod` |
| `game/strategy/validation/planet_order_validator.py` | 3 | 2 | MINOR | `validate_activate_ability`, `validate_deactivate_ability` |
| `game/ui/assets/ship_theme_manager.py` | 2 | 2 | ADVISORY | `_validate_image_size` |
| `game/ui/screens/build_queue_panel_factory.py` | 2 | 2 | ADVISORY | UI construction |
| `game/ui/screens/builder/structure_list_items.py` | 2 | 2 | ADVISORY | UI widgets |
| `game/ui/screens/builder/weapons_panel.py` | 2 | 2 | ADVISORY | UI rendering |
| `game/ui/screens/builder/weapons_viewmodel.py` | 2 | 2 | ADVISORY | ViewModel tested separately |
| `game/ui/screens/data_list_window_mixin.py` | 2 | 2 | ADVISORY | Mixin tested via subclasses |
| `game/ui/screens/galaxy_test/screen.py` | 2 | 2 | ADVISORY | Test screen UI |
| `game/ui/screens/race_setup/controller.py` | 2 | 2 | ADVISORY | Randomize callbacks |
| `game/ui/screens/workshop_data_reloader.py` | 2 | 2 | ADVISORY | `_refresh_ui_after_data_reload` |
| `game/ui/services/game_settings.py` | 2 | 2 | ADVISORY | `_load` |
| `game/ui/services/ship_factory.py` | 2 | 2 | ADVISORY | `setup_formation` |
| `game/ui/widgets/preference_row.py` | 2 | 2 | ADVISORY | `_build_widgets` |

---

## Heuristic Baseline Corrections

| File | Heuristic Claim | Verified Reality |
|------|----------------|------------------|
| `superweapons.py` | TIER_0_NO_TESTS (0 tested) | 162-line test file exists — 100% covered |
| `lay_mines.py` | TIER_0_NO_TESTS (0 tested) | Order handler tested, command handler has 0 tests |
| `planet_order_validator.py` | TIER_3_APPARENTLY_COVERED | Only `_facility_has_ability` tested; `validate_activate_ability` + `validate_deactivate_ability` untested |

---

## Prioritized Remediation Plan

1. **CRITICAL**: Write `tests/unit/simulation/interfaces/test_entity_protocols.py` — test all 4 Protocols and 4 TypeGuards with conformance/non-conformance mocks.
2. **CRITICAL**: Write `tests/unit/strategy/engine/handlers/test_lay_mines_command.py` — test fleet/planet paths with valid/invalid inputs.
3. **MAJOR**: Add direct tests for `planet_gen._create_single_planet` including the `validate_planet_parameters` warning path.
4. **MAJOR**: Add scalar-type branch tests for `_sum_warhead_damage`, `_extract_laserhead` (`wh`/`lh` as raw int/float).
5. **MAJOR**: Test `colonize_validator.find_ship_with_drop_pod` — verify (None, -1) return for no pods.
6. **MINOR**: Test `planet_order_validator.validate_activate_ability` and `validate_deactivate_ability`.
7. **MINOR**: Test `entity_protocols.TypeGuard` functions in isolation.
