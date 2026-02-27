# PROJ-200: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02-27 | Project initialized | Starting point for Reduce complexity: filter_ships (CC 36) |
| 2026-02-27 | Use predicate extraction pattern | Each filter category becomes a `_should_exclude_by_X()` helper returning bool. Clean composition, preserves invariants. |
| 2026-02-27 | Keep late imports inside helpers | FleetCapabilityCalculator import must stay inside function to avoid circular import with strategy layer. |
| 2026-02-27 | Preserve status filter order exactly | Order is: destroyed → derelict → damaged → undamaged. Critical because derelict implies damaged. Comment on line 203 documents this. |
| 2026-02-27 | Add test fortification phase | Safety analysis found gaps: no combination tests, only 1 of 5 special capabilities tested, no empty filter_state test. |
| 2026-02-27 | Extract special capabilities as single helper | The loop over SPECIAL_CAPABILITY_COLUMNS stays inside one helper to preserve break semantics. |
