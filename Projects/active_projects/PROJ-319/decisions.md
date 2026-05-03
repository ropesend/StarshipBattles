# PROJ-319: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-05-02 | Project initialized | Starting point for Audit-shrink cleanup 2026-05-02 |
| 2026-05-02 | Acted only on findings that passed independent verification of `Reviews/results/2026-05-02_184210_audit_shrink/` | Audit-shrink reports have produced false positives in past runs (e.g. `_eval_least_armor_rule` reachable via `data/targeting_policies.json`); rejected and uncertain items recorded in `findings/verification_report.md` |
| 2026-05-02 | Skipped Phase 3 (dead classes / dead files) entirely | Source audit's Section 3 Tier 1 (dead files) and Tier 2 (dead classes) had zero verified items; `GroupTargetCoordinator` was the only candidate and the audit's own verifier downgraded it to PRODUCT_DECISION |
| 2026-05-02 | Surface zero-rejection rate from verifier explicitly in design.md | Source audit's own verifier corrected one CRITICAL misclassification and one false finding in the same run; a downstream skeptical pass that finds zero additional issues across 30 candidates is unusual and warrants per-task safety nets during implementation |
