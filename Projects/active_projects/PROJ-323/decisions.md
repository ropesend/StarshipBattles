# PROJ-323: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-05-03 | Project initialized | Starting point for Test review P2 opportunistic polish 2026-05-02 |
| 2026-05-03 | Acted only on findings that passed independent verification of `2026-05-02_204633_test-review` (P2 tier) | OpenCode test-review confirms 94% of Phase-1 claims; a third skeptical pass with a different model catches blind spots the OpenCode verifier may share with its Phase-1 reviewer. P2 tier verification: 156 verified, 3 needs-rework, 1 rejected, 6 out-of-scope; rejected and out-of-scope items recorded in `findings/verification_report.md` |
| 2026-05-03 | Acted on OpenCode plan review (req_20260503_191424_2df3b4) — added cross-project dependency section, kept test_slots regression guard, kept count-based deprecated-code-removed tests as soft advisories, kept canonical CI tests in suite (not replaced by pre-commit hooks), removed below-threshold 2-test parametrize tasks (3.15/3.27/3.37), removed production-signature change from Task 5.22, added pre-condition for Task 1.8 line-range verification, and added Phase 2 class-level autouse caveat. | Plan-review found 37 findings (2 C, 13 M, 17 m, 5 I); 14 accepted and applied. Most minor + info findings deferred to implementation-time judgment. |
