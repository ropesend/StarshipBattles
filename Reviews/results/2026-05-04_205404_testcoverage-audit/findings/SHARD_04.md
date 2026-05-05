# Shard 04 — Test Coverage Audit Findings

**Audit date:** 2026-05-04  
**Files audited:** 34 production files (~8291 LOC)  
**Agent:** OpenCode (DeepSeek v4 Pro)  

---

## Summary

| Severity | Count | Description |
|----------|-------|-------------|
| **CRITICAL** | 0 | No Tier 0 non-UI files with zero unit tests |
| **MAJOR** | 8 | Untested error paths, missing direct tests for business logic, large gaps in private methods |
| **MINOR** | 6 | Partially tested functions, indirect coverage only |
| **ADVISORY** | 7 | UI rendering code, __init__.py re-exports |

### Quick Stats
- **Fully covered** (Tier 3): 5 files — `environmental_preference.py`, `order_types.py`, `component_modifier_grid_panel.py`, `panel_factory.py`
- **Partially covered** (Tier 2): 17 files
- **Untested** (Tier 0): 7 files — 5 are ADVISORY (UI rendering or __init__.py), 2 are MAJOR gaps
- **Coverage matrix false positives:** Private methods (`_read_api_key`, `_build_body`, etc.) are tested indirectly through public APIs but the AST heuristic matcher doesn't trace call graphs. The matrix undercounts coverage for private helpers tested via `complete()` and similar facade methods.

---

## Tier 0 — Critical Coverage Gaps

### No CRITICAL findings in this shard
All Tier 0 files are either UI rendering code (ADVISORY) or __init__.py re-exports (ADVISORY). The two non-trivial Tier 0 UI files (`build_queue_selector.py`, `dispatch.py`) have business-logic state management that warrants MAJOR classification rather than CRITICAL, per the skill definition: "CRITICAL: Tier 0 non-UI file with zero unit tests."

---

## Tier 1-2 — Major Gaps

### MAJOR-01: `game/ui/screens/transfer_controller.py` (323 LOC, Tier 0)
**Status:** Zero dedicated unit tests. 42 characterization tests exist at `tests/unit/ui/screens/test_transfer_dialog_characterization.py` that exercise `TransferController` methods indirectly through the `TransferDialog`, but no isolated unit tests.

**Untested directly (10 symbols):**
- `ConfirmResult` (line 31) — dataclass, used in tests
- `TransferController.__init__` (line 63) — exercised through dialog
- `collect_sources_and_targets` (line 71) — no isolated test for:
  - No planets at hex but fleet has projected position (line 86-92)
  - Fleet not in facade list (line 97-105)
  - Colony vs unowned planet label differentiation (line 114-126)
- `discover_pod_designs` (line 130) — no test for:
  - DesignLibrary load failure fallback to `[]` (line 143)
  - Empty design library (line 142)
- `fetch_dto` (line 153) — no isolated test for:
  - `None` entry returns `None` (line 159-160)
  - Fleet vs planet resolution (line 161-163)
- `_parse_cargo_key` (line 169) — tested through dialog characterization (lines 180-186), but not for edge cases:
  - Empty string cargo key
  - `drop_pod:` prefix with no name (line 180)
- `_resolve_endpoints` (line 188) — tested through dialog, but not for:
  - Both non-fleet returns `None` (line 206)
  - Fleet-to-fleet case (line 204-205)
- `_direction` (line 208) — tested through dialog characterization (line 213-220)
- `confirm_pending` (line 222) — tested heavily through 15+ characterization tests

**Remediation:** Add unit tests for `_parse_cargo_key` edge cases (empty string, `drop_pod:` prefix without name), `_resolve_endpoints` boundary conditions, and `discover_pod_designs` failure paths. The existing characterization tests already cover the happy paths and confirm dialog interaction patterns.

---

### MAJOR-02: `game/ui/screens/build_queue_selector.py` (196 LOC, Tier 0)
**Status:** Zero unit tests. No candidate test file exists.

