# PROJ-80: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02-08 | Project initialized | Starting point for Unify Design Details Panel |
| 2026-02-08 | Extract-and-Delegate pattern: new `DesignStatsPanel` widget | Clean separation of concerns. Portrait rendering is fundamentally different between workshop (side-by-side with controls) and build queue (full-width). The shared piece is the stats grid. |
| 2026-02-08 | `StatRow` moves to `design_stats_panel.py` | Colocate with its primary consumer. Both `right_panel.py` and `design_report_panel.py` will import from the new location. |
| 2026-02-08 | Always two-column layout (no adaptive/single-column mode) | User confirmed workshop layout is canonical. Build queue panel widens to 750px to match. |
| 2026-02-08 | Build Queue panel width: 750px (match workshop) | User chose full parity over compromise. Build queue list gets narrower (~440px on 1920 screen) but still usable. |
| 2026-02-08 | `show_requirements` boolean flag controls Requirements/Recommendations sections | Simple, clear API. Workshop passes `True`, build queue passes `False`. |
| 2026-02-08 | Use `get_logistics_rows(ship)` everywhere (not static JSON keys) | Dynamic version handles all resource types including non-standard ones. DesignReportPanel currently uses static `fuel_logistics`/`ammo_logistics`/`energy_logistics` which is less complete. |
| 2026-02-08 | Build Cost section shown in both panels | Workshop currently lacks it. Both contexts benefit from seeing construction costs. |
| 2026-02-08 | Portrait code stays separate in each parent | Portrait handling differs significantly and doesn't benefit from unification. |
