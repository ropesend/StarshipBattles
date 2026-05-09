# PROJ-401: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-05-09 | Project initialized | Starting point for Tier 1 B-02: Passenger-load validator missing species_id rejection |
| 2026-05-09 | Error code = `MISSING_SPECIES_ID` | Matches existing snake-upper convention in `_validate_load` (`NO_CARGO_SPACE`, `NO_POPULATION`, `NO_STAGING_ITEMS`, `NO_POD_CAPACITY`). The cargo type is implicit (passenger LOAD is the only path that needs species), so the code stays terse rather than `PASSENGER_LOAD_MISSING_SPECIES_ID`. |
| 2026-05-09 | Adjacent gap noted, NOT fixed | `_validate_unload` and `_validate_fleet_transfer` accept `species_id=None` for passengers without rejection. The runtime executor branches for these directions were not part of PROJ-393's deletion, so the contract may still be lenient on those paths. Out of scope for PROJ-401; surfacing here for follow-up triage. |
