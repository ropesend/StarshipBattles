# PROJ-75: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02-07 | Project initialized | Starting point for Resource Harvesting & Economy System |
| 2026-02-07 | All 5 planetary resources for construction | User preference - comprehensive economy using Metals, Organics, Vapors, Radioactives, Exotics |
| 2026-02-07 | Instant scuttle on maintenance failure | User preference - simple, predictable behavior vs degradation or efficiency penalty |
| 2026-02-07 | True global pool (no logistics) | User preference - simpler implementation for MVP, instant access everywhere |
| 2026-02-07 | Per-component costs in JSON | User preference - each component defines resource_cost, ship cost = sum of components |
| 2026-02-07 | 100-tick granular building | Matches existing turn structure (100 ticks/turn), enables mid-turn launches |
| 2026-02-07 | 5% maintenance rate | Specified in requirements - 5% of build cost per turn for ships and complexes |
| 2026-02-07 | Harvest formula: base_rate * quality | Simple multiplier approach, quality from planet.resources[type]['quality'] |
| 2026-02-07 | Storage overflow discarded | Excess harvested resources lost when max_storage exceeded, logged for player awareness |
| 2026-02-07 | Build pauses on insufficient resources | Don't decrement turns_remaining, resume when resources available |
| 2026-02-07 | One-pass scuttling | Process all maintenance checks first, then execute scuttles to prevent cascade |
| 2026-02-07 | Turn phase order: Harvest -> Maintenance -> Consumption -> Production | Logical flow: earn, pay, spend |
