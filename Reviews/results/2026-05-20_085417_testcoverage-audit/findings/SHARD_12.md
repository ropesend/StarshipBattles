# Shard 12 — Test Coverage Audit Report

**Audit date:** 2026-05-20 | **Agent:** OpenCode (skeptical verification)  
**Files audited:** 44 production files, ~9506 LOC  
**Tests verified:** Heuristic baseline cross-checked with live code + test file reading

---

## Heuristic Baseline Corrections

The Phase 1 heuristic had **3 classification errors** in this shard:

| File | Heuristic Tier | Corrected Tier | Reason |
|---|---|---|---|
| `species_selector_mixin.py` | Tier 0 | Tier 2 | Has real tests in `test_species_selector_mixin.py` |
| `json_diff.py` (`compute_json_diff`) | Tier 2 (partially covered) | Tier 2 (MAJOR gap) | `compute_json_diff` has ZERO test coverage — heuristic was wrong |
| `new_game_setup_ui_builder.py` | Tier 0 | Tier 1 | Thin builder used via fixture mocks in `NewGameSetupScreen` tests |

---

## Summary

| Severity | Count | Description |
|---|---|---|
| **CRITICAL** | 6 | Tier 0 non-UI files with zero tests |
| **MAJOR** | 9 | Tier 1 / untested error paths / logic with zero coverage |
| **MINOR** | 12 | Partial coverage gaps, missing corner cases |
| **ADVISORY** | 8 | `__init__.py` re-exports, UI rendering, thin wrappers |

---

## Tier 0 — CRITICAL: Non-UI Files with Zero Tests

### 1. `game/strategy/engine/handlers/recover_satellites.py` (111 LOC)
**CRITICAL** — `RecoverSatellitesCommandHandler` has ZERO unit tests.

All 5 symbols are uncovered:
- `RecoverSatellitesCommandHandler` (L37-38, `@command_spec` decorator)
- `RecoverSatellitesCommandHandler.execute` (L41-51) — dispatches to `_execute_fleet` / `_execute_planet` based on `cmd.planet_id`
- `RecoverSatellitesCommandHandler._execute_fleet` (L53-83) — resolves fleet + carrier, issues `recover_satellites` order
- `RecoverSatellitesCommandHandler._execute_planet` (L85-101) — resolves planet, issues `recover_satellites` order
- `register` (L104-108) — registers the handler in `CommandRegistry`

**Note:** The heuristic incorrectly flagged this because the Phase 1 scanner confused this CommandHandler (`handlers/recover_satellites.py`) with the OrderHandler variant at `order_handlers/recover_satellites_handler.py`. The OrderHandler HAS tests (`test_recover_satellites_handler.py`, 8 tests), but this CommandHandler does not.

**Error paths untested:**
- L46-48: `check_issuer_invariant` failure return
- L49-51: planet/fleet dispatch branch
- L56-58: fleet not found / error return
- L59-62: missing `ship_instance_id` validation
- L63-71: carrier not found in fleet
- L88-90: planet not found / error return

**Priority:** HIGH. This is the command-side of the FMS recovery pipeline. Missing tests mean command validation edge cases (invalid fleet, invalid planet, missing ship) are unchecked.

### 2. `game/strategy/interfaces/engines/movement.py` (96 LOC)
**CRITICAL** — `IMovementEngine` ABC has ZERO unit tests.

This is a Protocol/ABC defining the contract for fleet movement engines. While ABCs are interfaces, this one has 3 abstract methods:
- `IMovementEngine.collect_movements` (L40-60) — signature contract
- `IMovementEngine.apply_movements` (L62-78) — signature contract  
- `IMovementEngine.calculate_next_hex` (L80-96) — signature contract

The concrete implementation `FleetMovementEngine` IS tested, but the interface itself has no coverage. Per conventions, ABC protocol tests (mock implementations, contract verification) are standard practice.

### 3. `game/strategy/services/fleet_warp_resolution.py` (98 LOC)
**CRITICAL** — Two pure functions with ZERO test coverage.

