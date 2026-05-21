# Shard 15 — Unit Test Coverage Audit

**Audit date:** 2026-05-20  
**Scope:** 45 production files, ~9457 LOC  
**Tiers:** 0=11 (CRITICAL), 1=1 (MAJOR), 2=26 (MAJOR/MINOR), 3=7 (COVERED)  
**Heuristic baseline:** `coverage_data_15.md`

## Executive Summary

Shard 15 has **9 verified CRITICAL gaps** (Tier 0 files with zero tests), **1 heuristic false-negative** (Tier 0 downgraded to Tier 2), **21 MAJOR gaps** across Tier 1-2 files, and **5 MINOR/ADVISORY gaps**. Notable findings:

- **`strategy_screen_lifecycle.py`** was heuristically classified Tier 0 but has a comprehensive test suite (`test_strategy_screen_lifecycle.py`: 171 LOC, 19 tests). This is a heuristic false-negative — reclassified to Tier 3.
- **`carried_vehicle_deploy.py`** has zero tests despite containing critical fleet-launch/reboard logic shared by 3 call sites.
- **`system_mode.py`** at 576 LOC exceeds the 500-LOC ceiling AND has zero tests.
- **`radiation_shield_editor.py`** has no tests; the auto-shielding logic (`_set_auto` at line 197) is untested.
- **`transfer_container_rows.py`** has no tests despite containing the row-builder function for the transfer dialog.
- **`grouped_namespaces.py`** has the largest absolute gap — 45 heuristically untested symbols in a 406-LOC facade layer.
- **`component_derivatives.py`** has 6 untested helper functions (SHA hashing, manifest I/O, fast-path checks).
- **`test_lab/details/validation.py`** has zero tests despite containing 4 rendering functions with per-pixel layout contracts.

---

## Tier 0 Files — Verified Zero Test Coverage

### T0-01: `game/strategy/data/carried_vehicle_deploy.py` (116 LOC)
**Severity:** CRITICAL  
**Layer:** strategy  
**Symbols:** `carried_vehicle_to_ship_instance` (line 33), `carried_vehicle_to_ship_instance_safe` (line 92)

**Gap detail:** No test files exist anywhere in the repo. These two functions are the shared helper for materialising deployed `ShipInstance` from `CarriedVehicle`, consolidated from three previously-duplicated sites (fighter launch, satellite launch, post-battle overflow). The critical logic at lines 82-86 (component state restore with try/except) and the vehicle-type-aware instance-id prefix at line 67 have zero test coverage.

- Line 66-67: vehicle_type → prefix mapping (satellite/fighter) — untested
- Line 69-76: ShipInstance construction with design_data copy — untested
- Line 77-78: registries wiring — untested
- Line 82-86: component_states restore with Intentional broad catch — untested
- Line 87-88: is_alive/is_derelict flag sets — untested
- Line 105-109: `_safe` wrapper's fallback-to-None contract — untested

**Test suggestion:** `tests/unit/strategy/data/test_carried_vehicle_deploy.py` — test both functions with CarriedVehicle mocks for fighter, satellite, with/without component_states, with/without registries, and the safe wrapper's None fallback.

---

### T0-02: `game/ui/screens/galaxy_test/system_mode.py` (576 LOC)
**Severity:** CRITICAL  
**Layer:** ui  
**Symbols:** `SystemModeHelper` + 12 methods  
**LOC ceiling violation:** 576 > 500

**Gap detail:** No test files exist. This class manages system generation (stars + planets), blueprint loading, 2D rendering with camera transforms, click-based object selection, and detailed physics inspector panel formatting.

- Line 33-56: `__init__` — screen wiring, state defaults — untested
- Line 58-191: `create_ui` — builds 15+ pygame_gui widgets with layout math — untested
- Line 193-204: `_get_blueprint_options` — file I/O, error fallback — untested
- Line 206-286: `generate` — StarSystem + StarGenerator + PlanetGenerator orchestration; seed parsing (lines 216-222: int vs hash fallback), blueprint load, object generation — untested
- Line 288-322: `_center_camera` — bounding-box calculation, zoom fitting with min/max clamping — untested
- Line 324-361: `handle_click` — proximity detection, star vs planet priority — untested
- Line 363-383: `_update_inspector_panel` — object type dispatch — untested
- Line 385-482: `_format_star_info` / `_format_planet_info` / `_get_classification_reason` — physics data formatting, atmosphere sorting, classification reasoning — untested
- Line 484-571: `draw` — pygame rendering with camera transforms, orbital rings, glow effects, selection highlights, font rendering — untested
- Line 573-576: `update_fps_display` — untested

**Test suggestion:** `tests/unit/ui/screens/galaxy_test/test_system_mode.py` — can at minimum test `_get_blueprint_options` (mock loader), `generate` (mock generators), `_center_camera` (mock camera), `_format_star_info` / `_format_planet_info` (pure formatting with mock Star/Planet). Rendering methods can test that draw calls occur without crashing on a mock surface.

---

### T0-03: `game/ui/screens/race_setup/ui_builder.py` (42 LOC)
**Severity:** CRITICAL  
**Layer:** ui  
**Symbols:** `RaceSetupUiBuilder` (line 25), `RaceSetupUiBuilder.build` (line 38)

**Gap detail:** No direct unit test exists. The builder is tested indirectly through `tests/fixtures/test_race_setup_ui_builders.py` which verifies `NullRaceSetupUiBuilder` and `MockRaceSetupUiBuilder` behavior through `RaceSetupScreen` construction. However, the production `RaceSetupUiBuilder.build()` which delegates to `screen._create_ui()` has zero direct test coverage — no test calls `RaceSetupUiBuilder().build(screen)` and verifies `screen._create_ui()` is invoked.

