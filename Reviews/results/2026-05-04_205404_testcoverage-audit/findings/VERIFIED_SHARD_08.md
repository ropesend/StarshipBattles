# Test Coverage Audit — Shard 08 Skeptical Verification

**Date:** 2026-05-04
**Verified by:** OpenCode (Skeptical Verifier)
**Original Phase 2 report:** `SHARD_08.md`

---

## Summary

| Category | Original | Confirmed | Disputed | Inconclusive |
|----------|----------|-----------|----------|--------------|
| CRITICAL | 2 | 2 | 0 | 0 |
| MAJOR | 4 | 0 | 4 | 0 |
| MINOR | 5 | 3 | 2 | 0 |
| ADVISORY | 7 | 7 | 0 | 0 |

**Key findings:**
- Both CRITICAL claims confirmed — `ship_validator_helper.py` and `planet_slice.py` genuinely have zero dedicated unit tests.
- All 4 MAJOR claims disputed — the production code has comprehensive indirect/integration test coverage; the AST scanner produced false negatives for internal/private methods exercised through public entry points.
- 2 of 5 MINOR claims disputed — `planetary_facility.py` fuel methods have a full test suite (`test_facility_resource_tracking.py`, 50+ assertions); `abilities/base.py` `_parse_attrs` are exercised by subclass tests.

---

## CONFIRMED Gaps

### CRITICAL-1: `game/simulation/entities/ship_validator_helper.py` — CONFIRMED

**Verification:** Read complete 70 LOC production file. Searched for `test_ship_validator_helper*` — no test file found. Grep'd for `ShipValidatorHelper`, `check_validity`, `get_validation_warnings`, `get_missing_requirements` in entire tests/ tree.

**Findings:**
- No dedicated test file exists.
- The methods `check_validity()`, `get_validation_warnings()`, `get_missing_requirements()` are called on *Ship instances* (not `ShipValidatorHelper` directly) in 3 test files: `test_warnings.py`, `test_builder_logic.py`, `test_builder_improvements.py`. These exercise the helper indirectly through the `Ship` delegation chain.
- The only direct reference to the module in tests is `test_ship_component_manager_di.py` which verifies the module does NOT import `get_default_registry_provider` — not a behavioral test.
- The `get_or_create_validator` dependency and `registry_provider` DI path (PROJ-252) are untested in isolation.

**Verdict: CONFIRMED.** The helper class has no dedicated unit test. 3 tests exercise its methods indirectly through `Ship` delegation but no test creates a `ShipValidatorHelper` directly with controlled dependencies.

---

### CRITICAL-2: `game/strategy/facade/slices/planet_slice.py` — CONFIRMED

**Verification:** Read complete 105 LOC production file. Searched for `test_planet_slice*` — no test file found. Grep'd for `PlanetSlice`, `get_planets_at_hex`, `can_colonize` in tests/.

**Findings:**
- No dedicated test file exists.
- `get_planets_at_hex()` is heavily mocked in UI tests (e.g., `test_strategy_screen.py`, `test_transfer_dialog_characterization.py`, `test_sub_window_hotkeys.py`) but never tested directly. Mocks sidestep actual logic.
- `can_colonize()` at lines 84-105 performs cross-domain validation with multiple failure branches (fleet not found, planet not found, validate_colonize_order). No test covers any of these paths.
- `get_planet()` at lines 45-50 converts Planet to PlanetInfo DTO — untested DTO conversion path.
- `get_planets_at_hex()` at lines 52-78 has a dual-path lookup (strict + radius fallback) that is completely untested.

**Verdict: CONFIRMED.** Zero dedicated unit tests. Business logic (dual-path hex lookup, cross-domain colonize validation, DTO conversion) completely untested.

---

### MINOR-7: `game/assets/component_derivatives.py` — CONFIRMED MINOR

**Verification:** Grep'd for `_read_manifest`, `_write_manifest`, `_sha256`, `_has_expected_size`, `_write_derivative` in tests/ — zero matches. The manifest tests in `test_manifests.py` test project workflow manifests, not component derivative helpers.

**Verdict: CONFIRMED as MINOR.** 6 private helpers untested. Low risk — all are internal implementation details of `ensure_component_derivatives()`.

---

### MINOR-10: `game/simulation/projectile_manager.py` — CONFIRMED MINOR

