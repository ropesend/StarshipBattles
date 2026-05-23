# PROJ-484: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-05-22 | Project initialized | Starting point for Legacy removal — dead re-export sweep (2026-05-20) |
| 2026-05-22 | Bundled findings from `2026-05-20_210635_legacy-audit/` by removal cluster `dead_reexports` per user direction | Bundling driven by removal cluster (one project per system being eradicated) rather than severity to maximize deletion-PR coherence; full bundling discussion in findings/bundling_decisions.md |
