# PROJ-227: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02-26 | Project initialized | Starting point for Reduce complexity: filter_ships (CC 36) |
| 2026-02-26 | Function is refactorable | All 3 review agents agree: single caller, comprehensive tests, clear extraction points |
| 2026-02-26 | Add test fortification phase before refactoring | Safety analysis identified 5 missing test categories that should be covered first |
| 2026-02-26 | Extract `_passes_binary_filter` helper | Repeated 4x with identical logic; extraction removes 12-16 branches from main function |
| 2026-02-26 | Extract `_get_ship_status` helper | Separates categorization from filtering; reduces cascade complexity |
| 2026-02-26 | Keep late imports in helper scope | FleetCapabilityCalculator must be late-imported to avoid circular dependencies |
| 2026-02-26 | Preserve capability-then-status filter order | Invariant identified by safety analysis; changing order would alter behavior |
