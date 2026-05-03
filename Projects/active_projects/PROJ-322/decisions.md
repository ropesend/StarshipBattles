# PROJ-322: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-05-03 | Project initialized | Starting point for Test review P1 brittle-bloated remediation 2026-05-02 |
| 2026-05-03 | Acted only on findings that passed independent verification of `2026-05-02_204633_test-review` (P1 tier) | OpenCode test-review confirms 94% of Phase-1 claims; a third skeptical pass with a different model catches blind spots the OpenCode verifier may share with its Phase-1 reviewer. P1 tier verification: 111 verified, 4 needs-rework, 1 rejected, 3 out-of-scope; rejected and out-of-scope items recorded in `findings/verification_report.md` |
| 2026-05-03 | Acted on OpenCode plan review (req_20260503_191353_9376a0) — committed Task 5.15 to deletion, scoped Task 5.10 with integration-test pre-step, fixed Task 5.23 to use public API, switched Task 4.3 to mocked clock, added Phase 3→Phase 5 ordering, fixed Task 5.7 boundary classification, specified DUP-001 fixture shape, added cross-project dependency section, and applied 4 minor refinements (N-001..N-004). | Plan-review found 19 findings (1 C, 8 M, 6 m, 4 I); 14 accepted and applied. N-005 partial (added warning, did not split phase). N-006 + I-* skipped (cosmetic / positive). |
