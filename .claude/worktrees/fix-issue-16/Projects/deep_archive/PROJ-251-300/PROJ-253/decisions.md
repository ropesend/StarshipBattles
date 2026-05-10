# PROJ-253: Decisions Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-04-06 | Dirty flag on Ship, not on individual components | Ship is the unit of stat recalculation. Component-level dirty flags would add complexity without proportional benefit — the pipeline is all-or-nothing per ship. |
| 2026-04-06 | Debug-mode assertion to catch stale-cache bugs | Run full recalc every N ticks in debug builds and assert against cached values. Catches dirty-flag omissions without production cost. |
| 2026-04-06 | Planet energy cache invalidated by events, not polled | Build/destroy/toggle are discrete events with clear call sites. Polling would just be the current approach with extra steps. |
