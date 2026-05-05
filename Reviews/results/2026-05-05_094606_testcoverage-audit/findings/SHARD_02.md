# Test Coverage Audit — Shard 02 Findings

**Shard:** 02 | **Files:** 39 | **LOC Estimate:** ~8,649 | **Date:** 2026-05-05

---

## Summary

| Tier | Count | Description |
|------|-------|-------------|
| **CRITICAL** | 4 | Non-UI Tier 0 files with zero test coverage |
| **MAJOR** | 4 | Untested error paths, missing branch coverage, large partially-tested files |
| **MINOR** | 8 | Partially tested, missing minor branches or dunder methods |
| **ADVISORY** | 23 | UI rendering/event code, `__init__.py` re-export shims, protocol definitions, Tier 3 verified |

**Key findings:**
- 4 CRITICAL files in non-UI layers with zero unit tests: `facility.py` (FacilityAbilitySource adapter — untested), `transfer_controller.py` (business logic — untested), `workshop_viewmodel_ship_ops.py` (ViewModel CRUD — untested), `workshop_data_reloader.py` (data orchestration — untested)
- Phase 1 AST scanner false positives corrected: `colonize.py` `_parse_attrs` IS tested indirectly; `context.py` `__init__` IS tested; all `__repr__` methods on end conditions are logging-only
- 12 UI files classified ADVISORY — rendering/event code with pygame_gui dependencies
- 5 Tier 3 files verified as genuinely well-covered

---

## Tier 0 — CRITICAL: Non-UI Files With Zero Test Coverage

### 1. `game/strategy/services/ability_sources/facility.py` — CRITICAL

**LOC:** 87 | **Symbols:** 9 (all untested)

**What it does:** `FacilityAbilitySource` is a frozen dataclass implementing `IAbilitySource` (PROJ-300). It wraps a planetary facility and provides ability aggregation, hex/system scoping, and activation state querying.

**Untested logic:**
- Lines 46-62: `get_abilities()` — walks `facility.design_data` via `iter_keyed_components`, calls `extract_abilities_from_component`, handles the `is_operational` flag. No test covers: operational=True path, operational=False path (returns `{}`), or compound `ability_data` that is a list.
- Lines 64-69: `affects_hex()` — always returns `True` (sector scope); test would verify the contracts that downstream collectors depend on.
- Lines 71-72: `affects_system()` — always returns `True`.
- Lines 74-87: `get_activation_state()` — traverses components looking for the first match to `ability_name`, handles case where facility has no `get_activation_state` callable. No test covers: found match path, no match path, missing callable path.

**Risk:** Integration points with `SystemEffectsCollector` and the sector-effects pipeline. A regression here would silently drop facility-granted abilities (e.g., shield modifiers) from combat modifier stacks.

**Suggested tests:**
1. Facility with operational components → `get_abilities()` returns aggregated dict
2. Facility with `is_operational=False` → `get_abilities()` returns `{}`
3. Facility with no `get_activation_state` → returns `None`
4. Facility with activation state → returns correct state for matching ability

---

### 2. `game/ui/screens/transfer_controller.py` — CRITICAL

**LOC:** 323 | **Symbols:** 10 (all untested)

**What it does:** Controller for cargo transfer dialog (PROJ-328 Phase C). Contains business logic for facade queries, cargo key parsing, endpoint resolution, and `IssueTransferCommand` emission. Unlike typical UI code, this module has NO pygame_gui dependencies — it is pure business logic that happens to live under `game/ui/`.

