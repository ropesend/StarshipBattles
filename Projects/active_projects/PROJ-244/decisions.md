# PROJ-244: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02-26 | Project initialized | Starting point for Reduce complexity: filter_ships (CC 36) |
| 2026-02-26 | Extract helper predicates approach | Preserves function interface, allows incremental extraction, each helper testable in isolation |
| 2026-02-26 | Add safety tests before refactoring | Status filter hierarchy is high-risk; need tests to catch regressions |
| 2026-02-26 | Keep lazy imports if needed | `FleetCapabilityCalculator` imported inside function to avoid circular imports; preserve pattern in helpers |
| 2026-02-26 | Extract generic `_passes_binary_filter()` | Pattern repeats 4+ times; single helper reduces code and complexity |
| 2026-02-26 | Preserve status filter ordering | destroyed > derelict > damaged > undamaged is a critical invariant |
