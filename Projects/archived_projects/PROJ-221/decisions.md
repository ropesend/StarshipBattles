# PROJ-221: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-03-14 | Project initialized | Starting point for Build Queue Configurable Columns & Column Swap Fix |
| 2026-03-14 | Use existing TableColumnManager — no new column manager class | User directive: same system as PlanetListWindow and other lists |
| 2026-03-14 | Columns: order (#), item name, turns, 5× per-turn spend, 5× remaining cost | User wants order position, per-turn spend, and remaining cost |
| 2026-03-14 | Keep full-screen layout, embed VirtualTable in queue panel area | Less disruptive than converting to windowed panel |
| 2026-03-14 | Build order column is display-only (#1, #2, #3) | Keep existing drag-to-reorder for actual reordering |
| 2026-03-14 | Per-turn spend calculated dynamically from total_cost, resources_consumed, and build_rate | cost_per_tick field is not populated on queue items; proportional formula from ProductionEngine |
| 2026-03-14 | Supersedes BUG-96 | Resource display issues resolved by proper column rework |
| 2026-03-14 | Test baseline: 13180 passed, 2 skipped | Established before planning |
