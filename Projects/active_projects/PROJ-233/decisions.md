# PROJ-233: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02-26 | Project initialized | Starting point for Reduce complexity: filter_ships (CC 36) |
| 2026-02-26 | Test fortification required before refactoring | Safety analysis found 6+ missing test coverage areas; must establish safety net first |
| 2026-02-26 | Extract binary filter helper first | Repeated 4x in code; highest duplication reduction with lowest risk |
| 2026-02-26 | Keep late imports at helper function level | `FleetCapabilityCalculator` cannot move to module level due to circular import risk |
| 2026-02-26 | Preserve filter evaluation order | Capability filters must run before status filters to maintain existing behavior |
| 2026-02-26 | Status categories are mutually exclusive | destroyed > derelict > damaged > undamaged priority must be preserved |
| 2026-02-26 | Use list comprehension in refactored filter_ships | Declarative style, cleaner code, CC reduced to 2-3 |