**Untested logic:**
- Lines 71-128: `collect_sources_and_targets()` — fetches fleets/planets at hex, handles projected fleet position fallback. No test for: empty hex, projected position equals hex, colony vs uncolonized planet labeling.
- Lines 130-147: `discover_pod_designs()` — queries `DesignLibrary`, filters by `vehicle_type="Drop Pod"`, falls back on `Exception`. No test for: library with pod designs, empty library, I/O error fallback.
- Lines 169-186: `_parse_cargo_key()` — static method parsing `"drop_pod:<name>"`, `"passengers_<race_id>"`, `"passengers"`, and generic strings. No test for any format.
- Lines 188-206: `_resolve_endpoints()` — computes `(fleet_id, planet_id, target_fleet_id, ...)` from source/target dicts. No test for: fleet-to-planet, planet-to-fleet, fleet-to-fleet, planet-to-planet (returns None), colony endpoints.
- Lines 208-220: `_direction()` — determines "load"/"unload" based on source/target types and sign. No test for any combination.
- Lines 222-320: `confirm_pending()` — core command emission logic. Constructs `IssueTransferCommand` for each non-zero pending entry, handles `MAX_LOAD`/`MAX_DROP`, validates source/target/endpoints, reports `aborted_for_correction`. No test for: successful multi-cargo transfer, zero-pending abort, missing source/target abort, non-fleet endpoint abort, rejected command path.

**Risk:** Transfer is a core gameplay mechanic. Bugs in cargo key parsing or direction logic would cause incorrect resource movement, data corruption in save files, or silent command rejection.

**Suggested tests:** 15+ test cases covering the full state machine in `confirm_pending()` and standalone unit tests for `_parse_cargo_key`, `_resolve_endpoints`, `_direction`.

---

### 3. `game/ui/screens/workshop_viewmodel_ship_ops.py` — CRITICAL

**LOC:** 330 | **Symbols:** 18 (all untested)

**What it does:** `WorkshopShipOps` is a ViewModel helper (PROJ-309 sub-phase 3.8) providing service-backed ship CRUD operations. All 18 methods wrap `VehicleDesignService` calls with ViewModel state updates. Pure Python — no Pygame.

**Untested logic (key methods):**
- Lines 57-86: `create_default_ship()` — creates ship via service, raises `ValidationException` on failure. No test for: success path, failure path with error message.
- Lines 88-99: `add_component()` — adds via service, returns bool. No test for: success, failure.
- Lines 101-122: `add_component_bulk()` — bulk add with partial-failure handling (`count - 1` on warnings). No test for: all succeed, partial fail, all fail.
- Lines 177-205: `change_ship_class()` — class change with optional component migration. No test for: migrate=True success, migrate=True failure, migrate=False.
- Lines 232-246: `clear_design()` — clears non-hull components, resets policies. No test for: ship with components, empty ship.
- Lines 252-330: Setter methods (`set_ship_name`, `set_ship_theme`, `set_ship_movement_policy`, `set_ship_targeting_policy`, `set_ship_design_role`) — each has early-return on unchanged value. No test for: change, no-change, missing ship.

**Risk:** Workshop is the primary ship design interface. Bugs in bulk-add or class-change would corrupt ship designs. These operations are testable without UI (all dependencies are `VehicleDesignService` + ViewModel — injectable).

**Suggested tests:** Establish a test fixture pattern similar to existing workshop tests (see `tests/unit/workshop/`). Test each CRUD method independently with stubbed `VehicleDesignService`.

---

### 4. `game/ui/screens/workshop_data_reloader.py` — CRITICAL

**LOC:** 197 | **Symbols:** 11 (all untested)

**What it does:** Orchestrates data directory reload (PROJ-61). Coordinates between `WorkshopDataLoader`, ViewModel, and UI panels. Contains logic for standard vs test data loading paths, error handling, and UI refresh sequencing.

**Untested logic:**
- Lines 116-122: `load_standard_data()` — loads from `Paths.DATA_DIR`, sets ship folder. No test for: success path.
- Lines 124-130: `load_test_data()` — loads from `tests/data/`, sets ship folder. Different path resolution. No test for: success path.
- Lines 132-160: `reload_data()` — main reload pipeline: load → validate → refresh UI → show success. Error path returns early. No test for: success, load failure, missing directory.
- Lines 162-197: `_refresh_ui_after_data_reload()` — orchestrates 10+ UI refresh operations in sequence. No test for: any path.

**Risk:** Data reload is invoked from the Workshop UI. A bug would leave the builder in an inconsistent state after data switching.

**Suggested tests:** Mock `WorkshopDataLoader` and callbacks. Test: successful reload triggers UI refresh; failed reload shows error and does NOT refresh UI.

---

## Tier 0 — ADVISORY: UI Files With Zero Test Coverage

