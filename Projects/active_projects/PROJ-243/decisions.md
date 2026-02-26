# PROJ-243: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02-26 | Project initialized | Starting point for Reduce complexity: filter_ships (CC 36) |
| 2026-02-26 | Function is refactorable | Clear repeated patterns, good test coverage, single caller |
| 2026-02-26 | Extract binary filter helper | Pattern appears 4+ times, reduces CC by ~16 |
| 2026-02-26 | Extract status classification | Separates concern, encapsulates ordering |
| 2026-02-26 | Test fortification first | Add edge case tests before any code changes |
| 2026-02-26 | Keep late imports | Preserve lazy-loading to avoid circular dependencies |
| 2026-02-26 | Use predicate composition | `_ship_passes_filters` predicate with list comprehension |

---

## Decision Details

### Decision 1: Function is Refactorable

**Date:** 2026-02-26
**Context:** Initial analysis of `filter_ships` (CC 36)
**Decision:** Proceed with refactoring (not skip)

**Rationale:**
- Function has clear repeated patterns (binary filters appear 4+ times)
- 20 direct tests + 28 indirect tests provide safety net
- Single production caller makes changes low-risk
- Complexity is accidental (repetition), not essential (state machine)

**Alternatives Considered:**
- Skip and add to skip list - Rejected because complexity IS reducible

---

### Decision 2: Extract Binary Filter Helper

**Date:** 2026-02-26
**Context:** How to reduce repeated filter pattern complexity
**Decision:** Create `_passes_binary_filter()` helper with callable parameter

**Rationale:**
- Pattern appears identically for warp, spaceyard, cargo filters
- Pattern also appears in special capability loop
- Single helper reduces CC by ~16 points
- Callable parameter allows different capability checks

---

### Decision 3: Extract Status Classification

**Date:** 2026-02-26
**Context:** Status filter chain has strict ordering requirements
**Decision:** Create `_get_ship_status()` helper returning string

**Rationale:**
- Status classification is separate concern from filtering
- Return value ('destroyed'/'derelict'/'damaged'/'undamaged') maps to filter keys
- Ordering is encapsulated in one place with clear comments
- Reduces main function CC by ~4 points

---

### Decision 4: Test Fortification Before Refactoring

**Date:** 2026-02-26
**Context:** Safety analysis identified missing edge case tests
**Decision:** Add edge case tests in Phase 1 BEFORE any code changes

**Tests to Add:**
1. `test_destroyed_derelict_ship_classified_as_destroyed`
2. `test_derelict_damaged_ship_classified_as_derelict`
3. `test_multiple_special_capability_filters_all_must_pass`
4. `test_partial_filter_state_defaults_to_show_all`

---

### Decision 5: Keep Late Imports

**Date:** 2026-02-26
**Context:** `FleetCapabilityCalculator` is imported inside the function
**Decision:** Keep late imports in helper functions

**Rationale:**
- Late imports exist to avoid circular dependencies
- Moving to top-level would change import behavior
- Importing inside helper maintains same lazy-loading pattern

---

### Decision 6: Use Predicate Composition Pattern

**Date:** 2026-02-26
**Context:** How to structure the refactored code
**Decision:** Convert to `_ship_passes_filters()` predicate with list comprehension

**Final Structure:**
```python
def filter_ships(ships, filter_state):
    return [ship for ship in ships if _ship_passes_filters(ship, filter_state)]
```
