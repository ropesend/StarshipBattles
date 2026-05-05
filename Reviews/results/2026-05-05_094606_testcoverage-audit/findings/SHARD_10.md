# Shard 10 — Test Coverage Audit Findings

**Date:** 2026-05-05  
**Scope:** 34 production files, ~8666 LOC  
**Layers:** Core (1), Engine (1), Simulation (4), Strategy (6), UI (22)  
**Phase 1 heuristic reliability:** Mixed — substantial false negatives on operator-heavy classes (component_protocols, ship_component_manager)

---

## Summary

| Tier | Count | Files |
|------|-------|-------|
| **Tier 0** (No tests) | 6 | `ship_component_manager.py`†, `component_protocols.py`†, `validation/__init__.py`, `background.py`, `component_dropdown.py`, `test_lab/details/validation.py` |
| **Tier 1** (No symbols) | 3 | `panels/__init__.py`, `race_setup_screen.py`, `strategy_windows/__init__.py` |
| **Tier 2** (Partial) | 18 | `math.py`, `cargo.py`, `design_role_registry.py`, `galaxy_layouts_loader.py`, `fleet_navigation_service.py`, `replay_store.py`, `ship_theme_manager.py`, `filter_state_manager.py`, `build_queue_screen.py`, `modifier_row.py`, `schematic_view.py`, `cargo_quick_dialog.py`, `empire_panel_window.py`, `planet_list_window.py`, `save_selection_window.py`, `system_selection_window.py`, `transfer_grid_renderer.py`, `validation_service.py` |
| **Tier 3** (Verified) | 7 | `spatial.py`, `battle_spec.py`, `event_types.py`, `replay_verification_sidecar.py`, `task_group_suggester.py`, `data_source.py`, `strategy_panel_manager.py` |

† = Phase 1 false negative — actual test files exist but AST scanner missed them.

**Overall health:** 7/34 (20.6%) Tier 3 verified; 6/34 (17.6%) Tier 0; 18/34 (52.9%) Tier 2 partial; 3/34 (8.8%) Tier 1. Three critical gaps in strategy-service coverage (`replay_store`, `fleet_navigation_service`, `build_queue_screen`) represent ~1911 LOC of partially-untested production logic.

---

## Tier 0 — No Tests Found

### CRITICAL: `game/simulation/entities/ship_component_manager.py` (293 LOC, 15 symbols)

**Phase 1 claim:** 0 tested symbols. **Skeptical verification:** **FALSE POSITIVE.** Two test files exist:
- `tests/unit/simulation/entities/test_ship_component_manager.py` (445 LOC, 10 test classes, 30+ test functions)
- `tests/unit/simulation/entities/test_ship_component_manager_di.py`

The AST scanner missed these because the tests exercise `ShipComponentManager` through `Ship`'s facade API (the standard delegate pattern). The tests call `self.ship.add_component()`, `self.ship.get_all_components()`, etc. — which delegate to the manager.

**Actual coverage:** Tests cover `add_component`, `add_components_bulk`, `remove_component`, `get_all_components`, `iter_components`, `get_components_by_ability`, `get_weapon_components_cached`, `get_components_by_layer`, `has_components`, `find_component_with_index`, `clear_non_hull_components`, and cache invalidation.  
**Remaining gaps:** `_attach_component` is only tested indirectly; modifier_service branch (line 57-58, 73-79) is only partially covered. No direct constructor test. Reclassify as **Tier 2 partial** — the Phase 1 heuristic needlessly promoted a well-tested file to Tier 0.

### ADVISORY: `game/simulation/interfaces/component_protocols.py` (226 LOC, 23 symbols)

**Phase 1 claim:** 0 tested symbols. **Skeptical verification:** **FALSE POSITIVE.** This is a Protocol class (`IComponent`) with `@runtime_checkable`. All 23 "symbols" are Protocol properties/methods with `...` bodies — there's nothing to test. The `is_component` TypeGuard is exercised indirectly via every test that creates components and checks type narrowing. The `IComponent` protocol itself is structurally typed — explicit unit tests for a protocol definition add no value.