### 5. `game/ui/screens/galaxy_test/galaxy_mode.py` — ADVISORY

**LOC:** 427 | **Symbols:** 8

UI helper for galaxy layout testing mode. All 8 methods are pygame_gui construction, rendering (`draw`, `_draw_warp_lanes`), camera manipulation, and galaxy generation. Code uses `random.seed()` directly (line 239) as a known intentional bypass for the test tool's RNG — ADVISORY.

### 6. `game/ui/screens/race_setup/panel_factory.py` — ADVISORY

**LOC:** 177 | **Symbols:** 7

Factory functions that wire panel components for the race setup screen. Pure glue code — each function instantiates a panel class and stores it on the screen. ADVISORY.

### 7. `game/ui/screens/strategy_windows/event_log_window_ctrl.py` — ADVISORY

**LOC:** 159 | **Symbols:** 9

`EventLogRegistrar` — lifecycle manager for the Event Log window. Contains ReplayResolver construction (lines 85-118) which has a broad except with Intentional comment. Navigation and close callbacks. ADVISORY rendering/event code.

### 8. `game/ui/screens/strategy_windows/list_windows.py` — ADVISORY

**LOC:** 107 | **Symbols:** 11

`PlanetListRegistrar` and `StarListRegistrar` — lifecycle managers for list windows. Camera navigation helper. Pure window open/close/navigate callbacks. ADVISORY.

### 9. `game/ui/screens/test_lab/renderer/orchestrator.py` — ADVISORY

**LOC:** 211 | **Symbols:** 4

`TestLabRenderer` orchestrator class. Renders the Combat Lab UI by delegating to panel sub-renderers. The `__init__` creates all sub-panels; `draw()` calls delegates. All logic is rendering (pygame.Surface, colors, fonts). ADVISORY.

### 10. `game/core/protocols/registry.py` — ADVISORY

**LOC:** 38 | **Symbols:** 5

`IRegistryProvider` protocol definition with 4 abstract methods. A protocol — no implementation to test. Extensively used across 75+ test files indirectly. ADVISORY (protocol definitions are contracts, not code paths).

### 11. `game/engine/__init__.py` — ADVISORY

**LOC:** 36 | **Symbols:** 0

Package re-export shim: `PhysicsBody`, `CollisionSystem`, `SpatialGrid`. ADVISORY.

### 12. `game/strategy/engine/handlers/__init__.py` — ADVISORY

**LOC:** 72 | **Symbols:** 0

Package re-export shim. Imports and re-exports 20+ handler classes from sub-modules. ADVISORY.

### 13. `game/ui/research/__init__.py` — ADVISORY

**LOC:** 8 | **Symbols:** 0

Package re-export shim: `ResearchTreeScene`. ADVISORY.

---

## Tier 1 — Imported But No Symbols Tested

### 14. `game/simulation/entities/stat_contributors/__init__.py` — MINOR

**LOC:** 33 | **Symbols:** 0

Re-exports 6 module references (`command`, `defense`, `launch`, `movement`, `registry`, `weapons`). Imported by 5 test files via other modules. MINOR (re-export shim).

### 15. `game/strategy/data/__init__.py` — MINOR

**LOC:** 0 | **Symbols:** 0

Empty file. Imported by 5 test files transitively. MINOR.

---

## Tier 2 — Partial Coverage: Detailed Findings

### 16. `game/context.py` — Phase 1 False Positive

**LOC:** 191 | **Untested per matrix:** `ApplicationContext.__init__`

**Verdict: FALSE POSITIVE.** `__init__` is called by both `create_production()` (line 142) and `create_test()` (line 191), which are tested by `tests/unit/core/test_application_context.py`. All 10 service slots are covered. Dunder init should not be listed as untested. **Downgrade to Tier 3.**

### 17. `game/simulation/components/abilities/colonize.py` — Phase 1 False Positive

**LOC:** 81 | **Untested per matrix:** `ColonizePlanet._parse_attrs`

