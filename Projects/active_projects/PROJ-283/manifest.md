# PROJ-283 File Manifest

> Generated during project initialization. Used for parallel execution conflict detection.
> Update if implementation discovers additional files.

## Files

| File | Type | Notes |
|------|------|-------|
| game/strategy/data/environmental_preference.py | Production (NEW) | Phase 1 ✓ added: `EnvironmentalPreference` dataclass with validation |
| game/strategy/data/habitability_factors.py | Production (NEW) | Phase 1 ✓ added: `HabitabilityFactor` + `FACTOR_REGISTRY` (7 scalar + 10 gas) |
| game/strategy/data/race_config.py | Production (MODIFY) | Phase 1 ✓ added `preferences` field + `base_reproduction_rate` + `base_happiness` + `_validate_preferences()`; Phase 4 deletes legacy fields |
| game/strategy/data/race_point_budget.py | Production (MODIFY) | Phase 3 rewrite around registry; Phase 3 adds reproduction cost curve |
| game/strategy/data/homeworld_presets.py | Production (MODIFY) | Phase 5: new preference shape |
| game/strategy/formulas/habitability.py | Production (MODIFY) | Phase 2 adds v2; Phase 4 promotes to canonical |
| game/strategy/engine/population_engine.py | Production (MODIFY) | Phase 4: read `base_reproduction_rate` |
| game/strategy/engine/superweapon_order_processor.py | Production (MODIFY) | Phase 4: Dyson Sphere atmosphere seeding |
| game/ui/widgets/preference_row.py | Production (NEW) | Phase 5: reusable row widget |
| game/ui/panels/race_environment_panel.py | Production (MODIFY) | Phase 5: full rebuild, iterate registry |
| data/races/*.json | Data (DELETE) | Phase 4: user-confirmed disposable |
| tests/unit/strategy/data/test_environmental_preference.py | Test (NEW) | Phase 1 ✓ added: 12 tests, all passing |
| tests/unit/strategy/data/test_habitability_factors.py | Test (NEW) | Phase 1 ✓ added: 39 tests, all passing |
| tests/unit/strategy/data/test_race_config.py | Test (MODIFY) | Phase 1 ✓ added 11 new tests (preferences, base_reproduction_rate, base_happiness, validation). Phase 4 drops legacy fields. |
| tests/unit/strategy/formulas/test_habitability_v2.py | Test (NEW) | Phase 2 |
| tests/unit/strategy/formulas/test_habitability.py | Test (MODIFY) | Phase 4: update for v1 deletion |
| tests/unit/strategy/data/test_race_point_budget_v2.py | Test (NEW) | Phase 3 |
| tests/unit/strategy/data/test_race_point_budget.py | Test (MODIFY) | Phase 3: remove aptitude costs for deleted aptitudes |
| tests/unit/strategy/engine/test_population_engine.py | Test (MODIFY) | Phase 4: use `base_reproduction_rate` |
| tests/unit/strategy/engine/test_superweapon_order_processor.py | Test (MODIFY) | Phase 4: Dyson Sphere seeding uses preferences |
| tests/integration/strategy/test_superweapon_integration.py | Test (MODIFY) | Phase 4: Dyson Sphere |
| tests/unit/ui/widgets/test_preference_row.py | Test (NEW) | Phase 5 |
| tests/unit/ui/test_race_environment_panel.py | Test (MODIFY) | Phase 5: full rewrite to iterate registry |
| tests/unit/strategy/data/test_homeworld_presets.py | Test (MODIFY) | Phase 5: new preset shape |
| tests/conftest.py | Test helper (MODIFY) | Phase 4: add `make_test_race` helper |
| docs/systems/strategy_layer.md | Docs (MODIFY) | Phase 6: factor registry docs |
| docs/04_SERVICES.md | Docs (MODIFY) | Phase 6: services catalog |
| CLAUDE.md | Docs (MODIFY) | Phase 6: optional factor-registry pattern callout |