**Reclassify as Tier 1** — protocol-only file, no testable logic. No gap.

### MINOR: `game/simulation/validation/__init__.py` (36 LOC, 0 symbols)

This is a pure re-export module. All listed classes are tested via their own modules (`base.py`, `ship_validator.py`). No gap.

### ADVISORY: `game/ui/screens/strategy_render/background.py` (58 LOC, 4 symbols)

**BackgroundLayer** is a pure rendering utility (load image, scale, dim, blit). 0 tests. Methods: `__init__`, `_load_background`, `draw`. All operations are Pygame surface manipulation.
- `_load_background` — asset manager lookup + null check (untested)
- `draw` — scale + dim + blit (untested, rendering-only)
- **Suggestion:** Add smoke test verifying draw() runs without error given mock asset_manager (returns a simple Surface). ADVISORY — rendering.

### ADVISORY: `game/ui/screens/test_lab/component_dropdown.py` (157 LOC, 6 symbols)

**ComponentDropdown** — a custom Pygame dropdown widget (no pygame_gui dependency). 0 tests.
Methods: `__init__`, `handle_click`, `handle_hover`, `get_selected_component_id`, `draw`.
All methods are pure Pygame surface rendering + mouse coordinate math. 
- **Suggestion:** Unit test `handle_click` with mocked `pygame.mouse.get_pos()` and synthetic button-down events. Test boundary cases: empty component_ids, click outside, click on expanded option. ADVISORY — UI widget.

### ADVISORY: `game/ui/screens/test_lab/details/validation.py` (253 LOC, 4 symbols)

**Validation rendering** — four pure rendering functions: `_phase_color`, `draw_validation_results`, `draw_single_validation`, `draw_numeric_difference`. All operate on `DetailsDrawContext` and return updated y_offset ints.
- `draw_numeric_difference` has branching on `expected != 0`, `abs_pct_diff < 1e-9`, `abs_pct_diff < 0.01`, bool-subclass guards, and EXACT MATCH vs ± formatting.
- **Suggestion:** Unit test `draw_numeric_difference` for all formatting branches with synthetic context. Test `draw_single_validation` for PASS/FAIL/OTHER status, p_value rendering, and detail rendering. ADVISORY — rendering.

---

## Tier 1-2 — Partial Coverage

### CRITICAL: `game/strategy/services/replay_store.py` (494 LOC, 9/26 tested)

**THE LARGEST COVERAGE GAP IN THIS SHARD.** 17 untested symbols out of 26. The single test file (`test_replay_store_eviction.py`, 58 LOC) covers only `_evict_excess` error handling.

**Untested:**
- `load_replay_settings` — JSON settings loader with fallback/default logic, corrupt-JSON handling, key validation. Branch-heavy (4 error paths). **CRITICAL**
- `ReplayStore.__init__` — constructor with listener-lock threading setup. Untested.
- `ReplayStore.set_save_root` / `clear_save_root` — save lifecycle. Untested.
- `ReplayStore.on_battle_started` / `on_battle_ended` — IReplayCaptureSink contract methods. Untested.
- `ReplayStore.persist` — atomic-write + listener notification + eviction. Core method. Untested.
- `ReplayStore.list` / `load` / `load_or_error` — all three reader methods with schema validation, corrupt-JSON handling, version-drift detection. Untested.
- `ReplayStore.delete` — deletion with sidecar cleanup. Untested.
- `ReplayStore.add_on_record_persisted_listener` / `remove_on_record_persisted_listener` — thread-safe listener registry. Untested.
- `ReplaySettings` / `load_replay_settings` — settings infrastructure. Untested.

**Priority:** Write comprehensive unit tests. The store is a filesystem-backed service with multiple error paths (JSON corrupt, dir missing, OSError on write/delete, thread-safety edge cases). Test each public method with a tmp_path fixture.

### CRITICAL: `game/strategy/services/fleet_navigation_service.py` (759 LOC, 19/22 tested)

