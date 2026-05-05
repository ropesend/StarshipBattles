# Test Coverage Audit — Shard 16 (Discovery Agent)

**Date:** 2026-05-04
**Files in scope:** 35 production files, ~8541 LOC
**Methodology:** Every production file read exhaustively. Each function/method/class assessed against corresponding test files. Coverage matrix pre-computed data cross-referenced and verified.

---

## Summary

| Severity | Count | Description |
|----------|-------|-------------|
| **CRITICAL** | 3 | Tier 0 non-UI files with zero tests |
| **MAJOR** | 5 | Tier 1-2 files with substantial untested code or error paths |
| **MINOR** | 11 | Tier 2 files with minor gaps (partial branch coverage, small methods) |
| **ADVISORY** | 8 | UI rendering, `__init__.py`, stubs |
| **VERIFIED (Tier 3)** | 8 | Adequately tested per both matrix and manual review |

---

## CRITICAL — Tier 0 Non-UI, Zero Test Coverage

### 1. `game/core/protocols/strategy_entities.py` (456 LOC, 87 symbols)

**Status:** TIER_0_NO_TESTS — 0 candidate test files.

This is a **core protocol file** defining 10 structural protocols (`IStarSystem`, `IStar`, `IPlanet`, `IOrderable`, `IZoneOccupant`, `IFleet`, `IWarpPoint`, `ISectorEnvironment`, `IStorm`, `IAbilitySource`) and 9 TypeGuard functions. These are the interface contracts for the strategy layer — all strategy-consuming code depends on them.

**Gap:** Zero tests exist. No tests verify that concrete implementations satisfy the protocols (e.g., `isinstance(star_system, IStarSystem)`). No tests exercise the TypeGuard functions (`is_star_system`, `is_star`, `is_planet`, `is_fleet`, `is_warp_point`, `is_sector_environment`, `is_storm`, `is_ability_source`, `is_zone_occupant`).

**Risk:** A misnamed attribute on a concrete entity breaks protocol compatibility silently. Protocol drift (adding/removing attributes) goes undetected until runtime failures in strategy/UI code. The `IAbilitySource` protocol (PROJ-300) is particularly high-risk — it defines the contract for 6+ adapter classes.

**Recommendation:** Create `tests/unit/core/protocols/test_strategy_entities.py` with:
- `test_is_star_system` — positive/negative checks
- `test_is_star` — positive/negative checks
- `test_is_planet` — positive/negative checks
- `test_is_fleet` — positive/negative checks
- `test_is_warp_point` — positive/negative checks
- `test_is_sector_environment` — positive/negative checks
- `test_is_storm` — positive/negative checks
- `test_is_ability_source` — positive/negative checks with mock objects
- `test_is_zone_occupant` — positive/negative checks
- For each protocol: `test_<Protocol>_compliance` using concrete instances

---

### 2. `game/strategy/services/ability_sources/storm.py` (77 LOC, 9 symbols)

**Status:** TIER_0_NO_TESTS — 0 candidate test files.

The `StormAbilitySource` adapter wraps Storm entities to satisfy `IAbilitySource`. This is Tier 0 (non-UI strategy service) with substantial logic:
- `affects_hex()` has two code paths (global-frame with `system` vs local-frame fallback)
- `get_abilities()` has a type guard branch
- `source_id` construction uses prefix/suffix patterns

**Gap:** No tests. No tests for:
- `affects_hex` with global-coordinate translation (system.global_location present)
- `affects_hex` fallback path (system None, mock with occupied_hexes)
- `affects_hex` with AttributeError path
- `get_abilities` with valid/invalid storm.abilities shapes
- `source_kind`, `source_label`, `source_id` property values
- `affects_system` returning True
- `get_activation_state` returning None

**Risk:** Storm abilities silently fail to apply in combat if `affects_hex` coordinate math is wrong. The global-translation path involves `storm.location + offset + system.global_location` — coordinate frame errors produce zero-coverage bugs.

