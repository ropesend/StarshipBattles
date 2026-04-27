# PROJ-309: Decisions Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-04-26 | Project initialized | User: "take the top 10 files and break them down in a way that makes them difficult to grow" |
| 2026-04-26 | Top-10 by line count, NOT by dependency-graph importance | Simple objective rule; user's instruction was explicit |
| 2026-04-26 | 500-LOC ceiling is the published convention | User: "if files grow past 500 LOC point they should be broken apart" — round number, defensible cutoff |
| 2026-04-26 | Test files NOT subject to the 500-LOC rule | Long test files are often acceptable; the rule is about production-source maintainability |
| 2026-04-26 | Decomposition direction is per-file, decided in Phase 2 | Each file has different reasons for being big; one-size-fits-all splits produce bad architecture |
| 2026-04-26 | Re-export shim (Option A) vs caller migration (Option B) is per-file | Phase 2 design step decides per file based on caller surface |
| 2026-04-26 | Sequence after PROJ-298 + PROJ-306 | Both projects touch some of the target files; avoid merge conflicts |
| 2026-04-26 | Phase 3 may span weeks/months | 10 separate refactors; each sub-phase is independent |
| 2026-04-26 | The other 52 files >500 LOC are OUT OF SCOPE | The convention will pull them in eventually; don't bundle |
| 2026-04-26 | Tooling (`check_file_size.py`, CI rule) OUT OF SCOPE | Capture as follow-up; this project is the convention + 10 refactors |
