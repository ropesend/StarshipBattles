# PROJ-157: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02-16 | Project initialized as PROJ-157 (new, not reusing PROJ-154/155) | User preference for clean start |
| 2026-02-16 | Include Phase 4 (old directory trees) in this project | User chose to do all 4 phases together rather than deferring |
| 2026-02-16 | Search for test_ai_behaviors.py (found at `tests/unit/ai/test_ai_behaviors.py`) | File existed but at different path than review assumed |
| 2026-02-16 | KEEP all DISPUTED files - do not touch | Validation reviews identified 10+ items wrongly flagged for removal by original reviewers |
| 2026-02-16 | File-by-file verification for old directories, NOT wholesale deletion | Old files use real objects (integration) vs new files using MagicMock (unit) - need to verify each pair |
| 2026-02-16 | Skip items already cleaned up (17 files confirmed missing) | No need to re-verify or re-delete what's already gone |
| 2026-02-16 | Merge unique tests BEFORE deleting any duplicate file | Zero tolerance for coverage loss - always preserve unique tests |
