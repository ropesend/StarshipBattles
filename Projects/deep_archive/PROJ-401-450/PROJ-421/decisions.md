# PROJ-421: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-05-13 | Project initialized | Starting point for Legacy removal — Pattern #30 slot cleanup in strategy_event_router (2026-05-13) |
| 2026-05-13 | Bundled findings from `2026-05-13_194106_legacy-audit` by removal cluster `pattern30_slot_cleanup` per user direction | Bundling driven by removal cluster (one project per system being eradicated) rather than severity to maximize deletion-PR coherence; full bundling discussion in findings/bundling_decisions.md |
