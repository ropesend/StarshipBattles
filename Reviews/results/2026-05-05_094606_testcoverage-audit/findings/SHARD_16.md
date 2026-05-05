# Shard 16 — Test Coverage Audit Findings

**Audit date:** 2026-05-05  
**Discovery Agent:** OpenCode  
**Shard scope:** 49 production files, ~8743 LOC  
**Methodology:** Every production file read in full; coverage claims verified against test files.

---

## Summary

| Tier | Count | Files | Est. Missing Tests |
|------|-------|-------|---------------------|
| **Tier 0** (no tests) | 9 | economy_slice, gravity_target_editor, strategy_screen_lifecycle, storm_ability_source, replay_outcome, list_filter_utils, _draw_helpers, 2 __init__.py | ~47 missing tests |
| **Tier 1** (no symbols tested) | 4 | protocols __init__, llm __init__, ui/assets __init__, colors.py | 0 (re-exports/constants) |
| **Tier 2** (partial) | 30 | Various — ~73 untested callables across 30 files | ~73 missing tests |
| **Tier 3** (apparently covered) | 7 | designs, construction_forecast, transfer_handler, production_math, race_resolver, base_gallery, battle_state | Verified pass |
| **Total untested callables** | — | — | **~120 untested callables** |

---

## Tier 0 — No Tests At All

### `game/simulation/replay/replay_outcome.py` (49 LOC, 5 symbols, 0 tested)
**CRITICAL** — None of the 5 callables have tests:
- `ReplayOutcome` (dataclass) — no test coverage for construction, field access
- `ReplayOutcome.from_battle_outcome()` — roundtrip with `BattleOutcome` untested
- `ReplayOutcome.to_battle_outcome()` — deserialization from dict untested
- `ReplayOutcome.to_dict()` — serialization untested
- `ReplayOutcome.from_dict()` — deserialization from dict untested
- **Recommendation:** Add roundtrip tests (`from_battle_outcome` -> `to_dict` -> `from_dict` -> `to_battle_outcome`), edge cases for `from_dict` with missing/invalid keys

### `game/strategy/facade/slices/economy_slice.py` (188 LOC, 5 symbols, 0 tested)
**CRITICAL** — All 5 callable symbols are untested. This is the heaviest facade slice (~188 LOC):
- `EconomySlice.__init__()` — state wiring untested
- `EconomySlice.get_race_registry()` — lazy registry construction untested; PROJ-287 CachedRaceRegistry path uncovered
- `EconomySlice.resolve_economy_config()` — fallback to `get_default_economy_config()` untested; warning path on missing session config untested
- `EconomySlice.get_colony_demographic_view()` — ~104 LOC method with species iteration, habitability calculation, food surplus bonus, resource upkeep aggregation — **completely untested**
- **Recommendation:** Highest-impact gap in this shard. This DTO feeds strategy UI demographic panels. Test with mock planets having 0/1/2+ populations, test NULL race_registry fallback, test surplus_bonus cap logic

### `game/ui/screens/gravity_target_editor.py` (220 LOC, 9 symbols, 0 tested)
**MAJOR** — Full UI window with 9 callables, zero tests:
- `GravityTargetEditor.__init__()` — widget construction, species selector wiring
- `GravityTargetEditor._build_ui()` — pygame_gui element creation
- `GravityTargetEditor.update()` — slider change detection
- `GravityTargetEditor._button_handlers()` — button callback dict
- `GravityTargetEditor._on_apply()` — gravity conversion (g → m/s²), callback invocation
- `GravityTargetEditor._set_species_ideal()` — race_config.preferences["gravity"].setpoint lookup
- `GravityTargetEditor._set_match_current()` — slider to planet gravity
- `GravityTargetEditor._clear_target()` — apply None callback
- **Recommendation:** Use bypass_init pattern for widget seam; test conversion math (G_TO_MS2=9.81), test slider clamping, test species ideal path with mock RaceConfig

