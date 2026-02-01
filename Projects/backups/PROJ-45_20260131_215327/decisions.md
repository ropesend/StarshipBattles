# PROJ-45: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-01-28 | Project initialized | Starting point for Error Handling and Exception Management Refactor |
| 2026-01-28 | AI targeting: Convert to proper exception handling with logging | User prioritizes maintainability and debuggability over backward compatibility. Keep fallbacks but make errors visible. |
| 2026-01-28 | Formula system: Raise `FormulaException` instead of returning 0 | User stated backward compatibility is irrelevant; prefers explicit errors for easier maintenance and debugging. |
| 2026-01-28 | Create `ErrorCode` enum for standardized error codes | User approved. Enables programmatic error handling and consistent error categorization. |
| 2026-01-28 | Fix ALL 46+ broad exception handlers systematically | User wants comprehensive fix, not partial. Will also create documentation guidelines for future development. |
| 2026-01-28 | Custom exceptions import nothing from game.* | Avoids circular dependencies. All game modules can safely import from `game.core.exceptions`. |
| 2026-01-28 | 7-phase implementation plan | Ordered by dependency: Foundation → Core → Simulation → AI → Strategy → UI → Docs. Each layer builds on previous. |
| 2026-01-28 | Use json_utils.py as reference implementation | Already follows best practices: specific exception types, appropriate logging levels, context in messages. |
