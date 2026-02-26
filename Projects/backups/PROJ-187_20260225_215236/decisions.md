# PROJ-187: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02-24 | Project initialized | Starting point for Strategy Orders Tick-Based Action System |
| 2026-02-24 | Add OrderType.WARP now (don't defer) | User wants it for future-proofing. Even without fog-of-war, explicit warp point control is useful |
| 2026-02-24 | action_time stored on component abilities in components.json | User preference: data-driven, moddable. Field on ability dict, not a separate JSON file. Default=1 if absent |
| 2026-02-24 | Field name is `action_time` not `action_cost` | User specified: "cost doesn't really indicate time" |
| 2026-02-24 | Speed-0 fleets skip action ticks (same as movement) | Speed-0 = stations/satellites/planetary complexes. Only BUILD is valid. Fleets with BUILD have positive speed |
| 2026-02-24 | Cancel penalty = progress loss only | User confirmed: cancelling discards FleetOrder + execution_progress. No extra penalty |
| 2026-02-24 | WARP target = HexCoord of warp point to enter | User confirmed. Navigation service resolves exit point. Simplest approach, consistent with MOVE |
| 2026-02-24 | Superweapon action_time values | Stellerator=5, Dyson Sphere=5, Planet Imploder=3, Open/Close Warp Point=3, Self-Destruct=1, Colony Pods=1 |
| 2026-02-24 | Eradicate _process_end_turn_orders() entirely | Per project convention: "When a new system replaces an old one, ERADICATE the old system completely" |
| 2026-02-24 | BUILD order unchanged | Already handled by ProductionEngine per-tick. Not a "fleet action" in the traditional sense |
| 2026-02-24 | Baseline: 12,366 passed, 1 skipped, 0 failures | Established 2026-02-24 |
