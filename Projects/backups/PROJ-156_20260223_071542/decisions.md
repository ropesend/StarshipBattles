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
| 2026-02-19 | PROJ-157 overlap assessed — Phases 1 and 2 mostly done | PROJ-157 independently completed all Phase 1 deletes and Phase 2 Tasks 2.1–2.4. Task 2.5 (TestLayoutConstants) was missed. |
| 2026-02-19 | Phase 3 merges NOT done by PROJ-157 | Despite PROJ-157 listing some files as "Already Cleaned Up", all 5 source files for Pairs 1,2,4,5,6 still exist on disk. No merges were performed. |
| 2026-02-19 | 3 KiteBehavior tests lost by PROJ-157 Pair 3 merge | PROJ-157 deleted test_ai_behaviors.py but only merged 4/7 tests. 3 KiteBehavior tests (opt_dist_calculation, opt_dist_min_clamp, branching_kite_maintain) must be recovered from git commit b1edd82b^. Added Task 3.0 for recovery. |
| 2026-02-19 | Updated baseline to ~12,185 tests | Post-PROJ-157 baseline per its audit. Pre-existing failures reduced to 143 (from 145). |
| 2026-02-19 | Updated unique test counts from code review | Actual comparison of source vs target test names shows fewer truly unique tests than originally estimated for Pairs 1,2,4 (many renamed duplicates). Pairs 5,6 still have ~12 unique each. |
| 2026-02-19 | target_with_hp fixture identified as unused | In tests/unit/ai/target_evaluator/conftest.py — never referenced by any test. Added to Phase 4 cleanup. |
