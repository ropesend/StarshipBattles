# PROJ-240: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02-26 | Project initialized | Starting point for Reduce complexity: filter_ships (CC 36) |
| 2026-02-26 | Add edge case tests BEFORE refactoring | Safety analysis found missing tests for empty list, None cargo, combined filters |
| 2026-02-26 | Extract binary filter pattern to helper | Repeated 5x, eliminates ~40 lines of duplication |
| 2026-02-26 | Keep late imports in helper functions | FleetCapabilityCalculator must stay as late import to avoid circular imports |
| 2026-02-26 | Preserve filter evaluation order | Order (warp→spaceyard→cargo→special→status) is critical invariant |
| 2026-02-26 | Preserve status priority order | destroyed→derelict→damaged→undamaged is mutually exclusive chain |
| 2026-02-26 | Extract separate helper per filter type | Better than single mega-helper; easier to test and maintain |
| 2026-02-26 | Use _passes_X_filter naming convention | Consistent naming, returns bool for continue/include decision |
