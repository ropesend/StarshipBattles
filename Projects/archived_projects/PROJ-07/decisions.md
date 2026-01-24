# PROJ-07: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-01-21 | `expected_stats` is for load validation only | User explicitly stated this is the intended design |
| 2026-01-21 | Damage model: Gradual degradation to 30%, then inactive | Default behavior. Components define own thresholds in JSON. |
| 2026-01-21 | Warp drives require 100% HP to function | User requirement - any damage disables warp |
| 2026-01-21 | Armor does not degrade (effective at any HP) | User requirement - armor special case |
| 2026-01-21 | New utility module: `ship_stats_service.py` | Clean separation, easy to test |
| 2026-01-21 | Cache stats with invalidation on damage change | Balance accuracy and performance |
| 2026-01-21 | Fallback to expected_stats when no components found | Backward compatibility for test fixtures |
