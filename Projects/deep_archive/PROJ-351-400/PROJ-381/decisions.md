# PROJ-381: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-05-08 | Project initialized | Starting point for Error handling cleanup — strategy/ui/assets/sim (2026-05-07) |
| 2026-05-08 | Bundled all 27 actionable findings from `2026-05-07_220225_error-audit` into one project (single-project bundle) per user direction | Bundling driven by code relatedness rather than severity to maximize implementation continuity. V=26 verified (+1 user-included from UNCERTAIN) is below the protocol's 30-item single-project threshold; a split was considered (foundation vs presentation, or boundary vs hygiene) but each candidate split produced one bundle below 6 items, which is overkill for the volume. Full bundling discussion in `findings/bundling_decisions.md`. |
| 2026-05-08 | Included ERR-04-007 (`star_generation_config.py:192` over-broad catch tuple) despite UNCERTAIN verifier verdict, per user choice | User accepts the risk of losing the silent defaults fallback for malformed config files; the trade is "raise on bad data" rather than "return defaults on bad data". Reasoning preserved in `findings/bundling_decisions.md`. |
| 2026-05-08 | Excluded ERR-03-005 (REJECTED), B-8 + LLM-2 (OUT_OF_SCOPE) per verifier evidence | ERR-03-005's preceding-line comments communicate intent clearly enough that an automated comment-on-same-line scanner is the only thing flagging it. B-8 is caller responsibility (DesignLibrary doesn't own schema). LLM-2 has no actual leak per the audit's own evidence — exception messages are already redacted. Full evidence in `findings/verification_report.md`. |
| 2026-05-08 | Phase 3 Task 3.9 (B-4 facade conversion) couples to Phase 1 (B-5 UI catch) — Phase 1 catches `EnginePhaseError` initially, Phase 3 re-wraps as `TurnFailedError` and updates the UI catch | Could have been done atomically in Phase 1, but the audit ranked B-5 as CRITICAL and B-4 as MINOR. Shipping the crash fix first (without waiting for the layering polish) maximizes the user-visible value-per-phase. The cross-phase coupling is documented here so the Phase 3 implementer remembers to update the Phase 1 catch. |
