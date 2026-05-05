# PROJ-366: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-05-05 | Project created | PROJ-354B's plan asserted codex was handling the production sink wiring. User clarified codex is NOT handling it. PROJ-354B Phases 5-6 are blocked on that wiring. PROJ-366 owns the prereq + the Phase 5-6 work end-to-end. |
| 2026-05-05 | `ReplayStore` constructed inside `bootstrap()` (not lazy) | The sink must be registered before any code path that calls `start_engine_from_spec` runs (`battle_runner.py:156` queries `get_default_capture_sink()` at battle start). Lazy construction risks losing the first battle's record. |
| 2026-05-05 | Coordinator constructed and started inside `bootstrap()` (not lazy) | Same reasoning — the coordinator must be subscribed before any battle persists. The first persisted record otherwise has no listener and verification is silently skipped. |
| 2026-05-05 | Add `replay_store` and `replay_verification_coordinator` fields to `BootstrapResult` | `RunLoop.run()` needs the coordinator reference for `shutdown_all_coordinators(timeout=...)`. Adding two frozen-dataclass fields is the canonical extension shape; no new global is introduced. |
| 2026-05-05 | DI inputs for the coordinator: fresh `AIControllerFactory()` + `get_default_registry_provider()` + `load_replay_settings()` + `load_combat_lab_design` fallback | Matches what `screen_router.py` already does for in-game combat. No new abstractions invented. |
| 2026-05-05 | Combat Lab fallback wired in `bootstrap()`, not at coordinator-call-site | Per PROJ-354B Phase 6 plan: the coordinator's `__init__` accepts `fallback_ship_builder`. Wiring at construction means every verification call uses the same fallback policy without per-call decisions. |
| 2026-05-05 | Add invariants 7 & 8 to `tests/unit/test_app_bootstrap_invariants.py` rather than a new file | The existing module is the canonical home for bootstrap-order invariants. Concentrating them in one place lets future readers see the full contract. |
| 2026-05-05 | Headless-vs-visual equivalence test boundary at `BattleController.start_from_spec`, NOT `BattleScreen` | Inherited from PROJ-354B r004 Codex correction. Avoids Pygame UI dependency in tests; both paths flow through `start_engine_from_spec` → `run_battle`, so equivalence here proves equivalence downstream. |
| 2026-05-05 | Verifier-import lint as a unit test (AST parse), not a static analyzer | Lightweight; no new tooling dependency; locks in PROJ-354B audit-remediation `27e297815`'s layer-violation fix (AR-001) so future changes can't silently re-introduce the violation. |
| 2026-05-05 | Update PROJ-354B `plan.md` Quick Status to "Complete (via PROJ-366)" for Phases 5-6 at project end | Keeps the older project's status accurate without forging signatures or rewriting the plan body. PROJ-366 is the canonical owner of the work delivered. |

## Audit Remediation
| Cycle | Date | Findings | Resolution |
|-------|------|----------|------------|
| 1 | | | |