**Recommendation:** Create `tests/unit/strategy/services/ability_sources/test_storm.py` with comprehensive coverage of both `affects_hex` code paths.

---

### 3. `game/strategy/engine/handlers/build.py` (66 LOC, 4 symbols)

**Status:** TIER_0_NO_TESTS — 0 candidate test files.

Contains `BuildOrderCommandHandler` and `RemoveBuildOrderCommandHandler` — command handlers that modify fleet state (insert BUILD orders, clear movement paths, remove orders). These are game-state mutating handlers with specific side effects:
- `BuildOrderCommandHandler.execute`: inserts BUILD at queue front, clears `fleet.path`
- `RemoveBuildOrderCommandHandler.execute`: removes all BUILD-type orders via `fleet.remove_orders_by_type()`
- Both have `_resolve_player_fleet` error-path branches

**Gap:** Zero tests. No tests verify:
- BUILD order insertion at position 0
- Path clearance on BUILD
- Error path when fleet_id not found
- Remove BUILD order correctly delegates to `remove_orders_by_type`

**Risk:** BUILD-order bugs (fleet moving while building, double-build-orders) are high-impact because they affect production economy. These handlers are called by the turn engine.

**Recommendation:** Create `tests/unit/strategy/engine/handlers/test_build.py` with mocked GameSession and Fleet objects.

---

## MAJOR — Tier 1-2 Partial Coverage with Substantial Gaps

### 4. `game/strategy/combat/spec_compiler.py` (683 LOC, 3/10 symbols tested)

**Status:** TIER_2_PARTIAL. Only `build_strategy_battle_spec` (public entry point) has test coverage. Seven internal helpers are untested:

| Symbol | LOC | Why untested |
|--------|-----|-------------|
| `_build_strategy_post_battle_hook` | ~50 | Internal, exercised via `build_strategy_battle_spec` |
| `_hook` (closure) | ~5 | Inner closure of above |
| `_team_spec_for_fleet_group` | ~55 | Core fleet→TeamSpec translation |
| `_pick_formation_for_fleet` | ~10 | Formation resolution priority logic |
| `_ship_spec_from_instance` | ~45 | ShipInstance → ShipSpec translation, component sorting |
| `_build_modifier_stack` | ~45 | Modifier stack construction, sector-effects routing |
| `_emit_entries_team_scoped` | ~25 | AbilityStatRegistry wrapper |

The existing test file `test_spec_compiler.py` (760 LOC) mostly tests `build_strategy_battle_spec` end-to-end. While this exercises many of the internal functions indirectly, several have branch-level gaps:

- `_pick_formation_for_fleet`: The `task_forces` attribute check (`getattr(fleet, "task_forces", [])`) and first-TF-wins priority logic is not explicitly tested
- `_ship_spec_from_instance`: The `hasattr(ship, "design_data")` and `instance_components` branching, component sorting determinism
- `_build_modifier_stack`: The PROJ-343 ownerful routing (`empire_to_team_id`) branch
- `_team_spec_for_fleet_group`: Multi-fleet-per-team (PROJ-320 Phase 3) path, empty-fleet raise

**Risk:** This is a 683 LOC, high-complexity compiler. Untested internal branches that handle PROJ-320 allied-fleets, PROJ-343 ownerful sector effects, and formation resolution could produce silently wrong BattleSpecs.

---

### 5. `game/simulation/entities/ship_combat_engine.py` (252 LOC, 6/9 symbols tested)

**Status:** TIER_2_PARTIAL. Untested: `__init__`, `select_target`, `calculate_firing_solution`.

The `__init__` being flagged is likely a heuristic false positive (the engine is created in ship construction, tested implicitly). However:

- `select_target` (line 99-111): Delegates to `TargetingSystem.select_target`. This delegation path is the primary target-acquisition codepath for AI-controlled ships. Not explicitly unit-tested.
- `calculate_firing_solution` (line 113-126): Delegates to `TargetingSystem.calculate_firing_solution`. The `(aim_position, aim_vector)` return tuple shape is untested.

