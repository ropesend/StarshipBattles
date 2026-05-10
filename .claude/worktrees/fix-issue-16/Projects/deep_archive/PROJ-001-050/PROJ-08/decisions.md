# PROJ-08: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-01-21 | Per-turn consumption spread across 100 ticks (amount/100 per tick) | Smoother depletion, consistent with tick-based architecture |
| 2026-01-21 | Auto-disable components when out of resources | Ships continue operating, just lose capability |
| 2026-01-21 | Player can manually toggle components + auto-disable | Full control plus automatic safety |
| 2026-01-21 | Resource registry in `data/resources.json` (no display metadata) | Separation of concerns - UI config is separate |
| 2026-01-21 | Warp costs via `ResourceConsumption` with `trigger: 'warp_jump'` | Consistent with other trigger patterns |
| 2026-01-21 | Keep backward-compatible wrapper methods temporarily | Gradual migration, avoid breaking changes |
