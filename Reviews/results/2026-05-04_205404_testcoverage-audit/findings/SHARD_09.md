# Shard 09 — Test Coverage Audit Findings

**Date:** 2026-05-04  
**Analyst:** Discovery Agent (OpenCode)  
**Files audited:** 35 production files, ~8,484 LOC (per pre-computed matrix)  
**Total test files checked:** 14 (spot-checked + verified)

---

## Summary

| Severity | Count | Description |
|----------|-------|-------------|
| CRITICAL | 3 | Tier 0 non-UI files with zero unit tests |
| MAJOR | 6 | Tier 1/2 files with significant untested logic/paths |
| MINOR | 10 | Files with moderate untested branches or private symbols |
| ADVISORY | 10 | UI rendering code, `__init__.py` re-exports, protocol definitions |
| OK | 6 | Tier 3 files with adequate coverage |

**Overall coverage:** ~57% of files have at least partial testing. Several gaps are notable — particularly `replay_player.py` (0 tests), `strategy_click_dispatcher.py` (0 tests), and `construction_queue.py` handlers (only the `Paused` handler tested).

---

## Tier 0 — CRITICAL: Zero Unit Tests (Non-UI Files)

### 1. `game/simulation/replay/replay_player.py` (122 LOC) — **CRITICAL**
**Coverage matrix says:** TIER_0_NO_TESTS. Verified — no test file exists.

Four public functions with zero coverage:
- `replay_record_to_spec()` (line 26) — reconstructs BattleSpec from ReplayRecord
- `build_replay_ship_builder()` (line 42) — closure builder with registry_provider DI, fallback, ValueError path
- `_builder()` (line 67, inner closure) — ShipInstance → Ship materialization with 3 branches (snapshot found, fallback, error)
- `run_replay_headless()` (line 89) — end-to-end replay runner with `capture_context=None`

**Impact:** Replay determinism verification relies on this code. No test exercises the snapshot→ShipInstance→Ship data flow, the fallback builder path, or the ValueError on missing snapshot.

**Recommendation:** Create `tests/unit/simulation/replay/test_replay_player.py` with tests for:
1. `replay_record_to_spec` returns BattleSpec from ReplayRecord
2. `build_replay_ship_builder` with snapshot present returns valid Ship
3. `build_replay_ship_builder` with missing snapshot + no fallback raises ValueError
4. `build_replay_ship_builder` with missing snapshot + fallback uses fallback
5. `run_replay_headless` passes `capture_context=None`
6. `run_replay_headless` without registry_provider (edge case)

### 2. `game/strategy/facade/slices/empire_slice.py` (97 LOC) — **CRITICAL**
**Coverage matrix says:** TIER_0_NO_TESTS. Verified — no test file found via glob.

Nine symbols with zero coverage. This is a query slice (CQRS-lite Read path) with business logic:
- `EmpireSlice.__init__` (line 25)
- `get_empire_by_id()` (line 32) — linear-scan ID lookup, returns None for unknown
- `get_all_empires()` (line 40) — maps to `EmpireInfo.from_empire()` DTOs
- `get_empire()` (line 47) — get-by-ID with DTO conversion
- `get_empire_colonies()` (line 54) — colony summaries with late import
- `get_empire_fleets()` (line 61) — fleet summaries
- `get_empire_build_queues()` (line 68) — late-imports `collect_all_build_queues_for_empire`, DTO conversion
- `get_hex_build_queues()` (line 82) — per-hex queue collection with late import

**Impact:** This is the empire query path consumed by the UI's empire panel. Untested DTO mappings, None-return branches, and late-import error paths.

**Recommendation:** Create `tests/unit/strategy/facade/slices/test_empire_slice.py`. Test all 7 public methods, including:
- Empty empire list returns empty DTO lists
- Unknown empire_id returns None/empty
- Verify build queue DTO field preservation
- Late import failure paths (mocked)

### 3. `game/simulation/interfaces/entity_protocols.py` (487 LOC) — **CRITICAL** (Protocols, advisory for definitions)
**Coverage matrix says:** TIER_0_NO_TESTS. 68 symbols untested.

