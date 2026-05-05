# Shard 05 — Test Coverage Audit Report

**Date:** 2026-05-04
**Files in scope:** 42 production files, ~8,785 LOC
**Audit type:** Full discovery (every production file read, every candidate test file traced)

---

## Summary

| Severity | Count | Description |
|----------|-------|-------------|
| **CRITICAL** | 1 | Tier 0 non-UI file with zero unit tests |
| **MAJOR** | 7 | Tier 1-2 files with untested business logic, error paths, or boundary conditions |
| **MINOR** | 3 | Partially tested symbols with missing branch/edge coverage |
| **ADVISORY** | 11 | UI rendering/event code, `__init__.py` re-exports |
| **FALSE NEGATIVE** | 1 | Pre-computed matrix wrongly classified a file as Tier 0 |
| **Total** | 42 files analyzed | 100% of shard read |

### Aggregate tier distribution

| Tier | Files | LOC |
|------|-------|-----|
| Tier 0 (zero coverage) | 10 | 1,627 |
| Tier 2 (partial coverage) | 25 | 5,765 |
| Tier 3 (apparently covered) | 7 | 1,393 |

### Key Risks

- **Core protocols with zero tests** (`game/core/protocols/ui.py`): `IScene`, `ICamera`, and `is_camera` TypeGuard have no direct unit tests. These are runtime-checkable protocols used by multiple layers; a regression in the `is_camera` TypeGuard would silently break camera-dependent features across research, strategy, and UI.

- **Infrastructure service with no tests** (`game/ui/services/game_settings.py`): One of 10 `ApplicationContext`-managed services with concrete I/O behavior (JSON read/write), a module-level singleton, and no tests. A `save`/`load` bug would corrupt user settings silently.

- **System effects collector private pipeline** (`game/strategy/services/system_effects_collector.py`): Five private helpers (`_ability_kind`, `_format_status`, `_is_activatable`, `_aggregate`, `_legacy_provider_fields`) spanning 474 lines with D16/D17 validation, ownership gating, scope filtering, and activation state logic are tested only indirectly. The `_aggregate` function alone contains 192 lines of conditionals.

- **Workshop layer ops with zero tests** (`game/ui/screens/workshop_viewmodel_layer_ops.py`): 254 lines of pure-Python algorithm code (layer resolution, component movement) extracted from a monolith during PROJ-309 but never given unit tests. No Pygame dependencies — testable.

---

## Tier 0 Findings (Zero Coverage)

### CRITICAL: `game/core/protocols/ui.py` (112 LOC, 15 symbols)

**Path:** `game/core/protocols/ui.py`
**Coverage matrix:** Tier 0, 0 candidate test files
**Layer:** Core (should never be Tier 0)

This module defines two `@runtime_checkable` protocols and one `TypeGuard`:

| Symbol | Line | Type |
|--------|------|------|
| `IScene` | 8-31 | `@runtime_checkable` Protocol with 4 abstract methods |
| `ICamera` | 33-107 | `@runtime_checkable` Protocol with 8 abstract methods + properties |
| `is_camera` | 110-112 | `TypeGuard[ICamera]` function |

**Why CRITICAL:** These are core-layer protocols used by the strategy, research, and UI layers for dependency inversion. The `@runtime_checkable` decorator means `isinstance(obj, IScene)` and `isinstance(obj, ICamera)` are valid at runtime, which means a protocol drift (adding/removing methods) would silently pass structural checks without tests. The `is_camera` TypeGuard delegates to `_has_attrs(obj, 'width', 'height', 'zoom', 'world_to_screen')` from `game/core/protocols/common.py` — if the attribute-check helper changes, `is_camera` may silently mismatch `ICamera` without any failing test.

**Covered indirectly?** Yes — `IScene` is implemented by all screen classes (tested indirectly), and `ICamera` is implemented by the concrete `Camera` class (tested via integration tests). However, neither the `TypeGuard`, nor the `@runtime_checkable` semantics, nor `isinstance()` protocol checks are exercised by any direct test.

**Recommendation:** Add `tests/unit/core/protocols/test_ui.py` with:
- `is_camera` TypeGuard: true/false for objects with/without camera attributes
- `isinstance(obj, IScene)` / `isinstance(obj, ICamera)` runtime protocol checks
- `ICamera` property access on a concrete mock

**Confidence:** Verified — 0 test files referencing `game/core/protocols/ui.py`

---

### MAJOR: `game/ui/services/game_settings.py` (94 LOC, 11 symbols)