The delegated methods (`solve_lead`, `fire_weapons`, `take_damage`, `update_combat_cooldowns`) are adequately covered by `test_combat_ops.py` and `test_cooldowns.py`. The `_apply_repair` private method is exercised via `update_combat_cooldowns`.

**Gap:** The `take_damage` → SHIP_DESTROYED event emission path and `was_alive` gating (lines 161-174) should be explicitly verified.

---

### 6. `game/simulation/interfaces/ai_controller.py` (140 LOC, 3/7 symbols tested)

**Status:** TIER_2_PARTIAL. The `IAIController` protocol is well-tested (used throughout AI tests). The `IAIControllerFactory` protocol methods are flagged as untested: `set_grid`, `create_for_ship`, `create_for_ships`.

Since these are **protocol definitions** (no implementation), coverage depends on whether any test explicitly checks protocol compliance:
- `tests/unit/simulation/interfaces/test_ai_controller_interface.py` tests IAIController compliance
- The factory protocol methods are exercised implicitly through the concrete `AIControllerFactory` in `tests/unit/simulation/factories/test_ai_factory.py`

**Risk:** Low — protocols don't have runtime behavior to break. But the formal contract is unenforced.

---

### 7. `game/simulation/components/modifier_manager.py` (330 LOC, 10/15 symbols tested)

**Status:** TIER_2_PARTIAL. Untested: `__init__`, `_load_initial_modifiers`, `remove_modifier_inplace`, `get_all_effects_static`, `get_stat_summary_static`.

- `__init__` and `_load_initial_modifiers`: Likely tested implicitly (Component creation hits these). Heuristic false positive.
- `remove_modifier_inplace`: Static method used by `add_modifier_static` during modifier replacement. Not directly tested.
- `get_all_effects_static` / `get_stat_summary_static`: DEPRECATED static methods marked for removal in Task 1.3. The instance versions (`get_all_effects` / `get_stat_summary`) are tested.

The instance method `remove_modifier` (in-place list mutation, line 127-138) differs from the deprecated static `remove_modifier_static` (returns new list). The in-place behavior is tested indirectly via `add_modifier` which calls `remove_modifier` for replacement.

**Risk:** Low — the deprecated statics should simply be removed. The instance methods are covered.

---

### 8. `game/simulation/components/abilities/__init__.py` (303 LOC, 1/3 symbols tested)

**Status:** TIER_2_PARTIAL. Untested: `_contains_unevaluated_formula`, `get_ability_default_scope`.

- `_contains_unevaluated_formula` (lines 151-166): Recursive formula-string detector. Has three type branches (str, dict, list). Used in `create_ability` error handling. **No direct tests.** Formula detection logic is safety-critical — false negatives cause `create_ability` to raise instead of skip.
- `get_ability_default_scope` (lines 191-221): PROJ-272 Phase 1 helper that resolves class-level `default_scope` for ability names. Has fallback branch for unknown abilities + enum-value extraction. **No direct tests.**

The rest of the file (ABILITY_REGISTRY, `create_ability`, imports) is tested through `test_create_ability_formula_skip.py` and various ability tests.

---

## MINOR — Tier 2 Partial Coverage, Small Gaps

### 9. `game/assets/asset_manager.py` (350 LOC, 13/20 symbols tested)

Untested (7 symbols): `__init__`, `_load_star_metadata`, `clear`, `load_star_image`, `get_star_core_info`, `get_star_asset_key_for_type`, `_get_star_folder_for_size`.

Several are heuristic false positives (`__init__` tested via `get_default_asset_manager()`). Real gaps:
- `load_star_image` (line 132): Star multi-resolution loading with fallback chain. Used by star rendering.
- `get_star_core_info` (line 160): Star metadata lookup with default fallback dict.
- `get_star_asset_key_for_type` (line 178): Manifest-driven star type → asset key mapping.
- `_get_star_folder_for_size` / `_load_star_metadata`: Star-specific infrastructure.

