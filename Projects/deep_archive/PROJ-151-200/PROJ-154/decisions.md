# PROJ-154: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02-16 | Project created from validated review findings | Review v3 identified ~85 candidates; validation review confirmed 22 actionable findings |
| 2026-02-16 | Respect all 6 DISPUTED findings — do not touch | UI-10 (import smoke tests): cheap circular import insurance. UI-12 (battle panels): cleanup not removal. STR-8 (fleet order transfer): complementary not duplicate. STR-11 (production repro): real regression tests. STR-12 (battle resolver): valuable interface contracts. STR-13 (engine events): complementary event tests. |
| 2026-02-16 | Migrate unique tests before deleting source files | Ensures zero coverage loss. Applies to UI-2 (2 tests), STR-1 (16 tests), STR-3 (1 test), UI-8 (3 tests) |
| 2026-02-16 | Phase order: pure deletes → migrate+delete → partial edits → relocation | Simplest/safest operations first. Partial edits have highest risk of accidentally breaking kept tests. Relocation is standalone. |
| 2026-02-16 | STR-3: Keep root version, delete data/ version | Root uses real Fleet/ShipInstance objects (higher fidelity). Data/ version uses MagicMock for everything (lower quality despite more lines). |
| 2026-02-16 | STR-2: Keep data/ version, delete root version | Data/ version has 50 tests (749 lines) vs root's 22 tests (196 lines). Data/ is a strict superset. |
| 2026-02-16 | UI-5/UI-13: Keep relationship/range/type tests, remove pure positivity checks | `assert X > 0` for static integer constants is trivially obvious. But `assert TITLE >= NAME >= STAT` catches hierarchy violations. `assert 0 <= ALPHA <= 255` catches pygame crashes. `test_all_constants_are_integers` catches type regressions. |
| 2026-02-16 | UI-7: Keep 6 unique edge case tests, remove 14 duplicates/trivial | Unique tests cover: unknown event types, None click clearing, right-click no-clear, F3 overlay, min/max speed boundaries. These are not tested elsewhere. |