**Verdict: FALSE POSITIVE.** `_parse_attrs` is tested indirectly through `__init__` in `test_colonize_harvester.py`. The test file covers:
- String shorthand (`"ICE_DWARF"`) — line 41
- Dict format with `planet_type` — line 47
- Dict format missing `planet_type` — line 53
- Non-string/non-dict data — line 63
- `action_time` with string shorthand (defaults to 1) — line 149
- `action_time` from dict — line 162
- `action_time` with non-dict data — line 169

All three branches in `_parse_attrs` (`isinstance(data, str)`, `isinstance(data, dict)`, `else`) are exercised. **Downgrade to Tier 3.**

### 18. `game/simulation/components/abilities/stat_keys.py` — MINOR

**LOC:** 190 | **Untested per matrix:** `AbilityStatBinding.__post_init__`

**Verified:** `__post_init__` validates the `operation` field (lines 132-143). The validation check is:
- `operation in {'multiply', 'add', 'set'}` → passes silently
- Otherwise → raises `ValidationException`

The existing test `test_stat_key.py` does NOT test an invalid operation raising. **CONFIRMED: MAJOR** — the error path `operation not in valid_operations` is untested. However, this is a data validation guard that fires at construction time from JSON; the operation always comes from a known set. **Downgrade to MINOR** given the defensive nature and low blast radius.

### 19. `game/simulation/components/component.py` — MINOR

**LOC:** 406 | **Untested per matrix:** `Component.mark_hp_cache_dirty`

**Verified:** `mark_hp_cache_dirty()` (lines 226-232) sets `_hp_ratio_dirty = True`. It is a public API wrapper around a private flag, consumed by `health_manager.hp_ratio`. The method is called during HP resets via `reset_hp()` → `health_manager.reset_hp()`. **CONFIRMED: the direct method is untested but the behavior is covered through indirect paths.** MINOR.

### 20. `game/simulation/components/component_loader.py` — MINOR

**LOC:** 323 | **Untested per matrix:** `ComponentCacheManager.__init__`

**Verified:** `__init__` (lines 60-64) sets 4 fields to `None`. Tested via `test_component_loader.py` through `get_default_cache_manager()` / `reset_component_caches()`. **CONFIRMED: Minor — dunder init not directly tested but behavior covered.**

### 21. `game/simulation/components/modifiers.py` — Tier 3 Verified

**LOC:** 149 | **All symbols tested**

Four functions: `_apply_effect_to_dict`, `apply_modifier_effects`, `get_default_stat_multipliers`, `calculate_stat_multipliers`. Tested by `test_modifiers.py` and `test_invalid_operation_handling.py`. **Tier 3 — CONFIRMED.**

### 22. `game/simulation/systems/battle_end_conditions.py` — MINOR

**LOC:** 496 | **Untested per matrix:** 10 `__repr__` methods

**Verified:** All 10 `__repr__` methods are untested. These are debugging/logging helpers that return `f"ClassName(params)"`. The matrix correctly identifies them. **CONFIRMED: MINOR** — `__repr__` methods are not user-facing and have no behavioral impact. Their untested status is cosmetic.

### 23. `game/strategy/combat/spec_compiler.py` — MAJOR

**LOC:** 693 | **Untested per matrix:** 7 private methods

**Verified:** The spec compiler has comprehensive tests at `test_spec_compiler.py` (32KB), `test_spec_compiler_formation.py`, and `test_post_battle_hook.py`. The 7 "untested" symbols are all private helpers that ARE tested — just through the public `build_strategy_battle_spec()` entry point:

- `_build_strategy_post_battle_hook` (line 234) — indirectly tested through `build_strategy_battle_spec()` with `empires` kwarg
- `_hook` (line 278, inner closure) — tested via the post-battle hook applied to outcomes
- `_team_spec_for_fleet_group` (line 293) — tested through the main compiler
- `_pick_formation_for_fleet` (line 357) — tested through the main compiler
- `_ship_spec_from_instance` (line 372) — tested through the main compiler
- `_build_modifier_stack` (line 439) — tested through the main compiler
- `_emit_entries_team_scoped` (line 489) — tested through `_entries_from_fleet_combat_modifiers`