**Untested (7 symbols):**
- `BuildQueueSelector.__init__` (line 29) — selection state initialization, button creation
- `refresh` (line 89) — button destruction and recreation, selected/unselected display, empty queue message
- `handle_button_click` (line 135) — ctrl+click toggle vs single-click routing, non-selector button rejection
- `_on_queue_selected` (line 155) — single selection with deselection of others, callback invocation
- `_on_queue_toggled` (line 167) — toggle add/remove, empty selection prevention (line 179-180), single→multi transition (line 183-189)
- `get_selected_sources` (line 194) — sorted index iteration

**Business logic risk:**
- `_on_queue_toggled` prevents empty selection with a silent fallback to index 0 (line 179). Without tests, this safety net could be accidentally removed.
- `handle_button_click`'s ctrl routing uses a `_button_index_map` dict (line 84) that must stay in sync with `self.buttons` list. Desync would cause silent failures.

**Remediation:** Create `tests/unit/ui/screens/test_build_queue_selector.py` with tests for:
1. Single-click selection updates indices and calls callback
2. Ctrl+click toggles multi-selection
3. Empty selection prevented (cannot deselect last item)
4. Single→multi transition clears active_source
5. `get_selected_sources` returns sorted sources
6. `handle_button_click` returns False for non-selector buttons

---

### MAJOR-03: `game/ui/screens/strategy_windows/dispatch.py` (129 LOC, Tier 0)
**Status:** Zero unit tests. No candidate test file exists.

**Untested (7 symbols):**
- `UICallbackDispatcher.__init__` (line 38)
- `UICallbackDispatcher.process` (line 41) — button press callback lookup, execution, and cleanup (delete-after-call on line 54)
- `ConfirmationDialogController.__init__` (line 68)
- `ConfirmationDialogController.show` (line 71) — dialog creation, callback storage, centering
- `ConfirmationDialogController.process_event` (line 106) — event matching, callback invocation, state cleanup (lines 124-128)

**Business logic risk:**
- `UICallbackDispatcher.process` deletes the callback after execution (line 54). If an exception occurs in `callback()` before the `del` on line 54, the callback persists in the map causing a stale reference.
- `ConfirmationDialogController.process_event` sets `_pending_confirmation_dialog = None` before calling `callback()` (line 124-127). If `callback()` raises, the dialog reference is already lost.

**Remediation:** Create `tests/unit/ui/screens/test_strategy_windows_dispatch.py` with tests for:
1. Dispatcher calls and removes callback on matching button press
2. Dispatcher returns False for non-matching button
3. Confirmation controller stores and invokes callback
4. Confirmation controller clears state after callback
5. Edge cases: non-UI_BUTTON_PRESSED events, missing dialog match

---

### MAJOR-04: `game/strategy/engine/harvesting_engine.py` (479 LOC, Tier 2)
**Status:** 7/20 symbols tested per coverage matrix. Tests exist at `tests/unit/strategy/engine/test_harvesting_engine.py` (32 test functions). However, 13 private methods and 2 module-level functions are marked untested.

**Untested symbols:**
- `get_harvester_info` (line 38) — module-level function with 3 branches: dict abilities, dict→registry lookup, string→registry lookup
- `get_harvester_from_registry` (line 67) — module-level function, tested implicitly through `get_harvester_info`
- `HarvestingEngine._aggregate_empire_storage` (line 196) — tested through `test_multiple_colonies_sum`, `test_resets_max_storage_before_recalculating`
- `HarvestingEngine._collect_staging_capacity` (line 215) — staging yard aggregation, no dedicated test
- `HarvestingEngine._get_staging_info` (line 228) — staging ability extraction, no dedicated test
- `HarvestingEngine._collect_storage_from_facility` (line 252) — tested through storage tests
- `HarvestingEngine._get_storage_info` (line 274) — tested through storage tests
- `HarvestingEngine._get_storage_from_registry` (line 301) — tested through registry-based tests
- `HarvestingEngine._process_empire` (line 319) — tested through tick harness tests
- `HarvestingEngine._process_colony` (line 329) — tested through facility harvest tests
- `HarvestingEngine._process_facility` (line 342) — tested through facility harvest tests
- `HarvestingEngine._get_harvest_booster_mult` (line 388) — strategic ability scanner, NO dedicated test
- `HarvestingEngine._harvest_resource` (line 421) — tested extensively through harvest tests