All 2 symbols uncovered:
- `compute_path_for_warp` (L24-52) — computes path-to-WP + reciprocal exit hex. Deep logic: path calculation, start-hex stripping, exit resolution. Has branches at L37-45 (path exists, start matches) and L48-50 (exit hex found).
- `resolve_warp_exit` (L55-98) — resolves reciprocal warp point. Has 4 error branches (L68, L80, L86, L91) and a fallback at L98.

**Error paths untested:**
- `compute_path_for_warp`:
  - L37: fleet NOT at warp point → pathfinding
  - L43: path starts at current location → strip
  - L48-50: exit hex exists/doesn't exist
- `resolve_warp_exit`:
  - L68: no warp point at hex
  - L80: warp point not found at local offset
  - L86: destination system not found
  - L91-94: reciprocal warp point found (normal path)
  - L97-98: fallback to system center

**Priority:** HIGH. These are pure functions with complex logic. Tests should be trivial to write (mock `NavigationState`, `galaxy`).

### 4. `game/strategy/generation/__init__.py` (23 LOC)
**CRITICAL** — Re-export module with ZERO tests.

Re-exports `DensityMap`, `ISystemPlacementStrategy`, `RandomPlacementStrategy`, `DensityBasedPlacementStrategy`, `PlanetImageRegistry`, `StarImageRegistry`.

While this is a thin re-export `__init__.py`, tests should verify the re-export surface is correct (all exports resolve to actual classes).

### 5. `game/services/__init__.py` (13 LOC)
**CRITICAL** — Package docstring only, zero symbols, zero tests.

Pure documentation `__init__.py`. ADVISORY-grade, but classified as Tier 0 by the system.

### 6. `game/ui/screens/test_lab/details/panel.py` (216 LOC)
**CRITICAL** — `TestRunDetailsPanel` has ZERO unit tests (UI file but complex state logic).

8 symbols uncovered:
- `TestRunDetailsPanel.__init__` (L34-70) — initializes colors, fonts, scroll state, button rects
- `TestRunDetailsPanel.set_run` (L72-76) — sets selected run + recalculates scroll
- `TestRunDetailsPanel.clear` (L78-81) — clears state
- `TestRunDetailsPanel._calculate_scroll` (L83-103) — computes content height from metrics + validation results
- `TestRunDetailsPanel.handle_event` (L105-138) — scroll + button click dispatch (View States, Use Seed, Copy Results)
- `TestRunDetailsPanel._build_ctx` (L140-159) — builds frozen `DetailsDrawContext`
- `TestRunDetailsPanel.draw` (L161-216) — full rendering pipeline dispatching to `chrome`, `validation`, `resource_outcomes`, `propulsion_outcomes`

**Priority:** MEDIUM. Contains non-trivial scroll calculation (L90-102) and event dispatching (L111-131) that could benefit from unit tests.

---

## Tier 1 — MAJOR: Files with Symbol Gaps

### 7. `game/simulation/components/__init__.py` (5 LOC)
**MAJOR** — Empty namespace marker. Intentional no-re-export design. Tests exist via package submodule imports. ADVISORY-grade.

### 8. `game/ui/screens/builder/modifier_config.py` (99 LOC)
**MAJOR** — Module-level configuration data (`MODIFIER_UI_CONFIG`, `DEFAULT_CONFIG`). No functions to test directly. Tests in `test_modifier_config_size_mount.py` and `test_slider_increment.py` exercise the config data indirectly through the builder UI. ADVISORY-grade.

### 9. `game/ui/screens/new_game_setup_ui_builder.py` (41 LOC)
**MAJOR** (reclassified from Tier 0) — Thin builder delegating to `screen._create_ui()`. Tests for `NewGameSetupScreen` indirectly exercise this through the fixture mock at `tests/fixtures/new_game_setup_ui_builder.py`. The builder has no independent logic. ADVISORY-grade.

---

## Tier 2 — MINOR: Partial Coverage Gaps

### 10. `game/simulation/components/abilities/stat_keys.py` (201 LOC)
**MINOR** — `AbilityStatBinding.__post_init__` (L143-154) validation logic is heuristically untested.

Verification: The `__post_init__` raises `ValidationException` for invalid operations. Test search across `tests/unit/modifiers/` reveals no test that constructs `AbilityStatBinding` with an invalid `operation` string. The `apply` method (L162-192) IS well-tested through ability binding tests.

