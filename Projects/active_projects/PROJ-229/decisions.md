# PROJ-229: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02-26 | Project initialized | Starting point for Reduce complexity: filter_ships (CC 36) |
| 2026-02-26 | Proceed with refactoring (not skip) | Function is NOT irreducibly complex; complexity comes from repeated patterns |
| 2026-02-26 | Test fortification first | Safety analysis found missing edge case coverage; tests act as safety net |
| 2026-02-26 | Extract predicate helpers approach | Most natural for Python; each predicate has single responsibility |
| 2026-02-26 | Preserve lazy imports | Keep FleetCapabilityCalculator imports inside helpers to avoid circular imports |
| 2026-02-26 | Status helper returns string | Maps to filter keys; preserves mutual exclusivity invariant |

---

## Decision Details

### Decision 1: Proceed with Refactoring

**Date:** 2026-02-26

**Rationale:**
- Function is NOT irreducibly complex — complexity comes from repeated patterns
- Clear extraction opportunities identified by all 3 review agents
- Comprehensive test coverage (43+ tests) provides safety net
- Status hierarchy can be preserved with careful `_get_ship_status()` extraction

**Alternatives Considered:**
- Skip function: Rejected because complexity is clearly reducible
- Partial refactoring: Rejected because full extraction gives best results

---

### Decision 2: Test Fortification First

**Date:** 2026-02-26

**Rationale:**
- Safety analysis identified missing edge case coverage
- Status hierarchy invariants are critical and subtle
- Tests act as safety net to catch regressions

**Tests to Add:**
1. Empty ships list
2. Empty filter_state defaults
3. Derelict-not-damaged invariant
4. Destroyed-not-derelict invariant
5. Both filter pairs False
6. Order preservation
7. Input non-mutation

---

### Decision 3: Extract Predicate Helpers Approach

**Date:** 2026-02-26

**Rationale:**
- Most natural fit for Python
- Each predicate has single responsibility
- Main function becomes trivially simple
- Preserves order (list comprehension maintains input order)

**Alternatives Considered:**
- Filter chain composition: More complex, less readable
- Table-driven filters: Over-engineered for this use case
- Keep current structure: Doesn't reduce complexity

---

### Decision 4: Preserve Lazy Imports

**Date:** 2026-02-26

**Rationale:**
- Matches original lazy loading behavior
- Avoids circular import issues
- Import cost is minimal (cached after first load)

---

### Decision 5: Status Helper Returns String

**Date:** 2026-02-26

**Rationale:**
- Maps directly to filter keys (`show_destroyed`, etc.)
- Single source of truth for status classification
- Preserves mutual exclusivity invariant
- Easy to test in isolation