**Actual gap:** `_get_harvest_booster_mult` (line 388-419) has zero dedicated test coverage. This method aggregates `ResourceHarvestBooster` abilities across planet/sector/system/empire scopes using `find_abilities_in_scope` and `aggregate_multipliers`. The 32 existing tests all pass `galaxy=None` to `process_harvesting_tick` (line 159), which causes the booster path to short-circuit at line 402-403.

**Remediation:** Add test(s) for `_get_harvest_booster_mult` with a mock galaxy providing scoped ability entries. Test that:
1. Empire-scope booster with matching resource_type contributes multiplier
2. Unmatched resource_type is ignored
3. Multiple scopes aggregate correctly
4. `galaxy=None` falls back to 1.0

---

### MAJOR-05: `game/strategy/validation/colonize_validator.py` (143 LOC, Tier 2)
**Status:** 3/7 symbols tested per coverage matrix. 43 test functions exist at `tests/unit/strategy/validation/test_colonize_validator.py`. The matrix undercounts — most static methods ARE tested.

**Actually untested:**
- `find_ship_with_drop_pod` (line 123) — NOT referenced in any test. Searches fleet ships for a carried drop pod and returns `(ship, index)` tuple. Critical for the colonize execution path (pop retrieves the pod item).
- `_validate_drop_pod_availability` (line 89) — NOT directly named in tests, but the "chain check" logic (committed >= available) is tested through `test_overcommit_succeeds_at_command_time`, `test_any_planet_exhausted_pods_fails`, `test_any_planet_two_pods_one_committed_succeeds`.

**Verified coverage (falsely marked untested by matrix):**
- `ColonizeValidator.validate` (line 32) — 20+ tests: `test_validate_no_fleet`, `test_validate_unowned_planet`, `test_validate_owned_planet_fails`, etc.
- `fleet_has_drop_pod` (line 80) — `test_fleet_has_drop_pod_returns_true`, `test_fleet_has_drop_pod_returns_false`
- `count_drop_pods` (line 112) — `test_count_drop_pods`, `test_count_drop_pods_multiple_ships`
- `count_committed_colonize_orders` (line 136) — `test_count_committed_colonize_orders`, `test_count_committed_skips_non_colonize_orders`

**Remediation:** Add test for `find_ship_with_drop_pod` — verify it returns `(ship, 0)` for a ship with a pod at index 0, `(None, -1)` for a fleet with no pods, and handles empty ships list.

---

### MAJOR-06: `game/simulation/systems/battle_engine.py` (768 LOC, Tier 2)
**Status:** 23/35 symbols tested per coverage matrix. Extensive test coverage via 9+ test files.

**Above the 500 LOC ceiling** (768 lines). This is a documented known issue — the file exceeds the 500 LOC convention. Splitting is tracked but not in scope for this audit.

**Actually untested private methods (verified against test file content):**
- `BattleEngine.enforce_boundary` (line 639) — boundary enforcement per tick. Test file exists at `tests/unit/simulation/systems/test_battle_engine_boundary.py` (5 test functions). Verified: tests exist for exit policies.
- `BattleEngine.shutdown` (line 766) — calls `self.logger.close()`. Simple one-liner, but no direct test.
- `BattleEngine.remove_ship` (line 479) — ship removal + AI controller cleanup + aura unregistration. Tested indirectly through retreat/escape flow.
- `BattleEngine.get_ship_by_name` (line 510) — simple list scan, no direct test.
- `BattleEngine._rebuild_grid` (line 543) — tested through tick tests.
- `BattleEngine._update_ai_and_ships` (line 556) — tested through tick tests.
- `BattleEngine._collect_new_attacks` (line 570) — tested through tick tests.
- `BattleEngine._process_attacks` (line 579) — tested through tick tests.
- `BattleEngine._process_projectile_attack` (line 592) — tested through tick tests.
- `BattleEngine._process_launch_attack` (line 604) — NO dedicated test for:
  - Fighter name generation with wing count (line 610-611)
  - Random spawn offset within ±10 (line 613)
  - Launch speed + velocity inheritance (line 628-629)
  - Mid-battle ship addition via `add_ship_mid_battle` (line 632)
- `BattleEngine._initialize_start_state` (line 362) — tested through `start()` / `start_teams()` which delegates to it.

