# PROJ-232: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02-26 | Project initialized | Starting point for Reduce complexity: filter_ships (CC 36) |
| 2026-02-26 | Extract helper functions approach | Preserves filter order clarity, easier to debug than data-driven approach |
| 2026-02-26 | Keep explicit loop (not list comprehension) | Status filter order is semantically critical; explicit continues make order visible |
| 2026-02-26 | Pass FleetCapabilityCalculator as parameter | Avoids repeated late imports inside helpers; single import at function top |
| 2026-02-26 | Add tests BEFORE refactoring (Phase 1) | Status hierarchy invariant must be tested to catch regressions |
| 2026-02-26 | Private helpers only | Public interface unchanged, existing 20+ tests work without modification |
| 2026-02-26 | Preserve status filter order exactly | Derelict implies damaged; checking derelict first is semantically required |
