# PROJ-77: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02-07 | Project initialized | Starting point for Event Log System |
| 2026-02-07 | Use existing log_event() callback pattern | Non-invasive, already exists in game/core/logger.py, no new dependencies |
| 2026-02-07 | Modal popup at turn start | User preference - non-intrusive, can be dismissed to continue playing |
| 2026-02-07 | Save all events (full history) | User preference - allows reviewing history from many turns ago |
| 2026-02-07 | Combat summary only | User preference - keep log concise, no detailed battle replay |
| 2026-02-07 | Filter tabs (All/Combat/Production/Colonies) | User preference - allow filtering by event type |
| 2026-02-07 | Add "Log" button to top bar | Required to reopen log after dismissing |
| 2026-02-07 | Store EventLog in GameSession | Natural owner of game state, handles persistence via to_dict()/from_dict() |
| 2026-02-07 | Facade returns List[Dict] not Event objects | UI should receive immutable DTOs, not domain objects |
| 2026-02-07 | Events stored newest-first in display | User expectation - most recent events at top |
| 2026-02-07 | Category as string enum not complex hierarchy | Simple filtering, extensible for future event types |
| 2026-02-07 | No max_events limit initially | User requested full history; can add limit later if needed |