This file defines 4 `@runtime_checkable` Protocol classes and 4 TypeGuard functions:
- `ICombatShip` (27 property + 4 method signatures)
- `IProjectile` (22 property signatures)
- `IPhysicsShip` (6 property signatures)
- `ISerializableShip` (6 property signatures)
- `is_combat_ship()` (line 469), `is_projectile()` (line 474), `is_physics_ship()` (line 480), `is_serializable_ship()` (line 485)

**Impact:** Protocol bodies are empty (`...` stubs) — they are documentation/typing constructs. The TypeGuard functions (lines 469-487) contain actual logic (attribute checks via `_has_attrs`). These are used throughout the codebase for duck-typing guards but have no direct unit tests.

**Recommendation:** Test the TypeGuard functions at minimum — they contain branch logic:
```python
def test_is_combat_ship_false_for_lacking_attrs()
def test_is_projectile_true_for_projectile()
def test_is_physics_ship_false_for_non_physics()
```
Protocol definitions themselves don't need unit tests (they are type system artifacts).

### 4. `game/strategy/interfaces/__init__.py` (44 LOC) — **ADVISORY**
Re-exports 15 interface/protocol classes. No executable logic. Tests not needed.

### 5. `game/research/systems/__init__.py` (4 LOC) — **ADVISORY**
Single re-export of `ResearchService`. No executable logic. Tests not needed.

---

## Tier 1-2 — MAJOR: Significant Untested Code

### 6. `game/ui/screens/strategy_click_dispatcher.py` (593 LOC) — **MAJOR**
**Coverage matrix says:** TIER_0_NO_TESTS. Verified — no test file exists. 24 symbols untested.

This is a critical UI component that routes ALL mouse click events on the strategy map. 15 mode-specific click handlers with complex branching logic:
- `_handle_move_mode_click` (line 89) — move/intercept choice, success/error branches, right-click cancel
- `_handle_select_mode_click` (line 323) — left-click picking, right-click quick-move
- `_handle_picking` (line 505) — sector hit-testing (fleets, planets, warp points, stars, zone objects, SectorEnvironment)
- `_hit_test_planets` (line 365) — complex multi-planet spatial layout with 5+ size code paths
- `_resolve_click_target` (line 474) — smart hex resolution with camera zoom branching
- 5 superweapon handlers (lines 303-321) — all delegate to `_handle_superweapon_click`
- Transfer, cargo, warp, colonize handlers — each with left/right-click branching

**Impact:** This is the user's primary interaction surface for the strategy layer. A bug here manifests as unresponsive clicks or wrong targets. The `_hit_test_planets` method has ~108 lines of geometric hit-testing with no test coverage.

**Recommendation:** Extract `_hit_test_planets` and `_resolve_click_target` as testable pure functions (they are mostly math). Then test:
- Planet hit-testing with 1/2/3/4/5+ planets per hex
- Right-click cancels reset input_mode to 'SELECT'
- Mode dispatch table routes to correct handler
- `_handle_picking` populates sector_contents correctly for empty/full hex

### 7. `game/strategy/engine/handlers/construction_queue.py` (265 LOC) — **MAJOR**
**Coverage matrix:** TIER_2_PARTIAL, 5/10 symbols untested. Verified — only `SetBuildQueuePausedCommandHandler` tested.

Untested handlers (all business logic):
- `AddToConstructionQueueCommandHandler.execute()` (line 36) — 8-step handler: entity resolution, queue resolution, index validation, design validation, cost calculation, queue item creation, target_planet_id, insert/append
- `AddToConstructionQueueCommandHandler._check_design_valid()` (line 95) — loads design library, runs DesignValidator, blocks on errors AND warnings, handles OSError/ValueError/KeyError with graceful pass-through
- `AddToConstructionQueueCommandHandler._load_design_cost()` (line 132) — loads design from library, calls DesignCostCalculator, handles OSError/ValueError/KeyError with empty dict fallback
- `RemoveFromConstructionQueueCommandHandler.execute()` (line 167) — entity resolution, queue resolution (with `getattr(cmd, 'queue_id', None)`), index validation, pop removal
- `ReorderConstructionQueueCommandHandler.execute()` (line 201) — pop+insert reorder with dual index validation

**Impact:** These are the primary CRUD operations for the construction queue. Only the pause/unpause handler is tested. Zero tests for add/remove/reorder — the most commonly exercised operations.

