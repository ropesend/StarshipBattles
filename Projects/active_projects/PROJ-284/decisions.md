# PROJ-284: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-04-18 | Project initialized | Starting point for Colony Demographics Loop. |
| 2026-04-18 | Food allocation slider is per-colony per-species, default 1.0, range 0-inf (UI-capped at 5.0 with typed override) | User request: the dial scales consumption + happiness + reproduction linearly. User confirmed 0.5 = half base happiness and reproduction. Practical UI needs a cap; starvation path makes over-allocation above stockpile auto-cap. |
| 2026-04-18 | Population food is a real resource (harvested + stockpiled + consumed), defaults to `organics`, read from `data/economy.json` for moddability | User-confirmed (Q6-round-2): organics already exists in `data/resources.json`; modders should be able to swap the food resource without code edits; UI labels must relabel automatically. |
| 2026-04-18 | Starvation = happiness penalty + population decline | User-confirmed (Q7-round-2). Decline term: `-decline_rate * pop * (1 - last_food_ratio)` when ratio < 1. Recommend starting `decline_rate = 0.02`; tune per playtesting. |
| 2026-04-18 | Happiness is fully derived each turn by `HappinessEngine`; `SpeciesPopulation.happiness` becomes a cache | Plan agent recommendation accepted; `aptitude_happiness` was double-dipping with habitability. Formula: `happiness = clamp(base_happiness * last_food_ratio * habitability, 0, 3)` (unbounded above for over-supply). |
| 2026-04-18 | `ColonySpeciesConfig` dataclass is a NEW class, attached as `Planet.species_configs: Dict[race_id, ColonySpeciesConfig]`, with `last_food_ratio` as a TRANSIENT non-serialized field | Option B in the exploration. Keeps `SpeciesPopulation` pure runtime state; gives per-colony config a proper home; future knobs (labor, tax) slot in without touching `SpeciesPopulation`. |
| 2026-04-18 | `OrganicsConsumptionEngine` runs per-turn (not per-tick) after the 100-tick loop, before `HappinessEngine` | Consumption -> happiness -> population-growth is the logical data-flow order. Running per-turn (not per-tick) aligns with `PopulationEngine` and keeps math cheap. |
| 2026-04-18 | Reproduction formula: `growth = (base_reproduction_rate * last_food_ratio) * pop * (1 - pop/K_eff) * happiness` where `K_eff = max_population * habitability` | Merges user requirements: reproduction scales with base rate, scales with food ratio, scales with happiness (which itself derives from habitability + food). Logistic K still uses habitability. |
| 2026-04-18 | Project scaffolded from master plan at `C:\Users\rossr\.claude\plans\i-want-to-effervescent-hennessy.md` | User requested the big plan be broken into smaller projects. PROJ-284 owns the gameplay-visible demographics loop. |
| 2026-04-18 | Blocked on PROJ-283 completion (depends on `base_reproduction_rate`, `base_happiness`, registry-driven `preferences`) | Strict phase ordering; no PROJ-284 code changes begin until PROJ-283 Phase 6 complete. |
