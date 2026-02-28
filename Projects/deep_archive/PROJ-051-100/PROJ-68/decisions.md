# PROJ-68: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02-07 | Project initialized | Population System & Generic Cargo |
| 2026-02-07 | 1 pop unit = 1,000 people | Granular enough for transport (ships carry 1-10K units), manageable display numbers. Earth-like planet maxes at ~50M units |
| 2026-02-07 | Max density: 100 pop/km² surface | Earth-like planet (~510M km²) → ~50B people = 50M units. Good gameplay range for growth |
| 2026-02-07 | Colony founding pop from ship cargo | Requires passenger quarters for effective colonization. Makes ship design a strategic choice. If no passengers, seed minimum 100 units |
| 2026-02-07 | Store full RaceConfig on Empire | Avoids file I/O at runtime. Clean access to all race data for growth calculations, habitability scoring. Multiple races possible per empire in future |
| 2026-02-07 | Multi-species per colony from the start | Design data model for multiple SpeciesPopulation entries per planet immediately. Avoids painful refactor when absorbing alien races |
| 2026-02-07 | Generic cargo system (not passenger-specific) | Build CargoStorage ability with cargo_type parameter. Passengers first, but future cargo types (metals, organics, hardware, fighters) slot in with zero refactoring |
| 2026-02-07 | Logistic growth model (S-curve) | `growth = r * P * (1 - P/K) * happiness`. Natural feeling, slows near capacity. K = max_population * habitability |
| 2026-02-07 | Per-species happiness (not colony-wide) | Each species has own happiness based on habitability match, tolerance_other_species, crowding. Richer gameplay, enables species-specific mechanics |
| 2026-02-07 | Single TRANSFER order type | One order with direction (load/unload), cargo_type, amount params. Clean, extensible. Not separate LOAD/UNLOAD order types |
| 2026-02-07 | CargoStorage follows ResourceStorage pattern | Same STAT_BINDINGS, sync_data(), recalculate() pattern. Consistent with codebase conventions |
| 2026-02-07 | Population growth runs after production in turn engine | End-of-turn processing, not distributed across 100 ticks (unlike resources). Population changes once per turn, not fractionally |
| 2026-02-07 | Habitability uses linear falloff from ideal | Score = max(0, 1 - abs(actual - ideal) / tolerance). Simple, predictable, easy to balance. Geometric mean of all factors for final score |