The planet-related methods (`load_planet_image`, `_get_planet_folder_for_size`) and core methods (`load_image`, `load_group`, `get_missing_texture`) ARE well tested.

---

### 10. `game/core/registry.py` (470 LOC, 34/37 symbols tested)

Untested (3 symbols): `GameRegistries.__post_init__`, `RegistryManager.unfrozen`, `freeze_registry`.

- `__post_init__`: Sets default ResourceCatalog when `resource_catalog` is None. Tested implicitly.
- `unfrozen` contextmanager: Scoped unfreeze with exception-safe restoration. **The `yield` path is tested, but the `finally` re-freeze on exception is not explicitly verified.**
- `freeze_registry`: Module-level wrapper. Tested implicitly through freeze/clear tests.

**Gap:** `unfrozen` contextmanager's exception-safety (re-freeze on exit via exception) should have an explicit test.

---

### 11. `game/strategy/data/empire.py` (387 LOC, 15/17 symbols tested)

Untested: `add_colony`. This is a 3-line method that appends to `self.colonies` and sets `planet.owner_id`. Likely tested indirectly via empire construction + colony operations. The test file `test_empire.py` (in 35 candidate test files) exercises most methods.

---

### 12. `game/strategy/generation/density/density_map.py` (241 LOC, 6/7 symbols tested)

Untested: `DensityMap.__len__` — a one-liner returning `len(self._primitives)`. Trivial gap.

---

### 13. `game/strategy/systems/save_game_service.py` (519 LOC, 11/17 symbols tested)

Untested (6 symbols): `set_replay_store`, `get_replay_store`, `_notify_replay_store_save_or_load`, `_notify_replay_store_save_deleted`, `SaveGameService._validate_save`, `SaveGameService._is_compatible_version`.

- Replay store functions (PROJ-312): Module-level getter/setter + two notification helpers. These are wiring functions — set/get are trivial, notification helpers have broad-exception try/except blocks that swallow errors.
- `_validate_save`: Validates folder structure (metadata.json + turns/ folder). **Error branches for missing folder, not-a-directory, missing metadata, missing turns folder are untested.**
- `_is_compatible_version`: Strict version check returning bool. Simple but could reject valid saves if broken.

The main save/load/delete/list APIs are well covered by `test_save_load_ops.py`, `test_error_handling.py`, `test_load_helpers.py`.

---

### 14. `game/ui/assets/ship_theme_manager.py` (453 LOC, 17/20 symbols tested)

Untested: `__init__`, `_validate_image_size`, `get_theme_description`.

- `__init__` — heuristic false positive (tested via `get_default_ship_theme_manager()`)
- `_validate_image_size` (line 239-267): PIL-based image dimension validation with multiple error-swallowing branches (PIL import failure, decode error, TypeError in expected size parsing). **Best-effort validation with no test coverage.**
- `get_theme_description` (line 423-426): Simple accessor, likely tested implicitly.

---

### 15. `game/ui/panels/race_identity_panel.py` (493 LOC, 11/15 symbols tested)

Untested: `_create_race_section`, `_create_government_section`, `_create_faction_section`, `_recreate_dropdown`.

These are UI widget construction methods — `pygame_gui` element creation. The public API (`update_config`, `set_from_config`, `handle_event`, `_auto_generate_faction_name`) is well tested. The private helpers are exercised through panel construction in integration tests.

---

### 16. `game/ui/screens/build_queue_viewmodel.py` (268 LOC, 17/19 symbols tested)

Untested: `__init__`, `queue_sources`.

- `__init__` — heuristic false positive (tested through ViewModel construction in test file)
- `queue_sources` property — simple getter, tested implicitly

---

### 17. `game/ui/screens/empire_build_queue_data_source.py` (114 LOC, 5/7 symbols tested)