**Verification:** Grep'd for `_apply_hit` in tests/ — zero matches. The method at lines 130-154 handles distance-based damage evaluation from source weapon and creates `DamageContext`. Only tested indirectly through `update()` collision path.

**Verdict: CONFIRMED as MINOR.** `_apply_hit()` lacks direct coverage. Indirect coverage exists via `update()` but `source_weapon is None` fallback and `get_damage(hit_dist)` branch are not independently verified.

---

### ADVISORY Items (12-21) — All CONFIRMED as ADVISORY

**Verified by sampling:**
- `battle_state_viewer.py` — Read file. All 8 symbols are `show()`, `hide()`, `draw()`, `handle_event()` — pure pygame rendering/event dispatch. No business logic.
- `strategy_render/grid.py` — `draw_grid()` is snake-line hex drawing with viewport culling. Pure rendering.
- `test_lab/theme.py` — Color hex constant definitions only. No executable logic.
- `test_lab/renderer/tag_filter_panel.py` — Pure pygame tag filter button rendering with hover/active states.
- `range_slider_builder.py` — `build_range_slider_row()` constructs pygame_gui elements. Pure UI widget factory.

**Verdict: All 7 ADVISORY items correctly classified.** No business logic hidden in rendering code. No upgrades needed.

---

## Disputed / Inconclusive Table

| # | File | Original Severity | New Severity | Verdict | Evidence |
|---|------|-------------------|-------------|---------|----------|
| 3 | `empire_economy_calculator.py` | MAJOR | MINOR | DISPUTED | 1169-line test file. All private methods exercised through `calculate()`. Edge cases tested: non-operational facilities (line 209), zero quality (line 316), exhausted deposits (resource_quantity in production), paused queues (line 705), multi-colony aggregation (line 246), population upkeep empty-empire/empty-population (lines 857-895), backward compat without economy_config (line 1021). **Downgrade to MINOR** for the `__init__` constructor and the `_aggregate_population_upkeep` early-return path (no economy_config) that could use a dedicated test. |
| 4 | `game_session.py` | MAJOR | MINOR | DISPUTED | `process_turn()` tested in `test_game_session_strategy.py:25-31` and 20+ integration tests. `preview_fleet_path()` tested directly in `test_command_handlers.py:76-91` and `test_fleet_operations.py:79`. `race_registry` property tested in `test_strategy_session_facade.py:767-793`. `_create_event_handler()` tested via event replay tests. **Downgrade to MINOR** for `get_fleet_path_projection()` which is an untested delegation to `project_fleet_path()`. |
| 5 | `damage_calculator.py` | MAJOR | ADVISORY | DISPUTED | 1199-line test file with 13 test classes, 40+ test methods. All 5 pipeline stages exercised through `apply_damage()`. Specific edge cases the report claimed untested ARE covered: `current_shields <= 0` early return → `TestEmissiveArmorReduction` (shields=0). `ea <= 0` early return → `TestShieldRegeneratingArmorAbsorption` (emissive_armor=0). `sra <= 0` with max_shields > 0 → `TestShieldAbsorption` (sra=0, max_shields=100). Empty layers → `test_empty_layer_returns_full_damage`. Single-component layers → `test_single_component_receives_all_damage`. No-damage early return → `test_negative_damage_treated_as_no_damage`, `test_damage_skipped_when_dead`. **Downgrade to ADVISORY** — coverage is actually excellent. |
| 6 | `superweapon_order_processor.py` | MAJOR | ADVISORY | DISPUTED | 1231-line test file + 594-line gaps test file = 1825 LOC of tests. `SuperweaponResult` is a frozen dataclass tested implicitly via return values of all 6 public methods. `__init__()` trivially tested. `_finalize_superweapon()` exercised through all process methods including stabilizer-blocking paths, ship-consumption paths, empty-fleet cleanup (SG-003) in `TestSelfDestructFleetCleanup`, event logging. **Downgrade to ADVISORY** — comprehensive coverage. |
| 8 | `abilities/base.py` | MINOR | NO GAP | DISPUTED | `_parse_attrs` methods at lines 98, 459, 511 are called from `__init__` and `sync_data()`. The report itself states "thoroughly exercised by subclass tests" and the AST scanner cannot resolve dispatch. **False negative — remove claim.** |
| 11 | `planetary_facility.py` | MINOR | NO GAP | DISPUTED | All 4 fuel-management methods have a comprehensive test suite at `tests/unit/strategy/data/test_facility_resource_tracking.py`. `get_fuel_storage()` has 3 dedicated tests (lines 207-222). `get_max_fuel_storage()` has 4 tests including missing components edge case (lines 226-281). `add_fuel()` has 5 tests covering empty facility, overflow, multi-add, zero-max edge case (lines 285-338). `withdraw_fuel()` has 4 tests covering full amount, partial, empty, exact (lines 343-371). **False negative — remove claim.** |