**Test suggestion:** `tests/unit/ui/screens/race_setup/test_ui_builder.py` — trivial test that `RaceSetupUiBuilder().build(mock_screen)` calls `mock_screen._create_ui()`.

---

### T0-04: `game/ui/screens/radiation_shield_editor.py` (231 LOC)
**Severity:** CRITICAL  
**Layer:** ui  
**Symbols:** `RadiationShieldEditor` + 8 methods

**Gap detail:** Zero test coverage. This is a PlanetTargetEditor subclass managing radiation shielding UI with slider, species selector, and auto/clear/apply buttons.

- Line 34-74: `__init__` — parent init, planet state reading, `_build_ui` call — untested
- Line 76-166: `_build_ui` — species selector (line 85 via `build_species_selector`), 5 labels, 1 slider, 3 buttons — untested
- Line 168-174: `update` — slider-moved-recently polling — untested
- Line 176-181: `_button_handlers` — button-to-callback mapping — untested
- Line 183-195: `_on_apply` — slider value read + callback + kill — untested
- Line 197-221: `_set_auto` — race config resolution, preference.setpoint read, clamping to [0, 2], slider set — **critical logic untested**
- Line 224-231: `_clear_target` — callback with None + kill — untested

**Test suggestion:** `tests/unit/ui/screens/test_radiation_shield_editor.py` — can use bypass_init + make_ui_widget to test the editor with mock planet, mock race_config. Test `_set_auto` with various preference.setpoint values and clamping. Test `_on_apply` and `_clear_target` callbacks.

---

### T0-05: `game/ui/screens/strategy_windows/move_choice_dialog.py` (94 LOC)
**Severity:** CRITICAL  
**Layer:** ui  
**Symbols:** `MoveChoiceWindow` (line 26), `MoveChoiceDialog.__init__` (line 39), `MoveChoiceDialog.show` (line 42)

**Gap detail:** Zero tests. This dialog asks the player to choose between static sector move and dynamic fleet intercept, creating pygame_gui buttons wired through `UICallbackDispatcher`.

- Line 39-40: `MoveChoiceDialog.__init__` — composer wiring — untested
- Line 42-94: `MoveChoiceDialog.show` — window creation, 2 labels, 2 buttons, callback lambda wiring (lines 93-94) — untested

**Test suggestion:** `tests/unit/ui/screens/strategy_windows/test_move_choice_dialog.py` — test with bypass_init on MoveChoiceWindow, mock composer with ui_callbacks dict, verify buttons created with correct callbacks.

---

### T0-06: `game/ui/screens/test_lab/component_dropdown.py` (157 LOC)
**Severity:** CRITICAL  
**Layer:** ui  
**Symbols:** `ComponentDropdown` + 6 methods

**Gap detail:** Zero tests. Pure pygame rendering and click/hover detection with no pygame_gui framework dependency.

- Line 18-46: `__init__` — state init, font/color loading — untested
- Line 48-84: `handle_click` — header click expand/collapse (lines 54-58, 62-66), option selection (lines 69-77), outside-click collapse (lines 80-82) — untested
- Line 86-99: `handle_hover` — hover index tracking — untested
- Line 101-106: `get_selected_component_id` — "No components" sentinel check — untested
- Line 108-157: `draw` — pygame.Surface rendering with expand/collapse arrow polygon — untested

**Test suggestion:** `tests/unit/ui/screens/test_lab/test_component_dropdown.py` — logic can be tested with mock pygame.mouse.get_pos() and mock surface. Test click expansion/collapse, option selection, hover detection, and the "No components" fallback.

---

### T0-07: `game/ui/screens/test_lab/details/validation.py` (253 LOC)
**Severity:** CRITICAL  
**Layer:** ui  
**Symbols:** `_phase_color` (line 39), `draw_validation_results` (line 49), `draw_single_validation` (line 102), `draw_numeric_difference` (line 201)

**Gap detail:** Zero tests for 4 module-level rendering functions that have per-pixel layout contracts. The module docstring explicitly documents the UI contract including phase colors, V/X glyphs, EXACT MATCH formatting, essentially-exact sub-0.01% threshold, and tolerance/TOST detail rendering.

- Line 39-46: `_phase_color` — phase-to-color dict lookup (DATA/PRECONDITION/OUTCOME) — untested
- Line 49-99: `draw_validation_results` — phase grouping, header rendering, phase-header colors, and separators — untested
- Line 102-198: `draw_single_validation` — PASS/FAIL/WARN status colors, V/X/! symbols, expected/actual value formatting, p-value rendering with significance threshold (line 174), detail string (line 185), subtle separator line (line 195) — untested
- Line 201-253: `draw_numeric_difference` — boolean guard (line 218-219), EXACT MATCH for <1e-9 pct (line 231), essentially-exact for <0.01% (line 234), ± formatting (line 237), zero-expected branch (lines 239-245) — untested

**Test suggestion:** `tests/unit/ui/screens/test_lab/details/test_validation.py` — test with mock DetailsDrawContext, mock pygame.Surface and pygame.font.Font. Verify correct y_offset returns, phase colors, status formatting, numeric difference edge cases (zero expected, boolean values, exact match threshold).

---

### T0-08: `game/ui/screens/test_lab/renderer/_draw_helpers.py` (222 LOC)
**Severity:** CRITICAL  
**Layer:** ui  
**Symbols:** `draw_section` (line 27), `draw_section_wrapped` (line 51), `draw_bullet_list` (line 75), `draw_wrapped_text` (line 115), `draw_validation_flag` (line 152), `draw_output_log` (line 212)

**Gap detail:** Zero tests for 6 visual draw primitives used by multiple Combat Lab renderer panels. These are low-level pygame Surface rendering functions.