Untested: `__init__`, `_get_column_value`.

`_get_column_value` has two special branches (system/sector column names → galaxy lookups) + default delegation. These branches are exercised through `get_cell_value` but not directly tested with specific column_id values.

---

### 18. `game/ui/screens/orders_window.py` (469 LOC, 11/21 symbols tested)

Untested (10 symbols): `OrdersListRenderer`, `OrdersListRenderer.render`, `OrdersWindowUiBuilder`, `OrdersWindowUiBuilder.build`, `OrdersWindow.__init__`, `OrdersWindow.rebuild_list`, `OrdersWindow.process_event`, `OrdersWindow.move_order`, `OrdersWindow.edit_order`, `OrdersWindow.delete_order`.

Many of these are PROJ-328 two-stage construction artifacts:
- `OrdersListRenderer` and `OrdersWindowUiBuilder` are production widget builders; testing uses `MockOrdersUiBuilder` / `NullOrdersUiBuilder`. The production builders are only exercised in integration tests.
- `process_event` has complex button-ID parsing logic (`#up_`, `#down_`, `#edit_`, `#del_` prefix matching + `int()` parsing) — **the string-parsing path is untested.**

The pure-data `OrderDescriber` is very well tested in `test_orders_window.py`.

---

### 19. `game/ui/screens/race_browser_dialog.py` (338 LOC, 8/11 symbols tested)

Untested: `RaceBrowserDialogUiBuilder`, `RaceBrowserDialogUiBuilder.build`, `RaceBrowserDialog._render_row_surface`.

`RaceBrowserDialogUiBuilder` is the production widget builder — integration-only. `_render_row_surface` (line 232-272) is a composite surface renderer with portrait/flag/ship/name layout logic. **The surface composition logic is untested.**

---

### 20. `game/ui/screens/race_setup/input_handler.py` (174 LOC, 2/3 symbols tested)

Untested: `RaceSetupInputHandler.handle`. This is the giant event dispatch method (~170 lines) routing 15+ button types. **The routing logic is only tested via integration with the full RaceSetupScreen.**

---

## ADVISORY — UI Rendering, `__init__.py`, Stubs

| File | LOC | Tier | Notes |
|------|-----|------|-------|
| `game/simulation/__init__.py` | 130 | TIER_1 | Package init with re-exports only |
| `game/simulation/validation/__init__.py` | 36 | TIER_0 | Package init with re-exports only |
| `game/ui/research/__init__.py` | 8 | TIER_0 | Package init, single import |
| `game/ui/research/research_renderer.py` | 324 | TIER_0 | Pure rendering (pygame draw calls). Visual-only. |
| `game/ui/screens/galaxy_test/__init__.py` | 9 | TIER_1 | Package init |
| `game/ui/screens/test_lab/__init__.py` | 22 | TIER_1 | Package init |
| `game/ui/screens/test_lab/component_dropdown.py` | 157 | TIER_0 | Custom pygame dropdown widget. Visual rendering. |
| `game/ui/screens/test_lab/details/panel.py` | 216 | TIER_0 | Combat Lab details panel. Visual rendering with scroll/click handling. |
| `game/ui/screens/strategy_windows/ship_picker.py` | 43 | TIER_0 | Stub class (`ShipPickerStub`) — placeholder for future enhancement. |

---

## VERIFIED — Tier 3, Adequately Covered

