# PROJ-156: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02-16 | Project initialized from Validation Review 3 | Review confirmed 12 deletes, 13 partial removals, disputed 5 (kept) |
| 2026-02-16 | 4-phase approach: Deletes → Partial → Merge → Cleanup | Ordered by risk: safest first, most complex last |
| 2026-02-16 | Merge order: Spatial → Collision → Behaviors → Adapter → Integration → Rules | Simplest merges first; bug-documenting eval rules last for highest care |
| 2026-02-16 | Path corrections applied from exploration | Review had 7 incorrect paths; all corrected in design.md |
| 2026-02-16 | Disputed items excluded from scope | Research tracker edge cases, 4 AI controller files, 23 refactor/ files, persistence.py rename, main_integration.py - all kept as-is per validation review |
| 2026-02-16 | Refactor/ → modifiers/ rename deferred | Cosmetic, no test removal value, separate project if desired |
| 2026-02-16 | Both TestLayoutConstants removed (research_scene + empire_treasury) | Both confirmed trivial: `> 0` checks and range bound checks on constants |
| 2026-02-16 | Baseline: 12,788 passed, 145 failed | 145 failures are pre-existing UI issues in build queue/cargo/transfer - unrelated to this project |