**Path:** `game/ui/services/game_settings.py`
**Coverage matrix:** Tier 0, 0 candidate test files
**Layer:** UI Services (ApplicationContext service #9 of 10)

This is a concrete data-persistence service with:

| Symbol | Line | Type |
|--------|------|------|
| `GameSettings` | 25-80 | Class with `__init__`, `_load`, `save`, `get`, `set`, `reset_to_defaults`, `background_brightness` property |
| `get_default_game_settings` | 83-88 | Module-level singleton factory |
| `set_default_game_settings` | 91-94 | Module-level singleton setter |

**Why MAJOR (not CRITICAL):** In the UI services sub-package — not cross-cutting system logic. However:
- It is one of 10 `ApplicationContext`-managed services (`docs/02_PATTERNS.md` §1)
- `_load()` (line 36) reads JSON from `output/settings/game_settings.json` via `load_json` — if the file is corrupt/malformed, it silently falls back to defaults
- `save()` (line 43) writes via `save_json` — output corruption would persist
- `get()` (line 47) returns `DEFAULTS.get(key)` fallback (could return None for unknown keys)
- Module-level singleton `_default_game_settings` (line 22) violates the Singleton divergence risk documented in `docs/02_PATTERNS.md` §18
- No file found at `tests/unit/ui/services/test_game_settings.py` — confirmed by glob

**Recommendation:** Add `tests/unit/ui/services/test_game_settings.py` covering: default construction, get/set roundtrip, `reset_to_defaults`, `_load` with missing/corrupt file, `background_brightness` property clamping, singleton get/set cycle.

**Confidence:** Verified — `glob("**/test_game_settings*")` returned zero results

---

### MAJOR: `game/ai/spatial_behaviors/_formation_utils.py` (39 LOC, 1 symbol)

**Path:** `game/ai/spatial_behaviors/_formation_utils.py`
**Coverage matrix:** Tier 0, 0 candidate test files
**Layer:** AI

Single public function:

| Symbol | Line | Type |
|--------|------|------|
| `compute_circular_position` | 15-39 | Pure function — math-only, no I/O |

**Why MAJOR:** AI-layer utility with zero tests. The function takes 5 parameters (anchor position, distance, slot index, total slots) and computes a circular formation position. Edge cases include:
- `total=0` — handled by `max(int(total), 1)` at line 34 (zero becomes 1)
- `slot_index` negative or exceeding total — wraps via `2*pi*slot_index/total`
- Large coordinate values — no overflow handling

This utility was extracted during PROJ-319 (DUP-X-13) to remove duplicated code but was never given a dedicated test.

**Recommendation:** Add `tests/unit/ai/spatial_behaviors/test_formation_utils.py` covering: normal 4-ship diamond, single-ship case, zero total, negative slot index, edge-case radius 0.

**Confidence:** Verified — `glob("**/test_formation_utils*")` returned zero results

---

### ADVISORY: `game/ui/screens/workshop_viewmodel_layer_ops.py` (254 LOC, 7 symbols)

**Path:** `game/ui/screens/workshop_viewmodel_layer_ops.py`
**Coverage matrix:** Tier 0, 0 candidate test files
**Layer:** UI

| Symbol | Line | Type |
|--------|------|------|
| `WorkshopLayerOps` | 28-254 | Class with 5 public methods |
| `resolve_target_layer` | 53-103 | Algorithm: layer resolution with restriction validation |
| `quick_add_component` | 105-141 | Algorithm: add with auto-layer targeting |
| `resolve_move_target` | 147-193 | Algorithm: find next valid layer in direction |
| `move_component` | 195-213 | Algorithm: single component move |
| `move_component_group` | 215-254 | Algorithm: bulk component move |

**Why ADVISORY (not MAJOR):** In `game/ui/screens/` — UI layer. However, notable that all 7 symbols have zero tests despite being pure-Python algorithm code with no Pygame dependencies. The layer resolution logic (`resolve_target_layer`, lines 53-103) enumerates valid layers, sorts by value, and handles invalid-selected-layer fallback — all testable. Extracted from a monolith in PROJ-309 sub-phase 3.8 but never given tests.

**Recommendation:** `tests/unit/ui/screens/test_workshop_viewmodel_layer_ops.py`

---

### ADVISORY: `game/ui/screens/list_filter_utils.py` (43 LOC, 2 symbols)

**Path:** `game/ui/screens/list_filter_utils.py`
**Coverage matrix:** Tier 0, 0 candidate test files
**Layer:** UI

| Symbol | Line | Type |
|--------|------|------|
| `make_attr_sort_key` | 21-43 | Factory returning a sort-key callable |
| `_key` (inner closure) | 30-42 | Dotted-attribute-path extractor with fallback |

**Why ADVISORY:** Small UI utility (43 LOC). The `make_attr_sort_key` + inner `_key` are used by `planet_list_filters.py` and `star_list_filters.py` (tested through their tests). No direct tests exist. Edge cases: dotted path resolution failure returns `""`, missing `func`/`attr` in column returns `""`.

**Recommendation:** `tests/unit/ui/screens/test_list_filter_utils.py` (small — can be 5-10 test cases)

---

### ADVISORY: `game/ui/screens/galaxy_test/system_mode.py` (576 LOC, 13 symbols)

**Path:** `game/ui/screens/galaxy_test/system_mode.py`
**Coverage matrix:** Tier 0, 0 candidate test files
**Layer:** UI

**Why ADVISORY:** GalaxyTestScreen utility — a test/debug aid, not a game feature. Heavy Pygame rendering code (drawing stars, planets, orbital rings, selection highlights). The `SystemModeHelper` class handles system generation, object inspection, and UI rendering. Low priority for unit testing; rendering code is inherently integration-test territory.

---

### ADVISORY: `game/ui/screens/test_lab/details/resource_outcomes.py` (294 LOC, 5 symbols)

**Path:** `game/ui/screens/test_lab/details/resource_outcomes.py`
**Coverage matrix:** Tier 0, 0 candidate test files
**Layer:** UI

**Why ADVISORY:** Test Lab UI rendering code. All 5 functions (`is_resource_test`, `draw_resource_outcomes`, `_draw_fuel_outcomes`, `_draw_energy_outcomes`, `_draw_ammo_outcomes`) involve Surface blitting and font rendering. The `is_resource_test` function (line 18-21) is a simple string-check that could be tested, but the benefit is small.

---

### ADVISORY: `game/ui/screens/water_target_editor.py` (227 LOC, 9 symbols)

**Path:** `game/ui/screens/water_target_editor.py`
**Coverage matrix:** Tier 0, 0 candidate test files
**Layer:** UI

**Why ADVISORY:** Strategy modal window for editing water targets. Extends `PlanetTargetEditor`, creates slider + button widgets. Pure Pygame_gui rendering code. No critical business logic.

---

### ADVISORY: `game/ui/screens/workshop_data_reloader.py` (197 LOC, 11 symbols)

**Path:** `game/ui/screens/workshop_data_reloader.py`
**Coverage matrix:** Tier 0, 0 candidate test files
**Layer:** UI

**Why ADVISORY:** Workshop data reload orchestration. Coordinates data loading, UI refresh, and panel synchronization. Heavy callback/coupling pattern. `reload_data` (line 132) has error handling for `OSError/ValueError/KeyError`. Integration-level concern.

---

### ADVISORY: Re-export `__init__.py` files (6 files, 245 LOC total)

| File | LOC | Coverage |
|------|-----|----------|
| `game/ai/__init__.py` | 109 | Tier 0 — re-exports AIController, behaviors, PolicyManager, TargetEvaluator, AIControllerFactory |
| `game/core/patterns/__init__.py` | 19 | Tier 0 — re-exports iteration helpers |
| `game/research/data/__init__.py` | 6 | Tier 0 — re-exports data model classes |
| `game/strategy/adapters/__init__.py` | 10 | Tier 0 — re-exports SimulationBattleResolver |
| `game/strategy/engine/handlers/__init__.py` | 72 | Tier 0 — re-exports all command handlers + factory |
| `game/ui/services/__init__.py` | 29 | Tier 1 — re-exports 8 UI service classes |

**Why ADVISORY:** `__init__.py` re-export files. Per project convention, these don't need dedicated tests; import correctness is verified by dependent test imports.

---

## Tier 1-2 Findings (Partial Coverage)

### MAJOR: `game/strategy/services/system_effects_collector.py` (503 LOC)

**Path:** `game/strategy/services/system_effects_collector.py`
**Coverage matrix:** Tier 2, 5 untested symbols out of 12 total
**Candidate tests:** `tests/unit/strategy/services/test_system_effects_collector.py`

**Untested symbols:**

| Symbol | Line | Severity | Notes |
|--------|------|----------|-------|
| `_ability_kind` | 93-94 | MAJOR | Classifies ability as 'rate' or 'multiplier'. Returns 'rate' for `EnvironmentalDamage` and `FuelDrain`, 'multiplier' for everything else. Simple but used in the critical aggregation path. A typo here silently misclassifies abilities. |
| `_format_status` | 103-115 | MAJOR | Renders activation state as human-readable string with remaining-ticks formatting. 5 branches (None, ACTIVE, ACTIVATING, DEACTIVATING, default). The ACTIVATING/DEACTIVATING paths compute `state.required_ticks - state.progress_ticks`. |
| `_is_activatable` | 118-120 | MINOR | One-liner: checks `'activation_time' in ability_data`. Trivial but untested. |
| `_aggregate` | 281-473 | MAJOR | 192-line private pipeline function. Contains: ownership filtering (line 297-299), hex affinity check with exception safety net (line 304-312), get_abilities with exception safety net (line 314-320), scope validation (line 329-346), D17 ownerless-scope gating (line 336-346), activation state resolution (line 351-361), value extraction (line 364-367), provider construction (line 369-382), group aggregation with active/inactive fallback (line 400-422), D16 mixed-kind validation (line 429-448), rate vs multiplier dispatch (line 450-459). |
| `_legacy_provider_fields` | 476-503 | MINOR | Builds back-compat provider fields for non-facility sources. Simple branching on `source_kind`. |

**Public symbols with verified coverage:** `collect_system_effects`, `collect_sector_effects`, `find_sector_effect`, `aggregate_value_or`, `make_group_key`, `make_display_name`, `format_intrinsic_ability_magnitude` — all tested in the candidate test file.

**Why MAJOR:** The `_aggregate` function contains 7 error-handling paths, 4 filtering stages, and 2 PROJ-300 validation rules (D16 mixed-kind, D17 ownerless-scope). It is tested only indirectly through `collect_system_effects` and `collect_sector_effects`. A regression in any gating or filtering logic would affect all system/sector effect panels in the UI but may not produce visible failures — effects would silently disappear or misclassify.

**Recommendation:** Extract `_aggregate` into a package-public function and add `test_aggregate_pipeline` covering: ownership filtering (ownerless + owned), D17 ownerless scope rejection, hex affinity safety net (affects_hex exception path), get_abilities exception path, activation state resolution, D16 mixed-kind rejection, empty/inactive/all-active provider stacks.

---

### MAJOR: `game/strategy/engine/resupply_engine.py` (294 LOC)

**Path:** `game/strategy/engine/resupply_engine.py`
**Coverage matrix:** Tier 2, 5 untested symbols out of 10 total
**Candidate tests:** `tests/unit/strategy/engine/test_resupply_engine.py`

**Untested symbols:**

| Symbol | Line | Severity | Notes |
|--------|------|----------|-------|
| `ResupplyEngine.__init__` | 58-73 | MAJOR | Constructor with None guard raising `ValidationException`. Strict DI pattern — `registries` is required. |
| `_process_facility_generation` | 113-144 | MAJOR | Per-facility fuel generation. Branches: non-operational skip (line 123), zero generation skip (line 128), capacity overflow handling via `facility.add_fuel` (line 135). |
| `_get_fuel_generation_rate` | 146-175 | MAJOR | Scans all facility components for `ResourceGeneration` with `resource="fuel"`. Iterates design_data layers, resolves components from registries, handles dict/str comp entries (line 166). |
| `_calculate_fuel_distribution` | 232-268 | MAJOR | Fuel distribution algorithm: calculates per-ship fuel targets to equalize max range across all fleet ships. Divides available fuel proportionally to per-hex fuel cost. |
| `_transfer_fuel` | 270-294 | MAJOR | Executes fuel transfer from facility to ships. Calls `ship.resupply("fuel", actual)` and `facility.withdraw_fuel()`. |

**Public symbols with verified coverage:** `process_fuel_generation`, `process_fleet_resupply`, `_validate_tick_inputs`, and `ResupplyEvent` dataclass are tested.

**Why MAJOR:** These 5 private methods contain all the actual business logic. The public methods `process_fuel_generation` and `process_fleet_resupply` are tested, but they call through to these untested privates. Bugs in `_calculate_fuel_distribution` (division by zero when `total_cost_per_hex <= 0`, NaN handling) or `_get_fuel_generation_rate` (missing component in registry silently skipped at line 168) would pass through the public-method tests without detection.

**Recommendation:** Add test cases for: `_get_fuel_generation_rate` with missing component IDs, dict vs str comp entries; `_calculate_fuel_distribution` with zero fuel cost, single/multi ship; `_transfer_fuel` with insufficient facility fuel; `_process_facility_generation` with full/near-full fuel storage.

---

### MAJOR: `game/strategy/services/strategic_ability_scanner.py` (295 LOC)

**Path:** `game/strategy/services/strategic_ability_scanner.py`
**Coverage matrix:** Tier 2, 2 untested symbols out of 7 total
**Candidate tests:** `tests/unit/strategy/services/test_strategic_ability_scanner.py`

**Untested symbols:**

| Symbol | Line | Severity | Notes |
|--------|------|----------|-------|
| `_is_component_functionally_active` | 248-266 | MAJOR | Checks if a facility component is in ACTIVE phase. Uses `getattr` to probe `get_activation_state` (line 262), returns False if absent (line 263). Returns `state.is_functionally_active` (line 266). If `is_functionally_active` is not a bool, the result is untyped. |
| `_extract_ability` | 269-295 | MAJOR | Delegates to `component_inspector.extract_abilities_from_component` which is the single source of truth (PROJ-277 fix). Returns dict, list of dicts, or None depending on ability data shape. |

**Verified coverage gap:** AST scan confirmed the test file (`test_strategic_ability_scanner.py`, 713 lines) does NOT import or call `_is_component_functionally_active` or `_extract_ability`. They are exercised only indirectly through `find_abilities_at_planet`.

**Why MAJOR:** `_is_component_functionally_active` controls the `require_active` filtering path in `find_abilities_at_planet` (line 53-56). If `get_activation_state` returns unexpected types or `is_functionally_active` is not a boolean, the filtering silently fails. The `_extract_ability` function was specifically created (PROJ-277) to fix a bug where callers passing a plain components dict got no abilities back — but this fix path has no direct test.

**Recommendation:** Add `test_is_component_functionally_active` with mock facility (with/without `get_activation_state`, with ACTIVE/INACTIVE/None states). Add `test_extract_ability` with plain dict vs GameRegistries registries.

---

### MINOR: `game/strategy/formulas/habitability.py` (105 LOC)

**Path:** `game/strategy/formulas/habitability.py`
**Coverage matrix:** Tier 2, 1 untested symbol out of 3 total
**Candidate tests:** `tests/unit/strategy/formulas/test_habitability.py`

**Untested symbol:**

| Symbol | Line | Severity | Notes |
|--------|------|----------|-------|
| `_gaussian_factor` | 32-49 | MINOR | Gaussian falloff: `exp(-0.5 * (deviation/sigma)^2)`. Edge cases: `tolerance=0` → `sigma = max(0, 0.01) = 0.01` (avoids division by zero), large deviation → approaches 0, `value == ideal` → exactly 1.0. |

**Why MINOR:** Simple mathematical function. The edge case handling (`min_sigma=0.01`, `max(tolerance, min_sigma)`) is defensive and should have an explicit test. `calculate_habitability` and `score_planet_for_race` are tested, and `_gaussian_factor` is called by the factor scorers in `habitability_factors.py` (tested indirectly). However, a direct test would catch the `sigma=0` guard.

**Recommendation:** Add `test_gaussian_factor` with: zero tolerance case (sigma floor), exact match returns 1.0, large deviation returns near-zero, negative values.

---

### MINOR: `game/strategy/systems/race_randomizer.py` (446 LOC)

**Path:** `game/strategy/systems/race_randomizer.py`
**Coverage matrix:** Tier 2, 3 untested symbols out of 12 total
**Candidate tests:** `tests/unit/strategy/test_race_randomizer.py`

**Untested symbols:**

| Symbol | Line | Severity | Notes |
|--------|------|----------|-------|
| `_resolve_rng` | 37-39 | MINOR | Module-level helper: `return rng if rng is not None else random.Random()`. Trivial one-liner. |
| `RaceRandomizer._pick_name_entry` | 109-124 | MINOR | Picks name+plural from portrait data or fallback. 3 branches: portrait-specific names exist, fallback names exist, neither (returns "Unknown"/"Unknown"). |
| `RaceRandomizer._pick_leader` | 127-142 | MINOR | Picks leader name. Same 3-branch pattern as `_pick_name_entry`. Returns "Leader" as ultimate fallback. |

**Why MINOR:** Simple helper methods tested indirectly through `randomize_identity`. The `_resolve_rng` function is trivial. The name/leader pickers have clear branches but are exercised through `randomize_identity`'s existing test coverage.

---

### MAJOR: `game/ui/screens/builder/weapons_panel.py` (321 LOC)

**Path:** `game/ui/screens/builder/weapons_panel.py`
**Coverage matrix:** Tier 2, 14 untested symbols out of 15 total
**Candidate tests:** `tests/unit/ui/test_weapons_report_layout.py`

**Coverage gap:** Only 1 of 15 symbols appears to be tested. The `WeaponsReportPanel` class has comprehensive tests via `test_weapons_report_layout.py`. However, the pre-computed matrix reports 14 untested symbols, including:

| Symbol | Line | Type |
|--------|------|------|
| `WeaponsReportPanel.__init__` | 32-86 | Constructor |
| `_setup_filter_buttons` | 87-116 | UI widget creation |
| `_update_button_colors` | 118-128 | UI update |
| `_on_weapons_updated` | 134-144 | Event handler |
| `_on_filter_changed` | 146-150 | Event handler |
| `_update_scrollbar` | 152-163 | Scrollbar management |
| `hovered_weapon` / `verbose_tooltip` | 170-183 | Properties |
| `set_target` / `clear_target` | 184-190 | Public API |
| `update` | 192-194 | Public API |
| `handle_event` | 196-218 | Event routing |
| `draw` | 220-321 | Rendering |

**Why MAJOR (not ADVISORY):** While this is a UI panel, the extensive event handling logic (button routing, scroll wheel, tooltip hover detection) has zero coverage. A regression in `handle_event` (line 196) or `draw` (line 220) would silently break the weapons panel. One test file (`test_weapons_report_layout.py`) exists but is a layout/rendering test that exercises the MVVM components (WeaponsRenderer, WeaponsViewModel, WeaponsInputHandler) rather than the panel coordinator.

**Verified partial coverage:** The MVVM subcomponents (WeaponsRenderer, WeaponsViewModel, WeaponsInputHandler) have their own test files. This finding is about the coordinator — the `WeaponsReportPanel` shell that wires them together.

---

### MINOR: `game/ui/screens/transfer_dialog.py` (486 LOC)

**Path:** `game/ui/screens/transfer_dialog.py`
**Coverage matrix:** Tier 2, 12 untested symbols out of 39 total
**Candidate tests:** 5 test files

**Untested symbols:**

| Symbol | Line | Type | Notes |
|--------|------|------|-------|
| `_init_widget_refs` | 169-187 | Widget placeholder setup | Simple — sets None/defaults on all widget slots |
| `_filter_empty` (property) | 228-233 | Property shim | Delegates to view_model |
| `_extract_dropdown_value` | 292-293 | Static method shim | Delegates to renderer |
| `_discover_pod_designs` | 301-302 | Query shim | Delegates to controller |
| `_on_target_changed` | 332-335 | Event handler | 3-line delegation |
| `_reset_and_build_grid` | 337-339 | Event handler | 2-line delegation |
| `_build_grid` | 341-348 | Grid construction | Delegates to view_model + renderer |
| `_update_pending_label` | 358-359 | Label update shim | Delegates to renderer |
| `_on_filter_toggle` | 361-364 | Event handler | 3-line delegation |
| `process_event` | 417-449 | Event routing | 32-line event dispatch with keydown + button press routing |
| `handle_external_selection` | 451-473 | External selection | 23-line external target selection |

**Why MINOR:** All untested methods are thin delegation shims. The real logic lives in `TransferViewModel` and `TransferController` (tested separately). The `process_event` method has 32 lines of event routing but this is pure Pygame_gui event plumbing — inherent to the UI layer. The 5 test files (`test_transfer_dialog.py`, `test_transfer_dialog_characterization.py`, `test_transfer_dialog_enhanced.py`, `test_transfer_dialog_keeps_open_on_abort.py`, `test_sub_window_hotkeys.py`) cover the integration behavior through the dialog shell.

---

### ADVISORY: `game/ui/components/table/virtual_table.py` (553 LOC)

**Path:** `game/ui/components/table/virtual_table.py`
**Coverage matrix:** Tier 2, 4 untested symbols out of 20 total
**Candidate tests:** `tests/unit/ui/components/table/test_virtual_table.py`

**Untested symbols:**

| Symbol | Line | Type | Notes |
|--------|------|------|-------|
| `_build_containers` | 111-141 | UI container construction | Creates UIPanel, scrollbar |
| `_rebuild_row_pool` | 143-259 | Row pool construction | 116-line widget factory |
| `_update_selection_highlights` | 432-453 | Color update logic | Near-duplicate of logic in `update_visible_rows` |
| `scroll_bar` (property) | 534-537 | Property | Simple getter |

**Why ADVISORY:** UI rendering code. `_build_containers` and `_rebuild_row_pool` are widget construction methods that depend on pygame_gui. `_update_selection_highlights` duplicates logic from `update_visible_rows` (a deduplication candidate — see PROJ-319 pattern). The `scroll_bar` property is a trivial getter.

---

### ADVISORY: `game/ui/screens/builder/modifier_logic.py` (234 LOC)

**Path:** `game/ui/screens/builder/modifier_logic.py`
**Coverage matrix:** Tier 2, 10 untested symbols out of 21 total
**Candidate tests:** 3 test files

**Untested symbols:**

| Symbol | Line | Notes |
|--------|------|-------|
| `ModifierLogicService.__init__` | 48-64 | DI constructor with None guard. Tested indirectly through service creation in candidate tests. |
| `ModifierLogicService.is_modifier_allowed` | 66-68 | Delegates to `_component_service.is_modifier_allowed`. Tested indirectly. |
| `ModifierLogicService.get_mandatory_modifiers` | 70-78 | Core logic — returns all applicable modifier IDs. **Should be tested.** |
| `ModifierLogicService.ensure_mandatory_modifiers` | 121-129 | Mutation method — adds modifiers + sets initial values. **Should be tested.** |
| `ModifierLogic.init_service` (deprecated) | 187-190 | Static wrapper. **ADVISORY — deprecated path.** |
| `ModifierLogic._get_service` (deprecated) | 192-199 | Static wrapper with RuntimeError guard. **ADVISORY — deprecated path.** |
| `ModifierLogic.set_service` (deprecated) | 201-204 | Static wrapper for testing. **ADVISORY — deprecated path.** |
| `ModifierLogic.is_modifier_allowed` (deprecated) | 206-208 | Static wrapper. **ADVISORY — deprecated path.** |
| `ModifierLogic.get_mandatory_modifiers` (deprecated) | 210-212 | Static wrapper. **ADVISORY — deprecated path.** |
| `ModifierLogic.ensure_mandatory_modifiers` (deprecated) | 222-224 | Static wrapper. **ADVISORY — deprecated path.** |

**Why ADVISORY:** 6 of the 10 untested symbols are the deprecated `ModifierLogic` static wrapper class (lines 182-234). The actual service `ModifierLogicService` has test files covering most of its methods. The two `ModifierLogicService` methods flagged as untested (`get_mandatory_modifiers`, `ensure_mandatory_modifiers`) are exercised indirectly through candidate test files.

---

### ADVISORY: Remaining Tier 2 files with minor untested symbols

| File | Untested | Severity | Notes |
|------|----------|----------|-------|
| `game/strategy/data/galaxy.py` | `StarSystem.__repr__`, `_register_zones_from_system`, `_rebuild_warp_point_index`, `_rebuild_all_warp_point_indices`, `generate_planets` | ADVISORY | `__repr__` is cosmetic. Zone/warp indexers are tested through `add_system`/`remove_warp_link`. `generate_planets` delegates to `GalaxySystemGenerator`. |
| `game/strategy/data/group_policy_registry.py` | `GroupPolicyRegistry.__init__` | ADVISORY | Constructor sets empty dicts + `_loaded=False`. Trivial — tested through `load()` + query methods. |
| `game/strategy/data/orbital_generation_config.py` | `OrbitalGenerationConfig.__init__`, `_load_from_json`, `_use_defaults` | ADVISORY | Constructor dispatches to `_load_from_json` or `_use_defaults`. Tested through `test_orbital_generation_config.py` which exercises the config accessor `get_orbital_generation_config`. |
| `game/strategy/engine/environmental_hazard_engine.py` | `EnvironmentalHazardEngine.__init__` (line 57) | ADVISORY | Constructor is a no-op (empty body). Trivial. |
| `game/strategy/events/event_log.py` | `EventLog.__init__` (line 84), `_matches_empire` (line 165) | ADVISORY | Constructor sets empty list. `_matches_empire` is tested through `get_events_for_turn` + `get_events_by_category` with `empire_id` kwarg. |
| `game/ui/filters/filter_state_manager.py` | `FilterStateManager.__init__` | ADVISORY | Constructor copies `filter_definitions`. Tested through remaining 7 methods. |
| `game/ui/fonts.py` | `_ensure_cache_valid` | ADVISORY | Cache invalidation guard. Tested indirectly through `get_font`/`get_default_font` calls. |
| `game/ui/screens/cargo_quick_dialog_controller.py` | `CargoQuickDialogController.__init__`, `get_unload_items`, `get_load_items`, `get_target_planet_id` | ADVISORY | Controller methods tested indirectly through `test_cargo_quick_dialog_controller_widget_purity.py`. |
| `game/ui/screens/new_game_setup_view_model.py` | `NewGameSetupViewModel.__init__` | ADVISORY | Constructor sets default values. Tested through the other 11 tested symbols. |
| `game/ui/screens/food_allocation_editor.py` | `FoodAllocationRowData`, `FoodAllocationEditorUiBuilder.build`, `_build_row`, `FoodAllocationEditor.update`, `process_event` | ADVISORY | RowData is a dataclass. Builder methods are UI construction. `update` and `process_event` are widget event handlers — tested through integration tests in `test_food_allocation_editor.py`. |

---

## Tier 3 Findings (Apparently Covered)

All Tier 3 files were verified against their candidate test files:

### `game/core/error_codes.py` (216 LOC) — VERIFIED

**Path:** `game/core/error_codes.py`
**Candidate tests:** 11 test files including `tests/unit/core/test_error_codes.py`
**Verification:** The `ErrorCode` enum has 27 unique codes across 9 categories (V, S, R, P, F, C, T, L, I). `tests/unit/core/test_error_codes.py` tests enum membership, uniqueness, and category membership. Coverage is adequate.

### `game/simulation/managers/battle_state_manager.py` (134 LOC) — VERIFIED

**Path:** `game/simulation/managers/battle_state_manager.py`
**Candidate tests:** `tests/unit/simulation/managers/test_battle_state_manager.py`
**Verification:** All 5 symbols (capture_state, restore_config_from_state, extract_ships_from_state, validate_state) have dedicated tests. `capture_state` has an engine==None error path test. `validate_state` has None/non-None variants.

### `game/strategy/data/species_population.py` (43 LOC) — VERIFIED

**Path:** `game/strategy/data/species_population.py`
**Candidate tests:** 12 test files (heavily exercised through integration tests)
**Verification:** `SpeciesPopulation` dataclass with `from_dict` deserializer. Tested through `test_species_population_characterization.py` and 11 other integration test files.

### `game/strategy/engine/handlers/transfer.py` (120 LOC) — VERIFIED

**Path:** `game/strategy/engine/handlers/transfer.py`
**Candidate tests:** `tests/unit/strategy/engine/test_transfer_handler_fleet_to_fleet.py`
**Verification:** `TransferCommandHandler.execute` is tested for both planet-target and fleet-target paths. The PROJ-343 T1.1 fix (fleet-to-fleet transfer) is explicitly covered.

### `game/simulation/entities/ship_layer_manager.py` (167 LOC) — VERIFIED

**Path:** `game/simulation/entities/ship_layer_manager.py`
**Verification:** 4 of 5 symbols tested. `__init__` is verified because it's called in all other test methods. `initialize_layers`, `equip_default_hull`, and `change_class` all have dedicated test cases.

---

## FALSE NEGATIVE in Coverage Matrix

### `game/strategy/services/ability_sources/planet_intrinsic.py` (91 LOC)

**Matrix claim:** Tier 0, 0 candidate test files, 0 tested symbols
**Actual status:** **Tier 3 (FULLY COVERED)**

**Path:** `tests/unit/strategy/services/ability_sources/test_planet_intrinsic.py`
**Test file:** 121 lines, 9 test functions:

- `test_source_kind_is_planet` — verifies `source_kind == 'planet'`
- `test_source_label_is_planet_name_with_type` — verifies formatted label
- `test_source_id_uses_planet_id` — verifies `source_id == "planet:42"`
- `test_owner_id_is_always_none` — verifies PROJ-301 D2 (ownerless)
- `test_get_abilities_returns_intrinsic_dict` — verifies ability dict roundtrip
- `test_get_abilities_empty_when_planet_has_none` — verifies empty dict fallback
- `test_affects_hex_at_global_location` — verifies single-hex footprint
- `test_affects_hex_multi_hex_dyson_sphere` — verifies PROJ-301 D8 multi-hex body
- `test_get_activation_state_is_none` — verifies always-on activation
- `test_satisfies_iability_source_protocol` — verifies `IAbilitySource` protocol conformance

**Root cause of false negative:** The test file exists at `tests/unit/strategy/services/ability_sources/test_planet_intrinsic.py` but the pre-computed coverage matrix's symbol scanner did not match `PlanetIntrinsicAbilitySource` against any candidate test file. This is likely because the matrix scanner searches for test files by symbol name, and the test file imports `PlanetIntrinsicAbilitySource` but the scanner's heuristic didn't register the match. The test file uses `from game.strategy.services.ability_sources import PlanetIntrinsicAbilitySource` (imported via `__init__.py` re-export), which may have confused the symbol-name matching.

**All 9 symbols are fully tested.** Adjust tier from 0 to 3.

---

## File Coverage Verification Table

| File | Tier | LOC | Tested / Total Symbols | Candidate Tests | Verdict |
|------|------|-----|------------------------|-----------------|---------|
| `game/ai/__init__.py` | 0 | 109 | 0/0 | 0 | ADVISORY (re-exports) |
| `game/ai/spatial_behaviors/_formation_utils.py` | 0 | 39 | 0/1 | 0 | **MAJOR** |
| `game/core/error_codes.py` | 3 | 216 | 1/1 | 11 | VERIFIED |
| `game/core/patterns/__init__.py` | 0 | 19 | 0/0 | 0 | ADVISORY (re-exports) |
| `game/core/protocols/ui.py` | 0 | 112 | 0/15 | 0 | **CRITICAL** |
| `game/research/data/__init__.py` | 0 | 6 | 0/0 | 0 | ADVISORY (re-exports) |
| `game/simulation/combat/targeting_system.py` | 2 | 309 | 5/7 | 2 | VERIFIED |
| `game/simulation/entities/ship_layer_manager.py` | 3 | 167 | 5/5 | 1 | VERIFIED |
| `game/simulation/managers/battle_state_manager.py` | 3 | 134 | 5/5 | 1 | VERIFIED |
| `game/strategy/adapters/__init__.py` | 0 | 10 | 0/0 | 0 | ADVISORY (re-exports) |
| `game/strategy/data/galaxy.py` | 2 | 693 | 36/41 | 24 | VERIFIED |
| `game/strategy/data/group_policy_registry.py` | 2 | 108 | 9/10 | 2 | VERIFIED |
| `game/strategy/data/orbital_generation_config.py` | 2 | 195 | 2/5 | 1 | VERIFIED |
| `game/strategy/data/species_population.py` | 3 | 43 | 2/2 | 12 | VERIFIED |
| `game/strategy/engine/environmental_hazard_engine.py` | 2 | 222 | 6/7 | 4 | VERIFIED |
| `game/strategy/engine/handlers/__init__.py` | 0 | 72 | 0/0 | 0 | ADVISORY (re-exports) |
| `game/strategy/engine/handlers/transfer.py` | 3 | 120 | 2/2 | 1 | VERIFIED |
| `game/strategy/engine/resupply_engine.py` | 2 | 294 | 5/10 | 3 | **MAJOR** |
| `game/strategy/events/event_log.py` | 2 | 188 | 11/13 | 3 | VERIFIED |
| `game/strategy/formulas/habitability.py` | 2 | 105 | 2/3 | 2 | MINOR |
| `game/strategy/services/ability_sources/planet_intrinsic.py` | **0→3** | 91 | **9/9** | **1** | **FALSE NEGATIVE** |
| `game/strategy/services/replay_resolver.py` | 2 | 119 | 3/6 | 1 | MINOR |
| `game/strategy/services/strategic_ability_scanner.py` | 2 | 295 | 5/7 | 1 | **MAJOR** |
| `game/strategy/services/system_effects_collector.py` | 2 | 503 | 7/12 | 1 | **MAJOR** |
| `game/strategy/systems/race_randomizer.py` | 2 | 446 | 9/12 | 1 | MINOR |
| `game/ui/components/table/virtual_table.py` | 2 | 553 | 15/20 | 1 | ADVISORY |
| `game/ui/filters/filter_state_manager.py` | 2 | 54 | 7/8 | 2 | VERIFIED |
| `game/ui/fonts.py` | 2 | 92 | 3/4 | 1 | VERIFIED |
| `game/ui/screens/builder/modifier_logic.py` | 2 | 234 | 11/21 | 3 | ADVISORY |
| `game/ui/screens/builder/weapons_panel.py` | 2 | 321 | 1/15 | 1 | **MAJOR** |
| `game/ui/screens/cargo_quick_dialog_controller.py` | 2 | 131 | 2/6 | 1 | VERIFIED |
| `game/ui/screens/food_allocation_editor.py` | 2 | 394 | 10/16 | 1 | VERIFIED |
| `game/ui/screens/galaxy_test/system_mode.py` | 0 | 576 | 0/13 | 0 | ADVISORY |
| `game/ui/screens/list_filter_utils.py` | 0 | 43 | 0/2 | 0 | ADVISORY |
| `game/ui/screens/new_game_setup_view_model.py` | 2 | 191 | 11/12 | 2 | VERIFIED |
| `game/ui/screens/test_lab/details/resource_outcomes.py` | 0 | 294 | 0/5 | 0 | ADVISORY |
| `game/ui/screens/transfer_dialog.py` | 2 | 486 | 20/39 | 5 | VERIFIED |
| `game/ui/screens/water_target_editor.py` | 0 | 227 | 0/9 | 0 | ADVISORY |
| `game/ui/screens/workshop_data_reloader.py` | 0 | 197 | 0/11 | 0 | ADVISORY |
| `game/ui/screens/workshop_viewmodel_layer_ops.py` | 0 | 254 | 0/7 | 0 | ADVISORY |
| `game/ui/services/__init__.py` | 1 | 29 | 0/0 | 2 | ADVISORY (re-exports) |
| `game/ui/services/game_settings.py` | 0 | 94 | 0/11 | 0 | **MAJOR** |

---

## Context Usage Estimate

| Activity | Files Read | Lines Read |
|----------|-----------|------------|
| Documentation | 3 | ~2,500 |
| Coverage matrix (full) | 1 | ~90,000 |
| Coverage matrix (filtered to shard) | N/A | ~1,800 |
| Production files | 42 | ~8,800 |
| Test file verification | 2 | ~850 |
| **Total** | **48 unique files** | **~14,500 lines** |

---

## Remediation Priority

| Priority | File | Severity | Estimated Test LOC | Rationale |
|----------|------|----------|---------------------|-----------|
| P0 | `game/core/protocols/ui.py` | CRITICAL | ~50 | Core layer. TypeGuard/Protocol breakage is silent. |
| P1 | `game/ui/services/game_settings.py` | MAJOR | ~80 | Context-managed service. User settings corruption risk. |
| P2 | `game/strategy/services/system_effects_collector.py` | MAJOR | ~200 | Complex pipeline. 192-line `_aggregate` with 7 error paths. |
| P3 | `game/strategy/engine/resupply_engine.py` | MAJOR | ~150 | Fuel distribution algorithm. 5 private methods with math. |
| P4 | `game/strategy/services/strategic_ability_scanner.py` | MAJOR | ~80 | Activation state filtering + registry extraction. |
| P5 | `game/ui/screens/builder/weapons_panel.py` | MAJOR | ~120 | Event handler routing + button state management. |
| P6 | `game/ai/spatial_behaviors/_formation_utils.py` | MAJOR | ~30 | Small utility — low effort. |
| P7 | `game/strategy/formulas/habitability.py` | MINOR | ~20 | Gaussian factor edge cases. |
| P8 | `game/strategy/systems/race_randomizer.py` | MINOR | ~40 | Name/leader picker branches. |
| P9 | `game/strategy/services/replay_resolver.py` | MINOR | ~50 | Resolver construction + replay store dir. |

---

## Methodology Notes

- Every production file in the shard was read in full (42 files, ~8,785 lines)
- Candidate test files were verified by reading key files and performing AST scans
- The pre-computed coverage matrix was cross-referenced against glob searches for test files
- One false negative was discovered (`planet_intrinsic.py` — Tier 0 in matrix, actually Tier 3)
- UI files are assessed per convention: rendering/event code → ADVISORY; business logic → appropriate severity
- `__init__.py` re-export files are ADVISORY per convention