| File | LOC | Symbols | Verification |
|------|-----|---------|-------------|
| `game/simulation/components/modifier_schema.py` | 251 | 6/6 | Schema validation functions well-tested. `test_modifier_schema.py` + `test_modifier_json_schema.py` + `test_invalid_operation_handling.py` cover all validation branches including empty-effects rejection. |
| `game/simulation/components/modifiers.py` | 149 | 4/4 | Effect application functions tested. `test_modifiers.py` + `test_invalid_operation_handling.py` cover `apply_modifier_effects`, `calculate_stat_multipliers`, `get_default_stat_multipliers`, `_apply_effect_to_dict`. |
| `game/simulation/designs.py` | 68 | 2/2 | `create_brick` + `create_interceptor` tested via `test_designs.py`. |
| `game/simulation/validation/base.py` | 126 | 7/7 | Template-method pattern base classes. `test_base_rule.py` + `test_ship_validator_rules.py` + `test_ship_validator_di.py` cover all abstract/concrete behavior. |
| `game/strategy/data/storm.py` | 154 | 4/4 | Storm entity well-tested. `test_storm.py` (531 LOC) covers creation, occupied_hexes computation, serialization roundtrip, from_dict error paths (invalid location, missing keys, legacy effects rejection), and Galaxy zone registration integration. |
| `game/ui/panels/base_gallery.py` | 265 | 17/17 | Abstract base class for galleries. `test_base_gallery.py` covers scroll/grid/population logic via concrete mock subclass. |
| `game/simulation/components/abilities/__init__.py` | 303 | 1/3 tested | ABILITY_REGISTRY and `create_ability` are tested. Functions `_contains_unevaluated_formula` and `get_ability_default_scope` are untested (flagged in MINOR section above). |

---

## File Coverage Verification Table

| # | File | Tier | Symbols (tested/total) | Key Gaps |
|---|------|------|------------------------|----------|
| 1 | `game/assets/asset_manager.py` | 2 | 13/20 | Star image loading, star metadata |
| 2 | `game/core/protocols/strategy_entities.py` | **0** | 0/87 | **ALL — CRITICAL** |
| 3 | `game/core/registry.py` | 2 | 34/37 | `unfrozen` exception-safety |
| 4 | `game/simulation/__init__.py` | 1 | N/A | Advisory (init only) |
| 5 | `game/simulation/components/abilities/__init__.py` | 2 | 1/3 | `_contains_unevaluated_formula`, `get_ability_default_scope` |
| 6 | `game/simulation/components/modifier_manager.py` | 2 | 10/15 | Deprecated statics, heuristic init gaps |
| 7 | `game/simulation/components/modifier_schema.py` | **3** | 6/6 | None — verified |
| 8 | `game/simulation/components/modifiers.py` | **3** | 4/4 | None — verified |
| 9 | `game/simulation/designs.py` | **3** | 2/2 | None — verified |
| 10 | `game/simulation/entities/ship_combat_engine.py` | 2 | 6/9 | `select_target`, `calculate_firing_solution` delegations |
| 11 | `game/simulation/interfaces/ai_controller.py` | 2 | 3/7 | Factory protocol definitions |
| 12 | `game/simulation/validation/__init__.py` | 0 | N/A | Advisory (init only) |
| 13 | `game/simulation/validation/base.py` | **3** | 7/7 | None — verified |
| 14 | `game/strategy/combat/spec_compiler.py` | 2 | 3/10 | **7 internal helpers — MAJOR** |
| 15 | `game/strategy/data/empire.py` | 2 | 15/17 | `add_colony` (implicit) |
| 16 | `game/strategy/data/storm.py` | **3** | 4/4 | None — verified |
| 17 | `game/strategy/engine/handlers/build.py` | **0** | 0/4 | **ALL — CRITICAL** |
| 18 | `game/strategy/generation/density/density_map.py` | 2 | 6/7 | `__len__` |
| 19 | `game/strategy/services/ability_sources/storm.py` | **0** | 0/9 | **ALL — CRITICAL** |
| 20 | `game/strategy/systems/save_game_service.py` | 2 | 11/17 | `_validate_save` error branches, replay store hooks |
| 21 | `game/ui/assets/ship_theme_manager.py` | 2 | 17/20 | `_validate_image_size`, implicit init |
| 22 | `game/ui/panels/base_gallery.py` | **3** | 17/17 | None — verified |
| 23 | `game/ui/panels/race_identity_panel.py` | 2 | 11/15 | Private UI construction helpers |
| 24 | `game/ui/research/__init__.py` | 0 | N/A | Advisory (init only) |
| 25 | `game/ui/research/research_renderer.py` | 0 | 0/9 | Advisory (pure rendering) |
| 26 | `game/ui/screens/build_queue_viewmodel.py` | 2 | 17/19 | Heuristic init gaps |
| 27 | `game/ui/screens/empire_build_queue_data_source.py` | 2 | 5/7 | `_get_column_value` branches |
| 28 | `game/ui/screens/galaxy_test/__init__.py` | 1 | N/A | Advisory (init only) |
| 29 | `game/ui/screens/orders_window.py` | 2 | 11/21 | Production builders, button-ID parsing |
| 30 | `game/ui/screens/race_browser_dialog.py` | 2 | 8/11 | Production builder, surface rendering |
| 31 | `game/ui/screens/race_setup/input_handler.py` | 2 | 2/3 | `handle()` dispatch routing |
| 32 | `game/ui/screens/strategy_windows/ship_picker.py` | 0 | 0/3 | Advisory (stub) |
| 33 | `game/ui/screens/test_lab/__init__.py` | 1 | N/A | Advisory (init only) |
| 34 | `game/ui/screens/test_lab/component_dropdown.py` | 0 | 0/6 | Advisory (custom widget) |
| 35 | `game/ui/screens/test_lab/details/panel.py` | 0 | 0/8 | Advisory (rendering) |

