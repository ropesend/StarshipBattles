# PROJ-279: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-04-17 | Project initialized | Starting point for Combat Lab Spec Compiler — Explicit Composition (delete to_spec monkey-patch) |
| 2026-04-17 | Approach: delete `to_spec` entirely (Option A) | User chose "Delete to_spec entirely (Recommended)". Scenarios describe a setup; spec construction is the runner's responsibility. Matches Battle Setup pattern (BattleSetupState has no to_spec). Rejected: late-import method (still couples scenario to compiler) and DI injection (adds construction ceremony for every scenario) |
| 2026-04-17 | Sequencing: AFTER PROJ-278 | PROJ-278 changes the role-tagging shape on ShipSpec (adds `scenario_role` field). Doing this project before PROJ-278 means we'd touch the same compiler file twice |
| 2026-04-17 | Add documented authoring rule against `to_spec` on future scenarios | Without an explicit rule, the next contributor might re-introduce the convenience method. Doc rule lives in `docs/guides/simulation_testing.md` |