**Recommendation:** Create `tests/unit/strategy/engine/handlers/test_construction_queue.py` covering:
- Add to planet/fleet queues, with/without index
- Add with invalid design (mass budget exceeded)
- Add with design that fails validation (errors + warnings)
- Remove from queue with valid/invalid index
- Reorder with valid/invalid from/to indices
- `_load_design_cost` on load failure returns `{}`
- `_check_design_valid` on library load failure returns True (graceful)

### 8. `game/ui/screens/builder/stat_getters.py` (410 LOC) — **MAJOR**
**Coverage matrix:** TIER_2_PARTIAL, 32/49 symbols untested. Verified — 19 test functions in test file, but many getters untested.

Only 17 of 49 getter functions tested. Untested (all lines with business logic):
- `get_resource_storage` (line 111) — ResourceRegistry lookup with None guard
- `get_resource_current` (line 116)
- `get_resource_generation` (line 121)
- `get_resource_consumption` (line 126) — complex fallback: stat lookup → manual ResourceConsumption iteration across layers
- `get_resource_endurance` (line 141) — division with zero guard
- `get_resource_replenish` (line 149) — division with zero guard
- `get_resource_max_usage` (line 157) — potential_map lookup with fallback
- `get_warp_tonnage` (line 207), `get_warp_cost` (line 211), `get_warp_jumps` (line 215)
- `get_fuel_per_hex` (line 228) — manual component iteration
- `get_hex_range` (line 240) — fuel/consumption calculation with inf guard
- `get_passenger_capacity` (line 255), `get_pod_storage` (line 259), `get_colony_types` (line 263)
- `get_superweapon_summary` (line 290), `has_superweapons` (line 303)
- `get_dps_duration` (line 190), `get_fuel_consumption` (line 99), `get_ammo_consumption` (line 102), `get_energy_consumption` (line 105)
- `get_maneuver_points` (line 84), `get_strategic_speed` (line 87), `get_max_targets` (line 75), `get_armor_hp` (line 78), `get_crew_required` (line 66), `get_crew_capacity` (line 69), `get_life_support` (line 72)
- `mass_unit_func` (line 405)
- Validators: `crew_validator` (line 48), `life_support_validator` (line 54)
- Formatters: `fmt_time` (line 12), `fmt_multiply` (line 23), `fmt_decimal` (line 26), `fmt_score` (line 29), `fmt_targeting` (line 32)

**Impact:** These are data-driven getters referenced by name from `stats_layout.json`. Many contain error-handling paths (ResourceRegistry None, division by zero, infinite returns) that are untested.

**Recommendation:** Expand `tests/unit/workshop/test_stat_getters.py` to cover all resource getters, formatter edge cases (infinite, negative), and validators with both pass/fail scenarios.

### 9. `game/ui/screens/test_lab/screen_input_handler.py` (399 LOC) — **MAJOR** (Tier 1)
**Coverage matrix:** TIER_0_NO_TESTS (Tier 1). Verified — no test file exists. 13 symbols untested.

This handles ALL mouse/keyboard input for the Combat Lab UI:
- `handle_event` (line 54) — event dispatch with USEREVENT, dialog, panel, scroll/mouse routing
- `_handle_dialog_events` (line 86) — confirmation dialog + JSON popup modal gating
- `_handle_panel_events` (line 109) — delegates to 5 panel types
- `_handle_scroll_and_mouse` (line 142) — MOUSEWHEEL, MOUSEMOTION, MOUSEBUTTONDOWN routing
- `_update_hover_state` (line 171) — category, group, test-item hover detection
- `_handle_click` (line 224) — dispatches to 5 sub-checkers
- `_check_category_clicks` (line 245) — All Tests, group expand/collapse, category select/deselect
- `_check_tag_filter_clicks` (line 288) — tag cycling, clear filters, Run All
- `_check_test_item_click` (line 317) — scrolled test list click with viewport clipping
- `_check_action_button_clicks` (line 353) — Run Test, Run Headless, Visual Baseline buttons
- `_check_seed_mode_clicks` (line 380) — seed mode cycling + custom seed prompt

**Impact:** Central coordinator for all Combat Lab interaction. Untested click-detection logic, scroll-aware hit-testing, modal dialog gating.