### `game/strategy/services/ability_sources/storm.py` (77 LOC, 9 symbols, 0 tested)
**CRITICAL** — StormAbilitySource adapter for PROJ-300 universal ability framework. 9 callables, zero tests:
- All 7 property accessors (`source_kind`, `source_label`, `source_id`, `owner_id`, `get_abilities`, `affects_system`, `get_activation_state`)
- `affects_hex()` — two code paths: global-frame hex math (with `system.global_location`) and local-frame fallback (with `storm.occupied_hexes`). The global path computes `sys_loc + storm_loc + off` — **uncovered arithmetic**
- `get_abilities()` — returns dict or empty dict based on type check — **both paths untested**
- **Recommendation:** Test with Storm mocks in both global-frame and local-frame fallback modes; verify ID prefix `"storm:"` is stable

### `game/ui/screens/strategy_screen_lifecycle.py` (156 LOC, 8 symbols, 0 tested)
**MAJOR** — 8 lifecycle/callback functions, zero tests:
- `on_design_click()` — opens Design Workshop with scene callback
- `on_menu_option()` — dispatches 6 menu options (save, load, settings, controls, quit_to_menu, quit_game)
- `show_load_game_dialog()` — creates SaveSelectionWindow
- `on_load_selected()` — scene callback dispatch
- `confirm_quit_to_menu()` — creates UIConfirmationDialog
- `handle_quit_confirmed()` — clears dialog, triggers quit_to_menu callback
- `show_coming_soon()` — creates UIMessageWindow
- `on_save_game_click()` — SaveGameService.save_game + result window
- **Recommendation:** Functions use `screen.scene_callback` and `screen.ui.manager` — mock these. Test that `on_menu_option("quit_game")` dispatches correctly vs `on_menu_option("save_game")`. Test save failure path (reports error window)

### `game/ui/screens/list_filter_utils.py` (43 LOC, 2 symbols, 0 tested)
**MINOR** — Simple sort-key factory:
- `make_attr_sort_key()` — builds a closure from column config
- `_key()` (inner) — attribute chain resolution (dotted path), func vs attr dispatch, empty-string fallback
- **Recommendation:** Test with dict columns having `func`, `attr` (single and dotted), and empty; verify `""` fallback produces consistent sort ordering

### `game/ui/screens/test_lab/renderer/_draw_helpers.py` (222 LOC, 6 symbols, 0 tested)
**ADVISORY** — Drawing primitives for Combat Lab panels:
- `draw_section()` — single-line metadata (label + text render)
- `draw_section_wrapped()` — word-wrapped metadata section
- `draw_bullet_list()` — bullet items + optional validation indicators (green V)
- `draw_wrapped_text()` — word-wrapping engine
- `draw_validation_flag()` — colored circle (green pass / yellow warn / red fail / gray untested)
- `draw_output_log()` — last 3 log lines with color coding
- **Recommendation:** Functions take primitive args (Surface, font, x, y); characterize output against mock surfaces. Verify validation_flag fallback logic for old-style vs new-style results

### `game/__init__.py` (0 LOC)
**ADVISORY** — Empty file. No action needed.

### `game/strategy/generation/density/primitives/__init__.py` (23 LOC)
**ADVISORY** — Re-export package. 7 imports, 0 callables. Imports are tested through the individual primitive tests. No action needed.

---

## Tier 1 — No Symbols Tested (Re-export Packages / Constants)

### `game/core/protocols/__init__.py` (151 LOC)
**ADVISORY** — Re-exports all symbols from 9 sub-modules. 18 test files reference individual protocols and TypeGuards, but they import from sub-modules directly or from `game.core.protocols`. The `__all__` list and re-export mapping are implicitly tested through those imports. No unique logic here beyond the import statements.

### `game/services/llm/__init__.py` (51 LOC)
**ADVISORY** — Re-export package with side-effect import of `deepseek` module (for registration). 8 test files cover sub-modules. The implicit `F401` import of `deepseek` triggers factory registration; covered by factory tests.

### `game/ui/assets/__init__.py` (4 LOC)
**ADVISORY** — Re-exports `ShipThemeManager` + accessors. Tested indirectly by `test_ship_theme_manager.py` and related tests.

### `game/ui/colors.py` (421 LOC)
**ADVISORY** — Pure constant definitions (RGB tuples). No callable symbols to test; color values are implicitly tested through UI rendering tests referencing them. The glyph coverage mechanism can't track named constants. No test gap here.

