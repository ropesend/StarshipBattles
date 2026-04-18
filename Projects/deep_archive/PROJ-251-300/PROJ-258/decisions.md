# PROJ-258: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-04-08 | Project initialized | Starting point for Dependency Injection - ApplicationContext and Singleton Migration |
| 2026-04-08 | Full migration (all 11 singletons), not partial | Partial migration leaves two access patterns (DI and singleton) creating confusion. Full migration gives a single consistent pattern. |
| 2026-04-08 | Wrapper-first approach for safety | Phase 1 creates ApplicationContext wrapping existing singletons. This means all existing .instance() calls still work, and we can validate the container design before committing to the full migration. Zero risk of breaking anything in Phase 1. |
| 2026-04-08 | One singleton per commit for bisectability | Each singleton migration is a self-contained change. If a regression appears, `git bisect` can pinpoint exactly which singleton migration caused it. This is critical for a 14783-test codebase. |
| 2026-04-08 | ApplicationContext is NOT itself a singleton | Making the container a singleton defeats the purpose. The caller (app.py or conftest.py) manages the instance lifetime. Tests create fresh contexts. Production creates one context at startup and passes it down. |
| 2026-04-08 | ApplicationContext placed in `game/context.py` (not `game/core/`) | The context imports from all layers (Core, Simulation, AI, UI). Placing it in Core would create upward dependencies violating the layer rules. `game/context.py` sits outside the layer hierarchy at the package root level. Factory methods use late imports. |
| 2026-04-08 | Migrate in layer order: Core -> AI -> UI | Core singletons have the most dependents and are simplest (no Pygame). AI is a small layer (1 singleton). UI singletons are the most complex (Pygame dependencies). This order builds confidence before tackling the hardest cases. |
| 2026-04-08 | SessionRegistryCache handled in Phase 5 (not Phase 2) | SessionRegistryCache is test infrastructure, not production code. It's a manual singleton (not using SingletonMeta). Migrating it alongside conftest.py simplification makes more sense. |
| 2026-04-08 | GameSettings uses `GameSettings()` not `.instance()` in call sites | GameSettings call sites use `GameSettings()` which resolves to `.instance()` via SingletonMeta.__call__. These still need migration but the grep pattern differs. |
| 2026-04-08 | Preserve all singleton class APIs during migration | Only the access pattern changes (from `.instance()` to context attribute). The classes themselves keep their existing methods (clear(), load_data(), etc.). No internal refactoring of service classes. |
| 2026-04-08 | SingletonMeta kept but unused after migration | We do not delete `game/core/singleton.py`. It may be useful for future use cases. We just remove all current usages. |