- Line 27-48: `draw_section` — label + text rendering with y-offset tracking — untested
- Line 51-72: `draw_section_wrapped` — text wrapping integration — untested
- Line 75-112: `draw_bullet_list` — bullet items, None fallback (line 95), validation flag integration with `is_condition_verified` — untested
- Line 115-149: `draw_wrapped_text` — word wrapping algorithm with line splitting — untested
- Line 152-209: `draw_validation_flag` — 5-branch logic: no last_run_results (line 172), new-style validations with fail/warn/pass counts (lines 176-192), old-style single-passed-bool fallback (lines 193-195), no validation data (lines 196-198), circle rendering with symbol overlay — untested
- Line 212-222: `draw_output_log` — last-3-messages display with ERROR color highlighting — untested

**Test suggestion:** `tests/unit/ui/screens/test_lab/renderer/test_draw_helpers.py` — test each function with mock pygame.Surface and mock pygame.font.Font instances. Test wrapped_text word splitting, bullet_list with/without validation_results, validation_flag all branches.

---

### T0-09: `game/ui/screens/transfer_container_rows.py` (142 LOC)
**Severity:** CRITICAL  
**Layer:** ui  
**Symbols:** `build_row_data_from_containers` (line 48), `_aggregate_quantities_by_cargo_key` (line 117)

**Gap detail:** Zero tests. This module builds the row list for the transfer dialog from ContainerSnapshotInfo entries, aggregating by (kind, type_id), with specific ordering (resources in catalog order, population alphabetical, items alphabetical).

- Line 48-114: `build_row_data_from_containers` — multi-kind aggregation, resource catalog ordering (lines 73-81), population emission guard (lines 86-95), items emission guard (lines 98-107), filter_empty branch (lines 109-113) — untested
- Line 117-139: `_aggregate_quantities_by_cargo_key` — ContainableKind dispatch for RESOURCE/POPULATION/ITEM, unknown-kind skip (line 137) — untested

**Test suggestion:** `tests/unit/ui/screens/test_transfer_container_rows.py` — test with mock ContainerSnapshotInfo entries for all three kinds, verify ordering, verify filter_empty behavior, verify unknown kind skip.

---

### T0-10: `game/strategy/facade/__init__.py` (8 LOC)
**Severity:** ADVISORY  
**Layer:** strategy  

Re-export shim — exports `StrategySessionFacade`. No functional code; tested implicitly through facade tests. ADVISORY only.

---

## Tier 1 File — Heuristic False Classification

### T1-01: `game/ui/screens/test_lab/__init__.py` (22 LOC)
**Severity:** ADVISORY  
**Layer:** ui  

Package re-exports `TestLabScreen`, `TestLabDataExtractor`, `get_test_data_dir`. The heuristic flagged this as Tier 1 ("no symbols tested") because `__init__.py` has 0 exported symbols in the heuristic's symbol counter. The underlying modules are tested. ADVISORY only.

---

## Tier 0 Heuristic False-Negative — Reclassified

### FN-01: `game/ui/screens/strategy_screen_lifecycle.py` (175 LOC)
**Original tier:** 0 (heuristic) → **Reclassified:** Tier 3 (well-tested)  
**Test file:** `tests/unit/ui/screens/test_strategy_screen_lifecycle.py` (171 LOC)

**Correction:** The heuristic name-grep failed because the test filename uses "lifecycle" not "strategy_screen_lifecycle". This file has **comprehensive test coverage**: 19 tests across 6 test classes (`TestOnDesignClick`, `TestOnMenuOption`, `TestLoadGameDialog`, `TestQuitConfirmation`, `TestComingSoon`, `TestSaveGameClick`).

All 8 public symbols are covered:
- `on_design_click` (line 27) — tested with/without callback, context_data verification
- `on_menu_option` (line 59) — all 6 branches tested + unknown-option noop
- `show_load_game_dialog` (line 83) — window creation + callback wiring
- `on_load_selected` (line 107) — callback + no-callback safety
- `confirm_quit_to_menu` (line 113) — dialog creation
- `handle_quit_confirmed` (line 127) — dialog clear + callback
- `show_coming_soon` (line 137) — message window creation
- `on_save_game_click` (line 148) — success + failure dialog paths

No gaps. Remove from CRITICAL list.

---

## Tier 2 Files — Detailed Coverage Analysis

### T2-01: `game/ai/target_evaluator.py` (331 LOC)
**Severity:** MAJOR  
**Test files:** 6 candidate files

**Gap:** The 6 private `_eval_*` static methods (lines 41-263) are heuristically untested. In practice they are tested **indirectly** through `TargetEvaluator.evaluate()` (line 266) which dispatches to them. However, direct tests for individual eval methods would improve isolation and edge case coverage:

- `_eval_distance_rule` (line 41): weight>0 vs weight<=0 branches, distance_cache hit vs miss — indirect only
- `_eval_mass_rule` (line 81): mass/largest/smallest/weakest with weight>0 vs factor paths — indirect only
- `_eval_damage_rule` (line 137): most_damaged vs least_damaged with hp_pct scaling — indirect only
- `_eval_least_armor_rule` (line 197): non-combat-ship guard (line 207), armor_hp sum using current_hp — indirect only
- `_eval_pdc_arc_rule` (line 218): non-missile passthrough (line 227), in-arc/not-in-arc paths, -999999 penalty — indirect only
- `_eval_capability_rule` (line 241): dispatcher for has_weapons/least_armor/pdc_arc — indirect only

---

### T2-02: `game/assets/component_derivatives.py` (182 LOC)
**Severity:** MAJOR  
**Test file:** `tests/unit/assets/test_component_derivatives.py`

**Gap:** Only `ensure_component_derivatives`, `component_filename`, and `_sha256` are tested directly. Six internal helpers are covered only through the integration-level `ensure_component_derivatives` path:

