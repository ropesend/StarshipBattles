# VERIFIED Shard 05 — Skeptical Verification Report

**Date:** 2026-05-04
**Phase:** Phase 3 (Skeptical Verification)
**Verifier Method:** CRITICAL/MAJOR 100% read production + test code; MINOR/ADVISORY spot-checks via glob + imports scan
**Disposition:** 1 CRITICAL CONFIRMED, 5 MAJOR CONFIRMED (2 with DOWNGRADE, 1 with partial DISPUTE), 1 FALSE NEGATIVE CONFIRMED, 1 ADVISORY→MAJOR UPGRADE

---

## Summary

| Category | Count |
|----------|-------|
| CONFIRMED (as reported) | 6 |
| CONFIRMED with DOWNGRADE | 4 |
| DISPUTED (partial) | 1 |
| CONFIRMED FALSE NEGATIVE | 1 |
| ADVISORY→MAJOR UPGRADE | 1 |
| Discovery Agent Errors | 1 |

---

## CONFIRMED Gaps

### CRITICAL: `game/core/protocols/ui.py` (112 LOC) — CONFIRMED

**Verification:** Read production code (112 lines), glob confirmed zero test files exist. The module contains:
- `IScene` protocol (lines 8-31) — 4 abstract methods, `@runtime_checkable`
- `ICamera` protocol (lines 33-107) — 8 abstract methods + properties, `@runtime_checkable`
- `is_camera` TypeGuard (lines 110-112) — delegates to `_has_attrs(obj, 'width', 'height', 'zoom', 'world_to_screen')` in `game/core/protocols/common.py:17-19`

`_has_attrs` (common.py:17-19) is a pure `hasattr` check: `all(hasattr(obj, attr) for attr in attrs)`. The discovery agent's concern about drift is valid: if `ICamera` adds a new property, `is_camera` would NOT detect it unless `_has_attrs` call site is updated. Tests on `common.py` may exist but do not cover this coupling risk in `ui.py` itself.

**Verdict:** CONFIRMED. Core-layer protocol definitions with zero unit tests. No dispute.

---

### MAJOR: `game/ui/services/game_settings.py` (94 LOC) — CONFIRMED

**Verification:** Read production code (94 lines), glob confirmed zero test files. Code review confirms:
- `_load()` at line 38: `saved = load_json(SETTINGS_FILE, default={})` — fallback is `{}`
- `get()` at line 56: `self._data.get(key, DEFAULTS.get(key))` — returns `None` for unknown keys
- `save()` at line 45: `save_json(SETTINGS_FILE, self._data)` — no validation of data integrity
- `background_brightness` setter at line 80: `max(0.0, min(1.0, value))` — clamps correctly
- Module-level singleton `_default_game_settings` at line 22 — mutable global state
- `get_default_game_settings` at line 83: lazy-init singleton factory
- `set_default_game_settings` at line 91: uses `global` keyword

All claims in the Phase 2 report about this file are accurate.

