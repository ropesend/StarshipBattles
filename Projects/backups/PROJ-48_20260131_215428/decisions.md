# PROJ-48: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-01-28 | Project initialized | Starting point for Testing Infrastructure Overhaul |
| 2026-01-28 | Address all 36 issues | User requested comprehensive overhaul, not partial fixes |
| 2026-01-28 | Split all files >500 LOC | User selected aggressive splitting over conservative approach |
| 2026-01-28 | Infrastructure only, no new coverage tests | Coverage gaps (TC-01 to TC-09) will be separate project |
| 2026-01-28 | Exclude 5 pre-existing test failures | Failures in `test_builder_io_integration.py` are unrelated to infrastructure |
| 2026-01-28 | 8-phase approach | Logical grouping by type of change minimizes risk of breaking tests |
| 2026-01-28 | Phase 1 focuses on critical issues | Must fix disabled tests and isolation before other changes |
| 2026-01-28 | Create subdirectories for monoliths >1000 LOC | Files this large benefit from dedicated directory with shared conftest |
| 2026-01-28 | Keep `tests/strategy/` until Phase 6 | Directory moves are risky; postpone until structure stabilized |
