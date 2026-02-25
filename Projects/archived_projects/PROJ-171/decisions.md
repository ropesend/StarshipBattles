# PROJ-171: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02-23 | Project initialized | Deserialization Input Validation — from review findings EXC-D |
| 2026-02-23 | Use PersistenceException (not ValidationException) for from_dict errors | from_dict receives external/saved data — persistence boundary, not user input validation |
| 2026-02-23 | Error code P003 (CORRUPT_DATA) for all from_dict validation failures | Data was presumably valid when saved; corruption detected during load |
| 2026-02-23 | Create validation helper module in game/core/ | 15 methods × same pattern = worth a helper; core is correct layer (no game logic) |
| 2026-02-23 | Skip bad children in collections (log + continue) | One bad planet shouldn't lose entire galaxy — resilient degradation for user experience |
| 2026-02-23 | Fail on missing required scalar fields (id, name, location) | Object can't exist without identity/location — fail fast with clear message |
| 2026-02-23 | Soft dependency on PROJ-170 | Can proceed independently; PROJ-170 changes raise types but PROJ-171 adds new raises using exceptions directly |
| 2026-02-23 | Only require_keys for fields that have ALWAYS existed | Backwards compat for old saves — newer optional fields use .get() with defaults |
| 2026-02-23 | Exclude RaceConfig, EventLog, LayerData from scope | Already validate well — no changes needed |
