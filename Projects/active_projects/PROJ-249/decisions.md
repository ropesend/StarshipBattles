# PROJ-249: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02-26 | Project initialized | Starting point for Reduce complexity: filter_ships (CC 36) |
| 2026-02-26 | Add tests BEFORE refactoring (Phase 1) | Safety analysis found missing test coverage for edge cases and status filter order - need tests as safety net |
| 2026-02-26 | Extract 7 helper functions | Structure analysis identified repeated binary filter pattern; extracting helpers reduces duplication and CC |
| 2026-02-26 | Keep late imports in helper functions | FleetCapabilityCalculator must be late-imported to avoid circular dependencies - cannot be moved to module level |
| 2026-02-26 | Preserve status filter order in _get_status_category | Order destroyed > derelict > damaged > undamaged is critical invariant; must be preserved exactly |
| 2026-02-26 | Use _passes_binary_filter shared helper | Pattern repeated 6+ times; single helper function eliminates duplication and centralizes logic |
| 2026-02-26 | Function interface stays unchanged | Single caller makes interface changes safe, but no need to change - keeps refactoring scope minimal |