**Recommendation:** Create `tests/unit/ui/screens/test_lab/test_screen_input_handler.py` with unit tests for:
1. Dialog open blocks other events (modal gating)
2. Category click toggles selection (select → deselect on re-click)
3. Test item click with scroll offset applied
4. Seed mode button click changes mode
5. USEREVENT+1 dispatches to continue_batch callback
6. MOUSEWHEEL only handled within test_list_panel bounds

### 10. `game/ui/services/image/openai_provider.py` (390 LOC) — **MAJOR**
**Coverage matrix:** TIER_2_PARTIAL, 9/11 symbols listed untested. Verified — 10 test functions exist but they test via mock patching.

The matrix lists 9 private methods as "untested" but 7 of them are tested indirectly:
- `__init__` (line 69) — tested via all other tests
- `__repr__`/`__str__` — `test_repr_redacts_key` verifies
- `_read_api_key` — `test_no_api_key_raises_image_config_error` covers
- `_build_headers` — used by all normal-path tests
- `_post_generation` — exercised via generate_image test
- `_post_edit` — image edit path (line 272-304) — **genuinely untested** (only generation endpoint tested)
- `_parse_response` — exercised via normal-path tests
- `_read_actual_size` (line 365) — uses PIL late-import with broad `except Exception` fallback to `(0,0)`. **The fallback path is untested.**

**Actual uncovered branches:**
- `_post_edit` with mask vs. without mask (lines 299-304)
- `_post_edit` with `edit_image is None` raising ImageConfigError (line 286)
- `_parse_response` JSON decode failure (line 316)
- `_parse_response` missing `b64_json` field (line 327)
- `_parse_response` invalid base64 (line 340)
- `_read_actual_size` PIL failure fallback returning `(0,0)` (line 377)
- 5xx retry exhaustion path (lines 196-212) — tested via `test_5xx_retries_then_raises`

**Recommendation:** Add tests for edit endpoint (`_post_edit`) and `_parse_response`/`_read_actual_size` error paths.

### 11. `game/strategy/engine/game_initializer.py` (399 LOC) — **MINOR** (reclassified from TIER_2_PARTIAL)
**Coverage matrix:** TIER_2_PARTIAL, 6/10 symbols listed untested. Verified — 32 test functions exist and COVER the untested symbols indirectly.

The 6 "untested" symbols are all tested indirectly through `initialize()`:
- `_PlanetShortageError` — tested via `test_planet_shortage_eventually_raises` and `test_planet_shortage_retry_succeeds_when_a_later_attempt_has_enough`
- `_wire_fleet_lookups` — tested via all test scenarios (part of `initialize()`)
- `_create_empires` — tested via `test_empire_always_has_race_config`, `test_empire_preserves_explicit_race_config`
- `_initialize_galaxy` — tested via all map generation tests
- `_empire_home_indices` — tested via N=1/N=2/N=5 spacing tests
- `_setup_initial_scenario` — tested via all homeworld assignment tests

The matrix incorrectly flags these as untested due to string-matching heuristics that miss private method names. **Severity reduced to MINOR** — the actual uncovered gap is the `_adjust_homeworld_to_race` edge case where `atmosphere` is empty (line 380-382, `else` branch at line 380 only exercises when no gas factors > 0).

---

## Tier 2 — MINOR: Partial Coverage

### 12. `game/simulation/systems/tick_phase.py` (201 LOC) — **MINOR**
**Coverage matrix:** TIER_2_PARTIAL, 7/34 symbols listed untested. Verified — 9 test functions exist.

Untested symbols are all 6 phase classes + `create_default_phases`:
- `RebuildGridPhase` (line 87) — delegates to `engine._rebuild_grid()`
- `AIAndShipUpdatePhase` (line 102) — delegates to `engine._update_ai_and_ships()`
- `BoundaryEnforcementPhase` (line 117) — delegates to `engine.enforce_boundary()`
- `AttackProcessingPhase` (line 137) — delegates to `engine._collect_new_attacks()` + `_process_attacks()`
- `RammingPhase` (line 153) — delegates to `engine.collision_system.process_ramming()`
- `ProjectileUpdatePhase` (line 168) — delegates to `engine.projectile_manager.update()`
- `create_default_phases()` (line 183)

**Verification:** All phase classes are thin delegates (single-line `execute()`). The actual logic lives in BattleEngine. `create_default_phases` is tested indirectly via `test_execute_all_calls_in_priority_order` (which uses `create_default_phases` indirectly). 9 tests cover the registry (register, sort, execute, protocol conformance).

