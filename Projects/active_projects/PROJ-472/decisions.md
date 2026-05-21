# PROJ-472: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-05-20 | Project initialized | Starting point for Facade read-path migration: route game/ui access through strategy facade DTOs (deferred from PROJ-470) |
| 2026-05-20 | **Scope populated from PROJ-470 Protocol-06 revision.** FAC-001/FAC-002/FAC-003 (facade read-path migration) extracted here from PROJ-470. | Dual independent+Codex review (2026-05-20) found the facade read-path gap is a deliberately-deferred architecture migration (PROJ-382 / U1–U3), not a cleanup CRITICAL. Repo search confirmed 93 `game/ui/` files import `game.strategy` directly (`grep -rln "import game.strategy\|from game.strategy" game/ui/` → 93). A single-pass migration would balloon PROJ-470's conformance pass into a structural refactor. Per Protocol 07, the scope lives here as policy + read-path static guard + first migration slice; remaining sites migrate incrementally under the guard. |
| 2026-05-20 | Phase 1 scoped as **policy + read-path static guard + first slice**, NOT a 93-site single-pass migration. | Mirrors how the write-path guard (`tests/static_guards/test_facade_bypass_guard.py`) was rolled out. The first slice covers the densest FAC-002 sites (build_queue_screen, build_queue_controller, fleet_data_source) and the FAC-003 `StrategyScreen.session` consumers. The remaining ~85 sites are migrated in per-subpackage batches under the guard, decomposed into further phases/projects as scope demands. |
| 2026-05-20 | Read-path policy (option a read DTOs vs option b documented UI-safe read surface) is **deferred to Phase 1 Task 1** of this project — not pre-decided here. | The choice has real trade-offs (DTO surface/conversion cost vs convention+allowlist) and should be made by the implementing agent against live code, then recorded in Pattern #5 of `docs/02_PATTERNS.md`. PROJ-470 deliberately did not pre-commit the policy. |
