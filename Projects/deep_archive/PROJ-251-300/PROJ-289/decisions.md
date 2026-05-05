# PROJ-289: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-04-18 | Project initialized | Starting point for Planet Report Panel Per-Species + Per-Resource UI |
| 2026-04-18 | Per-species layout: indented sub-block, 4 visual rows per species (header + 3 metric lines) | User-confirmed 2026-04-18. Alternative was flat 4-line-per-species layout; sub-block is more scannable for multi-species colonies. |
| 2026-04-18 | Metrics per species: habitability (raw 0-1), happiness (raw 0-3), growth (signed %), food ratio (raw), food allocation (× multiplier) | User-confirmed: "use raw numbers for now - percentage for reproduction". Growth is the only percentage; other decimals are raw. |
| 2026-04-18 | Growth number = per-capita `projected_growth_rate` from PROJ-288, expressed as a signed percentage | User-confirmed: "reproduction should be a function of the base rate modified by food allocation and habitability. Can be very negative if conditions are really bad." Predicted-next-turn, not historical. |
| 2026-04-18 | Happiness category label: Content / Settled / Unhappy at thresholds 1.5 / 0.5 | PROJ-283 `base_happiness` default = 0.5, so "Settled" is baseline. Threshold 1.5 for "Content" = base × food × habitability on an ideal planet. Tunable. |
| 2026-04-18 | Resource grid: 4 columns (Harvest / Upkeep / Yard / Net), all signed | User-confirmed: "show the whole row. Net per turn after all production and all expenses - build queues and population costs". Yard = "current projected queue consumption, if there is a resource shortage it doesn't need to account for that it can just go negative". |
| 2026-04-18 | Keep existing stockpile "current / max" display as a compact row BELOW the projection grid | Removing it loses signal. Compact row (one line with all resources) preserves visibility without doubling the grid's vertical footprint. |
| 2026-04-18 | Non-food resources show 0 in the upkeep column | Per PROJ-286's MIN aggregation, only resources in `economy.population_consumption` contribute to upkeep. UI shows 0 (not blank) so the alignment of the grid stays readable. |
| 2026-04-18 | Net column color: green positive, red negative | Existing `game/ui/colors.py` conventions. Default (white) when zero. |
| 2026-04-18 | Ordering of species = largest count first | User-confirmed pattern; matches PROJ-288's `ColonyDemographicView.species` ordering. |
| 2026-04-18 | `PlanetReportPanel.update_planet` gains optional `view` kwarg; `format_planet_info` gains optional `view` kwarg | Backward compat — existing tests / legacy call sites that don't have a facade pass None and get the legacy rendering (simpler). New call sites pass the view. |
| 2026-04-18 | Blocked on PROJ-286 + PROJ-287 + PROJ-288 | Consumes multi-resource config (PROJ-286), race registry (PROJ-287), and `ColonyDemographicView` DTO (PROJ-288). |