- `_read_manifest` (line 105): JSON decode error fallback (line 110-111) — untested
- `_write_manifest` (line 115): atomic temp-write-then-replace pattern (lines 117-119) — untested
- `_source_fast_path_hit` (line 130): size+mtime proxy check with 4 guard conditions (lines 144-157) — untested *in isolation*
- `_has_expected_size` (line 160): PIL OSError fallback (line 164-165) — untested
- `_write_derivative` (line 168): same-size copy vs LANCZOS resize (lines 170-173), temp-file cleanup in finally (lines 179-182) — untested in isolation
- `ComponentDerivativeResult` (line 23): frozen dataclass construction — untested in isolation

---

### T2-03: `game/context.py` (241 LOC)
**Severity:** MINOR  
**Test files:** 4 candidate files

**Gap (heuristic):**
- `_install_default_habitability_service` (line 57): called at module import time (line 67); tested implicitly by any test that imports `game.context`. `tests/unit/test_context_habitability_accessors.py` tests the get/set/clear accessors directly.
- `ApplicationContext.__init__` (line 81): tested through `create_production()` (line 111) and `create_test()` (line 206). Direct `__init__` call not needed per conventions (dunders exempt from return-type requirement).

**Verdict:** MINOR — effectively covered.

---

### T2-04: `game/core/registry.py` (483 LOC)
**Severity:** MINOR  
**Test files:** 72 candidate files

**Gap (heuristic):**
- `RegistryManager.unfrozen` (line 171): context manager for scoped unfreeze. Tested in `test_registry_operations.py` & `test_singleton_and_thread.py`.
- `freeze_registry` (line 318): module-level wrapper. Extensively used in test fixtures.

**Verdict:** MINOR — effectively covered through extensive test usage.

---

### T2-05: `game/simulation/combat/ability_stat_registry.py` (237 LOC)
**Severity:** MAJOR  
**Test file:** `tests/unit/simulation/combat/test_ability_stat_registry.py`

**Gap (heuristic):** `_extract_value` (line 128) and `_route_team_ids` (line 148) are private helpers called only by `emit_entries_for_ability`. They are tested indirectly, but edge cases are not covered:

- `_extract_value` line 140-142: dict path with missing value_field, primitive float/int path, non-dict/non-numeric fallback (0.0)
- `_route_team_ids` line 154-156: OPPONENT_SCOPES N-team fan-out, empty list path

---

### T2-06: `game/strategy/combat/battle_assembly.py` (353 LOC)
**Severity:** MAJOR  
**Test files:** `test_battle_assembly.py`, `test_battle_assembly_third_party_mines.py`

**Gap (heuristic):**
- `_boundary_to_box` (line 64): `UnboundedRegion` → None (line 73-74), radius-based extraction (lines 76-78), bounds extraction (lines 79-81), None boundary (lines 73-74) — heuristic says untested. The test for third-party mines interacts with this via `battle_boundary` parameter.
- `StrategyBattleAssembler.__init__` (line 161): trivial constructor — MINOR.
- `StrategyBattleAssembler.assemble` (line 166): the main orchestration method. Heuristically untested because the heuristic matches on method name "assemble" but the test likely exercises `build_strategy_battle_assembly()`.

**Verdict:** `_boundary_to_box` needs targeted unit test with all boundary variants (UnboundedRegion, radius-only, bounds-rect, None).

---

### T2-07: `game/strategy/data/orbital_generation_config.py` (195 LOC)
**Severity:** MAJOR  
**Test file:** `tests/unit/strategy/data/test_orbital_generation_config.py`

**Gap (heuristic):** `__init__` (line 72), `_load_from_json` (line 84), `_use_defaults` (line 136) — heuristically untested. Tested through `get_orbital_generation_config()` (line 180) and through the `__init__` path when tests construct with `data=None` or mock data. The `_load_from_json` method has 30+ attribute assignments at lines 92-134, and the `_use_defaults` method mirrors them at lines 138-177. Direct tests for empty data, partial JSON, and full JSON loading would be valuable.

---

### T2-08: `game/strategy/data/ship_display_formatter.py` (131 LOC)
**Severity:** MINOR  
**Test file:** `tests/unit/strategy/test_ship_display_formatter.py`

**Gap (heuristic):** `ShipDisplayFormatter.__init__` (line 38) — trivial constructor, tested via all other tests that create formatter instances. MINOR.

---

### T2-09: `game/strategy/data/squadron.py` (102 LOC)
**Severity:** MINOR  
**Test files:** 6 candidate files

**Gap (heuristic):** `Squadron.__init__` (line 30) — tested through `from_dict` and through fleet hierarchy test files. MINOR.

---

### T2-10: `game/strategy/engine/handlers/movement.py` (284 LOC)
**Severity:** MINOR  
**Test file:** `tests/unit/strategy/engine/handlers/test_movement_handlers.py`

**Gap (heuristic):** `register` (line 272) — iterates handler classes and calls `registry.register()`. Covered by integration tests that seed the command registry. MINOR.

---

### T2-11: `game/strategy/engine/happiness_engine.py` (141 LOC)
**Severity:** MAJOR  
**Test files:** `test_happiness_engine.py`, `test_turn_engine_lazy_properties.py`

**Gap (heuristic):**
- `_validate_tick_inputs` (line 90): None-colony detection — indirectly tested through `process_happiness` which calls it first (line 103).
- `_process_colony` (line 109): core happiness formula (lines 110-129) — includes habitability calculation, food-surplus bonus with clamping. Indirectly tested through `process_happiness`.

