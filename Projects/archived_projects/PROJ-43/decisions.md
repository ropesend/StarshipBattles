# PROJ-43: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-01-28 | Project initialized | Starting point for Architecture Layer Violations Remediation |
| 2026-01-28 | Re-verify all previous fixes (PROJ-11, PROJ-38) | User preference for thoroughness over trusting previous completions |
| 2026-01-28 | Full Constructor DI for TurnEngine | User wants extensibility and maintainability for future complexity; willing to invest extra effort now |
| 2026-01-28 | Split Phase 2 into sub-phases (2A, 2B, 2C) | User preference for manageable chunks: Setup screens, Builder screens, Workshop/Battle screens |
| 2026-01-28 | Test baseline established | 5198 passed, 1 failed (pre-existing), 3 skipped, 28327 warnings |
