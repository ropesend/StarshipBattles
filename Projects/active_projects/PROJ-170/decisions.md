# PROJ-170: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02-23 | Project initialized from review findings | 7-agent focused review identified 63 raises to migrate, 36 catches to update, 80 tests to change |
| 2026-02-23 | 3 new error codes: V002, V003, C003 | V002 (SCHEMA_VALIDATION_ERROR) for 18+ loader validates, V003 (MISSING_ENTITY) for entity lookups, C003 (MISSING_DEPENDENCY) for 13 DI checks |
| 2026-02-23 | No new exception classes needed | Existing 10 classes cover all identified migration needs |
| 2026-02-23 | TypeError DI → ValidationException (not a new TypeException) | DI validation is conceptually input validation, not type checking. Matches existing pattern. |
| 2026-02-23 | Phase 5 strategy: additive-then-remove for broad catches | Add domain exceptions to except tuples first (safe), remove generic types after all raises migrated (verified) |
| 2026-02-23 | 6 generic raises kept as-is | 3 TypeError (protocol compliance: take_damage, subscribe, HexCoord math), 3 KeyError (dict-like protocol: get_mass_distribution, get_orbit_zone, get_blueprint) |
| 2026-02-23 | Deserialization validation deferred | 15 from_dict methods need validation improvements, but this is a separate concern from exception type migration. Track as future PROJ. |
| 2026-02-23 | Phase ordering: loaders → simulation → UI | Loaders have zero external callers (safest first), simulation is highest-value (core domain), UI is last (most callers are internal) |
| 2026-02-23 | Baseline: 12,016 passed, 1 skipped | Established before any changes |
