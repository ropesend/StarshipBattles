# PROJ-323: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-05-03 | Project initialized | Starting point for Test review P2 opportunistic polish 2026-05-02 |
| 2026-05-03 | Acted only on findings that passed independent verification of `2026-05-02_204633_test-review` (P2 tier) | OpenCode test-review confirms 94% of Phase-1 claims; a third skeptical pass with a different model catches blind spots the OpenCode verifier may share with its Phase-1 reviewer. P2 tier verification: 156 verified, 3 needs-rework, 1 rejected, 6 out-of-scope; rejected and out-of-scope items recorded in `findings/verification_report.md` |
| 2026-05-03 | Acted on OpenCode plan review (req_20260503_191424_2df3b4) — added cross-project dependency section, kept test_slots regression guard, kept count-based deprecated-code-removed tests as soft advisories, kept canonical CI tests in suite (not replaced by pre-commit hooks), removed below-threshold 2-test parametrize tasks (3.15/3.27/3.37), removed production-signature change from Task 5.22, added pre-condition for Task 1.8 line-range verification, and added Phase 2 class-level autouse caveat. | Plan-review found 37 findings (2 C, 13 M, 17 m, 5 I); 14 accepted and applied. Most minor + info findings deferred to implementation-time judgment. |
| 2026-05-03 | Pass 1 — addressed 27 substantive items across all 5 phases; 41 obsolete-skipped (PROJ-321 deletions); 43 deferred to pass 2 | Worker hit context budget at ~340 tool uses. Phase 3 (CAT-10 parametrize, 53 items) and Phase 5 (CAT-12 logic-heavy, 27 items) were the largest piles deferred. Net pass 1: -838 LOC. Tests green. |
| 2026-05-03 | Pass 2 — closed remaining 43 deferred items (23 substantive Phase 3 parametrizations + 9 substantive Phase 5 logic-heavy refactors + 10 leave-as-is/documented-intent + 1 documented-rationale deferral at Task 3.34) | Net pass 2: -580 LOC. All 5 phases now at 100% (149/149). Worker bypassed worktree and committed to parent branch via absolute paths. |
| 2026-05-03 | Branch `feat/03c-phase-aware-execution` pushed to GitHub (after PROJ-321 + PROJ-322 + PROJ-323 work all merged) | User directed: keep merge on current feat branch (not main); push to origin. |