**Verdict: FALSE POSITIVE from Phase 1 AST scanner.** These are private decomposition methods tested through their public caller. **Downgrade to Tier 3 for coverage purposes, but note**: direct unit tests for `_parse_cargo_key`-style edge cases in `_ship_spec_from_instance` (e.g., missing `design_data`, empty components) would improve robustness. MINOR finding.

### 24. `game/strategy/engine/game_config.py` — MINOR

**LOC:** 261 | **Untested per matrix:** `_get_default_asset_path`, `_get_default_players`

**Verified:** Both are module-level helpers. `_get_default_asset_path` returns `Paths.SHIP_THEMES_DIR`. `_get_default_players` returns a 2-player list. Both are used as `field(default_factory=...)` in `GameConfig`. Tested indirectly via `test_game_config.py`. **MINOR.**

### 25. `game/strategy/engine/superweapon_command_handlers.py` — Tier 3 Verified

**LOC:** 353 | **All 22 symbols tested**

Extensively tested by 3 test files (29KB, `test_superweapon_command_handlers.py`, `test_superweapon_edge_cases.py`, `test_superweapon_handler_validation.py`). **Tier 3 — CONFIRMED.**

### 26. `game/strategy/facade/strategy_session_facade.py` — MINOR

**LOC:** 502 | **Untested per matrix:** 5 symbols (cache properties)

**Verified:** The "untested" symbols (`_all_stars_cache_turn` ×2, `_fleets_by_hex_turn` ×2, `_resolve_economy_config`) are:
- The `_*_turn` properties are simple property shims (lines 120-142) forwarding to `self._state`. They are accessed by tests via `test_strategy_session_facade.py`.
- `_resolve_economy_config` (line 454) has `# pragma: no cover — internal helper` and is a legacy alias.

**MINOR — effectively covered.** The property shims serve backward compatibility for legacy tests.

### 27. `game/strategy/services/replay_verification_coordinator.py` — MAJOR

**LOC:** 441 | **Untested per matrix:** `_json_safe`, `_difference_to_dict`, `__init__`, `_worker_loop`, `_write_sidecar`

**Verified:**
- `__init__` (line 159) — stores injected deps. Tested indirectly via `start()`/`shutdown()`.
- `_json_safe` (line 104) — recursive JSON coercion helper. **MAJOR: NOT tested with non-JSON types.** The helper handles Enum, dict, list, tuple, and fallback `repr()`. Tests only exercise JSON-primitive paths.
- `_difference_to_dict` (line 136) — wraps `_json_safe`. Tested trivially.
- `_worker_loop` (line 288) — the background thread loop. Tested indirectly via `start()`→`_on_record_persisted()`→wait.
- `_write_sidecar` (line 387) — sidecar construction + persistence. Tested indirectly.

**CONFIRMED: MAJOR.** `_json_safe` has 5 distinct branches (bool/int/float/str, Enum, dict, list/tuple, fallback repr) but only the JSON-primitive path is tested. The Enum and fallback-repr branches are completely untested and could silently fail if the verifier encounters real non-JSON types.

**Suggested test:** Create a `Difference` with Enum values in expected/actual, verify `_json_safe` converts to `.value`.

### 28. `game/ui/panels/empire_treasury_panel.py` — ADVISORY

**LOC:** 333 | **Untested per matrix:** `__init__`, `_build_ui`, `_build_section`, `_build_row`, `load_resource_icons`

**Verified:** All untested methods are pygame_gui widget construction and rendering code. `test_empire_treasury_panel.py` exists but doesn't cover internal widget building. ADVISORY (UI rendering code).

### 29. `game/ui/screens/battle_setup/screen.py` — ADVISORY

**LOC:** 189 | **Untested per matrix:** 16 symbols (mostly property shims)

**Verified:** `FleetBattleSetupScreen` is a thin MVVM shell (PROJ-282 Phase 8). The untested symbols are:
- `handle_event`, `update`, `draw`, `handle_resize` — IScene protocol methods (ADVISORY rendering)
- `start` — delegates to controller, tested indirectly
- 8 property shims (`active_fleet_index`, `tick_limit`, `end_all_destroyed`, etc.) — simple getter/setters
- `_get_toggle` — controller accessor

**FALSE POSITIVE for most symbols.** Property shims are mechanical forwarders. ADVISORY.

