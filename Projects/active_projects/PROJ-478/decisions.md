# PROJ-478: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-05-22 | Project initialized | Starting point for Test review P0 dead-trivial cleanup 2026-05-20 |
| 2026-05-22 | Acted only on findings that passed independent verification of `2026-05-20_210550_test-review` (P0 tier) | OpenCode test-review confirms 94% of Phase-1 claims; a third skeptical pass with a different model catches blind spots the OpenCode verifier may share with its Phase-1 reviewer. P0 tier verification: 44 verified, 9 needs-rework, 0 rejected, 5 out-of-scope; rejected and out-of-scope items recorded in `findings/verification_report.md` |
| 2026-05-22 | Phantom-method tests (S01-F002/F003/F004) classified as NEEDS_REWORK rather than DELETE | The production methods `save_ship`, `load_ship`, `on_select_target_pressed` exist (without the underscore prefix the test uses); rewriting preserves coverage of the real flow instead of dropping it entirely |
| 2026-05-22 | Codex tooling tests (S02-F022, S10-F019) classified as NEEDS_REWORK with "relocate" rather than "delete" | Tests have legitimate purpose (agent skill metadata validation) but mis-located in `tests/unit/`. Moving them preserves coverage of skill correctness while clearing the unit-test directory |
| 2026-05-22 | TDD-pending issue17 tests (S09-F005) handled via `@pytest.mark.skip` not deletion | The `_spy_invalidate` helper guards a real planned API (`invalidate_widget_caches`) due in PROJ-410 Phase 2. Skipping preserves the TDD intent; deletion would lose the contract |
