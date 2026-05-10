# PROJ-286: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-04-18 | Project initialized | Starting point for Multi-Resource Population Consumption |
| 2026-04-18 | Population consumes THREE resources with per-pop-per-turn rates: organics 0.001, metals 0.0001, radioactives 0.00001 | User-confirmed. Organics is the PROJ-284 baseline; metals at 10% and radioactives at 1% represent minor industrial overhead for advanced civilizations. Values intentionally small so colonies on metals/radioactives-poor worlds can still survive with trade. |
| 2026-04-18 | Aggregation from per-resource ratios to the single `last_food_ratio` consumed by downstream engines uses MIN | Liebig's Law of the Minimum: a colony is as well-fed as its worst-supplied resource. Simpler than weighted average, harsher than average, most intuitive for players. |
| 2026-04-18 | `ColonySpeciesConfig.last_food_ratio` becomes a computed `@property` returning `min(last_consumption_ratios.values())` (or 1.0 when empty) | Preserves PROJ-284's `cfg.last_food_ratio` read API byte-for-byte. HappinessEngine + PopulationEngine source files don't change. Tests that pre-set `last_food_ratio = X` migrate to `last_consumption_ratios = {"organics": X}`. |
| 2026-04-18 | `economy.json` schema: `population_consumption: Dict[resource_id, rate]` replaces `population_food_resource` + `food_per_pop_per_turn` | More flexible, future-proof for additional resources, and matches the `population consumes multiple resources` design intent from 2026-04-18 user session. No backward-compat shim for old JSON — per CLAUDE.md System Migration Policy, data files are disposable; there is exactly one `data/economy.json` in the tree and we rewrite it. |
| 2026-04-18 | `EconomyConfig.primary_resource` convenience property returns the first key in `population_consumption` dict | UI titles (e.g. FoodAllocationEditor) need a "primary" food resource name. Dict insertion order is preserved in Python 3.7+; data-file authors control ordering. |
| 2026-04-18 | `EconomyConfig.population_food_resource` kept as a read-only property delegating to `primary_resource` for minimal PROJ-289-until-landed UI compat | Avoids breaking the existing FoodAllocationEditor title until PROJ-289 lands. PROJ-289 will migrate callers to the new name and remove the shim. |
| 2026-04-18 | Do NOT rename `OrganicsConsumptionEngine` to `PopulationUpkeepEngine` in this project | Rename is cosmetic; combining it with a behavior change obscures the multi-resource change in git history. Ripples into IOrganicsConsumptionEngine, TurnEngineConfig field, tests, docs. Deferred. |
| 2026-04-18 | Parallel-safe with PROJ-287; consumer of PROJ-286 is PROJ-288 (projector helpers), PROJ-289 (planet report UI), PROJ-290 (treasury) | PROJ-287 changes only the race registry facade + Empire.resident_species; no overlap. PROJ-288..290 depend on PROJ-286's new `population_consumption` API surface. |
