# PROJ-248: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02-26 | Project initialized | Starting point for Reduce complexity: filter_ships (CC 36) |
| 2026-02-26 | Add test fortification phase before refactoring | Safety analysis found 5 missing critical tests; must add before code changes |
| 2026-02-26 | Extract filter predicates approach | Repeated binary filter pattern (4x) allows clean extraction; reduces nesting |
| 2026-02-26 | Preserve status check order in dedicated function | Status cascade (destroyed->derelict->damaged->undamaged) is critical invariant |
| 2026-02-26 | Keep lazy imports inside helper functions | FleetCapabilityCalculator has circular import risk if moved to module level |
| 2026-02-26 | Use generic `_passes_binary_filter` utility | DRY principle - same pattern appears 4 times with identical structure |
| 2026-02-26 | Convert main loop to list comprehension | After extracting predicates, single `_passes_all_filters` predicate enables clean comprehension |