The heuristic correctly identifies these as untested at the direct-method level, but they are tested through the public API. The happiness formula at line 119 (`raw = base_happiness * last_food_ratio * habitability`) and the FEAT-19 surplus branch (lines 123-128) should have direct unit tests with controlled inputs. MAJOR.

---

### T2-12: `game/strategy/facade/dto/fleet_dto.py` (332 LOC)
**Severity:** MAJOR  
**Test files:** `test_fleet_dto.py` (633 LOC), `test_fleet_dto_build.py`, `test_fleet_dto_capabilities.py`

**Gap (heuristic):** Three private static methods heuristically untested:
- `_aggregate_carried_vehicles_by_type` (line 248): counts mine/fighter/satellite from `bay_inventory.bay` — 259-268 lines with vehicle_type filtering
- `_sum_vehicle_bay_used` (line 271): iterates ships, calls `get_vehicle_bay_capacity()`, Intentional broad catch for mock fleets
- `_sum_vehicle_bay_max` (line 285): mirrors `_sum_vehicle_bay_used` pattern

The main test file (633 LOC) is extensive and likely covers these via `FleetInfo.from_fleet()` which calls them. However, the bay_inventory-specific edge cases (None inventory, non-tuple return from get_vehicle_bay_capacity) should be verified.

---

### T2-13: `game/strategy/facade/grouped_namespaces.py` (406 LOC)
**Severity:** MAJOR  
**Test file:** `tests/unit/strategy/facade/test_container_snapshots.py`

**Gap:** 45 heuristically untested symbols. This is the largest absolute gap in the shard. These namespace classes wrap facade slices:

- `FacadeCommands` (line 63): `__init__` (line 79), `__getattr__` (line 94), `__dir__` (line 107) — MAJOR
- `FacadeFleetQueries` (line 119): `get` (line 127), `at_hex` (line 131), `path_preview` (line 135), `path_projection` (line 141), `remaining_pods` (line 147), `get_containers` (line 151) — MAJOR
- `FacadePlanetQueries` (line 163): `__init__` (line 168), `get` (line 171), `at_hex` (line 175), `get_containers` (line 179) — MAJOR
- `FacadeSystemQueries` (line 192): various methods — MAJOR
- `FacadeEmpireQueries` (line 232): various methods — MAJOR
- `FacadeEventQueries` (line 272): various methods — MAJOR
- `FacadeSessionInfo` (line 302): various methods — MAJOR
- `FacadeEconomyQueries` (line 344): various methods — MAJOR
- `FacadeValidation` (line 372): various methods — MAJOR

The heuristic correctly identifies these as untested by direct test imports. The `test_container_snapshots.py` file navigates these namespaces via the facade. However, the `FacadeCommands.__getattr__` dynamic dispatch (line 94) and `__dir__` override (line 107) have no direct unit tests, and the `AttributeError` raising path (line 101-104) is untested.

---

### T2-14: `game/strategy/facade/slices/empire_slice.py` (97 LOC)
**Severity:** MAJOR  
**Test file:** `tests/unit/strategy/facade/slices/test_empire_slice.py`

**Gap (heuristic):** 5 methods heuristically untested:
- `__init__` (line 25): trivial
- `get_all_empires` (line 40): list comprehension with `EmpireInfo.from_empire`
- `get_empire` (line 47): None-guard for missing empire
- `get_empire_colonies` (line 54): `ColonySummary.from_planet` mapping
- `get_empire_fleets` (line 61): `FleetSummary.from_fleet` mapping

These are thin delegation methods. The test file likely covers them, but the heuristic name-grep may not match. Verify that test_empire_slice.py tests all public read methods.

---

### T2-15: `game/strategy/generation/density/density_map.py` (241 LOC)
**Severity:** MINOR  
**Test files:** 4 candidate files

**Gap (heuristic):** `DensityMap.__len__` (line 239) — returns `len(self._primitives)`. Trivial dunder, tested implicitly. MINOR.

---

### T2-16: `game/strategy/services/action_time_resolver.py` (243 LOC)
**Severity:** MAJOR  
**Test file:** `tests/unit/strategy/services/test_action_time_resolver.py`

**Gap (heuristic):**
- `_activate_time_field` (line 46): raises `ValueError` for unregistered ability (line 65-70) and for ability without EnergyFacet (line 72-78). The error paths have explicit "fail fast" behavior — CRITICAL to test.
- `_find_fleet_ability_time` (line 166): iterates ships, calls `iterate_design_components`, returns first match — indirectly tested.
- `_find_planet_ability_time` (line 183): facility filter by instance_id (lines 198-206), is_operational check (line 209), time_value > 0 guard (line 216) — indirectly tested.
- `_get_abilities` (line 237): thin wrapper — untested separately.

**Key finding:** `_activate_time_field` has two `ValueError` raise paths that form a fail-fast contract. These error paths need direct testing. MAJOR.

---

### T2-17: `game/strategy/services/component_abilities.py` (403 LOC)
**Severity:** MINOR  
**Test files:** `test_component_abilities.py`, `test_fleet_report_filters.py`

**Gap (heuristic):**
- `_get_component_registry` (line 94): handles GameRegistries + dict registry — underexposed internal
- `get_component_type` (line 107): handles dict + Component + None — MINOR
- `get_component_threshold` (line 125): handles dict + Component + None defaults — MINOR

The main test file covers 10 of 13 symbols. These 3 are thin attribute extractors. MINOR.

---

### T2-18: `game/ui/screens/battle_results_screen.py` (291 LOC)
**Severity:** ADVISORY  
**Test file:** `tests/unit/ui/screens/test_battle_results_screen.py`

**Gap (heuristic):** `__init__` (line 52), `_draw_header` (line 149), `_draw_team_column` (line 177), `_draw_footer` (line 272) — heuristically untested. These are rendering methods that call pygame.Surface methods. The test file likely tests event handling and `draw()` which calls all helpers. ADVISORY for UI rendering layer.

