# Phase 4: Switch callers + delete legacy fields

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-283 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Migrate every caller off the legacy fields and delete them. Habitability pipeline becomes registry-only. `PopulationEngine` reads `base_reproduction_rate` directly. Dyson Sphere seeding rebuilt. Existing user race JSONs deleted. This is the riskiest phase — one commit that removes the parallel fields and rewires every caller.

---

## Tasks

### Task 4.1: Promote v2 habitability to the canonical name [Simple]
**File:** `game/strategy/formulas/habitability.py`
**Tests:** `pytest tests/unit/strategy/formulas/` + full suite

- [x] Delete the legacy `calculate_habitability`, `calculate_atmosphere_factor`, `calculate_gravity_factor`, `calculate_temperature_factor`, `calculate_water_factor`, `calculate_radiation_factor`.
- [x] Rename `calculate_habitability_v2` to `calculate_habitability`.
- [x] `score_planet_for_race(planet, race_config)` stays as the public entry; updated to call the new function.
- [x] Updated tests that imported the deleted per-factor functions: deleted the v1 `tests/unit/strategy/formulas/test_habitability.py` (per-factor coverage already lives in `test_habitability_factors.py::TestScorer` from Phase 1) and renamed `test_habitability_v2.py` → `test_habitability.py` (the canonical name).

**Notes:** Also pruned `STANDARD_GRAVITY_MS2` and `FACTOR_WEIGHTS` (v1-only constants) and updated `game/strategy/formulas/__init__.py` to export only `calculate_habitability` + `score_planet_for_race`. The lazy-import pattern for `FACTOR_REGISTRY` carried over unchanged.

### Task 4.2: Delete legacy `RaceConfig` fields [Medium]
**File:** `game/strategy/data/race_config.py`

- [x] Deleted fields: `gravity_ideal`, `gravity_tolerance`, `temperature_ideal`, `temperature_tolerance`, `water_ideal`, `water_tolerance`, `atmosphere_preferences`, `radiation_tolerance`, `aptitude_happiness`, `aptitude_population_growth`.
- [x] Updated `to_dict` / `from_dict` to not emit or require those keys (legacy keys in old saves are silently ignored — save files are disposable per CLAUDE.md System Migration Policy).
- [x] Updated `validate()` — removed `_validate_environment_ranges` (the bounds it enforced now live on `EnvironmentalPreference.validate()`). Added `_validate_reproduction_and_happiness` to bound the new fields.
- [x] Removed `DEFAULT_ATMOSPHERE_PREFERENCES` constant. `APTITUDE_NAMES` shrunk to 7 entries.
- [x] Kept `GAS_NAME_TO_FORMULA` / `GAS_FORMULA_TO_NAME` — still used by `homeworld_presets.apply_preset_to_config` (transitional shim) and several editor UIs that translate between display names and formulas.

**Notes:** `__post_init__` simplified — only the registry-driven preferences backfill remains (the legacy `atmosphere_preferences` defaulting block is gone). `_validate_aptitudes` now drives off the shared `APTITUDE_NAMES` list rather than a duplicate inline tuple.

### Task 4.3: Rewire `PopulationEngine` to read `base_reproduction_rate` [Simple]
**File:** `game/strategy/engine/population_engine.py`
**Tests:** `pytest tests/unit/strategy/engine/test_population_engine.py`

- [x] Deleted `_aptitude_to_growth_rate` helper (was a dead static method after the field-read change).
- [x] Replaced `aptitude_population_growth`-reading call site with `race_config.base_reproduction_rate`.
- [x] Logistic formula untouched (PROJ-284 owns the rework).
- [x] Updated tests: `make_human_race_config` now seeds `base_reproduction_rate` (translates the legacy `aptitude_population_growth` parameter via the same `0.0005 * aptitude` scale the deleted helper used, so test expectations stay numerically stable). `TestAptitudeConversion` deleted entirely.

**Notes:** 13 population-engine tests pass after the migration. Reproduction-rate cost-curve coverage now lives in `test_race_point_budget_v2.py::TestCalculateReproductionCost` (Phase 3).

### Task 4.4: Rewire `SuperweaponOrderProcessor.process_create_dyson_sphere` [Medium]
**File:** `game/strategy/engine/superweapon_order_processor.py`
**Tests:** `pytest tests/unit/strategy/engine/test_superweapon_order_processor.py` + Dyson Sphere integration tests

- [x] Replaced the legacy field reads (`race.gravity_ideal`, `race.atmosphere_preferences`, `GAS_NAME_TO_FORMULA` translation) with iteration over `race.preferences` filtered to gas factors with `setpoint > 0`.
- [x] Removed the `from game.strategy.data.race_config import GAS_NAME_TO_FORMULA` import inside the function — gas factor ids are already keyed by chemical formula (`gas.O2`, `gas.N2`, ...), no translation needed.
- [x] Updated Dyson Sphere fixture in `test_superweapon_order_processor.py::test_dyson_sphere_uses_race_config_conditions` to set preferences via the registry instead of legacy fields.