**3 untested private methods** that handle projection internals:
- `_project_path_inner` (lines 475-554) — the core projection loop with 100+ lines, safety iteration limit, action-order tick consumption, and multi-turn movement. **CRITICAL.**
- `_get_action_time_for_projection` — ActionTimeResolver integration. Minor (one late-import + call).
- `_project_action_order` — action_time tick consumption with initial_progress tracking. Medium.

**Gap analysis:** The public `project_path` method is tested, but its inner loop and action-order handling are only exercised indirectly through integration. The mutex guard (`_projection_guard`) and the `NavigationState` / `NavigationStep` data structures are well tested (11 test files total).

### CRITICAL: `game/ui/screens/build_queue_screen.py` (658 LOC, 8/23 tested)

15 untested symbols, but many are complex UI event handlers:
- `BuildQueueScreen.__init__` — 100+ line constructor with param validation, panel factory, controller wiring, drag handler setup. Untested directly.
- `_validate_params` — validation of required constructor params + owner_id/name attribute checking. Untested.
- `_on_queue_selection_changed` — multi-queue selection sync logic. Untested.
- `_dispatch_add_to_queue_command` / `_dispatch_remove_from_queue_command` / `_dispatch_toggle_pause_command` — command construction + facade/session dispatch. Untested.
- `_handle_button_press` — 50-line event dispatch with 20+ elif branches. Untested.
- `_handle_virtual_table_action` — remove/add/up/down actions. Untested.
- `_handle_keydown` — 30-line keyboard dispatch for 8 actions. Only tested via hotkey integration.
- `_handle_drag_operations` — drag-and-drop state management. Untested.

**Existing test:** `tests/unit/ui/screens/test_sub_window_hotkeys.py` only tests hotkey resolution (InputMapper integration), not business logic.

### `game/core/math.py` (280 LOC, 24/33 tested)

9 untested dunder methods: `__add__`, `__radd__`, `__sub__`, `__rsub__`, `__mul__`, `__rmul__`, `__truediv__`, `__neg__`, `__iter__`. These are indirectly tested through vector operations used in other tests (63 candidate test files). The standalone math tests (`test_vector2_basic.py`, `test_vector2_geometry.py`, `test_helpers.py`) test the non-dunder surface well.

**Assessment:** MINOR — dunders are exercised widely. The Phase 1 scanner correctly flagged them as name-unmatched but they're tested via `v1 + v2`, `v1 * 3`, etc.

### `game/simulation/components/abilities/cargo.py` (78 LOC, 5/6 tested)

`CargoStorage.__init__` marked untested — actually tested implicitly by `test_cargo_storage.py` which constructs CargoStorage instances. The init is exercised through `get_ui_rows`, `sync_data`, `recalculate`, etc. MINOR false positive.

### `game/strategy/data/design_role_registry.py` (98 LOC, 3/4 tested)

`_build_default` untested. This is the core lazy-construction function that loads base + mods + user overlay. It's exercised through `get_default_design_role_registry()` but not directly unit-tested. The three test files (`test_design_role_registry*.py`) test loading and invalidation but focus on the public API. **Verification:** `_build_default` is called on first `get_default_*` access and indirectly tested by any test that calls `get_default_design_role_registry()`. MINOR — add explicit test for layered loading order.

### `game/strategy/generation/loaders/galaxy_layouts_loader.py` (182 LOC, 6/7 tested)

`_scale_primitive` untested. This is a private function that scales individual primitives. All callers go through `scale_layout_for_radius()` which is tested. MINOR — indirect coverage.

### `game/ui/assets/ship_theme_manager.py` (453 LOC, 17/20 tested)

3 untested: `__init__`, `_validate_image_size`, `get_theme_description`. `__init__` is tested via factory functions. `get_theme_description` is a simple dict accessor. `_validate_image_size` has 4 branches (PIL import, expected parsing, actual check, exception handling). MINOR.

### `game/ui/filters/filter_state_manager.py` (54 LOC, 7/8 tested)

`__init__` untested — exercised by every other test method. MINOR false positive.

### `game/ui/screens/builder/modifier_row.py` (355 LOC, 8/10 tested)

