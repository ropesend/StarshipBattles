# PROJ-99: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02-10 | Separate EmpireEconomyCalculator in strategy layer | Testable without pygame, reusable by AI, clean data/UI separation |
| 2026-02-10 | Replicate harvest/maintenance formulas (don't call engines) | Calculator is read-only for display; engines modify state during turns |
| 2026-02-10 | Scrollable species cards for Population tab | User chose this over list+detail. Each species gets full card section. |
| 2026-02-10 | Placeholder rows for future income/expense sources | User wants Ships, Trade, Tribute, Remote Mining showing 0 |
| 2026-02-10 | 4 phases: Calculator → Treasury Panel → Window → Integration | Bottom-up: data first, then rendering, then window, then wiring |
| 2026-02-10 | Window size 90% of screen | Matches existing large windows (planet list, fleet report, build queue) |
| 2026-02-10 | Resource icons loaded once and cached in window | Avoids reloading on tab switch; 5 small images |