**Recommended test:** `test_ability_stat_binding_rejects_invalid_operation` passing `operation='divide'`.

### 11. `game/simulation/components/component_loader.py` (323 LOC)
**MINOR** — `ComponentCacheManager.__init__` (L60-64) is heuristically untested.

Verification: `ComponentCacheManager` is constructed by `reset_component_caches()` for test isolation and by `get_default_cache_manager()`. The `__init__` sets 4 instance attributes to `None`. While trivial, no test directly constructs `ComponentCacheManager` to verify initial state.

### 12. `game/simulation/entities/projectile.py` (212 LOC)
**MINOR** — `_default_event_logger` (L8-20) is heuristically untested.

Verification: This is a no-op default (intentionally silent per PROJ-390). Not a gap — it's a deliberate sentinel. **RECLASSIFY: NOT A GAP.**

### 13. `game/simulation/managers/retreat_manager.py` (280 LOC)
**MINOR** — Two claimed untested symbols:

**`RetreatManager.__init__`** (L61-75): Sets `boundary`, initializes empty dicts/lists, sets `_on_ship_escaped=None`. Tests construct `RetreatManager` but don't verify the initial state independently.

**`RetreatManager._handle_ship_escaped`** (L182-192): Sets `ship.retreat_status = "escaped"`, appends to `escaped_ships`, logs, calls callback. This IS exercised by the `update` method tests, but no test directly calls `_handle_ship_escaped` to verify the callback invocation path (L191-192).

**Recommended test:** `test_escape_callback_invoked` — set a mock callback and verify it's called with the escaping ship.

### 14. `game/strategy/data/fleet_pursuer_tracker.py` (145 LOC)
**MINOR** — Two claimed untested symbols:

**`FleetPursuerTracker.__init__`** (L35-37): Simple constructor. Tests exist but don't independently verify initial state.

**`FleetPursuerTracker._remove_orders_targeting_fleet`** (L134-145): Iterates in reverse to pop pursuit orders, clears path if active order removed. This IS tested indirectly through `notify_target_destroyed` (L112-131), but the edge case at L144 (`pursuer.path and not pursuer.orders`) has no direct assertion test.

### 15. `game/strategy/engine/fleet_movement_engine.py` (383 LOC)
**MINOR** — Two claimed untested symbols:

**`FleetMovementEngine.__init__`** (L58-79): Simple constructor. Tests construct the engine but don't independently assert initial state.

**`FleetMovementEngine._get_fleet_mutator`** (L81-93): Lazy-defaults `FleetWriteService`. Tests DO exercise this indirectly via `apply_movement` (L205). However, the lazy-init branch where BOTH `_nav_service` and `_fleet_mutator` are `None` (L88-89) has no direct assertion.

**Correction to heuristic:** `_get_effective_fleet_speed` IS tested (5 assertions in `test_characterization.py`). `_filter_jump_past_collisions` IS tested (5+ tests in `test_characterization.py`). The heuristic was wrong about these.

### 16. `game/strategy/engine/planet_energy_engine.py` (325 LOC)
**MINOR** — Six claimed untested symbols. After verification:

Actually UNTESTED:
- `_extract_abilities` (L83-89): Thin delegation wrapper to `extract_abilities_from_component`. No direct test.
- `PlanetEnergyEngine._get_planet_mutator` (L167-173): Lazy-init path for `PlanetWriteService`. No test directly sets `planet_mutator=None` and verifies lazy init.
- `PlanetEnergyEngine._get_facility_fingerprint` (L185-189): Builds tuple of `(instance_id, is_operational)`. No direct test, but implicitly tested through `_process_planet` (L219: `fingerprint = self._get_facility_fingerprint(planet)`).
- `PlanetEnergyEngine._compute_activation_drain` (L280-292): Sums energy drain from `ComponentActivationState` entries. Tested indirectly through `test_shield_drains_energy` and `test_shield_auto_deactivates`, but no test directly calls this method.
- `PlanetEnergyEngine._cancel_all_draining_components` (L294-324): Cancels all draining components and logs events. Tested indirectly through `test_shield_auto_deactivates_on_energy_depletion`, but no test verifies the event_bus integration (L311-324 with `if self._event_bus`).

