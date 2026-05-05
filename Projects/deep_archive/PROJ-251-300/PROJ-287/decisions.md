# PROJ-287: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-04-18 | Project initialized | Starting point for Race Registry Facade + Empire.resident_species |
| 2026-04-18 | `IRaceRegistry` protocol has ONE method: `get_race(race_id) -> Optional[RaceConfig]` | Narrow protocol per CLAUDE.md "minimum dependencies" principle. Callers that need iteration or list-all can extend when a concrete use case appears — not now. |
| 2026-04-18 | `CachedRaceRegistry` caches `None` results along with hits | Prevents repeated disk reads when a UI looks up a race_id that doesn't exist (e.g. stale reference in a SpeciesPopulation). Negligible memory, correct behavior. |
| 2026-04-18 | Cache invalidation is an explicit `invalidate(race_id=None)` call from the race editor save flow | User can only mutate race files via the in-game race editor during a session. Alternative (file-watch / mtime polling) adds complexity without real value. External edits require a game restart — documented. |
| 2026-04-18 | `StrategySessionFacade.get_race_registry()` is lazy-init, one registry per session | Matches `TurnEngine.harvesting_engine` lazy-init pattern. Session-scoped — resets when a new game starts or a save is loaded. |
| 2026-04-18 | `Empire.resident_species()` is NOT cached, returns `Set[str]` | Recomputes on every call. Empire colonies × species counts are small (~100-500 iterations worst case). Caching introduces invalidation complexity (population extinction, new species arrival) for no measurable gain. |
| 2026-04-18 | "Species in the empire" = `race_id with count >= 1 anywhere in empire.colonies` | User-confirmed 2026-04-18. Excludes extinct species (count=0) and species in allied fleets (fleet race membership is not currently a gameplay concept). |
| 2026-04-18 | Do NOT migrate `PopulationEngine._get_race_config` / `HappinessEngine._get_race_config` to the new registry | The engines' existing resolvers work. Migrating requires touching their event-handlers and tests; risk > reward for PROJ-287. Deferred to a dedicated engine-consolidation project if it ever matters. |
| 2026-04-19 (PROJ-291 reversal) | REVERSAL of the row above: PROJ-291 Phase 2 retrofitted both engines to consume `IRaceRegistry` per the standard PROJ-285 pattern (`race_registry: Optional['IRaceRegistry'] = None` kwarg + None-fallback). | The original deferral was made before multi-species colonies were a reachable game state. Post-PROJ-284/286/289 they are, which exposed a silent dual-return bug in `_get_race_config` (it returned `empire.race_config` regardless of whether `race_id` matched, so non-primary species silently used the empire's primary race's `base_happiness` / `base_reproduction_rate`). PROJ-291 Phase 2 tightens the legacy path (returns `None` on race_id mismatch instead of the wrong config) and wires a session-scoped `CachedRaceRegistry` through `GameSession.race_registry` → `TurnEngine(race_registry=...)` → engine lazy-init. See [PROJ-291/design.md](../PROJ-291/design.md) § Architecture for the retrofit shape. |
| 2026-04-18 | Parallel-safe with PROJ-286; consumer projects are PROJ-288 (projector helpers), PROJ-289 (planet report UI), PROJ-290 (treasury + uncolonized habitability) | Zero file overlap with PROJ-286 (different modules). All three consumers depend on `facade.get_race_registry()` + `Empire.resident_species()`. |
