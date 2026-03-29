# PROJ-235: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-03-28 | Project initialized | Starting point for TurnEngine Phase Timing Cleanup |
| 2026-03-28 | Use `_time_phase()` helper method, not decorator or context manager | Codebase has no existing `*args/**kwargs` wrapper patterns; helper methods are the established convention for extracted logic in engine files |
| 2026-03-28 | Keep BUG-109 logging as extracted helper, don't remove it | Bug is ROOT CAUSE CONFIRMED but logging is low-overhead `logger.debug`; preserves observability for related future issues |
| 2026-03-28 | Define TICKS_PER_TURN in `turn_engine.py`, import into `production_engine.py` | Turn engine owns the tick loop; dependency mapper verified zero circular import risk |
| 2026-03-28 | Simplify turn-level BUG-109 blocks to match tick-level format | Extra fields (facilities count, ships count) were only needed during initial triage; simplified form is consistent |
| 2026-03-28 | Accept BUG-109 timing shift in harvesting phase | Current code includes BUG-109 logging inside harvesting timing; after refactor it's outside. Makes timing consistent across all phases. Acceptable because timing is diagnostic-only. |
| 2026-03-28 | Don't update sub-engine hardcoded `100.0` divisors | `resource_management_engine.py`, `resupply_engine.py`, `environmental_hazard_engine.py` use `/ 100.0` — out of scope for this focused refactoring |
| 2026-03-28 | Don't touch test files | User explicitly requested no test code changes |