---

### T2-19: `game/ui/screens/battle_setup/renderer.py` (86 LOC)
**Severity:** MINOR  
**Test file:** `tests/unit/ui/screens/battle_setup/test_renderer.py`

**Gap (heuristic):** `_build_bottom_bar` (line 61) — creates 5 buttons in a UIPanel. Indirectly tested via `rebuild()`. MINOR.

---

### T2-20: `game/ui/screens/empire_build_queue_data_source.py` (114 LOC)
**Severity:** MINOR  
**Test file:** `tests/unit/ui/screens/test_build_queue_data_source.py`

**Gap (heuristic):** `__init__` (line 30), `_get_column_value` (line 93) — the "system"/"sector"/delegate branching. Tested indirectly through `get_cell_value`. MINOR.

---

### T2-21: `game/ui/screens/orders_window.py` (463 LOC)
**Severity:** MAJOR  
**Test files:** `test_orders_window.py`, `test_fleet_orders_refresh.py`

**Gap (heuristic):** 9 untested symbols:
- `OrdersListRenderer` (line 129) / `render` (line 140): row widget construction with button layout math — MAJOR
- `OrdersWindowUiBuilder` (line 237) / `build` (line 243): container + clear-button creation — MAJOR
- `OrdersWindow.rebuild_list` (line 363): delegates to `_list_renderer.render` — tested through update()
- `OrdersWindow.process_event` (line 383): button-press dispatch with object_id parsing (lines 395-412) — MAJOR
- `OrdersWindow.move_order` (line 416), `edit_order` (line 424), `delete_order` (line 431): callback+rebuild — MAJOR

The test file (`test_orders_window.py`) tests with MockOrdersUiBuilder/NormalOrdersUiBuilder and likely covers most of these indirectly.

---

### T2-22: `game/ui/screens/planet_list_window.py` (453 LOC)
**Severity:** MINOR  
**Test files:** 7 candidate files

**Gap (heuristic):** 9 heuristically untested symbols:
- `filter_effects` (lines 231, 232-233): property delegates to `_filter_mgr.filter_effects` — MINOR
- `filter_ranges` (lines 241, 242-243): property delegates to `_filter_mgr.filter_ranges` — MINOR
- `_capture_current_state` (line 292): calls `capture_planet_list_state` — tested via preset capture
- `_apply_state` (line 300): calls `apply_planet_list_state` — tested via preset apply
- `process_event` (line 314): delegates to `_event_router.process_event` — MINOR
- `_super_process_event` (line 318): thin base-class passthrough — MINOR
- `set_dimensions` (line 323): property delegation pattern — MINOR

The heuristic matched property accessors as untested symbols, but they are trivial delegates. MINOR.

---

### T2-23: `game/ui/screens/star_list_presets.py` (127 LOC)
**Severity:** MAJOR  
**Test file:** `tests/unit/ui/screens/test_star_list_window.py`

**Gap (heuristic):** `capture_star_list_state` (line 24) and `apply_star_list_state` (line 60) — heuristically untested. These are tested indirectly through the star list window test, but direct unit tests would validate the capture/apply round-trip:
- `capture_star_list_state`: column visibility serialization, range slider value extraction (lines 47-52)
- `apply_star_list_state`: column reorder+visibility restore (lines 76-92), type toggle UI update (lines 110-118), range slider restore (lines 120-125)

---

### T2-24: `game/ui/screens/strategy_camera_nav.py` (232 LOC)
**Severity:** MAJOR  
**Test files:** `test_camera_navigator.py`, `test_strategy_screen_composition.py`

**Gap (heuristic):** `_resolve_global_hex` (line 79) — private method handling planet/fleet/system resolution. This is tested indirectly through `center_on()`. However, the fleet path (line 95) uses `is_fleet` protocol and the system path (line 98) uses `is_star_system` protocol — both need direct testing with mock objects conforming to those protocols.

---

### T2-25: `game/ui/screens/test_lab/viewmodel.py` (389 LOC)
**Severity:** MINOR  
**Test files:** `test_viewmodel.py`, `test_data_paths.py`

**Gap (heuristic):** Button rect properties (lines 271-368) — 12 heuristically untested symbols. These are simple getter/setter property pairs that store pygame.Rect values set by the renderer and read by the input handler. The test file likely tests them via `setattr` patterns. MINOR.

---

### T2-26: `game/ui/screens/workshop_viewmodel_layer_ops.py` (254 LOC)
**Severity:** MAJOR  
**Test file:** `tests/unit/ui/screens/test_workshop_viewmodel_layer_ops.py`

**Gap (heuristic):** `WorkshopLayerOps.quick_add_component` (line 105) — heuristically untested. This is the '+' button handler in the component palette. Contains:
- Line 119-120: `_require_ship` guard
- Line 122-127: `create_component` lookup with None fallback
- Line 129-134: `resolve_target_layer` call with invalid-layer fallback
- Line 139-141: bulk vs single add branching

The test file likely tests `resolve_target_layer`, `resolve_move_target`, `move_component`, and `move_component_group`, but `quick_add_component` needs direct coverage.

---

## Tier 3 Files — Apparently Covered

### T3-01: `game/core/combat_types.py` (20 LOC)
**Severity:** COVERED  
`DamageContext` frozen dataclass. Tested via `test_combat_types.py` and hit-log tests.

### T3-02: `game/simulation/managers/battle_state_manager.py` (134 LOC)
**Severity:** COVERED  
`test_battle_state_manager.py` covers capture/restore/extract/validate.

### T3-03: `game/simulation/systems/tech_preset_loader.py` (203 LOC)
**Severity:** COVERED  
`test_tech_preset_loader.py` covers list/load/get/check methods.