**Actual gap:** `_process_launch_attack` (line 604-633). Fighter launch is a complex path that:
1. Generates a name based on wing count (which depends on ships currently in battle — non-deterministic if ships have been added/removed)
2. Randomizes spawn offset via `self.rng`
3. Applies launch speed along the source ship's facing direction
4. Calls `add_ship_mid_battle` which has its own AI factory + aura registration cascade

Without seeded RNG in a focused test, verifying the name pattern (`"{source} Wing N"`) and spawn position is impossible to reproduce.

**Remediation:** Add a test for `_process_launch_attack` with a seeded RNG to verify:
1. Spawn position is within expected range
2. Launched fighter inherits source team_id and color
3. Wing count increments correctly with existing ships
4. Velocity combines source velocity + launch speed along source angle

---

### MAJOR-07: `game/ui/screens/strategy_event_router.py` (506 LOC, Tier 2)
**Status:** 6/18 symbols tested per coverage matrix. 25 test functions at `tests/unit/ui/screens/test_strategy_event_router.py`.

**Above the 500 LOC ceiling** (506 lines). Borderline — splitting is desirable but the file is only 6 lines over.

**Untested symbols:**
- `on_ui_selection` (line 75) — simple one-liner delegating to `ui.scene.on_ui_selection(obj)`. LOW risk.
- `route_event` (line 83) — complex event routing chain (8 paths). Tests cover button presses and window closes. NOT tested:
  - Escape key closes menu panel (line 101-103)
  - Click-outside closes menu panel (line 106-110)
  - System tree event propagation (line 112-113)
  - Sector tree event propagation (line 114-116)
- `_handle_button_pressed` (line 133) — large if/elif chain (lines 139-173). Tests cover some branches.
- `_open_atmosphere_editor` (line 175) — tested through integration tests
- `_open_planet_target_editor` (line 213) — extracted from duplicate methods (PROJ-319). No dedicated test.
- `_open_gravity_editor` (line 246) — thin wrapper, tested through integration
- `_open_water_editor` (line 254) — thin wrapper, tested through integration
- `_open_radiation_shield_editor` (line 262) — thin wrapper, tested through integration
- `_open_food_allocation_editor` (line 271) — tested through integration
- `_get_race_config` (line 327) — tested through integration
- `_handle_colonize_button` (line 345) — tested through integration
- `process_custom_events` (line 426) — one-liner delegation

**Verified coverage (falsely marked untested by matrix):**
- `has_modal_open` (line 47) — tested in multiple scenarios
- `_handle_window_close` (line 391) — 15 `elif` branches for window references. Tests cover some.
- `handle_click` (line 435) — sidebar/modal blocking logic, tested
- `_is_blocking_ui_element_at` (line 458) — modal window and menu panel blocking, tested

**Remediation:** The 12 untested symbols are mostly tested indirectly through integration. Focus new tests on:
1. `route_event` — Escape key dismissal, click-outside menu close, tree event propagation
2. `_open_planet_target_editor` — verify it constructs the command class with the correct kwarg, creates the editor with the right rect size
3. `_handle_colonize_button` — no-fleet case, no-galaxy case, multi-planet prompt path

---

### MAJOR-08: `game/simulation/services/battle_service.py` (396 LOC, Tier 2)
**Status:** 16/18 symbols tested per coverage matrix. 77 test functions.

**Untested symbols:**
- `BattleService.__init__` (line 48) — trivial constructor, tested implicitly
- `BattleService._require_engine` (line 55) — simple guard returning `BattleServiceResult`. Tested indirectly through every method that calls it.

**Actual gap:** `adopt_started_engine` (line 220). Only 2 test functions reference `adopt_started_engine`. Not tested:
- Adopting an engine that was started via `start_engine_from_spec` with N teams
- `team_ships_by_id` with empty teams
- Seed propagation to service state

**Remediation:** Add a test for `adopt_started_engine` with a pre-started engine and verify `is_battle_over()` and `get_battle_state()` return correct post-adoption state.

---

## Tier 3 — MINOR Gaps

### MINOR-01: `game/services/llm/deepseek.py` (354 LOC, Tier 2)
**Status:** 3/9 symbols tested per matrix. 22 test functions + 7 test classes. ALL 6 untested symbols (`__repr__`, `__str__`, `_read_api_key`, `_build_body`, `_build_headers`, `_parse_response`) are PRIVATE METHODS tested INDIRECTLY through the `complete()` public API.

