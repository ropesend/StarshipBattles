# PROJ-106: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02-11 | Project initialized | Starting point for Architecture Layer Violations |
| 2026-02-11 | 7 phases planned (not just grouping by finding) | Ordered by risk: simple fixes first, then legacy removal, then new abstractions, then audit. This lets each phase build confidence before the next. |
| 2026-02-11 | StrategyMetadataService in game.core (not game.strategy) | Consumed by both UI and AI layers. Core is the only layer both can depend on. StrategyManager stays in game.ai for AI-specific logic. |
| 2026-02-11 | ICamera as Protocol (not ABC or move-to-core) | Camera depends on pygame internally. Moving to core would require refactoring Camera. Protocol is structural typing -- zero cost, no inheritance needed. |
| 2026-02-11 | Keep DesignLoaderAdapter (reuse PROJ-43 work) | Adapter already exists. Just need consistency -- route all UI callers through it instead of creating a new abstraction. |
| 2026-02-11 | Selective getattr() removal in BattleUIService | Only remove for Ship properties confirmed in __init__. Keep for genuinely optional properties (source_file). Avoid breaking defensive code for edge cases. |
| 2026-02-11 | ADR-UI1-009 is a false positive | strategy_screen.py creates its OWN `self._facade` (line 76), not accessing `self.session._facade`. No private attribute cross-boundary access exists. |
| 2026-02-11 | ADR-UI2-003 (ShipThemeManager reset) already fixed | Code at line 91 already calls `cls._instance.clear()` before `cls._instance = None`. No changes needed. |
| 2026-02-11 | Deferred: ADR-UI2-006 (DI standardization) | Inconsistent DI patterns across services is a real issue but requires a dedicated project to establish conventions and migrate. Out of scope. |
| 2026-02-11 | Deferred: ADR-UI1-006 (Law of Demeter, 27 files) | 27 files with deep attribute chains is too broad. Would require accessor methods across the entire UI. Separate project needed. |
| 2026-02-11 | Deferred: ADR-UI1-007 (Strategy data objects in UI) | Requires DTO extraction for strategy domain objects. Related to PROJ-87 strategy tier decomposition. |
| 2026-02-11 | Deferred: ADR-UI1-008 and ADR-UI2-009 | TYPE_CHECKING imports are an acceptable architectural trade-off. Full DTO/viewmodel extraction is out of scope. |
| 2026-02-11 | ADR-UI2-010 (BattleOrchestrator) is intentional | BattleOrchestrator is explicitly designed as a cross-layer orchestrator. Its imports from game.ai are documented and intentional. Not a violation. |
| 2026-02-11 | God class findings deferred to PROJ-86/87/88/89 | 12 god class findings are out of scope. They are separate decomposition projects with their own plans. |
| 2026-02-11 | ADR-UI2-004 reclassified: not an architecture violation | game_renderer.py imports LayerType from game.core.constants (canonical location). The real issue is hardcoded magic numbers (0.1, 0.35 etc.) which is code quality, addressed in Phase 6. |
| 2026-02-11 | Component.mark_hp_cache_dirty() for all external callers | 6 files modify _hp_ratio_dirty directly. Add public method and update all callers. Internal reads within component module are acceptable. |
