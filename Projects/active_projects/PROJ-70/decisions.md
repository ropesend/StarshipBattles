# PROJ-70: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02-07 | Project initialized | Starting point for Fleet Details Panel Enhancement |
| 2026-02-07 | Enhance `format_fleet_info()` instead of creating FleetReportPanel | The detail panel uses a simple HTML UITextBox - a full panel class (like PlanetReportPanel) is overkill. The formatting function approach matches the established pattern for stars, planets, etc. |
| 2026-02-07 | Show both speed (hex/turn) and fuel endurance | User confirmed they want both metrics displayed |
| 2026-02-07 | Group ships by `design_id`, sort by mass descending | User wants condensed list with "Devastator x 3" format, most massive first |
| 2026-02-07 | Aggregate cargo by iterating `cargo_contents` dicts | Future-proof: discovers all cargo types dynamically rather than hardcoding "passengers" |
| 2026-02-07 | Remove inline fleet formatting from strategy_ui.py | Eliminates duplication with `format_fleet_info()`, follows single-source-of-truth principle |
| 2026-02-07 | Use `getattr(fleet, 'construction_queue', [])` for BUILD orders | Defensive access since not all fleet contexts may have construction_queue |
