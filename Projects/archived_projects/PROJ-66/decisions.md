# PROJ-66: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02-07 | Project initialized | Starting point for Race Setup Enhancement |
| 2026-02-07 | Use "Faction Name" for combined entity name | User selected over "Entity Name" and "Polity Name"; more natural for sci-fi genre |
| 2026-02-07 | Auto-generate Faction Name from Race Name + Government Type with manual override | Best UX: auto-combines but allows customization. e.g., "Rossarian" + "Commonwealth" = "Rossarian Commonwealth" |
| 2026-02-07 | Reorganize to 7 tabs: Summary, Identity, Visuals, Ships, Environment, Aptitudes, Descriptions | Cleanly separates concerns; Identity holds all naming/classification fields, Aptitudes holds point-buy stats |
| 2026-02-07 | Use PlanetType enum for homeworld selection (ALL types habitable) | Gas giants and planetoids are habitable by alien species; species from gas giants will have trouble on terrestrial worlds and vice versa |
| 2026-02-07 | Single shared point pool for aptitudes AND environmental tolerance | Forces meaningful tradeoffs between racial stats and environmental flexibility |
| 2026-02-07 | Exponential cost curve: doubling (2^n) for tolerance increases | Broad tolerance becomes prohibitively expensive fast; prevents "jack of all trades" builds |
| 2026-02-07 | Store-only for Government Organization and Society Type effects | Save selection in RaceConfig now; defer gameplay modifier design to follow-up project |
| 2026-02-07 | Water preference uses ideal + tolerance pair | Consistent with existing gravity/temperature pattern; ideal water %, plus tolerance range |
| 2026-02-07 | Race name field stays; "name" field in RaceConfig becomes "faction_name" | Current `name` field acts as display name; we'll use it for faction, add separate race identity fields |