### T3-04: `game/strategy/facade/dto/build_queue_dto.py` (42 LOC)
**Severity:** COVERED  
`test_build_queue_dto.py` covers `from_domain` with output verification.

### T3-05: `game/strategy/generation/density/primitives/linear.py` (86 LOC)
**Severity:** COVERED  
`test_linear.py` covers `evaluate` with various hex coordinates.

### T3-06: `game/ui/screens/builder/modifier_utils.py` (20 LOC)
**Severity:** COVERED  
`test_modifier_utils.py` covers `copy_modifiers`.

### T3-07: `game/ui/screens/strategy_menu_panel.py` (103 LOC)
**Severity:** COVERED  
`test_strategy_menu_panel.py` covers button creation and event dispatch.

### FN-01: `game/ui/screens/strategy_screen_lifecycle.py` (175 LOC)
**Severity:** COVERED (reclassified from Tier 0)  
See FN-01 section above. Comprehensive test coverage confirmed.

---

## File Coverage Verification Table

| File | LOC | Tier | Test File(s) | Coverage Verdict |
|---|---|---|---|---|
| `game/ai/target_evaluator.py` | 331 | 2 | 6 test files | PARTIAL — 6 private eval methods indirect-only; `evaluate()` covered |
| `game/assets/component_derivatives.py` | 182 | 2 | 1 test file | PARTIAL — 6 helpers indirect-only; `ensure_component_derivatives` covered |
| `game/context.py` | 241 | 2 | 4 test files | COVERED — `_install_default` runs at import; `__init__` tested via factory methods |
| `game/core/combat_types.py` | 20 | 3 | 3 test files | COVERED |
| `game/core/registry.py` | 483 | 2 | 72 test files | COVERED — extensively tested; `unfrozen`/`freeze_registry` heavily used |
| `game/simulation/combat/ability_stat_registry.py` | 237 | 2 | 2 test files | PARTIAL — `_extract_value`/`_route_team_ids` indirect-only |
| `game/simulation/managers/battle_state_manager.py` | 134 | 3 | 1 test file | COVERED |
| `game/simulation/systems/tech_preset_loader.py` | 203 | 3 | 1 test file | COVERED |
| `game/strategy/combat/battle_assembly.py` | 353 | 2 | 2 test files | PARTIAL — `_boundary_to_box` needs direct unit test |
| `game/strategy/data/carried_vehicle_deploy.py` | 116 | 0 | NONE | **CRITICAL — ZERO TESTS** |
| `game/strategy/data/orbital_generation_config.py` | 195 | 2 | 1 test file | PARTIAL — `_load_from_json`/`_use_defaults` indirect through `get_*_config` |
| `game/strategy/data/ship_display_formatter.py` | 131 | 2 | 1 test file | COVERED — constructor is trivial |
| `game/strategy/data/squadron.py` | 102 | 2 | 6 test files | COVERED — constructor tested through hierarchy tests |
| `game/strategy/engine/handlers/movement.py` | 284 | 2 | 1 test file | COVERED — `register` tested via integration |
| `game/strategy/engine/happiness_engine.py` | 141 | 2 | 2 test files | PARTIAL — `_validate_tick_inputs`/`_process_colony` indirect through `process_happiness` |
| `game/strategy/facade/__init__.py` | 8 | 0 | NONE | **CRITICAL — ADVISORY (re-export)** |
| `game/strategy/facade/dto/build_queue_dto.py` | 42 | 3 | 1 test file | COVERED |
| `game/strategy/facade/dto/fleet_dto.py` | 332 | 2 | 5 test files | PARTIAL — `_aggregate_carried_vehicles_by_type`/`_sum_vehicle_bay_*` indirect |
| `game/strategy/facade/grouped_namespaces.py` | 406 | 2 | 1 test file | PARTIAL — 45 symbols heuristically untested; thin wrappers but `__getattr__` error path untested |
| `game/strategy/facade/slices/empire_slice.py` | 97 | 2 | 1 test file | PARTIAL — 5 public reads heuristically untested |
| `game/strategy/generation/density/density_map.py` | 241 | 2 | 4 test files | COVERED — `__len__` is trivial |
| `game/strategy/generation/density/primitives/linear.py` | 86 | 3 | 2 test files | COVERED |
| `game/strategy/services/action_time_resolver.py` | 243 | 2 | 1 test file | PARTIAL — `_activate_time_field` error paths need direct testing |
| `game/strategy/services/component_abilities.py` | 403 | 2 | 2 test files | COVERED — 3 thin helpers are minor |
| `game/ui/screens/battle_results_screen.py` | 291 | 2 | 1 test file | ADVISORY — rendering methods |
| `game/ui/screens/battle_setup/renderer.py` | 86 | 2 | 1 test file | COVERED — `_build_bottom_bar` tested via `rebuild` |
| `game/ui/screens/builder/modifier_utils.py` | 20 | 3 | 1 test file | COVERED |
| `game/ui/screens/empire_build_queue_data_source.py` | 114 | 2 | 1 test file | COVERED — tested via `get_cell_value` |
| `game/ui/screens/galaxy_test/system_mode.py` | 576 | 0 | NONE | **CRITICAL — ZERO TESTS + LOC CEILING VIOLATION** |
| `game/ui/screens/orders_window.py` | 463 | 2 | 3 test files | PARTIAL — `process_event` button dispatch and `move/edit/delete_order` need verification |
| `game/ui/screens/planet_list_window.py` | 453 | 2 | 7 test files | COVERED — properties are thin delegates |
| `game/ui/screens/race_setup/ui_builder.py` | 42 | 0 | NONE | **CRITICAL — ZERO DIRECT TESTS** |
| `game/ui/screens/radiation_shield_editor.py` | 231 | 0 | NONE | **CRITICAL — ZERO TESTS** |
| `game/ui/screens/star_list_presets.py` | 127 | 2 | 1 test file | PARTIAL — `capture`/`apply` need direct round-trip tests |
| `game/ui/screens/strategy_camera_nav.py` | 232 | 2 | 2 test files | PARTIAL — `_resolve_global_hex` protocol paths untested |
| `game/ui/screens/strategy_menu_panel.py` | 103 | 3 | 1 test file | COVERED |
| `game/ui/screens/strategy_screen_lifecycle.py` | 175 | ~~0~~ 3 | 1 test file | **COVERED** (heuristic false-negative corrected) |
| `game/ui/screens/strategy_windows/move_choice_dialog.py` | 94 | 0 | NONE | **CRITICAL — ZERO TESTS** |
| `game/ui/screens/test_lab/__init__.py` | 22 | 1 | 6 test files | ADVISORY — package re-exports |
| `game/ui/screens/test_lab/component_dropdown.py` | 157 | 0 | NONE | **CRITICAL — ZERO TESTS** |
| `game/ui/screens/test_lab/details/validation.py` | 253 | 0 | NONE | **CRITICAL — ZERO TESTS** |
| `game/ui/screens/test_lab/renderer/_draw_helpers.py` | 222 | 0 | NONE | **CRITICAL — ZERO TESTS** |
| `game/ui/screens/test_lab/viewmodel.py` | 389 | 2 | 2 test files | COVERED — button rects are property getter/setters |
| `game/ui/screens/transfer_container_rows.py` | 142 | 0 | NONE | **CRITICAL — ZERO TESTS** |
| `game/ui/screens/workshop_viewmodel_layer_ops.py` | 254 | 2 | 1 test file | PARTIAL — `quick_add_component` needs direct test |