---

## Discovery Agent Errors

### False Negatives (AST scanner missed existing tests)

1. **`planetary_facility.py` fuel methods** — `tests/unit/strategy/data/test_facility_resource_tracking.py` (50+ assertions) covers all 4 methods. Scanner found 0.

2. **`abilities/base.py` `_parse_attrs`** — Called via `__init__` → subclass dispatch. Scanner cannot resolve dynamic dispatch.

3. **`fleet_hierarchy.py` `FleetHierarchyNode.__init__()`** — Trivial constructor tested whenever a node is created in any test. Scanner counts `__init__` separately.

4. **`damage_calculator.py` pipeline stages** — All 5 static methods exercised through `apply_damage()`. Scanner doesn't trace call chains.

5. **`superweapon_order_processor.py` `_finalize_superweapon()`** — Called from all 6 public methods, tested extensively (1825 LOC of tests). Scanner cannot trace private method call sites.

6. **`superweapon_validator.py`** (identified in original report) — `tests/unit/strategy/validation/test_superweapon_validator.py` (650 LOC) covers all 11 symbols. Scanner path normalization mismatch.

7. **`strategy_screen_order_editing.py`** (identified in original report) — `tests/unit/ui/screens/test_strategy_screen_order_editing.py` (183 LOC, 13 tests). Scanner missed the file.

### Severity Misclassifications

1. **`damage_calculator.py`** — Reported as MAJOR with 5 untested symbols. Actually: 1199-line test file, comprehensive pipeline coverage via `apply_damage()`. Should be ADVISORY at most.

2. **`superweapon_order_processor.py`** — Reported as MAJOR with 3 untested symbols. Actually: 1825 LOC of tests across 2 test files, all 12 symbols tested. Should be ADVISORY at most.

3. **`empire_economy_calculator.py`** — Reported as MAJOR for 4 "untested" private methods. Actually: all exercised through `calculate()` with edge-case coverage. Should be MINOR.

4. **`game_session.py`** — Reported as MAJOR for 8 "untested" symbols. Actually: most have integration coverage; only `get_fleet_path_projection()` is genuinely untested. Should be MINOR.

### Edge-Case Coverage Gaps Actually Present (non-false)

These are genuine gaps identified through skeptical verification, but none rise to MAJOR severity:

- **`ship_validator_helper.py`**: 0 dedicated tests (CRITICAL confirmed).
- **`planet_slice.py`**: 0 dedicated tests (CRITICAL confirmed).
- **`game_session.py` `get_fleet_path_projection()`**: Delegates to `project_fleet_path()`, no test (MINOR).
- **`component_derivatives.py` 6 private helpers**: No behavioral tests (MINOR confirmed).
- **`projectile_manager.py` `_apply_hit()`**: `source_weapon is None` fallback untested (MINOR confirmed).

---

## Adjusted Severity Summary

| Severity | Count | Items |
|----------|-------|-------|
| CRITICAL | 2 | `ship_validator_helper.py`, `planet_slice.py` |
| MAJOR | 0 | — |
| MINOR | 5 | `empire_economy_calculator.py` (private method edge cases), `game_session.py` (get_fleet_path_projection), `component_derivatives.py` (6 private helpers), `projectile_manager.py` (_apply_hit), `builder_utils.py` (1 builder_util) |
| ADVISORY | 9 | `damage_calculator.py` (pipeline edge cases), `superweapon_order_processor.py` (internal plumbing), 7 UI/__init__.py items |
| FALSE NEGATIVES | 3 | `planetary_facility.py` fuel methods, `abilities/base.py` _parse_attrs, `fleet_hierarchy.py` __init__ |
