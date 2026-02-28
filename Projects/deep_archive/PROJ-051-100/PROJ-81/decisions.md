# PROJ-81: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02-08 | Project initialized | Starting point for Sector Build Queue Window Fixes |
| 2026-02-08 | Target display: 2560x1600 minimum, optimized for 4K | User specified. All layout calculations should assume this minimum. |
| 2026-02-08 | Fix cost calculation by loading Ship object, not from DesignMetadata | `DesignMetadata._calculate_resource_cost()` reads from design JSON which lacks cost data. Ship object has correct `construction_cost` via `ShipStatsCalculator`. Loading ship is the same pattern already used by `refresh_design_report()`. |
| 2026-02-08 | Widen Build Yards panel to 700px | At 2560px minimum display, this leaves 580px for Build Queue column - plenty of room. User requested 2-3x wider (280 -> 700 is 2.5x). |
| 2026-02-08 | Add `update_stats(ship)` call to `DesignReportPanel.update_design()` | Same fix as BUG-04 in Workshop right_panel.py. The `_build_layout(ship)` creates rows with "--" defaults but never populates values. |