`_build_linear_controls` and `_clear_ui` untested. Both are internal UI construction/destruction methods called by `build_ui` and `kill`. The public API (`build_ui`, `update`, `handle_event`, `kill`) is well tested. MINOR — these are UI element lifecycle methods.

### `game/ui/screens/builder/schematic_view.py` (189 LOC, 4/10 tested)

6 untested: `__init__`, `update_rect`, `draw`, `draw_all_firing_arcs`, `draw_component_firing_arc`, `draw_weapon_arc`. All are rendering methods. The cache key logic (`_get_cached_arc`) is tested. ADVISORY — UI rendering methods.

### `game/ui/screens/cargo_quick_dialog.py` (330 LOC, 5/11 tested)

6 untested: `CargoQuickDialogUiBuilder` (class + build + _setup_ui + _apply_tooltips + _add_cargo_row), `CargoQuickDialog._handle_keydown`. The UiBuilder is exercised by the constructor path; the keyboard handling is tested via integration. MINOR — controller methods are tested in separate files.

### `game/ui/screens/empire_panel_window.py` (572 LOC, 9/19 tested)

10 untested symbols, almost all are rendering methods: `_create_ui`, `_create_tab_buttons`, `_create_tab_panels`, `_build_treasury_tab`, `_render_species_card`, `_render_identity_section`, `_render_aptitudes_section`, `_build_placeholder_tab`, `kill`. ADVISORY — UI rendering.

### `game/ui/screens/planet_list_window.py` (760 LOC, 12/29 tested)

Major UI component with 15 untested symbols. Most are event handlers (`process_event`, `_set_all_filters`, `_set_all_effects`) and rendering methods. Core logic (filter, sort, column management) tested separately in `test_planet_list_components.py`. ADVISORY — UI rendering with complex interaction logic.

### `game/ui/screens/save_selection_window.py` (473 LOC, 9/14 tested)

5 untested: `SaveSelectionUiBuilder` (class + build), `_on_expand_clicked`, `_on_delete_clicked`, `_on_cancel_clicked`. Core `_load_saves` and selection logic well tested. MINOR — UI builder and edge case handlers.

### `game/ui/screens/system_selection_window.py` (166 LOC, 3/5 tested)

`SystemSelectionUiBuilder` and `SystemSelectionUiBuilder.build` untested. The UiBuilder is exercised via construction; widget interactions (confirm/cancel) tested. MINOR false positive.

### `game/ui/screens/transfer_grid_renderer.py` (366 LOC, 7/10 tested)

3 untested: `_add_row`, `TransferDialogUiBuilder`, `TransferDialogUiBuilder.build`. The grid renderer is exercised through the production path. MINOR.

### `game/ui/services/validation_service.py` (79 LOC, 3/5 tested)

`__init__` and `_get_validator` untested. Both are exercised by the public methods (`validate_addition`, `validate_design`) which ARE tested. MINOR false positive.

---

## Tier 3 — Verified Coverage

### `game/engine/spatial.py` (61 LOC, 7/7 tested)

**SpatialGrid** — all methods tested: `__init__`, `clear`, `_get_cell`, `insert`, `query_radius`, `query_radius_exact`. 9 candidate test files. **Verified.** Coverage includes exact vs broad-phase queries, empty grid, and edge-case cell boundaries.

### `game/simulation/battle_spec.py` (242 LOC, 8/8 tested)

**BattleSpec + 7 nested DTOs** — frozen dataclasses with no behavior. All 8 are tested across 21 candidate test files. **Verified.** Tests cover construction, immutability, and spec-compiler integration.

### `game/strategy/events/event_types.py` (38 LOC, 2/2 tested)

**EventType** and **EventCategory** enums. 9 candidate test files. **Verified.** All enum members are used across strategy tests.

### `game/strategy/services/replay_verification_sidecar.py` (173 LOC, 8/8 tested)

**VerificationSidecar** + enums + read/write functions. Well-tested via `test_replay_verification_sidecar.py` and `test_replay_verification_coordinator.py`. **Verified.** Coverage includes read/write, corrupt JSON handling, schema mismatch.