**Verified indirect coverage:**
- `__repr__` (line 76) → `test_repr_redacts_api_key`
- `__str__` (line 79) → `test_str_redacts_api_key`
- `_build_body` (line 255) → `test_request_body_shape` (validates body structure, model/temperature/max_tokens defaults)
- `_build_headers` (line 280) → `test_request_headers_include_auth_and_user_agent` (validates Authorization, Content-Type, User-Agent)
- `_parse_response` (line 287) → `test_returns_completion_result` (full parse), `test_malformed_response_raises_response_error` (missing fields), `test_non_json_response_raises_response_error` (non-JSON body)
- `_read_api_key` (line 241) → `test_missing_key_raises_config_error`, `test_empty_key_raises_config_error`

**No actual gap.** The coverage matrix's heuristic name-matching cannot trace call graphs, so it flags private methods as untested even when exhaustively tested through the sole public entry point.

---

### MINOR-02: `game/ui/panels/race_portrait_gallery.py` (153 LOC, Tier 2)
**Status:** 3/11 symbols tested per matrix. 14 test functions. 8 untested symbols are TEMPLATE METHODS from `BaseGallery` abstract interface.

**Untested template methods (all trivially simple):**
- `_get_label_text` (line 79) → returns `"Select Portrait:"`
- `_get_thumb_size` (line 82) → returns `self.PORTRAIT_THUMB_SIZE` (256)
- `_get_preview_size` (line 85) → returns `self.PREVIEW_SIZE` (256)
- `_get_object_id_prefix` (line 88) → returns `"portrait"`
- `_get_preview_panel_object_id` (line 91) → returns `"#portrait_preview"`
- `_get_current_selection` (line 94) → returns `self.race_config.portrait_id`
- `_set_selection` (line 97) → sets `self.race_config.portrait_id = asset_id`
- `_update_preview` (line 134) → tested indirectly through `test_on_asset_selected_*` tests

**Verified coverage (falsely marked untested):**
- `_discover_assets` (line 100) → tested through `test_race_portrait_gallery_has_button_list`
- `_update_preview` (line 134) → exercised through `test_on_asset_selected_clears_old_preview_image`
- `_on_asset_selected` → exercised through 5 tests

**Remediation:** Add targeted tests for the template methods:
1. `_get_current_selection` returns correct value when race_config has a portrait
2. `_get_current_selection` returns None when no portrait set
3. `_set_selection` mutates the race_config correctly

---

### MINOR-03: `game/strategy/services/planet_economy_projector.py` (259 LOC, Tier 2)
**Status:** 7/9 symbols tested per matrix. 13 test functions. 2 untested symbols are private methods.

**Untested:**
- `_project_harvest` (line 109) — calls `compute_planet_production` + habitability scaling. Tested through `project()`.
- `_project_upkeep` (line 114) — tested through `test_upkeep_sums_pop_times_allocation_times_rate`.

**Verified:** Both methods ARE tested indirectly through `project()`. The `compute_planet_production` module-level function (line 190) is tested through `test_unowned_planet` (returns `{}`), `test_uncolonized_with_harvesters`, and other harvest tests.

**No significant gap.**

---

### MINOR-04: `game/strategy/services/empire_economy_service.py` (70 LOC, Tier 2)
**Status:** 2/3 symbols tested. `EmpireEconomyService.__init__` (line 40) is the only untested symbol. It creates an `EmpireEconomyCalculator` and stores it. Tested implicitly through `get_snapshot()`.

**No actual gap.** 4 test functions cover the service facade.

---

### MINOR-05: `game/ui/panels/design_stats_panel.py` (516 LOC, Tier 2)
**Status:** 13/15 symbols tested. 2 untested private methods: `_build_section` (line 296) and `_update_requirements` (line 413). Both tested through `update_stats()` and `rebuild()`.

**Above the 500 LOC ceiling** (516 lines). Minor — only 16 lines over. Should be addressed in next refactor cycle.

**No significant gap.**

---

### MINOR-06: `game/ui/screens/strategy_camera_nav.py` (232 LOC, Tier 2)
**Status:** 8/13 symbols tested. 5 untested methods: `center_on`, `_resolve_global_hex`, `zoom_to_galaxy`, `zoom_to_system`, `cycle_selection`.

