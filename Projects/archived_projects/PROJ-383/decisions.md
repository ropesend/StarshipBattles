# PROJ-383: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-05-08 | Project initialized | Starting point for Legacy removal — command_handlers.py shim eradication (2026-05-07) |
| 2026-05-08 | Bundled findings from `2026-05-07_220621_legacy-audit` by removal cluster `command_handlers_shim` per user direction | Bundling driven by removal cluster (one project per system being eradicated) rather than severity to maximize deletion-PR coherence; full bundling discussion in `findings/bundling_decisions.md` |
