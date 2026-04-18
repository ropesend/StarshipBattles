# PROJ-285: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-04-18 | Project initialized | Starting point for Habitability-to-Production Economy Hook. |
| 2026-04-18 | Multi-species habitability aggregation uses population-weighted average | User-confirmed (Q4): larger species' habitability counts proportionally more. Smoothly handles shifting demographics. Matches worker-productivity intuition. Min-across-species would be unfair to mixed colonies; dominant-species-only ignores minorities. |
| 2026-04-18 | Uncolonized planets (`total_pop == 0`) default multiplier = 1.0 | Defensible default: no population means no unhappy workers, so full-rate extraction. Discussable if we ever want "strategic colonization" to matter more; leaving as 1.0 for now. |
| 2026-04-18 | Per-turn caching of `planet_habitability_multiplier` | Avoid O(species × resources × ticks) recomputation. Populations only change between turns; cache invalidates on `TurnEngine.process_turn` boundary. |
| 2026-04-18 | Multiplier applies to harvesting AND production; not resupply fuel generation (deferred) | User didn't explicitly request fuel generation. If fuel-gen becomes habitability-dependent later, the helper is already available — a one-line hook in `ResupplyEngine.process_fuel_generation`. |
| 2026-04-18 | Habitability multiplier stacks multiplicatively alongside `BuildRateBooster` / `ResourceHarvestBooster` | Matches the existing "multipliers multiply" pattern in `aggregate_multipliers`. No behavior change for the boosters themselves. |
| 2026-04-18 | `planet_habitability_multiplier` lives at `game/strategy/formulas/colony_output.py` | Groups with `habitability.py`; clean boundary for future "colony performance" extensions (happiness-as-production, cultural traits, etc.). |
| 2026-04-18 | Project scaffolded from master plan at `C:\Users\rossr\.claude\plans\i-want-to-effervescent-hennessy.md` | User requested the big plan be broken into smaller projects. PROJ-285 owns the economy hook. |
| 2026-04-18 | Blocked on PROJ-283 completion; parallel-safe with PROJ-284 | Depends on PROJ-283's registry-driven habitability formula. Independent of PROJ-284's demographics loop changes. |
