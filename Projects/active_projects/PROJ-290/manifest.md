# PROJ-290 File Manifest

> Used for parallel execution conflict detection with PROJ-286..289.
> Update if implementation discovers additional files.

## Files

| File | Type | Notes |
|------|------|-------|
| game/strategy/engine/empire_economy_calculator.py | Production (MODIFY) | Add `total_population_upkeep: Dict[str, float]` to `EmpireEconomySnapshot`; populate via `PlanetEconomyProjector` (PROJ-288) |
| game/ui/panels/empire_treasury_panel.py | Production (MODIFY) | Add a new "Population Upkeep" row in the expenses section; hidden when all values zero |
| game/ui/screens/strategy_detail_fmt.py | Production (MODIFY) | Add `empire` + `race_registry` kwargs to `format_planet_info`; emit uncolonized-habitability section when `planet.owner_id is None` |
| game/ui/panels/planet_report_panel.py | Production (MODIFY) | Thread `empire` + `race_registry` kwargs through `update_planet` to `format_planet_info` |
| game/ui/screens/strategy_screen.py | Production (MODIFY) | Pass `scene.current_empire` + `facade.get_race_registry()` when calling `update_planet` on an uncolonized planet |
| tests/unit/strategy/engine/test_empire_economy_calculator.py | Test (MODIFY) | `TestPopulationUpkeepAggregation` — sums across colonies, per resource, empty-empire edge case |
| tests/unit/ui/panels/test_empire_treasury_panel.py | Test (MODIFY / NEW) | Row rendering + hidden-when-zero behavior |
| tests/unit/ui/screens/test_strategy_detail_fmt.py | Test (MODIFY) | `TestUncolonizedHabitabilityForEmpire` — scoring, ordering, missing-race skip, empty empire fallback |
| docs/systems/strategy_layer.md | Docs (MODIFY) | §9 addendum: Treasury populace-upkeep line + uncolonized-planet habitability list |
| docs/systems/production_system.md | Docs (MODIFY) | Cross-reference: Treasury now shows population upkeep alongside construction upkeep |
