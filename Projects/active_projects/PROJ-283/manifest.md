# PROJ-283 File Manifest

> Generated during project initialization. Used for parallel execution conflict detection.
> Update if implementation discovers additional files.

## Files

| File | Type | Notes |
|------|------|-------|
| game/strategy/data/environmental_preference.py | Production (NEW) | Phase 1 ✓ added: `EnvironmentalPreference` dataclass with validation |
| game/strategy/data/habitability_factors.py | Production (NEW) | Phase 1 ✓ added: `HabitabilityFactor` + `FACTOR_REGISTRY` (7 scalar + 10 gas) |
| game/strategy/data/race_config.py | Production (MODIFY) | Phase 1 ✓ added `preferences` field + `base_reproduction_rate` + `base_happiness` + `_validate_preferences()`; Phase 4 ✓ deleted 10 legacy fields, simplified `__post_init__`, removed `_validate_environment_ranges`, added `_validate_reproduction_and_happiness`, dropped `DEFAULT_ATMOSPHERE_PREFERENCES` constant, shrunk `APTITUDE_NAMES` to 7 |
| game/strategy/data/race_point_budget.py | Production (MODIFY) | Phase 3 ✓ rewrote around `FACTOR_REGISTRY`: deleted hardcoded step constants + `calculate_tolerance_cost` + `get_tolerance_breakdown`; added `calculate_preferences_cost`, `calculate_reproduction_cost` (linear-in-rate refund), `get_breakdown`; dropped happiness/population_growth from aptitude cost list |
| game/ui/panels/race_aptitudes_panel.py | Production (MODIFY) | Phase 3 ✓ updated to call `calculate_preferences_cost` instead of deleted `calculate_tolerance_cost` |
| game/ui/panels/race_environment_panel.py | Production (MODIFY) | Phase 3 ✓ updated to call `calculate_preferences_cost` instead of deleted `calculate_tolerance_cost` |
| game/strategy/data/homeworld_presets.py | Production (MODIFY) | Phase 5: new preference shape |
| game/strategy/formulas/habitability.py | Production (MODIFY) | Phase 2 ✓ added `calculate_habitability_v2`; Phase 4 ✓ deleted v1 (5 per-factor functions + entry-point + STANDARD_GRAVITY_MS2 + FACTOR_WEIGHTS) and renamed v2 → canonical `calculate_habitability`. `score_planet_for_race` retained as thin wrapper |
| game/strategy/formulas/__init__.py | Production (MODIFY) | Phase 4 ✓ pruned exports to `calculate_habitability` + `score_planet_for_race` only |
| game/strategy/data/habitability_factors.py | Production (MODIFY) | Phase 2 ✓ tuned `gas.N2` default setpoint 0 → 79000 Pa, tolerance → 20000 Pa so an unconfigured Earth-like default race tolerates Earth's atmosphere |
| game/strategy/engine/population_engine.py | Production (MODIFY) | Phase 4 ✓ deleted `_aptitude_to_growth_rate`, replaced `aptitude_population_growth` read with `base_reproduction_rate` |
| game/strategy/engine/superweapon_order_processor.py | Production (MODIFY) | Phase 4 ✓ Dyson Sphere atmosphere seeding rewritten to iterate `race.preferences` gas factors with positive setpoint |
| game/strategy/engine/game_initializer.py | Production (MODIFY) | Phase 4 ✓ `_adjust_homeworld_to_race` reads from `race_config.preferences[<id>].setpoint` |
| game/strategy/data/homeworld_presets.py | Production (MODIFY) | Phase 4 ✓ transitional shim; Phase 5 ✓ rewritten to consume registry-native preset shape (`preferences: {factor_id: {setpoint?, tolerance?}}`); fills omitted setpoint/tolerance from registry defaults |
| data/homeworld_presets.json | Data (MODIFY) | Phase 5 ✓ rewrote 11 presets in registry-native partial-`preferences` shape with explanatory `_schema` field; setpoint units match registry (m/s² gravity, K temperature, fraction water, Pa gases) |
| game/strategy/data/habitability_factors.py | Production (MODIFY) | Phase 1 ✓ created; Phase 2 ✓ tuned `gas.N2` defaults; Phase 5 ✓ extended `temperature` factor bounds (50–2000 K instead of 100–500 K) to admit ICE_GIANT (~80 K) and CHTHONIAN (~1500 K) preset setpoints |
| game/ui/widgets/preference_row.py | Production (NEW) | Phase 5 ✓ added: reusable row widget rendering name + setpoint slider + tolerance slider + value labels + per-factor cost label; static `format_value(factor, raw)` and `calculate_factor_cost(factor, pref)` helpers reusable elsewhere |
| game/ui/panels/race_environment_panel.py | Production (REWRITE) | Phase 4 left runtime-broken; Phase 5 ✓ rebuilt from scratch (~597 → ~280 lines): iterates `iter_scalar_factors()` + `iter_gas_factors()` for one `PreferenceRow` per factor; adds `base_reproduction_rate` and `base_happiness` sliders; live points label refreshes on every row callback |
| game/ui/widgets/__init__.py | Production (MODIFY) | Phase 5 — kept untouched (PreferenceRow imported directly by callers; not added to package `__all__` to avoid pygame_gui import side effects in environments without display) |
| game/ui/panels/race_summary_panel.py | Production (MODIFY) | Phase 4 ✓ display formatters (gravity, temperature, radiation, atmosphere, water, aptitudes) read from `race.preferences` and `base_*` fields |
| game/ui/screens/empire_panel_window.py | Production (MODIFY) | Phase 4 ✓ env display + aptitude list migrated to new fields |
| game/ui/screens/race_validator.py | Production (MODIFY) | Phase 4 ✓ removed water_ideal/_tolerance bounds checks (now enforced by `EnvironmentalPreference.validate()`); aptitude list shrunk to 7 |
| game/ui/panels/race_aptitudes_panel.py | Production (MODIFY) | Phase 3 ✓ updated calculate_preferences_cost calls; Phase 4 ✓ `APTITUDE_DISPLAY_NAMES` + `APTITUDE_ORDER` shrunk to 7 entries |
| output/races/*.json | Data (DELETE) | Phase 4 ✓ deleted 9 user-saved race files; data/races/qs_*.json kept (legacy keys silently ignored on load) |
| data/races/*.json | Data (DELETE) | Phase 4: user-confirmed disposable |
| tests/unit/strategy/data/test_environmental_preference.py | Test (NEW) | Phase 1 ✓ added: 12 tests, all passing |
| tests/unit/strategy/data/test_habitability_factors.py | Test (NEW) | Phase 1 ✓ added: 39 tests, all passing |
| tests/unit/strategy/data/test_race_config.py | Test (MODIFY) | Phase 1 ✓ added 11 new tests; Phase 4 ✓ legacy fields gone (file is mostly Phase 1 tests; the pre-existing 16-test `TestRaceConfigValidation` tuple-unpacking bug is unchanged and out of PROJ-283 scope) |
| tests/unit/strategy/formulas/test_habitability.py | Test (DELETE+RECREATE) | Phase 4 ✓ deleted v1 file; renamed `test_habitability_v2.py` → `test_habitability.py`; updated docstring + class names; deleted obsolete `TestV1V2Parity::test_near_earth_setup_both_score_high` |
| tests/unit/ui/test_race_environment_panel.py | Test (DELETE) | Phase 4 ✓ deleted (legacy panel will be rewritten in Phase 5; new tests will be authored alongside the rebuild) |
| tests/conftest.py | Test helper (MODIFY) | Phase 4 ✓ added `make_test_race(...)` helper at the end of the file |
| tests/fixtures/strategy_entities.py | Test helper (MODIFY) | Phase 4 ✓ `create_test_race_config` defaults migrated off legacy fields onto registry preferences via `__post_init__` |
| tests/unit/strategy/engine/test_population_engine.py | Test (MODIFY) | Phase 4 ✓ `make_human_race_config` translates `aptitude_population_growth` → `base_reproduction_rate` for source-stability; deleted `TestAptitudeConversion` |
| tests/unit/strategy/engine/test_game_initializer.py | Test (MODIFY) | Phase 4 ✓ Mock-based race_config replaced with real `RaceConfig` + `_make_race` helper for the 4 `_adjust_homeworld_to_race` tests |
| tests/unit/strategy/engine/test_superweapon_order_processor.py | Test (MODIFY) | Phase 4 ✓ Dyson Sphere fixture migrated to use `race.preferences` overrides via registry |
| tests/unit/strategy/systems/test_race_library.py | Test (MODIFY) | Phase 4 ✓ `test_save_and_load_race` migrated to `preferences["gravity"]` round-trip |
| tests/integration/save_load/test_roundtrip_empire.py | Test (MODIFY) | Phase 4 ✓ all 5 `TestRaceConfigRoundTrip` tests migrated to new schema (`preferences`, `base_reproduction_rate`, `base_happiness`); `test_atmosphere_preferences_round_trip` renamed `test_preferences_round_trip` |
| tests/unit/ui/test_race_summary_panel.py | Test (MODIFY) | Phase 4 ✓ replaced MagicMock fixtures with real `RaceConfig`; rewrote radiation tests (Sensitive/Resistant labels deleted; format now shows numeric tolerance); atmosphere tests now check chemical-formula labels + kPa |
| tests/unit/ui/screens/test_race_validator.py | Test (MODIFY) | Phase 4 ✓ deleted `TestRaceValidatorWaterRanges` class (water bounds now enforced by `EnvironmentalPreference.validate()`) |
| tests/unit/ui/panels/test_race_aptitudes_panel.py | Test (MODIFY) | Phase 4 ✓ `test_aptitudes_panel_has_9_sliders` → `_has_7_sliders`; expected_names list shrunk; tolerance test rewired through `preferences["gravity"]` |
| tests/unit/strategy/formulas/test_habitability_v2.py | Test (NEW) | Phase 2 ✓ added: 21 tests, all passing (happy path, registry-iteration, gas-missing edge cases, parity with v1, isolated single-factor checks for pressure/tectonic) |
| tests/unit/strategy/formulas/test_habitability.py | Test (MODIFY) | Phase 4: update for v1 deletion |
| tests/unit/strategy/data/test_race_point_budget_v2.py | Test (NEW) | Phase 3 ✓ added: 46 tests covering preferences cost (registry-driven, per-axis parity), reproduction cost curve + refund + floor clamp, aptitude-cost dropping happiness/pop_growth, total + breakdown, aptitude edge cases (max=440, min=-49), legacy method removal sanity checks |
| tests/unit/strategy/data/test_race_point_budget.py | Test (DELETE) | Phase 3 ✓ deleted: legacy file fully superseded by v2; surviving aptitude edge-case tests ported into v2's `TestAptitudeCostEdgeCases` + `TestCustomBudget` classes |
| tests/unit/strategy/engine/test_population_engine.py | Test (MODIFY) | Phase 4: use `base_reproduction_rate` |
| tests/unit/strategy/engine/test_superweapon_order_processor.py | Test (MODIFY) | Phase 4: Dyson Sphere seeding uses preferences |
| tests/integration/strategy/test_superweapon_integration.py | Test (MODIFY) | Phase 4: Dyson Sphere |
| tests/unit/ui/widgets/test_preference_row.py | Test (NEW) | Phase 5 ✓ added: 15 tests covering construction (scalar + gas factors), display scaling (Pa→kPa, m/s²→g, fraction→%), `on_change` callback contract, per-factor cost label |
| tests/unit/ui/test_race_environment_panel.py | Test (NEW) | Phase 4 deleted legacy file; Phase 5 ✓ rewrote with 13 tests covering registry iteration, update_config + set_from_config flow, homeworld preset application, points label updates |
| tests/unit/strategy/data/test_homeworld_presets.py | Test (REWRITE) | Phase 5 ✓ replaced 211-line legacy file with 150-line registry-driven file: 16 tests covering JSON shape, per-preset content, partial-override semantic of `apply_preset_to_config` |
| tests/conftest.py | Test helper (MODIFY) | Phase 4: add `make_test_race` helper |
| docs/systems/strategy_layer.md | Docs (MODIFY) | Phase 6 ✓ added "## 7. Race Preferences & Habitability (PROJ-283)" section: factor registry pattern, weight table, adding-a-factor recipe, legacy → new field migration table, weighted geometric mean combiner. Updated stale Habitability bullet under `### Planet Modifier Effect Engine` and `### Atmosphere Modification Pipeline` |
| docs/04_SERVICES.md | Docs (MODIFY) | Phase 6 ✓ added `game/strategy/data/` + `game/strategy/formulas/` blocks to Service Directory; added "Race Habitability & Point-Buy (PROJ-283)" section with budget-method index and forward-link to strategy_layer.md §7 |
| CLAUDE.md | Docs (MODIFY) | Phase 6 ✓ added one-line "Habitability Factor Registry (PROJ-283)" callout to Key Patterns list |
| Projects/active_projects/PROJ-284/decisions.md | Cross-project (MODIFY) | Phase 6 ✓ added 2 PROJ-283 unblock confirmation entries (field shapes, API, commit hash baseline) |
| Projects/active_projects/PROJ-285/decisions.md | Cross-project (MODIFY) | Phase 6 ✓ added 2 PROJ-283 unblock confirmation entries (habitability formula API, weight allocation, registry tweaks) |
| game/ui/screens/gravity_target_editor.py | Production (MODIFY) | Phase 6 ✓ migrated `_set_species_ideal` from `getattr(rc, 'gravity_ideal')` to `rc.preferences["gravity"].setpoint / 9.81` |
| game/ui/screens/water_target_editor.py | Production (MODIFY) | Phase 6 ✓ migrated `_set_species_ideal` from `getattr(rc, 'water_ideal')` to `rc.preferences["water"].setpoint` |
| game/ui/screens/atmosphere_target_editor.py | Production (MODIFY) | Phase 6 ✓ rewrote `_set_species_ideal` to iterate `rc.preferences["gas.<formula>"].setpoint` directly; removed `GAS_NAME_TO_FORMULA` import + translation step |
| game/ui/screens/radiation_shield_editor.py | Production (MODIFY) | Phase 6 ✓ replaced legacy `threshold = 0.5 - (radiation_tolerance / 200)` formula in `_set_auto` with direct `rc.preferences["radiation"].setpoint` read |
| tests/unit/strategy/data/test_race_config.py | Test (REWRITE) | Phase 4 broke its import (deleted DEFAULT_ATMOSPHERE_PREFERENCES); Phase 6 ✓ surgically rewrote ~1000→~410 lines, 45 passing tests; retained Phase 1 preferences/repro/happiness coverage; closed the long-standing TestRaceConfigValidation tuple-unpacking bug |
| tests/unit/strategy/data/test_population_model.py | Test (MODIFY) | Phase 6 ✓ migrated `test_empire_race_config_serialization_roundtrip` from legacy `water_ideal`/`temperature_ideal` to `preferences["water"]`/`preferences["temperature"]` |
