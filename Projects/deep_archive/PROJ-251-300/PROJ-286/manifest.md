# PROJ-286 File Manifest

> Used for parallel execution conflict detection with PROJ-287..290.
> Update if implementation discovers additional files.

## Files

| File | Type | Notes |
|------|------|-------|
| data/economy.json | Data (REWRITE) | New schema: `population_consumption: Dict[resource_id, rate]`. Values: organics 0.001, metals 0.0001, radioactives 0.00001 |
| game/strategy/config/economy_config.py | Production (MODIFY) | EconomyConfig: replace `population_food_resource` + `food_per_pop_per_turn` with `population_consumption: Dict[str, float]`. Add `primary_resource` property. Keep `population_food_resource` as read-only shim for PROJ-289-until-landed UI |
| game/strategy/data/colony_species_config.py | Production (MODIFY) | Add `last_consumption_ratios: Dict[str, float]` (transient, not serialized). Convert `last_food_ratio` to a `@property` returning `min(last_consumption_ratios.values())` or 1.0 when empty |
| game/strategy/engine/organics_consumption_engine.py | Production (MODIFY) | Iterate `economy.population_consumption` dict; drain each resource; write per-resource ratio into `cfg.last_consumption_ratios` |
| tests/unit/strategy/config/test_economy_config.py | Test (MODIFY) | Migrate tests to new dict-shaped schema |
| tests/unit/strategy/data/test_colony_species_config.py | Test (MODIFY) | Migrate `last_food_ratio` pre-set tests to `last_consumption_ratios` dict; add property-read tests |
| tests/unit/strategy/engine/test_organics_consumption_engine.py | Test (MODIFY) | Migrate 12 tests to multi-resource dict-shaped economy + new ratio dict |
| tests/unit/strategy/engine/test_happiness_engine.py | Test (VERIFY) | No changes expected — reads `cfg.last_food_ratio` which is now a property. Confirm all 12 tests still green |
| tests/unit/strategy/engine/test_population_engine.py | Test (VERIFY) | No changes expected — same. Confirm `TestFoodRatioAndDecline` still green after the `cfg.last_food_ratio = X` pattern migration |
| tests/integration/strategy/test_demographics_loop.py | Test (MODIFY) | 5 tests — replace `last_food_ratio` pre-sets with `last_consumption_ratios` dicts |
| docs/systems/strategy_layer.md | Docs (MODIFY) | Update §8 (Colony Demographics Loop) to describe the multi-resource consumption schema + MIN aggregation contract |
| docs/04_SERVICES.md | Docs (MODIFY) | Update PROJ-284 catalog entry to reflect multi-resource signature on OrganicsConsumptionEngine + the new ColonySpeciesConfig field |
