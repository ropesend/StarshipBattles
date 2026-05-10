# PROJ-310: Decisions Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-04-26 | Project initialized | User: "I want a focused review on the > 3 layers deep nesting" |
| 2026-04-26 | Read-only investigation; output is a review document | Per user directive; deep nesting can be legitimate, so categorization must precede action |
| 2026-04-26 | Threshold: 4+ indent levels (Python convention says max 3) | CLAUDE.md "Code Quality" already states "Avoid deep nesting (max 3 levels)" |
| 2026-04-26 | Test files excluded from analysis | The 4-level convention is for production-source maintainability; test files have different ergonomics |
| 2026-04-26 | AST-based metric, not regex | Regex on indentation depth misses control-flow nesting (e.g., comprehensions, walrus). AST is the correct tool |
| 2026-04-26 | Recommendations may seed multiple follow-up projects | A single "deep nesting cleanup" project would be over-scoped. Output is a roadmap |
| 2026-04-26 | Cross-reference with PROJ-309 | Decomposition there will dent these numbers; recommendations should not duplicate work |
| 2026-04-26 | Cross-reference with `radon` (PROJ-297 deliverable) | Complexity metrics correlate with nesting; worth checking |
| 2026-04-26 | Verified deep-nesting count: 389/563 files = 69.1% (NOT 373/67% as in original review) | Independent grep + Python script |
