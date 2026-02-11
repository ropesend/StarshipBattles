# PROJ-87: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02-09 | Project initialized | Starting point for God Class Decomposition - Strategy Data Tier |
| 2026-02-09 | Execute PROJ-87 first among 4 God class projects | Cleanest dependency graphs (23-100 importers), good test coverage (17-77 test files), highest duplication density (~360 lines) |
| 2026-02-09 | Include re-offender classes | Prior decompositions were incomplete or grew back; need stronger extraction with facade pattern |
| 2026-02-09 | Use facade/delegate pattern for all extractions | Preserves public API; import chains don't break; original classes remain the entry point; 100 Fleet importers make API changes dangerous |
| 2026-02-09 | Extract display methods to strategy layer, not UI | Avoid circular dependency between strategy data and UI layers; create ShipDisplayFormatter in strategy/data/ |
| 2026-02-09 | Use CommandHandlerRegistry pattern for GameSession | 8 command handlers in growing if/elif chain; registry enables plugin-style extension and isolated testing |
| 2026-02-09 | Add Galaxy.get_fleet_by_id() O(1) lookup | Current _get_fleet_by_id() iterates all empires O(n); Galaxy already has O(1) get_planet_by_id() — follow same pattern |
| 2026-02-09 | Serialization stays in original classes | to_dict/from_dict, to_ship/from_ship are core identity of ShipInstance and Fleet; delegation would add complexity without benefit |