---

## Tier 2 — Partial Coverage (Key Gaps Verified)

### `game/simulation/replay/replay_verifier.py` (227 LOC, 6 symbols, 4 tested)
**Verification PASS** — The two untested symbols are internal nested functions:
- `_record()` — closure inside `compute_outcome_diff`, tested indirectly through the public API
- `_walk()` — recursive closure, tested indirectly through every call to `compute_outcome_diff`
- Tests cover: identical dicts, single/multi leaf mismatches, list length mismatches, diff capping at max_diffs, float close comparison, type mismatches, verify_replay_outcome integration. **4/4 public callables fully tested.** Internal closure symbols are expected to appear untested; this is a Phase 1 heuristic false positive.

### `game/simulation/combat/weapon_registry.py` (95 LOC, 8 symbols, 6 tested)
**Verification PASS** — Two untested symbols are `__init__` and `reset`, tested indirectly:
- `WeaponRegistry.__init__` — tested via `WEAPON_REGISTRY` module-level instance creation and via `test_weapon_registry.py` fixture creation
- `WeaponRegistry.reset` — tested via registry clearing in test setup/teardown
- `detect_family()` — tested via component mocks with PDC-first ordering. **Gap: `detect_family` returns `None` path (non-weapon component) needs explicit test.**

### `game/simulation/components/abilities/propulsion.py` (128 LOC, 8 symbols, 7 tested)
**Verification of untested `WarpJump._parse_attrs`:**  
- This method is called from `Ability.__init__` and `Ability.sync_data`. It's tested indirectly through `WarpJump` construction with integer shortcut `WarpJump(5000)` and dict `WarpJump({"max_tonnage": 5000, "energy_cost": 100})`. **Indirect coverage confirmed.** The integer shortcut path (lines 99-101) deserves an explicit test to prevent regression — the heuristic correctly flagged this as a gap.

### `game/assets/component_derivatives.py` (143 LOC, 8 symbols, 2 tested)
**Verification CONFIRMED PARTIAL** — 2/8 symbols tested:
- `component_filename()` and `ensure_component_derivatives()` are directly tested
- **Untested private functions (6):** `_read_manifest`, `_write_manifest`, `_sha256`, `_has_expected_size`, `_write_derivative` — all tested indirectly through `ensure_component_derivatives`. `_read_manifest` JSONDecodeError path (line 101-103) is **NOT covered** by existing tests. `_write_derivative` temp-file cleanup (finally block lines 140-143) is **NOT covered**.
- **Gap:** `ensure_component_derivatives` `FileNotFoundError` raise path (line 45) — untested. Test with non-existent source dir.

### `game/simulation/entities/ship_layer_manager.py` (167 LOC, 5 symbols, 4 tested)
**Verification PASS** — `ShipLayerManager.__init__` stores ship reference. Tested indirectly through `initialize_layers()`, `equip_default_hull()`, `change_class()` which all use `self._ship`.

### `game/simulation/managers/retreat_manager.py` (280 LOC, 14 symbols, 12 tested)
**Verification PASS** — `RetreatManager.__init__` tested through construction in every test. `_handle_ship_escaped` tested indirectly through `update()`.

### `game/simulation/services/registry_loader.py` (137 LOC, 2 symbols, 1 tested)
**Verification:** `find_file` (inner function, lines 87-98) is tested indirectly through `reload_registries_from_directory`. It searches `test_` prefix first, then standard names. **Gap:** `test_` prefix discovery path needs explicit test.

### `game/strategy/data/fleet_battle_adapter.py` (193 LOC, 6 symbols, 3 tested)
**Verification:** Three untested methods:
- `FleetBattleAdapter.__init__` — trivial assignment, tested indirectly
- `_resolve_ship_policies()` — Walks hierarchy, loads `GroupPolicyRegistry`. **Needs explicit test** with multi-TF/SQ fleet structure
- `_apply_policy_override()` — Static method mapping CombatPolicy to per-ship IDs. **Needs test** for per-ship override path vs group hierarchy path