**Verified:** 7 test functions in `test_camera_navigator.py`. The untested methods are:
- `center_on` (line 51) — delegates to `_resolve_global_hex` + `center_on_hex`. Tested through `test_center_on_planet` etc.
- `_resolve_global_hex` (line 79) — planet, fleet, system resolution. Tested through `center_on` tests.
- `zoom_to_galaxy` (line 102) — NOT tested (no galaxy zoom test)
- `zoom_to_system` (line 144) — NOT tested (no system zoom test)
- `cycle_selection` (line 204) — NOT tested (no cycle test)

**Remediation:** Add tests for:
1. `zoom_to_galaxy` with empty systems list (no-op)
2. `cycle_selection` for colonies and fleets with wrap-around
3. `zoom_to_system` with no target (fallback chain)

---

## ADVISORY — UI Rendering / Re-exports

| File | LOC | Rationale |
|------|-----|-----------|
| `game/ui/components/filters/__init__.py` | 3 | Single re-export of `TriStateFilterWidget` |
| `game/ui/interfaces/__init__.py` | 25 | Re-exports 6 protocol classes |
| `game/ui/screens/battle_setup/panels/right_panel.py` | 35 | Pure pygame_gui panel construction — no business logic |
| `game/ui/screens/strategy_render/cursor.py` | 53 | Pure rendering functions (`draw_move_preview`, `draw_ghost_hex`, `draw_hover_hex`) — no state |
| `game/ui/screens/test_lab/renderer/test_list_panel.py` | 202 | Pure rendering with scrollbar — no business logic mutations |
| `game/ui/widgets/column_toggle_section.py` | 66 | Single helper function building toggle buttons — stateless, thin |
| `game/ui/widgets/panel_factory.py` | 46 | Fully covered (TIER_3_APPARENTLY_COVERED) |

**Note on `column_toggle_section.py`:** While 66 LOC with no tests, the function `build_column_toggle_section` is stateless — it creates pygame_gui elements and returns positions. Could benefit from a smoke test but given the ADVISORY classification for UI rendering helpers, this is low priority.

---

## File Coverage Verification Table

