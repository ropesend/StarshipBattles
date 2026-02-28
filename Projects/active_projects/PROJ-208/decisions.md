# PROJ-208: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02-27 | Project created from review | Review identified 42 findings; 25 selected for remediation |
| 2026-02-27 | Severity-based phasing | Critical findings in Phase 1, Major in Phase 2, etc. |
| 2026-02-28 | Removed IssueBuildShipCommand (dead code) | No production callers - only tests/docs. Replaced by AddToConstructionQueueCommand which uses the actual queue-based system instead of planet.add_production(). |