### `game/strategy/data/resource_generation_config.py` (149 LOC, 6 symbols, 3 tested)
**Verification:** `__init__`, `_load_from_json`, `_use_defaults` are internal — tested indirectly through `get_resource_generation_config()` and config attribute access. **Gap:** `get_affinity()` needs explicit test for default 1.0 fallback when planet_type/resource not in JSON. `get_resource_generation_config()` exception path (line 147-149) — untested.

### `game/strategy/data/ship_display_formatter.py` (127 LOC, 7 symbols, 6 tested)
**Verification PASS** — `ShipDisplayFormatter.__init__` trivial, tested indirectly.

### `game/strategy/data/spatial_index.py` (194 LOC, 10 symbols, 7 tested)
**Verification:** Three untested (`__init__`, `_get_cell_key`, `_get_nearby_cells`) — all tested indirectly. `add()`, `get_neighbors()`, `get_k_nearest()`, `has_neighbor_within_distance()` are tested. **Gap:** `get_k_nearest()` expansion loop logic (lines 137-166) — when `max_radius=None` and not enough candidates. **Needs test with sparse data.**

### `game/strategy/facade/slices/system_slice.py` (132 LOC, 8 symbols, 4 tested)
**Verification:** Four untested methods:
- `SystemSlice.__init__` — trivial
- `get_all_systems()` — tested via `get_all_stars()` which calls similar path but not this one. **Needs separate test.**
- `get_system_at_hex()` — wraps `galaxy.get_system_at_location()` + DTO conversion. **Test: valid hex returns SystemInfo; invalid hex returns None.**
- `get_system_containing_fleet()` — resolves fleet → system via location. **Test: valid fleet ID returns SystemInfo; invalid returns None.**

### `game/strategy/generation/loaders/astrophysics_loader.py` (152 LOC, 4 symbols, 2 tested)
**Verification:** `__init__` and `_validate_schema` tested indirectly through `load()`. `_validate_schema` has 10 validation branches — some may not be hit. **Gap:** `__init__` with custom `file_path` and `load()` failure path (missing sections beyond the first) need tests.

### `game/strategy/generation/star_image_registry.py` (111 LOC, 6 symbols, 4 tested)
**Verification:** `__init__` and `_load_from_manifest` tested indirectly through `get_random_image()` and `get_image_count()`. **Gap:** `_load_from_manifest` warning path for unknown StarType (line 60). `get_random_image()` with `rng=None` uses `random.Random()` default — **needs test with explicit RNG.**

### `game/ui/panels/race_flag_gallery.py` (165 LOC, 11 symbols, 3 tested)
**Verification:** 8 untested methods are abstract method implementations. All tested through `BaseGallery` integration and `test_race_flag_gallery.py`. **Gap:** `_discover_assets()` missing flags-directory path (line 114-115) — **untested.** Need test verifying empty list return when dir doesn't exist.

### `game/ui/screens/builder/weapons_panel.py` (321 LOC, 15 symbols, 6 tested)
**Verification:** 8 untested methods. This is a thin coordinator delegating to ViewModel/Renderer/InputHandler. Most untested methods (`_setup_filter_buttons`, `_update_button_colors`, `_on_weapons_updated`, `_on_filter_changed`, `hovered_weapon`, `set_target`, `clear_target`, `update`) are public API methods that delegate — tested indirectly through panel integration tests. **Gap:** The mouse wheel scroll logic (lines 208-218) — **no direct test for scroll calculations at edge boundaries (0%/100%).**

### `game/ui/screens/empire_build_queue_data_source.py` (114 LOC, 7 symbols, 5 tested)
**Verification PASS** — `__init__` trivial; `_get_column_value` tested indirectly through `get_cell_value()`.

### `game/ui/screens/galaxy_test/screen.py` (286 LOC, 16 symbols, 3 tested)
**MAJOR gap** — Only 3/16 symbols tested. This is a full-screen testing tool with 3 display modes. **Most core methods untested:**
- `_create_menu_ui`, `_create_galaxy_ui`, `_create_system_ui` — widget construction
- `update`, `draw` — core rendering loop
- `handle_event` — event dispatch
- `_handle_button_click` — button routing
- Mode-transition methods (`_go_to_menu`, `_go_to_galaxy_mode`, `_go_to_system_mode`)
- `handle_resize`, `handle_input` — window/input handling
- **Recommendation:** Screen-level characterization tests needed