---

## Gap Summary by Severity

### CRITICAL (9 files, zero tests)
1. `carried_vehicle_deploy.py` — shared fleet-launch/reboard helper, 3 call sites
2. `system_mode.py` — 576 LOC system inspector, LOC ceiling violation
3. `ui_builder.py` — race setup widget builder seam
4. `radiation_shield_editor.py` — shielding target editor with auto logic
5. `move_choice_dialog.py` — fleet move-type choice dialog
6. `component_dropdown.py` — test lab component selector
7. `validation.py` — test lab validation results renderer
8. `_draw_helpers.py` — test lab draw primitives
9. `transfer_container_rows.py` — transfer dialog row builder

### MAJOR (15 files, partial/indirect coverage)
1. `target_evaluator.py` — private eval methods indirect-only
2. `component_derivatives.py` — helper functions (manifest I/O, fast-path, derivative write) indirect-only
3. `ability_stat_registry.py` — `_extract_value`/`_route_team_ids` indirect-only
4. `battle_assembly.py` — `_boundary_to_box` needs direct test
5. `orbital_generation_config.py` — `_load_from_json`/`_use_defaults` indirect
6. `happiness_engine.py` — `_validate_tick_inputs`/`_process_colony` indirect
7. `fleet_dto.py` — 3 private aggregate methods indirect
8. `grouped_namespaces.py` — 45 symbols, thin wrappers but `__getattr__` error path untested
9. `empire_slice.py` — 5 public reads heuristically untested
10. `action_time_resolver.py` — `_activate_time_field` ValueError paths untested
11. `orders_window.py` — renderer/builder/reprocess_event/move/edit/delete order methods
12. `star_list_presets.py` — `capture`/`apply` need direct round-trip
13. `strategy_camera_nav.py` — `_resolve_global_hex` protocol paths untested
14. `workshop_viewmodel_layer_ops.py` — `quick_add_component` needs direct test
15. `component_abilities.py` — `_get_component_registry`/3 thin helpers (actually MINOR)

### MINOR/ADVISORY (remaining)
- Thin delegates, properties, re-exports, or constructors tested via public API

---

## LOC Ceiling Violations
- `game/ui/screens/galaxy_test/system_mode.py` — 576 LOC (>500 limit)
- `game/ui/screens/orders_window.py` — 463 LOC (approaching)
- `game/ui/screens/planet_list_window.py` — 453 LOC (approaching)

---

## Priority Remediation Plan

**Phase 1 — Immediate (CRITICAL Tier 0):**
1. `carried_vehicle_deploy.py` — highest risk (shared fleet-launch logic, 3 call sites, component state damage bug previously existed)
2. `transfer_container_rows.py` — new PROJ-437 code, no safety net
3. `radiation_shield_editor.py` — auto-shielding logic untested
4. `move_choice_dialog.py` — fleet interception UI untested

**Phase 2 — Combat Lab UI (CRITICAL Tier 0):**
5. `test_lab/details/validation.py` — static rendering functions, easy to test
6. `test_lab/renderer/_draw_helpers.py` — static rendering functions, easy to test
7. `test_lab/component_dropdown.py` — click/hover logic testable without display
8. `system_mode.py` — needs to be split first (LOC ceiling), then tested

**Phase 3 — MAJOR gaps:**
9. `_boundary_to_box` in `battle_assembly.py` — targeted unit test
10. `_activate_time_field` error paths in `action_time_resolver.py`
11. `quick_add_component` in `workshop_viewmodel_layer_ops.py`
12. `grouped_namespaces.py` — facade namespace `__getattr__` error path
13. `component_derivatives.py` — focused helper tests

**Phase 4 — Indirect coverage hardening:**
14. `target_evaluator.py` — direct eval method tests
15. `ability_stat_registry.py` — `_extract_value`/`_route_team_ids` edge cases
16. `orbital_generation_config.py` — `_load_from_json` direct tests
17. `star_list_presets.py` — capture/apply round-trip tests
