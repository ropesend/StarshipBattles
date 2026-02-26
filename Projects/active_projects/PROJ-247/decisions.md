# PROJ-247: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02-26 | Project initialized | Starting point for Reduce complexity: filter_ships (CC 36) |
| 2026-02-26 | Proceed with refactoring (not skip) | Function is NOT irreducibly complex - complexity from repeated patterns, single caller, 18 tests, pure function |
| 2026-02-26 | Use predicate extraction strategy | Each filter category becomes a predicate, maintains short-circuit, allows list comprehension |
| 2026-02-26 | Test fortification first | Safety analysis identified 5 coverage gaps; tests serve as regression safety net |
| 2026-02-26 | Preserve late imports | FleetCapabilityCalculator must stay as late import to avoid circular dependencies |
| 2026-02-26 | Share _classify_ship_status | Same logic in sort_ships (lines 251-258); single source of truth |

---

## Decision Details

### Decision 1: Proceed with Refactoring

**Date:** 2026-02-26

**Rationale:**
- Function is NOT irreducibly complex - complexity comes from repeated patterns
- Single caller makes interface changes safe
- Comprehensive existing test coverage (18 tests)
- Pure function with no side effects
- Clear extraction opportunities identified

**Alternatives Considered:**
- Skip: Rejected because the function has clear refactoring opportunities

### Decision 2: Predicate Extraction Strategy

**Date:** 2026-02-26

**Rationale:**
- Each filter category (warp, spaceyard, cargo, special, status) becomes a single predicate
- Maintains short-circuit optimization inside each predicate
- Allows list comprehension in main function
- CC distributed across focused helpers

**Alternatives Considered:**
- Filter chain pattern: More complex, overkill for this use case
- Data-driven configuration: Would require significant restructuring

### Decision 3: Test Fortification First

**Date:** 2026-02-26

**Rationale:**
- Safety analysis identified 5 coverage gaps
- Status hierarchy is critical invariant that needs explicit testing
- Combined filter behavior not currently tested
- Tests serve as regression safety net during refactoring

### Decision 4: Preserve Late Imports

**Date:** 2026-02-26

**Rationale:**
- Late imports exist to avoid circular dependencies
- Comment in `sort_ships` confirms this is intentional
- Moving to module level could break import order
- Performance impact is negligible (Python caches imports)

### Decision 5: Share `_classify_ship_status` with sort_ships

**Date:** 2026-02-26

**Rationale:**
- Same logic duplicated in `sort_ships` (lines 251-258)
- Single source of truth for status hierarchy
- Ensures consistent behavior between filter and sort