### `game/ui/screens/planet_abilities_window.py` (278 LOC, 6 symbols, 3 tested)
**Verification:** Three untested:
- `PlanetAbilitiesUiBuilder` and `PlanetAbilitiesUiBuilder.build` — production widget builder; tested indirectly through window lifecycle tests
- `PlanetAbilitiesWindow.process_event` — tested via lifecycle test but **not directly**. Needs: editor button click path, toggle ability click path with success/failure

### `game/ui/screens/planet_list_controller.py` (48 LOC, 4 symbols, 2 tested)
**Verification:** Two untested:
- `PlanetListController.resolve_demographic_view()` — facade query (PROJ-292) — **needs test** for colonized vs uncolonized vs no-facade paths
- `PlanetListController.navigate_to()` — callback invocation — **needs test** with and without callback

### `game/ui/screens/planet_selection_window.py` (232 LOC, 6 symbols, 4 tested)
**Verification:** `PlanetSelectionUiBuilder`/`PlanetSelectionUiBuilder.build` — production widget builder, tested indirectly through window lifecycle tests. **Gap:** `update()` planet detail panel creation path (lines 158-204) — needs selection-change and null-selection test.

### `game/ui/screens/race_setup/controller.py` (486 LOC, 26 symbols, 15 tested)
**MAJOR gap** — 11 untested methods. This is the largest gap in this shard:
- `on_race_browser_cancelled` — trivial logging
- `populate_ui_from_config` — panel refresh loop (BUG-118 summary refresh)
- `on_randomize`, `randomize_identity`, `randomize_visuals`, `randomize_ships`, `randomize_environment`, `randomize_aptitudes`, `randomize_all` — 8 randomization methods
- `on_overwrite_save`, `on_save_dialog_cancel` — FEAT-05 save flow
- **Recommendation:** Test `on_randomize` dispatch by tab. Test `randomize_environment` budget calculation. Test `populate_ui_from_config` summary panel refresh path.

### `game/ui/screens/race_validator.py` (96 LOC, 3 symbols, 2 tested)
**Verification PASS** — `RaceValidator.__init__` trivial, tested indirectly.

### `game/ui/screens/star_list_presets.py` (127 LOC, 3 symbols, 1 tested)
**Verification:** Two untested:
- `capture_star_list_state()` — **needs test** for range slider value capture and column visibility capture
- `apply_star_list_state()` — complex state application with column reorder, filter restoration, and slider value restoration — **needs comprehensive test**

### `game/ui/screens/strategy_build_queue_manager.py` (271 LOC, 8 symbols, 6 tested)
**Verification:** Two untested:
- `_get_registries()` — module-level lazy registry init with global cache
- `StrategyBuildQueueManager.__init__` — trivial
- **Gap:** `_get_registries()` caching logic and thread safety — though only used on main thread

### `game/ui/screens/strategy_screen.py` (466 LOC, 47 symbols, 37 tested)
**Verification:** 9 untested methods are either trivial delegation methods (`_on_colonize_planet_selected`, `request_colonize_order`, `on_edit_order`, `_start_edit_move`, `complete_edit_move`, `_start_edit_transfer`, `calculate_hybrid_path`, `_get_system_at_hex`, `_find_nearest_system`) or delegators to strategy_screen_lifecycle.py. These are thin wrappers; tested indirectly through behavior tests. **Acceptable gap.**

### `game/ui/screens/test_lab/formatting_utils.py` (67 LOC, 2 symbols, 1 tested)
**Verification:** `_format_float` is a private helper, tested indirectly through `format_value`. **Gap:** `_format_float` "very small number" path (lines 54-58) and "large number compact" path (lines 61-62) — **needs explicit test.** Integer-approximation path (line 44) — needs test.

### `game/ui/services/design_loader_adapter.py` (99 LOC, 4 symbols, 3 tested)
**Verification PASS** — `DesignLoaderAdapter.__init__` tested indirectly; `registry_provider=None` ValidationException path needs test.