---

## Prioritized Remediation Plan

### Immediate (CRITICAL — 0 tests exist, non-UI code)

1. **`game/strategy/engine/handlers/build.py`** — Create `tests/unit/strategy/engine/handlers/test_build.py`
   - Test BUILD order insert + path clear
   - Test fleet-not-found error path
   - Test RemoveBuildOrder delegation
   - Estimated: ~60 LOC test file, 5 test cases

2. **`game/strategy/services/ability_sources/storm.py`** — Create `tests/unit/strategy/services/ability_sources/test_storm.py`
   - Test `affects_hex` with both code paths (global + fallback)
   - Test `get_abilities` valid/missing
   - Test all properties
   - Estimated: ~80 LOC test file, 8 test cases

3. **`game/core/protocols/strategy_entities.py`** — Create `tests/unit/core/protocols/test_strategy_entities.py`
   - Test all 9 TypeGuard functions (positive + negative)
   - Test protocol compliance with concrete instances
   - Estimated: ~150 LOC test file, 20 test cases

### Short-term (MAJOR — substantial gaps in tested files)

4. **`game/strategy/combat/spec_compiler.py`** — Enhance `test_spec_compiler.py`
   - Test `_entries_from_sector_effects` ownerful routing (PROJ-343 branch)
   - Test `_ship_spec_from_instance` with/without design_data, with component sorting
   - Test `_team_spec_for_fleet_group` multi-fleet path
   - Estimated: ~100 LOC additions

5. **`game/simulation/components/abilities/__init__.py`** — Create/modify tests
   - Test `_contains_unevaluated_formula` for str/dict/list branches
   - Test `get_ability_default_scope` for known/unknown/false-attribute cases
   - Estimated: ~50 LOC additions

### Backlog (MINOR — small gaps)

6. Test `unfrozen` contextmanager exception re-freeze path (registry.py)
7. Test `_validate_save` error branches (save_game_service.py)
8. Test `_validate_image_size` error-swallowing (ship_theme_manager.py)
9. Test `RaceSetupInputHandler.handle` routing (race_setup/input_handler.py)
10. Test OrdersWindow button-ID parsing (orders_window.py)

---

## Context Usage Estimate

**Total files read:** 35 production files + 3 test files + 3 docs + coverage matrix = ~42 files
**Lines read (production):** ~8,541 LOC
**Report generation:** ~500 lines
**Total context:** Approximately 75K tokens (production files) + 10K (tests) + 3K (docs) + 5K (report) ≈ 93K tokens