| File | LOC | Tier | Total Symbols | Tested | Key Gaps |
|------|-----|------|---------------|--------|----------|
| `game/services/llm/deepseek.py` | 354 | T2 | 9 | 3† | Private methods tested indirectly |
| `game/simulation/components/component_loader.py` | 323 | T2 | 10 | 9 | `__init__` only |
| `game/simulation/managers/retreat_manager.py` | 280 | T2 | 14 | 12 | `__init__`, `_handle_ship_escaped` |
| `game/simulation/services/battle_service.py` | 396 | T2 | 18 | 16 | `adopt_started_engine` path |
| `game/simulation/systems/battle_engine.py` | 768 | T2 | 35 | 23 | `_process_launch_attack` path |
| `game/strategy/data/environmental_preference.py` | 89 | T3 | 5 | 5 | Fully covered |
| `game/strategy/data/order_types.py` | 166 | T3 | 6 | 6 | Fully covered |
| `game/strategy/data/planet.py` | 642 | T2 | 30 | 26 | `total_pressure_atm`, `get_staging_mass`, `add_production`, `_deserialize_planet_orders` |
| `game/strategy/engine/action_execution_engine.py` | 215 | T2 | 7 | 5 | `__init__`, `_process_fleet_action_tick` |
| `game/strategy/engine/fleet_movement_engine.py` | 360 | T2 | 10 | 9 | `__init__` only |
| `game/strategy/engine/harvesting_engine.py` | 479 | T2 | 20 | 7 | `_get_harvest_booster_mult` path |
| `game/strategy/services/empire_economy_service.py` | 70 | T2 | 3 | 2 | `__init__` only |
| `game/strategy/services/planet_economy_projector.py` | 259 | T2 | 9 | 7 | `_project_harvest`, `_project_upkeep` (tested indirectly) |
| `game/strategy/validation/colonize_validator.py` | 143 | T2 | 7 | 3† | `find_ship_with_drop_pod` |
| `game/ui/components/filters/__init__.py` | 3 | T0 | 0 | 0 | ADVISORY — re-export |
| `game/ui/interfaces/__init__.py` | 25 | T0 | 0 | 0 | ADVISORY — re-exports |
| `game/ui/panels/build_queue_controller.py` | 652 | T2 | 21 | 15 | 6 private queue-routing methods |
| `game/ui/panels/component_modifier_grid_panel.py` | 151 | T3 | 10 | 10 | Fully covered |
| `game/ui/panels/design_stats_panel.py` | 516 | T2 | 15 | 13 | `_build_section`, `_update_requirements` (tested indirectly) |
| `game/ui/panels/race_portrait_gallery.py` | 153 | T2 | 11 | 3† | 8 template methods (trivial) |
| `game/ui/screens/battle_setup/panels/right_panel.py` | 35 | T0 | 1 | 0 | ADVISORY — rendering |
| `game/ui/screens/build_queue_selector.py` | 196 | T0 | 7 | 0 | **MAJOR-02** — no tests |
| `game/ui/screens/menu_scene.py` | 109 | T2 | 8 | 7 | `_create_buttons` |
| `game/ui/screens/strategy_camera_nav.py` | 232 | T2 | 13 | 8 | `zoom_to_galaxy`, `zoom_to_system`, `cycle_selection` |
| `game/ui/screens/strategy_event_router.py` | 506 | T2 | 18 | 6 | **MAJOR-07** — 12 methods untested |
| `game/ui/screens/strategy_render/cursor.py` | 53 | T0 | 3 | 0 | ADVISORY — rendering |
| `game/ui/screens/strategy_windows/dispatch.py` | 129 | T0 | 7 | 0 | **MAJOR-03** — no tests |
| `game/ui/screens/test_lab/renderer/test_list_panel.py` | 202 | T0 | 4 | 0 | ADVISORY — rendering |
| `game/ui/screens/transfer_controller.py` | 323 | T0 | 10 | 0 | **MAJOR-01** — characterization tests exist but no isolated unit tests |
| `game/ui/services/vehicle_class_service.py` | 134 | T2 | 9 | 7 | `__init__`, `_get_provider` |
| `game/ui/utils/json_diff.py` | 113 | T2 | 3 | 1 | `compute_json_diff` (tested through scrollable json panel), `_mark_all_paths` (tested recursively) |
| `game/ui/widgets/column_toggle_section.py` | 66 | T0 | 1 | 0 | ADVISORY — rendering helper |
| `game/ui/widgets/panel_factory.py` | 46 | T3 | 2 | 2 | Fully covered |
| `game/ui/widgets/scroll_state.py` | 103 | T2 | 9 | 8 | `__init__` only |

† = Coverage matrix undercount due to heuristic matcher limitations with private methods / static methods.

---

## Context Usage Estimate

| Phase | Tokens |
|-------|--------|
| Documentation read | ~1,200 |
| Coverage matrix extraction | ~800 |
| Production file reads (34 files, ~8291 LOC) | ~82,000 |
| Test file verification (scans) | ~1,500 |
| Analysis and report writing | ~4,000 |
| **Total** | **~89,500** |

---

## Prioritized Remediation Plan

1. **MAJOR-02** — `build_queue_selector.py`: Create test file (`tests/unit/ui/screens/test_build_queue_selector.py`) with 6 focused tests. Estimated 40-60 new LOC.
2. **MAJOR-03** — `dispatch.py`: Create test file (`tests/unit/ui/screens/test_strategy_windows_dispatch.py`) with 5 focused tests. Estimated 50-70 new LOC.
3. **MAJOR-04** — `harvesting_engine.py`: Add 1-2 tests for `_get_harvest_booster_mult`. Estimated 30-50 new LOC.
4. **MAJOR-06** — `battle_engine.py`: Add 1 test for `_process_launch_attack`. Estimated 20-30 new LOC.
5. **MAJOR-05** — `colonize_validator.py`: Add 1-2 tests for `find_ship_with_drop_pod`. Estimated 15-25 new LOC.
6. **MAJOR-07** — `strategy_event_router.py`: Add 3-5 tests for uncovered event routing paths. Estimated 60-80 new LOC.
7. **MINOR-06** — `strategy_camera_nav.py`: Add 3 tests for zoom and cycle methods. Estimated 30-40 new LOC.

**Total estimated new test LOC:** ~245-355 across 7 files.
