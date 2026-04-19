# PROJ-288 File Manifest

> Used for parallel execution conflict detection with PROJ-286, 287, 289, 290.
> Update if implementation discovers additional files.

## Files

| File | Type | Notes |
|------|------|-------|
| game/strategy/formulas/colony_output.py | Production (MODIFY) | Add `projected_growth_rate(planet, pop, race_config, cfg) -> float` alongside existing `planet_habitability_multiplier` |
| game/strategy/services/planet_economy_projector.py | Production (NEW) | `ResourceProjection` frozen dataclass + `PlanetEconomyProjector` service. Contains MOVED `compute_planet_production` logic |
| game/strategy/facade/dto/colony_demographic_view.py | Production (NEW) | Frozen `ColonyDemographicView` + `SpeciesDemographicView` DTOs |
| game/strategy/facade/strategy_session_facade.py | Production (MODIFY) | Add `get_colony_demographic_view(planet_id) -> Optional[ColonyDemographicView]` |
| game/ui/panels/planet_report_panel.py | Production (MODIFY) | Replace local `compute_planet_production` (~line 498) with `from game.strategy.services.planet_economy_projector import compute_planet_production` |
| tests/unit/strategy/formulas/test_colony_output.py | Test (MODIFY) | Add `TestProjectedGrowthRate` class — parity with engine, per-capita semantics, starvation cases |
| tests/unit/strategy/services/test_planet_economy_projector.py | Test (NEW) | Full coverage: harvest, upkeep (multi-resource from PROJ-286), yard (single + multi-queue), net = sum |
| tests/unit/strategy/facade/test_colony_demographic_view.py | Test (NEW) | DTO shape + facade method returns expected data |
| tests/integration/strategy/test_growth_rate_equivalence.py | Test (NEW) | `PopulationEngine._grow_species` delta == `projected_growth_rate * pop.count` (within int-cast tolerance) |
| docs/04_SERVICES.md | Docs (MODIFY) | Add `PlanetEconomyProjector` + `ColonyDemographicView` entries; cross-reference `projected_growth_rate` |
| docs/systems/strategy_layer.md | Docs (MODIFY) | Add a pointer under §8 / §9 to the new projection helpers |