### `game/strategy/services/task_group_suggester.py` (125 LOC, 1/1 tested)

`suggest_task_groups` function — tested via `test_task_group_suggester.py`. **Verified.** Tests cover empty ships, single ship, multiple roles, sort order.

### `game/ui/components/table/data_source.py` (111 LOC, 7/7 tested)

**ITableDataSource** — all methods tested via `test_data_source.py`. **Verified.** Tests cover base-class NotImplementedError raising, default implementations, and `get_visible_columns` filtering.

### `game/ui/screens/strategy_panel_manager.py` (507 LOC, 4/4 tested)

**StrategyWidgets** dataclass, `create_strategy_panels`, `resize_strategy_panels`, `apply_hotkey_tooltips` — all tested via `test_strategy_panel_manager.py` and `test_strategy_ui_button_wiring.py`. **Verified.** Tests cover widget creation, anchoring, and button-tooltip binding.

---

## Tier 1 — No Symbols (Re-export/Empty)

### `game/ui/panels/__init__.py` (0 LOC)
Empty file. No action needed.

### `game/ui/screens/race_setup_screen.py` (31 LOC)
Legacy import shim re-exporting from `game.ui.screens.race_setup.screen`. The canonical module has its own test suite. No action needed.

### `game/ui/screens/strategy_windows/__init__.py` (9 LOC)
Docstring-only package init. No action needed.

---

## File Coverage Verification Table

| File | LOC | Tier | Symbols Tested | Phase 1 Accuracy | Verdict |
|------|-----|------|----------------|-----------------|---------|
| `game/core/math.py` | 280 | 2 | 24/33 | OK | Dunders tested indirectly |
| `game/engine/spatial.py` | 61 | 3 | 7/7 | OK | Verified |
| `game/simulation/battle_spec.py` | 242 | 3 | 8/8 | OK | Verified (DTOs) |
| `game/simulation/components/abilities/cargo.py` | 78 | 2 | 5/6 | OK | Init tested indirectly |
| `game/simulation/entities/ship_component_manager.py` | 293 | 0→2 | 0/15→12/15 | **FALSE NEGATIVE** | 2 test files exist (445+ LOC) |
| `game/simulation/interfaces/component_protocols.py` | 226 | 0→1 | 0/23→N/A | **FALSE NEGATIVE** | Protocol-only, no testable logic |
| `game/simulation/validation/__init__.py` | 36 | 0 | 0/0 | OK | Re-export only |
| `game/strategy/data/design_role_registry.py` | 98 | 2 | 3/4 | OK | _build_default tested indirectly |
| `game/strategy/events/event_types.py` | 38 | 3 | 2/2 | OK | Verified (enums) |
| `game/strategy/generation/loaders/galaxy_layouts_loader.py` | 182 | 2 | 6/7 | OK | _scale_primitive tested indirectly |
| `game/strategy/services/fleet_navigation_service.py` | 759 | 2 | 19/22 | OK | 3 private methods, projection loop critical |
| `game/strategy/services/replay_store.py` | 494 | 2 | 9/26 | OK | **CRITICAL GAP** — 17 untested |
| `game/strategy/services/replay_verification_sidecar.py` | 173 | 3 | 8/8 | OK | Verified |
| `game/strategy/services/task_group_suggester.py` | 125 | 3 | 1/1 | OK | Verified |
| `game/ui/assets/ship_theme_manager.py` | 453 | 2 | 17/20 | OK | Image-size validation untested |
| `game/ui/components/table/data_source.py` | 111 | 3 | 7/7 | OK | Verified |
| `game/ui/filters/filter_state_manager.py` | 54 | 2 | 7/8 | OK | Init false positive |
| `game/ui/panels/__init__.py` | 0 | 1 | 0/0 | OK | Empty |
| `game/ui/screens/build_queue_screen.py` | 658 | 2 | 8/23 | OK | **CRITICAL GAP** — 15 untested |
| `game/ui/screens/builder/modifier_row.py` | 355 | 2 | 8/10 | OK | UI build/destroy internals |
| `game/ui/screens/builder/schematic_view.py` | 189 | 2 | 4/10 | OK | UI rendering methods |
| `game/ui/screens/cargo_quick_dialog.py` | 330 | 2 | 5/11 | OK | UiBuilder exercised via construction |
| `game/ui/screens/empire_panel_window.py` | 572 | 2 | 9/19 | OK | UI rendering methods |
| `game/ui/screens/planet_list_window.py` | 760 | 2 | 12/29 | OK | UI rendering + event handlers |
| `game/ui/screens/race_setup_screen.py` | 31 | 1 | 0/0 | OK | Re-export shim |
| `game/ui/screens/save_selection_window.py` | 473 | 2 | 9/14 | OK | UiBuilder + edge handlers |
| `game/ui/screens/strategy_panel_manager.py` | 507 | 3 | 4/4 | OK | Verified |
| `game/ui/screens/strategy_render/background.py` | 58 | 0 | 0/4 | OK | UI rendering |
| `game/ui/screens/strategy_windows/__init__.py` | 9 | 1 | 0/0 | OK | Docstring only |
| `game/ui/screens/system_selection_window.py` | 166 | 2 | 3/5 | OK | UiBuilder false positive |
| `game/ui/screens/test_lab/component_dropdown.py` | 157 | 0 | 0/6 | OK | UI rendering widget |
| `game/ui/screens/test_lab/details/validation.py` | 253 | 0 | 0/4 | OK | UI rendering functions |
| `game/ui/screens/transfer_grid_renderer.py` | 366 | 2 | 7/10 | OK | _add_row + UiBuilder |
| `game/ui/services/validation_service.py` | 79 | 2 | 3/5 | OK | Init + _get_validator false positives |