### 30. `game/ui/screens/build_queue_queue_data_source.py` — MINOR

**LOC:** 184 | **Untested per matrix:** `_format_int`, `__init__`

**Verified:** `_format_int` (lines 57-62) is a static function with 3 branches (zero→"-", non-zero→formatted, rounds float). The zero-value branch is tested implicitly. `__init__` is trivial storage. **MINOR.**

### 31. `game/ui/screens/builder/components.py` — MINOR

**LOC:** 173 | **Untested per matrix:** `set_selected`, `set_hovered`

**Verified:** Both are 2-line pygame_gui button state setters (`button.select()/unselect()`, `is_hovered = True/False`). Tested indirectly by interaction controller tests. **MINOR.**

### 32. `game/ui/screens/event_log_data_source.py` — MINOR

**LOC:** 242 | **Untested per matrix:** `_recompute_filtered`

**Verified:** `_recompute_filtered` (lines 227-242) is called from `__init__`, `set_filter`, and `update_events`. All three callers are tested. The private method splits into "all" filter vs category-specific filter. **FALSE POSITIVE — tested indirectly.** MINOR.

### 33. `game/ui/screens/fleet_report_window.py` — ADVISORY

**LOC:** 430 | **Untested per matrix:** 12 symbols

**Verified:** The untested symbols are either:
- `FleetReportLayoutBuilder.build()` — pygame_gui widget construction (ADVISORY)
- Event handlers (`process_event`, `_handle_row_click`) — UI event dispatch (ADVISORY)
- Private mutators (`_swap_columns`, `_toggle_filter`, `_toggle_column`, `_post_removal_refresh`, `_apply_tri_state_filter`) — indirectly tested via `select_ship` and integration tests in `test_fleet_report_window.py`

**Mostly FALSE POSITIVES** due to indirect testing through the public API. ADVISORY due to UI layer.

### 34. `game/ui/screens/test_lab/data_extractor.py` — MAJOR

**LOC:** 227 | **Untested per matrix:** `extract_ships`, `_extract_component_ids`, `load_component`, `get_components_cache`

**Verified:** `test_data_paths.py` is the only test file. The 4 untested methods contain substantial logic:
- `extract_ships` (lines 55-166) — 111 lines of conditional parsing: condition-based ship extraction (single-ship format, multi-ship format), scenario class attribute fallback, PROP-002 hardcoded multi-ship list. **MAJOR: Only ~25% of the method's branches could be covered by existing tests.**
- `_extract_component_ids` (lines 168-185) — walks CORE/ARMOR/HULL layers. **MAJOR: empty layers, missing 'id' key branches untested.**
- `load_component` (lines 187-213) — loads and caches `components.json`. First-call populates cache, subsequent calls read from cache. **MAJOR: cache-miss path, missing file path, empty components list untested.**
- `get_components_cache` (lines 215-227) — triggers lazy cache population.

**CONFIRMED: MAJOR.** `test_data_paths.py` only tests path resolution, not data extraction logic.

### 35. `game/ui/screens/test_lab/renderer/metadata_panel.py` — ADVISORY

**LOC:** 221 | **Untested per matrix:** `__init__`

**Verified:** `__init__` (lines 26-52) stores injected font/color references. Tested by `test_metadata_panel.py` which constructs the class and calls `draw()`. **FALSE POSITIVE.** ADVISORY.

### 36. `game/ui/services/modifier_icon_service.py` — MINOR

**LOC:** 87 | **Untested per matrix:** `__init__`

**Verified:** `__init__` (lines 37-46) stores `icon_size` and computes `_base_path`. Tested by `test_modifier_icon_service.py` through `get_icon()`. **MINOR — dunder init not directly tested.**

---

## Tier 3 — Verified Coverage (Confirmed Well-Tested)

### 37. `game/ai/group_target_coordinator.py` — CONFIRMED

**LOC:** 124 | **All 5 symbols tested**