**`PlanetEnergyEngine.__init__`** (L136-163): Constructor, explicitly tested through the construction in all 20 tests. NOT a gap.

### 17. `game/strategy/engine/water_engine.py` (73 LOC)
**MINOR** — Two claimed untested symbols:

**`WaterEngine.__init__`** (L25-26): Simple constructor. Tests construct `WaterEngine` but don't independently assert.

**`WaterEngine._process_colony`** (L40-73): Core logic — sums `WaterModifier` rates, applies delta toward `water_target`. IS tested through `process_water_modification` tests. The edge case at L67-70 (overshoot protection: `abs(delta) <= total_rate` vs `else`) has no direct unit test.

### 18. `game/strategy/generation/placement_strategies.py` (210 LOC)
**MINOR** — `DensityBasedPlacementStrategy.__init__` (L129-135): Simple constructor. Tests exist but don't independently assert.

### 19. `game/strategy/generation/star_image_registry.py` (111 LOC)
**MINOR** — Two claimed untested symbols:

**`StarImageRegistry.__init__`** (L30-35): Initializes `_type_to_images` dict and calls `_load_from_manifest`. Tests construct the registry but don't verify empty initial state.

**`StarImageRegistry._load_from_manifest`** (L37-68): Core loading logic with error branches:
- L40-42: manifest load failure
- L49-53: parsing `stars` section for basenames
- L56-64: mapping `StarType` names to color keys
- L58-61: unknown `StarType` warning

Tests DO exercise the successful path, but the error branches (manifest `None`, unknown star types, non-list paths) have no direct test assertions.

### 20. `game/strategy/services/system_destroyer.py` (187 LOC)
**MINOR** — `SystemDestructionResult` (L69-76): Simple dataclass. Tests exist for `collect_system_contents` and `destroy_system`. The `SystemDestructionResult` dataclass itself has no standalone test, but it's used as a return type. NOT a significant gap.

### 21. `game/ui/components/table/virtual_table.py` (696 LOC)
**MINOR** — Five claimed untested symbols. After verification:

Actually UNTESTED:
- `VirtualTable._build_containers` (L122-152): Builds header, list panel, scrollbar. Not independently tested — called only from `__init__`.
- `VirtualTable._pool_dims_changed` (L154-181): Cache-fingerprint comparison. No direct test for fingerprint matching/mismatch logic.
- `VirtualTable._update_selection_highlights` (L569-590): Updates row background colors. Called from `handle_click` but no test independently calls this method.
- `VirtualTable.scroll_bar` (L677-680): Simple property getter. NOT a gap.

**`VirtualTable._rebuild_row_pool`** (L183-313): IS tested (3 tests in `test_virtual_table.py`). Heuristic was wrong.

### 22. `game/ui/screens/design_selector_window.py` (708 LOC)
**MINOR** — Nine claimed untested symbols:

Actually significant gaps:
- `DesignSelectorUiBuilder.build` (L40-44): Tested via `NullDesignSelectorWindowUiBuilder` mock. NOT a real gap.
- `DesignSelectorWindow._create_main_list` (L263-283): Widget construction. No independent test.
- `DesignSelectorWindow._create_bottom_buttons` (L286-318): Widget construction. No independent test.
- `DesignSelectorWindow._get_role_filter_options` (L388-399): Registry-driven query. No independent test.
- `DesignSelectorWindow._get_type_filter_options` (L401-413): Registry-driven query. No independent test.
- `DesignSelectorWindow._get_class_filter_options` (L415-429): Registry-driven query. No independent test.
- `DesignSelectorWindow._sanitize_object_id` (L457-460): Pure string replacement. No independent test.
- `DesignSelectorWindow.update` (L701-708): One-line delegation to `super().update()`.

**`DesignSelectorWindow.__init__`** is tested through existing tests. `DesignSelectorUiBuilder` is a compositional-construction seam — its test gap is normal.