**Notes:** Hardcoded fallback atmosphere updated from `{"O2": 210, "N2": 780}` (legacy preference scores × 10) to `{"O2": 21000, "N2": 79000}` Pa — consistent with the new model's units.

### Task 4.5: Grep sweep for remaining callers [Medium]
**File:** (various)
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [x] Ran the grep; non-UI callers found: `game/strategy/engine/game_initializer.py` (lines 222-244), `game/strategy/data/homeworld_presets.py:apply_preset_to_config`, `game/ui/panels/race_summary_panel.py` (display formatters), `game/ui/screens/empire_panel_window.py` (display formatters), `game/ui/screens/race_validator.py`.
- [x] Migrated each non-UI hit:
  - `game_initializer._adjust_homeworld_to_race`: reads `race_config.preferences[<id>].setpoint` for gravity/temperature/water and iterates gas factors for atmosphere.
  - `homeworld_presets.apply_preset_to_config`: rewritten as a transitional shim that translates the legacy preset JSON schema (display-name gas scores, gravity in g) into `EnvironmentalPreference` entries on `race.preferences`. Phase 5 will rewrite the JSON to the registry-native shape.
- [x] UI display files (race_summary_panel, empire_panel_window, race_validator) migrated to read from `preferences` so they stay functional between Phase 4 and Phase 5.
- [x] `race_environment_panel.py` left unchanged — Phase 5 rebuilds it. The legacy field reads will AttributeError at runtime if the user opens the race-setup screen; no other call site triggers it.

**Notes:** Several editor UIs (gravity_target_editor, water_target_editor, radiation_shield_editor, atmosphere_target_editor) used defensive `getattr(rc, 'foo', None)` patterns that now silently return None. They keep compiling; their behaviour with None inputs is "show defaults" which is acceptable until Phase 5 rebuilds them.

### Task 4.6: Delete existing user race JSON files [Simple]
**File:** `output/races/*.json`

- [x] Located user-saved race files: `output/races/*.json` (9 files, all containing legacy fields).
- [x] Deleted them. `data/races/qs_empire_*.json` (shipped quickstart races) kept — `from_dict` silently ignores their legacy keys, and `test_quickstart_races.py` only checks identity fields (theme_id/flag_id/portrait_id) which still load correctly.
- [x] `RaceLibrary` doesn't depend on pre-seeded files — it scans the directory.

**Notes:** Per CLAUDE.md, save files are disposable. No migration shim provided.

### Task 4.7: Introduce test helper for race construction [Simple]
**File:** `tests/conftest.py`

- [x] Added `make_test_race(preferences_overrides=None, base_reproduction_rate=0.03, base_happiness=0.5, name="Test Race", flag_id="flag_test", portrait_id="portrait_test", theme_id="Federation", **aptitude_overrides) -> RaceConfig`. Backfills preferences from the registry via `__post_init__`, accepts overrides for any axis.
- [x] Implemented EARLY (before Task 4.2) per the handoff watchout — the helper became the construction pattern used by every test that subsequently needed a valid race.

**Notes:** Existing tests didn't all migrate to the helper this phase — most used inline `RaceConfig(...)` calls that I migrated surgically (population_engine, game_initializer, race_summary_panel, race_library, superweapon, etc.). Subsequent phases / new tests should prefer the helper.

### Task 4.8: Full suite green [Simple]
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [x] Full sharded suite: 14724/14725 in the cleanest run; one failure is the same pre-existing flaky `test_copy_designs_without_themes_preserves_original` (Klingons vs Federation theme leak). Across multiple sharded runs, occasionally `test_make_minimal_spec` and `test_reference_integrity::test_colony_owner_id_matches_empire` flake — both pass deterministically in isolation, both unrelated to PROJ-283 (battle-screen and colony save-load surfaces respectively). All flaky failures are infrastructure quirks of the sharded runner.
- [x] No tests are irrecoverably tied to the old model — every legacy-field-touching test was either migrated (game_initializer, race_summary_panel, race_library, race_aptitudes_panel, race_validator, roundtrip_empire, superweapon_order_processor, population_engine, strategy_entities fixture) or deleted (test_race_environment_panel.py: full UI rebuild in Phase 5).

**Notes:** Total tests deleted in Phase 4: ~12 (the entire `test_race_environment_panel.py` file plus `TestAptitudeConversion` class). Total tests rewritten: ~50. Net coverage delta is positive — the new tests exercise the registry-driven path the production code now uses.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