`test_group_target_coordinator.py` (9.8KB) exhaustively tests all 4 methods. Coverage verified:
- `select_focus_target`: all 5 priority modes + "largest"→"strongest" equivalence + None for empty enemies + default fallback
- `compute_group_hp_ratio`: normal case, zero HP, empty list, total_max=0 guard
- `should_commit_reserve`: above/below/at threshold, empty list
- `find_flagship_successor`: candidates found, no candidates, has_cnc_check filter

### 38. `game/ai/spatial_behaviors/__init__.py` — CONFIRMED

**LOC:** 66 | **All 1 symbol tested**

`create_spatial_behavior` tested by `test_spatial_behaviors.py` for all 7 known types + unknown type fallback to `FreeManeuverBehavior`.

### 39. `game/simulation/components/modifiers.py` — CONFIRMED

**LOC:** 149 | **All 4 symbols tested**

Tested by `test_modifiers.py` and `test_invalid_operation_handling.py`. All 4 functions covered.

### 40. `game/strategy/engine/superweapon_command_handlers.py` — CONFIRMED

**LOC:** 353 | **All 22 symbols tested**

Extensively tested by 3 test files totaling ~52KB. 12 command handlers × validation + error paths + mission handlers with MOVE+ACTION queuing.

### 41. `game/ui/services/image/factory.py` — CONFIRMED

**LOC:** 82 | **All 3 symbols tested**

`test_factory.py` (3.1KB) tests: registered provider creation, unknown provider raises, deferred validation returns None.

---

## Corrected Phase 1 Data

| File | Phase 1 Tier | Corrected Tier | Correction |
|------|-------------|----------------|------------|
| `game/context.py` | Tier 2 | Tier 3 | `__init__` tested indirectly through `create_production`/`create_test` |
| `game/simulation/components/abilities/colonize.py` | Tier 2 | Tier 3 | `_parse_attrs` tested indirectly through `__init__` with all branches |
| `game/strategy/combat/spec_compiler.py` | Tier 2 (10/3) | Tier 3 (10/10) | All 7 "untested" private methods tested through `build_strategy_battle_spec` |
| `game/simulation/systems/battle_end_conditions.py` | Tier 2 (67/57) | Tier 2 (67/57) | Correct — 10 `__repr__` untested but cosmetic |
| `game/ui/screens/event_log_data_source.py` | Tier 2 (11/10) | Tier 3 (11/11) | `_recompute_filtered` tested indirectly |
| `game/ui/screens/test_lab/renderer/metadata_panel.py` | Tier 2 (4/3) | Tier 3 (4/4) | `__init__` tested when `draw()` is called |

---

## File Coverage Verification Table