### 23. `game/ui/screens/keybindings_scene.py` (584 LOC)
**MINOR** — 14 claimed untested symbols. This is a UI rendering file with heavy pygame_gui widget construction. Most untested symbols are widget-build methods or rendering code (`_build_ui`, `_build_action_rows`, `_build_action_row`, `_build_footer`, `_clear_ui`, `_draw_capture_overlay`, `_refresh_all_rows`, `_refresh_action_row`).

Significant logic gaps:
- `KeybindingsScene._handle_key_capture` (L364-421): Conflict detection + dialog. No direct test.
- `KeybindingsScene._apply_binding` (L423-439): Applies binding + clears conflicts. No direct test.
- `KeybindingsScene._handle_button_press` (L479-501): Button dispatch. No direct test.

**`_build_key_name_map`** (L62-68): Module-level init function, idempotent. Called from `__init__`. Test exists at `tests/unit/ui/screens/test_keybindings_scene.py`.

### 24. `game/ui/screens/planet_list_filter_manager.py` (148 LOC)
**MINOR** — `PlanetListFilterManager.__init__` (L47-72): Simple constructor. Tests DO exercise this through the fixture in `test_planet_list_filter_manager.py`. NOT a gap.

### 25. `game/ui/screens/setup_screen.py` (292 LOC)
**MINOR** — Two claimed untested symbols:

**`BattleSetupScreen.get_team_display_groups`** (L133-144): Pure data transformation. Tests at `TestBattleSetupScreen` exist but may not directly test this method.

**`BattleSetupScreen._handle_action_buttons`** (L206-218): Complex click-to-action dispatch. Not independently tested — called from `_handle_click`.

### 26. `game/ui/utils/json_diff.py` (113 LOC)
**MAJOR** — `compute_json_diff` has ZERO test coverage. The heuristic claimed it was covered via `test_scrollable_json_panel.py`, but that test has no mention of `compute_json_diff` at all. 

Actually uncovered:
- `compute_json_diff` (L33-89): Full recursive diff algorithm with branches for:
  - L48-51: type mismatch
  - L53-69: dict comparison (added keys, removed keys, recursion)
  - L71-82: list comparison (added items, removed items, recursion)
  - L84-88: primitive comparison
- `_mark_all_paths` (L92-113): Recursive subtree marking (ADDED/REMOVED)

**Priority:** HIGH. This is pure logic with no external dependencies. Should be trivial to test.

### 27. `game/ui/panels/race_description_panel.py` (418 LOC)
**MINOR** — `RaceDescriptionPanel._tick_field_label` (L343-356): Per-frame elapsed-seconds label update. Called from `update()` (L307-341). The test `test_race_description_panel.py` exercises the panel but may not test the per-frame tick behavior independently.

### 28. `game/ui/panels/race_identity_panel.py` (493 LOC)
**MINOR** — Four claimed untested:

**`RaceIdentityPanel._create_race_section`** (L102-159), **`_create_government_section`** (L161-255), **`_create_faction_section`** (L257-295): Widget construction methods. Called from `_create_content`. Tests at `test_race_identity_panel.py` exist but may not test these independently.

**`RaceIdentityPanel._recreate_dropdown`** (L423-453): Kills old dropdown, creates new one with selected value. No independent test.

### 29. `game/ui/pygame_gui_patch.py` (208 LOC)
**MINOR** — Three claimed untested:

**`_detect_upstream_bug`** (L64-71): Source-fingerprint inspection. Module-level init. NOT a gap — it's a build-time check.

**`_to_tuple`** (L90-94): Simple `list | None → tuple | None` conversion. No independent test, but trivial.

**`StarshipUIAppearanceTheme.__init__`** (L105-110): Super + dict init. Tests exist at `test_pygame_gui_patch.py` for the patch but may not test the constructor independently.

### 30. `game/ui/screens/cargo_quick_dialog_controller.py` (131 LOC)
**MINOR** — Four claimed untested:

**`CargoQuickDialogController.__init__`** (L35-39): Simple constructor. Tests exist but may not verify independently.

**`CargoQuickDialogController.get_unload_items`** (L43-49), **`get_load_items`** (L51-55), **`get_target_planet_id`** (L57-65): All delegate to `CargoTransferService`. Tests exist at `test_cargo_quick_dialog_controller_widget_purity.py` but test widget purity, not query correctness.

