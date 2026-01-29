# PROJ-44: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-01-28 | Project initialized | Starting point for Code Quality & God Classes Refactoring |
| 2026-01-28 | Risk-based refactoring approach | User preference - tackle most tightly-coupled code first to minimize cascading changes |
| 2026-01-28 | Fresh start (not reviewing PROJ-12) | User preference - findings document already captures what remains to be done |
| 2026-01-28 | Unify damage threshold to 50% (Option A) | User preference - change strategy layer to use 50% threshold for consistency with simulation layer |
| 2026-01-28 | 9 phases planned | Break large refactor into manageable chunks: Quick Wins -> Services -> Ship Helpers -> Component -> Combat -> Battle -> UI -> Methods -> Cleanup |