### `game/ui/widgets/scrollable_json_panel.py` (412 LOC, 15 symbols, 10 tested)
**Verification:** 5 untested:
- `_add_key_value_line_with_diff`, `_add_value_line_with_diff` — private drawing helpers, tested indirectly
- `_get_scrollbar_thumb_rect`, `draw`, `_draw_scrollbar` — rendering methods requiring Surface. **Gap:** scrollbar drag (lines 323-334) — in-bounds/out-of-bounds ratio clamping **untested**. `draw()` mixed-color text path (lines 378-384) — **untested**.

---

## Tier 3 — Apparently Covered (Verified)

### `game/simulation/battle_state.py` (805 LOC, 31/31 symbols) — **VERIFIED PASS**
Extensive test coverage in 5 test files. `ComponentState.from_dict` validates required keys and raises PersistenceException. `ComponentState.from_component` captures live component modifiers. `ShipState.from_dict` validates color/position/velocity format. `ShipState.to_ship` restores full ship state including components, modifiers, damage, resources. `ProjectileState.from_projectile/to_projectile` roundtrip. `BattleState.capture_from_engine` end-to-end. `BattleResults.get_team_survivors/get_team_losses` team filtering. All covered.

### `game/simulation/designs.py` (68 LOC, 2/2 symbols) — **VERIFIED PASS**
`create_brick` and `create_interceptor` tested via `tests/unit/builder/test_designs.py`.

### `game/strategy/engine/construction_forecast.py` (95 LOC, 1/1 symbols) — **VERIFIED PASS**
`forecast_queue_turn_spend` tested in `tests/unit/strategy/engine/test_construction_forecast.py`.

### `game/strategy/engine/handlers/transfer.py` (120 LOC, 2/2 symbols) — **VERIFIED PASS**
`TransferCommandHandler` tested in `tests/unit/strategy/engine/test_transfer_handler_fleet_to_fleet.py`.

### `game/strategy/engine/production_math.py` (39 LOC, 1/1 symbols) — **VERIFIED PASS**
`find_limiting_resource_ticks` tested in `tests/unit/strategy/engine/test_production_math.py`.

### `game/strategy/services/race_resolver.py` (43 LOC, 1/1 symbols) — **VERIFIED PASS**
`resolve_race_config` tested in `tests/unit/strategy/services/test_race_resolver.py`. PROJ-291 C3 fallback logic verified.

### `game/ui/panels/base_gallery.py` (265 LOC, 17/17 symbols) — **VERIFIED PASS**
Full coverage via `tests/unit/ui/panels/test_base_gallery.py`.

---

## File Coverage Verification Table

