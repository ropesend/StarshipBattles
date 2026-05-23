# PROJ-480: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-05-22 | Project initialized | Starting point for Test review P2 opportunistic polish 2026-05-20 |
| 2026-05-22 | Acted only on findings that passed independent verification of `2026-05-20_210550_test-review` (P2 tier) | OpenCode test-review confirms 94% of Phase-1 claims; a third skeptical pass with a different model catches blind spots the OpenCode verifier may share with its Phase-1 reviewer. P2 tier verification: 145 verified, 4 needs-rework, 4 rejected, 32 out-of-scope; rejected and out-of-scope items recorded in `findings/verification_report.md` |
| 2026-05-22 | Phase sequencing: CAT-9 → CAT-8 → CAT-10 → CAT-11 → CAT-12 | Lowest risk first (simplification with already-defined helpers), then complexity reduction, then high-volume parametrize batch, then assertion polish, then logic-heavy rewrites that may surface real flakiness |
| 2026-05-22 | CAT-10 clusters with <3 members rejected during verification | Parametrize overhead is rarely worth it for 2-element clusters; OpenCode flagged several such cases (e.g. some 2-test pairs already covered by P1 CAT-4 work) |
| 2026-05-22 | CAT-10 clusters where members exercise different pipeline stages rejected | S02-F005 pipeline_unification (each test = distinct ability class), S06-F005 superweapon_order_pop_matrix (per-weapon Order target structure differs). Parametrize would obscure semantic coverage boundaries |
| 2026-05-22 | Coordination notes inline in tasks where work overlaps with PROJ-478 or PROJ-479 | ~10 P2 tasks reference cross-project work. Marked with `_(coord)_` so implementer doesn't double-touch a file. Sequence P0 → P1 → P2 |
| 2026-05-22 | CAT-9 / CAT-11 / CAT-12 findings flagged "no action — well-suited" retained as tasks for traceability | S14-F005 (REJECTED, 5-line loop not logic-heavy), S12-F022/F023/F024 (acceptable shared utilities), S13-F025 (test names document branches), S14-F020 (already-optimally parametrized), S16-F014 (well-factored factories) — keep visible so audits can trace why no work was done |
