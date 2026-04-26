# PROJ-290 File Manifest

> Used for parallel execution conflict detection with PROJ-286..289.
> Update if implementation discovers additional files.

## Files

| File | Type | Notes |
|------|------|-------|
| game/strategy/engine/empire_economy_calculator.py | Production (MODIFIED) | Added `total_population_upkeep: Dict[str, float]` field to `EmpireEconomySnapshot`. `EmpireEconomyCalculator.__init__` now accepts optional `economy_config` + `race_registry`; lazy-constructs `PlanetEconomyProjector` inside new `_aggregate_population_upkeep` method. Backward-compat preserved (legacy callers leave the field as `{}`). |
| game/ui/panels/empire_treasury_panel.py | Production (MODIFIED) | `_get_expense_rows` conditionally inserts a "Population Upkeep" row BEFORE "Total" when `snapshot.total_population_upkeep` has non-zero values. Cell values pre-negated (drain visualization). |
| game/ui/screens/strategy_detail_fmt.py | Production (MODIFIED) | New module-level helper `format_uncolonized_habitability_for_empire(planet, empire, race_registry)`. `format_planet_info` signature extended with keyword-only `empire` + `race_registry` kwargs. Imports `score_planet_for_race`. |
| game/ui/panels/planet_report_panel.py | Production (MODIFIED) | `__init__` + `update_planet` accept + store + forward `empire` + `race_registry` kwargs. `update_planet` falls back to construction-time values when called without fresh deps. |
| game/ui/screens/empire_panel_window.py | Production (MODIFIED) | Constructor accepts `race_registry` kwarg. `_build_treasury_tab` threads `get_default_economy_config()` + `race_registry` into `EmpireEconomyCalculator`. |
| game/ui/screens/planet_list_window.py | Production (MODIFIED) | Constructor accepts `race_registry=None` kwarg; forwards to `PlanetReportPanel`. |
| game/ui/screens/strategy_window_manager.py | Production (MODIFIED) | Both `_open_planet_list_window` and `_open_empire_panel_window` pull `facade.get_race_registry()` and thread it through. |
| tests/unit/strategy/engine/test_empire_economy_calculator.py | Test (MODIFIED) | New `TestPopulationUpkeepAggregation` class — 7 tests. Also added `total_population_upkeep == {}` default assertion to `TestEmpireEconomySnapshot.test_empty_snapshot_defaults_to_empty_dicts`. |
| tests/unit/ui/panels/test_empire_treasury_panel.py | Test (MODIFIED) | New `TestPopulationUpkeepRow` class — 5 tests covering hidden-when-empty, hidden-when-all-zero, single/multi-resource render, and insertion-order before Total. |
| tests/unit/ui/screens/test_strategy_detail_fmt.py | Test (MODIFIED) | New `TestUncolonizedHabitabilityForEmpire` (6 tests) + `TestFormatPlanetInfoUncolonizedHabitabilitySection` (4 tests) classes. |
| docs/systems/strategy_layer.md | Docs (MODIFIED) | §9 addendum: new `### Treasury & Planet Detail UI Integration (PROJ-290)` subsection covering both UI surfaces + production wiring. |
| docs/systems/production_system.md | Docs (MODIFIED) | Blockquote callout under `## Habitability Multiplier (PROJ-285)` linking to the new strategy_layer.md section. |