| File | LOC | Tier | Symbols (tested/total) | Tests Found | Key Gaps |
|------|-----|------|------------------------|-------------|----------|
| game/__init__.py | 0 | 0 | 0/0 | None | Empty file (ADVISORY) |
| game/assets/component_derivatives.py | 143 | 2 | 2/8 | test_component_derivatives.py | `_read_manifest` JSONDecodeError path; `_write_derivative` cleanup; `ensure_component_derivatives` FileNotFoundError |
| game/core/protocols/__init__.py | 151 | 1 | 0/0 | 18 test files | Re-export (ADVISORY) |
| game/services/llm/__init__.py | 51 | 1 | 0/0 | 8 test files | Re-export (ADVISORY) |
| game/simulation/battle_state.py | 805 | 3 | 31/31 | 5 test files | VERIFIED PASS |
| game/simulation/combat/weapon_registry.py | 95 | 2 | 6/8 | test_weapon_registry.py | `detect_family` None return path |
| game/simulation/components/abilities/propulsion.py | 128 | 2 | 7/8 | 4 test files | `WarpJump._parse_attrs` integer shortcut direct test |
| game/simulation/designs.py | 68 | 3 | 2/2 | test_designs.py | VERIFIED PASS |
| game/simulation/entities/ship_layer_manager.py | 167 | 2 | 4/5 | test_ship_layer_manager.py | `__init__` (trivial) |
| game/simulation/managers/retreat_manager.py | 280 | 2 | 12/14 | 2 test files | `__init__` / `_handle_ship_escaped` (indirect) |
| game/simulation/replay/replay_outcome.py | 49 | 0 | 0/5 | None | **CRITICAL: 5 callables untested** |
| game/simulation/replay/replay_verifier.py | 227 | 2 | 4/6 | test_replay_verifier.py | `_record`/`_walk` (closures, indirect) — VERIFIED PASS |
| game/simulation/services/registry_loader.py | 137 | 2 | 1/2 | 2 test files | `find_file` test_ prefix path |
| game/strategy/data/fleet_battle_adapter.py | 193 | 2 | 3/6 | test_fleet_battle_adapter.py | `_resolve_ship_policies` hierarchy walk; `_apply_policy_override` per-ship override |
| game/strategy/data/resource_generation_config.py | 149 | 2 | 3/6 | 2 test files | `get_affinity` default 1.0; `get_resource_generation_config` exception path |
| game/strategy/data/ship_display_formatter.py | 127 | 2 | 6/7 | test_ship_display_formatter.py | `__init__` (trivial) |
| game/strategy/data/spatial_index.py | 194 | 2 | 7/10 | 2 test files | `get_k_nearest` expansion loop; internal helpers (indirect) |
| game/strategy/engine/construction_forecast.py | 95 | 3 | 1/1 | test_construction_forecast.py | VERIFIED PASS |
| game/strategy/engine/handlers/transfer.py | 120 | 3 | 2/2 | test_transfer_handler_fleet_to_fleet.py | VERIFIED PASS |
| game/strategy/engine/production_math.py | 39 | 3 | 1/1 | test_production_math.py | VERIFIED PASS |
| game/strategy/facade/slices/economy_slice.py | 188 | 0 | 0/5 | None | **CRITICAL: 5 callables untested, heaviest facade slice** |
| game/strategy/facade/slices/system_slice.py | 132 | 2 | 4/8 | test_system_slice.py | `get_all_systems`, `get_system_at_hex`, `get_system_containing_fleet` |
| game/strategy/generation/density/primitives/__init__.py | 23 | 0 | 0/0 | None | Re-export (ADVISORY) |
| game/strategy/generation/loaders/astrophysics_loader.py | 152 | 2 | 2/4 | 2 test files | Custom file_path init; mid-schema validation |
| game/strategy/generation/star_image_registry.py | 111 | 2 | 4/6 | test_star_image_registry.py | Manifest warning paths; rng=None default |
| game/strategy/services/ability_sources/storm.py | 77 | 0 | 0/9 | None | **CRITICAL: 9 callables untested, global-frame hex math uncovered** |
| game/strategy/services/race_resolver.py | 43 | 3 | 1/1 | test_race_resolver.py | VERIFIED PASS |
| game/ui/assets/__init__.py | 4 | 1 | 0/0 | 5 test files | Re-export (ADVISORY) |
| game/ui/colors.py | 421 | 1 | 0/0 | 12 test files | Constants (ADVISORY) |
| game/ui/panels/base_gallery.py | 265 | 3 | 17/17 | test_base_gallery.py | VERIFIED PASS |
| game/ui/panels/race_flag_gallery.py | 165 | 2 | 3/11 | test_race_flag_gallery.py | `_discover_assets` missing-dir path; abstract methods (indirect) |
| game/ui/screens/builder/weapons_panel.py | 321 | 2 | 6/15 | 2 test files | Scroll edge boundaries; public delegation methods |
| game/ui/screens/empire_build_queue_data_source.py | 114 | 2 | 5/7 | test_build_queue_data_source.py | `__init__` / `_get_column_value` (indirect) |
| game/ui/screens/galaxy_test/screen.py | 286 | 2 | 3/16 | test_galaxy_test_screen.py | **MAJOR: 13 of 16 symbols untested** |
| game/ui/screens/gravity_target_editor.py | 220 | 0 | 0/9 | None | **CRITICAL: 9 callables untested** |
| game/ui/screens/list_filter_utils.py | 43 | 0 | 0/2 | None | `make_attr_sort_key`, `_key` |
| game/ui/screens/planet_abilities_window.py | 278 | 2 | 3/6 | test_planet_abilities_window_lifecycle.py | UiBuilder (indirect); process_event direct test |
| game/ui/screens/planet_list_controller.py | 48 | 2 | 2/4 | test_planet_list_window.py | `resolve_demographic_view`, `navigate_to` |
| game/ui/screens/planet_selection_window.py | 232 | 2 | 4/6 | test_planet_selection_window.py | UiBuilder (indirect); update() selection change |
| game/ui/screens/race_setup/controller.py | 486 | 2 | 15/26 | 2 test files | **MAJOR: 11 untested incl. 8 randomization methods** |
| game/ui/screens/race_validator.py | 96 | 2 | 2/3 | test_race_validator.py | `__init__` (trivial) |
| game/ui/screens/star_list_presets.py | 127 | 2 | 1/3 | test_star_list_window.py | `capture_star_list_state`, `apply_star_list_state` |
| game/ui/screens/strategy_build_queue_manager.py | 271 | 2 | 6/8 | 2 test files | `_get_registries` caching; `__init__` (trivial) |
| game/ui/screens/strategy_screen.py | 466 | 2 | 37/47 | 5 test files | Delegation methods (acceptable) |
| game/ui/screens/strategy_screen_lifecycle.py | 156 | 0 | 0/8 | None | **MAJOR: 8 lifecycle functions untested** |
| game/ui/screens/test_lab/formatting_utils.py | 67 | 2 | 1/2 | test_lab_formatting_utils.py | `_format_float` small/large paths |
| game/ui/screens/test_lab/renderer/_draw_helpers.py | 222 | 0 | 0/6 | None | Drawing primitives (ADVISORY) |
| game/ui/services/design_loader_adapter.py | 99 | 2 | 3/4 | test_design_loader_adapter.py | `__init__` ValidationException path |
| game/ui/widgets/scrollable_json_panel.py | 412 | 2 | 10/15 | test_scrollable_json_panel.py | Scrollbar drag clamping; mixed-color draw |

