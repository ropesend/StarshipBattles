# PROJ-241 File Manifest

> Generated during /proj-start. Used by /proj-parallel for conflict detection.
> Updated if implementation discovers additional files.

## Files

| File | Type | Notes |
|------|------|-------|
| game/simulation/components/component.py | Production | Slim down to facade; delegate modifiers/abilities to managers |
| game/simulation/components/modifier_manager.py | Production | Convert from static namespace to stateful delegate |
| game/simulation/components/ability_manager.py | Production | Move ability index building in; add has_ability_with_tag() |
| game/simulation/components/component_stats_calculator.py | Production | Add FORMULA_DEFAULTS mapping, parse_formulas(), apply_formula_defaults() |
| tests/unit/simulation/components/test_modifier_manager.py | Test | Extend — stateful delegate API tests |
| tests/unit/simulation/components/test_ability_manager.py | Test | Extend — stateful delegate API tests |
| tests/unit/simulation/components/test_component_stats_calculator.py | Test | Extend — formula parsing tests |
| tests/unit/regressions/test_bug_regressions_2026_01.py | Test | Update _apply_base_stats call to use ComponentStatsCalculator directly |
| docs/02_PATTERNS.md | Production | Add Component delegate pattern to Pattern #5 |
| docs/01_ARCHITECTURE.md | Production | Update component architecture if documented |