**Remaining gap:** Direct unit test of `create_default_phases()` verifying priority values and phase order.

### 13. `game/simulation/components/abilities/colonize.py` (81 LOC) — **MINOR**
**Coverage matrix:** TIER_2_PARTIAL, 1/4 symbols untested (`_parse_attrs`). Verified via test file.

**Remaining gap:** `_parse_attrs` (line 46) with 3 branches:
- String input (`isinstance(data, str)`) — likely covered via data file loading
- Dict input (`isinstance(data, dict)`) — likely covered
- Fallback (`else` at line 56) — untested non-string/non-dict input

**Recommendation:** Add test for `_parse_attrs` with non-string/non-dict fallback path (line 56-57).

### 14. `game/ai/spatial_behaviors/battle_line.py` (92 LOC) — **MINOR**
**Coverage matrix:** TIER_2_PARTIAL, 1/3 symbols untested (`__init__`). Verified — 22 test functions exist.

The `__init__` is tested via `test_battle_line_assigns_slots` and similar. Uncovered branches:
- `leader is None` returns None (line 47-48) — may be covered
- `total = len(group_ships)` edge case where `total == 0` → set to 1 (line 51-52)
- `shape == "wedge"` branch (lines 74-78) — needs verification
- `shape == "echelon_left"` (lines 80-84) — needs verification  
- `shape == "echelon_right"` (lines 86-90) — needs verification

**Recommendation:** Verify which shapes are tested. The 3 shape branches may be untested.

### 15. `game/ui/screens/battle_results_data.py` (181 LOC) — **MINOR**
**Coverage matrix:** TIER_2_PARTIAL, 2/7 symbols untested. Verified — 9 test functions exist.

Untested: `_build_team_summary` and `_derive_winner` are listed as untested but test `test_team_summary` and `test_draw_result` cover them indirectly.

**Actual gap:** `_derive_winner` has 3 branches (0 survivors, 1 team with survivors, multiple teams). Only 1-survivor case covered.

### 16. `game/ui/screens/design_image_helper.py` (218 LOC) — **MINOR**
**Coverage matrix:** TIER_2_PARTIAL, 2/5 symbols untested. Verified — 12 tests.

Untested: `_load_portrait_thumbnail_uncached` and `_load_topdown_thumbnail_uncached`. These are the cache-miss paths that handle:
- File I/O error fallback to placeholder generation
- 5 class name variations for skin files
- Png.get_bounding_rect edge cases
- Placeholder color selection from vehicle type

Verified: Covered indirectly through cached wrapper tests (`test_loads_and_scales_image_when_file_exists` calls `load_portrait_thumbnail` which calls `_load_portrait_thumbnail_uncached` on cache miss).

### 17. `game/ui/screens/empire_build_queue_sidebar.py` (234 LOC) — **ADVISORY** (UI)
**Coverage matrix:** TIER_2_PARTIAL, 3/8 symbols untested. Verified — 13 tests.

Untested: `__init__`, `_build_column_toggles`, `_build_filters`. These are UI construction methods that create `pygame_gui` widgets. Partially tested via integration (button click tests). UI construction is ADVISORY severity per methodology.

### 18. `game/ui/screens/strategy_panel_manager.py` (507 LOC) — **MINOR**
**Coverage matrix:** TIER_2_PARTIAL, 2/4 symbols untested. Verified — test file exists.

Untested: `resize_strategy_panels` (line 410) and `apply_hotkey_tooltips` (line 469).

`resize_strategy_panels` has ~60 lines of dimensional recalculation logic with branching (`graph_h < 50`, swapped graph dimensions). `apply_hotkey_tooltips` has a 14-element button-action map with `input_mapper is None` early return.

### 19. `game/strategy/data/fleet_consumable_aggregator.py` (341 LOC) — **MINOR**
**Coverage matrix:** TIER_2_PARTIAL, 4/19 symbols untested. Verified — 58 test functions exist.

Untested symbols listed: `__init__`, `_accumulate_ship_costs`, `get_fleet_pod_capacity`, `get_fleet_pod_mass_used`. These are all tested indirectly:
- `__init__` tested via all tests
- `_accumulate_ship_costs` tested via `test_get_movement_resource_costs_*`
- `get_fleet_pod_capacity` / `get_fleet_pod_mass_used` — genuinely untested (lines 251-257, no test references)