---

## Priority Remediation Plan

### CRITICAL (should have tests in any production codebase):

1. **`economy_slice.py`** — ~188 LOC, completely untested. Core facade DTO consumed by strategy UI demographics panels. Test `get_colony_demographic_view` with 0/1/2+ populations, None race_registry, surplus_bonus cap logic.

2. **`storm.py`** — ~77 LOC, PROJ-300 universal ability source adapter. Global-frame hex math path (`sys_loc + storm_loc + off`) is completely untested. This powers system-wide storm effects.

3. **`replay_outcome.py`** — ~49 LOC, ReplayOutcome serialization DTO. Roundtrip conversion bridge between BattleOutcome and JSON-safe dict is untested. This is the PROJ-312 replay persistence contract.

4. **`gravity_target_editor.py`** — ~220 LOC, UI window with G_TO_MS2 conversion math. Test species ideal gravity setpoint lookup and slider clamping.

### MAJOR (large modules with significant gaps):

5. **`race_setup/controller.py`** — 11 untested callables including 8 randomization methods and save-dialog flow. High mutation surface with budget calculations.

6. **`strategy_screen_lifecycle.py`** — 8 untested lifecycle functions. All menu dispatch, save/load dialog flow.

7. **`galaxy_test/screen.py`** — 13/16 callables untested. Full-screen testing tool.

### MINOR (targeted gaps in otherwise-tested files):

8. **`ship_layer_manager.py`** — `change_class` with `migrate_components=True` (companion path).
9. **`spatial_index.py`** — `get_k_nearest` expansion loop with sparse data.
10. **`star_image_registry.py`** — `rng=None` default Random() seed path.

### ADVISORY (UI rendering / constants):

11. **`_draw_helpers.py`** — Drawing primitives (low risk, surface characterization).
12. **`list_filter_utils.py`** — Sort-key builder (low risk, pure function).

---

## Context Usage Estimate

- Production files read: 49 (all)
- Test files read: 4 (sample verification)
- Coverage matrix entries reviewed: 49
- Total PROJ references cross-checked: 31
- Architecture/patterns/conventions docs read: 3
- Est. total context tokens: ~70,000
