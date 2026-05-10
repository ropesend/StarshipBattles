# PROJ-382: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-05-08 | Project initialized | Starting point for Pattern conformance — Facade integrity, EventBus injection, doc drift, LOC sweep (2026-05-07) |
| 2026-05-08 | Bundled findings from `2026-05-07_220452_pattern-audit` into a single project ordered Critical → Major → Minor → Strategic → LOC | Bundling driven by code relatedness (layer + pattern-area locality across simulation/strategy/ui) rather than severity. V<30 ⇒ single-project default per Protocol 18. Full bundling discussion in `findings/bundling_decisions.md` |
| 2026-05-08 | Deferred U1 (~127 UI command DTO imports), U2 (40 service imports), U3 (26 systems imports) to a future dedicated PROJ | These read-side bypasses are real but would dwarf the rest of the project. Audit itself classifies UI command DTO imports as "partial bypass / pass-through". Logged as deferred in `findings/verification_report.md`. |
| 2026-05-08 | Included U4 (rename builder EventBus → WorkshopEventBus), U5 (require ProductionSpawner.registries), U6 (document Strategy Config Singleton variant) per user direction during Phase D | U4 removes long-standing import-ambiguity surface despite Pattern #10's documented-intentional status. U5 tightens DI in strategy layer (Pattern #3 is simulation-scoped but stylistic improvement). U6 lands as doc-add even though only 1 site uses the variant — the variant has explicit in-code justification. |
| 2026-05-08 | Phase 5 (LOC ceiling sweep) covers 5 of 14 oversized files — only those NOT already in an active PROJ | Files already covered by an active PROJ (race_summary_panel, battle_screen, ship_detail_panel, production_engine, workshop_event_router, build_queue_panel_factory, battle_panels, registry, spec_compiler) stay with their owning project to avoid duplicate work. |
| 2026-05-08 | VER-001 / PAT-02-001 (`GameSession.get_default_registry_provider`) treated as out-of-scope | Audit's own verifier marked DISPUTED; Pattern #3 limits the restriction to simulation-layer code, and `GameSession` is strategy-layer. If the team wants to extend the restriction, that's a separate Pattern #3 update, not a code fix. |
| 2026-05-08 | Phase 1 includes a mandatory AST static-guard test against `session.handle_command` in UI | Pattern #5 facade-bypass is an architectural-decay path; without an enforcement gate the next PR can silently re-introduce it. PROJ-306's static-guard against `get_default_registry_provider` in simulation is the canonical reference shape. |