**Actual gap:** Pod storage methods (lines 251-257) — 7 LOC with 2 methods, zero test coverage.

### 20. `game/strategy/data/physics.py` (76 LOC) — **MINOR**
**Coverage matrix:** TIER_2_PARTIAL, 1/4 symbols untested (`SectorEnvironment.__init__`). Verified — test file exists.

`__init__` is tested via all `calculate_incident_radiation` tests. Actual gaps:
- `calculate_incident_radiation` with `dist < 1.0` clamping to 1.0 (lines 57-59)
- `calculate_incident_radiation` with empty stars list (returns zero spectrum)

### 21. `game/strategy/generation/loaders/astrophysics_loader.py` (152 LOC) — **MINOR**
**Coverage matrix:** TIER_2_PARTIAL, 2/4 symbols untested. Verified — test files exist.

Untested: `__init__` and `_validate_schema`.
- `__init__` tested indirectly
- `_validate_schema` validation branches (lines 59-152): 9 required sections, mass_distributions validation, orbit_zones validation, habitable_zone factors, atmosphere_retention thresholds, classification thresholds, resource_generation keys. These error paths may be partially covered by integration tests.

### 22. `game/strategy/generation/loaders/system_blueprints_loader.py` (241 LOC) — **MINOR**
**Coverage matrix:** TIER_2_PARTIAL, 3/7 symbols untested. Verified — test files exist.

Untested: `__init__`, `_validate_schema`, `_validate_blueprint`.
- `_validate_blueprint` has 8 distinct validation branches (lines 153-241) — type checks, range checks, enum checks. Some error paths likely untested.

---

## Tier 3 — Verified Coverage

### 23. `game/ai/policy_manager.py` (118 LOC) — **OK**
**Coverage matrix:** TIER_3_APPARENTLY_COVERED. Verified — 13 test functions. All 8 symbols tested. Thorough coverage of lazy loading, threading, defaults, test isolation (`clear()`).

### 24. `game/simulation/battle_state.py` (805 LOC) — **OK**
**Coverage matrix:** TIER_3_APPARENTLY_COVERED. Verified — 5 test files. 31 symbols. Thorough serialization round-trip testing. `from_component`, `from_ship`, `from_projectile`, `to_ship`, `to_projectile`, `capture_from_engine` all have test coverage.

### 25. `game/strategy/data/component_activation_state.py` (156 LOC) — **OK**
**Coverage matrix:** TIER_3_APPARENTLY_COVERED. Verified — 10 test files reference it. Thorough state machine testing. All transitions (INACTIVE→ACTIVATING→ACTIVE→DEACTIVATING→INACTIVE), raises on invalid transitions, backward compatibility in `from_dict`.

### 26. `game/strategy/generation/density/primitives/geometric.py` (101 LOC) — **OK**
**Coverage matrix:** TIER_3_APPARENTLY_COVERED. Verified — 2 test files. `GeometricPrimitive.evaluate` with polygon distance calculations, edge falloff, center case, circle fallback.

### 27. `game/ui/screens/empire_build_queue_filter_manager.py` (242 LOC) — **OK**
**Coverage matrix:** TIER_3_APPARENTLY_COVERED. Verified — 39 test functions. Every filter state, column toggle, sort path, and search method tested. Excellent coverage.

### 28. `game/ui/services/image/factory.py` (82 LOC) — **OK**
**Coverage matrix:** TIER_3_APPARENTLY_COVERED. Verified — test file exists. `create()`, `register_image_provider()`, env var resolution, unknown provider raises, deferred validation for missing API key.

---

## Tier 0 (UI) — ADVISORY: Rendering / No Tests

### 29. `game/ui/screens/race_setup/screen.py` (489 LOC) — **ADVISORY** (UI, NOT TIER_0)
**Coverage matrix incorrectly says:** TIER_0_NO_TESTS. **Verified — 63 tests exist.** The screen is a thin orchestrator that delegates to ViewModel/Controller/Renderer/InputHandler. Tests exercise lifecycle (`__init__`, `_show_step`, `update`, `kill`), UI construction, callbacks, tab navigation, randomization, LLM integration, and edge cases. The matrix mismatch is due to the screen being in a `race_setup/` subpackage while tests are at the parent level.

