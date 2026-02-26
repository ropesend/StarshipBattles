# PROJ-245: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02-26 | Project initialized | Starting point for Reduce complexity: filter_ships (CC 36) |
| 2026-02-26 | Use predicate extraction approach | Binary filter pattern repeats 5 times; extracting to named predicates reduces CC while improving readability |
| 2026-02-26 | Add edge case tests BEFORE refactoring | Safety analysis identified missing coverage for combined filters and edge cases; tests prevent regressions |
| 2026-02-26 | Keep filter evaluation order unchanged | Order matters for short-circuit optimization and status priority chain |
| 2026-02-26 | Preserve late imports in helpers | `FleetCapabilityCalculator` must stay inside function to avoid circular imports |
| 2026-02-26 | Extract 5 helper predicates | One per filter type: warp, spaceyard, cargo, special capability, status |
| 2026-02-26 | Convert to list comprehension | After extracting helpers, main function becomes simple list comp with AND chain |
