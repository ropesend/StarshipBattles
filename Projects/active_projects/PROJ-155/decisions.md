# PROJ-155: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02-16 | Project created from validated review findings | 4 validation reviews confirmed 47 safe removals, disputed 30 items, modified 32 items |
| 2026-02-16 | Only implement CONFIRMED and MODIFIED findings | DISPUTED findings were proven to have real value by validators — do not remove |
| 2026-02-16 | Merge-before-delete for all MODIFIED findings | ~20 unique tests must be preserved in target files before source deletion |
| 2026-02-16 | File-by-file deletion for old directories, not wholesale | Validation review 4 warned old files may use real objects vs new files' MagicMock — verify each pair |
| 2026-02-16 | Include Phase 3 (old directory trees) in this project | User chose full cleanup over deferral |
| 2026-02-16 | Keep Tasks 2.12/2.13 as conditional | Spatial extended + collision system merges not yet verified to exist, execute if present |
| 2026-02-16 | Do NOT delete builder/systems/ai conftest.py files | These have fixture imports; validation claims they're unused but needs verification |
| 2026-02-16 | Do NOT delete reproduce_scaling.py | Validated as legitimate pytest test with real assertions despite misleading name |
| 2026-02-16 | Do NOT delete any repro_*.py files at root | Validators proved claimed replacements test DIFFERENT functionality |
| 2026-02-16 | Phase ordering: delete > merge > old dirs > partial > structural | Safest items first, highest-risk (old dirs) after simpler cleanups established pattern |
| 2026-02-16 | Baseline: 12,790 passed, 143 pre-existing failures | Pre-existing failures unrelated to this project; track to ensure no increase |