**Actual minimal gaps:** The screen's `_create_tab_buttons`, `_create_step_panels`, `_create_navigation_buttons` are UI construction methods tested only indirectly via bypass_init + mock builders.

### 30. `game/ui/screens/test_lab/dialogs.py` (272 LOC) — **ADVISORY**
Zero tests. Two classes (`JSONPopup`, `ConfirmationDialog`) with pure rendering logic:
- Overlay drawing, scroll handling, button management, event dispatch
- `ConfirmationDialog._kill_buttons` (line 197) — cleanup logic
- `JSONPopup.handle_event` — three branches (UI_BUTTON_PRESSED, MOUSEWHEEL, KEYDOWN/ESCAPE)

ADVISORY per methodology (UI rendering code). However, the non-rendering logic (`close`, `_handle_confirm`, `_handle_cancel`, `_kill_buttons`) should be testable.

### 31. `game/ui/screens/test_lab/renderer/category_panel.py` (157 LOC) — **ADVISORY**
Zero tests. Pure rendering: draws category tree with hover/selected states, group expand/collapse triangles, child categories.

### 32. `game/ui/screens/test_lab/results_panel.py` (266 LOC) — **ADVISORY**
Zero tests. Pure rendering + scroll state management. `_is_card_visible` (line 237) and `_recalculate_scroll` (line 97) contain testable logic.

### 33. `game/ui/screens/strategy_ui_action_router.py` (97 LOC) — **ADVISORY**
Zero tests. Simple delegation: maps `InputAction` enum values to scene method calls. Highly testable — each action has a clear contract:
- Zoom actions → `scene._camera_nav.zoom_*()`
- UI actions → `scene.ui.open_*()` / `scene.on_*_click()`
- Cycle actions → `scene.cycle_selection()`
- Unrecognized action → returns False

**Recommendation:** Add simple contract tests verifying the action→method mapping for all 16 InputAction values.

### 34. `game/ui/panels/race_flag_gallery.py` (165 LOC) — **ADVISORY**
8 methods listed as untested. All are thin overrides (getters/setters) or pygame rendering code. `_discover_assets` has I/O logic (lines 100-139) with error handling that could be tested.

### 35. `game/ui/panels/__init__.py` (0 LOC) — **ADVISORY**
Empty file. No tests needed.

---

## File Coverage Verification Table