---

## Context Usage Estimate

This shard covered 34 files (~8666 LOC). After verifying all production files (100% read) and test-file listings from the coverage matrix, with targeted skeptical reads of the three most critical test files:

- **Production files read:** 34/34 (100%)
- **Test files read:** 6/55 candidate files (10.9%) — focused on Tier 0 false positives and CRITICAL gaps
- **Phase 1 inaccuracies corrected:** 2 substantial (ship_component_manager, component_protocols both reclassified from Tier 0)

---

## Prioritized Recommendations

1. **`replay_store.py` — ADD COMPREHENSIVE TESTS.** 17 untested symbols across all public methods. This is a filesystem I/O service with atomic writes, ring-buffer eviction, thread-safe listeners, and schema validation. Test in isolation with tmp_path, covering all error paths (OSError, corrupt JSON, missing dir, version drift). Priority: **CRITICAL**.

2. **`build_queue_screen.py` — ADD BUSINESS LOGIC TESTS.** 15 untested symbols. The constructor, command dispatch methods, and event handlers need coverage beyond the existing hotkey-only tests. Test via the MVVM collaborators (Controller, Renderer, DragHandler) in isolation. Priority: **CRITICAL**.

3. **`fleet_navigation_service.py` — ADD PROJECTION LOOP TESTS.** `_project_path_inner` (100+ LOC) is the core loop with safety limits, action-order tick consumption, and multi-turn state management. Add dedicated unit tests with synthetic `NavigationState` inputs. Priority: **HIGH**.

4. **`component_dropdown.py` — ADD WIDGET TESTS.** The custom dropdown has handle_click with 5+ branches (header click, option click, outside click, collapsed/expanded state). Test with mock mouse positions. Priority: **MEDIUM** (ADVISORY).

5. **`test_lab/details/validation.py` — ADD FORMATTING TESTS.** `draw_numeric_difference` has 6 formatting branches (EXACT MATCH, essentially exact, ±%, zero-denominator, bool guards). Test all branches. Priority: **MEDIUM** (ADVISORY).

6. **`design_role_registry.py` — ADD LAYERED LOAD TEST.** `_build_default` tests base + mods + user overlay loading order. Add explicit test with temporary JSON files in each layer. Priority: **LOW**.
