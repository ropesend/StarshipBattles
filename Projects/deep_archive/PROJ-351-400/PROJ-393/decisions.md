# PROJ-393: Decisions Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-05-08 | Project initialized | Starting point for Legacy removal — Test-injection fallbacks + comment cleanups (2026-05-07) |
| 2026-05-08 | Bundled findings from `2026-05-07_220621_legacy-audit` by removal cluster `test_injection_and_misc_legacy` per user direction | Catch-all bundle for legacy paths and fallbacks not covered by other clusters. UNCERTAIN-included: LEG-02-006 (view=None branch), LEG-03-023 (Combat Lab vars — PROJ-270 archived), LEG-03-024 (sprite pattern with asset-scan-first). INFO-included: LEG-02-005, LEG-02-017. UNCERTAIN-excluded: LEG-02-001 (Game.running test backdoor still needed). Full bundling discussion in `findings/bundling_decisions.md`. |