### 31. `game/ui/screens/test_lab/renderer/metadata_panel.py` (221 LOC)
**MINOR** — `MetadataPanel.__init__` (L26-52): Constructor with 13 parameters. Tests at `test_metadata_panel.py` exist but may not independently verify constructor state.

### 32. `game/ui/screens/test_lab/test_executor.py` (393 LOC)
**MINOR** — Five claimed untested:

**`TestLabExecutor.run_visual`** (L76-127): Visual test execution. Has tests in `test_visual_run.py`.
**`TestLabExecutor.run_visual_baseline`** (L129-173): Visual baseline. Tests in `test_visual_run.py`.
**`TestLabExecutor._run_scenario_via_run_battle`** (L239-304): Core headless path. Tests in `test_batch_skip.py`.
**`TestLabExecutor.run_all`** (L306-323): Batch init.
**`TestLabExecutor.continue_batch`** (L390-393): Batch continuation.

These are tested indirectly but the test files focus on batch skip + visual run. No test independently verifies `run_all`'s batch initialization (L313-323) or `continue_batch`'s delegation.

### 33. `game/ui/services/ship_io_adapter.py` (100 LOC)
**MINOR** — `ShipIOAdapter.__init__` (L41-51): Simple constructor with lazy import of ShipIO. Tests at `test_ship_io_adapter.py` exist.

### 34. `game/ui/fonts.py` (92 LOC)
**MINOR** — `_ensure_cache_valid` (L29-47): Cache validation function. Tests at `test_fonts.py` test `get_font` and `get_default_font` which call `_ensure_cache_valid`, but no test verifies the cache-invalidation path (L35-47: empty cache early return, font error clearing).

---

## Tier 3 — APPARENTLY COVERED: Verified

### 35. `game/core/spectrum_math.py` (155 LOC)
VERIFIED COVERED. Tests at `tests/unit/core/test_spectrum_math.py`. `kelvin_to_rgb`, `stefan_boltzmann_luminosity`, `wien_peak_wavelength` all have dedicated tests.

### 36. `game/simulation/components/modifiers.py` (149 LOC)
VERIFIED COVERED. Tests at `tests/unit/simulation/components/test_modifiers.py` and `tests/unit/modifiers/test_invalid_operation_handling.py`. `apply_modifier_effects`, `get_default_stat_multipliers`, `calculate_stat_multipliers` all tested.

### 37. `game/strategy/data/order_types.py` (167 LOC)
VERIFIED COVERED. 105 candidate test files reference `OrderType` and `Order`. `to_dict` and `from_dict` tested in `test_order_serializer.py` and `test_order_types_characterization.py`.

### 38. `game/strategy/generation/density/primitives/geometric.py` (101 LOC)
VERIFIED COVERED. `GeometricPrimitive.evaluate` tested in `test_geometric.py`. Conftest fixtures support it.

### 39. `game/strategy/interfaces/battle_resolver.py` (109 LOC)
VERIFIED COVERED. `BattleResult` and `IBattleResolver` tested in `test_battle_resolver.py` and `test_battle_resolver_replay_id.py`.

### 40. `game/strategy/services/galaxy_pathfinding_service.py` (211 LOC)
VERIFIED COVERED. All 7 symbols tested across `test_galaxy_pathfinding_service.py`, `test_basic_paths.py`, `test_edge_cases.py`, etc.

### 41. `game/strategy/services/modifier_resolver.py` (69 LOC)
VERIFIED COVERED. `resolve_size_multiplier` and `resolve_stat_from_size_mount` tested in `test_modifier_resolver.py`.

### 42. `game/strategy/systems/save_game_service.py` (588 LOC)
LARGELY COVERED. 10 test files with extensive error-handling coverage (18 error-path tests in `test_error_handling.py`). Three heuristically-flagged gaps:

**`_flush_pending_built_counts`** (L488-522): NOT directly tested. Complex logic with `services` attribute check, `design_catalogs_by_empire` iteration, `DesignRepository` import, per-empire flush. No test explicitly constructs a session with pending built counts and verifies flush.

