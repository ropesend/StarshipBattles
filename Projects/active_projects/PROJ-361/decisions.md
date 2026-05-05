# PROJ-361: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-05-04 | Project initialized | Top finding (P1) of Strategy Layer Tech Debt Review (Reviews/results/2026-05-05_strategy-layer-tech-debt-review/report.md, finding #1) |
| 2026-05-04 | Renumbered from PROJ-351 to PROJ-361 | Merge-conflict collision on PROJ-351..360 from commit 97a96e7d0; user chose to leave existing IDs alone and start fresh at 361 |
| 2026-05-04 | No `IRegistryProvider` adapter class — pass `registries` directly | `GameRegistries` already implements the Protocol per PROJ-211 (`game/core/registry.py:66-112`). An adapter would be dead code. |
| 2026-05-04 | Preserve `get_default_registry_provider()` as `None`-fallback | PROJ-306 explicitly permits strategy layer to call it; we are correcting the asymmetry of ignoring an injected `registries`, not removing the default. |
| 2026-05-04 | Single-phase project, no decomposition | Bug fix scope: one production line + one regression test. Decomposing into phases would be ceremonial. |
| 2026-05-04 | New regression test uses marker-design fixture pattern | Inject a `GameRegistries` containing a design name not in defaults; assert the materialized ship contains it. Simplest end-to-end proof. |
