# PROJ-104: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02-10 | Project initialized | Starting point for Cyclomatic Complexity Reduction - Critical Functions |
| 2026-02-10 | Sub-method extraction only, no new EventRouter classes | User preference: simpler approach, less file churn, keeps all logic in one place |
| 2026-02-10 | Extract sub-methods, not dispatch tables (dicts) | User preference: sub-methods are more readable and debuggable for step-through |
| 2026-02-10 | Order phases by CC score, highest first | User preference: get the biggest CC reduction wins first |
| 2026-02-10 | Keep ShipStatsCalculator main loop intact | Strict phase ordering between Phases 1-5 means we can't rearrange or parallelize. Extract only the body of each phase, keeping the sequential orchestration in calculate() |
| 2026-02-10 | TargetEvaluator rule handlers return (val, match) tuples | The `required` rule early termination (`return -inf`) must stay in the main loop, not inside extracted handlers. Handlers just compute values. |
| 2026-02-10 | All TargetEvaluator extracted methods are @staticmethod | Matches existing class pattern — TargetEvaluator has no instance state, all methods are static |
| 2026-02-10 | Keep small event handlers inline in FormationEditor | MOUSEWHEEL (2 lines), KEYDOWN (4 lines), MOUSEBUTTONUP (5 lines), MOUSEMOTION (1 line) — too small to justify extraction overhead |