**`_validate_save`** (L525-547): NOT directly tested. Called from `_load_save_metadata`, but no test independently calls `_validate_save` with missing turns folder or non-directory paths.

**`_is_compatible_version`** (L550-556): NOT directly tested. Simple one-line comparison, but no test independently verifies version rejection.

### 43. `game/ui/fonts.py` (92 LOC) — Partially in Tier 2
See item 34 above for `_ensure_cache_valid` gap. `get_font` and `get_default_font` ARE tested.

### 44. `game/ui/panels/race_description_panel.py` (418 LOC) — Partially in Tier 2
See item 27 above for `_tick_field_label` gap.

---

## File Coverage Verification Table

| # | File | LOC | Tier | Test Files | Gaps | Severity |
|---|---|---|---|---|---|---|
| 1 | `game/core/spectrum_math.py` | 155 | 3 | `test_spectrum_math.py` | None | Covered |
| 2 | `game/services/__init__.py` | 13 | 0 | None | Package doc only | ADVISORY |
| 3 | `game/simulation/components/__init__.py` | 5 | 1 | None | Namespace marker | ADVISORY |
| 4 | `game/simulation/components/abilities/stat_keys.py` | 201 | 2 | 20 files | `__post_init__` validation | MINOR |
| 5 | `game/simulation/components/component_loader.py` | 323 | 2 | 9 files | `__init__` not independently tested | MINOR |
| 6 | `game/simulation/components/modifiers.py` | 149 | 3 | 2 files | None | Covered |
| 7 | `game/simulation/entities/projectile.py` | 212 | 2 | 7 files | `_default_event_logger` (no-op, not a gap) | Covered |
| 8 | `game/simulation/managers/retreat_manager.py` | 280 | 2 | 2 files | `_handle_ship_escaped` callback path | MINOR |
| 9 | `game/strategy/data/fleet_pursuer_tracker.py` | 145 | 2 | 2 files | `_remove_orders_targeting_fleet` edge case | MINOR |
| 10 | `game/strategy/data/order_types.py` | 167 | 3 | 105 files | None | Covered |
| 11 | `game/strategy/engine/fleet_movement_engine.py` | 383 | 2 | 9 files | `__init__` not independently tested | MINOR |
| 12 | `game/strategy/engine/handlers/recover_satellites.py` | 111 | 0 | None | **ALL symbols** | **CRITICAL** |
| 13 | `game/strategy/engine/order_handlers/__init__.py` | 45 | 1 | 1 indirect | Re-export module | ADVISORY |
| 14 | `game/strategy/engine/planet_energy_engine.py` | 325 | 2 | 4 files | `_extract_abilities`, `_get_planet_mutator`, `_compute_activation_drain`, `_cancel_all_draining_components` event_bus path | MINOR |
| 15 | `game/strategy/engine/water_engine.py` | 73 | 2 | 2 files | `_process_colony` overshoot branch | MINOR |
| 16 | `game/strategy/generation/__init__.py` | 23 | 0 | None | Re-export verification | **CRITICAL** |
| 17 | `game/strategy/generation/density/primitives/geometric.py` | 101 | 3 | 2 files | None | Covered |
| 18 | `game/strategy/generation/placement_strategies.py` | 210 | 2 | 1 file | `__init__` not independently tested | MINOR |
| 19 | `game/strategy/generation/star_image_registry.py` | 111 | 2 | 1 file | `_load_from_manifest` error branches | MINOR |
| 20 | `game/strategy/interfaces/battle_resolver.py` | 109 | 3 | 9 files | None | Covered |
| 21 | `game/strategy/interfaces/engines/movement.py` | 96 | 0 | None | **ALL symbols** (ABC) | **CRITICAL** |
| 22 | `game/strategy/services/fleet_warp_resolution.py` | 98 | 0 | None | **ALL symbols** | **CRITICAL** |
| 23 | `game/strategy/services/galaxy_pathfinding_service.py` | 211 | 3 | 7 files | None | Covered |
| 24 | `game/strategy/services/modifier_resolver.py` | 69 | 3 | 1 file | None | Covered |
| 25 | `game/strategy/services/system_destroyer.py` | 187 | 2 | 1 file | `SystemDestructionResult` dataclass | MINOR |
| 26 | `game/strategy/systems/save_game_service.py` | 588 | 2 | 10 files | `_flush_pending_built_counts`, `_validate_save`, `_is_compatible_version` | MAJOR |
| 27 | `game/ui/components/table/virtual_table.py` | 696 | 2 | 1 file | `_build_containers`, `_pool_dims_changed`, `_update_selection_highlights` | MINOR |
| 28 | `game/ui/fonts.py` | 92 | 2 | 1 file | `_ensure_cache_valid` invalidation path | MINOR |
| 29 | `game/ui/panels/race_description_panel.py` | 418 | 2 | 1 file | `_tick_field_label` | MINOR |
| 30 | `game/ui/panels/race_identity_panel.py` | 493 | 2 | 2 files | `_recreate_dropdown`, section constructors | MINOR |
| 31 | `game/ui/pygame_gui_patch.py` | 208 | 2 | 1 file | `_to_tuple`, `__init__` | MINOR |
| 32 | `game/ui/screens/builder/modifier_config.py` | 99 | 1 | 2 indirect | Config data only | ADVISORY |
| 33 | `game/ui/screens/cargo_quick_dialog_controller.py` | 131 | 2 | 1 file | Query methods not independently tested | MINOR |
| 34 | `game/ui/screens/design_selector_window.py` | 708 | 2 | 1 file | Filter-option builders, `_sanitize_object_id` | MINOR |
| 35 | `game/ui/screens/keybindings_scene.py` | 584 | 2 | 1 file | 14 widget-build/handler methods | MINOR |
| 36 | `game/ui/screens/new_game_setup_ui_builder.py` | 41 | 1 | 0 (fixture) | Thin builder | ADVISORY |
| 37 | `game/ui/screens/planet_list_filter_manager.py` | 148 | 2 | 1 file | `__init__` (trivial) | MINOR |
| 38 | `game/ui/screens/setup_screen.py` | 292 | 2 | 2 files | `_handle_action_buttons` | MINOR |
| 39 | `game/ui/screens/species_selector_mixin.py` | 163 | 2 | 1 file | `build_species_selector` widget creation | MINOR |
| 40 | `game/ui/screens/test_lab/details/panel.py` | 216 | 0 | None | **ALL symbols** | **CRITICAL** |
| 41 | `game/ui/screens/test_lab/renderer/metadata_panel.py` | 221 | 2 | 1 file | `__init__` not independently tested | MINOR |
| 42 | `game/ui/screens/test_lab/test_executor.py` | 393 | 2 | 2 files | `run_all`/`continue_batch` init path | MINOR |
| 43 | `game/ui/services/ship_io_adapter.py` | 100 | 2 | 1 file | `__init__` not independently tested | MINOR |
| 44 | `game/ui/utils/json_diff.py` | 113 | 2 | 0 | **`compute_json_diff` + `_mark_all_paths`** | **MAJOR** |

---

## Priority Remediation Queue

1. **CRITICAL: `fleet_warp_resolution.py`** — 2 pure functions, 0 tests. Write 4-6 tests covering all branches of `compute_path_for_warp` and `resolve_warp_exit`.
2. **CRITICAL: `RecoverSatellitesCommandHandler`** — Write 6-8 tests mirroring the OrderHandler pattern: valid fleet dispatch, valid planet dispatch, missing fleet, missing ship, missing planet, invariant failure.
3. **CRITICAL: `TestRunDetailsPanel`** — Write unit tests for `set_run`, `_calculate_scroll`, `handle_event` (button clicks, scroll).
4. **MAJOR: `compute_json_diff`** — Write exhaustive tests for dict diff (added, removed, changed, nested), list diff, primitive diff, type-change detection.
5. **MAJOR: `_flush_pending_built_counts`** — Write test with mock session containing pending built counts.
6. **MAJOR: `_validate_save` / `_is_compatible_version`** — Write standalone tests for save folder validation and version compatibility.
7. **CRITICAL: `strategy/generation/__init__.py`** — Write re-export surface verification test.
8. **CRITICAL: `strategy/interfaces/engines/movement.py`** — Write ABC contract test with mock implementation.