| # | File | Tier | LOC | Symbols Tested/Total | Verdict |
|---|------|------|-----|----------------------|---------|
| 1 | `game/ai/group_target_coordinator.py` | 3 | 124 | 5/5 | CONFIRMED |
| 2 | `game/ai/spatial_behaviors/__init__.py` | 3 | 66 | 1/1 | CONFIRMED |
| 3 | `game/context.py` | 3↑ | 191 | 4/4 | FALSE POS (was T2) |
| 4 | `game/core/protocols/registry.py` | 0 | 38 | 0/5 | ADVISORY (protocol) |
| 5 | `game/engine/__init__.py` | 0 | 36 | 0/0 | ADVISORY (re-export) |
| 6 | `game/simulation/components/abilities/colonize.py` | 3↑ | 81 | 4/4 | FALSE POS (was T2) |
| 7 | `game/simulation/components/abilities/stat_keys.py` | 2 | 190 | 7/8 | MINOR (__post_init__) |
| 8 | `game/simulation/components/component.py` | 2 | 406 | 31/35 | MINOR (mark_hp_cache_dirty) |
| 9 | `game/simulation/components/component_loader.py` | 2 | 323 | 9/10 | MINOR (__init__) |
| 10 | `game/simulation/components/modifiers.py` | 3 | 149 | 4/4 | CONFIRMED |
| 11 | `game/simulation/entities/stat_contributors/__init__.py` | 1 | 33 | 0/0 | ADVISORY (re-export) |
| 12 | `game/simulation/systems/battle_end_conditions.py` | 2 | 496 | 57/67 | MINOR (10 __repr__) |
| 13 | `game/strategy/combat/spec_compiler.py` | 3↑ | 693 | 10/10 | FALSE POS (was T2) |
| 14 | `game/strategy/data/__init__.py` | 1 | 0 | 0/0 | ADVISORY (empty) |
| 15 | `game/strategy/engine/game_config.py` | 2 | 261 | 8/10 | MINOR |
| 16 | `game/strategy/engine/handlers/__init__.py` | 0 | 72 | 0/0 | ADVISORY (re-export) |
| 17 | `game/strategy/engine/superweapon_command_handlers.py` | 3 | 353 | 22/22 | CONFIRMED |
| 18 | `game/strategy/facade/strategy_session_facade.py` | 2 | 502 | 73/82 | MINOR (property shims) |
| 19 | `game/strategy/services/ability_sources/facility.py` | 0 | 87 | 0/9 | **CRITICAL** |
| 20 | `game/strategy/services/replay_verification_coordinator.py` | 2 | 441 | 8/13 | **MAJOR** |
| 21 | `game/ui/panels/empire_treasury_panel.py` | 2 | 333 | 7/12 | ADVISORY (UI) |
| 22 | `game/ui/research/__init__.py` | 0 | 8 | 0/0 | ADVISORY (re-export) |
| 23 | `game/ui/screens/battle_setup/screen.py` | 2 | 189 | 8/31 | ADVISORY (MVVM shell) |
| 24 | `game/ui/screens/build_queue_queue_data_source.py` | 2 | 184 | 6/8 | MINOR |
| 25 | `game/ui/screens/builder/components.py` | 2 | 173 | 5/7 | MINOR |
| 26 | `game/ui/screens/event_log_data_source.py` | 3↑ | 242 | 11/11 | FALSE POS (was T2) |
| 27 | `game/ui/screens/fleet_report_window.py` | 2 | 430 | 6/18 | ADVISORY (UI events) |
| 28 | `game/ui/screens/galaxy_test/galaxy_mode.py` | 0 | 427 | 0/8 | ADVISORY (UI) |
| 29 | `game/ui/screens/race_setup/panel_factory.py` | 0 | 177 | 0/7 | ADVISORY (glue) |
| 30 | `game/ui/screens/strategy_windows/event_log_window_ctrl.py` | 0 | 159 | 0/9 | ADVISORY (UI) |
| 31 | `game/ui/screens/strategy_windows/list_windows.py` | 0 | 107 | 0/11 | ADVISORY (UI) |
| 32 | `game/ui/screens/test_lab/data_extractor.py` | 2 | 227 | 3/7 | **MAJOR** |
| 33 | `game/ui/screens/test_lab/renderer/metadata_panel.py` | 3↑ | 221 | 4/4 | FALSE POS (was T2) |
| 34 | `game/ui/screens/test_lab/renderer/orchestrator.py` | 0 | 211 | 0/4 | ADVISORY (rendering) |
| 35 | `game/ui/screens/transfer_controller.py` | 0 | 323 | 0/10 | **CRITICAL** |
| 36 | `game/ui/screens/workshop_data_reloader.py` | 0 | 197 | 0/11 | **CRITICAL** |
| 37 | `game/ui/screens/workshop_viewmodel_ship_ops.py` | 0 | 330 | 0/18 | **CRITICAL** |
| 38 | `game/ui/services/image/factory.py` | 3 | 82 | 3/3 | CONFIRMED |
| 39 | `game/ui/services/modifier_icon_service.py` | 2 | 87 | 3/4 | MINOR (__init__) |

**Corrected Totals:** CRITICAL 4 | MAJOR 4 | MINOR 8 | ADVISORY 18 | CONFIRMED 5

---

## Context Usage Estimate

- **Production files read:** 39/39 (100%)
- **Key test files verified:** ~15 of ~70 candidate test files
- **Lines of production code reviewed:** ~8,649
- **Phase 1 corrections applied:** 6 files re-tiered (3 Tier 2→3, 3 Tier 2→3 on false positives)
- **Blind-spots acknowledged:** Did not exhaustively verify all 70+ candidate test files; relied on Phase 1 data + selective spot-checking for Tier 3 files. Tier 0 and critical Tier 2 files were read exhaustively.
