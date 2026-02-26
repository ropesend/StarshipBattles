# PROJ-239: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02-26 | Project initialized | Starting point for Reduce complexity: filter_ships (CC 36) |
| 2026-02-26 | Function is refactorable, not skipped | Multi-agent analysis confirmed complexity from duplication, not inherent algorithmic needs |
| 2026-02-26 | Add edge case tests before refactoring | Safety analysis identified 4 untested edge cases that could mask bugs |
| 2026-02-26 | Use predicate helper extraction approach | Structure analysis showed 4x duplicated binary filter pattern ideal for extraction |
| 2026-02-26 | Preserve filter application order | Capability filters must run before status categorization to match current behavior |
| 2026-02-26 | Create single status classifier function | Simplifies mutually exclusive status logic, reduces risk of breaking exclusivity |
| 2026-02-26 | Move FleetCapabilityCalculator import outside loop | Performance improvement - currently imported N*M times inside nested loops |
