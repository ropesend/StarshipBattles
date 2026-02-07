# PROJ-54: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02-01 | Project initialized: Universal Planet Report Component | Consolidate duplicate planet display implementations across 4 UI contexts |
| 2026-02-01 | Use Strategy layer bottom-right panel as "golden" template | User confirmed this is the most complete implementation and will be extended in future |
| 2026-02-01 | Each planet has specific image file assigned during generation | User confirmed planets get specific `image_id` assigned (not procedural) - need to fix loading bug |
| 2026-02-01 | Build Queue link button should only appear in Strategy viewport and Planet List | Build Queue and Colonize windows shouldn't link to themselves (avoid circular navigation) |
| 2026-02-01 | Replace Strategy UI inline implementation with PlanetReportPanel | User chose consolidation over keeping duplicate code (consistency > minimal risk) |
| 2026-02-01 | Position Build Queue button BELOW the planet report panel | User chose vertical layout - cleaner, easier to implement than integrated or side-by-side |
| 2026-02-01 | Upgrade Colonize window to use full PlanetReportPanel | User chose richer display over simple text-only (more information helps colonization decisions) |
| 2026-02-01 | Fix planet image bug FIRST, then consolidate panels | User chose two-phase approach - fixes bug for all contexts immediately, consolidation builds on working foundation |
| 2026-02-01 | Enhance PlanetReportPanel with backward-compatible parameters | Add `portrait_surface` to __init__, `show_complexes` parameter - enables reuse without breaking existing code |
| 2026-02-01 | Keep action buttons external to panel (not embedded) | Follows single-responsibility principle - panel is display-only, screens manage interactions |
| 2026-02-01 | Delete duplicate `format_planet_info()` from strategy_ui.py | Eliminate code duplication - use single source in `strategy_detail_fmt.py` |
| 2026-02-01 | 6-phase implementation strategy | Sequential phases allow independent testing, image fix first prevents building on broken foundation |

