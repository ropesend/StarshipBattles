# PROJ-323: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-05-03 | Project initialized | Starting point for Test review P2 opportunistic polish 2026-05-02 |
| 2026-05-03 | Acted only on findings that passed independent verification of `2026-05-02_204633_test-review` (P2 tier) | OpenCode test-review confirms 94% of Phase-1 claims; a third skeptical pass with a different model catches blind spots the OpenCode verifier may share with its Phase-1 reviewer. P2 tier verification: 156 verified, 3 needs-rework, 1 rejected, 6 out-of-scope; rejected and out-of-scope items recorded in `findings/verification_report.md` |