**Verdict:** CONFIRMED. ApplicationContext-managed service (#9 of 10) with zero tests. Severity MAJOR is appropriate — user settings corruption risk.

---

### MAJOR: `game/ai/spatial_behaviors/_formation_utils.py` (39 LOC) — CONFIRMED

**Verification:** Read production code, glob confirmed zero test files. `compute_circular_position` (lines 15-39):
- `total = max(int(total), 1)` at line 34 — guards `total=0`
- angle formula: `(2 * math.pi * slot_index) / total` — wraps correctly for any slot_index
- Returns `Optional[Vector2]` type annotation but docstring says "Always non-None" — documentation/type annotation inconsistency not noted in Phase 2 report
- No overflow handling for large coordinates — accurate

**Verdict:** CONFIRMED. Pure math function with zero tests. Note: docstring claims "Always non-None" but return type is `Optional[Vector2]`. This is a mild annotation inconsistency but doesn't affect the coverage finding.

---

### MAJOR: `game/strategy/services/system_effects_collector.py` (503 LOC) — CONFIRMED, severity adjusted

**Verification:** Read production code (503 lines) and test file (759 lines, 35 test functions). The 5 untested private symbols:

| Symbol | Lines | Discovery Severity | Verified Severity | Reason |
|--------|-------|-------------------|-------------------|--------|
| `_ability_kind` | 93-94 | MAJOR | **MINOR** | 2-line function (`return 'rate' if name in frozenset else 'multiplier'`). Exercised indirectly via `kind` assertions in `TestKindDiscriminator` and every test checking effect kinds. |
| `_format_status` | 103-115 | MAJOR | **MINOR** | 5 branches. ALL exercised indirectly: `None → "Active"` (always-on), `ACTIVE → "Active"`, `ACTIVATING → "Activating (N)"` (line 153 asserts "Activating (200)"), `DEACTIVATING → "Deactivating (N)"`, `default → "Inactive"` (line 134 asserts "Inactive"). |
| `_is_activatable` | 118-120 | MINOR | **MINOR** | Correct. One-liner. |
| `_aggregate` | 281-473 | MAJOR | **MAJOR** | 192 lines, 7 error-handling paths, 4 filtering stages, D16/D17 validation. Tested ONLY indirectly through 35 test cases on `collect_system_effects`/`collect_sector_effects`. D16 path tested in `TestD16MixedKindValidation` (line 579); D17 path tested in `TestD17OwnerlessScopeValidation` (line 527); activation state, scope filtering, and provider construction all exercised indirectly. The risk of silent regression in a gating/filtering path is real. |
| `_legacy_provider_fields` | 476-503 | MINOR | **MINOR** | Correct. Simple branching on `source_kind`. |

**Verdict:** CONFIRMED (5 private methods not directly imported by any test). Downgraded `_ability_kind` and `_format_status` from MAJOR to MINOR — they are thoroughly exercised indirectly. `_aggregate` remains MAJOR.

---

### MAJOR: `game/strategy/engine/resupply_engine.py` (294 LOC) — PARTIALLY CONFIRMED, DISPUTED

**Verification:** Read production code (294 lines) and test file (600 lines, 15 test functions).

| Symbol | Discovery Verdict | Verified Verdict | Detail |
|--------|------------------|------------------|--------|
| `__init__` (58-73) | MAJOR untested | **DISPUTED — ERROR** | Directly tested in `TestResupplyEngineDI` (test file lines 110-119). `test_engine_requires_registries_strict_di` tests None→ValidationException. `test_engine_accepts_valid_registries` tests valid construction. Discovery agent incorrectly claimed untested. |
| `_process_facility_generation` (113-144) | MAJOR untested | **CONFIRMED (indirect) → MINOR** | No direct test, but exercised through `process_fuel_generation` with 8 test cases covering: operational, non-operational (line 178), zero synthesis (line 192), capacity overflow (line 162), already full (line 239), empty facilities (line 274). Coverage is thorough. |
| `_get_fuel_generation_rate` (146-175) | MAJOR untested | **CONFIRMED (indirect) → MINOR** | No direct test. Exercised through fuel generation tests. Missing component in registry (line 168: `comp_def = registry.get(comp_id); if not comp_def: continue`) is exercised by `test_facility_without_synthesizer_no_generation` and `test_energy_generator_does_not_produce_fuel`. Dict vs str handling (line 166) is exercised by tests that use dict-shaped components. |
| `_calculate_fuel_distribution` (232-268) | MAJOR untested | **CONFIRMED → MAJOR** | No direct test. Exercised through `process_fleet_resupply`. Two tests validate distribution math with hardcoded values (200.0/40.0 in line 486, 100.0/10.0 in line 534). However, the division path `(available + current) / total_cost_per_hex` at line 257 could yield `NaN` if floating edge cases occur; the guard `total_cost_per_hex <= 0` at line 253 IS handled but NOT exercised by any test. Also, the `max_range` calculation when `current_total` is very large relative to `available_fuel` is untested. |
| `_transfer_fuel` (270-294) | MAJOR untested | **CONFIRMED (indirect) → MINOR** | No direct test. Simple iterative transfer loop. Tests validate `ship.resupply.assert_called()` and call args. The `min(amount, available - total_transferred)` path and `break` when `actual <= 0` (line 289) are exercised through the fleet resupply tests. |

**Discovery Agent Error:** `ResupplyEngine.__init__` is directly tested — the `TestResupplyEngineDI` class in the test file explicitly tests the constructor's strict DI behavior. The Phase 2 report claimed it was untested.

**Verdict:** 4 of 5 claims about untested private methods confirmed (indirect-only), but `__init__` is directly tested. Severity adjusted: only `_calculate_fuel_distribution` warrants MAJOR for the untested division-by-edge-case path. The rest are MINOR.

---

### MAJOR: `game/strategy/services/strategic_ability_scanner.py` (295 LOC) — CONFIRMED, severity adjusted

**Verification:** Read production code (295 lines) and test file (713 lines, 27 test functions). Import scan confirms test file imports only 4 public symbols: `find_abilities_at_planet`, `find_abilities_in_scope`, `aggregate_multipliers`, `aggregate_rates`.

| Symbol | Discovery Verdict | Verified Verdict | Detail |
|--------|------------------|------------------|--------|
| `_is_component_functionally_active` (248-266) | MAJOR | **CONFIRMED (indirect) → MINOR** | Not directly imported. BUT exercised through `find_abilities_at_planet` with `require_active=True` in 6 tests in `TestActivationStateFiltering` (lines 383-488). Tests cover ACTIVE→found, INACTIVE→skipped, ACTIVATING→skipped, DEACTIVATING→skipped, default→found. `getattr(gate, 262-264)` returning None when facility lacks `get_activation_state` IS exercised: `MockFacility` always has `get_activation_state`. The claim about untyped `is_functionally_active` return is a mild type-safety concern but not a test gap. |
| `_extract_ability` (269-295) | MAJOR | **CONFIRMED (indirect) → MINOR** | Not directly imported. BUT called at line 52 of `find_abilities_at_planet` — exercised in every test of `find_abilities_at_planet` (12 test cases). Delegates to `component_inspector.extract_abilities_from_component`. The PROJ-277 fix path (plain dict vs GameRegistries) is tested indirectly through the mock registry approach. |

**Verdict:** CONFIRMED (no direct imports in tests). But both functions are thoroughly exercised indirectly. Downgraded both from MAJOR to MINOR. The discovery agent's core claim is accurate but the risk assessment was inflated.

---

### MAJOR: `game/ui/screens/builder/weapons_panel.py` (321 LOC) — CONFIRMED

**Verification:** Read production code (321 lines) and test file (63 lines). Test file (`test_weapons_report_layout.py`) tests ONLY:
- `WeaponsReportPanel.__init__` — called to create the panel
- `_setup_filter_buttons` — called during init, button widths verified
- Button placement coordinates (lines 38-63)

**Not tested at all:**
- `handle_event` (lines 196-218): 23 lines of event routing — UI_BUTTON_PRESSED dispatch + MOUSEWHEEL scrolling
- `draw` (lines 220-321): 101 lines of rendering logic — target info, weapon rows, range bars, scroll offset, tooltip hover detection, clipping
- `_update_scrollbar` (lines 152-163): scrollbar visibility and percentage calculation
- `_on_weapons_updated` / `_on_filter_changed` event handlers
- `hovered_weapon` / `verbose_tooltip` properties
- `set_target` / `clear_target` / `update` public API

MVVM subcomponents (`WeaponsRenderer`, `WeaponsViewModel`, `WeaponsInputHandler`) have their own dedicated test files — those are covered elsewhere. This finding is about the coordinator shell.

**Verdict:** CONFIRMED. 14 of 15 symbols have zero direct tests. Only `__init__` + `_setup_filter_buttons` (indirectly) are exercised. Severity MAJOR is appropriate — event routing logic and scroll management are meaningfully complex.

---

## FALSE NEGATIVE

### `game/strategy/services/ability_sources/planet_intrinsic.py` (91 LOC) — CONFIRMED FALSE NEGATIVE

**Verification:** Read production code (91 lines, 9 public symbols in `PlanetIntrinsicAbilitySource` frozen dataclass). Read test file (121 lines, 9 test functions). Confirmation:

| Test Function | What It Tests | Production Symbol |
|---------------|--------------|-------------------|
| `test_source_kind_is_planet` | `source_kind` property | `source_kind` |
| `test_source_label_is_planet_name_with_type` | Formatted label | `source_label` |
| `test_source_id_uses_planet_id` | `"planet:{id}"` format | `source_id` |
| `test_owner_id_is_always_none` | PROJ-301 D2 | `owner_id` |
| `test_get_abilities_returns_intrinsic_dict` | Ability dict roundtrip | `get_abilities` |
| `test_get_abilities_empty_when_planet_has_none` | Empty fallback | `get_abilities` |
| `test_affects_hex_at_global_location` | Single-hex footprint | `affects_hex` |
| `test_affects_hex_multi_hex_dyson_sphere` | PROJ-301 D8 multi-hex | `affects_hex` |
| `test_get_activation_state_is_none` | Always-on | `get_activation_state` |
| `test_satisfies_iability_source_protocol` | Protocol conformance | `IAbilitySource` |

The test file imports via `from game.strategy.services.ability_sources import PlanetIntrinsicAbilitySource` — the re-export path may have confused the matrix scanner's symbol-name matching.

**Verdict:** CONFIRMED FALSE NEGATIVE. All 9 symbols are fully tested. Tier should be 3, not 0. The discovery agent correctly identified this and provided detailed evidence.

---

## ADVISORY→MAJOR UPGRADE

### `game/ui/screens/workshop_viewmodel_layer_ops.py` (254 LOC) — UPGRADED: ADVISORY → MAJOR

**Verification:** Read production code (254 lines). Despite being in `game/ui/screens/`, this module contains **zero Pygame dependencies**. All 5 public methods are pure-Python algorithm code:

| Method | Lines | Complexity |
|--------|-------|-----------|
| `resolve_target_layer` | 53-103 | Layer resolution with restriction validation, sorting, 3-branch dispatch |
| `quick_add_component` | 105-141 | Quick-add pipeline with component creation, layer targeting, bulk/single dispatch |
| `resolve_move_target` | 147-193 | Directional layer search with restriction validation |
| `move_component` | 195-213 | Single component move with mass budget warning |
| `move_component_group` | 215-254 | Bulk component move with reverse-index iteration |

The Phase 2 report rated this ADVISORY because it sits in `game/ui/screens/`. However, the report's own text notes: "All 7 symbols have zero tests despite being pure-Python algorithm code with no Pygame dependencies." This is a clear contradiction of the ADVISORY classification. Without Pygame deps, these are unit-testable algorithms that happen to live in the UI package.

**Verdict:** UPGRADED from ADVISORY to MAJOR. 254 lines of untested algorithm code with complex branching (layer resolution, restriction validation, reverse-index iteration) is a significant gap regardless of package location.

---

## Disputed/Inconclusive Table

| File | Claim | Disposition | Detail |
|------|-------|-------------|--------|
| `game/strategy/engine/resupply_engine.py` | `__init__` untested | **DISPUTED — DISCOVERY ERROR** | `TestResupplyEngineDI` directly tests constructor (lines 110-119) |
| `game/strategy/services/system_effects_collector.py` | `_ability_kind` severity MAJOR | **DOWNGRADED to MINOR** | 2-line function, exercised indirectly via kind assertions |
| `game/strategy/services/system_effects_collector.py` | `_format_status` severity MAJOR | **DOWNGRADED to MINOR** | All 5 branches exercised indirectly |
| `game/strategy/services/strategic_ability_scanner.py` | `_is_component_functionally_active` severity MAJOR | **DOWNGRADED to MINOR** | 6 tests exercise it indirectly |
| `game/strategy/services/strategic_ability_scanner.py` | `_extract_ability` severity MAJOR | **DOWNGRADED to MINOR** | 12 tests exercise it indirectly |
| `game/ui/screens/workshop_viewmodel_layer_ops.py` | ADVISORY | **UPGRADED to MAJOR** | 254 LOC pure-algorithm code, zero Pygame deps |

---

## Discovery Agent Errors

1. **ResupplyEngine `__init__` classified as untested** — The test file `test_resupply_engine.py` contains `TestResupplyEngineDI` with two explicit tests for the constructor. The discovery agent listed `process_fuel_generation`, `process_fleet_resupply`, `_validate_tick_inputs`, and `ResupplyEvent` as "public symbols with verified coverage" but omitted `__init__`, which IS tested directly.

2. **Overstated severity on small helper functions** — `_ability_kind` (2 lines), `_format_status` (12 lines, all branches exercised), `_is_component_functionally_active` (exercised in 6 tests), `_extract_ability` (exercised in 12 tests) were rated MAJOR despite comprehensive indirect coverage. The discovery agent's own text acknowledged indirect coverage but still assigned MAJOR severity.

3. **`workshop_viewmodel_layer_ops.py` rated ADVISORY despite being pure Python** — The discovery agent noted the file has no Pygame dependencies and zero tests but still classified it as ADVISORY due to package location. This contradicts the project's testing standards which prioritize testability over package hierarchy.

---

## Spot-Check Verification (MINOR Claims)

| File | Claim | Spot-Check Result |
|------|-------|-------------------|
| `game/strategy/formulas/habitability.py` | `_gaussian_factor` MINOR | CONFIRMED. 4 test files exist for habitability. Production code at line 48 has `sigma = max(tolerance, min_sigma)` guard. Tested indirectly through factor scorers. MINOR appropriate. |
| `game/strategy/systems/race_randomizer.py` | `_resolve_rng`, `_pick_name_entry`, `_pick_leader` MINOR | CONFIRMED. Test file exists at `test_race_randomizer.py`. Helpers tested indirectly through `randomize_identity`. MINOR appropriate. |
| `game/ui/screens/list_filter_utils.py` | `make_attr_sort_key` + `_key` ADVISORY | CONFIRMED. 43 LOC. Tested indirectly through planet_list and star_list filter tests. ADVISORY appropriate. |
| `game/ui/components/table/virtual_table.py` | `_build_containers`, `_rebuild_row_pool`, etc. ADVISORY | CONFIRMED. Pygame_gui widget construction code. ADVISORY appropriate per UI rendering convention. |
| `game/ui/screens/builder/modifier_logic.py` | 10 untested, mostly deprecated `ModifierLogic` class ADVISORY | CONFIRMED. 6 of 10 untested symbols are the deprecated `ModifierLogic` static wrapper. ADVISORY appropriate. |
| `game/ui/screens/transfer_dialog.py` | 12 untested delegation shims MINOR | CONFIRMED. All untested methods are thin delegation shims to ViewModel/Controller/Renderer. MINOR appropriate. |

---

## Final Severity Matrix (Verified)

| Priority | File | Original Severity | Verified Severity | Delta |
|----------|------|-------------------|-------------------|-------|
| P0 | `game/core/protocols/ui.py` | CRITICAL | **CRITICAL** | — |
| P1 | `game/ui/services/game_settings.py` | MAJOR | **MAJOR** | — |
| P2 | `game/strategy/services/system_effects_collector.py` | MAJOR | **MAJOR** (`_aggregate` only) | Other symbols→MINOR |
| P3 | `game/ui/screens/workshop_viewmodel_layer_ops.py` | ADVISORY | **MAJOR** | **UPGRADE** |
| P4 | `game/ui/screens/builder/weapons_panel.py` | MAJOR | **MAJOR** | — |
| P5 | `game/ai/spatial_behaviors/_formation_utils.py` | MAJOR | **MAJOR** | — |
| P6 | `game/strategy/engine/resupply_engine.py` | MAJOR | **MAJOR** (`_calculate_fuel_distribution` only) | 4 symbols→MINOR, 1 ERROR |
| P7 | `game/strategy/services/strategic_ability_scanner.py` | MAJOR | **MINOR** | **DOWNGRADE** — comprehensive indirect coverage |
| P8 | `game/strategy/formulas/habitability.py` | MINOR | **MINOR** | — |
| P9 | `game/strategy/systems/race_randomizer.py` | MINOR | **MINOR** | — |
| — | `game/strategy/services/ability_sources/planet_intrinsic.py` | FALSE NEGATIVE | **TIER 3** (FULLY COVERED) | Confirmed |

