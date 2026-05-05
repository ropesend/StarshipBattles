# PROJ-289 File Manifest

> Used for parallel execution conflict detection with PROJ-286, 287, 288, 290.
> Update if implementation discovers additional files.

## Files

| File | Type | Notes |
|------|------|-------|
| game/ui/screens/strategy_detail_fmt.py | Production (MODIFY) | `format_planet_info` gains optional `view: Optional[ColonyDemographicView]` kwarg; per-species loop rewritten to emit indented sub-block when view is provided |
| game/ui/panels/planet_report_panel.py | Production (MODIFY) | `update_planet(planet, registries=None, view=None)` signature change; `_build_resource_grid` + `_update_resource_grid` rewritten to use 4-column (harvest/upkeep/yard/net) layout from `view.resource_projections`. Compact stockpile summary retained as separate row |
| game/ui/utils/formatters.py | Production (MODIFY) | Add `format_signed_float(value, decimals=1)` helper |
| game/ui/screens/strategy_screen.py (or wherever the panel is instantiated) | Production (MODIFY) | Call `self.facade.get_colony_demographic_view(planet.id)` and pass the view into `update_planet` |
| tests/unit/ui/screens/test_strategy_detail_fmt.py | Test (MODIFY / NEW) | Add `TestPerSpeciesSubBlock`: view=None legacy fallback, single-species, multi-species, largest-first ordering, category labels |
| tests/unit/ui/panels/test_planet_report_panel.py | Test (MODIFY / NEW) | Add `TestResourceGrid4Column`: 4 columns built, correct formulas, signed formatting, zero-upkeep non-food rows |
| tests/unit/ui/utils/test_formatters.py | Test (MODIFY) | Tests for `format_signed_float` |
| docs/systems/strategy_layer.md | Docs (MODIFY) | §8 addendum: planet report panel shows per-species sub-blocks + per-resource projections |