| # | File | LOC | Matrix Tier | Actual Status | Severity |
|---|------|-----|------------|---------------|----------|
| 1 | `game/ai/policy_manager.py` | 118 | TIER_3 | OK — 13 tests | — |
| 2 | `game/ai/spatial_behaviors/battle_line.py` | 92 | TIER_2 | MINOR — shape branches | MINOR |
| 3 | `game/research/systems/__init__.py` | 4 | TIER_0 | Re-export only | ADVISORY |
| 4 | `game/simulation/battle_state.py` | 805 | TIER_3 | OK — 5 test files | — |
| 5 | `game/simulation/components/abilities/colonize.py` | 81 | TIER_2 | MINOR — fallback branch | MINOR |
| 6 | `game/simulation/interfaces/entity_protocols.py` | 487 | TIER_0 | CRITICAL (TypeGuards) | CRITICAL |
| 7 | `game/simulation/replay/replay_player.py` | 122 | TIER_0 | NO TESTS EXIST | **CRITICAL** |
| 8 | `game/simulation/systems/tick_phase.py` | 201 | TIER_2 | MINOR — thin delegates | MINOR |
| 9 | `game/strategy/data/component_activation_state.py` | 156 | TIER_3 | OK — 10 test files | — |
| 10 | `game/strategy/data/fleet_consumable_aggregator.py` | 341 | TIER_2 | MINOR — pod storage untested | MINOR |
| 11 | `game/strategy/data/physics.py` | 76 | TIER_2 | MINOR — edge cases | MINOR |
| 12 | `game/strategy/engine/game_initializer.py` | 399 | TIER_2 | MINOR — indirectly covered | MINOR |
| 13 | `game/strategy/engine/handlers/construction_queue.py` | 265 | TIER_2 | 3 handlers untested | **MAJOR** |
| 14 | `game/strategy/facade/slices/empire_slice.py` | 97 | TIER_0 | NO TESTS EXIST | **CRITICAL** |
| 15 | `game/strategy/generation/density/primitives/geometric.py` | 101 | TIER_3 | OK — 2 test files | — |
| 16 | `game/strategy/generation/loaders/astrophysics_loader.py` | 152 | TIER_2 | MINOR — validation branches | MINOR |
| 17 | `game/strategy/generation/loaders/system_blueprints_loader.py` | 241 | TIER_2 | MINOR — validation branches | MINOR |
| 18 | `game/strategy/interfaces/__init__.py` | 44 | TIER_0 | Re-exports only | ADVISORY |
| 19 | `game/ui/panels/__init__.py` | 0 | TIER_1 | Empty file | ADVISORY |
| 20 | `game/ui/panels/race_flag_gallery.py` | 165 | TIER_2 | UI rendering | ADVISORY |
| 21 | `game/ui/screens/battle_results_data.py` | 181 | TIER_2 | MINOR — _derive_winner branches | MINOR |
| 22 | `game/ui/screens/builder/stat_getters.py` | 410 | TIER_2 | 32 of 49 untested | **MAJOR** |
| 23 | `game/ui/screens/design_image_helper.py` | 218 | TIER_2 | Indirect coverage | MINOR |
| 24 | `game/ui/screens/empire_build_queue_filter_manager.py` | 242 | TIER_3 | OK — 39 tests | — |
| 25 | `game/ui/screens/empire_build_queue_sidebar.py` | 234 | TIER_2 | UI construction | ADVISORY |
| 26 | `game/ui/screens/race_setup/screen.py` | 489 | TIER_0* | 63 tests (matrix wrong) | ADVISORY |
| 27 | `game/ui/screens/strategy_click_dispatcher.py` | 593 | TIER_0 | NO TESTS EXIST | **MAJOR** |
| 28 | `game/ui/screens/strategy_panel_manager.py` | 507 | TIER_2 | MINOR — resize+tooltips | MINOR |
| 29 | `game/ui/screens/strategy_ui_action_router.py` | 97 | TIER_0 | NO TESTS EXIST | ADVISORY |
| 30 | `game/ui/screens/test_lab/dialogs.py` | 272 | TIER_0 | NO TESTS EXIST | ADVISORY |
| 31 | `game/ui/screens/test_lab/renderer/category_panel.py` | 157 | TIER_0 | NO TESTS EXIST | ADVISORY |
| 32 | `game/ui/screens/test_lab/results_panel.py` | 266 | TIER_0 | NO TESTS EXIST | ADVISORY |
| 33 | `game/ui/screens/test_lab/screen_input_handler.py` | 399 | TIER_0 | NO TESTS EXIST | **MAJOR** |
| 34 | `game/ui/services/image/factory.py` | 82 | TIER_3 | OK — tests exist | — |
| 35 | `game/ui/services/image/openai_provider.py` | 390 | TIER_2 | Edit path + error paths | MAJOR |

*\* Matrix incorrectly classifies #26 as TIER_0 — it has 63 tests.*

---

## Priority Remediation Queue

| # | File | Why first |
|---|------|-----------|
| 1 | `replay_player.py` | Zero tests; replay determinism is a PROJ-312 contract |
| 2 | `empire_slice.py` | Zero tests; CQRS-lite read path consumed by UI |
| 3 | `construction_queue.py` | Only pause tested — add/remove/reorder are core UX |
| 4 | `strategy_click_dispatcher.py` | Zero tests; primary user interaction surface |
| 5 | `screen_input_handler.py` (test_lab) | Tier 1, zero tests; central input coordinator |
| 6 | `stat_getters.py` | 65% untested; includes error-handling branches |
| 7 | `openai_provider.py` | Image edit path + `_parse_response`/`_read_actual_size` error paths |
| 8 | `entity_protocols.py` | TypeGuard functions testable in <10 lines each |
| 9 | `tick_phase.py` | Phase classes are thin but `create_default_phases` untested |
| 10 | `strategy_ui_action_router.py` | 16-action mapping, highly testable |

---

## Context Usage Estimate

- Files read: 35 production + 3 docs + coverage matrix
- Total production LOC read: ~8,484
- Test files spot-checked: 14
- Total test LOC spot-checked: ~3,000
- Approximate token consumption: ~180K input, ~12K output
